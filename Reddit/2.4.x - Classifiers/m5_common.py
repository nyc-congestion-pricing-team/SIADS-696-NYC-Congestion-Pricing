#!/usr/bin/env python3
"""Shared module for the 5-fold-CV-tuned classifier pipeline (Project Data - 15).

Supersedes the earlier classifier notebooks. Four families, 4-class stance
{anti, neutral, pro, off-topic}:
  Naive Bayes · XGBoost · DistilRoBERTa@512 · ModernBERT@512   (both transformers at max_len 512)

Three stages (see tuned_5fold.ipynb):
  1. BASELINE  — library-default configs, trained once, saved to saved_models/baseline/.
  2. TUNED     — hyperparameters chosen by **5-fold grouped cross-validation** (StratifiedGroupKFold
                 on link_id), best config refit on the FULL training pool, saved to saved_models/tuned/.
  3. GOLD      — the tuned (and baseline) models on the held-out human gold set (population-weighted).

Heavy GPU work is run by train_baseline.py / tune_5fold.py (trial-parallel across both GPUs);
nothing heavy runs at import. torch/transformers/xgboost import lazily inside functions.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import json

import numpy as np
import pandas as pd

# ── constants (4-class) ──────────────────────────────────────────────────────
SEED       = 42
LABELS     = ["anti", "neutral", "pro", "off-topic"]
ON_TOPIC   = ["anti", "neutral", "pro"]
STANCE_MAP = {"pro": "pro", "anti": "anti", "neutral": "neutral",
              "mixed": "neutral", "unsure": "neutral",
              "NA": "off-topic", "not_about_it": "off-topic"}
lab2i = {l: i for i, l in enumerate(LABELS)}
i2lab = {i: l for l, i in lab2i.items()}
NB_COLS    = ["target", "context"]
STRONG_EMB = "BAAI/bge-base-en-v1.5"

# ── paths (inputs from P11/M2; outputs in THIS folder) ───────────────────────
M2   = ROOT   # (submission: inputs in ../data, models in ../models)
HERE = Path(__file__).resolve().parent
ROOT = next((p for p in HERE.parents if p.name == "Reddit"), HERE.parent)  # Reddit code root
CLF  = ROOT / "data"
DATA = ROOT / "data"
TEXT_XLSX    = DATA / "relabel_5k_v2.xlsx"
LABEL_CSV    = DATA / "relabel_5k-claude-v2.csv"
GOLD_JSONL   = DATA / "gold_labels_Anita_301.jsonl"
GOLD_SIDECAR = DATA / "gold_adj_sidecar.parquet"
SENT_DIR     = DATA

SAVED    = ROOT / "models" / "saved_models"
BASE_DIR   = SAVED / "baseline"
TUNED_DIR  = SAVED / "tuned"
FEAT_CACHE = SAVED / "feat_cache"
STUDY_DB   = SAVED / "studies.db"                  # optuna sqlite (shared by trial-parallel workers)
TUNED_HP   = SAVED / "tuned_hyperparams.json"
for _d in (SAVED, FEAT_CACHE):
    _d.mkdir(parents=True, exist_ok=True)

# ── model registry ───────────────────────────────────────────────────────────
MODELS = ["NaiveBayes", "XGBoost", "DistilRoBERTa", "ModernBERT"]
TF_SPECS = {"DistilRoBERTa": ("distilroberta-base", 512, 32),
            "ModernBERT":    ("answerdotai/ModernBERT-base", 512, 16)}   # both @512

N_TRIALS_XGB   = 30        # prior budget
N_TRIALS_TF    = 20        # per transformer
TF_TUNE_EPOCHS = 4
CV_N_SPLITS    = 5         # FIVE-fold only


def model_path(stage, name):
    """File/dir path for a saved model. stage in {'baseline','tuned'}."""
    root = BASE_DIR if stage == "baseline" else TUNED_DIR
    return {"NaiveBayes": root / "nb.joblib", "XGBoost": root / "xgb.json",
            "DistilRoBERTa": root / "distilroberta", "ModernBERT": root / "modernbert"}[name]


# ─────────────────────────────────────────────────────────────────────────────
# Data prep
# ─────────────────────────────────────────────────────────────────────────────
def _build_text(frame):
    frame = frame.copy()
    frame["context"] = frame["context"].fillna("").astype(str).str.strip()
    frame["target"]  = frame["target"].fillna("").astype(str).str.strip()
    frame["text"] = "[CONTEXT]\n" + frame["context"] + "\n\n[TARGET]\n" + frame["target"]
    return frame


@lru_cache(maxsize=1)
def load_frames():
    """{'df': training pool (gold removed), 'gold_text': pop-weighted gold}."""
    text_df  = pd.read_excel(TEXT_XLSX)
    label_df = pd.read_csv(LABEL_CSV, keep_default_na=False)
    cols = ["row_id", "kind", "subreddit", "context", "target"]
    df = label_df.merge(text_df[cols], on="row_id", how="inner", suffixes=("", "_x"))
    df["label"] = df["claude_v2_stance"].map(STANCE_MAP)
    df = df[df["label"].isin(LABELS)].copy()
    df = _build_text(df)[["row_id", "reddit_id", "link_id", "kind", "subreddit",
                          "context", "target", "text", "label"]]

    gold = pd.DataFrame([json.loads(l) for l in GOLD_JSONL.read_text(encoding="utf-8").splitlines() if l.strip()])
    sidecar = pd.read_parquet(GOLD_SIDECAR)[["qid", "row_id", "reddit_id", "cell", "n_cell"]]
    gold = gold.merge(sidecar, on="qid", how="left")
    df = df[~df["row_id"].isin(set(gold["row_id"].dropna())) &
            ~df["reddit_id"].isin(set(gold["reddit_id"].dropna()))].copy()

    gt = gold.merge(text_df[cols].drop(columns=[c for c in cols if c in gold.columns and c != "row_id"]),
                    on="row_id", how="left")
    gt["label"] = gt["label"].map(STANCE_MAP)
    gt = gt[gt["label"].isin(LABELS)].copy()
    gt = _build_text(gt)
    gt["w"] = gt["n_cell"] / gt.groupby("cell")["qid"].transform("count")
    return {"df": df.reset_index(drop=True), "gold_text": gt}


def fold_indices(df, n_splits=CV_N_SPLITS, seed=SEED):
    """Deterministic 5-fold grouped-stratified (tr_idx, va_idx) pairs — identical in every process."""
    from sklearn.model_selection import StratifiedGroupKFold
    df = df.reset_index(drop=True)
    groups = df["link_id"].fillna(df["row_id"]).to_numpy()
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    return [(tr, va) for tr, va in sgkf.split(df, df["label"], groups)]


def class_weights(y):
    vc = pd.Series(y).value_counts(); n, k = len(y), len(vc)
    return {c: n / (k * vc[c]) for c in vc.index}


# ─────────────────────────────────────────────────────────────────────────────
# Metrics
# ─────────────────────────────────────────────────────────────────────────────
def macro_metrics(y_true, y_pred, sample_weight=None):
    from sklearn.metrics import f1_score, accuracy_score, balanced_accuracy_score
    y_true = pd.Series(list(y_true)).reset_index(drop=True)
    y_pred = pd.Series(list(y_pred)).reset_index(drop=True)
    sw = None if sample_weight is None else np.asarray(sample_weight, dtype=float)
    out = {"macro_f1": f1_score(y_true, y_pred, labels=LABELS, average="macro", sample_weight=sw, zero_division=0),
           "accuracy": accuracy_score(y_true, y_pred, sample_weight=sw),
           "balanced_accuracy": balanced_accuracy_score(y_true, y_pred, sample_weight=sw)}
    m = y_true.isin(ON_TOPIC).to_numpy(); sw_m = None if sw is None else sw[m]
    out["macro_f1_3class"] = (f1_score(y_true[m], y_pred[m], labels=ON_TOPIC, average="macro",
                                       sample_weight=sw_m, zero_division=0) if m.any() else float("nan"))
    for lbl in LABELS:
        out[f"f1_{lbl}"] = f1_score(y_true, y_pred, labels=[lbl], average="macro", sample_weight=sw, zero_division=0)
    return out


def ap_per_class(y_true, y_score, sample_weight=None):
    """Per-class average precision (PR-AUC, one-vs-rest) + macro. y_score in LABELS order."""
    from sklearn.metrics import average_precision_score
    y_true = np.asarray(list(y_true)); y_score = np.asarray(y_score)
    sw = None if sample_weight is None else np.asarray(sample_weight, dtype=float)
    out, aps = {}, []
    for i, lbl in enumerate(LABELS):
        ybin = (y_true == lbl).astype(int)
        ap = (float("nan") if ybin.sum() == 0
              else float(average_precision_score(ybin, y_score[:, i], sample_weight=sw)))
        out[f"ap_{lbl}"] = ap; aps.append(ap)
    out["macro_pr_auc"] = float(np.nanmean(aps))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Feature builders (bge ⊕ meta ⊕ sentiment) for XGBoost
# ─────────────────────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(STRONG_EMB, device="cuda")


def embed(texts):
    return _embedder().encode(list(texts), batch_size=128, show_progress_bar=False,
                              convert_to_numpy=True, normalize_embeddings=True)


def meta(frame):
    is_post = (frame["kind"] == "post").to_numpy().astype("float32")[:, None]
    loglen  = np.log1p(frame["target"].str.len().to_numpy()).astype("float32")[:, None]
    return np.hstack([is_post, loglen])


@lru_cache(maxsize=1)
def _sent_feats():
    sent = pd.concat([pd.read_parquet(SENT_DIR / "comment_sentiment.parquet"),
                      pd.read_parquet(SENT_DIR / "post_sentiment.parquet")], ignore_index=True)
    num = [c for c in sent.select_dtypes(include="number").columns if c != "id"]
    return sent.drop_duplicates("id").set_index("id")[num]


def xgb_feats(frame):
    return np.hstack([embed(frame["text"]), meta(frame),
                      _sent_feats().reindex(frame["reddit_id"]).to_numpy(dtype="float32")]).astype("float32")


def get_xgb_cache(df):
    """Disk-cache the XGBoost feature matrix for the pool so all workers share it (no re-embed)."""
    xp, yp = FEAT_CACHE / "X_xgb.npy", FEAT_CACHE / "y_idx.npy"
    if xp.exists() and yp.exists():
        X = np.load(xp)
        if X.shape[0] == len(df):
            return X, np.load(yp)
    X = xgb_feats(df); y = df["label"].map(lab2i).to_numpy()
    np.save(xp, X); np.save(yp, y)
    return X, y


# ─────────────────────────────────────────────────────────────────────────────
# Model builders / trainers (parametric — used for both baseline and tuned)
# ─────────────────────────────────────────────────────────────────────────────
def build_nb(alpha=1.0, tgt_ngram=(1, 1), ctx_weight=1.0):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import ComplementNB
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    return Pipeline([
        ("feats", ColumnTransformer([
            ("tgt", TfidfVectorizer(ngram_range=tgt_ngram, sublinear_tf=True, strip_accents="unicode"), "target"),
            ("ctx", TfidfVectorizer(ngram_range=(1, 1), sublinear_tf=True, strip_accents="unicode"), "context"),
        ], transformer_weights={"tgt": 1.0, "ctx": ctx_weight})),
        ("clf", ComplementNB(alpha=alpha))])


NB_DEFAULT = dict(alpha=1.0, tgt_ngram=(1, 1), ctx_weight=1.0)        # library default
NB_GRID    = {"clf__alpha": [0.1, 0.3, 1.0],
              "feats__tgt__ngram_range": [(1, 1), (1, 2)],
              "feats__transformer_weights": [{"tgt": 1.0, "ctx": 0.3}, {"tgt": 1.0, "ctx": 0.6}, {"tgt": 1.0, "ctx": 1.0}]}

XGB_DEFAULT = {}                                                     # library defaults
XGB_FIXED   = dict(objective="multi:softprob", num_class=len(LABELS), tree_method="hist",
                   device="cuda", eval_metric="mlogloss", random_state=SEED)


def build_xgb(params=None, early_stop=False):
    import xgboost as xgb
    p = dict(params or {})
    kw = dict(XGB_FIXED)
    if early_stop:
        kw["early_stopping_rounds"] = 40
    return xgb.XGBClassifier(**p, **kw)


def xgb_space(trial):
    return dict(n_estimators=1000,
                max_depth=trial.suggest_int("max_depth", 3, 9),
                learning_rate=trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                min_child_weight=trial.suggest_int("min_child_weight", 1, 8),
                subsample=trial.suggest_float("subsample", 0.6, 1.0),
                colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
                gamma=trial.suggest_float("gamma", 0.0, 5.0),
                reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True))


TF_DEFAULT = dict(lr=5e-5, weight_decay=0.0, warmup_ratio=0.0, epochs=3, class_weighted=False)  # HF-ish default


def tf_space(trial):
    return dict(lr=trial.suggest_float("lr", 1e-5, 5e-5, log=True),
                weight_decay=trial.suggest_float("weight_decay", 0.0, 0.1),
                warmup_ratio=trial.suggest_float("warmup_ratio", 0.0, 0.2),
                epochs=TF_TUNE_EPOCHS, class_weighted=True)


def train_tf(model_name, max_len, bs, train_df, lr, weight_decay, warmup_ratio, epochs,
             class_weighted=True, on_epoch_end=None):
    """Fine-tune a fresh transformer on train_df. Returns (model, tokenizer).

    on_epoch_end(ep): optional no-op-by-default callback invoked after each finished epoch (0-based);
    used by the sensitivity sweep's cross-config epoch timer. Leaving it None preserves prior behavior.
    """
    import torch
    from torch import nn
    from torch.utils.data import DataLoader
    from transformers import (AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding)
    tk = AutoTokenizer.from_pretrained(model_name); tk.truncation_side = "left"
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=len(LABELS),
        id2label={i: l for i, l in enumerate(LABELS)}, label2id=lab2i).to("cuda")
    enc = tk(train_df["text"].tolist(), truncation=True, max_length=max_len)
    rows = [{"input_ids": ii, "labels": y} for ii, y in zip(enc["input_ids"], train_df["label"].map(lab2i).tolist())]
    dl = DataLoader(rows, batch_size=bs, shuffle=True, collate_fn=DataCollatorWithPadding(tk))
    if class_weighted:
        cw = class_weights(train_df["label"]); w = torch.tensor([cw[l] for l in LABELS], dtype=torch.float, device="cuda")
    else:
        w = None
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    total = max(1, len(dl) * epochs); warm = int(total * warmup_ratio)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: s / max(1, warm) if s < warm else max(0.0, (total - s) / max(1, total - warm)))
    model.train()
    for ep in range(epochs):
        for b in dl:
            y = b.pop("labels").to("cuda"); b = {k: v.to("cuda") for k, v in b.items()}
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss = nn.functional.cross_entropy(model(**b).logits, y, weight=w)
            loss.backward(); opt.step(); sched.step(); opt.zero_grad()
        if on_epoch_end is not None:
            on_epoch_end(ep)                       # epoch ep (0-based) just finished — sweep timer hook
    model.eval()
    return model, tk


def predict_tf(model, tok, frame, max_len, bs=64, return_proba=False):
    import torch
    from torch.utils.data import DataLoader
    from transformers import DataCollatorWithPadding
    enc = tok(frame["text"].tolist(), truncation=True, max_length=max_len)
    dl = DataLoader([{"input_ids": ii} for ii in enc["input_ids"]], batch_size=bs, shuffle=False,
                    collate_fn=DataCollatorWithPadding(tok))
    out = []
    with torch.no_grad():
        for b in dl:
            b = {k: v.to("cuda") for k, v in b.items()}
            with torch.autocast("cuda", dtype=torch.bfloat16):
                out.append(model(**b).logits.float().cpu())
    logits = torch.cat(out)
    if return_proba:
        return torch.softmax(logits, dim=-1).numpy()
    return pd.Series(logits.argmax(-1).numpy(), index=frame.index).map(i2lab)


# ─────────────────────────────────────────────────────────────────────────────
# 5-fold CV scoring (the tuning objective)
# ─────────────────────────────────────────────────────────────────────────────
def cv_macro_f1_xgb(params, X, y, folds):
    """Mean 5-fold macro-F1 for an XGBoost config (class-weighted, early-stop on each fold)."""
    sc = []
    for tr, va in folds:
        cwd = class_weights(pd.Series(y[tr])); sw = pd.Series(y[tr]).map(cwd).to_numpy()
        m = build_xgb(params, early_stop=True)
        m.fit(X[tr], y[tr], sample_weight=sw, eval_set=[(X[va], y[va])], verbose=False)
        m.get_booster().set_param({"device": "cpu"})
        sc.append(macro_metrics(pd.Series(y[va]).map(i2lab), pd.Series(m.predict(X[va])).map(i2lab))["macro_f1"])
    return float(np.mean(sc))


def cv_macro_f1_tf(model_name, max_len, bs, hp, df, folds, trial=None):
    """Mean 5-fold macro-F1 for a transformer config. Per-fold report enables Optuna pruning."""
    import torch
    sc = []
    for k, (tr, va) in enumerate(folds):
        model, tk = train_tf(model_name, max_len, bs, df.iloc[tr], hp["lr"], hp["weight_decay"],
                             hp["warmup_ratio"], hp["epochs"], hp.get("class_weighted", True))
        pred = predict_tf(model, tk, df.iloc[va], max_len)
        sc.append(macro_metrics(df.iloc[va]["label"], pred)["macro_f1"])
        del model; torch.cuda.empty_cache()
        if trial is not None:
            trial.report(float(np.mean(sc)), k)
            if trial.should_prune():
                import optuna
                raise optuna.TrialPruned()
    return float(np.mean(sc))


# ─────────────────────────────────────────────────────────────────────────────
# Save / load + tuned-hyperparameter store
# ─────────────────────────────────────────────────────────────────────────────
def save_nb(stage, pipe):
    import joblib
    p = model_path(stage, "NaiveBayes"); p.parent.mkdir(parents=True, exist_ok=True); joblib.dump(pipe, p)


def save_xgb(stage, model):
    p = model_path(stage, "XGBoost"); p.parent.mkdir(parents=True, exist_ok=True); model.save_model(str(p))


def save_tf(stage, name, model, tok, hp):
    d = model_path(stage, name); d.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(d); tok.save_pretrained(d)
    json.dump({"max_len": TF_SPECS[name][1], "truncation_side": "left", "labels": LABELS, "hyperparams": hp},
              open(d / "inference_config.json", "w"), indent=2)


def exists(stage, name):
    return model_path(stage, name).exists()


def load_proba(stage, name, frame):
    """Load a saved model and return (n, len(LABELS)) class-probabilities in LABELS order."""
    p = model_path(stage, name)
    if name == "NaiveBayes":
        import joblib
        m = joblib.load(p); idx = [list(m.classes_).index(l) for l in LABELS]
        return m.predict_proba(frame[NB_COLS])[:, idx]
    if name == "XGBoost":
        import xgboost as xgb
        m = xgb.XGBClassifier(); m.load_model(str(p)); m.get_booster().set_param({"device": "cpu"})
        return m.predict_proba(xgb_feats(frame))
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch  # noqa: F401
    cfg = json.loads((p / "inference_config.json").read_text()); mlen = cfg.get("max_len", 512)
    tk = AutoTokenizer.from_pretrained(p); tk.truncation_side = cfg.get("truncation_side", "left")
    model = AutoModelForSequenceClassification.from_pretrained(p).to("cuda").eval()
    return predict_tf(model, tk, frame, mlen, return_proba=True)


def read_tuned_hp():
    return json.loads(TUNED_HP.read_text(encoding="utf-8")) if TUNED_HP.exists() else {}


def write_tuned_hp(name, params):
    cur = read_tuned_hp(); cur[name] = params
    TUNED_HP.write_text(json.dumps(cur, indent=2), encoding="utf-8")

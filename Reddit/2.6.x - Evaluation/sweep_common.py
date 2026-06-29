#!/usr/bin/env python3
"""Shared logic for the ModernBERT@512 LR / epochs SENSITIVITY sweep (Project Data - 15).

One-at-a-time (OAT) **local** sensitivity around the 5-fold-CV-tuned ModernBERT@512 config:
  * LR sweep     — 10 log-spaced points in [1e-5, 2e-4] (incl. the tuned LR), epochs held at tuned 4.
                   The grid deliberately extends ABOVE the 5e-5 tuning ceiling to test whether the
                   tuned LR (~5e-5, which sat at the edge of the tuning range) is a real optimum.
  * EPOCHS sweep — integer epochs 1..8 (faithful per-k runs: each k trained from scratch for k epochs,
                   so each point is a true "if epochs had been k" model), LR held at the tuned value.

Everything else is held at the tuned recipe: weight_decay, warmup_ratio, batch size, class-weighting,
the 5 grouped folds (StratifiedGroupKFold on link_id), and max_len 512. The tuned config
(tuned LR, 4 epochs) is the SHARED CENTRE of both curves and is trained once.

No full-pool refit; no model weights are saved. For every (config, fold) we cache the val-fold
probabilities (a tiny .npz) and record the FULL metric suite — macro-F1[4], macro-F1[3 on-topic],
balanced accuracy, accuracy, per-class F1, per-class PR-AUC, and macro PR-AUC — so any other metric
can be recomputed later without retraining (this replaces "save the model" for KB instead of GB).

Per-fold training is seeded by fold (SEED + fold), so the ONLY thing that varies along a curve is the
swept hyperparameter, not the random init / data shuffle.
"""
from __future__ import annotations
import sys
from pathlib import Path
import time
import numpy as np

# The shared classifier library m5_common.py lives in Project Data - 15 (it is imported, not moved,
# because tune_5fold/train_baseline/the ablation all depend on it). Add P15 to the path, cross-folder.
P15 = Path(__file__).resolve().parent
if str(P15) not in sys.path:
    sys.path.insert(0, str(P15))
import m5_common as M

MODEL          = "ModernBERT"
NAME, MLEN, BS = M.TF_SPECS[MODEL]                 # answerdotai/ModernBERT-base, 512, 16

# Sensitivity artifacts live HERE in Project Data - 16 (the evaluation folder), not back in P15.
HERE16    = Path(__file__).resolve().parent
SENS_DIR  = HERE16 / "sensitivity"
PROBA_DIR = SENS_DIR / "proba"
HERE_CSV  = HERE16 / "sensitivity_results.csv"     # merged long-form results (one row per cfg×fold)
for _d in (SENS_DIR, PROBA_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ── tuned ModernBERT@512 recipe = the centre everything is held at ────────────
_T  = M.read_tuned_hp()[MODEL]
LR0 = float(_T["lr"]); WD = float(_T["weight_decay"]); WU = float(_T["warmup_ratio"])
EP0 = int(_T["epochs"]); CW = bool(_T.get("class_weighted", True))

LR_GRID = sorted(set(np.geomspace(1e-5, 2e-4, 9).tolist()) | {LR0})   # 9 new + tuned centre = 10
EP_GRID = list(range(1, 9))                                           # 1..8 (4 = tuned centre)

METRICS = (["macro_f1", "macro_f1_3class", "balanced_accuracy", "accuracy"]
           + [f"f1_{l}" for l in M.LABELS]
           + [f"ap_{l}" for l in M.LABELS] + ["macro_pr_auc"])


def cfg_id(lr, epochs):
    return f"lr{lr:.3e}_ep{epochs}"


def build_configs():
    """Unique (lr, epochs) configs to TRAIN, each tagged with the (sweep, x_value) labels it feeds.
    The tuned centre (LR0, EP0) appears in BOTH the LR and EPOCHS sweep and is trained ONCE."""
    cfgs = {}                                   # cfg_id -> {lr, epochs, labels:[(sweep, x_value)]}
    for lr in LR_GRID:
        cid = cfg_id(lr, EP0)
        cfgs.setdefault(cid, dict(lr=float(lr), epochs=EP0, labels=[]))["labels"].append(("lr", float(lr)))
    for ep in EP_GRID:
        cid = cfg_id(LR0, ep)
        cfgs.setdefault(cid, dict(lr=LR0, epochs=int(ep), labels=[]))["labels"].append(("epochs", int(ep)))
    return [dict(cfg_id=cid, **v) for cid, v in sorted(cfgs.items())]


SMOKE_CFG = cfg_id(LR0, 1)                        # cheapest config (1 epoch) — used by --smoke


def pending_epochs(cfgs, fold_ids, force=False):
    """Epochs that will ACTUALLY be trained (cached folds are skipped) — the denominator for ETA."""
    tot = 0
    for c in cfgs:
        for k in fold_ids:
            if force or not (PROBA_DIR / f"{c['cfg_id']}__fold{k}.npz").exists():
                tot += c["epochs"]
    return tot


def _fmt(secs):
    s = int(secs); h, r = divmod(s, 3600); m, sec = divmod(r, 60)
    return f"{h}h{m:02d}m{sec:02d}s" if h else f"{m}m{sec:02d}s"


class EpochTimer:
    """Cross-config epoch timer for one worker. Call .tick() after every TRAINED epoch (wire it via
    train_tf's on_epoch_end). Prints every `every` epochs: elapsed, epochs done, sec/epoch for this
    batch AND overall, and the remaining ETA (from the overall rate)."""
    def __init__(self, total_epochs, every=10, label=""):
        self.total = max(0, int(total_epochs)); self.every = every; self.label = label
        self.done = 0; self.t0 = time.perf_counter()
        self.batch_t0 = self.t0; self.batch_done = 0

    def tick(self, *_):
        self.done += 1; self.batch_done += 1
        if self.done % self.every and self.done != self.total:
            return
        now = time.perf_counter(); elapsed = now - self.t0
        spe_batch = (now - self.batch_t0) / max(1, self.batch_done)
        spe_all   = elapsed / max(1, self.done)
        remaining = max(0, self.total - self.done)
        print(f"{self.label}[timer] {self.done}/{self.total} epochs · elapsed {_fmt(elapsed)} · "
              f"{spe_batch:.1f}s/ep (last {self.batch_done}) · {spe_all:.1f}s/ep (overall) · "
              f"ETA {_fmt(remaining * spe_all)} ({remaining} epochs left)", flush=True)
        self.batch_t0 = now; self.batch_done = 0


def _metrics_row(cfg, fold_k, y_true, proba):
    pred = np.asarray(M.LABELS)[proba.argmax(1)]
    mm = M.macro_metrics(y_true, pred)
    ap = M.ap_per_class(y_true, proba)
    row = dict(cfg_id=cfg["cfg_id"], lr=cfg["lr"], epochs=cfg["epochs"], fold=fold_k)
    row.update({k: mm[k] for k in ("macro_f1", "macro_f1_3class", "balanced_accuracy", "accuracy")})
    row.update({f"f1_{l}": mm[f"f1_{l}"] for l in M.LABELS})
    row.update({f"ap_{l}": ap[f"ap_{l}"] for l in M.LABELS})
    row["macro_pr_auc"] = ap["macro_pr_auc"]
    return row


def run_fold(cfg, fold_k, df, folds, force=False, on_epoch_end=None):
    """Train `cfg` on fold_k's train split, score its val split, cache val proba (.npz), return a
    metrics dict. Resumable: if the proba cache exists and not `force`, reload it (no retrain — and
    `on_epoch_end` is NOT called, so the timer's denominator stays accurate)."""
    import torch
    tr, va = folds[fold_k]
    va_df  = df.iloc[va]
    y_true = va_df["label"].to_numpy()
    npz    = PROBA_DIR / f"{cfg['cfg_id']}__fold{fold_k}.npz"

    if npz.exists() and not force:
        proba = np.load(npz)["proba"]
    else:
        seed = M.SEED + fold_k                                  # same per-fold randomness for every cfg
        np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        mdl, tok = M.train_tf(NAME, MLEN, BS, df.iloc[tr], lr=cfg["lr"], weight_decay=WD,
                              warmup_ratio=WU, epochs=cfg["epochs"], class_weighted=CW,
                              on_epoch_end=on_epoch_end)
        proba = M.predict_tf(mdl, tok, va_df, MLEN, return_proba=True).astype("float32")
        np.savez_compressed(npz, proba=proba, y_idx=va_df["label"].map(M.lab2i).to_numpy(),
                            row_id=va_df["row_id"].to_numpy())
        del mdl; torch.cuda.empty_cache()

    return _metrics_row(cfg, fold_k, y_true, proba)

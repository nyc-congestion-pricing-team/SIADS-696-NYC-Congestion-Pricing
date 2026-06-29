#!/usr/bin/env python3
"""STEP 2 — hyperparameter tuning with 5-FOLD cross-validation, then refit the best config on the
full training pool and save it (load-if-saved).

- Naive Bayes : GridSearchCV over NB_GRID, cv = the 5 grouped folds, scoring=f1_macro (CPU).
- XGBoost / transformers : Optuna with a **5-fold-CV objective**, run **trial-parallel across both
  GPUs** (two `_tune_worker.py` processes share one sqlite study). Best config is then refit on the
  full pool and saved.

Run (classifiers env):
    python tune_5fold.py                 # all four; --gpus 0,1
    python tune_5fold.py --model XGBoost
    python tune_5fold.py --force         # ignore saved tuned models and retune
"""
import argparse, json, os, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m5_common as M


def tune_nb(df):
    from sklearn.model_selection import GridSearchCV
    folds = M.fold_indices(df, M.CV_N_SPLITS)
    gs = GridSearchCV(M.build_nb(), M.NB_GRID, scoring="f1_macro", cv=folds, refit=True, n_jobs=-1)
    gs.fit(df[M.NB_COLS], df["label"])     # refit=True -> best refit on the FULL pool
    M.save_nb("tuned", gs.best_estimator_)
    bp = {k: (list(v) if isinstance(v, tuple) else v) for k, v in gs.best_params_.items()}
    M.write_tuned_hp("NaiveBayes", {**bp, "cv_macro_f1": round(float(gs.best_score_), 4)})
    print(f"NaiveBayes: 5-fold CV macro-F1 = {gs.best_score_:.4f}  best={bp}", flush=True)


def study_trials(model):
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    try:
        return len(optuna.load_study(study_name=model, storage=f"sqlite:///{M.STUDY_DB.as_posix()}").trials)
    except Exception:
        return 0


def run_workers(model, n_total, gpus, seed_offset=0):
    n_each = [n_total // len(gpus) + (1 if i < n_total % len(gpus) else 0) for i in range(len(gpus))]
    procs = []
    for i, g in enumerate(gpus):
        if n_each[i] == 0:
            continue
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=g, TOKENIZERS_PARALLELISM="false")
        cmd = [sys.executable, str(Path(__file__).parent / "_tune_worker.py"),
               "--model", model, "--n-trials", str(n_each[i]), "--seed", str(M.SEED + i + seed_offset)]
        procs.append(subprocess.Popen(cmd, env=env))
        print(f"  launched GPU{g}: {n_each[i]} trials of {model}", flush=True)
    rc = 0
    for p in procs:
        p.wait(); rc |= p.returncode
    return rc


def best_params(model):
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    st = optuna.load_study(study_name=model, storage=f"sqlite:///{M.STUDY_DB.as_posix()}")
    return st.best_params, float(st.best_value)


def refit_xgb(df, params, cv_f1):
    import pandas as pd
    X, y = M.get_xgb_cache(df)
    cwd = M.class_weights(pd.Series(y)); sw = pd.Series(y).map(cwd).to_numpy()
    p = dict(params); p["n_estimators"] = 1000
    m = M.build_xgb(p)                              # no early stopping -> train full on the pool
    m.fit(X, y, sample_weight=sw)
    M.save_xgb("tuned", m)
    M.write_tuned_hp("XGBoost", {**p, "cv_macro_f1": round(cv_f1, 4)})
    print(f"XGBoost: refit on full pool & saved (CV macro-F1 = {cv_f1:.4f})", flush=True)


def refit_tf(df, model, params, cv_f1):
    name, mlen, bs = M.TF_SPECS[model]
    hp = {"lr": params["lr"], "weight_decay": params["weight_decay"],
          "warmup_ratio": params["warmup_ratio"], "epochs": M.TF_TUNE_EPOCHS, "class_weighted": True}
    mdl, tok = M.train_tf(name, mlen, bs, df, **hp)
    M.save_tf("tuned", model, mdl, tok, hp)
    M.write_tuned_hp(model, {**hp, "max_len": mlen, "cv_macro_f1": round(cv_f1, 4)})
    print(f"{model}: refit on full pool & saved (CV macro-F1 = {cv_f1:.4f})", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="all", choices=["all"] + M.MODELS)
    ap.add_argument("--gpus", default="0,1")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--add-trials", type=int, default=0,
                    help="resume the existing Optuna study/studies, run N MORE trials (trial-parallel), "
                         "then re-refit the best config and overwrite the saved model.")
    ap.add_argument("--refit-only", action="store_true",
                    help="no new trials: just refit each model's CURRENT best study config and save "
                         "(use in the morning if an --add-trials batch was cut off before finishing).")
    args = ap.parse_args()
    gpus = [g.strip() for g in args.gpus.split(",") if g.strip()]
    todo = M.MODELS if args.model == "all" else [args.model]

    df = M.load_frames()["df"]
    print(f"training pool = {len(df)}   models = {todo}   folds = {M.CV_N_SPLITS}", flush=True)
    if any(m == "XGBoost" for m in todo):
        print("precomputing XGBoost features (shared cache) ...", flush=True); M.get_xgb_cache(df)

    # ── refit-only: capture the current best of each study without running new trials ──
    if args.refit_only:
        for model in [m for m in todo if m != "NaiveBayes"]:
            if study_trials(model) == 0:
                print(f"{model}: no study yet — skipping", flush=True); continue
            bp, cv_f1 = best_params(model)
            os.environ["CUDA_VISIBLE_DEVICES"] = gpus[0]
            (refit_xgb if model == "XGBoost" else (lambda d, p, c: refit_tf(d, model, p, c)))(df, bp, cv_f1)
        print("\nREFIT-ONLY DONE", flush=True); return

    # ── add-trials mode: extend existing studies (resume from the current best) ──
    if args.add_trials > 0:
        for model in [m for m in todo if m != "NaiveBayes"]:   # NB grid is exhaustive — nothing to add
            base = study_trials(model)
            print(f"\n== {model}: +{args.add_trials} trials (resuming from {base} existing) ==", flush=True)
            t0 = time.perf_counter()
            rc = run_workers(model, args.add_trials, gpus, seed_offset=base)
            if rc:
                print(f"!! {model} workers exited {rc}", flush=True); sys.exit(rc)
            bp, cv_f1 = best_params(model)
            os.environ["CUDA_VISIBLE_DEVICES"] = gpus[0]
            (refit_xgb if model == "XGBoost" else (lambda d, p, c: refit_tf(d, model, p, c)))(df, bp, cv_f1)
            print(f"   {model}: now {study_trials(model)} trials, best CV={cv_f1:.4f} "
                  f"({time.perf_counter()-t0:.0f}s)", flush=True)
        print("\nADD-TRIALS DONE", flush=True); return

    for model in todo:
        if M.exists("tuned", model) and not args.force:
            print(f"\n== {model}: tuned model already saved — skipping ==", flush=True); continue
        print(f"\n== tuning {model} (5-fold CV) ==", flush=True); t0 = time.perf_counter()
        if model == "NaiveBayes":
            tune_nb(df)
        else:
            n = M.N_TRIALS_XGB if model == "XGBoost" else M.N_TRIALS_TF
            rc = run_workers(model, n, gpus)
            if rc:
                print(f"!! {model} workers exited {rc}", flush=True); sys.exit(rc)
            bp, cv_f1 = best_params(model)
            os.environ["CUDA_VISIBLE_DEVICES"] = gpus[0]    # refit on the first GPU
            (refit_xgb if model == "XGBoost" else (lambda d, p, c: refit_tf(d, model, p, c)))(df, bp, cv_f1)
        print(f"   {model} done ({time.perf_counter()-t0:.0f}s)", flush=True)
    print("\nALL TUNING DONE", flush=True)


if __name__ == "__main__":
    main()

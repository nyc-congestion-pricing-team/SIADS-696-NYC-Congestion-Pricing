#!/usr/bin/env python3
"""Optuna tuning worker pinned to ONE GPU. Trial-parallel: several of these run at once against a
shared sqlite study, so each GPU runs complete 5-fold-CV trials concurrently. Launched by
tune_5fold.py — not meant to be run by hand. Objective = mean macro-F1 over 5 grouped CV folds.
"""
import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)       # XGBoost | DistilRoBERTa | ModernBERT
    ap.add_argument("--n-trials", type=int, required=True)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    import m5_common as M
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    df = M.load_frames()["df"]
    folds = M.fold_indices(df, M.CV_N_SPLITS)

    if args.model == "XGBoost":
        X, y = M.get_xgb_cache(df)
        def objective(trial):
            return M.cv_macro_f1_xgb(M.xgb_space(trial), X, y, folds)
    else:
        name, mlen, bs = M.TF_SPECS[args.model]
        def objective(trial):
            return M.cv_macro_f1_tf(name, mlen, bs, M.tf_space(trial), df, folds, trial=trial)

    study = optuna.create_study(
        study_name=args.model, storage=f"sqlite:///{M.STUDY_DB.as_posix()}", direction="maximize",
        load_if_exists=True, sampler=optuna.samplers.TPESampler(seed=args.seed),
        pruner=optuna.pruners.SuccessiveHalvingPruner())

    def _cb(study, trial):
        print(f"[{args.model}] trial {trial.number} state={trial.state.name} "
              f"value={trial.value if trial.value is not None else float('nan'):.4f} "
              f"best={study.best_value:.4f}", flush=True)

    study.optimize(objective, n_trials=args.n_trials, callbacks=[_cb])


if __name__ == "__main__":
    main()

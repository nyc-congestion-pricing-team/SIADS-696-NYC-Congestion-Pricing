#!/usr/bin/env python3
"""Sensitivity-sweep worker pinned to ONE GPU. Each worker processes an explicit list of configs
(passed by sweep_sensitivity.py); a config = ModernBERT@512 trained/scored on the 5 grouped CV folds.
Launched by the orchestrator — not meant to be run by hand.

Resumable: a (config, fold) whose proba cache already exists is reloaded, not retrained. Results are
checkpointed to results_shard{N}.csv after every fold.
"""
import argparse, sys
from pathlib import Path

# this folder (P16) holds sweep_common; m5_common lives cross-folder in P15 — both on the path.
_HERE = Path(__file__).resolve().parent
_P15  = Path(__file__).resolve().parent
for _p in (_HERE, _P15):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, default=0)            # only used for the output filename
    ap.add_argument("--cfg-ids", default="")                   # comma list; empty + --smoke -> smoke cfg
    ap.add_argument("--folds", default="")                     # "" = all 5; else comma list
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    import pandas as pd
    import m5_common as M
    import sweep_common as S

    df    = M.load_frames()["df"].reset_index(drop=True)
    folds = M.fold_indices(df, M.CV_N_SPLITS)
    all_cfgs = {c["cfg_id"]: c for c in S.build_configs()}

    if args.smoke:
        ids = [S.SMOKE_CFG]; fold_ids = [0]
    else:
        ids = [c for c in args.cfg_ids.split(",") if c]
        fold_ids = list(range(len(folds))) if not args.folds else [int(x) for x in args.folds.split(",")]
    mine = [all_cfgs[c] for c in ids]

    out = S.SENS_DIR / f"results_shard{args.shard}.csv"
    pend = S.pending_epochs(mine, fold_ids, force=args.force)
    print(f"[shard {args.shard}] {len(mine)} configs x {len(fold_ids)} folds  "
          f"-> {out.name}  ({pend} epochs to train)", flush=True)
    timer = S.EpochTimer(pend, every=10, label=f"[shard {args.shard}] ")

    rows = []
    for cfg in mine:
        for k in fold_ids:
            row = S.run_fold(cfg, k, df, folds, force=args.force, on_epoch_end=timer.tick)
            rows.append(row)
            print(f"[shard {args.shard}] {cfg['cfg_id']} (lr={cfg['lr']:.2e} ep={cfg['epochs']}) "
                  f"fold{k}: macroF1[4]={row['macro_f1']:.3f} macroPR-AUC={row['macro_pr_auc']:.3f}",
                  flush=True)
            pd.DataFrame(rows).to_csv(out, index=False)        # checkpoint after every fold
    print(f"[shard {args.shard}] DONE ({len(rows)} rows) -> {out}", flush=True)


if __name__ == "__main__":
    main()

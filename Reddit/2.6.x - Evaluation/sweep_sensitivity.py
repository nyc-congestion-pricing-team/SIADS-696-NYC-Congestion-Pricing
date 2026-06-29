#!/usr/bin/env python3
"""ModernBERT@512 LR / epochs SENSITIVITY sweep — orchestrator.

One-at-a-time local sensitivity around the tuned ModernBERT@512 config (grids + method live in
sweep_common.py). Splits the config list across GPUs (one _sweep_worker.py per GPU, each pinned via
CUDA_VISIBLE_DEVICES) using longest-processing-time balancing on epoch-cost, then merges the per-shard
results into sensitivity_results.csv. The full metric suite is recorded per (config, fold); there is
NO full-pool refit and NO model weights are saved (only tiny per-fold proba caches).

Run (classifiers env — C:\\Users\\Freya\\.venvs\\mads-m2-classifiers\\Scripts\\python.exe):
    python sweep_sensitivity.py --gpus 0,1          # full sweep (~85 fold-trains, ~3 h wall)
    python sweep_sensitivity.py --gpus 0 --smoke    # 1 config (1 epoch) x 1 fold — pipeline sanity
    python sweep_sensitivity.py --merge-only        # just rebuild the merged CSV from shard files
"""
import argparse, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent           # P16 (sweep_common + the worker live here)
P15  = Path(__file__).resolve().parent
for _p in (HERE, P15):                            # m5_common is cross-folder in P15
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import m5_common as M
import sweep_common as S

WORKER = HERE / "_sweep_worker.py"


def assign(cfgs, n):
    """Longest-processing-time bin-packing by epoch-cost so both GPUs finish around the same time."""
    bins = [[] for _ in range(n)]; load = [0] * n
    for c in sorted(cfgs, key=lambda c: -c["epochs"]):
        j = min(range(n), key=lambda i: load[i])
        bins[j].append(c["cfg_id"]); load[j] += c["epochs"] * M.CV_N_SPLITS
    return bins, load


def merge():
    import pandas as pd
    parts = sorted(S.SENS_DIR.glob("results_shard*.csv"))
    if not parts:
        print("no shard CSVs to merge"); return
    df = (pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
            .drop_duplicates(["cfg_id", "fold"], keep="last")
            .sort_values(["epochs", "lr", "fold"]))
    df.to_csv(S.HERE_CSV, index=False)
    print(f"merged {len(parts)} shards -> {S.HERE_CSV.name}  ({len(df)} rows, "
          f"{df['cfg_id'].nunique()} configs)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpus", default="0,1")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--merge-only", action="store_true")
    args = ap.parse_args()

    if args.merge_only:
        merge(); return

    gpus = [g.strip() for g in args.gpus.split(",") if g.strip()]

    if args.smoke:
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpus[0], TOKENIZERS_PARALLELISM="false")
        print(f"SMOKE: 1 config (1 epoch) x 1 fold on GPU{gpus[0]}", flush=True)
        sys.exit(subprocess.call([sys.executable, str(WORKER), "--smoke"], env=env))

    cfgs = S.build_configs()
    n_trains = sum(M.CV_N_SPLITS for _ in cfgs)
    n_epochs = sum(c["epochs"] * M.CV_N_SPLITS for c in cfgs)
    bins, load = assign(cfgs, len(gpus))
    print(f"configs={len(cfgs)}  fold-trains={n_trains}  total-epochs={n_epochs} "
          f"(= {n_epochs / S.EP0:.0f} {S.EP0}-epoch-equiv)  gpus={gpus}", flush=True)
    for g, ids, ld in zip(gpus, bins, load):
        print(f"  GPU{g}: {len(ids)} configs, {ld} epoch-folds", flush=True)

    t0 = time.perf_counter()
    procs = []
    for i, (g, ids) in enumerate(zip(gpus, bins)):
        if not ids:
            continue
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=g, TOKENIZERS_PARALLELISM="false")
        cmd = [sys.executable, str(WORKER), "--shard", str(i), "--cfg-ids", ",".join(ids)]
        if args.force:
            cmd.append("--force")
        procs.append(subprocess.Popen(cmd, env=env))
    rc = 0
    for p in procs:
        p.wait(); rc |= p.returncode
    if rc:
        print(f"!! a worker exited {rc}", flush=True); sys.exit(rc)

    merge()
    print(f"\nSWEEP DONE ({time.perf_counter() - t0:.0f}s). "
          f"Build the chart: python build_sensitivity_notebook.py", flush=True)


if __name__ == "__main__":
    main()

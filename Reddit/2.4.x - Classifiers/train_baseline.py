#!/usr/bin/env python3
"""STEP 1 — baseline models with LIBRARY-DEFAULT settings, trained on the full training pool and
saved to saved_models/baseline/ (load-if-saved). Defaults: ComplementNB(alpha=1.0) on unigram
TF-IDF; XGBoost out-of-the-box; transformers @512 with HF-style defaults (lr 5e-5, 3 epochs,
unweighted CE). These are a reference point for the 5-fold-CV-tuned models.

Run (classifiers env):
    python train_baseline.py            # uses the one visible GPU (set CUDA_VISIBLE_DEVICES)
    python train_baseline.py --force
"""
import argparse, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
import m5_common as M


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--force", action="store_true"); args = ap.parse_args()
    df = M.load_frames()["df"]
    print(f"training pool = {len(df)}", flush=True)

    if M.exists("baseline", "NaiveBayes") and not args.force:
        print("NaiveBayes baseline: already saved", flush=True)
    else:
        nb = M.build_nb(**M.NB_DEFAULT); nb.fit(df[M.NB_COLS], df["label"])
        M.save_nb("baseline", nb); print("NaiveBayes baseline: saved", flush=True)

    if M.exists("baseline", "XGBoost") and not args.force:
        print("XGBoost baseline: already saved", flush=True)
    else:
        X, y = M.get_xgb_cache(df); m = M.build_xgb(M.XGB_DEFAULT); m.fit(X, y)
        M.save_xgb("baseline", m); print("XGBoost baseline: saved", flush=True)

    import torch
    for model in ["DistilRoBERTa", "ModernBERT"]:
        if M.exists("baseline", model) and not args.force:
            print(f"{model} baseline: already saved", flush=True); continue
        name, mlen, bs = M.TF_SPECS[model]; t0 = time.perf_counter()
        mdl, tok = M.train_tf(name, mlen, bs, df,
                              lr=M.TF_DEFAULT["lr"], weight_decay=M.TF_DEFAULT["weight_decay"],
                              warmup_ratio=M.TF_DEFAULT["warmup_ratio"], epochs=M.TF_DEFAULT["epochs"],
                              class_weighted=M.TF_DEFAULT["class_weighted"])
        M.save_tf("baseline", model, mdl, tok, M.TF_DEFAULT)
        del mdl; torch.cuda.empty_cache()
        print(f"{model} baseline: saved ({time.perf_counter()-t0:.0f}s)", flush=True)
    print("BASELINE DONE", flush=True)


if __name__ == "__main__":
    main()

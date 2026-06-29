#!/usr/bin/env python3
"""Sharded ModernBERT word-level Integrated-Gradients attribution — one GPU per process.

Each instance attributes a stride-shard of the training pool and writes a PARTIAL table
[class, token, attr_sum, n] (sum + count, so shards merge exactly: mean = Σsum / Σn).
Word-level (offset mapping), mean-of-subword IG, TARGET-span only, bf16 autocast, no sampling.

Run two instances in parallel (the notebook launch cell does this for you):
  python attribute_tokens.py --gpu 0 --shard 0 --n-shards 2 --out outputs/raw_target.shard0.csv
  python attribute_tokens.py --gpu 1 --shard 1 --n-shards 2 --out outputs/raw_target.shard1.csv

Then merge the two partials in the notebook (see merge cell).
"""
import os, sys, time, json, argparse


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpu", required=True)                 # physical GPU id (becomes cuda:0 in-process)
    ap.add_argument("--shard", type=int, required=True)     # this process handles texts[shard::n_shards]
    ap.add_argument("--n-shards", type=int, default=2)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-steps", type=int, default=24)
    ap.add_argument("--ibs", type=int, default=32)          # IG internal_batch_size
    ap.add_argument("--no-target-only", action="store_true")
    ap.add_argument("--p15", default=".")
    args = ap.parse_args()

    # MUST set device visibility before importing torch
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    import numpy as np, pandas as pd, torch
    from collections import defaultdict
    from captum.attr import LayerIntegratedGradients
    from transformers import AutoTokenizer, AutoModelForSequenceClassification

    sys.path.insert(0, args.p15)
    import m5_common as m5

    tag = f"gpu{args.gpu} shard{args.shard}"
    target_only = not args.no_target_only
    markers = ("[CONTEXT]", "[TARGET]", "[OP]")

    # ── tuned ModernBERT (matches the deployment window: max_len 512, left-truncation) ──
    p = m5.model_path("tuned", "ModernBERT")
    cfg = json.loads((p / "inference_config.json").read_text())
    max_len = cfg.get("max_len", 512)
    tok = AutoTokenizer.from_pretrained(p)
    tok.truncation_side = cfg.get("truncation_side", "left")   # keep the TARGET (end) when truncating
    model = AutoModelForSequenceClassification.from_pretrained(p).to("cuda").eval()
    id2label = model.config.id2label
    ref_id = tok.pad_token_id if tok.pad_token_id is not None else tok.cls_token_id
    lig = LayerIntegratedGradients(
        lambda ids, am, t: model(input_ids=ids, attention_mask=am).logits[:, t],
        model.get_input_embeddings())

    # ── pool, strided shard (interleaved → both GPUs get a balanced length mix) ──
    texts = m5.load_frames()["df"]["text"].tolist()
    shard = texts[args.shard::args.n_shards]
    print(f"[{tag}] {len(shard)} of {len(texts)} pool items | n_steps={args.n_steps} ibs={args.ibs} "
          f"target_only={target_only}", flush=True)

    # ── predict (group by predicted class) + cache encodings ──
    preds, cache = [], []
    with torch.no_grad():
        for t in shard:
            enc = tok(t, return_tensors="pt", truncation=True, max_length=max_len,
                      return_offsets_mapping=True)
            wids, offs = enc.word_ids(0), enc["offset_mapping"][0].tolist()
            ids, am = enc["input_ids"].to("cuda"), enc["attention_mask"].to("cuda")
            with torch.autocast("cuda", dtype=torch.bfloat16):
                preds.append(int(model(input_ids=ids, attention_mask=am).logits.argmax(-1)))
            cache.append((t, ids, am, wids, offs))
    preds = np.array(preds)

    # ── attribute ──
    acc = {lbl: defaultdict(list) for lbl in id2label.values()}
    total, done, t0 = len(shard), 0, time.time()
    for cls_i, cls_name in id2label.items():
        for i in np.where(preds == cls_i)[0]:
            t, ids, am, wids, offs = cache[i]
            baseline = torch.full_like(ids, ref_id)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                a = lig.attribute(inputs=ids, baselines=baseline,
                                  additional_forward_args=(am, cls_i),
                                  n_steps=args.n_steps, internal_batch_size=args.ibs)
            a = a.float().sum(dim=-1).squeeze(0)
            a = (a / (torch.norm(a) + 1e-12)).tolist()

            mspans = []
            for mk in markers:
                pp = t.find(mk)
                while pp != -1:
                    mspans.append((pp, pp + len(mk))); pp = t.find(mk, pp + 1)
            in_marker = lambda s, e: any(s < me and ms < e for ms, me in mspans)
            tgt_start = t.find("[TARGET]") if target_only else -1

            agg = {}
            for wid, av, (s, e) in zip(wids, a, offs):
                if wid is None or e <= s:
                    continue
                if wid not in agg:
                    agg[wid] = [0.0, s, e, 0]
                agg[wid][0] += av; agg[wid][1] = min(agg[wid][1], s)
                agg[wid][2] = max(agg[wid][2], e); agg[wid][3] += 1
            for wid, (asum, s, e, npc) in agg.items():
                if tgt_start != -1 and s < tgt_start:
                    continue
                word = t[s:e].strip().lower()
                if not word or not any(ch.isalnum() for ch in word) or in_marker(s, e):
                    continue
                acc[cls_name][word].append(float(asum / npc))

            done += 1
            if done % 50 == 0 or done == total:
                el = time.time() - t0; eta = el / done * (total - done)
                print(f"[{tag}] {done}/{total} ({100*done/total:.0f}%) "
                      f"elapsed {el/60:.1f}m eta {eta/60:.1f}m", flush=True)

    # ── partial table: per (class, word) SUM + COUNT (merge across shards = Σsum / Σn) ──
    rows = [dict(**{"class": c}, token=w, attr_sum=float(np.sum(v)), n=len(v))
            for c, d in acc.items() for w, v in d.items()]
    pd.DataFrame(rows).to_csv(args.out, index=False)
    print(f"[{tag}] DONE — wrote {args.out} ({len(rows)} rows) in {(time.time()-t0)/60:.1f}m", flush=True)


if __name__ == "__main__":
    main()

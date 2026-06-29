"""
analysis_utils.py  —  Shared helpers for the stance-analysis notebooks.
================================================================================
Loading, geography tagging, day-part/time bucketing, rollups, confidence
intervals, and the standard plot styling. Notebooks do:

    import config as C
    import analysis_utils as A

and lean on these so each notebook stays about ANALYSIS, not plumbing.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

import config as C

# =============================================================================
# Styling
# =============================================================================
def apply_style():
    """Apply the team palette + clean defaults to matplotlib (call once per nb)."""
    mpl.rcParams.update({
        "figure.figsize": (11, 5.5),
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#E6ECEE",
        "grid.linewidth": 0.8,
        "axes.edgecolor": "#5A6B6F",
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "font.size": 10.5,
        "legend.frameon": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    })

def stance_color(stance: str) -> str:
    return C.STANCE_COLORS.get(stance, "#888888")

# =============================================================================
# Geography
# =============================================================================
def add_geo(df: pd.DataFrame, sub_col: str = "subreddit") -> pd.DataFrame:
    """Attach geo_tier / cbd_zone / is_topical (case-insensitive match)."""
    key = df[sub_col].astype(str).str.lower()
    m = C.SUBREDDIT_MAP
    out = df.copy()
    out["geo_tier"]   = key.map(lambda s: m.get(s, {}).get("geo_tier", "Unmapped"))
    out["cbd_zone"]   = key.map(lambda s: m.get(s, {}).get("cbd_zone", None))
    out["is_topical"] = key.map(lambda s: m.get(s, {}).get("is_topical", False))
    return out

# =============================================================================
# Time: NYC-local conversion, day-parts, and grain bucketing
# =============================================================================
def to_local(utc_seconds: pd.Series) -> pd.Series:
    """epoch seconds (UTC) -> tz-naive NYC-local Timestamps."""
    return (pd.to_datetime(utc_seconds, unit="s", utc=True)
              .dt.tz_convert(C.TIMEZONE).dt.tz_localize(None))

def assign_daypart(hours) -> pd.Series:
    """Map hour-of-day (0-23) to a day-part label using config.DAYPARTS.

    Handles wrap-around buckets like overnight (22 -> 6).
    """
    hours = pd.Series(hours).astype(int)
    out = pd.Series(pd.NA, index=hours.index, dtype="object")
    for name, (start, end) in C.DAYPARTS.items():
        if start < end:
            mask = (hours >= start) & (hours < end)
        else:  # wrap past midnight
            mask = (hours >= start) | (hours < end)
        out[mask] = name
    return out

def time_bucket(et_date, grain: str):
    """Collapse a date to the start of its time bucket for a given grain.

    grain in {"daily", "weekly", "monthly"}.  Returns a Timestamp (period start).
    For day-part rollups, group on (date, daypart) directly instead.
    """
    ts = pd.to_datetime(et_date)
    if grain == "daily":
        return ts.normalize() if isinstance(ts, pd.Timestamp) else ts.dt.normalize()
    if grain == "weekly":   # ISO week, Monday start
        return ts.dt.to_period("W-MON").dt.start_time if hasattr(ts, "dt") \
               else ts.to_period("W-MON").start_time
    if grain == "monthly":
        return ts.dt.to_period("M").dt.start_time if hasattr(ts, "dt") \
               else ts.to_period("M").start_time
    raise ValueError(f"unknown grain {grain!r}")

# =============================================================================
# Loading
# =============================================================================
def load_stance_items(drop_offtopic: bool = False) -> pd.DataFrame:
    """Load the item-level stance file with NYC-local time + geo attached.

    Adds: dt_local, et_date, hour, daypart, geo_tier, cbd_zone, is_topical.
    Keep off-topic by default (track it as a relevance signal); the analysis
    notebooks restrict to on-topic where appropriate.
    """
    df = pd.read_parquet(C.STANCE_FILE)
    df["dt_local"] = to_local(df["created_utc"])
    df["et_date"]  = df["dt_local"].dt.normalize()
    df["hour"]     = df["dt_local"].dt.hour
    df["daypart"]  = assign_daypart(df["hour"])
    df = add_geo(df)
    if drop_offtopic:
        df = df[df["stance_pred"] != "off-topic"].copy()
    return df

def load_rollup(name: str) -> pd.DataFrame:
    """Load a cached rollup parquet from the rollups/ folder (built in nb 01)."""
    path = C.ROLLUPS / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run 01_data_prep.ipynb first to build the rollups.")
    return pd.read_parquet(path)

# =============================================================================
# Rollups from the cached hourly tables
# =============================================================================
def aggregate(hourly: pd.DataFrame, grain: str, by=("geo_tier",),
              count_col: str = "n", stance_col: str | None = "stance") -> pd.DataFrame:
    """Aggregate an hourly-grain table up to a coarser time grain.

    hourly must have columns: et_date, hour, the grouping cols in `by`, the
    `count_col`, and (optionally) `stance_col`.

    grain: "daypart" | "daily" | "weekly" | "monthly".
      - "daypart" groups on (daypart, *by[, stance]) collapsing across dates,
        i.e. the typical-day profile. (Use a date filter beforehand for a window.)
      - others group on (period_start, *by[, stance]).
    """
    df = hourly.copy()
    group_cols = list(by) + ([stance_col] if stance_col else [])
    if grain == "daypart":
        df["daypart"] = assign_daypart(df["hour"])
        keys = ["daypart"] + group_cols
    else:
        df["period"] = time_bucket(df["et_date"], grain)
        keys = ["period"] + group_cols
    return (df.groupby(keys, observed=True)[count_col].sum()
              .reset_index())

# =============================================================================
# Stance shares + net index
# =============================================================================
def stance_shares(long_counts: pd.DataFrame, index_cols, stance_col="stance",
                  count_col="n", include=("anti", "neutral", "pro")) -> pd.DataFrame:
    """Pivot long stance counts -> wide shares within each index group.

    Returns one row per index group with: n_anti/n_neutral/n_pro, n_total,
    share_* , and net = share_pro - share_anti.
    """
    d = long_counts[long_counts[stance_col].isin(include)]
    wide = (d.pivot_table(index=index_cols, columns=stance_col, values=count_col,
                          aggfunc="sum", fill_value=0, observed=True)
              .reset_index())
    for s in include:
        if s not in wide:
            wide[s] = 0
    wide = wide.rename(columns={s: f"n_{s}" for s in include})
    ncols = [f"n_{s}" for s in include]
    wide["n_total"] = wide[ncols].sum(axis=1)
    for s in include:
        wide[f"share_{s}"] = np.where(wide["n_total"] > 0,
                                      wide[f"n_{s}"] / wide["n_total"], np.nan)
    wide["net"] = wide.get("share_pro", 0) - wide.get("share_anti", 0)
    return wide

def net_stance_soft(items: pd.DataFrame) -> pd.Series:
    """Confidence-weighted stance per item: p_pro - p_anti  (range -1..1).

    Renormalize over on-topic mass so off-topic probability doesn't shrink it.
    """
    on = items[["p_anti", "p_neutral", "p_pro"]].sum(axis=1).replace(0, np.nan)
    return (items["p_pro"] - items["p_anti"]) / on

def entropy(items: pd.DataFrame, cols=("p_anti", "p_neutral", "p_pro")) -> pd.Series:
    """Shannon entropy over the on-topic stance distribution (model ambivalence)."""
    p = items[list(cols)].to_numpy(dtype=float)
    p = p / p.sum(axis=1, keepdims=True).clip(min=1e-12)
    return pd.Series(-(p * np.log2(np.clip(p, 1e-12, 1))).sum(axis=1), index=items.index)

# =============================================================================
# Confidence intervals
# =============================================================================
def net_ci(p_pro, p_anti, n, z: float = 1.96):
    """Normal-approx CI half-width for the net index (p_pro - p_anti).

    Uses the variance of a difference of two multinomial cells:
        Var = (p_pro + p_anti - (p_pro - p_anti)**2) / n
    Returns (lo, hi) around net = p_pro - p_anti.
    """
    p_pro = np.asarray(p_pro, float); p_anti = np.asarray(p_anti, float)
    n = np.asarray(n, float)
    net = p_pro - p_anti
    with np.errstate(divide="ignore", invalid="ignore"):
        var = (p_pro + p_anti - net**2) / n
        half = z * np.sqrt(np.clip(var, 0, None))
    lo = np.where(n > 0, net - half, np.nan)
    hi = np.where(n > 0, net + half, np.nan)
    return lo, hi

def wilson_ci(k, n, z: float = 1.96):
    """Wilson score interval for a binomial proportion. Vectorized.

    Returns (lo, hi). Use for share error bars -- it behaves at small n where
    the normal approximation breaks.
    """
    k = np.asarray(k, dtype=float); n = np.asarray(n, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        p = k / n
        denom = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denom
        half = (z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
        lo, hi = center - half, center + half
    lo = np.where(n > 0, np.clip(lo, 0, 1), np.nan)
    hi = np.where(n > 0, np.clip(hi, 0, 1), np.nan)
    return lo, hi

# =============================================================================
# Share of conversation (numerator / denominator)
# =============================================================================
def share_of_conversation(topic_counts: pd.DataFrame, total_counts: pd.DataFrame,
                          on=("period", "geo_tier")) -> pd.DataFrame:
    """Merge topic-item counts with total-activity counts -> salience share.

    Both inputs are long tables with the join keys in `on`, plus an `n` column.
    Returns the merge with n_topic, n_total, share_topic.
    """
    a = topic_counts.rename(columns={"n": "n_topic"})
    b = total_counts.rename(columns={"n": "n_total"})
    m = a.merge(b, on=list(on), how="left")
    m["share_topic"] = m["n_topic"] / m["n_total"]
    return m

# =============================================================================
# Plot helpers
# =============================================================================
def annotate_events(ax, events=None, grain_is_time=True, top=True):
    """Draw vertical dashed lines + labels for the config event timeline."""
    if not grain_is_time:
        return
    events = events if events is not None else C.EVENTS
    ymin, ymax = ax.get_ylim()
    for ev in events:
        x = pd.Timestamp(ev["date"])
        primary = ev.get("primary", False)
        ax.axvline(x, color=C.PALETTE["deep_teal"] if primary else "#9AA7AB",
                   ls="--", lw=1.6 if primary else 1.0, alpha=0.9, zorder=1)
        ax.annotate(ev["label"], xy=(x, ymax if top else ymin),
                    xytext=(3, -2 if top else 10), textcoords="offset points",
                    rotation=90, va="top" if top else "bottom", ha="left",
                    fontsize=8, color="#3A4B4F",
                    fontweight="bold" if primary else "normal")

def stacked_share(ax, wide, xcol, stances=None, title=None):
    """100%-stacked stance share area/bar over time on `ax`."""
    stances = stances or C.STANCE_ORDER
    x = wide[xcol]
    bottoms = np.zeros(len(wide))
    for s in stances:
        col = f"share_{s}"
        ax.fill_between(x, bottoms, bottoms + wide[col].values,
                        color=stance_color(s), label=s, alpha=0.95, step="mid")
        bottoms = bottoms + wide[col].fillna(0).values
    ax.set_ylim(0, 1); ax.set_ylabel("share of on-topic items")
    if title: ax.set_title(title)
    ax.legend(ncol=len(stances), loc="upper center", bbox_to_anchor=(0.5, -0.12))
    return ax

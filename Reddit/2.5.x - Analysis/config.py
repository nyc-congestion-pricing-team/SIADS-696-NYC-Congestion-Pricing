"""
config.py  —  Single edit-hub for the NYC Congestion Pricing stance analysis.
================================================================================
Everything a teammate is likely to tweak lives HERE, not buried in a notebook:

    * file paths            (local vs Deepnote)
    * the color palette
    * the subreddit -> geography mapping (tiers, CBD split, topical flags)
    * the day-part buckets
    * the canonical event timeline

Notebooks do `import config as C` and read these. Change a value here once and
every notebook picks it up on its next run.
"""
from __future__ import annotations
import os
from pathlib import Path

# -----------------------------------------------------------------------------
# 1. PATHS
# -----------------------------------------------------------------------------
# This file lives in ".../696 - Milestone 2/Project Data - 12 - Analysis".
BASE = Path(__file__).resolve().parent

# DATA_ROOT defaults to the Milestone-2 folder (the parent of this analysis
# folder). On Deepnote the data usually mounts elsewhere -- set the env var
# MADS_DATA_ROOT (or just edit the fallback below) to point at wherever
# "Project Data ..." lives in that environment.
DATA_ROOT = Path(os.environ.get("MADS_DATA_ROOT", BASE.parent / "data"))   # ../data (shared, git-ignored)

# Numerator: model stance predictions (one row per post/comment).
STANCE_FILE = DATA_ROOT / "stance_predictions_modernbert_tuned.parquet"

# Denominators: the FULL unfiltered conversation on these subreddits.
# Used only to compute "share of conversation" (topic items / all items).
ALL_COMMENTS = DATA_ROOT / "all_comments.parquet"
ALL_POSTS    = DATA_ROOT / "all_posts.parquet"

# Cached rollups written by 01_data_prep.ipynb and reloaded by every other nb.
ROLLUPS = BASE / "rollups"
ROLLUPS.mkdir(exist_ok=True)

# -----------------------------------------------------------------------------
# 2. COLOR PALETTE
# -----------------------------------------------------------------------------
# The team palette (from the project brief).
PALETTE = {
    "deep_teal":  "#006D77",
    "teal":       "#83C5BE",
    "pale":       "#EDF6F9",
    "pink":       "#FFDDD2",
    "terracotta": "#E29578",
}

# Stance -> color. Read as a diverging scale: cool teal = PRO, warm terracotta =
# ANTI, muted in-between = neutral, grey = off-topic (de-emphasized).
STANCE_COLORS = {
    "pro":       "#006D77",   # deep teal
    "neutral":   "#83C5BE",   # light teal
    "anti":      "#E29578",   # terracotta
    "off-topic": "#AAB7BC",   # muted grey (kept off the diverging scale)
}

# Order used everywhere stance is stacked / categorical (bottom -> top).
STANCE_ORDER = ["anti", "neutral", "pro"]          # on-topic stances
STANCE_ORDER_ALL = ["anti", "neutral", "pro", "off-topic"]

# -----------------------------------------------------------------------------
# 3. DAY-PARTS   (local NYC time -- see TIMEZONE)
# -----------------------------------------------------------------------------
# created_utc is UTC; we convert to NYC local time before bucketing, because
# discussion clusters by people's local clock, not UTC.
#
# Each bucket is (start_hour_inclusive, end_hour_exclusive) on a 24h clock.
# Wrap-around (e.g. overnight 22->6) is handled by analysis_utils.assign_daypart.
#
# >>> EDIT FREELY to match the teammate doing the day-part rollups. <<<
TIMEZONE = "America/New_York"
DAYPARTS = {
    "morning":   (6, 12),
    "afternoon": (12, 17),
    "evening":   (17, 22),
    "overnight": (22, 6),
}
# Order for plotting / categorical axis.
DAYPART_ORDER = ["morning", "afternoon", "evening", "overnight"]

# -----------------------------------------------------------------------------
# 4. EVENT TIMELINE
# -----------------------------------------------------------------------------
# Canonical congestion-pricing events. The event-study notebook annotates these
# and also lets you append your own (outlier dates the day-part teammate finds).
# 'primary' marks the main natural-experiment boundary.
EVENTS = [
    {"date": "2024-06-05", "label": "Hochul 'pause'",      "primary": False},
    {"date": "2024-11-14", "label": "Revival / re-approval","primary": False},
    {"date": "2025-01-05", "label": "Launch",               "primary": True},
    {"date": "2025-02-19", "label": "Federal challenge",    "primary": False},
]

# -----------------------------------------------------------------------------
# 5. SUBREDDIT -> GEOGRAPHY MAPPING
# -----------------------------------------------------------------------------
# Each subreddit maps to:
#   geo_tier   : coarse geographic bucket (the design-doc tiers)
#   cbd_zone   : Manhattan-only CBD split. One of:
#                "CBD" (below 60th St), "Non-CBD" (above 60th),
#                "Manhattan-whole" (island-ambiguous), or None (not Manhattan).
#   is_topical : True  = non-geographic activist sub (strong pro selection bias)
#                "partial" = transit/cycling sub (geo-ish but topical-leaning)
#                False = ordinary geographic sub
#
# Matching is case-insensitive (see analysis_utils.add_geo), so casing here only
# needs to be human-readable.
#
# NOTE: CBD-Manhattan is THIN (eastvillage only, n~136 total). Treat the
# CBD-vs-Non-CBD split as suggestive, not conclusive -- CIs will be wide.
SUBREDDIT_MAP: dict[str, dict] = {}

def _add(subs, geo_tier, cbd_zone=None, is_topical=False):
    for s in subs:
        SUBREDDIT_MAP[s.lower()] = {
            "geo_tier": geo_tier, "cbd_zone": cbd_zone, "is_topical": is_topical,
        }

# Manhattan core  (+ CBD split)
_add(["eastvillage"],                          "Manhattan core", cbd_zone="CBD")
_add(["uppereastside", "Upperwestside", "Harlem"], "Manhattan core", cbd_zone="Non-CBD")
_add(["manhattan"],                            "Manhattan core", cbd_zone="Manhattan-whole")
# Outer boroughs
_add(["Brooklyn", "parkslope", "williamsburg", "Greenpoint", "Bushwick", "BedStuy",
      "crownheights", "sunsetpark", "Queens", "astoria", "longislandcity",
      "jacksonheights", "ForestHills", "Flushing", "ridgewood", "bronx",
      "statenisland"], "Outer boroughs")
# NYC citywide (borough-ambiguous)
_add(["nyc", "newyorkcity", "AskNYC"],         "NYC citywide")
# NY state / Long Island shed
_add(["newyork", "longisland"],                "NY state / LI shed")
# Lower Hudson Valley shed
_add(["hudsonvalley", "Westchester", "yonkers", "NewRochelle", "Rockland"],
     "Hudson Valley shed")
# Connecticut commuter shed
_add(["Connecticut", "Greenwich"],             "Connecticut shed")
# New Jersey commuter shed
_add(["newjersey", "jerseycity", "Hoboken", "bergencounty", "Newark", "montclair"],
     "New Jersey shed")
# Transit / cycling (NYC-metro, topical-leaning)
_add(["nycrail", "NYCbike", "nycbus", "MicromobilityNYC", "NJTransit"],
     "Transit / cycling", is_topical="partial")
# Topical, non-geographic (quarantined from geographic comparison)
_add(["transit", "fuckcars", "urbanplanning"], "Topical (activist)", is_topical=True)

# Tier display order (used for small-multiples etc.). Topical tiers last.
GEO_TIER_ORDER = [
    "Manhattan core", "Outer boroughs", "NYC citywide", "NY state / LI shed",
    "Hudson Valley shed", "Connecticut shed", "New Jersey shed",
    "Transit / cycling", "Topical (activist)",
]
CBD_ZONE_ORDER = ["CBD", "Non-CBD", "Manhattan-whole"]

# -----------------------------------------------------------------------------
# 6. ANALYSIS DEFAULTS
# -----------------------------------------------------------------------------
# Suppress cells with fewer than this many on-topic items (avoids drawing
# conclusions from a handful of comments). Notebooks expose this so you can tune.
MIN_N = 30

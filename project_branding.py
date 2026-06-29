"""Shared visual branding constants for the NYC mobility notebooks."""

BRAND_COLORS = {
    "dark_teal": "#006D77",
    "seafoam": "#83C5BE",
    "ice": "#EDF6F9",
    "pale_peach": "#FFDDD2",
    "terracotta": "#E29578",
}

BRAND_COLOR_SEQUENCE = [
    BRAND_COLORS["dark_teal"],
    BRAND_COLORS["terracotta"],
    BRAND_COLORS["seafoam"],
    BRAND_COLORS["pale_peach"],
    BRAND_COLORS["ice"],
]

BRAND_DIVERGING_SEQUENCE = [
    BRAND_COLORS["dark_teal"],
    BRAND_COLORS["seafoam"],
    BRAND_COLORS["ice"],
    BRAND_COLORS["pale_peach"],
    BRAND_COLORS["terracotta"],
]

BRAND_MAP_COLORS = {
    "primary": BRAND_COLORS["dark_teal"],
    "secondary": BRAND_COLORS["terracotta"],
    "supporting": BRAND_COLORS["seafoam"],
    "background": BRAND_COLORS["ice"],
    "soft_highlight": BRAND_COLORS["pale_peach"],
}

BRAND_PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "white",
        "plot_bgcolor": BRAND_COLORS["ice"],
        "font": {"color": BRAND_COLORS["dark_teal"]},
        "colorway": BRAND_COLOR_SEQUENCE,
    }
}

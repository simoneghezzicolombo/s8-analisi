from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.colors as mc
import colorsys
import json

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data" / "reproducibility" / "top20"
DATA_PATH = DATA_DIR / "top20_lines.csv"
FIG_DIR = ROOT / "figures" / "reproducibility" / "top20"
FIG_DIR.mkdir(parents=True, exist_ok=True)

S8_FILL = "#F8B1B0"
S8_DARK = "#8E435D"
S8_EDGE = "#A64D6A"
BG = "#FAFAF7"
TRACK = "#ECECE8"
TRACK_EDGE = "#DFDFDA"
TEXT = "#222222"
MUTED = "#666666"
GRID = "#E6E6E1"
LOMBARDY_CODES = {"S5", "S8", "RE6", "S6", "S1", "S11", "RE80", "S13", "S9"}

def load_data():
    df = pd.read_csv(DATA_PATH).sort_values("rank").head(20).copy()
    with open(DATA_DIR / "label_map.json", encoding="utf-8") as f:
        label_map = json.load(f)
    df["label"] = df["line_name"].map(label_map).fillna(df["line_name"])
    df["rank_label"] = df["rank"].astype(str) + ". " + df["label"]
    return df

def adjust_lightness(color, amount=1.0):
    try:
        c = mc.cnames[color]
    except Exception:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])

def softened(hex_color, amount=1.14):
    try:
        return adjust_lightness(hex_color, amount)
    except Exception:
        return "#C8C8C8"

def lombardy_or_grey_color(row, neutral="#BDBDBD", amount=1.12):
    if row["line_code"] == "S8":
        return S8_FILL
    if row["line_code"] in LOMBARDY_CODES:
        return softened(row["color_hex"], amount)
    return neutral

def rounded_rect(ax, x, y, w, h, facecolor, edgecolor="none", lw=0, zorder=1):
    patch = FancyBboxPatch(
        (x, y - h/2), w, h,
        boxstyle=f"round,pad=0,rounding_size={h/2}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=lw,
        zorder=zorder
    )
    ax.add_patch(patch)
    return patch

def add_footer(fig, style_note):
    fig.text(
        0.065, 0.055,
        "Fonte: elaborazione su dati Trenord, Cotral, Trenitalia e Regioni. Lombardia: campagne 2025 di maggio, luglio e novembre.",
        ha="left", va="bottom", fontsize=8.7, color="#555555"
    )
    fig.text(
        0.935, 0.055,
        style_note,
        ha="right", va="bottom", fontsize=8.7, color="#777777"
    )

def clean_axes(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

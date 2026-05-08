from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path

import bbcstyle
import matplotlib.font_manager as fm
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent / "output"
FONT_DIR = ROOT / "grafici_rifatti_v01" / "github_bbcstyle_top20" / "assets" / "fonts"

GREEN = "#1f642c"
GREEN_DARK = "#174f24"
OFF_WHITE = "#f7fbf4"
SOFT_WHITE = "#dfeee0"
MUTED_WHITE = "#bdd8bf"
GRID = (1, 1, 1, 0.18)
BAR = (1, 1, 1, 0.28)
BAR_WEAK = (1, 1, 1, 0.18)
S8_FILL = "#f2b8c1"
S8_EDGE = "#ffd6de"
S8_TEXT = OFF_WHITE
ACCENT = "#f8b1b0"
OTHER = (1, 1, 1, 0.42)
GREY_DOT = (1, 1, 1, 0.28)

SLIDE_SIZE = (16, 9)
SLIDE_DPI = 220

MERATESE = {"Airuno", "Osnago", "Cernusco-Merate", "Olgiate-Calco-Brivio"}


def data_path(*parts: str) -> Path:
    return ROOT.joinpath(*parts)


def load_font(filename: str) -> FontProperties:
    path = FONT_DIR / filename
    fm.fontManager.addfont(str(path))
    return FontProperties(fname=str(path))


TITLE_FONT = load_font("BricolageGrotesque.ttf")
TEXT_FONT = load_font("OpenSans-Regular.ttf")
BOLD_FONT = load_font("OpenSans-Bold.ttf")


def next_path(stem: str, suffix: str = ".png") -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for idx in range(1, 100):
        candidate = OUT_DIR / f"{stem}_v{idx:02d}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Troppi output presenti per {stem}.")


def preview_path_for(transparent_path: Path) -> Path:
    name = transparent_path.name.replace("_trasparente_", "_preview_verde_")
    return transparent_path.with_name(name)


def save_slide(fig: plt.Figure, stem: str) -> tuple[Path, Path]:
    transparent = next_path(f"{stem}_trasparente")
    preview = preview_path_for(transparent)
    fig.savefig(transparent, dpi=SLIDE_DPI, transparent=True)
    plt.close(fig)

    image = Image.open(transparent).convert("RGBA")
    bg = Image.new("RGBA", image.size, GREEN)
    bg.alpha_composite(image)
    bg.convert("RGB").save(preview, quality=95)
    return transparent, preview


def setup() -> tuple[plt.Figure, plt.Axes]:
    bbcstyle.use()
    plt.rcParams.update(
        {
            "figure.facecolor": "none",
            "axes.facecolor": "none",
            "savefig.facecolor": "none",
            "axes.grid": False,
            "axes.unicode_minus": False,
        }
    )
    fig, ax = plt.subplots(figsize=SLIDE_SIZE, constrained_layout=False)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    return fig, ax


def wrap_title(text: str, width: int = 42) -> str:
    return "\n".join(
        textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)
    )


def add_title(
    fig: plt.Figure,
    title: str,
    subtitle: str,
    *,
    title_size: int = 45,
    title_y: float = 0.935,
    subtitle_y: float = 0.805,
    center: bool = True,
) -> None:
    x = 0.5 if center else 0.055
    ha = "center" if center else "left"
    fig.text(
        x,
        title_y,
        wrap_title(title),
        ha=ha,
        va="top",
        fontsize=title_size,
        fontproperties=TITLE_FONT,
        fontweight="bold",
        color=OFF_WHITE,
        linespacing=0.86,
        path_effects=[pe.withStroke(linewidth=2.5, foreground=GREEN_DARK, alpha=0.28)],
    )
    fig.text(
        x,
        subtitle_y,
        subtitle,
        ha=ha,
        va="top",
        fontsize=13.3,
        fontproperties=TEXT_FONT,
        color=SOFT_WHITE,
    )


def add_source(fig: plt.Figure, text: str) -> None:
    fig.text(
        0.055,
        0.055,
        text,
        ha="left",
        va="bottom",
        fontsize=8.3,
        fontproperties=TEXT_FONT,
        color=MUTED_WHITE,
    )


def clean_ax(ax: plt.Axes) -> None:
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)


def style_x_axis(ax: plt.Axes, label: str | None = None) -> None:
    ax.xaxis.grid(True, color=GRID, linewidth=1.0)
    ax.yaxis.grid(False)
    ax.tick_params(axis="x", labelsize=10.6, colors=MUTED_WHITE)
    for tick in ax.get_xticklabels():
        tick.set_fontproperties(TEXT_FONT)
    if label:
        ax.set_xlabel(
            label,
            fontsize=11.0,
            fontproperties=TEXT_FONT,
            color=SOFT_WHITE,
            labelpad=8,
        )


def fmt_int_it(value: float) -> str:
    return f"{int(round(value)):,.0f}".replace(",", ".")


def fmt_pct(value: float, decimals: int = 0) -> str:
    return f"{value:.{decimals}f}%".replace(".", ",")


def shorten(text: str, max_chars: int = 42) -> str:
    text = (
        str(text)
        .replace("–", "-")
        .replace(" / ", "/")
        .replace("Fiumicino Aeroporto", "Fiumicino")
        .replace("Milano Passante", "Milano Pass.")
        .replace("Milano Porta Garibaldi", "Milano P. Garibaldi")
        .replace("Civita Castellana", "Civita Cast.")
        .replace("San Cristoforo", "S. Cristoforo")
    )
    if len(text) <= max_chars:
        return text
    words = text.split()
    out: list[str] = []
    for word in words:
        proposal = " ".join(out + [word])
        if len(proposal) > max_chars - 1:
            break
        out.append(word)
    return " ".join(out).rstrip(" -/") + "..."


def barh_labels(
    ax: plt.Axes,
    labels: list[str],
    *,
    x: float,
    highlight: set[str] | None = None,
    keys: list[str] | None = None,
    size: float = 10.2,
) -> None:
    highlight = highlight or set()
    keys = keys or labels
    for idx, (label, key) in enumerate(zip(labels, keys)):
        is_hi = key in highlight
        ax.text(
            x,
            idx,
            label,
            va="center",
            ha="right",
            fontsize=size,
            fontproperties=BOLD_FONT if is_hi else TEXT_FONT,
            color=OFF_WHITE if is_hi else SOFT_WHITE,
        )


def chart_top20() -> tuple[Path, Path]:
    path = data_path(
        "linee",
        "top 20 italia",
        "base_dati_top20_linee_ferroviarie_nonAV_italia_colori_finali_tilo_blu_ticino.xlsx",
    )
    df = pd.read_excel(path, sheet_name="Top20").sort_values("rank", ascending=False)
    df["value"] = pd.to_numeric(df["central_mln"], errors="coerce")

    def label(row: pd.Series) -> str:
        name = str(row["line_name"]).replace("–", "-")
        code = str(row["line_code"])
        if name.startswith(code):
            name = name[len(code) :].strip()
        return f"{int(row['rank'])}. {code} · {shorten(name)}"

    df["label"] = df.apply(label, axis=1)
    fig, ax = setup()
    add_title(
        fig,
        "Le 20 linee locali più usate in Italia",
        "La S8 Lecco-Milano è al 4° posto: 14,8 milioni di passeggeri annui.",
        title_size=43,
        subtitle_y=0.815,
    )

    colors = [S8_FILL if code == "S8" else BAR for code in df["line_code"]]
    edgecolors = [S8_EDGE if code == "S8" else (1, 1, 1, 0) for code in df["line_code"]]
    linewidths = [1.8 if code == "S8" else 0 for code in df["line_code"]]
    bars = ax.barh(
        range(len(df)),
        df["value"],
        color=colors,
        edgecolor=edgecolors,
        linewidth=linewidths,
        height=0.58,
    )
    ax.set_yticks([])
    ax.set_ylim(-0.8, len(df) - 0.2)
    barh_labels(
        ax,
        df["label"].tolist(),
        x=-0.45,
        highlight={"S8"},
        keys=df["line_code"].tolist(),
        size=9.6,
    )

    for idx, row in df.iterrows():
        ax.add_patch(
            Rectangle(
                (-0.25, idx - 0.18),
                0.055,
                0.36,
                transform=ax.transData,
                clip_on=False,
                color=str(row["color_hex"]),
                linewidth=0,
            )
        )

    for bar, value, code in zip(bars, df["value"], df["line_code"]):
        is_s8 = code == "S8"
        ax.text(
            value + 0.13,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}",
            va="center",
            ha="left",
            fontsize=12.4 if is_s8 else 10.8,
            fontproperties=BOLD_FONT if is_s8 else TEXT_FONT,
            color=OFF_WHITE if is_s8 else SOFT_WHITE,
        )

    s8_y = int(np.where(df["line_code"].to_numpy() == "S8")[0][0])
    s8_value = float(df.loc[df["line_code"] == "S8", "value"].iloc[0])
    ax.plot([s8_value + 1.05, s8_value + 1.62], [s8_y, s8_y], color=S8_EDGE, linewidth=1.2)
    ax.text(
        s8_value + 1.80,
        s8_y,
        "4° posto in Italia",
        va="center",
        ha="left",
        fontsize=11.8,
        fontproperties=BOLD_FONT,
        color=OFF_WHITE,
    )
    ax.set_xlim(0, 23.2)
    ax.set_xticks([0, 5, 10, 15, 20])
    style_x_axis(ax, "Milioni di passeggeri annui")
    clean_ax(ax)
    add_source(fig, "Fonte: elaborazione su dati Trenord, Cotral, Trenitalia e Regioni. Lombardia: campagne 2025.")
    fig.subplots_adjust(left=0.30, right=0.94, top=0.73, bottom=0.15)
    return save_slide(fig, "01_top20_linee_italia_s8")


def chart_delta_linee() -> tuple[Path, Path]:
    df = pd.read_csv(data_path("linee", "2024 2025", "plotly_linee_suburbane_S1S12_summary.csv"))
    df = df.sort_values("Delta").reset_index(drop=True)
    fig, ax = setup()
    add_title(
        fig,
        "La S8 cresce più di tutte le linee S",
        "+22.800 passeggeri medi al giorno tra 2024 e 2025: il salto più forte nel sistema suburbano.",
        title_size=42,
        subtitle_y=0.815,
    )
    colors = [S8_FILL if line == "S8" else (S8_EDGE if v > 0 else BAR_WEAK) for line, v in zip(df["N. linea"], df["Delta"])]
    edges = [S8_EDGE if line == "S8" else (1, 1, 1, 0) for line in df["N. linea"]]
    ax.barh(range(len(df)), df["Delta"] / 1000, color=colors, edgecolor=edges, linewidth=[1.8 if x == "S8" else 0 for x in df["N. linea"]], height=0.62)
    ax.axvline(0, color=SOFT_WHITE, linewidth=1.1, alpha=0.8)
    ax.set_yticks([])
    ax.set_ylim(-0.7, len(df) - 0.3)
    for i, row in df.iterrows():
        is_s8 = row["N. linea"] == "S8"
        ax.text(
            -8.0,
            i,
            row["N. linea"],
            ha="right",
            va="center",
            fontsize=13,
            fontproperties=BOLD_FONT if is_s8 else TEXT_FONT,
            color=OFF_WHITE if is_s8 else SOFT_WHITE,
        )
        v = row["Delta"] / 1000
        ax.text(
            v + (0.45 if v >= 0 else -0.45),
            i,
            f"{v:+.1f}k".replace(".", ","),
            ha="left" if v >= 0 else "right",
            va="center",
            fontsize=11.4,
            fontproperties=BOLD_FONT if is_s8 else TEXT_FONT,
            color=OFF_WHITE if is_s8 else SOFT_WHITE,
        )
    ax.set_xlim(-8.5, 25.5)
    ax.set_xticks([-5, 0, 5, 10, 15, 20, 25])
    style_x_axis(ax, "Variazione 2025 vs 2024, migliaia di passeggeri medi/giorno")
    clean_ax(ax)
    add_source(fig, "Fonte: elaborazione su dati di frequentazione linee ferroviarie regionali Lombardia, 2024-2025.")
    fig.subplots_adjust(left=0.22, right=0.91, top=0.72, bottom=0.17)
    return save_slide(fig, "02_crescita_linee_s_2024_2025")


def chart_stazioni_2025_index() -> tuple[Path, Path]:
    df = pd.read_csv(
        data_path(
            "ANALISI INIZIALE",
            "stazioni",
            "update",
            "S8_stazioni_Saliti24H_Novembre_2015_2025_no_Maggianico_indice2019_100.csv",
        )
    )
    last = df[df["Anno"].eq(2025)].sort_values("Indice_2019_100").reset_index(drop=True)
    fig, ax = setup()
    add_title(
        fig,
        "Nel Meratese la domanda supera il 2019",
        "Indice 2019=100: Airuno 258, Osnago 216, Cernusco-Merate 174, Olgiate-Calco-Brivio 169.",
        title_size=42,
        subtitle_y=0.815,
    )
    keys = last["Stazione"].tolist()
    colors = [S8_FILL if s in MERATESE else BAR for s in keys]
    ax.barh(range(len(last)), last["Indice_2019_100"], color=colors, height=0.62)
    ax.axvline(100, color=S8_EDGE, linewidth=1.2, alpha=0.95)
    ax.text(100, len(last) - 0.1, "2019", ha="center", va="bottom", color=S8_EDGE, fontsize=10.5, fontproperties=BOLD_FONT)
    ax.set_yticks([])
    ax.set_ylim(-0.7, len(last) - 0.2)
    barh_labels(ax, keys, x=-6, highlight=MERATESE, keys=keys, size=10.4)
    for i, row in last.iterrows():
        is_hi = row["Stazione"] in MERATESE
        ax.text(
            row["Indice_2019_100"] + 4,
            i,
            f"{row['Indice_2019_100']:.0f}",
            ha="left",
            va="center",
            fontsize=11.4,
            fontproperties=BOLD_FONT if is_hi else TEXT_FONT,
            color=OFF_WHITE if is_hi else SOFT_WHITE,
        )
    ax.set_xlim(0, 280)
    ax.set_xticks([0, 50, 100, 150, 200, 250])
    style_x_axis(ax, "Saliti giornalieri, indice 2019=100")
    clean_ax(ax)
    add_source(fig, "Fonte: elaborazione su Flussi Stazioni Ferroviarie e campagne Lombardia 2025.")
    fig.subplots_adjust(left=0.26, right=0.91, top=0.72, bottom=0.17)
    return save_slide(fig, "03_stazioni_s8_indice_2025")


def chart_fuori_punta() -> tuple[Path, Path]:
    df = pd.read_csv(
        data_path(
            "stazioni",
            "altro",
            "Pacchetto_analisi_Meratese_S8_v3_fino2025",
            "S8_crescita_totale_punta_offerta_2015_2025.csv",
        )
    )
    df = df.sort_values("Differenziale_crescita_24H_meno_7_9_pp").reset_index(drop=True)
    fig, ax = setup()
    add_title(
        fig,
        "La crescita si sposta fuori dall'ora di punta",
        "Il totale giornaliero cresce molto più della fascia 7-9, soprattutto nel Meratese.",
        title_size=42,
        subtitle_y=0.815,
    )
    colors = [S8_FILL if g == "Meratese" else BAR for g in df["Gruppo"]]
    ax.barh(range(len(df)), df["Differenziale_crescita_24H_meno_7_9_pp"], color=colors, height=0.60)
    ax.axvline(0, color=SOFT_WHITE, linewidth=1.0, alpha=0.8)
    ax.set_yticks([])
    ax.set_ylim(-0.7, len(df) - 0.3)
    labels = [shorten(s, 35) for s in df["Stazione"]]
    barh_labels(ax, labels, x=-23, highlight=MERATESE, keys=df["Stazione"].tolist(), size=9.9)
    for i, row in df.iterrows():
        v = row["Differenziale_crescita_24H_meno_7_9_pp"]
        is_hi = row["Gruppo"] == "Meratese"
        ax.text(
            v + (2.5 if v >= 0 else -2.5),
            i,
            f"{v:+.0f} pp",
            ha="left" if v >= 0 else "right",
            va="center",
            fontsize=10.8,
            fontproperties=BOLD_FONT if is_hi else TEXT_FONT,
            color=OFF_WHITE if is_hi else SOFT_WHITE,
        )
    ax.set_xlim(-28, 145)
    ax.set_xticks([-20, 0, 40, 80, 120])
    style_x_axis(ax, "Crescita 24H meno crescita 7-9, punti percentuali")
    clean_ax(ax)
    add_source(fig, "Fonte: elaborazione S8 2015-2025 su saliti 24H e fascia 7-9.")
    fig.subplots_adjust(left=0.29, right=0.91, top=0.72, bottom=0.17)
    return save_slide(fig, "04_crescita_fuori_punta")


def chart_gruppi() -> tuple[Path, Path]:
    df = pd.read_csv(
        data_path(
            "stazioni",
            "altro",
            "Pacchetto_analisi_Meratese_S8_v3_fino2025",
            "S8_confronto_gruppi_2015_2025.csv",
        )
    )
    order = ["Nodi S8", "Intermedie S8", "Meratese"]
    df["order"] = df["Gruppo"].map({k: i for i, k in enumerate(order)})
    df = df.sort_values("order").reset_index(drop=True)
    fig, ax = setup()
    add_title(
        fig,
        "Nel Meratese i saliti quasi raddoppiano",
        "+97% dal 2015 al 2025: molto più delle intermedie e dei grandi nodi.",
        title_size=43,
        subtitle_y=0.815,
    )
    colors = [S8_FILL if g == "Meratese" else BAR for g in df["Gruppo"]]
    ax.barh(range(len(df)), df["Crescita_Saliti24H_pct"], color=colors, height=0.54)
    ax.set_yticks([])
    ax.set_ylim(-0.55, len(df) - 0.45)
    barh_labels(ax, df["Gruppo"].tolist(), x=-5, highlight={"Meratese"}, keys=df["Gruppo"].tolist(), size=14)
    for i, row in df.iterrows():
        is_hi = row["Gruppo"] == "Meratese"
        ax.text(
            row["Crescita_Saliti24H_pct"] + 2,
            i,
            fmt_pct(row["Crescita_Saliti24H_pct"]),
            ha="left",
            va="center",
            fontsize=15 if is_hi else 13,
            fontproperties=BOLD_FONT if is_hi else TEXT_FONT,
            color=OFF_WHITE if is_hi else SOFT_WHITE,
        )
    ax.set_xlim(0, 110)
    ax.set_xticks([0, 25, 50, 75, 100])
    style_x_axis(ax, "Crescita saliti giornalieri 2015-2025")
    clean_ax(ax)
    add_source(fig, "Fonte: elaborazione su stazioni S8, saliti giornalieri 2015-2025.")
    fig.subplots_adjust(left=0.25, right=0.86, top=0.70, bottom=0.20)
    return save_slide(fig, "05_gruppi_crescita_meratese")


def chart_scatter_lombardia() -> tuple[Path, Path]:
    df = pd.read_csv(
        data_path(
            "stazioni",
            "altro",
            "S8_SalitiS_e_scatter_Lombardia",
            "Scatter_Lombardia_base2019_vs_crescita2019_2025_dataset.csv",
        )
    )
    df = df[(df["Saliti24H_2019"] > 0) & df["Growth_pct_24H"].notna()].copy()
    fig, ax = setup()
    add_title(
        fig,
        "Il Meratese cresce più di quasi tutte le stazioni lombarde",
        "Confronto 2019-2025: le quattro stazioni meratesi stanno nella parte alta della distribuzione.",
        title_size=39,
        subtitle_y=0.815,
    )
    other = df[df["Gruppo"].ne("Meratese")]
    mer = df[df["Gruppo"].eq("Meratese")]
    ax.scatter(other["Saliti24H_2019"], other["Growth_pct_24H"], s=20, color=GREY_DOT, linewidth=0)
    ax.scatter(mer["Saliti24H_2019"], mer["Growth_pct_24H"], s=85, color=S8_FILL, edgecolor=S8_EDGE, linewidth=1.2)
    ax.axhline(0, color=SOFT_WHITE, linewidth=1.0, alpha=0.65)
    ax.set_xscale("log")
    label_offsets = {
        "AIRUNO": (1.07, 3.5),
        "OSNAGO": (1.08, 4.0),
        "CERNUSCO-MERATE": (1.08, 5.5),
        "OLGIATE-CALCO-BRIVIO": (1.08, -8.0),
    }
    for _, row in mer.iterrows():
        mult, dy = label_offsets.get(str(row["StationKey"]), (1.08, 2.5))
        ax.text(
            row["Saliti24H_2019"] * mult,
            row["Growth_pct_24H"] + dy,
            str(row["Stazione"]).title().replace("Cernusco-Merate", "Cernusco-Merate"),
            fontsize=8.7,
            fontproperties=BOLD_FONT,
            color=OFF_WHITE,
        )
    ax.set_xlim(80, max(df["Saliti24H_2019"]) * 1.3)
    ax.set_ylim(-70, 190)
    ax.set_xticks([100, 300, 1000, 3000, 10000, 30000])
    ax.set_xticklabels(["100", "300", "1.000", "3.000", "10.000", "30.000"])
    ax.set_yticks([-50, 0, 50, 100, 150])
    ax.tick_params(axis="both", labelsize=10.3, colors=MUTED_WHITE)
    for tick in ax.get_xticklabels() + ax.get_yticklabels():
        tick.set_fontproperties(TEXT_FONT)
    ax.grid(True, color=GRID, linewidth=1.0)
    ax.set_xlabel("Saliti giornalieri 2019, scala logaritmica", fontsize=10.8, fontproperties=TEXT_FONT, color=SOFT_WHITE, labelpad=8)
    ax.set_ylabel("Crescita 2019-2025", fontsize=10.8, fontproperties=TEXT_FONT, color=SOFT_WHITE, labelpad=8)
    clean_ax(ax)
    add_source(fig, "Fonte: dataset stazioni lombarde 2019-2025; evidenza sulle stazioni del Meratese.")
    fig.subplots_adjust(left=0.12, right=0.91, top=0.72, bottom=0.18)
    return save_slide(fig, "06_scatter_lombardia_meratese")


def chart_peso_punta() -> tuple[Path, Path]:
    df = pd.read_csv(
        data_path(
            "stazioni",
            "cambio rapporto",
            "orari",
            "Meratese_series_Saliti7-9_Saliti24H_2015_2025.csv",
        )
    )
    agg = df.groupby("Anno", as_index=False)[["Saliti7-9", "Saliti24H"]].sum()
    agg["Quota"] = agg["Saliti7-9"] / agg["Saliti24H"] * 100
    fig, ax = setup()
    add_title(
        fig,
        "La S8 non è più solo ora di punta",
        "Nel Meratese la quota dei saliti 7-9 scende dal 53% al 28%.",
        title_size=42,
        subtitle_y=0.815,
    )
    ax.plot(agg["Anno"], agg["Quota"], color=S8_FILL, linewidth=3.2, marker="o", markersize=7, markeredgecolor=S8_EDGE)
    ax.fill_between(agg["Anno"], agg["Quota"], 0, color=S8_FILL, alpha=0.10)
    first = agg.iloc[0]
    last = agg.iloc[-1]
    for row, label in [(first, "2015"), (last, "2025")]:
        ax.text(
            row["Anno"],
            row["Quota"] + 3.2,
            f"{label}\n{row['Quota']:.0f}%",
            ha="center",
            va="bottom",
            fontsize=12,
            fontproperties=BOLD_FONT,
            color=OFF_WHITE,
        )
    ax.set_xlim(2014.5, 2025.5)
    ax.set_ylim(0, 62)
    ax.set_xticks([2015, 2017, 2019, 2021, 2023, 2025])
    ax.set_yticks([0, 15, 30, 45, 60])
    ax.tick_params(axis="both", labelsize=10.5, colors=MUTED_WHITE)
    for tick in ax.get_xticklabels() + ax.get_yticklabels():
        tick.set_fontproperties(TEXT_FONT)
    ax.grid(True, color=GRID, linewidth=1.0)
    ax.set_ylabel("Quota saliti 7-9 sul totale giornaliero", fontsize=10.8, fontproperties=TEXT_FONT, color=SOFT_WHITE, labelpad=8)
    clean_ax(ax)
    add_source(fig, "Fonte: elaborazione Meratese, saliti 7-9 e saliti 24H 2015-2025.")
    fig.subplots_adjust(left=0.12, right=0.91, top=0.72, bottom=0.17)
    return save_slide(fig, "07_peso_punta_meratese")


def chart_weekend() -> tuple[Path, Path]:
    df = pd.read_csv(
        data_path(
            "stazioni",
            "cambio rapporto",
            "weekend vs feriale",
            "Meratese___weekend_vs_feriale_2015-2025.csv",
        )
    )
    recent = df[df["Anno"].isin([2024, 2025])].copy()
    metrics = ["Sabato/Feriale_%", "Festivo/Feriale_%", "Weekend_totale/Feriale_%"]
    labels = ["Sabato", "Festivo", "Weekend totale"]
    fig, ax = setup()
    add_title(
        fig,
        "Nel weekend la domanda resta molto alta",
        "Nel 2025 sabato e festivo insieme valgono il 106% di un feriale nel Meratese.",
        title_size=41,
        subtitle_y=0.815,
    )
    y = np.arange(len(labels))
    h = 0.28
    vals_2024 = recent[recent["Anno"].eq(2024)][metrics].iloc[0].to_numpy(dtype=float)
    vals_2025 = recent[recent["Anno"].eq(2025)][metrics].iloc[0].to_numpy(dtype=float)
    ax.barh(y - h / 1.8, vals_2024, height=h, color=BAR_WEAK, label="2024")
    ax.barh(y + h / 1.8, vals_2025, height=h, color=[BAR, BAR, S8_FILL], label="2025")
    ax.set_yticks([])
    for i, lab in enumerate(labels):
        ax.text(-4, i, lab, ha="right", va="center", fontsize=13, fontproperties=BOLD_FONT if lab == "Weekend totale" else TEXT_FONT, color=OFF_WHITE if lab == "Weekend totale" else SOFT_WHITE)
        ax.text(vals_2025[i] + 2, i + h / 1.8, fmt_pct(vals_2025[i], 1), ha="left", va="center", fontsize=11.5, fontproperties=BOLD_FONT if lab == "Weekend totale" else TEXT_FONT, color=OFF_WHITE if lab == "Weekend totale" else SOFT_WHITE)
    ax.axvline(100, color=S8_EDGE, linewidth=1.2, alpha=0.85)
    ax.text(100, len(labels) - 0.35, "un feriale", ha="center", va="bottom", fontsize=10.5, fontproperties=BOLD_FONT, color=S8_EDGE)
    ax.set_xlim(0, 115)
    ax.set_ylim(-0.6, len(labels) - 0.35)
    ax.set_xticks([0, 25, 50, 75, 100])
    style_x_axis(ax, "Rapporto rispetto a un giorno feriale")
    ax.text(64, -0.55, "2024", color=MUTED_WHITE, fontsize=9.5, fontproperties=TEXT_FONT, ha="center")
    ax.text(75, -0.55, "2025", color=OFF_WHITE, fontsize=9.5, fontproperties=BOLD_FONT, ha="center")
    clean_ax(ax)
    add_source(fig, "Fonte: elaborazione Meratese, confronto weekend/feriale 2024-2025.")
    fig.subplots_adjust(left=0.23, right=0.88, top=0.70, bottom=0.22)
    return save_slide(fig, "08_weekend_feriale_meratese")


def generate_all() -> list[dict[str, str]]:
    charts = [
        ("01 Top20 nazionale", chart_top20),
        ("02 Linee S 2024-2025", chart_delta_linee),
        ("03 Stazioni indice 2025", chart_stazioni_2025_index),
        ("04 Crescita fuori punta", chart_fuori_punta),
        ("05 Gruppi Meratese", chart_gruppi),
        ("06 Scatter Lombardia", chart_scatter_lombardia),
        ("07 Peso punta", chart_peso_punta),
        ("08 Weekend/Feriale", chart_weekend),
    ]
    manifest: list[dict[str, str]] = []
    for label, fn in charts:
        transparent, preview = fn()
        manifest.append(
            {
                "grafico": label,
                "trasparente": str(transparent),
                "preview_verde": str(preview),
            }
        )
        print(label)
        print(transparent)
        print(preview)
    manifest_path = next_path("manifest_grafici_canva_verde", ".json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(manifest_path)
    return manifest


if __name__ == "__main__":
    generate_all()

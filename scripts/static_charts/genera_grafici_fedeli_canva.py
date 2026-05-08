from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Patch, Rectangle
from PIL import Image, ImageDraw

try:
    import bbcstyle
except ModuleNotFoundError:
    bbcstyle = None


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent / "output"
READY_ROOT = Path(__file__).resolve().parent
FONT_DIR = ROOT / "grafici_rifatti_v01" / "github_bbcstyle_top20" / "assets" / "fonts"

GREEN = "#1f642c"
GREEN_DARK = "#174f24"
OFF_WHITE = "#f7fbf4"
SOFT_WHITE = "#dfeee0"
MUTED_WHITE = "#bdd8bf"
NOTE_FACE = "#fff7f8"
NOTE_TEXT = "#243524"
GREY_FACE = "#eef1ee"
GREY_TEXT = "#4e5851"
GRID = (1, 1, 1, 0.20)
BAR_MUTED = (1, 1, 1, 0.27)
LINE_MUTED = (1, 1, 1, 0.34)
S8 = "#f2b8c1"
S8_EDGE = "#ffd6de"
PUNTA = "#8e3d7a"
MORBIDA = "#f2b8c1"

STATION_COLORS = {
    "Airuno": "#ffd1d1",
    "Osnago": "#ff7faa",
    "Cernusco-Merate": "#c4447a",
    "Olgiate-Calco-Brivio": "#f0a4d8",
}
MERATESE = set(STATION_COLORS)

LINE_COLORS = {
    "S8": S8,
    "S1/S12": "#e84b5f",
    "S5": "#ff9a3d",
    "S6": "#ffd83d",
    "Totale Trenord": SOFT_WHITE,
}

SLIDE_SIZE = (16, 9)
SLIDE_DPI = 220
SIGNATURE = "Analisi di Simone Ghezzi Colombo"


def load_font(filename: str) -> FontProperties:
    path = FONT_DIR / filename
    fm.fontManager.addfont(str(path))
    return FontProperties(fname=str(path))


TITLE_FONT = load_font("BricolageGrotesque.ttf")
TEXT_FONT = load_font("OpenSans-Regular.ttf")
BOLD_FONT = load_font("OpenSans-Bold.ttf")


def p(*parts: str) -> Path:
    return ROOT.joinpath(*parts)


def next_path(stem: str, suffix: str = ".png") -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for idx in range(1, 100):
        candidate = OUT_DIR / f"{stem}_v{idx:02d}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Troppi output per {stem}.")


def setup() -> tuple[plt.Figure, plt.Axes]:
    if bbcstyle is not None:
        bbcstyle.use()
    else:
        plt.style.use("default")
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


def wrap(text: str, width: int = 44) -> str:
    return "\n".join(
        textwrap.wrap(str(text), width=width, break_long_words=False, break_on_hyphens=False)
    )


def add_header(
    fig: plt.Figure,
    title: str,
    subtitle: str,
    *,
    title_size: int = 32,
    title_y: float = 0.950,
    subtitle_y: float = 0.885,
) -> None:
    fig.text(
        0.5,
        title_y,
        title,
        ha="center",
        va="top",
        fontsize=title_size,
        fontproperties=TITLE_FONT,
        color=OFF_WHITE,
        linespacing=0.92,
        path_effects=[pe.withStroke(linewidth=2.0, foreground=GREEN_DARK, alpha=0.30)],
    )
    if subtitle:
        fig.text(
            0.5,
            subtitle_y,
            subtitle,
            ha="center",
            va="top",
            fontsize=13.2,
            fontproperties=TEXT_FONT,
            color=SOFT_WHITE,
        )


def add_source(fig: plt.Figure, source: str) -> None:
    source = "\n".join(textwrap.wrap(source, width=132, break_long_words=False, break_on_hyphens=False))
    fig.text(
        0.045,
        0.045,
        source,
        ha="left",
        va="bottom",
        fontsize=8.6,
        fontproperties=TEXT_FONT,
        color=MUTED_WHITE,
    )
    fig.text(
        0.955,
        0.045,
        SIGNATURE,
        ha="right",
        va="bottom",
        fontsize=8.6,
        fontproperties=TEXT_FONT,
        color=MUTED_WHITE,
    )


def clean(ax: plt.Axes) -> None:
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)


def axis_style(ax: plt.Axes, xlabel: str | None = None, ylabel: str | None = None) -> None:
    ax.grid(True, color=GRID, linewidth=1.15)
    ax.tick_params(axis="both", colors=MUTED_WHITE, labelsize=12.2)
    for tick in ax.get_xticklabels() + ax.get_yticklabels():
        tick.set_fontproperties(TEXT_FONT)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12.4, fontproperties=TEXT_FONT, color=SOFT_WHITE, labelpad=9)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12.4, fontproperties=TEXT_FONT, color=SOFT_WHITE, labelpad=9)


def save(fig: plt.Figure, stem: str) -> tuple[Path, Path]:
    transparent = next_path(f"{stem}_trasparente")
    fig.savefig(transparent, dpi=SLIDE_DPI, transparent=True)
    plt.close(fig)
    preview = transparent.with_name(transparent.name.replace("_trasparente_", "_preview_verde_"))
    image = Image.open(transparent).convert("RGBA")
    bg = Image.new("RGBA", image.size, GREEN)
    bg.alpha_composite(image)
    bg.convert("RGB").save(preview, quality=95)
    return transparent, preview


def fmt_int(value: float) -> str:
    return f"{int(round(value)):,.0f}".replace(",", ".")


def fmt_plus(value: float) -> str:
    return ("+" if value >= 0 else "") + fmt_int(value)


def shorten(text: str, max_chars: int = 42) -> str:
    replacements = {
        "Fiumicino Aeroporto": "Fiumicino",
        "Milano Passante": "Milano Pass.",
        "Milano Porta Garibaldi": "Milano P. Garibaldi",
        "Civita Castellana": "Civita Cast.",
        "San Cristoforo": "S. Cristoforo",
    }
    out = str(text).replace("–", "-").replace(" / ", "/")
    for k, v in replacements.items():
        out = out.replace(k, v)
    if len(out) <= max_chars:
        return out
    words: list[str] = []
    for word in out.split():
        candidate = " ".join(words + [word])
        if len(candidate) > max_chars - 1:
            break
        words.append(word)
    return " ".join(words).rstrip(" -/") + "..."


def label_right(ax: plt.Axes, x: float, y: float, text: str, color: str | tuple, bold: bool = False, size: float = 10.8) -> None:
    ax.text(
        x,
        y,
        text,
        ha="left",
        va="center",
        fontsize=size,
        fontproperties=BOLD_FONT if bold else TEXT_FONT,
        color=color,
        path_effects=[pe.withStroke(linewidth=2.0, foreground=GREEN_DARK, alpha=0.55)],
    )


def label_box(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    color: str,
    *,
    ha: str = "left",
    size: float = 8.5,
    facecolor: str = NOTE_FACE,
    text_color: str = NOTE_TEXT,
) -> None:
    ax.text(
        x,
        y,
        text,
        ha=ha,
        va="center",
        fontsize=size,
        fontproperties=BOLD_FONT,
        color=text_color,
        bbox={
            "boxstyle": "round,pad=0.20",
            "facecolor": facecolor,
            "edgecolor": color,
            "linewidth": 1.15,
            "alpha": 0.97,
        },
    )


def chart_linee_s_indice() -> tuple[Path, Path]:
    df = pd.read_csv(p("ANALISI INIZIALE", "s8", "Linee_S1S12_S5_S6_S8_2019-2025_dataset.csv"))
    fig, ax = setup()
    add_header(
        fig,
        "Linee suburbane Trenord: indice 2019=100",
        "La S8 è l'unica tra le linee considerate nettamente sopra il livello 2019.",
        title_size=31,
    )
    order = ["S1/S12", "S5", "S6", "S8", "Totale Trenord"]
    for serie in order:
        sub = df[df["Serie"].eq(serie)].sort_values("Anno")
        is_s8 = serie == "S8"
        is_total = serie == "Totale Trenord"
        ax.plot(
            sub["Anno"],
            sub["Indice_2019_100"],
            color=LINE_COLORS[serie],
            linewidth=4.4 if is_s8 else (3.0 if not is_total else 2.3),
            linestyle="--" if is_total else "-",
            marker="o",
            markersize=6.4 if is_s8 else 4.7,
            alpha=1 if is_s8 else 0.88,
        )
        last = sub.iloc[-1]
        label_right(ax, last["Anno"] + 0.12, last["Indice_2019_100"], serie, LINE_COLORS[serie], is_s8, 12.4 if is_s8 else 10.8)
    ax.axhline(100, color=MUTED_WHITE, linewidth=1.0, linestyle=":", alpha=0.65)
    ax.set_xlim(2018.7, 2025.9)
    ax.set_ylim(0, 170)
    ax.set_xticks([2019, 2020, 2021, 2022, 2023, 2024, 2025])
    ax.set_yticks([0, 40, 80, 120, 160])
    axis_style(ax, "Anno", "Indice (2019=100)")
    clean(ax)
    add_source(fig, "Fonti: Regione Lombardia, Trenord, relazioni e comunicati 2019-2025. Elaborazione su indice 2019=100.")
    fig.subplots_adjust(left=0.085, right=0.90, top=0.845, bottom=0.135)
    return save(fig, "01_linee_suburbane_trenord_indice_2019_100")


def chart_delta_linee() -> tuple[Path, Path]:
    df = pd.read_csv(p("linee", "2024 2025", "plotly_linee_suburbane_S1S12_summary_CORRETTO.csv"))
    df = df.sort_values("Delta").reset_index(drop=True)
    fig, ax = setup()
    add_header(
        fig,
        "Variazione assoluta passeggeri",
        "Linee suburbane Trenord: 2025 vs 2024, passeggeri/giorno feriale.",
        title_size=32,
    )
    extra_colors = {
        "S1/S12": "#e84b5f",
        "S5": "#ff9a3d",
        "S6": "#ffd83d",
    }
    colors = [S8 if x == "S8" else extra_colors.get(x, BAR_MUTED) for x in df["N. linea"]]
    alphas = [1.0 if x == "S8" else (0.78 if x in extra_colors else 0.55) for x in df["N. linea"]]
    edges = [S8_EDGE if x == "S8" else (1, 1, 1, 0.0) for x in df["N. linea"]]
    bars = ax.barh(range(len(df)), df["Delta"], color=colors, edgecolor=edges, linewidth=[2.2 if x == "S8" else 0 for x in df["N. linea"]], height=0.62)
    for bar, alpha in zip(bars, alphas):
        bar.set_alpha(alpha)
    ax.axvline(0, color=SOFT_WHITE, linewidth=1.0, alpha=0.85)
    ax.set_yticks([])
    ax.set_ylim(-0.85, len(df) - 0.15)
    for i, row in df.iterrows():
        is_s8 = row["N. linea"] == "S8"
        is_colored = row["N. linea"] in extra_colors
        ax.text(-8600, i, row["N. linea"], ha="right", va="center", fontsize=13.4, fontproperties=BOLD_FONT if is_s8 else TEXT_FONT, color=OFF_WHITE if (is_s8 or is_colored) else SOFT_WHITE)
        val = row["Delta"]
        ax.text(val + (620 if val >= 0 else -620), i, fmt_plus(val), ha="left" if val >= 0 else "right", va="center", fontsize=11.4, fontproperties=BOLD_FONT if is_s8 else TEXT_FONT, color=OFF_WHITE if (is_s8 or is_colored) else SOFT_WHITE)
    s112_y = int(df.index[df["N. linea"].eq("S1/S12")][0])
    ax.text(
        14600,
        s112_y + 0.46,
        "da 70 a 130 corse/giorno grazie a S12",
        ha="center",
        va="center",
        fontsize=10.8,
        fontproperties=BOLD_FONT,
        color=NOTE_TEXT,
        bbox={
            "boxstyle": "round,pad=0.22",
            "facecolor": NOTE_FACE,
            "edgecolor": S8_EDGE,
            "linewidth": 1.0,
            "alpha": 0.98,
        },
    )
    ax.set_xlim(-9300, 25000)
    ax.set_xticks([-5000, 0, 5000, 10000, 15000, 20000])
    ax.set_xticklabels(["-5.000", "0", "5.000", "10.000", "15.000", "20.000"])
    axis_style(ax, "Passeggeri/giorno feriale (2025 - 2024)")
    clean(ax)
    add_source(fig, "Fonte: Dati frequentazione linee regionali Lombardia, 2024-2025. Metodo: solo campagne disponibili in entrambi gli anni; escluse S10, S30, S31, S40, S50.")
    fig.subplots_adjust(left=0.22, right=0.945, top=0.84, bottom=0.135)
    return save(fig, "02_variazione_assoluta_linee_suburbane_2025_2024")


def chart_metro() -> tuple[Path, Path]:
    df = pd.read_csv(p("linee", "comparazione metro", "numeri_da_metropolitana.csv"))
    genova = df["servizio"].eq("Genova Metro")
    df.loc[genova, "passeggeri_annui"] = 12_600_000
    df.loc[genova, "passeggeri_annui_label"] = "12,6 mln"
    df = df.sort_values("passeggeri_annui", ascending=True).reset_index(drop=True)
    fig, ax = setup()
    add_header(
        fig,
        "Passeggeri annui per linea",
        "La S8 ha numeri da metropolitana.",
        title_size=32,
    )
    vals = df["passeggeri_annui"] / 1_000_000
    colors = [S8 if "S8" in s else BAR_MUTED for s in df["servizio"]]
    bars = ax.barh(range(len(df)), vals, color=colors, edgecolor=[S8_EDGE if "S8" in s else (1, 1, 1, 0) for s in df["servizio"]], linewidth=[2.2 if "S8" in s else 0 for s in df["servizio"]], height=0.66)
    for bar, servizio in zip(bars, df["servizio"]):
        if "S8" not in servizio:
            bar.set_alpha(0.58)
    ax.set_yticks([])
    for i, row in df.iterrows():
        is_s8 = "S8" in row["servizio"]
        ax.text(-0.36, i, shorten(row["servizio"], 35), ha="right", va="center", fontsize=12.1, fontproperties=BOLD_FONT if is_s8 else TEXT_FONT, color=OFF_WHITE if is_s8 else SOFT_WHITE)
        ax.text(vals.iloc[i] + 0.20, i, row["passeggeri_annui_label"], ha="left", va="center", fontsize=11.8, fontproperties=BOLD_FONT if is_s8 else TEXT_FONT, color=OFF_WHITE if is_s8 else SOFT_WHITE)
        if pd.notna(row["freq_punta"]):
            freq = str(row["freq_punta"]).replace(".0", "").replace(".", ",")
            ax.text(
                vals.iloc[i] + 0.18,
                i - 0.22,
                f"freq. {freq} min",
                ha="left",
                va="center",
                fontsize=9.7,
                fontproperties=BOLD_FONT if is_s8 else TEXT_FONT,
                color=NOTE_TEXT,
                bbox={
                    "boxstyle": "round,pad=0.17",
                    "facecolor": NOTE_FACE,
                    "edgecolor": S8_EDGE if is_s8 else MUTED_WHITE,
                    "linewidth": 0.9,
                    "alpha": 0.96,
                },
            )
    ax.set_xlim(0, 18.7)
    ax.set_xticks([0, 5, 10, 15])
    axis_style(ax, "Passeggeri annui, milioni")
    clean(ax)
    add_source(fig, "Fonti: dati passeggeri e frequenze da schede/operatori indicati nel dataset; S8 benchmark con dati utente/Trenord.")
    fig.subplots_adjust(left=0.28, right=0.955, top=0.84, bottom=0.135)
    return save(fig, "03_comparazione_metro_s8_benchmark")


def chart_top20() -> tuple[Path, Path]:
    df = pd.read_excel(
        p("linee", "top 20 italia", "base_dati_top20_linee_ferroviarie_nonAV_italia_colori_finali_tilo_blu_ticino.xlsx"),
        sheet_name="Top20",
    ).sort_values("rank", ascending=False).reset_index(drop=True)
    fig, ax = setup()
    add_header(
        fig,
        "Le 20 linee ferroviarie locali più usate in Italia",
        "La S8 Lecco-Milano è al 4° posto, con 14,8 milioni di passeggeri annui.",
        title_size=31,
    )
    vals = df["central_mln"].astype(float)
    ax.barh(range(len(df)), vals, color=[S8 if x == "S8" else BAR_MUTED for x in df["line_code"]], edgecolor=[S8_EDGE if x == "S8" else (1, 1, 1, 0) for x in df["line_code"]], linewidth=[2.1 if x == "S8" else 0 for x in df["line_code"]], height=0.63)
    ax.set_yticks([])
    for i, row in df.iterrows():
        code = row["line_code"]
        name = str(row["line_name"]).replace("–", "-")
        if name.startswith(code):
            name = name[len(code):].strip()
        label = f"{int(row['rank'])}. {code} · {shorten(name, 36)}"
        is_s8 = code == "S8"
        ax.text(-0.45, i, label, ha="right", va="center", fontsize=9.5, fontproperties=BOLD_FONT if is_s8 else TEXT_FONT, color=OFF_WHITE if is_s8 else SOFT_WHITE)
        ax.add_patch(Rectangle((-0.25, i - 0.18), 0.060, 0.36, transform=ax.transData, clip_on=False, color=str(row["color_hex"]), linewidth=0))
        ax.text(vals.iloc[i] + 0.13, i, f"{vals.iloc[i]:.1f}", ha="left", va="center", fontsize=10.0 if not is_s8 else 12.1, fontproperties=BOLD_FONT if is_s8 else TEXT_FONT, color=OFF_WHITE if is_s8 else SOFT_WHITE)
    ax.text(16.4, int(np.where(df["line_code"].to_numpy() == "S8")[0][0]), "4° in Italia", ha="left", va="center", fontsize=12.0, fontproperties=BOLD_FONT, color=OFF_WHITE)
    ax.set_xlim(0, 22.2)
    ax.set_xticks([0, 5, 10, 15, 20])
    axis_style(ax, "Milioni di passeggeri annui")
    clean(ax)
    add_source(fig, "Fonte: elaborazione su dati Trenord, Cotral, Trenitalia e Regioni. Lombardia: campagne di frequentazione 2025.")
    fig.subplots_adjust(left=0.32, right=0.945, top=0.84, bottom=0.135)
    return save(fig, "04_top20_linee_locali_italia_s8")


def chart_stazioni_indice() -> tuple[Path, Path]:
    df = pd.read_csv(
        p("ANALISI INIZIALE", "stazioni", "update", "S8_stazioni_Saliti24H_Novembre_2015_2025_no_Maggianico_indice2019_100.csv")
    )
    df = df[~df["Stazione"].eq("Vercurago-S. Girolamo")].copy()
    fig, ax = setup()
    add_header(
        fig,
        "Passeggeri nelle stazioni S8: 2015-2025",
        "Indice base 2019=100: nel Meratese la crescita accelera dopo il 2022.",
        title_size=31,
    )
    for station, sub in df.groupby("Stazione"):
        sub = sub.sort_values("Anno")
        is_mer = station in MERATESE
        color = STATION_COLORS.get(station, LINE_MUTED)
        ax.plot(sub["Anno"], sub["Indice_2019_100"], color=color, linewidth=3.9 if is_mer else 1.7, marker="o", markersize=5.2 if is_mer else 3.1, alpha=1 if is_mer else 0.60)
        last = sub.iloc[-1]
        if is_mer or last["Indice_2019_100"] > 115 or last["Indice_2019_100"] < 75:
            label_right(ax, 2025.12, last["Indice_2019_100"], station, color if is_mer else MUTED_WHITE, is_mer, 10.0 if is_mer else 8.9)
    ax.axhline(100, color=MUTED_WHITE, linewidth=1.0, linestyle=":", alpha=0.65)
    ax.set_xlim(2014.7, 2026.3)
    ax.set_ylim(0, 275)
    ax.set_xticks([2015, 2017, 2019, 2021, 2023, 2025])
    ax.set_yticks([0, 50, 100, 150, 200, 250])
    axis_style(ax, "Anno", "Indice (2019=100)")
    clean(ax)
    add_source(fig, "Fonti: Regione Lombardia, Flussi Stazioni Ferroviarie 2015-2023; campagne Lombardia 2024-2025; elaborazione su novembre feriale.")
    fig.subplots_adjust(left=0.085, right=0.86, top=0.84, bottom=0.135)
    return save(fig, "05_stazioni_s8_indice_2019_100")


def chart_saliti_per_corsa() -> tuple[Path, Path]:
    df = pd.read_csv(
        p(
            "stazioni",
            "altro",
            "Scatter_precedenti_filtrati_base700",
            "Dataset_scatter_precedenti_filtrati_base2019_almeno700.csv",
        )
    )
    fig, ax = setup()
    add_header(
        fig,
        "Crescita passeggeri nelle stazioni lombarde",
        "Le stazioni meratesi sono un caso raro nel confronto lombardo.",
        title_size=31,
    )
    x = df["Growth_pct_Saliti24H"]
    y = df["Growth_pct_Saliti_per_corsa"]
    size = np.clip(np.sqrt(df["Delta_abs_Saliti24H"].clip(lower=1)) * 3.2, 12, 170)
    others = df[~df["IsMeratese"]]
    ax.scatter(
        others["Growth_pct_Saliti24H"],
        others["Growth_pct_Saliti_per_corsa"],
        s=np.clip(np.sqrt(others["Delta_abs_Saliti24H"].clip(lower=1)) * 3.4, 14, 160),
        color=(1, 1, 1, 0.22),
        linewidth=0,
    )
    mer = df[df["IsMeratese"]]
    for _, row in mer.iterrows():
        label = str(row["Label"])
        ax.scatter(
            row["Growth_pct_Saliti24H"],
            row["Growth_pct_Saliti_per_corsa"],
            s=190,
            color=STATION_COLORS.get(label, S8),
            edgecolor=OFF_WHITE,
            linewidth=1.1,
            zorder=4,
        )
    ax.axhline(0, color=MUTED_WHITE, linestyle=":", linewidth=1.1, alpha=0.75)
    ax.axvline(0, color=MUTED_WHITE, linestyle=":", linewidth=1.1, alpha=0.75)
    label_offsets = {
        "Airuno": (4, 2),
        "Osnago": (4, 1),
        "Cernusco-Merate": (4, 3),
        "Olgiate-Calco-Brivio": (4, -5),
    }
    for _, row in mer.iterrows():
        label = str(row["Label"])
        dx, dy = label_offsets[label]
        label_box(
            ax,
            row["Growth_pct_Saliti24H"] + dx,
            row["Growth_pct_Saliti_per_corsa"] + dy,
            label,
            STATION_COLORS.get(label, S8),
            size=11.3,
            text_color="#5b2438",
        )
    selected = {
        "MILANOSCRISTOFORO": (2, 3, "Milano S. Cristoforo"),
        "TREVIGLIOOVEST": (2, 3, "Treviglio Ovest"),
        "CARNATEUSMATE": (2, -4, "Carnate Usmate"),
        "ARCORE": (2, 2, "Arcore"),
        "CALOLZIOCORTEOLGINATE": (2, -5, "Calolziocorte-Olginate"),
    }
    for key, (dx, dy, label) in selected.items():
        sub = df[df["StationKey"].eq(key)]
        if not sub.empty:
            row = sub.iloc[0]
            label_box(
                ax,
                row["Growth_pct_Saliti24H"] + dx,
                row["Growth_pct_Saliti_per_corsa"] + dy,
                label,
                "#c9d0ca",
                size=8.8,
                facecolor=GREY_FACE,
                text_color=GREY_TEXT,
            )
    ax.set_xlim(-75, 168)
    ax.set_ylim(-75, 145)
    ax.set_xticks([-50, 0, 50, 100, 150])
    ax.set_yticks([-50, 0, 50, 100])
    axis_style(ax, "Crescita % passeggeri 2019-2025", "Cambiamento % passeggeri per corsa 2019-2025")
    clean(ax)
    add_source(fig, "Filtro: stazioni lombarde con almeno 700 saliti24H nel 2019. Dimensione punto = crescita assoluta passeggeri.")
    fig.subplots_adjust(left=0.09, right=0.945, top=0.84, bottom=0.135)
    return save(fig, "06_saliti_per_corsa_stazioni_s8")


def chart_peso_punta() -> tuple[Path, Path]:
    df = pd.read_csv(
        p("stazioni", "cambio rapporto", "orari", "Grafico_scientifico_S8_peso_punta_2015_2025_dataset_v2.csv")
    )
    fig, ax = setup()
    add_header(
        fig,
        "Peso della punta nelle stazioni S8",
        "Quota di saliti 7-9 sul totale giornaliero, novembre feriale 2015-2025.",
        title_size=31,
    )
    mer_label_offsets = {
        "Airuno": 2.2,
        "Osnago": -0.2,
        "Cernusco-Merate": 3.4,
        "Olgiate-Calco-Brivio": 1.1,
    }
    other_label_y = {
        "Carnate Usmate": 23.6,
        "Arcore": 22.0,
        "Calolziocorte-Olginate": 20.4,
        "Monza": 18.5,
        "Sesto S. Giovanni": 14.2,
        "Lecco": 12.4,
        "Milano Greco Pirelli": 10.8,
        "Milano Porta Garibaldi": 9.6,
    }
    for station, sub in df.groupby("Stazione"):
        sub = sub.sort_values("Anno")
        is_mer = station in MERATESE
        color = STATION_COLORS.get(station, LINE_MUTED)
        ax.plot(
            sub["Anno"],
            sub["Peso_punta_pct"],
            color=color,
            linewidth=4.0 if is_mer else 1.45,
            marker="o",
            markersize=5.2 if is_mer else 2.8,
            alpha=1 if is_mer else 0.46,
        )
        last = sub.iloc[-1]
        if is_mer:
            label_box(
                ax,
                2025.18,
                last["Peso_punta_pct"] + mer_label_offsets[station],
                station,
                color,
                size=9.2,
                text_color="#5b2438",
            )
        elif station in other_label_y:
            label_right(ax, 2025.14, other_label_y[station], station, MUTED_WHITE, False, 8.6)
    ax.set_xlim(2014.7, 2026.5)
    ax.set_ylim(0, 62)
    ax.set_xticks([2015, 2017, 2019, 2021, 2023, 2025])
    ax.set_yticks([0, 10, 20, 30, 40, 50, 60])
    axis_style(ax, "Anno", "Saliti 7-9 / saliti 24H (%)")
    clean(ax)
    add_source(fig, "Fonti: Regione Lombardia, Flussi Stazioni Ferroviarie; frequentazione stazioni del servizio ferroviario regionale.")
    fig.subplots_adjust(left=0.095, right=0.86, top=0.84, bottom=0.135)
    return save(fig, "07_peso_punta_stazioni_s8")


def chart_punta_morbida() -> tuple[Path, Path]:
    series = pd.read_csv(
        p("stazioni", "cambio rapporto", "orari", "Meratese_series_Saliti7-9_Saliti24H_2015_2025.csv")
    )
    rows: list[dict[str, float | str]] = []
    current = series[series["Anno"].isin([2019, 2025])].copy()
    for station, sub in current.groupby("Stazione"):
        wide = sub.set_index("Anno")
        delta_tot = float(wide.loc[2025, "Saliti24H"] - wide.loc[2019, "Saliti24H"])
        delta_punta = float(wide.loc[2025, "Saliti7-9"] - wide.loc[2019, "Saliti7-9"])
        rows.append(
            {
                "Stazione": station,
                "punta": delta_punta,
                "morbida": delta_tot - delta_punta,
                "delta_tot": delta_tot,
            }
        )
    totals = current.groupby("Anno")[["Saliti7-9", "Saliti24H"]].sum()
    delta_tot = float(totals.loc[2025, "Saliti24H"] - totals.loc[2019, "Saliti24H"])
    delta_punta = float(totals.loc[2025, "Saliti7-9"] - totals.loc[2019, "Saliti7-9"])
    rows.append(
        {
            "Stazione": "Meratese totale",
            "punta": delta_punta,
            "morbida": delta_tot - delta_punta,
            "delta_tot": delta_tot,
        }
    )
    df = pd.DataFrame(rows)
    order = ["Meratese totale", "Airuno", "Osnago", "Cernusco-Merate", "Olgiate-Calco-Brivio"]
    df["order"] = df["Stazione"].map({k: i for i, k in enumerate(order)})
    df = df.sort_values("order", ascending=False).reset_index(drop=True)
    fig, ax = setup()
    add_header(
        fig,
        "Crescita meratese: punta e morbida",
        "Variazione saliti/giorno 2025 vs 2019: quasi tutta la crescita è fuori dalla fascia 7-9.",
        title_size=31,
    )
    y = np.arange(len(df))
    ax.barh(y, df["punta"], color=PUNTA, height=0.64, label="Punta 7-9")
    ax.barh(y, df["morbida"], left=df["punta"], color=MORBIDA, height=0.64, label="Morbida / fuori 7-9")
    ax.axvline(0, color=SOFT_WHITE, linewidth=1.0, alpha=0.85)
    ax.set_yticks([])
    for i, row in df.iterrows():
        station = row["Stazione"]
        color = STATION_COLORS.get(station, OFF_WHITE)
        is_agg = station == "Meratese totale"
        ax.text(-250, i, station, ha="right", va="center", fontsize=12.1, fontproperties=BOLD_FONT if is_agg else TEXT_FONT, color=OFF_WHITE if is_agg else color)
        ax.text(row["delta_tot"] + 90, i, fmt_plus(row["delta_tot"]), ha="left", va="center", fontsize=11.5, fontproperties=BOLD_FONT if is_agg else TEXT_FONT, color=OFF_WHITE)
        if row["delta_tot"] > 0:
            pct_morbida = row["morbida"] / row["delta_tot"] * 100
            ax.text(row["punta"] + row["morbida"] / 2, i, f"{pct_morbida:.0f}%", ha="center", va="center", fontsize=10.4, fontproperties=BOLD_FONT, color=GREEN_DARK)
    handles = [Patch(facecolor=PUNTA, label="Punta 7-9"), Patch(facecolor=MORBIDA, label="Morbida / fuori 7-9")]
    leg = ax.legend(handles=handles, loc="lower right", bbox_to_anchor=(0.985, 0.035), frameon=True, fontsize=10.4)
    leg.get_frame().set_facecolor(NOTE_FACE)
    leg.get_frame().set_edgecolor(SOFT_WHITE)
    leg.get_frame().set_alpha(0.96)
    for txt in leg.get_texts():
        txt.set_color(NOTE_TEXT)
        txt.set_fontproperties(TEXT_FONT)
    ax.set_xlim(-300, 4800)
    ax.set_xticks([0, 1000, 2000, 3000, 4000])
    ax.set_xticklabels(["0", "1.000", "2.000", "3.000", "4.000"])
    axis_style(ax, "Passeggeri/giorno (2025 - 2019)")
    clean(ax)
    add_source(fig, "Definizioni: punta = variazione saliti 7-9; morbida = variazione saliti 24H al netto della punta. Fonte: Regione Lombardia/Trenord.")
    fig.subplots_adjust(left=0.235, right=0.92, top=0.84, bottom=0.135)
    return save(fig, "08_crescita_meratese_punta_morbida")


def generate() -> list[dict[str, str]]:
    charts = [
        ("01 Linee suburbane indice 2019=100", chart_linee_s_indice),
        ("02 Variazione assoluta linee suburbane", chart_delta_linee),
        ("03 Comparazione metro", chart_metro),
        ("04 Top20 linee locali Italia", chart_top20),
        ("05 Stazioni S8 indice 2019=100", chart_stazioni_indice),
        ("06 Saliti per corsa", chart_saliti_per_corsa),
        ("07 Peso punta stazioni S8", chart_peso_punta),
        ("08 Crescita punta/morbida", chart_punta_morbida),
    ]
    manifest: list[dict[str, str]] = []
    for title, fn in charts:
        transparent, preview = fn()
        manifest.append({"grafico": title, "trasparente": str(transparent), "preview_verde": str(preview)})
        print(title)
        print(transparent)
        print(preview)
    manifest_path = next_path("manifest_grafici_fedeli_canva", ".json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(manifest_path)
    return manifest


def copy_ready(manifest: list[dict[str, str]]) -> None:
    for idx in range(1, 100):
        ready_dir = READY_ROOT / f"pronti_canva_v{idx:02d}"
        if not ready_dir.exists():
            break
    else:
        raise RuntimeError("Troppi pacchetti pronti Canva gia' presenti.")
    ready_dir.mkdir(parents=True, exist_ok=False)
    names = [
        "01_linee_suburbane_indice_2019_100.png",
        "02_variazione_assoluta_linee_suburbane.png",
        "03_comparazione_metro_s8.png",
        "04_top20_linee_locali_italia.png",
        "05_stazioni_s8_indice_2019_100.png",
        "06_saliti_per_corsa_stazioni_s8.png",
        "07_peso_punta_stazioni_s8.png",
        "08_crescita_punta_morbida_meratese.png",
    ]
    for row, name in zip(manifest, names):
        Image.open(row["trasparente"]).save(ready_dir / name)

    previews = [Image.open(row["preview_verde"]).convert("RGB") for row in manifest]
    thumbs: list[Image.Image] = []
    for img, name in zip(previews, names):
        img.thumbnail((640, 360))
        canvas = Image.new("RGB", (640, 400), "white")
        canvas.paste(img, (0, 0))
        ImageDraw.Draw(canvas).text((10, 368), name, fill=(0, 0, 0))
        thumbs.append(canvas)
    sheet = Image.new("RGB", (1280, 1600), (235, 235, 235))
    for idx, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((idx % 2) * 640, (idx // 2) * 400))
    sheet.save(ready_dir / "00_anteprima_tutti_grafici.jpg", quality=92)
    (ready_dir / "README_USO_CANVA.md").write_text(
        "PNG trasparenti 16:9 da importare in Canva sopra sfondo #1f642c.\n"
        "La preview JPG serve solo per controllo rapido su verde.\n"
        "Firma fissa: Analisi di Simone Ghezzi Colombo.\n",
        encoding="utf-8",
    )
    print(ready_dir)


if __name__ == "__main__":
    copy_ready(generate())

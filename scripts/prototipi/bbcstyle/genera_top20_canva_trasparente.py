from __future__ import annotations

from pathlib import Path

import bbcstyle
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = (
    ROOT
    / "linee"
    / "top 20 italia"
    / "base_dati_top20_linee_ferroviarie_nonAV_italia_colori_finali_tilo_blu_ticino.xlsx"
)
OUT_DIR = Path(__file__).resolve().parent
FONT_DIR = OUT_DIR / "assets" / "fonts"

GREEN = "#1f642c"
OFF_WHITE = "#f7fbf4"
SOFT_WHITE = "#dfeee0"
MUTED_WHITE = "#bdd8bf"
S8_FILL = "#f2b8c1"
S8_EDGE = "#ffd6de"


def next_output_path(stem: str) -> Path:
    for idx in range(1, 100):
        candidate = OUT_DIR / f"{stem}_v{idx:02d}.png"
        if not candidate.exists():
            return candidate
    raise RuntimeError("Troppi output gia' presenti: pulire o aumentare il limite.")


def load_font(filename: str) -> FontProperties:
    path = FONT_DIR / filename
    fm.fontManager.addfont(str(path))
    return FontProperties(fname=str(path))


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


def build_label(row: pd.Series) -> str:
    name = str(row["line_name"]).replace("–", "-")
    code = str(row["line_code"])
    if name.startswith(code):
        name = name[len(code) :].strip()
    return f"{int(row['rank'])}. {code} · {shorten(name)}"


def make_preview(transparent_path: Path, preview_path: Path) -> None:
    image = Image.open(transparent_path).convert("RGBA")
    bg = Image.new("RGBA", image.size, GREEN)
    bg.alpha_composite(image)
    bg.convert("RGB").save(preview_path, quality=95)


def main() -> None:
    title_font = load_font("BricolageGrotesque.ttf")
    text_font = load_font("OpenSans-Regular.ttf")
    bold_font = load_font("OpenSans-Bold.ttf")

    out_transparent = next_output_path(
        "top20_linee_ferroviarie_nonAV_S8_canva_trasparente_body"
    )
    out_preview = next_output_path("top20_linee_ferroviarie_nonAV_S8_canva_preview_verde")

    df = pd.read_excel(DATA_PATH, sheet_name="Top20")
    df = df.sort_values("rank", ascending=False).reset_index(drop=True)
    df["value"] = pd.to_numeric(df["central_mln"], errors="coerce")
    df["label"] = df.apply(build_label, axis=1)

    bbcstyle.use()
    plt.rcParams.update(
        {
            "figure.facecolor": "none",
            "axes.facecolor": "none",
            "savefig.facecolor": "none",
            "axes.grid": False,
        }
    )

    fig, ax = plt.subplots(figsize=(16, 9), constrained_layout=False)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    colors = [
        S8_FILL if code == "S8" else (1, 1, 1, 0.28)
        for code in df["line_code"]
    ]
    edgecolors = [
        S8_EDGE if code == "S8" else (1, 1, 1, 0.0)
        for code in df["line_code"]
    ]
    linewidths = [1.8 if code == "S8" else 0 for code in df["line_code"]]

    bars = ax.barh(
        range(len(df)),
        df["value"],
        color=colors,
        edgecolor=edgecolors,
        linewidth=linewidths,
        height=0.62,
    )

    ax.set_yticks([])
    ax.set_ylim(-0.8, len(df) - 0.2)

    for bar, value, code in zip(bars, df["value"], df["line_code"]):
        is_s8 = code == "S8"
        ax.text(
            value + 0.13,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}",
            va="center",
            ha="left",
            fontsize=13.2 if is_s8 else 11.4,
            fontproperties=bold_font if is_s8 else text_font,
            color=OFF_WHITE if is_s8 else SOFT_WHITE,
        )

    for idx, row in df.iterrows():
        is_s8 = row["line_code"] == "S8"
        ax.text(
            -0.45,
            idx,
            row["label"],
            va="center",
            ha="right",
            fontsize=10.4,
            fontproperties=bold_font if is_s8 else text_font,
            color=OFF_WHITE if is_s8 else SOFT_WHITE,
        )
        ax.add_patch(
            Rectangle(
                (-0.25, idx - 0.19),
                0.055,
                0.38,
                transform=ax.transData,
                clip_on=False,
                color=str(row["color_hex"]),
                linewidth=0,
            )
        )

    s8_y = int(df.index[df["line_code"] == "S8"][0])
    s8_value = float(df.loc[df["line_code"] == "S8", "value"].iloc[0])
    ax.plot(
        [s8_value + 1.05, s8_value + 1.64],
        [s8_y, s8_y],
        color=S8_EDGE,
        linewidth=1.2,
        solid_capstyle="round",
    )
    ax.text(
        s8_value + 1.82,
        s8_y,
        "4° posto in Italia",
        va="center",
        ha="left",
        fontsize=12.2,
        fontproperties=bold_font,
        color=OFF_WHITE,
    )

    ax.set_xlim(0, 23.2)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.tick_params(axis="x", labelsize=10.6, colors=MUTED_WHITE)
    ax.set_xlabel(
        "Milioni di passeggeri annui",
        fontsize=11.2,
        fontproperties=text_font,
        color=SOFT_WHITE,
        labelpad=8,
    )
    ax.xaxis.grid(True, color=(1, 1, 1, 0.18), linewidth=1.0)
    ax.yaxis.grid(False)

    for label in ax.get_xticklabels():
        label.set_fontproperties(text_font)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.text(
        0.055,
        0.070,
        "Fonte: elaborazione su dati Trenord, Cotral, Trenitalia e Regioni. Lombardia: campagne di frequentazione 2025.",
        ha="left",
        va="bottom",
        fontsize=8.5,
        fontproperties=text_font,
        color=MUTED_WHITE,
    )

    # The top space is intentionally left transparent for a Canva title.
    fig.subplots_adjust(left=0.30, right=0.94, top=0.78, bottom=0.15)
    fig.savefig(out_transparent, dpi=220, transparent=True)
    plt.close(fig)

    make_preview(out_transparent, out_preview)
    print(out_transparent)
    print(out_preview)
    _ = title_font


if __name__ == "__main__":
    main()

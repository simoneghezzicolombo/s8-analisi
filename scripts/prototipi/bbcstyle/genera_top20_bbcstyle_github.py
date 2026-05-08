from __future__ import annotations

from pathlib import Path

import bbcstyle
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = (
    ROOT
    / "linee"
    / "top 20 italia"
    / "base_dati_top20_linee_ferroviarie_nonAV_italia_colori_finali_tilo_blu_ticino.xlsx"
)
OUT_DIR = Path(__file__).resolve().parent
OUT_STEM = "top20_linee_ferroviarie_nonAV_S8_bbcstyle_github"


def next_output_path() -> Path:
    for idx in range(2, 100):
        candidate = OUT_DIR / f"{OUT_STEM}_v{idx:02d}.png"
        if not candidate.exists():
            return candidate
    raise RuntimeError("Troppi output gia' presenti: pulire o aumentare il limite.")


def shorten(text: str, max_chars: int = 44) -> str:
    text = (
        str(text)
        .replace("–", "-")
        .replace(" / ", "/")
        .replace("Fiumicino Aeroporto", "Fiumicino")
        .replace("Milano Passante", "Milano Pass.")
        .replace("Milano Porta Garibaldi", "Milano P. Garibaldi")
        .replace("Civita Castellana", "Civita Cast.")
        .replace("San Cristoforo", "S. Cristoforo")
        .replace("Mestre/Venezia S.L.", "Mestre/Venezia S.L.")
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


def main() -> None:
    out_path = next_output_path()
    df = pd.read_excel(DATA_PATH, sheet_name="Top20")
    df = df.sort_values("rank", ascending=False).reset_index(drop=True)
    df["value"] = pd.to_numeric(df["central_mln"], errors="coerce")
    df["label"] = df.apply(build_label, axis=1)

    bbcstyle.use()
    plt.rcParams.update(
        {
            "axes.grid": False,
            "font.family": "DejaVu Sans",
            "axes.labelsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )

    fig, ax = plt.subplots(figsize=(16, 9), constrained_layout=False)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    base_grey = "#D7D7D7"
    s8_fill = "#E9B2BB"
    s8_edge = "#8F3E59"
    text_dark = "#1F1F1F"
    muted = "#6B6B6B"

    colors = [s8_fill if code == "S8" else base_grey for code in df["line_code"]]
    edgecolors = [s8_edge if code == "S8" else "white" for code in df["line_code"]]
    linewidths = [1.65 if code == "S8" else 0 for code in df["line_code"]]

    bars = ax.barh(
        range(len(df)),
        df["value"],
        color=colors,
        edgecolor=edgecolors,
        linewidth=linewidths,
        height=0.68,
    )

    ax.set_yticks([])
    ax.set_ylim(-0.9, len(df) - 0.25)

    for bar, value, code in zip(bars, df["value"], df["line_code"]):
        is_s8 = code == "S8"
        ax.text(
            value + 0.13,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}",
            va="center",
            ha="left",
            fontsize=15 if is_s8 else 13.5,
            fontweight="bold" if is_s8 else "normal",
            color=s8_edge if is_s8 else "#4A4A4A",
        )

    for idx, row in df.iterrows():
        is_s8 = row["line_code"] == "S8"
        ax.text(
            -0.45,
            idx,
            row["label"],
            va="center",
            ha="right",
            fontsize=9.7,
            fontweight="bold" if is_s8 else "normal",
            color=text_dark,
        )

    s8_y = int(df.index[df["line_code"] == "S8"][0])
    s8_value = float(df.loc[df["line_code"] == "S8", "value"].iloc[0])
    ax.plot(
        [s8_value + 1.05, s8_value + 1.68],
        [s8_y, s8_y],
        color=s8_edge,
        linewidth=1.2,
        solid_capstyle="round",
    )
    ax.text(
        s8_value + 1.85,
        s8_y,
        "4° posto in Italia",
        va="center",
        ha="left",
        fontsize=11.5,
        fontweight="bold",
        color=s8_edge,
    )

    # Small route-colour chips preserve the original line-colour information
    # without turning the chart into a rainbow ranking.
    for idx, row in df.iterrows():
        ax.add_patch(
            Rectangle(
                (-0.25, idx - 0.20),
                0.055,
                0.40,
                transform=ax.transData,
                clip_on=False,
                color=str(row["color_hex"]),
                linewidth=0,
            )
        )

    ax.set_xlim(0, 23.2)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_xlabel("Milioni di passeggeri annui", fontsize=11.5, color=text_dark, labelpad=8)
    ax.tick_params(axis="x", labelsize=10.5, colors=muted)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(True, color="#E7E7E7", linewidth=1.0)
    ax.yaxis.grid(False)

    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.text(
        0.055,
        0.935,
        "Le 20 linee ferroviarie locali più usate in Italia",
        ha="left",
        va="top",
        fontsize=22,
        fontweight="bold",
        color=text_dark,
    )
    fig.text(
        0.055,
        0.885,
        "Passeggeri annui 2024-2025, in milioni. La S8 Lecco-Milano è al 4° posto.",
        ha="left",
        va="top",
        fontsize=13.2,
        color="#4A4A4A",
    )
    fig.text(
        0.055,
        0.045,
        "Fonte: elaborazione su dati Trenord, Cotral, Trenitalia e Regioni. "
        "Per la Lombardia: campagne di frequentazione 2025.",
        ha="left",
        va="bottom",
        fontsize=8.8,
        color="#4A4A4A",
    )
    fig.add_artist(
        plt.Line2D(
            [0.055, 0.945],
            [0.075, 0.075],
            transform=fig.transFigure,
            linewidth=1.2,
            color="#B8B8B8",
        )
    )

    fig.subplots_adjust(left=0.30, right=0.94, top=0.82, bottom=0.13)
    fig.savefig(out_path, dpi=220, facecolor="white")
    plt.close(fig)
    print(out_path)


if __name__ == "__main__":
    main()

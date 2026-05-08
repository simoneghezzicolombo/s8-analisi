import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from common import *

def main():
    df = load_data()
    plot_df = df.sort_values("rank", ascending=True).copy()
    plot_df = plot_df.iloc[::-1].copy()
    plot_df["y"] = range(len(plot_df))

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 24.0)
    ax.set_ylim(-1.0, len(plot_df) + 1.45)

    fig.text(0.065, 0.925, "La S8 è entrata nella fascia alta nazionale",
             ha="left", va="top", fontsize=25.5, fontweight="bold", color="#111111")
    fig.text(0.065, 0.868, "Passeggeri annui 2024–2025 · linee ferroviarie locali/non AV · valori in milioni",
             ha="left", va="top", fontsize=13.0, color="#555555")
    fig.text(0.935, 0.925, "Analisi di Simone Ghezzi Colombo",
             ha="right", va="top", fontsize=10.0, color="#666666")

    for x in [0, 5, 10, 15, 20]:
        ax.axvline(x, color="#EDEDED", linewidth=1, zorder=0)
        ax.text(x, -0.48, str(x), ha="center", va="top", fontsize=9.5, color="#666666")
    ax.text(12, -0.90, "Milioni di passeggeri annui", ha="center", va="top", fontsize=11.2, color="#333333")

    s8_y = None
    s8_val = None
    for _, row in plot_df.iterrows():
        y = row["y"]
        is_s8 = row["line_code"] == "S8"
        if is_s8:
            s8_y, s8_val = y, row["central_mln"]
            ax.add_patch(FancyBboxPatch((-0.10, y - 0.46), 23.25, 0.92,
                                        boxstyle="round,pad=0,rounding_size=0.08",
                                        facecolor="#FDF0F0", edgecolor="none", zorder=1))
            bar_color, edge, lw, height = S8_FILL, S8_EDGE, 2.4, 0.72
        elif row["line_code"] in LOMBARDY_CODES:
            bar_color, edge, lw, height = softened(row["color_hex"], 1.10), None, 0, 0.58
        else:
            bar_color, edge, lw, height = "#D7D7D7", None, 0, 0.54

        rounded_rect(ax, 0, y, row["central_mln"], height, bar_color,
                     edgecolor=edge if edge else bar_color, lw=lw, zorder=3)
        ax.text(-0.18, y, row["rank_label"], ha="right", va="center",
                fontsize=10.6 if not is_s8 else 12.0,
                fontweight="bold" if is_s8 else "normal",
                color=S8_DARK if is_s8 else "#222222", zorder=4)
        ax.text(row["central_mln"] + 0.22 if is_s8 else row["central_mln"] + 0.13,
                y,
                f"{row['central_mln']:.1f} mln" if is_s8 else f"{row['central_mln']:.1f}",
                ha="left", va="center",
                fontsize=13.6 if is_s8 else 10.0,
                fontweight="bold" if is_s8 else "normal",
                color=S8_DARK if is_s8 else "#333333", zorder=4)

    callout_x, callout_y = 16.3, 13.25
    ax.add_patch(FancyBboxPatch((callout_x, callout_y - 0.78), 5.4, 1.38,
                                boxstyle="round,pad=0.25,rounding_size=0.16",
                                facecolor="#FCE7E7", edgecolor="#F3B5C0", linewidth=1.2, zorder=2))
    ax.text(callout_x + 0.24, callout_y, "Nel 2019:\nS8 circa 21ª–22ª",
            ha="left", va="center", fontsize=12.8, fontweight="bold", color=S8_DARK, zorder=4)
    if s8_y is not None:
        ax.plot([s8_val + 0.20, callout_x + 0.05],
                [s8_y + 0.12, callout_y + 0.05],
                color="#C88498", linewidth=1.35, zorder=2)

    add_footer(fig, "Dati ufficiali e stime ragionate post-Covid")
    clean_axes(ax)

    out_png = FIG_DIR / "s8_top20_static_bar_slide.png"
    plt.savefig(out_png, dpi=240, bbox_inches="tight", facecolor="white")
    print(out_png)

if __name__ == "__main__":
    main()

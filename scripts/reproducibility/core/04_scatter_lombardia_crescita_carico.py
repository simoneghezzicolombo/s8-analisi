#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Crescita passeggeri nelle stazioni lombarde — scatterplot riproducibile.

Grafico richiesto:
X = crescita % passeggeri 2019-2025
Y = cambiamento % passeggeri per corsa 2019-2025
Filtro = Saliti24H_2019 >= 700
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
try:
    import plotly.graph_objects as go
except ImportError:
    go = None

from common import ensure_outdir, load_station_data, canonical_meratese_label, MERATESE_COLORS

BG = "#f5f5f3"


def make_dataset(master: pd.DataFrame, threshold=700) -> pd.DataFrame:
    sub = master[(master["Mese"] == "Novembre") & (master["TipoGiorno"] == "Feriale") & (master["Anno"].isin([2019, 2025]))].copy()
    display_map = master.sort_values("Anno").groupby("StationKey")["DisplayName"].last().to_dict()
    agg = sub.groupby(["Anno", "StationKey"], as_index=False)[["Saliti24H", "Saliti7-9", "Corse24H"]].mean()
    agg["Saliti_per_corsa"] = agg["Saliti24H"] / agg["Corse24H"]
    agg["Quota_7_9_pct"] = agg["Saliti7-9"] / agg["Saliti24H"] * 100
    pv = agg.pivot(index="StationKey", columns="Anno", values=["Saliti24H", "Saliti7-9", "Corse24H", "Saliti_per_corsa", "Quota_7_9_pct"])
    pv.columns = [f"{a}_{b}" for a, b in pv.columns]
    pv = pv.reset_index()
    pv["Stazione"] = pv["StationKey"].map(display_map)
    pv["Label"] = pv.apply(lambda r: canonical_meratese_label(r["StationKey"], r["Stazione"]), axis=1)
    pv["IsMeratese"] = pv["Label"].isin(["Osnago", "Cernusco-Merate", "Olgiate-Calco-Brivio", "Airuno"])
    pv["Growth_pct_Saliti24H"] = (pv["Saliti24H_2025"] / pv["Saliti24H_2019"] - 1) * 100
    pv["Growth_pct_Corse24H"] = (pv["Corse24H_2025"] / pv["Corse24H_2019"] - 1) * 100
    pv["Delta_abs_Saliti24H"] = pv["Saliti24H_2025"] - pv["Saliti24H_2019"]
    pv["Growth_pct_Saliti_per_corsa"] = (pv["Saliti_per_corsa_2025"] / pv["Saliti_per_corsa_2019"] - 1) * 100
    pv["Delta_quota_7_9_pp"] = pv["Quota_7_9_pct_2025"] - pv["Quota_7_9_pct_2019"]
    usable = pv[
        pv["Saliti24H_2019"].notna() & pv["Saliti24H_2025"].notna()
        & pv["Corse24H_2019"].notna() & pv["Corse24H_2025"].notna()
        & (pv["Saliti24H_2019"] > 0) & (pv["Corse24H_2019"] > 0) & (pv["Corse24H_2025"] > 0)
    ].copy()
    cols = [
        "StationKey",
        "Saliti24H_2019",
        "Saliti24H_2025",
        "Saliti7-9_2019",
        "Saliti7-9_2025",
        "Corse24H_2019",
        "Corse24H_2025",
        "Saliti_per_corsa_2019",
        "Saliti_per_corsa_2025",
        "Quota_7_9_pct_2019",
        "Quota_7_9_pct_2025",
        "Stazione",
        "Label",
        "IsMeratese",
        "Growth_pct_Saliti24H",
        "Delta_abs_Saliti24H",
        "Growth_pct_Corse24H",
        "Growth_pct_Saliti_per_corsa",
        "Delta_quota_7_9_pp",
    ]
    return usable[usable["Saliti24H_2019"] >= threshold].copy()[cols]


def make_png(df: pd.DataFrame, out: Path):
    others = df[~df["IsMeratese"]].copy()
    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    ax.scatter(others["Growth_pct_Saliti24H"], others["Growth_pct_Saliti_per_corsa"],
               s=np.clip(others["Delta_abs_Saliti24H"].abs().fillna(0) / 12, 12, 160),
               alpha=0.32, color="#9aa1aa", edgecolors="none")
    for label, color in MERATESE_COLORS.items():
        d = df[df["Label"] == label]
        if d.empty: continue
        ax.scatter(d["Growth_pct_Saliti24H"], d["Growth_pct_Saliti_per_corsa"],
                   s=np.clip(d["Delta_abs_Saliti24H"].abs().fillna(0) / 5, 110, 320),
                   color=color, edgecolors="white", linewidths=1.1, zorder=5)
        for _, r in d.iterrows():
            ax.text(r["Growth_pct_Saliti24H"] + 0.8, r["Growth_pct_Saliti_per_corsa"] + 0.9, label,
                    fontsize=10.2, color=color,
                    bbox=dict(boxstyle="round,pad=0.14", facecolor="white", edgecolor=color, linewidth=0.8), zorder=6)
    ax.axvline(0, linestyle=":", linewidth=1, color="#777")
    ax.axhline(0, linestyle=":", linewidth=1, color="#777")
    ax.set_xlabel("Crescita % dei passeggeri 2019→2025")
    ax.set_ylabel("Cambiamento % dei passeggeri per corsa 2019→2025")
    ax.grid(True, axis="both", alpha=0.18)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, colors="#4b5563")
    fig.text(0.06, 0.94, "Chi cresce molto e intensifica anche il carico per corsa?", fontsize=17, fontweight="bold", color="#424242")
    fig.text(0.06, 0.905, "Stazioni lombarde comparabili — novembre feriale — 2019 vs 2025", fontsize=12, color="#5b6570")
    fig.text(0.76, 0.94, "Analisi di Simone Ghezzi Colombo", fontsize=10.2, color="#555555")
    fig.text(0.06, 0.032, "In alto a destra: crescita forte accompagnata da maggiore carico medio su ogni treno.", fontsize=8.7, color="#5b6570")
    fig.text(0.06, 0.015, "Filtro: incluse solo stazioni con almeno 700 Saliti24H nel 2019. Dimensione punto = crescita assoluta passeggeri.", fontsize=8.7, color="#5b6570")
    fig.tight_layout(rect=[0.04, 0.06, 0.98, 0.88])
    fig.savefig(out, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def make_html(df: pd.DataFrame, out: Path):
    if go is None:
        print("Plotly non installato: HTML interattivo non generato.")
        return

    others = df[~df["IsMeratese"]].copy()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=others["Growth_pct_Saliti24H"], y=others["Growth_pct_Saliti_per_corsa"],
        mode="markers", name="Altre stazioni lombarde",
        marker=dict(size=np.clip(others["Delta_abs_Saliti24H"].abs().fillna(0) / 25, 7, 28), color="rgba(165,172,180,0.35)", line=dict(color="rgba(125,132,142,0.25)", width=0.5)),
        customdata=np.stack([others["Stazione"].astype(str), others["Saliti24H_2019"].round(0), others["Saliti24H_2025"].round(0), others["Growth_pct_Saliti24H"].round(2), others["Growth_pct_Corse24H"].round(2), others["Growth_pct_Saliti_per_corsa"].round(2), others["Delta_abs_Saliti24H"].round(0)], axis=-1),
        hovertemplate="<b>%{customdata[0]}</b><br>Saliti24H 2019→2025: %{customdata[1]:,.0f} → %{customdata[2]:,.0f}<br>Crescita passeggeri: %{customdata[3]:+.2f}%<br>Crescita corse: %{customdata[4]:+.2f}%<br>Cambiamento passeggeri/corsa: %{customdata[5]:+.2f}%<br>Δ passeggeri: %{customdata[6]:+,.0f}<extra></extra>"
    ))
    for label, color in MERATESE_COLORS.items():
        d = df[df["Label"] == label]
        if d.empty: continue
        fig.add_trace(go.Scatter(
            x=d["Growth_pct_Saliti24H"], y=d["Growth_pct_Saliti_per_corsa"], mode="markers+text", name=label, text=d["Label"], textposition="top right",
            marker=dict(size=np.clip(d["Delta_abs_Saliti24H"].abs().fillna(0) / 10, 14, 34), color=color, line=dict(color="white", width=1.2))
        ))
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(90,90,90,0.45)")
    fig.add_vline(x=0, line_dash="dot", line_color="rgba(90,90,90,0.45)")
    fig.update_layout(
        title=dict(text="Chi cresce molto e intensifica anche il carico per corsa?<br><sup>Stazioni lombarde comparabili — novembre feriale — 2019 vs 2025</sup>", x=0.02, xanchor="left", font=dict(size=22)),
        template="plotly_white", paper_bgcolor=BG, plot_bgcolor=BG, font=dict(color="#344055", size=14),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.0, bgcolor="rgba(255,255,255,0.75)"),
        margin=dict(l=70, r=30, t=100, b=90),
        xaxis=dict(title="Crescita % dei passeggeri 2019→2025", gridcolor="rgba(110,120,130,0.16)", zeroline=False),
        yaxis=dict(title="Cambiamento % dei passeggeri per corsa 2019→2025", gridcolor="rgba(110,120,130,0.16)", zeroline=False),
        annotations=[dict(x=0.01, y=-0.19, xref="paper", yref="paper", showarrow=False, align="left", text="Analisi di Simone Ghezzi Colombo · Filtro: base 2019 ≥ 700 Saliti24H · Dimensione punto = crescita assoluta passeggeri.", font=dict(size=12, color="#5b6570"))]
    )
    fig.write_html(out, include_plotlyjs=True, full_html=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flussi", required=True, type=Path)
    ap.add_argument("--frequentazione", required=True, type=Path)
    ap.add_argument("--outdir", default="outputs/scatter_lombardia", type=Path)
    ap.add_argument("--threshold", default=700, type=int)
    args = ap.parse_args()
    outdir = ensure_outdir(args.outdir)
    master = load_station_data(args.flussi, args.frequentazione)
    ds = make_dataset(master, threshold=args.threshold)
    ds.to_csv(outdir / "scatter_stazioni_lombarde_2019_2025.csv", index=False)
    ds.to_csv(outdir / "scatter_lombardia_crescita_carico_base700.csv", index=False)
    make_png(ds, outdir / "scatter_lombardia_crescita_carico_base700.png")
    make_html(ds, outdir / "scatter_lombardia_crescita_carico_base700.html")

if __name__ == "__main__":
    main()

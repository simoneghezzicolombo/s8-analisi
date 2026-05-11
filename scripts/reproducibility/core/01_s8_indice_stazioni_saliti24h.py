#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S8 – Indice passeggeri per stazione, Saliti24H, 2015-2025.

Output:
- CSV tidy con Saliti24H e indice 2019=100
- PNG statico
- HTML interattivo Plotly
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

from common import (
    S8_STATIONS_ORDER, MERATESI, MERATESE_COLORS,
    ensure_outdir, load_station_data, s8_novembre_feriale,
)

BG = "#f5f5f3"
OTHER = "#c7ccd3"
OTHER_TEXT = "#9098a3"
SITE_STATION_CODES = {
    "Milano Porta Garibaldi": "MILANO PORTA GARIBALDI",
    "Milano Greco Pirelli": "MILANO GRECO PIRELLI",
    "Sesto S. Giovanni": "SESTO S.GIOVANNI",
    "Monza": "MONZA",
    "Arcore": "ARCORE",
    "Carnate Usmate": "CARNATE USMATE",
    "Osnago": "OSNAGO",
    "Cernusco-Merate": "CERNUSCO-MERATE",
    "Olgiate-Calco-Brivio": "OLGIATE-CALCO-BRIVIO",
    "Airuno": "AIRUNO",
    "Calolziocorte-Olginate": "CALOLZIOCORTE-OLGINATE",
    "Vercurago-S. Girolamo": "VERCURAGO-S.GIROLAMO",
    "Lecco": "LECCO",
}


def make_dataset(master: pd.DataFrame, include_maggianico=False, include_vercurago=False, include_sesto=False) -> pd.DataFrame:
    d = s8_novembre_feriale(master)
    exclude = []
    if not include_maggianico:
        exclude.append("Lecco Maggianico")
    if not include_vercurago:
        exclude.append("Vercurago-S. Girolamo")
    if not include_sesto:
        exclude.append("Sesto S. Giovanni")
    d = d[~d["Stazione_std"].isin(exclude)].copy()
    base = d[d["Anno"] == 2019][["Stazione_std", "Saliti24H"]].rename(columns={"Saliti24H": "Base2019"})
    d = d.merge(base, on="Stazione_std", how="left")
    d["Indice_2019_100"] = d["Saliti24H"] / d["Base2019"] * 100
    return d.sort_values(["Stazione_std", "Anno"])


def make_png(df: pd.DataFrame, out: Path):
    fig, ax = plt.subplots(figsize=(13, 8.6), dpi=200)
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    order = [s for s in S8_STATIONS_ORDER if s in set(df["Stazione_std"])]
    for st in order:
        sub = df[df["Stazione_std"] == st].sort_values("Anno")
        if sub.empty: continue
        c = MERATESE_COLORS.get(st, OTHER)
        ax.plot(sub["Anno"], sub["Indice_2019_100"], marker="o",
                linewidth=3 if st in MERATESI else 1.8,
                markersize=5.5 if st in MERATESI else 3.8,
                color=c, zorder=3 if st in MERATESI else 2)
    last = df[df["Anno"] == 2025][["Stazione_std", "Indice_2019_100"]].dropna().sort_values("Indice_2019_100")
    gap = max((last["Indice_2019_100"].max() - last["Indice_2019_100"].min()) * 0.03, 2.0) if len(last) else 2
    ys, prev = [], -1e9
    for y in last["Indice_2019_100"]:
        yy = max(y, prev + gap)
        ys.append(yy); prev = yy
    last["label_y"] = ys
    for _, r in last.iterrows():
        st = r["Stazione_std"]
        c = MERATESE_COLORS.get(st, OTHER)
        ax.text(2025.35, r["label_y"], st, va="center", ha="left",
                fontsize=10.2 if st in MERATESI else 9.4,
                color=c if st in MERATESI else OTHER_TEXT,
                bbox=dict(boxstyle="round,pad=0.16", facecolor="white", edgecolor=c if st in MERATESI else "#bcc2ca", linewidth=0.7))
        ax.plot([2025.02, 2025.28], [r["Indice_2019_100"], r["label_y"]], color=c if st in MERATESI else "#bcc2ca", linewidth=0.7)
    ax.axhline(100, linestyle="--", linewidth=1.1, color="#6f6f6f")
    ax.set_xlim(2015, 2027.0); ax.set_xticks(range(2015, 2026))
    ax.set_ylabel("Indice passeggeri per stazione (2019=100)")
    ax.grid(True, axis="y", alpha=0.25); ax.grid(True, axis="x", alpha=0.10)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, colors="#4b5563")
    fig.text(0.06, 0.94, "La crescita delle stazioni meratesi", fontsize=18, fontweight="bold", color="#424242")
    fig.text(0.06, 0.905, "Indice passeggeri per stazione — Saliti24H, novembre feriale — Base 2019=100", fontsize=12, color="#5b6570")
    fig.text(0.77, 0.94, "Analisi di Simone Ghezzi Colombo", fontsize=10.2, color="#555555")
    fig.text(0.06, 0.032, "Fonti: Regione Lombardia, Flussi Stazioni Ferroviarie; Frequentazione delle stazioni del servizio ferroviario regionale.", fontsize=8.7, color="#5b6570")
    fig.text(0.06, 0.015, "Stazioni meratesi evidenziate. Default: Lecco Maggianico e Vercurago-S. Girolamo escluse.", fontsize=8.7, color="#5b6570")
    fig.tight_layout(rect=[0.04, 0.06, 0.98, 0.88])
    fig.savefig(out, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def make_html(df: pd.DataFrame, out: Path):
    if go is None:
        print("Plotly non installato: HTML interattivo non generato.")
        return

    fig = go.Figure()
    order = [s for s in S8_STATIONS_ORDER if s in set(df["Stazione_std"])]
    for st in order:
        sub = df[df["Stazione_std"] == st].sort_values("Anno")
        color = MERATESE_COLORS.get(st, "rgba(160,167,176,0.55)")
        fig.add_trace(go.Scatter(
            x=sub["Anno"], y=sub["Indice_2019_100"], mode="lines+markers+text" if st in MERATESI else "lines+markers",
            name=st, line=dict(color=color, width=3 if st in MERATESI else 1.6),
            marker=dict(size=7 if st in MERATESI else 5),
            text=[st if (st in MERATESI and a == 2025) else "" for a in sub["Anno"]], textposition="middle right",
            hovertemplate="<b>%{fullData.name}</b><br>Anno: %{x}<br>Indice: %{y:.1f}<extra></extra>"
        ))
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(80,80,80,0.7)")
    fig.update_layout(
        title="S8 – Indice passeggeri per stazione<br><sup>Saliti24H, novembre feriale, 2015–2025 — base 2019=100</sup>",
        template="plotly_white", paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis_title="Anno", yaxis_title="Indice 2019=100",
        legend_title="Stazione", margin=dict(l=70, r=40, t=90, b=80),
        annotations=[dict(x=0.01, y=-0.18, xref="paper", yref="paper", showarrow=False, align="left",
                          text="Fonti: Regione Lombardia. Stazioni meratesi evidenziate; default: Lecco Maggianico e Vercurago-S. Girolamo escluse.", font=dict(size=12, color="#5b6570"))]
    )
    fig.write_html(out, include_plotlyjs=True, full_html=True)


def site_dataset(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({
        "Anno": df["Anno"].astype(int),
        "Stazione_std": df["Stazione_std"].map(SITE_STATION_CODES),
        "Stazione": df["Stazione_std"],
        "Saliti24H": df["Saliti24H"],
        "Indice_2019_100": df["Indice_2019_100"],
        "Fonte_periodo": np.where(
            df["Anno"].astype(int) <= 2023,
            "Flussi Stazioni Ferroviarie (2015-2023)",
            "Frequentazione stazioni SFR (2024-2025)",
        ),
    })
    return out.sort_values(["Stazione_std", "Anno"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flussi", required=True, type=Path)
    ap.add_argument("--frequentazione", required=True, type=Path)
    ap.add_argument("--outdir", default="outputs/s8_indice_stazioni", type=Path)
    ap.add_argument("--include-maggianico", action="store_true")
    ap.add_argument("--include-vercurago", action="store_true")
    ap.add_argument("--include-sesto", action="store_true")
    args = ap.parse_args()
    outdir = ensure_outdir(args.outdir)
    master = load_station_data(args.flussi, args.frequentazione)
    ds = make_dataset(master, args.include_maggianico, include_vercurago=args.include_vercurago, include_sesto=args.include_sesto)
    site = site_dataset(ds)
    site.to_csv(outdir / "stazioni_s8_indice_2015_2025.csv", index=False)
    site.to_csv(outdir / "s8_indice_stazioni_saliti24h_2015_2025.csv", index=False)
    make_png(ds, outdir / "s8_indice_stazioni_saliti24h_2015_2025.png")
    make_html(ds, outdir / "s8_indice_stazioni_saliti24h_2015_2025.html")

if __name__ == "__main__":
    main()

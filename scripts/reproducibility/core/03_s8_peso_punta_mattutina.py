#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Peso della punta mattutina nelle stazioni S8.

Metrica: Saliti7-9 / Saliti24H × 100, novembre feriale, 2015-2025.
"""
from __future__ import annotations

import argparse
from pathlib import Path
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


def make_dataset(master: pd.DataFrame, include_maggianico=False, include_vercurago=False, include_sesto=True) -> pd.DataFrame:
    d = s8_novembre_feriale(master)
    exclude = []
    if not include_maggianico: exclude.append("Lecco Maggianico")
    if not include_vercurago: exclude.append("Vercurago-S. Girolamo")
    if not include_sesto: exclude.append("Sesto S. Giovanni")
    d = d[~d["Stazione_std"].isin(exclude)].copy()
    d["Peso_punta_pct"] = d["Saliti7-9"] / d["Saliti24H"] * 100
    return d.sort_values(["Stazione_std", "Anno"])


def make_png(df: pd.DataFrame, out: Path):
    fig, ax = plt.subplots(figsize=(13, 8.6), dpi=200)
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    order = [s for s in S8_STATIONS_ORDER if s in set(df["Stazione_std"])]
    for st in order:
        sub = df[df["Stazione_std"] == st].sort_values("Anno")
        c = MERATESE_COLORS.get(st, OTHER)
        ax.plot(sub["Anno"], sub["Peso_punta_pct"], marker="o",
                linewidth=3 if st in MERATESI else 1.8,
                markersize=5.5 if st in MERATESI else 3.8,
                color=c, zorder=3 if st in MERATESI else 2)
    last = df[df["Anno"] == 2025][["Stazione_std", "Peso_punta_pct"]].dropna().sort_values("Peso_punta_pct")
    gap = max((last["Peso_punta_pct"].max() - last["Peso_punta_pct"].min()) * 0.04, 0.8) if len(last) else 1
    ys, prev = [], -1e9
    for y in last["Peso_punta_pct"]:
        yy = max(y, prev + gap)
        ys.append(yy); prev = yy
    last["label_y"] = ys
    for _, r in last.iterrows():
        st = r["Stazione_std"]
        c = MERATESE_COLORS.get(st, OTHER)
        ax.text(2025.35, r["label_y"], st, va="center", ha="left", fontsize=10.2 if st in MERATESI else 9.4,
                color=c if st in MERATESI else OTHER_TEXT,
                bbox=dict(boxstyle="round,pad=0.16", facecolor="white", edgecolor=c if st in MERATESI else "#bcc2ca", linewidth=0.7))
        ax.plot([2025.02, 2025.28], [r["Peso_punta_pct"], r["label_y"]], color=c if st in MERATESI else "#bcc2ca", linewidth=0.7)
    ax.set_xlim(2015, 2027.0); ax.set_xticks(range(2015, 2026))
    ax.set_ylabel("Saliti 7–9 / Saliti24H (%)")
    ax.grid(True, axis="y", alpha=0.25); ax.grid(True, axis="x", alpha=0.10)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0, colors="#4b5563")
    fig.text(0.06, 0.94, "Peso della punta mattutina nelle stazioni S8", fontsize=18, fontweight="bold", color="#424242")
    fig.text(0.06, 0.905, "Saliti 7–9 / Saliti24H × 100 — novembre feriale — 2015–2025", fontsize=12, color="#5b6570")
    fig.text(0.77, 0.94, "Analisi di Simone Ghezzi Colombo", fontsize=10.2, color="#555555")
    fig.text(0.06, 0.032, "Fonti: Regione Lombardia, Flussi Stazioni Ferroviarie; Frequentazione delle stazioni del servizio ferroviario regionale.", fontsize=8.7, color="#5b6570")
    fig.text(0.06, 0.015, "Stazioni meratesi evidenziate. Default: Lecco Maggianico e Vercurago-S. Girolamo escluse; Sesto S. Giovanni inclusa.", fontsize=8.7, color="#5b6570")
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
            x=sub["Anno"], y=sub["Peso_punta_pct"], mode="lines+markers+text" if st in MERATESI else "lines+markers",
            name=st, line=dict(color=color, width=3 if st in MERATESI else 1.6),
            marker=dict(size=7 if st in MERATESI else 5),
            text=[st if (st in MERATESI and a == 2025) else "" for a in sub["Anno"]], textposition="middle right",
            hovertemplate="<b>%{fullData.name}</b><br>Anno: %{x}<br>Peso punta: %{y:.1f}%<extra></extra>"
        ))
    fig.update_layout(
        title="Peso della punta mattutina nelle stazioni S8<br><sup>Saliti 7–9 / Saliti24H × 100, novembre feriale, 2015–2025</sup>",
        template="plotly_white", paper_bgcolor=BG, plot_bgcolor=BG,
        xaxis_title="Anno", yaxis_title="Peso punta 7–9 (%)", legend_title="Stazione",
        margin=dict(l=70, r=40, t=90, b=80),
        annotations=[dict(x=0.01, y=-0.18, xref="paper", yref="paper", showarrow=False, align="left",
                          text="Fonti: Regione Lombardia. Stazioni meratesi evidenziate; default: Lecco Maggianico e Vercurago-S. Girolamo escluse; Sesto S. Giovanni inclusa.", font=dict(size=12, color="#5b6570"))]
    )
    fig.write_html(out, include_plotlyjs=True, full_html=True)


def site_peso_dataset(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({
        "Anno": df["Anno"].astype(int),
        "Stazione": df["Stazione_std"],
        "Saliti7-9": df["Saliti7-9"],
        "Saliti24H": df["Saliti24H"],
        "Peso_punta_pct": df["Peso_punta_pct"],
    })
    return out.sort_values(["Stazione", "Anno"])


def site_meratese_series(df: pd.DataFrame) -> pd.DataFrame:
    sub = df[df["Stazione_std"].isin(MERATESI)].copy()
    out = pd.DataFrame({
        "Anno": sub["Anno"].astype(int),
        "Stazione": sub["Stazione_std"],
        "Saliti7-9": sub["Saliti7-9"],
        "Saliti24H": sub["Saliti24H"],
        "Quota_7_9_pct": sub["Peso_punta_pct"],
    })
    return out.sort_values(["Anno", "Stazione"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flussi", required=True, type=Path)
    ap.add_argument("--frequentazione", required=True, type=Path)
    ap.add_argument("--outdir", default="outputs/s8_peso_punta", type=Path)
    ap.add_argument("--include-maggianico", action="store_true")
    ap.add_argument("--include-vercurago", action="store_true")
    ap.add_argument("--exclude-sesto", action="store_true")
    args = ap.parse_args()
    outdir = ensure_outdir(args.outdir)
    master = load_station_data(args.flussi, args.frequentazione)
    ds = make_dataset(master, args.include_maggianico, include_vercurago=args.include_vercurago, include_sesto=not args.exclude_sesto)
    site_peso_dataset(ds).to_csv(outdir / "peso_punta_stazioni_s8_2015_2025.csv", index=False)
    site_meratese_series(ds).to_csv(outdir / "crescita_meratese_punta_morbida_2015_2025.csv", index=False)
    site_peso_dataset(ds).to_csv(outdir / "s8_peso_punta_mattutina_2015_2025.csv", index=False)
    make_png(ds, outdir / "s8_peso_punta_mattutina_2015_2025.png")
    make_html(ds, outdir / "s8_peso_punta_mattutina_2015_2025.html")

if __name__ == "__main__":
    main()

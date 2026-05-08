#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Riproduce lo scatterplot:
"Chi cresce molto e intensifica anche il carico per corsa?"

Uso:
python scripts/reproducibility/scatter/make_scatter_intensificazione_carico.py \
  --flussi data/raw/regione_lombardia_flussi_stazioni_2015_2023_20260424.csv \
  --frequentazione data/raw/regione_lombardia_frequentazione_stazioni_sfr_20260424.csv \
  --outdir outputs/scatter \
  --threshold 700
"""
import argparse
import re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
try:
    import plotly.graph_objects as go
except ImportError:
    go = None

def norm_station(s):
    s = str(s).upper().strip()
    for a, b in {"À":"A","È":"E","É":"E","Ì":"I","Ò":"O","Ù":"U"}.items():
        s = s.replace(a, b)
    return re.sub(r"[^A-Z0-9]", "", s)

def month_from_campaign(x):
    s = str(x).lower()
    if "nov" in s: return "Novembre"
    if "lug" in s: return "Luglio"
    if "mag" in s: return "Maggio"
    return None

def day_type(x):
    s = str(x).lower()
    if "fer" in s: return "Feriale"
    if "sab" in s: return "Sabato"
    if "fes" in s: return "Festivo"
    return None

def canonical_label(station_key, display_name):
    sk = str(station_key)
    st = str(display_name).upper()
    if "OSNAGO" in sk or st == "OSNAGO": return "Osnago"
    if "CERNUSCO" in sk or "CERNUSCO" in st: return "Cernusco-Merate"
    if "OLGIATE" in sk or "OLGIATE" in st: return "Olgiate-Calco-Brivio"
    if "AIRUNO" in sk or st == "AIRUNO": return "Airuno"
    return str(display_name)

def load_master(flussi_path, frequentazione_path):
    fl = pd.read_csv(flussi_path, thousands=".", low_memory=False)
    fr = pd.read_csv(frequentazione_path, thousands=".", low_memory=False)

    num_cols = ["Saliti24H","Saliti7-9","Discesi7-9","Corse24H","Corse7-9",
                "Saliti_S","Saliti_R","Saliti_RE","Corse_S","Corse_R","Corse_RE"]
    for df in (fl, fr):
        for c in num_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

    fl2 = fl.copy()
    fl2["StationKey"] = fl2["Stazione"].map(norm_station)
    fl2["Mese"] = fl2["Campagna"].map(month_from_campaign)
    fl2["TipoGiorno"] = fl2["tipo_giorno"].map(day_type)
    fl2["DisplayName"] = fl2["Stazione"]

    fr2 = fr.copy()
    fr2["StationKey"] = fr2["Stazione"].map(norm_station)
    fr2["Mese"] = fr2["Campagna"].map(month_from_campaign)
    fr2["TipoGiorno"] = fr2["Tipo giorno"].map(day_type)
    fr2["DisplayName"] = fr2["Stazione"]

    common_cols = ["Anno","StationKey","DisplayName","Mese","TipoGiorno"] + [
        c for c in num_cols if c in fl2.columns and c in fr2.columns
    ]
    return pd.concat([fl2[common_cols], fr2[common_cols]], ignore_index=True)

def build_dataset(master, threshold=700):
    sub = master[
        (master["Mese"] == "Novembre")
        & (master["TipoGiorno"] == "Feriale")
        & (master["Anno"].isin([2019, 2025]))
    ].copy()

    display_map = master.sort_values("Anno").groupby("StationKey")["DisplayName"].last().to_dict()

    agg = sub.groupby(["Anno","StationKey"], as_index=False)[["Saliti24H","Saliti7-9","Corse24H"]].mean()
    agg["Saliti_per_corsa"] = agg["Saliti24H"] / agg["Corse24H"]

    pv = agg.pivot(index="StationKey", columns="Anno", values=["Saliti24H","Saliti7-9","Corse24H","Saliti_per_corsa"])
    pv.columns = [f"{a}_{b}" for a, b in pv.columns]
    pv = pv.reset_index()

    pv["Stazione"] = pv["StationKey"].map(display_map)
    pv["Label"] = pv.apply(lambda r: canonical_label(r["StationKey"], r["Stazione"]), axis=1)
    pv["IsMeratese"] = pv["Label"].isin(["Osnago","Cernusco-Merate","Olgiate-Calco-Brivio","Airuno"])

    pv["Growth_pct_Saliti24H"] = (pv["Saliti24H_2025"] / pv["Saliti24H_2019"] - 1) * 100
    pv["Growth_pct_Corse24H"] = (pv["Corse24H_2025"] / pv["Corse24H_2019"] - 1) * 100
    pv["Delta_abs_Saliti24H"] = pv["Saliti24H_2025"] - pv["Saliti24H_2019"]
    pv["Growth_pct_Saliti_per_corsa"] = (pv["Saliti_per_corsa_2025"] / pv["Saliti_per_corsa_2019"] - 1) * 100
    pv["Delta_abs_Saliti_per_corsa"] = pv["Saliti_per_corsa_2025"] - pv["Saliti_per_corsa_2019"]

    usable = pv[
        pv["Saliti24H_2019"].notna()
        & pv["Saliti24H_2025"].notna()
        & pv["Corse24H_2019"].notna()
        & pv["Corse24H_2025"].notna()
        & (pv["Saliti24H_2019"] > 0)
        & (pv["Corse24H_2019"] > 0)
        & (pv["Corse24H_2025"] > 0)
    ].copy()

    return usable[usable["Saliti24H_2019"] >= threshold].copy()

def make_png(df, out_path):
    mer_colors = {"Osnago":"#c239c8","Cernusco-Merate":"#23b9c9",
                  "Olgiate-Calco-Brivio":"#f06bb6","Airuno":"#a8bf39"}
    bg = "#f5f5f3"
    others = df[~df["IsMeratese"]].copy()

    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
    fig.patch.set_facecolor(bg); ax.set_facecolor(bg)

    ax.scatter(
        others["Growth_pct_Saliti24H"],
        others["Growth_pct_Saliti_per_corsa"],
        s=np.clip(others["Delta_abs_Saliti24H"].abs().fillna(0) / 12, 12, 160),
        alpha=0.32, color="#9aa1aa", edgecolors="none"
    )

    for label, color in mer_colors.items():
        d = df[df["Label"] == label]
        if d.empty: continue
        ax.scatter(
            d["Growth_pct_Saliti24H"], d["Growth_pct_Saliti_per_corsa"],
            s=np.clip(d["Delta_abs_Saliti24H"].abs().fillna(0) / 5, 110, 320),
            color=color, edgecolors="white", linewidths=1.1, zorder=5
        )
        for _, r in d.iterrows():
            ax.text(r["Growth_pct_Saliti24H"] + 0.8, r["Growth_pct_Saliti_per_corsa"] + 0.9,
                    label, fontsize=10.2, color=color,
                    bbox=dict(boxstyle="round,pad=0.14", facecolor="white", edgecolor=color, linewidth=0.8),
                    zorder=6)

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
    fig.savefig(out_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

def make_html(df, out_path):
    if go is None:
        print("Plotly non installato: HTML interattivo non generato.")
        return

    mer_colors = {"Osnago":"#c239c8","Cernusco-Merate":"#23b9c9",
                  "Olgiate-Calco-Brivio":"#f06bb6","Airuno":"#a8bf39"}
    others = df[~df["IsMeratese"]].copy()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=others["Growth_pct_Saliti24H"],
        y=others["Growth_pct_Saliti_per_corsa"],
        mode="markers",
        name="Altre stazioni lombarde",
        marker=dict(size=np.clip(others["Delta_abs_Saliti24H"].abs().fillna(0) / 25, 7, 28),
                    color="rgba(165, 172, 180, 0.35)",
                    line=dict(color="rgba(125, 132, 142, 0.25)", width=0.5)),
        customdata=np.stack([others["Stazione"].astype(str),
                             others["Saliti24H_2019"].round(0),
                             others["Saliti24H_2025"].round(0),
                             others["Growth_pct_Saliti24H"].round(2),
                             others["Growth_pct_Corse24H"].round(2),
                             others["Growth_pct_Saliti_per_corsa"].round(2),
                             others["Delta_abs_Saliti24H"].round(0)], axis=-1),
        hovertemplate=("<b>%{customdata[0]}</b><br>"
                       "Saliti24H 2019→2025: %{customdata[1]:,.0f} → %{customdata[2]:,.0f}<br>"
                       "Crescita passeggeri: %{customdata[3]:+.2f}%<br>"
                       "Crescita corse: %{customdata[4]:+.2f}%<br>"
                       "Cambiamento passeggeri/corsa: %{customdata[5]:+.2f}%<br>"
                       "Δ passeggeri: %{customdata[6]:+,.0f}<extra></extra>")
    ))
    for label, color in mer_colors.items():
        d = df[df["Label"] == label]
        if d.empty: continue
        fig.add_trace(go.Scatter(
            x=d["Growth_pct_Saliti24H"], y=d["Growth_pct_Saliti_per_corsa"],
            mode="markers+text", name=label, text=d["Label"], textposition="top right",
            marker=dict(size=np.clip(d["Delta_abs_Saliti24H"].abs().fillna(0) / 10, 14, 34),
                        color=color, line=dict(color="white", width=1.2))
        ))
    fig.update_layout(
        title=dict(text="Chi cresce molto e intensifica anche il carico per corsa?<br><sup>Stazioni lombarde comparabili — novembre feriale — 2019 vs 2025</sup>",
                   x=0.02, xanchor="left", font=dict(size=22)),
        template="plotly_white", paper_bgcolor="#f5f5f3", plot_bgcolor="#f5f5f3",
        font=dict(color="#344055", size=14),
        xaxis=dict(title="Crescita % dei passeggeri 2019→2025", gridcolor="rgba(110,120,130,0.16)", zeroline=False),
        yaxis=dict(title="Cambiamento % dei passeggeri per corsa 2019→2025", gridcolor="rgba(110,120,130,0.16)", zeroline=False)
    )
    fig.write_html(str(out_path), include_plotlyjs=True, full_html=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--flussi", required=True, type=Path)
    parser.add_argument("--frequentazione", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--threshold", default=700, type=int)
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    master = load_master(args.flussi, args.frequentazione)
    dataset = build_dataset(master, threshold=args.threshold)
    dataset.to_csv(args.outdir / "scatter_intensificazione_carico_base700.csv", index=False)
    make_png(dataset, args.outdir / "scatter_intensificazione_carico_base700.png")
    make_html(dataset, args.outdir / "scatter_intensificazione_carico_base700_interattivo.html")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02_variazione_linee_suburbane_2024_2025.py

Calcola la variazione assoluta 2025 vs 2024 per le linee suburbane:
- Tipo giorno = Feriale
- linee S
- escluse S10, S30, S31, S40, S50
- S1 e S12 aggregate come "S1/S12"
- confronto corretto: per ogni linea si confrontano solo le campagne presenti in entrambi gli anni
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

RAW = Path("data/raw")
OUT = Path("data/processed")
FIG = Path("figures")
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

def first_existing(paths):
    for path in paths:
        if path.exists():
            return path
    raise FileNotFoundError(paths[0])

LINEE = first_existing([
    RAW / "regione_lombardia_frequentazione_linee_sfr_20260424.csv",
    RAW / "Dati_di_frequentazione_delle_linee_del_servizio_ferroviario_regionale_20260424.csv",
])

df = pd.read_csv(LINEE, dtype=str)
for col in ["Viaggiatori", "N. corse", "viagg*km", "treni*km", "posti*km", "Posti"]:
    df[col] = df[col].str.replace(".", "", regex=False).astype(float)

df = df[(df["Tipo giorno"] == "Feriale") & (df["N. linea"].str.startswith("S"))].copy()
df = df[~df["N. linea"].isin({"S10", "S30", "S31", "S40", "S50"})].copy()
df["Anno"] = df["Campagna"].str.extract(r"c(\d{4})").astype(int)
df["Mese"] = df["Campagna"].str.extract(r"c\d{4}([A-Za-z]+)")[0]
df["Linea"] = df["N. linea"].replace({"S1": "S1/S12", "S12": "S1/S12"})

monthly = df.groupby(["Linea", "Anno", "Mese"], as_index=False)[["Viaggiatori", "N. corse"]].sum()

rows = []
availability = []
month_order = {"Maggio": 1, "Luglio": 2, "Novembre": 3}

for line, g in monthly.groupby("Linea"):
    months_2024 = set(g.loc[g["Anno"] == 2024, "Mese"])
    months_2025 = set(g.loc[g["Anno"] == 2025, "Mese"])
    matched = sorted(months_2024 & months_2025, key=lambda m: month_order.get(m, 99))
    availability.append({
        "Linea": line,
        "Campagne_2024": ", ".join(sorted(months_2024)),
        "Campagne_2025": ", ".join(sorted(months_2025)),
        "Campagne_confrontate": ", ".join(matched),
        "N_campagne_confrontate": len(matched),
    })
    if not matched:
        continue
    sub = g[g["Mese"].isin(matched)]
    v2024 = sub.loc[sub["Anno"] == 2024, "Viaggiatori"].sum()
    v2025 = sub.loc[sub["Anno"] == 2025, "Viaggiatori"].sum()
    c2024 = sub.loc[sub["Anno"] == 2024, "N. corse"].sum()
    c2025 = sub.loc[sub["Anno"] == 2025, "N. corse"].sum()
    rows.append({
        "Linea": line,
        "Viaggiatori_2024_matched": v2024,
        "Viaggiatori_2025_matched": v2025,
        "Delta_2025_vs_2024_matched": v2025 - v2024,
        "Corse_2024_matched": c2024,
        "Corse_2025_matched": c2025,
        "Delta_corse_matched": c2025 - c2024,
        "Campagne_confrontate": ", ".join(matched),
        "N_campagne_confrontate": len(matched),
    })

corrected = pd.DataFrame(rows).sort_values("Delta_2025_vs_2024_matched", ascending=True)
availability = pd.DataFrame(availability)

corrected.to_csv(OUT / "variazione_linee_suburbane_2024_2025_dettaglio.csv", index=False)
summary = corrected.rename(columns={
    "Linea": "N. linea",
    "Viaggiatori_2024_matched": "2024",
    "Viaggiatori_2025_matched": "2025",
    "Delta_2025_vs_2024_matched": "Delta",
}).copy()
summary["Delta_pct"] = 100 * summary["Delta"] / summary["2024"]
summary[["N. linea", "2024", "2025", "Delta", "Delta_pct"]].to_csv(
    OUT / "variazione_linee_suburbane_2024_2025.csv",
    index=False,
)
availability.to_csv(OUT / "disponibilita_campagne_linee_suburbane_2024_2025.csv", index=False)

colors = {
    "S1": "#ee162a", "S2": "#00aa87", "S3": "#aa0130", "S4": "#7ec340",
    "S5": "#f79336", "S6": "#f3d018", "S7": "#ee007d", "S8": "#f8b1b0",
    "S9": "#9e3a98", "S11": "#9b8ec4", "S12": "#004728", "S13": "#89580c",
}

fig, ax = plt.subplots(figsize=(12.5, 8.5))
labels = corrected["Linea"].tolist()
bar_h = 0.8

for y, line in enumerate(labels):
    val = corrected.loc[corrected["Linea"] == line, "Delta_2025_vs_2024_matched"].iloc[0]
    if line == "S1/S12":
        yb = y - bar_h / 2
        ax.add_patch(Rectangle((0, yb), val, bar_h/2, facecolor=colors["S12"], edgecolor="white", linewidth=0.8))
        ax.add_patch(Rectangle((0, yb + bar_h/2), val, bar_h/2, facecolor=colors["S1"], edgecolor="white", linewidth=0.8))
        ax.annotate(f"{int(val):+d}", xy=(val, y), xytext=(8 if val>=0 else -8, 0), textcoords="offset points", va="center", ha="left" if val>=0 else "right", fontsize=10, fontweight="bold")
        ax.annotate("* da 70 a 130 corse/giorno con S12", xy=(max(val*0.45, 4000), y), xytext=(0,16), textcoords="offset points", va="bottom", ha="left", fontsize=9.2, bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="0.8", alpha=0.97))
    else:
        ax.barh(y, val, height=bar_h, color=colors.get(line, "#999999"), edgecolor="white", linewidth=0.8)
        ax.annotate(f"{int(val):+d}", xy=(val, y), xytext=(8 if val>=0 else -8, 0), textcoords="offset points", va="center", ha="left" if val>=0 else "right", fontsize=10)

ax.axvline(0, color="black", linewidth=1)
ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels)
ax.set_title("Variazione assoluta 2025 vs 2024 per linee suburbane (feriale)", fontsize=14, pad=14)
ax.set_xlabel("Δ passeggeri/giorno (2025 − 2024)")
ax.set_ylabel("Linea")
ax.grid(True, axis="x", alpha=0.25)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.text(0.01, 0.01, "Escluse: S10, S30, S31, S40, S50. Metodo: per ogni linea si confrontano solo le campagne disponibili sia nel 2024 sia nel 2025.", fontsize=9)
plt.tight_layout(rect=[0, 0.05, 1, 1])
fig.savefig(FIG / "grafico_barre_delta_assoluto_linee_suburbane_2024_2025_corretto.png", dpi=220, bbox_inches="tight")

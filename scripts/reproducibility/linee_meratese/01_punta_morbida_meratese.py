#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_punta_morbida_meratese.py

Calcola la scomposizione della crescita 2019->2025 delle stazioni meratesi:
- "di punta": variazione dei saliti 7-9
- "di morbida": variazione dei saliti fuori 7-9 = Saliti24H - Saliti7-9

Input attesi nel repo pubblico:
  data/raw/regione_lombardia_flussi_stazioni_2015_2023_20260424.csv
  data/raw/regione_lombardia_frequentazione_stazioni_sfr_20260424.csv
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

FLUSSI = first_existing([
    RAW / "regione_lombardia_flussi_stazioni_2015_2023_20260424.csv",
    RAW / "Flussi_Stazioni_Ferroviarie_20260424.csv",
])
FREQ = first_existing([
    RAW / "regione_lombardia_frequentazione_stazioni_sfr_20260424.csv",
    RAW / "Frequentazione_delle_stazioni_del_servizio_ferroviario_regionale_20260424.csv",
])

def to_num(s):
    return pd.to_numeric(
        s.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce"
    )

def norm_station(s):
    return (
        s.astype(str).str.upper().str.strip()
        .replace({
            "OLGIATE-CALCO-BRIVIO": "OLGIATE CALCO-BRIVIO",
            "CERNUSCO MERATE": "CERNUSCO-MERATE",
        })
    )

stations = ["AIRUNO", "OSNAGO", "CERNUSCO-MERATE", "OLGIATE CALCO-BRIVIO"]
labels = {
    "AIRUNO": "Airuno",
    "OSNAGO": "Osnago",
    "CERNUSCO-MERATE": "Cernusco-Merate",
    "OLGIATE CALCO-BRIVIO": "Olgiate-Calco-Brivio",
}

flussi = pd.read_csv(FLUSSI, dtype=str)
freq = pd.read_csv(FREQ, dtype=str)

for df in [flussi, freq]:
    for c in ["Saliti24H", "Saliti7-9", "Anno"]:
        df[c] = to_num(df[c])

flussi["Stazione_norm"] = norm_station(flussi["Stazione"])
freq["Stazione_norm"] = norm_station(freq["Stazione"])
flussi["Campagna_lower"] = flussi["Campagna"].astype(str).str.lower()
freq["Campagna_lower"] = freq["Campagna"].astype(str).str.lower()

base2019 = (
    flussi[
        (flussi["Anno"] == 2019)
        & flussi["Campagna_lower"].str.contains("nov", na=False)
        & flussi["tipo_giorno"].astype(str).str.upper().str.startswith("FER", na=False)
        & flussi["Stazione_norm"].isin(stations)
    ]
    .groupby("Stazione_norm", as_index=False)[["Saliti24H", "Saliti7-9"]]
    .mean()
    .rename(columns={"Saliti24H": "Saliti24H_2019", "Saliti7-9": "Saliti7_9_2019"})
)

val2025 = (
    freq[
        (freq["Anno"] == 2025)
        & freq["Campagna_lower"].str.contains("nov", na=False)
        & (freq["Tipo giorno"].astype(str).str.upper() == "FERIALE")
        & freq["Stazione_norm"].isin(stations)
    ]
    .groupby("Stazione_norm", as_index=False)[["Saliti24H", "Saliti7-9"]]
    .mean()
    .rename(columns={"Saliti24H": "Saliti24H_2025", "Saliti7-9": "Saliti7_9_2025"})
)

df = base2019.merge(val2025, on="Stazione_norm", how="inner")
df["Fuori_7_9_2019"] = df["Saliti24H_2019"] - df["Saliti7_9_2019"]
df["Fuori_7_9_2025"] = df["Saliti24H_2025"] - df["Saliti7_9_2025"]
df["Delta_totale"] = df["Saliti24H_2025"] - df["Saliti24H_2019"]
df["Delta_punta_7_9"] = df["Saliti7_9_2025"] - df["Saliti7_9_2019"]
df["Delta_morbida_fuori_7_9"] = df["Fuori_7_9_2025"] - df["Fuori_7_9_2019"]
df["Quota_punta_pct"] = 100 * df["Delta_punta_7_9"] / df["Delta_totale"]
df["Quota_morbida_pct"] = 100 * df["Delta_morbida_fuori_7_9"] / df["Delta_totale"]
df["Stazione"] = df["Stazione_norm"].map(labels)

total = pd.DataFrame([{
    "Stazione": "Meratese (totale)",
    "Saliti24H_2019": df["Saliti24H_2019"].sum(),
    "Saliti24H_2025": df["Saliti24H_2025"].sum(),
    "Delta_totale": df["Delta_totale"].sum(),
    "Delta_punta_7_9": df["Delta_punta_7_9"].sum(),
    "Delta_morbida_fuori_7_9": df["Delta_morbida_fuori_7_9"].sum(),
}])
total["Quota_punta_pct"] = 100 * total["Delta_punta_7_9"] / total["Delta_totale"]
total["Quota_morbida_pct"] = 100 * total["Delta_morbida_fuori_7_9"] / total["Delta_totale"]

out = pd.concat([total, df], ignore_index=True)
out.to_csv(OUT / "punta_morbida_meratese_2019_2025.csv", index=False)

# chart
order = ["Meratese (totale)", "Airuno", "Osnago", "Cernusco-Merate", "Olgiate-Calco-Brivio"]
plot_df = out.copy()
plot_df["Stazione"] = pd.Categorical(plot_df["Stazione"], categories=order, ordered=True)
plot_df = plot_df.sort_values("Stazione", ascending=False)

fig, ax = plt.subplots(figsize=(12.5, 8))
y = np.arange(len(plot_df))
ax.barh(y, plot_df["Delta_punta_7_9"], color="#2f5aa8", edgecolor="white", linewidth=0.8, label="Di punta (7–9)")
ax.barh(y, plot_df["Delta_morbida_fuori_7_9"], left=plot_df["Delta_punta_7_9"], color="#8ecae6", edgecolor="white", linewidth=0.8, label="Di morbida (fuori 7–9)")
for i, r in enumerate(plot_df.itertuples()):
    ax.annotate(f"{int(r.Delta_totale):+d}", xy=(r.Delta_totale, i), xytext=(8, 0), textcoords="offset points", va="center", ha="left", fontsize=10, fontweight="bold")
    ax.text(r.Delta_punta_7_9/2, i, f"{r.Quota_punta_pct:.0f}%", va="center", ha="center", fontsize=9, color="white", fontweight="bold")
    ax.text(r.Delta_punta_7_9 + r.Delta_morbida_fuori_7_9/2, i, f"{r.Quota_morbida_pct:.0f}%", va="center", ha="center", fontsize=9, color="#16324f", fontweight="bold")
ax.set_yticks(y)
ax.set_yticklabels(plot_df["Stazione"].tolist())
ax.set_title("Crescita delle stazioni meratesi: quanta è di punta e quanta è di morbida\nΔ saliti/giorno, novembre feriale, 2025 vs 2019")
ax.set_xlabel("Δ passeggeri/giorno (2025 − 2019)")
ax.grid(True, axis="x", alpha=0.25)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(loc="upper left", frameon=False)
plt.tight_layout()
fig.savefig(FIG / "grafico_punta_morbida_meratese_2019_2025.png", dpi=220, bbox_inches="tight")

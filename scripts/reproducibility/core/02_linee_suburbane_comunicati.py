#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ricostruisce Linee_S1S12_S5_S6_S8_2019-2025_dataset_v2.xlsx.

Le osservazioni 2024-2025 sono da comunicati Trenord; 2023 è derivato dalle
percentuali 2024 vs 2023; 2019 è ricostruito da base feriale 2019 e quote.
2020-2022 sono una stima opzionale scalata sui passeggeri annui Trenord.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

COLORS = {
    "S1/S12": "#E40520",
    "S5": "#F39123",
    "S6": "#F6D200",
    "S8": "#F6B6B6",
    "Totale Trenord": "#222222",
}

SOURCES = pd.DataFrame([
    {"Fonte": "Trenord dati mobilità 2024", "URL": "https://www.trenord.it/news/trenord-informa/comunicati-stampa/dati-mobilita-2024/", "Uso": "valori 2024 e % vs 2023 per S1/S12, S5, S6, S8"},
    {"Fonte": "Trenord dati 2025", "URL": "https://www.trenord.it/news/trenord-informa/comunicati-stampa/dati-2025-trenord/", "Uso": "valori 2025 e % vs 2024 per S5, S6, S8, S1/S12"},
    {"Fonte": "Contratto Servizio Regione Lombardia - relazione programma esercizio 2019", "URL": "https://www.regione.lombardia.it/wps/wcm/connect/d391f02c-a7e1-4fe3-b341-485dcbda0b7b/ContrattoServizio_RegioneLombardia_Relazione_exDelibera48-2017.pdf?CACHEID=ROOTWORKSPACE-d391f02c-a7e1-4fe3-b341-485dcbda0b7b-nU1-ob3&MOD=AJPERES", "Uso": "quote 2019 programma esercizio"},
    {"Fonte": "Trenord bilanci/comunicati stampa", "URL": "https://www.trenord.it/news/trenord-informa/comunicati-stampa/", "Uso": "totale passeggeri annui 2019-2025"},
])


def build_dataset(include_scaled_2020_2022: bool = True) -> pd.DataFrame:
    # Base 2019 usata nella versione di lavoro: 820.300 utenti feriali Trenord.
    base_2019 = 820_300
    shares_2019 = {
        "S1/S12": 0.0524 + 0.0012,
        "S5": 0.0883,
        "S6": 0.0596,
        # Coerente con il dataset v2 usato nella pagina: circa 32.484 utenti/giorno.
        "S8": 32_484 / base_2019,
    }
    line2019 = {k: round(base_2019 * v) for k, v in shares_2019.items()}

    # Totale annuo Trenord: usato come indice di contesto e per stima 2020-2022.
    total_trenord = {
        2019: 214_521_000,
        2020: 92_577_000,
        2021: 116_348_000,
        2022: 151_000_000,
        2023: 190_000_000,
        2024: 201_000_000,
        2025: 205_000_000,
    }
    scale = {y: total_trenord[y] / total_trenord[2019] for y in total_trenord}

    # 2024 comunicato Trenord: S5 58k (+4%), S8 42k (+15%), S6 41.5k (+7%), S1/S12 40k (+3.3%).
    values_2024 = {"S1/S12": 40_000, "S5": 58_000, "S6": 41_500, "S8": 42_000}
    pct_2024_vs_2023 = {"S1/S12": 0.033, "S5": 0.04, "S6": 0.07, "S8": 0.15}
    values_2023 = {k: round(values_2024[k] / (1 + pct_2024_vs_2023[k])) for k in values_2024}

    # 2025 comunicato Trenord: S5 stabile a 58k; S8 +22%; S6 +2%; S1/S12 35k.
    values_2025 = {"S1/S12": 35_000, "S5": 58_000, "S6": round(41_500 * 1.02), "S8": round(42_000 * 1.22)}

    rows = []
    for serie in ["S1/S12", "S5", "S6", "S8"]:
        for year in range(2019, 2026):
            if year == 2019:
                value = line2019[serie]
                kind = "Stima: 820.300 (Nov 2019) × quota per linea (programma esercizio 2019)"
            elif year in [2020, 2021, 2022]:
                if not include_scaled_2020_2022:
                    continue
                value = round(line2019[serie] * scale[year])
                kind = "Stima: valori 2019 scalati su passeggeri annui Trenord"
            elif year == 2023:
                value = values_2023[serie]
                kind = "Derivato: valore 2024 / (1 + % 2024 vs 2023)"
            elif year == 2024:
                value = values_2024[serie]
                kind = "Ufficiale: comunicato Trenord (dati mobilità 2024)"
            elif year == 2025:
                value = values_2025[serie]
                kind = "Ufficiale: comunicato Trenord (dati 2025)"
            rows.append({"Anno": year, "Serie": serie, "Valore": value, "Unita": "Utenti/giorno feriale", "Tipo_dato": kind, "HEX": COLORS[serie]})

    for year, value in total_trenord.items():
        rows.append({"Anno": year, "Serie": "Totale Trenord", "Valore": value, "Unita": "Passeggeri/anno", "Tipo_dato": "Trenord (bilanci/comunicati stampa)", "HEX": COLORS["Totale Trenord"]})

    df = pd.DataFrame(rows)
    base = df[df["Anno"] == 2019].set_index("Serie")["Valore"].to_dict()
    df["Indice_2019_100"] = df.apply(lambda r: r["Valore"] / base[r["Serie"]] * 100, axis=1)
    return df


def make_xlsx(df: pd.DataFrame, out: Path):
    linee = df[df["Serie"] != "Totale Trenord"].copy()
    total = df[df["Serie"] == "Totale Trenord"].copy()
    assoluti = linee.pivot(index="Anno", columns="Serie", values="Valore").reset_index()
    indici = linee.pivot(index="Anno", columns="Serie", values="Indice_2019_100").reset_index()
    colors = pd.DataFrame([{"Serie": k, "HEX": v} for k, v in COLORS.items()])
    with pd.ExcelWriter(out, engine="openpyxl") as xw:
        df.to_excel(xw, sheet_name="Dataset_tidy", index=False)
        assoluti.to_excel(xw, sheet_name="Assoluti_wide", index=False)
        indici.to_excel(xw, sheet_name="Indice_wide_linee", index=False)
        total.to_excel(xw, sheet_name="Totale_Trenord_annuo", index=False)
        colors.to_excel(xw, sheet_name="Colori_HEX", index=False)
        SOURCES.to_excel(xw, sheet_name="Fonti", index=False)


def make_chart(df: pd.DataFrame, out: Path, include_total=False):
    fig, ax = plt.subplots(figsize=(11.5, 7), dpi=200)
    for serie in ["S1/S12", "S5", "S6", "S8"] + (["Totale Trenord"] if include_total else []):
        sub = df[df["Serie"] == serie].sort_values("Anno")
        ax.plot(sub["Anno"], sub["Indice_2019_100"], marker="o", label=serie, color=COLORS[serie], linewidth=2.5 if serie == "S8" else 2)
    ax.axhline(100, color="#777", linestyle="--", linewidth=1)
    ax.set_title("Linee suburbane — indice passeggeri 2019=100")
    ax.set_xlabel("Anno"); ax.set_ylabel("Indice 2019=100")
    ax.grid(True, alpha=0.25); ax.legend(frameon=False)
    for sp in ax.spines.values(): sp.set_visible(False)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="outputs/linee_suburbane", type=Path)
    ap.add_argument("--no-scaled-2020-2022", action="store_true", help="Non crea stime 2020-2022 per le singole linee")
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    df = build_dataset(include_scaled_2020_2022=not args.no_scaled_2020_2022)
    df.to_csv(args.outdir / "linee_s_indice_2019_2025.csv", index=False)
    df.to_csv(args.outdir / "Linee_S1S12_S5_S6_S8_2019-2025_dataset_v2.csv", index=False)
    make_xlsx(df, args.outdir / "Linee_S1S12_S5_S6_S8_2019-2025_dataset_v2.xlsx")
    make_chart(df, args.outdir / "Linee_S1S12_S5_S6_S8_indice_2019_100.png", include_total=False)

if __name__ == "__main__":
    main()

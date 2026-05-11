# -*- coding: utf-8 -*-
"""Funzioni comuni per riprodurre le analisi S8/Meratese.

I due dataset stazioni Regione Lombardia non hanno identici nomi-colonna per tipo giorno;
qui vengono armonizzati in un unico dataframe.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

NUMERIC_COLS = [
    "Saliti24H", "Saliti7-9", "Discesi7-9", "Corse24H", "Corse7-9",
    "Saliti_S", "Saliti_R", "Saliti_RE", "Corse_S", "Corse_R", "Corse_RE",
]

MERATESI = ["Airuno", "Olgiate-Calco-Brivio", "Cernusco-Merate", "Osnago"]

S8_STATIONS_ORDER = [
    "Milano Porta Garibaldi",
    "Milano Greco Pirelli",
    "Sesto S. Giovanni",
    "Monza",
    "Arcore",
    "Carnate Usmate",
    "Osnago",
    "Cernusco-Merate",
    "Olgiate-Calco-Brivio",
    "Airuno",
    "Calolziocorte-Olginate",
    "Lecco Maggianico",
    "Vercurago-S. Girolamo",
    "Lecco",
]

# Colori usati nei grafici.
MERATESE_COLORS = {
    "Osnago": "#c239c8",
    "Cernusco-Merate": "#23b9c9",
    "Olgiate-Calco-Brivio": "#f06bb6",
    "Airuno": "#a8bf39",
}

S8_NAME_MAP = {
    "MILANO PORTA GARIBALDI": "Milano Porta Garibaldi",
    "MILANO GRECO PIRELLI": "Milano Greco Pirelli",
    "SESTO S. GIOVANNI": "Sesto S. Giovanni",
    "SESTO S.GIOVANNI": "Sesto S. Giovanni",
    "MONZA": "Monza",
    "ARCORE": "Arcore",
    "CARNATE USMATE": "Carnate Usmate",
    "OSNAGO": "Osnago",
    "CERNUSCO-MERATE": "Cernusco-Merate",
    "OLGIATE-CALCO-BRIVIO": "Olgiate-Calco-Brivio",
    "OLGIATE CALCO-BRIVIO": "Olgiate-Calco-Brivio",
    "AIRUNO": "Airuno",
    "CALOLZIOCORTE-OLGINATE": "Calolziocorte-Olginate",
    "CALOLZIOCORTE OLGINATE": "Calolziocorte-Olginate",
    "LECCO MAGGIANICO": "Lecco Maggianico",
    "VERCURAGO-S.GIROLAMO": "Vercurago-S. Girolamo",
    "VERCURAGO S.GIROLAMO": "Vercurago-S. Girolamo",
    "VERCURAGO-S. GIROLAMO": "Vercurago-S. Girolamo",
    "LECCO": "Lecco",
}


def norm_station(s: str) -> str:
    s = str(s).upper().strip()
    for a, b in {"À": "A", "È": "E", "É": "E", "Ì": "I", "Ò": "O", "Ù": "U"}.items():
        s = s.replace(a, b)
    return re.sub(r"[^A-Z0-9]", "", s)


S8_KEY_TO_NAME = {norm_station(k): v for k, v in S8_NAME_MAP.items()}


def month_from_campaign(x: str) -> str | None:
    s = str(x).lower()
    if "nov" in s:
        return "Novembre"
    if "lug" in s:
        return "Luglio"
    if "mag" in s:
        return "Maggio"
    return None


def day_type(x: str) -> str | None:
    s = str(x).lower()
    if "fer" in s:
        return "Feriale"
    if "sab" in s:
        return "Sabato"
    if "fes" in s or "fest" in s:
        return "Festivo"
    return None


def canonical_meratese_label(station_key: str, display_name: str) -> str:
    sk = str(station_key)
    st = str(display_name).upper()
    if "OSNAGO" in sk or st == "OSNAGO":
        return "Osnago"
    if "CERNUSCO" in sk or "CERNUSCO" in st:
        return "Cernusco-Merate"
    if "OLGIATE" in sk or "OLGIATE" in st:
        return "Olgiate-Calco-Brivio"
    if "AIRUNO" in sk or st == "AIRUNO":
        return "Airuno"
    return str(display_name)


def _read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, thousands=".", low_memory=False)


def load_station_data(flussi_path: str | Path, frequentazione_path: str | Path) -> pd.DataFrame:
    """Carica e armonizza i dataset stazioni 2015-2023 e 2024-2025.

    Parametri
    ---------
    flussi_path: dataset storico Flussi Stazioni Ferroviarie.
    frequentazione_path: dataset più recente Frequentazione stazioni SFR.
    """
    fl = _read_csv(flussi_path)
    fr = _read_csv(frequentazione_path)

    for df in (fl, fr):
        for c in NUMERIC_COLS:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

    fl2 = fl.copy()
    fl2["StationKey"] = fl2["Stazione"].map(norm_station)
    fl2["Mese"] = fl2["Campagna"].map(month_from_campaign)
    fl2["TipoGiorno"] = fl2["tipo_giorno"].map(day_type)
    fl2["DisplayName"] = fl2["Stazione"]
    fl2["Fonte"] = "Flussi Stazioni Ferroviarie"

    fr2 = fr.copy()
    fr2["StationKey"] = fr2["Stazione"].map(norm_station)
    fr2["Mese"] = fr2["Campagna"].map(month_from_campaign)
    fr2["TipoGiorno"] = fr2["Tipo giorno"].map(day_type)
    fr2["DisplayName"] = fr2["Stazione"]
    fr2["Fonte"] = "Frequentazione stazioni SFR"

    common = ["Anno", "StationKey", "DisplayName", "Stazione", "Mese", "TipoGiorno", "Fonte"] + [
        c for c in NUMERIC_COLS if c in fl2.columns and c in fr2.columns
    ]
    out = pd.concat([fl2[common], fr2[common]], ignore_index=True)
    out["Stazione_std"] = out["StationKey"].map(S8_KEY_TO_NAME)
    return out


def s8_novembre_feriale(master: pd.DataFrame) -> pd.DataFrame:
    """Restituisce record S8, novembre feriale, per anno/stazione."""
    s8_names = set(S8_STATIONS_ORDER)
    d = master[
        (master["Stazione_std"].isin(s8_names))
        & (master["Mese"] == "Novembre")
        & (master["TipoGiorno"] == "Feriale")
    ].copy()
    value_cols = [c for c in NUMERIC_COLS if c in d.columns]
    d = d.groupby(["Anno", "StationKey", "Stazione_std"], as_index=False)[value_cols].mean()
    if "Saliti24H" in d.columns and "Saliti7-9" in d.columns:
        d["Quota_7_9_pct"] = d["Saliti7-9"] / d["Saliti24H"] * 100
    if "Saliti24H" in d.columns and "Corse24H" in d.columns:
        d["Saliti_per_corsa"] = d["Saliti24H"] / d["Corse24H"]
    return d


def ensure_outdir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

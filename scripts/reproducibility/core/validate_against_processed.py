#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confronta i CSV rigenerati con quelli pubblicati in data/processed."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype


DATASETS = [
    (
        "linee",
        Path("data/processed/linee_s_indice_2019_2025.csv"),
        Path("linee_suburbane/linee_s_indice_2019_2025.csv"),
        ["Anno", "Serie"],
    ),
    (
        "stazioni",
        Path("data/processed/stazioni_s8_indice_2015_2025.csv"),
        Path("s8_indice_stazioni/stazioni_s8_indice_2015_2025.csv"),
        ["Stazione_std", "Anno"],
    ),
    (
        "peso_punta",
        Path("data/processed/peso_punta_stazioni_s8_2015_2025.csv"),
        Path("s8_peso_punta/peso_punta_stazioni_s8_2015_2025.csv"),
        ["Stazione", "Anno"],
    ),
    (
        "punta_morbida_serie",
        Path("data/processed/crescita_meratese_punta_morbida_2015_2025.csv"),
        Path("s8_peso_punta/crescita_meratese_punta_morbida_2015_2025.csv"),
        ["Anno", "Stazione"],
    ),
    (
        "scatter",
        Path("data/processed/scatter_stazioni_lombarde_2019_2025.csv"),
        Path("scatter_lombardia/scatter_stazioni_lombarde_2019_2025.csv"),
        ["StationKey"],
    ),
]


def unequal_mask(current: pd.Series, rebuilt: pd.Series) -> pd.Series:
    if is_bool_dtype(current) or is_bool_dtype(rebuilt):
        return current.fillna(False).astype(bool) != rebuilt.fillna(False).astype(bool)
    if is_numeric_dtype(current) and is_numeric_dtype(rebuilt):
        delta = (pd.to_numeric(current, errors="coerce") - pd.to_numeric(rebuilt, errors="coerce")).abs()
        return delta.fillna(0) > 1e-8
    return current.fillna("").astype(str) != rebuilt.fillna("").astype(str)


def compare_one(root: Path, rebuilt_dir: Path, name: str, current_rel: Path, rebuilt_rel: Path, keys: list[str]) -> bool:
    current_path = root / current_rel
    rebuilt_path = rebuilt_dir / rebuilt_rel
    current = pd.read_csv(current_path)
    rebuilt = pd.read_csv(rebuilt_path)

    print(f"{name}: current {current.shape}, rebuilt {rebuilt.shape}")
    if list(current.columns) != list(rebuilt.columns):
        print("  ERRORE colonne diverse")
        print("  current:", list(current.columns))
        print("  rebuilt:", list(rebuilt.columns))
        return False

    merged = current.merge(rebuilt, on=keys, how="outer", indicator=True, suffixes=("_current", "_rebuilt"))
    missing = merged[merged["_merge"] != "both"]
    if len(missing):
        print("  ERRORE chiavi diverse:", missing["_merge"].value_counts().to_dict())
        print(missing[keys + ["_merge"]].head(20).to_string(index=False))
        return False

    differences = []
    for column in current.columns:
        if column in keys:
            continue
        mask = unequal_mask(merged[f"{column}_current"], merged[f"{column}_rebuilt"])
        if mask.any():
            differences.append((column, int(mask.sum())))

    if differences:
        print("  ERRORE valori diversi:")
        for column, count in differences:
            print(f"  - {column}: {count} righe")
        return False

    print("  OK")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuilt", type=Path, default=Path("outputs/rebuilt"))
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[3]
    rebuilt_dir = args.rebuilt if args.rebuilt.is_absolute() else root / args.rebuilt
    ok = True
    for dataset in DATASETS:
        ok = compare_one(root, rebuilt_dir, *dataset) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

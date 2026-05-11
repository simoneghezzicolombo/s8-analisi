#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Esegue tutti gli script principali.

Uso:
python scripts/reproducibility/core/build_all.py --rawdir data/raw --outdir outputs/rebuilt
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print("$", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rawdir", type=Path, default=Path("data/raw"))
    ap.add_argument("--outdir", type=Path, default=Path("outputs"))
    ap.add_argument("--threshold", type=int, default=700)
    args = ap.parse_args()
    script_dir = Path(__file__).resolve().parent
    flussi = args.rawdir / "regione_lombardia_flussi_stazioni_2015_2023_20260424.csv"
    freq = args.rawdir / "regione_lombardia_frequentazione_stazioni_sfr_20260424.csv"
    py = sys.executable
    run([py, script_dir / "01_s8_indice_stazioni_saliti24h.py", "--flussi", flussi, "--frequentazione", freq, "--outdir", args.outdir / "s8_indice_stazioni"])
    run([py, script_dir / "02_linee_suburbane_comunicati.py", "--outdir", args.outdir / "linee_suburbane"])
    run([py, script_dir / "03_s8_peso_punta_mattutina.py", "--flussi", flussi, "--frequentazione", freq, "--outdir", args.outdir / "s8_peso_punta"])
    run([py, script_dir / "04_scatter_lombardia_crescita_carico.py", "--flussi", flussi, "--frequentazione", freq, "--outdir", args.outdir / "scatter_lombardia", "--threshold", str(args.threshold)])

if __name__ == "__main__":
    main()

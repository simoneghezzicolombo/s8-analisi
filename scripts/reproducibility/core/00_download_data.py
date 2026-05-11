#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Downloader opzionale dei dataset Regione Lombardia.

Nota: gli endpoint Socrata possono cambiare o avere limiti; per riproducibilità
è consigliato archiviare anche una copia dei CSV grezzi usati.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import requests

URLS = {
    "flussi": "https://www.dati.lombardia.it/resource/m2u2-frtq.csv?$limit=5000000",
    "frequentazione": "https://www.dati.lombardia.it/resource/ut63-s688.csv?$limit=5000000",
    "linee": "https://hub.dati.lombardia.it/resource/dpns-ehdj.csv?$limit=5000000",
}

FILENAMES = {
    "flussi": "regione_lombardia_flussi_stazioni_2015_2023_20260424.csv",
    "frequentazione": "regione_lombardia_frequentazione_stazioni_sfr_20260424.csv",
    "linee": "regione_lombardia_frequentazione_linee_sfr_20260424.csv",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="data/raw", type=Path)
    ap.add_argument("--only", choices=list(URLS), nargs="*")
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    keys = args.only or list(URLS)
    for key in keys:
        url = URLS[key]
        out = args.outdir / FILENAMES[key]
        print(f"Scarico {key}: {url}")
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        out.write_bytes(r.content)
        print(f"Salvato: {out}")

if __name__ == "__main__":
    main()

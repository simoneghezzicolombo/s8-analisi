#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks source availability and value anchors for the Top 20 dataset."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

from common import (
    ROOT,
    OUTDIR,
    contains_any,
    fetch_text,
    is_url,
    line_value_variants,
    snippets,
    words_from_label,
    write_csv,
)

TOP20 = ROOT / "data" / "processed" / "top20_linee_locali_italia.csv"
SCRIPT_DIR = ROOT / "scripts" / "reproducibility" / "top20"


def automation_level(row: pd.Series, direct_value_match: bool, source_context_match: bool) -> str:
    status = str(row.get("status", ""))
    if status == "L25":
        return "recomputed_from_structured_lombardia_raw"
    if status == "S" and (direct_value_match or source_context_match):
        return "supporting_sources_checked_estimate_not_fully_automatic"
    if direct_value_match:
        return "direct_value_anchor_found_in_source"
    if status == "R":
        return "direct_source_expected_but_value_anchor_not_found"
    if status == "R/S":
        return "regional_source_checked_line_parser_needed"
    if source_context_match:
        return "supporting_sources_checked_estimate_not_fully_automatic"
    return "source_not_confirmed_by_generic_audit"


def method_note(
    row: pd.Series,
    primary_ok: bool,
    secondary_ok: bool,
    direct_match: bool,
    source_context_match: bool,
) -> str:
    status = str(row.get("status", ""))
    if status == "L25":
        return "La riga Lombardia/TILO e' ricalcolata da CSV regionale 2025 con lo script top20 esistente."
    if status == "S" and (direct_match or source_context_match):
        return "Le fonti sono controllabili, ma non pubblicano il valore finale come dato ufficiale di linea: il valore resta una stima modellata documentata."
    if direct_match:
        return "La fonte contiene un ancoraggio numerico compatibile con il valore finale."
    if status == "R":
        return "Fonte ufficiale diretta scaricata, ma il parser generico non ha trovato l'ancoraggio numerico esatto."
    if status == "R/S":
        return "Fonte regionale disponibile; serve parser dedicato per trasformare tabelle/pagine locali in valore annuo di linea."
    if source_context_match:
        return "Le fonti citano la linea o il contesto di stima, ma non pubblicano il valore finale come dato linea ufficiale."
    if primary_ok or secondary_ok:
        return "Le fonti di supporto sono scaricabili; il valore finale resta una stima modellata documentata, non un dato linea ufficiale."
    return "Fonti non verificate automaticamente in questa esecuzione."


def audit_source(
    url: str,
    source_cache: dict[str, object],
    line_patterns: list[str],
    value_patterns: list[str],
) -> dict:
    if not is_url(url):
        return {
            "url": url,
            "fetch_ok": False,
            "http_status": None,
            "content_type": "",
            "cache_path": "",
            "line_match": False,
            "value_match": False,
            "snippets": "",
            "error": "not a URL",
        }
    source = source_cache.setdefault(url, fetch_text(url))
    relevant_patterns = value_patterns + line_patterns
    line_match = contains_any(source.text, line_patterns) if source.ok else False
    value_match = contains_any(source.text, value_patterns) if source.ok else False
    return {
        "url": source.url,
        "fetch_ok": source.ok,
        "http_status": source.status_code,
        "content_type": source.content_type,
        "cache_path": source.cache_path,
        "line_match": line_match,
        "value_match": value_match,
        "snippets": " || ".join(snippets(source.text, relevant_patterns, limit=4)) if source.ok else "",
        "error": source.error,
    }


def main() -> int:
    top = pd.read_csv(TOP20)
    # Keep the structured Lombardia recomputation in the same audit workflow.
    subprocess.check_call([sys.executable, str(SCRIPT_DIR / "calculate_lombardia_annualization.py")])

    source_cache: dict[str, object] = {}
    rows = []
    for _, row in top.iterrows():
        line_patterns = [str(row.get("line_code", "")), str(row.get("line_name", ""))]
        line_patterns.extend(words_from_label(str(row.get("line_name", "")))[:6])
        value_patterns = line_value_variants(row.get("central_mln"))

        primary = audit_source(row.get("primary_source", ""), source_cache, line_patterns, value_patterns)
        secondary = audit_source(row.get("secondary_source", ""), source_cache, line_patterns, value_patterns)
        direct_match = bool(primary["value_match"] or secondary["value_match"])
        source_context_match = bool(
            primary["line_match"]
            or secondary["line_match"]
            or primary["value_match"]
            or secondary["value_match"]
        )

        rows.append({
            "rank": row.get("rank"),
            "line_code": row.get("line_code"),
            "line_name": row.get("line_name"),
            "status": row.get("status"),
            "data_year": row.get("data_year"),
            "central_mln": row.get("central_mln"),
            "automation_level": automation_level(row, direct_match, source_context_match),
            "primary_url": primary["url"],
            "primary_fetch_ok": primary["fetch_ok"],
            "primary_http_status": primary["http_status"],
            "primary_line_match": primary["line_match"],
            "primary_value_match": primary["value_match"],
            "primary_cache_path": primary["cache_path"],
            "secondary_url": secondary["url"],
            "secondary_fetch_ok": secondary["fetch_ok"],
            "secondary_http_status": secondary["http_status"],
            "secondary_line_match": secondary["line_match"],
            "secondary_value_match": secondary["value_match"],
            "secondary_cache_path": secondary["cache_path"],
            "method_note": method_note(
                row,
                bool(primary["fetch_ok"]),
                bool(secondary["fetch_ok"]),
                direct_match,
                source_context_match,
            ),
            "primary_snippets": primary["snippets"],
            "secondary_snippets": secondary["snippets"],
            "primary_error": primary["error"],
            "secondary_error": secondary["error"],
        })

    out = pd.DataFrame(rows)
    write_csv(out, OUTDIR / "top20_source_audit.csv")

    gaps = out[~out["automation_level"].isin([
        "recomputed_from_structured_lombardia_raw",
        "direct_value_anchor_found_in_source",
    ])].copy()
    write_csv(gaps[[
        "rank", "line_code", "line_name", "status", "central_mln",
        "automation_level", "method_note", "primary_url", "secondary_url"
    ]], OUTDIR / "top20_automation_gaps.csv")

    print(f"Creato: {OUTDIR / 'top20_source_audit.csv'}")
    print(f"Creato: {OUTDIR / 'top20_automation_gaps.csv'}")
    print(out["automation_level"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

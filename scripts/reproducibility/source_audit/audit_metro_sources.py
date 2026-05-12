#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks the sources used by the S8/metropolitan benchmark dataset."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from common import (
    ROOT,
    OUTDIR,
    contains_any,
    fetch_text,
    is_url,
    number_variants,
    snippets,
    words_from_label,
    write_csv,
)

DATASET = ROOT / "data" / "processed" / "benchmark_metropolitane_s8.csv"


def passenger_anchors_from_note(note: str) -> list[str]:
    note = str(note or "")
    anchors = []
    pattern = r"(\d{1,3}(?:[.]\d{3})+|\d+)\s+(?:passeggeri/giorno|passeggeri|viaggiatori|utenti)"
    for match in re.finditer(pattern, note, flags=re.IGNORECASE):
        raw = match.group(1)
        anchors.extend([raw, raw.replace(".", "")])
        if "." in raw:
            thousands = raw.split(".")[0]
            anchors.extend([
                f"{thousands}mila",
                f"{thousands} mila",
                f"{thousands}mila passeggeri",
                f"{thousands} mila passeggeri",
                f"{thousands}mila viaggiatori",
                f"{thousands} mila viaggiatori",
            ])
    return anchors


def frequency_variants(row: pd.Series) -> list[str]:
    variants = []
    box = str(row.get("frequenza_box") or "")
    if box:
        variants.extend([box, box.replace("'", " minuti"), box.replace(",", ".")])
    for col in ["frequenza_punta_min", "frequenza_ordinaria_min"]:
        val = row.get(col)
        if pd.notna(val):
            variants.extend(number_variants(float(val), "minuti"))
            variants.append(str(val).replace(".", ",") + "'")
    return sorted(set(v for v in variants if v and v != "nan"))


def source_rows(df: pd.DataFrame) -> list[dict]:
    rows = []
    for _, row in df.iterrows():
        for source_field in ["fonte_passeggeri", "fonte_frequenza"]:
            url = row.get(source_field)
            if is_url(url):
                rows.append({"source_field": source_field, "url": url, **row.to_dict()})
    return rows


def audit_one(item: dict, source_cache: dict[str, object]) -> dict:
    url = item["url"]
    source = source_cache.setdefault(url, fetch_text(url))

    passenger_patterns = []
    passenger_patterns.extend(number_variants(item.get("passeggeri_annui")))
    label = item.get("passeggeri_annui_label")
    if isinstance(label, str) and label:
        passenger_patterns.append(label)
    passenger_patterns.extend(passenger_anchors_from_note(item.get("note", "")))

    freq_patterns = frequency_variants(pd.Series(item))
    service_patterns = words_from_label(item.get("servizio", ""))[:4]

    passenger_match = contains_any(source.text, passenger_patterns) if source.ok else False
    frequency_match = contains_any(source.text, freq_patterns) if source.ok else False
    service_match = contains_any(source.text, service_patterns) if source.ok else False
    if item["source_field"] == "fonte_passeggeri":
        expected_anchor = "passenger"
        expected_anchor_match = passenger_match
    else:
        expected_anchor = "frequency"
        expected_anchor_match = frequency_match

    if not source.ok:
        audit_status = "blocked_or_unavailable"
    elif expected_anchor_match:
        audit_status = f"{expected_anchor}_anchor_found"
    elif service_match:
        audit_status = "source_reachable_context_found_anchor_missing"
    else:
        audit_status = "source_reachable_anchor_missing"

    relevant_patterns = passenger_patterns + freq_patterns + service_patterns
    return {
        "servizio": item.get("servizio"),
        "source_field": item["source_field"],
        "expected_anchor": expected_anchor,
        "url": source.url,
        "http_status": source.status_code,
        "content_type": source.content_type,
        "fetch_ok": source.ok,
        "service_match": service_match,
        "passenger_anchor_match": passenger_match,
        "frequency_anchor_match": frequency_match,
        "expected_anchor_match": expected_anchor_match,
        "audit_status": audit_status,
        "cache_path": source.cache_path,
        "error": source.error,
        "snippets": " || ".join(snippets(source.text, relevant_patterns, limit=4)) if source.ok else "",
    }


def main() -> int:
    df = pd.read_csv(DATASET)
    cache: dict[str, object] = {}
    results = [audit_one(item, cache) for item in source_rows(df)]
    out = pd.DataFrame(results)
    write_csv(out, OUTDIR / "metro_source_audit.csv")

    services = out.groupby("servizio", dropna=False).agg(
        sources_checked=("url", "count"),
        fetch_ok=("fetch_ok", "sum"),
        passenger_anchor_match=("passenger_anchor_match", "sum"),
        frequency_anchor_match=("frequency_anchor_match", "sum"),
        expected_anchor_match=("expected_anchor_match", "sum"),
    ).reset_index()
    write_csv(services, OUTDIR / "metro_source_audit_summary.csv")

    gaps = out[~out["expected_anchor_match"]].copy()
    write_csv(gaps[[
        "servizio", "source_field", "expected_anchor", "audit_status",
        "fetch_ok", "http_status", "url", "error"
    ]], OUTDIR / "metro_automation_gaps.csv")

    failed = out[~out["fetch_ok"]]
    if len(failed):
        print("WARNING: alcune fonti metro non sono state scaricate")
        print(failed[["servizio", "source_field", "url", "error"]].to_string(index=False))
    print(f"Creato: {OUTDIR / 'metro_source_audit.csv'}")
    print(f"Creato: {OUTDIR / 'metro_source_audit_summary.csv'}")
    print(f"Creato: {OUTDIR / 'metro_automation_gaps.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

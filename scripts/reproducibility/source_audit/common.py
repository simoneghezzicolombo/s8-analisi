# -*- coding: utf-8 -*-
"""Utilities for checking web/PDF sources used by the public datasets."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[3]
OUTDIR = ROOT / "data" / "reproducibility" / "source_audit"
CACHE = ROOT / "data" / "reproducibility" / "source_audit" / "_cache"

HEADERS = {
    "User-Agent": "Mozilla/5.0 source-audit/1.0 (+https://github.com/simoneghezzicolombo/s8-analisi)"
}


@dataclass
class SourceText:
    url: str
    ok: bool
    status_code: int | None
    content_type: str
    text: str
    error: str = ""
    cache_path: str = ""


def is_url(value: object) -> bool:
    return isinstance(value, str) and value.startswith(("http://", "https://"))


def normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def cache_name(url: str, content_type: str) -> str:
    suffix = ".pdf" if "pdf" in content_type.lower() or url.lower().endswith(".pdf") else ".html"
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16] + suffix


def extract_pdf_text(content: bytes, max_pages: int | None = None) -> str:
    reader = PdfReader(BytesIO(content))
    pages = reader.pages[:max_pages] if max_pages else reader.pages
    chunks = []
    for page in pages:
        chunks.append(page.extract_text() or "")
    return normalize_text("\n".join(chunks))


def extract_html_text(content: bytes) -> str:
    soup = BeautifulSoup(content, "lxml")
    for node in soup(["script", "style", "noscript", "svg"]):
        node.decompose()
    return normalize_text(soup.get_text(" "))


def fetch_text(url: str, timeout: int = 45) -> SourceText:
    CACHE.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        content_type = response.headers.get("content-type", "")
        cache_path = CACHE / cache_name(response.url, content_type)
        cache_path.write_bytes(response.content)
        response.raise_for_status()
        if "pdf" in content_type.lower() or response.url.lower().endswith(".pdf"):
            text = extract_pdf_text(response.content)
        else:
            text = extract_html_text(response.content)
        return SourceText(
            url=response.url,
            ok=True,
            status_code=response.status_code,
            content_type=content_type,
            text=text,
            cache_path=str(cache_path.relative_to(ROOT)),
        )
    except Exception as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        return SourceText(url=url, ok=False, status_code=status, content_type="", text="", error=str(exc))


def words_from_label(label: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9]+", str(label))
    return [w for w in words if len(w) >= 3]


def number_variants(value: float | int | None, unit: str = "") -> list[str]:
    if value is None or pd.isna(value):
        return []
    value = float(value)
    variants: set[str] = set()
    if value >= 1_000_000:
        whole = int(round(value))
        mln = value / 1_000_000
        variants.update({
            str(whole),
            f"{whole:,}".replace(",", "."),
            f"{mln:.0f}".replace(".", ",") + " milioni",
            f"{mln:.0f}".replace(".", ",") + " mln",
            f"{mln:.1f}".replace(".", ",") + " milioni",
            f"{mln:.2f}".replace(".", ",") + " milioni",
            f"{mln:.1f}".replace(".", ",") + " mln",
            f"{mln:.2f}".replace(".", ",") + " mln",
        })
    elif value >= 1000:
        whole = int(round(value))
        variants.update({
            str(whole),
            f"{whole:,}".replace(",", "."),
            f"{whole / 1000:.1f}".replace(".", ",") + " mila",
            f"{whole / 1000:.0f}".replace(".", ",") + " mila",
        })
    else:
        variants.update({
            str(int(round(value))),
            f"{value:.1f}".replace(".", ","),
            f"{value:.2f}".replace(".", ","),
        })
    if unit:
        variants.update({v + " " + unit for v in list(variants)})
    return sorted(v for v in variants if v)


def line_value_variants(mln: float | int | None) -> list[str]:
    if mln is None or pd.isna(mln):
        return []
    mln = float(mln)
    passengers = int(round(mln * 1_000_000))
    return sorted(set(number_variants(passengers) + [
        f"{mln:.1f}".replace(".", ","),
        f"{mln:.2f}".replace(".", ","),
        f"{mln:.3f}".replace(".", ","),
        f"{mln:.0f}".replace(".", ",") + " milioni",
        f"{mln:.0f}".replace(".", ",") + " mln",
        f"{mln:.1f}".replace(".", ",") + " milioni",
        f"{mln:.2f}".replace(".", ",") + " milioni",
        f"{mln:.1f}".replace(".", "."),
    ]))


def contains_any(text: str, patterns: Iterable[str]) -> bool:
    text_low = text.lower()
    for pattern in patterns:
        p = str(pattern).strip().lower()
        if not p:
            continue
        if p in text_low:
            return True
        million = re.fullmatch(r"(\d+(?:[,.]\d+)?)\s+(milioni|mln)", p)
        if million:
            number = million.group(1)
            unit = million.group(2)
            number_alts = {
                number,
                number.replace(",", "."),
                number.replace(".", ","),
            }
            regex = r"\b(?:" + "|".join(re.escape(n) for n in number_alts) + r")(?:\s+\w{1,2})?\s+" + re.escape(unit) + r"\b"
            if re.search(regex, text_low):
                return True
    return False


def snippets(text: str, patterns: Iterable[str], window: int = 120, limit: int = 3) -> list[str]:
    text_low = text.lower()
    found = []
    for pattern in patterns:
        p = str(pattern).strip()
        if not p:
            continue
        idx = text_low.find(p.lower())
        if idx >= 0:
            start = max(0, idx - window)
            end = min(len(text), idx + len(p) + window)
            snippet = normalize_text(text[start:end])
            if snippet not in found:
                found.append(snippet)
        if len(found) >= limit:
            break
    return found


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

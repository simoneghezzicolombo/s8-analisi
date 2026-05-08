from __future__ import annotations

import csv
from pathlib import Path
from textwrap import shorten

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "PPT_INIZIALE_review"
CATALOG_CSV = OUT / "catalogo_grafici_candidati.csv"
CONTACT_SHEET = OUT / "contact_sheet_grafici_candidati.png"

SKIP_PARTS = {"PPT_INIZIALE_review", "grafici_sleek"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
DATA_SUFFIXES = {".csv", ".xlsx", ".xls"}


def font(size: int, bold: bool = False):
    font_name = "arialbd.ttf" if bold else "arial.ttf"
    path = Path("C:/Windows/Fonts") / font_name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def is_candidate_image(path: Path) -> bool:
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        return False
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    return True


def probable_data_files(image_path: Path) -> list[Path]:
    folder = image_path.parent
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in DATA_SUFFIXES]
    image_words = {w.lower() for w in image_path.stem.replace("_", " ").replace("-", " ").split() if len(w) > 2}

    def score(path: Path) -> tuple[int, str]:
        words = {w.lower() for w in path.stem.replace("_", " ").replace("-", " ").split() if len(w) > 2}
        overlap = len(image_words & words)
        if "dataset" in path.stem.lower():
            overlap += 2
        if "indice" in path.stem.lower() or "output" in path.stem.lower():
            overlap += 1
        return (-overlap, path.name.lower())

    return sorted(files, key=score)[:4]


def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not is_candidate_image(path):
            continue
        try:
            with Image.open(path) as img:
                width, height = img.size
        except Exception:
            continue
        rel = path.relative_to(ROOT)
        data_files = probable_data_files(path)
        rows.append(
            {
                "id": len(rows) + 1,
                "file": str(rel),
                "folder": str(path.parent.relative_to(ROOT)),
                "width": width,
                "height": height,
                "size_kb": round(path.stat().st_size / 1024, 1),
                "probable_data": " | ".join(str(p.relative_to(ROOT)) for p in data_files),
            }
        )

    with CATALOG_CSV.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["id", "file"])
        writer.writeheader()
        writer.writerows(rows)

    thumb_w, thumb_h = 360, 220
    pad = 22
    label_h = 78
    cols = 3
    rows_count = (len(rows) + cols - 1) // cols
    sheet_w = cols * (thumb_w + pad) + pad
    sheet_h = rows_count * (thumb_h + label_h + pad) + pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), "#F6F7F4")
    draw = ImageDraw.Draw(sheet)
    f_id = font(22, True)
    f_text = font(17, False)
    f_small = font(14, False)

    for row in rows:
        idx = row["id"] - 1
        col = idx % cols
        r = idx // cols
        x = pad + col * (thumb_w + pad)
        y = pad + r * (thumb_h + label_h + pad)
        image_path = ROOT / row["file"]
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            bx = x + (thumb_w - img.width) // 2
            by = y + (thumb_h - img.height) // 2
            sheet.paste(img, (bx, by))
        draw.rectangle((x, y, x + thumb_w, y + thumb_h), outline="#D7DDD7", width=1)
        draw.text((x, y + thumb_h + 12), f"{row['id']:02d}", font=f_id, fill="#1F2933")
        draw.text((x + 48, y + thumb_h + 14), shorten(Path(row["file"]).name, width=43, placeholder="..."), font=f_text, fill="#1F2933")
        draw.text((x + 48, y + thumb_h + 42), shorten(row["folder"], width=48, placeholder="..."), font=f_small, fill="#667085")

    sheet.save(CONTACT_SHEET, "PNG", optimize=True)
    print(CATALOG_CSV)
    print(CONTACT_SHEET)
    print(f"{len(rows)} images catalogued")


if __name__ == "__main__":
    main()

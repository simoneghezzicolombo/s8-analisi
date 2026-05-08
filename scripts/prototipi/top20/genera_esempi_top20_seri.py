from __future__ import annotations

import re
import sys
from pathlib import Path
from textwrap import shorten

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "grafici_sleek"))

from chart_style import Canvas, fit_text  # noqa: E402


DATA_PATH = ROOT / "linee" / "top 20 italia" / "base_dati_top20_linee_ferroviarie_nonAV_italia_colori_finali_tilo_blu_ticino.xlsx"
OUT_DIR = ROOT / "grafici_rifatti_v01" / "top20_linee_modelli_seri"

W, H = 2200, 1500
MAX_X = 22.0
S8 = "#A64E6B"


THEMES = {
    "neutral": {
        "paper": "#FFFFFF",
        "ink": "#202124",
        "muted": "#5F6368",
        "grid": "#E2E5E2",
        "bar": "#C9CECA",
        "bar2": "#9FA7A2",
        "accent": S8,
        "accent_soft": "#F1D5DE",
    },
    "report": {
        "paper": "#FAFAF8",
        "ink": "#1F2933",
        "muted": "#667085",
        "grid": "#E1E5E1",
        "bar": "#D3D7D4",
        "bar2": "#A6AEA8",
        "accent": S8,
        "accent_soft": "#F3D9E1",
    },
    "ft_serious": {
        "paper": "#FFF7EF",
        "ink": "#2B2B2B",
        "muted": "#706B66",
        "grid": "#DED4C8",
        "bar": "#D4CBC1",
        "bar2": "#AFA59A",
        "accent": "#9B4A67",
        "accent_soft": "#F0D1DA",
    },
}


def clean_route(code: str, line_name: str) -> str:
    text = str(line_name).replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text).strip()
    if text.startswith(f"{code} "):
        text = text[len(code) + 1 :]
    replacements = {
        "Fiumicino Aeroporto - Roma - Fara Sabina/Orte": "Fiumicino - Roma - Fara Sabina",
        "Saronno - Seregno - Milano San Cristoforo - Albairate": "Saronno - Seregno - Milano - Albairate",
        "Locarno - Chiasso - Como - Milano Centrale": "Locarno - Chiasso - Como - Milano",
        "Varese - Milano Passante - Treviglio": "Varese - Milano - Treviglio",
        "Novara - Milano Passante - Treviglio/Pioltello": "Novara - Milano - Treviglio",
        "Pavia - Milano Passante - Milano Bovisa": "Pavia - Milano - Bovisa",
        "Saronno - Milano Passante - Lodi": "Saronno - Milano - Lodi",
        "Chiasso - Seregno - Milano Porta Garibaldi": "Chiasso - Seregno - Milano",
        "Roma-Lido / Metromare": "Roma - Lido",
    }
    return replacements.get(text, text)


def label_for(row) -> str:
    code = str(row["line_code"])
    route = clean_route(code, row["line_name"])
    if code in {"Roma-Viterbo", "Firenze-Pistoia-Lucca", "Bologna-Piacenza-Milano", "Padova-Venezia"}:
        return route
    return f"{code} · {route}"


def fmt(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def font(size: int, weight: str = "regular"):
    files = {
        "regular": ["segoeui.ttf", "arial.ttf"],
        "semibold": ["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"],
        "bold": ["segoeuib.ttf", "arialbd.ttf"],
    }
    for name in files.get(weight, files["regular"]):
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def source_text() -> str:
    return "Fonte: elaborazione su dati Trenord, Cotral, Trenitalia e Regioni. Valori in milioni di passeggeri annui, 2024-2025."


def header(c: Canvas, theme: dict, title: str, subtitle: str):
    c.text((115, 112), "Passeggeri annui delle principali linee ferroviarie locali non AV", c.font(24, "semibold"), theme["muted"])
    c.text((115, 178), title, c.font(50, "bold"), theme["ink"])
    c.text((115, 236), subtitle, c.font(26, "regular"), theme["muted"])


def footer(c: Canvas, theme: dict, y: int = H - 112):
    c.line((115, y - 24, W - 115, y - 24), theme["grid"], width=1)
    c.text((115, y + 4), source_text(), c.font(19), theme["muted"])


def draw_full_bar(df: pd.DataFrame, theme: dict, out: Path, title: str, subtitle: str, annotate: bool = True):
    c = Canvas(W, H, theme["paper"], scale=2)
    header(c, theme, title, subtitle)

    x0, y0 = 730, 326
    plot_w, row_h, bar_h = 1210, 49, 30
    label_x = 120
    bottom = y0 + len(df) * row_h + 34

    for tick in [0, 5, 10, 15, 20]:
        x = x0 + tick / MAX_X * plot_w
        c.line((x, y0 - 20, x, bottom - 20), theme["grid"], width=1)
        c.text((x, bottom + 20), str(tick), c.font(20), theme["muted"], anchor="mm")

    for _, row in df.iterrows():
        i = int(row["rank"]) - 1
        y = y0 + i * row_h
        value = float(row["central_mln"])
        width = value / MAX_X * plot_w
        code = str(row["line_code"])
        is_s8 = code == "S8"
        bar = theme["accent"] if is_s8 else theme["bar"]
        text_color = theme["accent"] if is_s8 else theme["ink"]

        label = fit_text(c.draw, f"{int(row['rank'])}. {label_for(row)}", c.font(21), c.u(x0 - label_x - 34))
        c.text((label_x, y + 22), label, c.font(21, "semibold" if is_s8 else "regular"), text_color, anchor="lm")
        if is_s8:
            c.rectangle((x0 - 5, y - 4, x0 + width + 5, y + bar_h + 4), theme["accent_soft"], outline=theme["accent"], width=3)
            c.rectangle((x0, y + 4, x0 + width, y + bar_h - 4), bar)
        else:
            c.rectangle((x0, y, x0 + width, y + bar_h), bar)
        c.text((x0 + width + 14, y + 22), fmt(value), c.font(21, "semibold"), text_color, anchor="lm")

    if annotate:
        s8 = df[df["line_code"] == "S8"].iloc[0]
        s8_y = y0 + (int(s8["rank"]) - 1) * row_h
        c.text((x0 + 850, s8_y - 20), "S8 Lecco - Milano", c.font(25, "bold"), theme["accent"])
        c.text((x0 + 850, s8_y + 14), "4a posizione nella graduatoria", c.font(22), theme["muted"])

    c.text((x0 + plot_w / 2, bottom + 62), "Milioni di passeggeri annui", c.font(23), theme["ink"], anchor="mm")
    footer(c, theme)
    c.save_png(out)


def draw_split_top_context(df: pd.DataFrame, theme: dict, out: Path):
    c = Canvas(W, H, theme["paper"], scale=2)
    header(
        c,
        theme,
        "La S8 è nel primo gruppo della classifica nazionale",
        "Le prime quattro linee superano tutte quota 14 milioni di passeggeri annui.",
    )

    top4 = df.head(4)
    rest = df.iloc[4:]
    x0, y0 = 620, 360
    plot_w, bar_h, row_h = 1150, 42, 82
    label_x = 145
    c.text((label_x, y0 - 50), "Prime quattro linee", c.font(25, "bold"), theme["ink"])
    for tick in [0, 5, 10, 15, 20]:
        x = x0 + tick / MAX_X * plot_w
        c.line((x, y0 - 22, x, y0 + len(top4) * row_h - 28), theme["grid"], width=1)

    for _, row in top4.iterrows():
        i = int(row["rank"]) - 1
        y = y0 + i * row_h
        value = float(row["central_mln"])
        width = value / MAX_X * plot_w
        is_s8 = row["line_code"] == "S8"
        c.text((label_x, y + 30), f"{int(row['rank'])}. {label_for(row)}", c.font(26, "semibold" if is_s8 else "regular"), theme["accent"] if is_s8 else theme["ink"], anchor="lm")
        c.rectangle((x0, y, x0 + width, y + bar_h), theme["accent"] if is_s8 else theme["bar"])
        c.text((x0 + width + 18, y + 30), fmt(value), c.font(25, "bold" if is_s8 else "semibold"), theme["accent"] if is_s8 else theme["ink"], anchor="lm")

    y2 = y0 + len(top4) * row_h + 110
    c.line((115, y2 - 48, W - 115, y2 - 48), theme["grid"], width=1)
    c.text((label_x, y2), "Dal 5° al 20° posto", c.font(24, "bold"), theme["ink"])
    x_small = 650
    for _, row in rest.iterrows():
        i = int(row["rank"]) - 5
        col = 0 if i < 8 else 1
        rr = i if i < 8 else i - 8
        y = y2 + 48 + rr * 48
        x_label = label_x + col * 900
        x_bar = x_small + col * 900
        value = float(row["central_mln"])
        width = value / MAX_X * 450
        c.text((x_label, y + 18), f"{int(row['rank'])}. {str(row['line_code'])}", c.font(19, "semibold"), theme["ink"], anchor="lm")
        c.rectangle((x_bar, y, x_bar + width, y + 22), theme["bar"])
        c.text((x_bar + width + 10, y + 17), fmt(value), c.font(18), theme["muted"], anchor="lm")

    footer(c, theme)
    c.save_png(out)


def draw_monochrome(df: pd.DataFrame, theme: dict, out: Path):
    c = Canvas(W, H, theme["paper"], scale=2)
    header(
        c,
        theme,
        "Le 20 linee locali con più passeggeri annui",
        "Versione monocromatica: l'unica evidenza visiva è la S8.",
    )
    x0, y0 = 730, 326
    plot_w, row_h, bar_h = 1210, 49, 28
    label_x = 120
    bottom = y0 + len(df) * row_h + 34
    for tick in [0, 5, 10, 15, 20]:
        x = x0 + tick / MAX_X * plot_w
        c.line((x, y0 - 20, x, bottom - 20), theme["grid"], width=1)
        c.text((x, bottom + 20), str(tick), c.font(20), theme["muted"], anchor="mm")
    for _, row in df.iterrows():
        i = int(row["rank"]) - 1
        y = y0 + i * row_h
        value = float(row["central_mln"])
        width = value / MAX_X * plot_w
        is_s8 = row["line_code"] == "S8"
        label = fit_text(c.draw, f"{int(row['rank'])}. {label_for(row)}", c.font(21), c.u(x0 - label_x - 34))
        c.text((label_x, y + 21), label, c.font(21, "semibold" if is_s8 else "regular"), theme["accent"] if is_s8 else theme["ink"], anchor="lm")
        c.rectangle((x0, y, x0 + width, y + bar_h), theme["accent"] if is_s8 else theme["bar"])
        c.text((x0 + width + 14, y + 21), f"{fmt(value)}" + (" mln" if is_s8 else ""), c.font(22, "bold" if is_s8 else "regular"), theme["accent"] if is_s8 else theme["muted"], anchor="lm")
    c.text((x0 + plot_w / 2, bottom + 62), "Milioni di passeggeri annui", c.font(23), theme["ink"], anchor="mm")
    footer(c, theme)
    c.save_png(out)


def make_contact_sheet(paths: list[Path]) -> Path:
    thumb_w, thumb_h = 520, 355
    pad = 28
    label_h = 70
    cols = 2
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (thumb_w + pad) + pad, rows * (thumb_h + label_h + pad) + pad), "#F5F6F4")
    draw = ImageDraw.Draw(sheet)
    f_title = font(24, "bold")
    f_small = font(17)
    for i, path in enumerate(paths):
        col = i % cols
        row = i // cols
        x = pad + col * (thumb_w + pad)
        y = pad + row * (thumb_h + label_h + pad)
        with Image.open(path) as img:
            img = img.convert("RGB")
            img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            sheet.paste(img, (x + (thumb_w - img.width) // 2, y + (thumb_h - img.height) // 2))
        draw.rectangle((x, y, x + thumb_w, y + thumb_h), outline="#D6DAD6", width=1)
        draw.text((x, y + thumb_h + 14), f"{i + 1}. {path.stem}", font=f_title, fill="#202124")
        draw.text((x, y + thumb_h + 44), shorten(path.name, width=58, placeholder="..."), font=f_small, fill="#667085")
    out = OUT_DIR / "00_contact_sheet_modelli_seri_top20.png"
    sheet.save(out, "PNG", optimize=True)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_excel(DATA_PATH, sheet_name="Top20").sort_values("rank").reset_index(drop=True)

    paths = []
    p = OUT_DIR / "01_report_neutro_top20.png"
    draw_full_bar(
        df,
        THEMES["neutral"],
        p,
        "La S8 è al 4° posto tra le linee locali più frequentate",
        "Classifica per passeggeri annui. Evidenza sulla S8, contesto in scala neutra.",
    )
    paths.append(p)

    p = OUT_DIR / "02_report_compatto_top20.png"
    draw_split_top_context(df, THEMES["report"], p)
    paths.append(p)

    p = OUT_DIR / "03_ft_sobrio_top20.png"
    draw_full_bar(
        df,
        THEMES["ft_serious"],
        p,
        "La S8 è tra le prime linee locali italiane per passeggeri",
        "Trattamento editoriale sobrio; nessun colore di linea salvo l'evidenza principale.",
        annotate=False,
    )
    paths.append(p)

    p = OUT_DIR / "04_monocromatico_top20.png"
    draw_monochrome(df, THEMES["neutral"], p)
    paths.append(p)

    contact = make_contact_sheet(paths)
    print(contact)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()

from __future__ import annotations

import re
import sys
from pathlib import Path
from textwrap import shorten

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "grafici_sleek"))

from chart_style import Canvas, PALETTE, blend, fit_text, luminance, shade  # noqa: E402


DATA_PATH = ROOT / "linee" / "top 20 italia" / "base_dati_top20_linee_ferroviarie_nonAV_italia_colori_finali_tilo_blu_ticino.xlsx"
OUT_DIR = ROOT / "grafici_rifatti_v01" / "top20_linee_modelli"

W, H = 2200, 1500
LOMBARD_LINES = {"S1", "S5", "S6", "S8", "S9", "S11", "S13", "RE6", "RE80"}
MAX_X = 22.0


THEMES = {
    "bbc": {
        "paper": "#F7F4EF",
        "ink": "#1D1D1B",
        "muted": "#5F6770",
        "grid": "#D9D5CD",
        "accent": "#B00020",
        "s8": "#E75B7C",
        "s8_soft": "#F9D6DF",
        "neutral": "#C8CAC8",
    },
    "ft": {
        "paper": "#FFF1E5",
        "ink": "#262A2E",
        "muted": "#6E625A",
        "grid": "#D8C8B8",
        "accent": "#0F6B6E",
        "s8": "#C85C80",
        "s8_soft": "#F3CBD6",
        "neutral": "#D7CEC4",
    },
    "civic": {
        "paper": "#F5F7F2",
        "ink": "#20302C",
        "muted": "#63746E",
        "grid": "#D8DED8",
        "accent": "#1E8A7A",
        "s8": "#C64F78",
        "s8_soft": "#F4D2DC",
        "neutral": "#D5DAD6",
    },
    "night": {
        "paper": "#172126",
        "ink": "#F3F1E8",
        "muted": "#AAB7B7",
        "grid": "#314046",
        "accent": "#8DD3C7",
        "s8": "#FF8DA8",
        "s8_soft": "#5B3340",
        "neutral": "#5B686D",
    },
    "poster": {
        "paper": "#FFFFFF",
        "ink": "#18222B",
        "muted": "#667085",
        "grid": "#E1E5E1",
        "accent": "#F79336",
        "s8": "#A75873",
        "s8_soft": "#F8D8DD",
        "neutral": "#D8DDD9",
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


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
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


def source_line() -> str:
    return "Fonte: elaborazione su dati Trenord, Cotral, Trenitalia e Regioni. Valori in milioni di passeggeri annui, 2024-2025."


def line_color(row, theme: dict, use_real_colors: bool = True) -> str:
    code = str(row["line_code"])
    if code == "S8":
        return theme["s8"]
    if use_real_colors and code in LOMBARD_LINES:
        return str(row["color_hex"])
    return theme["neutral"]


def draw_base_header(c: Canvas, theme: dict, kicker: str, title: str, subtitle: str):
    c.text((110, 105), kicker, c.font(26, "semibold"), theme["accent"])
    c.text((110, 172), title, c.font(58, "bold"), theme["ink"])
    c.text((110, 234), subtitle, c.font(29, "regular"), theme["muted"])


def draw_footer(c: Canvas, theme: dict, y: int):
    c.line((110, y - 25, W - 110, y - 25), theme["grid"], width=1)
    c.text((110, y + 4), source_line(), c.font(20, "regular"), theme["muted"])


def variant_01_bbc(df: pd.DataFrame) -> Path:
    theme = THEMES["bbc"]
    c = Canvas(W, H, theme["paper"], scale=2)
    draw_base_header(
        c,
        theme,
        "Modello 1 · stile giornalistico BBC-like",
        "La S8 è 4ª tra le linee locali più usate in Italia",
        "Le linee lombarde sono colorate; il resto resta in grigio per dare contesto senza rumore.",
    )
    x0, y0, plot_w, row_h, bar_h = 700, 325, 1240, 49, 30
    label_x = 125
    bottom = y0 + len(df) * row_h + 34
    for tick in [0, 5, 10, 15, 20]:
        x = x0 + tick / MAX_X * plot_w
        c.line((x, y0 - 18, x, bottom - 20), theme["grid"], width=1)
        c.text((x, bottom + 21), str(tick), c.font(21), theme["muted"], anchor="mm")
    for _, row in df.iterrows():
        i = int(row["rank"]) - 1
        y = y0 + i * row_h
        value = float(row["central_mln"])
        width = value / MAX_X * plot_w
        code = str(row["line_code"])
        color = line_color(row, theme, True)
        text_color = theme["s8"] if code == "S8" else theme["ink"]
        label = fit_text(c.draw, f"{int(row['rank'])}. {label_for(row)}", c.font(22), c.u(x0 - label_x - 34))
        c.text((label_x, y + 24), label, c.font(22, "semibold" if code == "S8" else "regular"), text_color, anchor="lm")
        if code == "S8":
            c.rounded((x0 - 8, y - 4, x0 + width + 8, y + bar_h + 4), 4, theme["s8_soft"], outline=theme["s8"], width=4)
            c.rounded((x0, y + 5, x0 + width, y + bar_h - 5), 3, color)
            c.text((x0 + width + 22, y + 21), f"{fmt(value)} mln  ← 4ª", c.font(28, "bold"), theme["s8"], anchor="lm")
        else:
            c.rounded((x0, y, x0 + width, y + bar_h), 2, color)
            c.text((x0 + width + 15, y + 21), fmt(value), c.font(22, "semibold"), theme["ink"], anchor="lm")
    c.text((x0 + plot_w / 2, bottom + 65), "Milioni di passeggeri annui", c.font(24), theme["ink"], anchor="mm")
    draw_footer(c, theme, H - 118)
    out = OUT_DIR / "01_bbc_like_ranking_top20.png"
    c.save_png(out)
    return out


def variant_02_ft_lollipop(df: pd.DataFrame) -> Path:
    theme = THEMES["ft"]
    c = Canvas(W, H, theme["paper"], scale=2)
    draw_base_header(
        c,
        theme,
        "Modello 2 · lollipop editoriale",
        "Una classifica leggibile anche da lontano",
        "Il punto finale porta il valore: meno inchiostro delle barre, stessa scala e stesso dato.",
    )
    x0, y0, plot_w, row_h = 740, 325, 1180, 50
    label_x = 125
    bottom = y0 + len(df) * row_h + 35
    for tick in [0, 5, 10, 15, 20]:
        x = x0 + tick / MAX_X * plot_w
        c.line((x, y0 - 18, x, bottom - 22), theme["grid"], width=1)
        c.text((x, bottom + 20), str(tick), c.font(21), theme["muted"], anchor="mm")
    for _, row in df.iterrows():
        i = int(row["rank"]) - 1
        y = y0 + i * row_h + 17
        value = float(row["central_mln"])
        x = x0 + value / MAX_X * plot_w
        code = str(row["line_code"])
        color = line_color(row, theme, True)
        if code not in LOMBARD_LINES and code != "S8":
            color = theme["neutral"]
        label_color = theme["s8"] if code == "S8" else theme["ink"]
        label = fit_text(c.draw, f"{int(row['rank'])}. {label_for(row)}", c.font(22), c.u(x0 - label_x - 45))
        c.text((label_x, y + 7), label, c.font(22, "semibold" if code == "S8" else "regular"), label_color, anchor="lm")
        c.line((x0, y, x, y), color if code == "S8" else blend(color, theme["paper"], 0.55), width=5 if code == "S8" else 3)
        radius = 13 if code == "S8" else 8
        c.rounded((x - radius, y - radius, x + radius, y + radius), radius, color, outline=theme["paper"], width=2)
        c.text((x + 22, y + 7), f"{fmt(value)}" + (" mln" if code == "S8" else ""), c.font(28 if code == "S8" else 21, "bold" if code == "S8" else "semibold"), label_color, anchor="lm")
    c.text((x0 + plot_w / 2, bottom + 64), "Milioni di passeggeri annui", c.font(24), theme["ink"], anchor="mm")
    draw_footer(c, theme, H - 118)
    out = OUT_DIR / "02_ft_like_lollipop_top20.png"
    c.save_png(out)
    return out


def variant_03_focus_number(df: pd.DataFrame) -> Path:
    theme = THEMES["civic"]
    c = Canvas(W, H, theme["paper"], scale=2)
    s8 = df[df["line_code"] == "S8"].iloc[0]
    draw_base_header(
        c,
        theme,
        "Modello 3 · apertura divulgativa",
        "La S8 non è una linea minore",
        "Prima il messaggio, poi il confronto: utile come slide di apertura del blocco dati.",
    )
    c.text((118, 455), "4ª", c.font(170, "bold"), theme["s8"])
    c.text((125, 650), "linea locale", c.font(48, "bold"), theme["ink"])
    c.text((125, 708), "più usata in Italia", c.font(48, "bold"), theme["ink"])
    c.line((125, 770, 570, 770), theme["grid"], width=3)
    c.text((125, 862), f"{fmt(float(s8['central_mln']))} mln", c.font(86, "bold"), theme["accent"])
    c.text((130, 915), "passeggeri annui", c.font(31), theme["muted"])
    c.text((130, 990), "Nel 2019 era fuori dalla Top 20.", c.font(31, "semibold"), theme["s8"])

    x0, y0, plot_w, row_h, bar_h = 760, 370, 1160, 56, 34
    top = df.head(10)
    for tick in [0, 5, 10, 15, 20]:
        x = x0 + tick / MAX_X * plot_w
        c.line((x, y0 - 18, x, y0 + len(top) * row_h - 9), theme["grid"], width=1)
    for _, row in top.iterrows():
        i = int(row["rank"]) - 1
        y = y0 + i * row_h
        value = float(row["central_mln"])
        width = value / MAX_X * plot_w
        code = str(row["line_code"])
        color = line_color(row, theme, True)
        if code not in LOMBARD_LINES and code != "S8":
            color = theme["neutral"]
        label_color = theme["s8"] if code == "S8" else theme["ink"]
        c.text((x0 - 30, y + 24), f"{int(row['rank'])}. {str(row['line_code'])}", c.font(23, "bold" if code == "S8" else "regular"), label_color, anchor="rm")
        c.rounded((x0, y, x0 + width, y + bar_h), 3, color)
        c.text((x0 + width + 16, y + 24), fmt(value), c.font(23, "bold" if code == "S8" else "semibold"), label_color, anchor="lm")
    c.text((x0, y0 + len(top) * row_h + 58), "Prime 10 linee della classifica, milioni di passeggeri annui", c.font(24), theme["muted"])
    draw_footer(c, theme, H - 118)
    out = OUT_DIR / "03_focus_numero_top10.png"
    c.save_png(out)
    return out


def variant_04_dark_stage(df: pd.DataFrame) -> Path:
    theme = THEMES["night"]
    c = Canvas(W, H, theme["paper"], scale=2)
    draw_base_header(
        c,
        theme,
        "Modello 4 · serata divulgativa / schermo",
        "Sul palco: la S8 è già tra le grandi linee locali",
        "Versione scura, pensata per proiezione: alto contrasto e pochi elementi decorativi.",
    )
    x0, y0, plot_w, row_h, bar_h = 675, 335, 1245, 49, 31
    label_x = 125
    bottom = y0 + len(df) * row_h + 35
    for tick in [0, 5, 10, 15, 20]:
        x = x0 + tick / MAX_X * plot_w
        c.line((x, y0 - 15, x, bottom - 25), theme["grid"], width=1)
        c.text((x, bottom + 20), str(tick), c.font(21), theme["muted"], anchor="mm")
    for _, row in df.iterrows():
        i = int(row["rank"]) - 1
        y = y0 + i * row_h
        value = float(row["central_mln"])
        width = value / MAX_X * plot_w
        code = str(row["line_code"])
        color = line_color(row, theme, True)
        if code not in LOMBARD_LINES and code != "S8":
            color = theme["neutral"]
        label = fit_text(c.draw, f"{int(row['rank'])}. {label_for(row)}", c.font(21), c.u(x0 - label_x - 30))
        label_color = theme["s8"] if code == "S8" else theme["ink"]
        c.text((label_x, y + 22), label, c.font(21, "semibold" if code == "S8" else "regular"), label_color, anchor="lm")
        if code == "S8":
            c.rounded((x0 - 6, y - 4, x0 + width + 6, y + bar_h + 4), 5, theme["s8_soft"], outline=theme["s8"], width=4)
        c.rounded((x0, y, x0 + width, y + bar_h), 3, color)
        c.text((x0 + width + 16, y + 22), fmt(value), c.font(22, "bold" if code == "S8" else "semibold"), label_color, anchor="lm")
    c.text((x0 + plot_w / 2, bottom + 65), "Milioni di passeggeri annui", c.font(24), theme["ink"], anchor="mm")
    draw_footer(c, theme, H - 118)
    out = OUT_DIR / "04_dark_projection_top20.png"
    c.save_png(out)
    return out


def variant_05_poster_bands(df: pd.DataFrame) -> Path:
    theme = THEMES["poster"]
    c = Canvas(W, H, theme["paper"], scale=2)
    draw_base_header(
        c,
        theme,
        "Modello 5 · poster pulito",
        "Le linee lombarde entrano nel gruppo di testa",
        "Le bande separano il podio, la S8 e il resto: più storytelling, stessa misura.",
    )
    x0, y0, plot_w, row_h, bar_h = 760, 340, 1100, 50, 28
    label_x = 145
    bands = [(y0 - 18, y0 + 3 * row_h - 4, "#FFF7EB", "podio"), (y0 + 3 * row_h - 4, y0 + 4 * row_h + 2, "#FFF0F4", "S8"), (y0 + 4 * row_h + 2, y0 + len(df) * row_h - 8, "#F8FAF8", "contesto")]
    for y1, y2, color, _ in bands:
        c.rectangle((85, y1, W - 135, y2), color)
    for tick in [0, 5, 10, 15, 20]:
        x = x0 + tick / MAX_X * plot_w
        c.line((x, y0 - 15, x, y0 + len(df) * row_h - 20), theme["grid"], width=1)
    for _, row in df.iterrows():
        i = int(row["rank"]) - 1
        y = y0 + i * row_h
        value = float(row["central_mln"])
        width = value / MAX_X * plot_w
        code = str(row["line_code"])
        color = line_color(row, theme, True)
        if code not in LOMBARD_LINES and code != "S8":
            color = theme["neutral"]
        label = fit_text(c.draw, f"{int(row['rank'])}. {label_for(row)}", c.font(22), c.u(x0 - label_x - 35))
        label_color = theme["s8"] if code == "S8" else theme["ink"]
        c.text((label_x, y + 20), label, c.font(22, "semibold" if code == "S8" else "regular"), label_color, anchor="lm")
        c.rounded((x0, y, x0 + width, y + bar_h), 14, color)
        c.text((x0 + width + 15, y + 20), fmt(value), c.font(22, "bold" if code == "S8" else "semibold"), label_color, anchor="lm")
    c.rounded((1885, y0 + 3 * row_h - 12, 2075, y0 + 4 * row_h + 22), 18, "#FFFFFF", outline=theme["s8"], width=2)
    c.text((1905, y0 + 3 * row_h + 33), "S8", c.font(42, "bold"), theme["s8"])
    c.text((1905, y0 + 3 * row_h + 72), "4ª in Italia", c.font(24, "semibold"), theme["s8"])
    c.text((x0 + plot_w / 2, y0 + len(df) * row_h + 52), "Milioni di passeggeri annui", c.font(24), theme["ink"], anchor="mm")
    draw_footer(c, theme, H - 118)
    out = OUT_DIR / "05_poster_bande_top20.png"
    c.save_png(out)
    return out


def make_contact_sheet(paths: list[Path]) -> Path:
    thumb_w, thumb_h = 520, 355
    pad = 28
    label_h = 70
    cols = 2
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (thumb_w + pad) + pad, rows * (thumb_h + label_h + pad) + pad), "#F4F5F2")
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
        draw.rectangle((x, y, x + thumb_w, y + thumb_h), outline="#D8DED7", width=1)
        draw.text((x, y + thumb_h + 14), f"{i + 1}. {path.stem}", font=f_title, fill="#1F2933")
        draw.text((x, y + thumb_h + 44), shorten(path.name, width=58, placeholder="..."), font=f_small, fill="#667085")
    out = OUT_DIR / "00_contact_sheet_modelli_top20.png"
    sheet.save(out, "PNG", optimize=True)
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_excel(DATA_PATH, sheet_name="Top20").sort_values("rank").reset_index(drop=True)
    paths = [
        variant_01_bbc(df),
        variant_02_ft_lollipop(df),
        variant_03_focus_number(df),
        variant_04_dark_stage(df),
        variant_05_poster_bands(df),
    ]
    contact = make_contact_sheet(paths)
    print(contact)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path
import re

import pandas as pd

from chart_style import (
    Canvas,
    PALETTE,
    blend,
    fit_text,
    luminance,
    shade,
    svg_end,
    svg_line,
    svg_rect,
    svg_start,
    svg_text,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "linee" / "top 20 italia" / "base_dati_top20_linee_ferroviarie_nonAV_italia_colori_finali_tilo_blu_ticino.xlsx"
OUT_DIR = ROOT / "linee" / "top 20 italia"
PNG_PATH = OUT_DIR / "top20_linee_ferroviarie_nonAV_S8_rilievo_sleek.png"
SVG_PATH = OUT_DIR / "top20_linee_ferroviarie_nonAV_S8_rilievo_sleek.svg"

W, H = 2400, 1700
LEFT = 118
LABEL_X = 128
PLOT_X = 690
PLOT_W = 1290
TOP_Y = 348
ROW_H = 54
BAR_H = 34
MAX_X = 22.0

LOMBARD_LINES = {"S1", "S5", "S6", "S8", "S9", "S11", "S13", "RE6", "RE80"}


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


def fmt_mln(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def bar_colors(row) -> tuple[str, str, str]:
    code = str(row["line_code"])
    if code == "S8":
        return PALETTE["s8"], PALETTE["s8_dark"], PALETTE["s8_dark"]
    if code in LOMBARD_LINES:
        base = str(row["color_hex"])
        fill = base
        outline = shade(base, -0.14, 0.02) if luminance(base) > 0.55 else shade(base, -0.04, 0.0)
        text = PALETTE["ink"]
        return fill, outline, text
    return PALETTE["neutral_bar"], PALETTE["neutral_bar_dark"], "#3C4541"


def status_label(status: str) -> str:
    mapping = {"R": "dato ufficiale", "S": "stima", "L25": "Lombardia 2025", "R/S": "dato/stima"}
    return mapping.get(str(status), str(status))


def display_label(row) -> str:
    code = str(row["line_code"])
    route = clean_route(code, row["line_name"])
    if code in {"Roma-Viterbo", "Firenze-Pistoia-Lucca", "Bologna-Piacenza-Milano", "Padova-Venezia"}:
        return route
    return f"{code} · {route}"


def draw_chart_png(df: pd.DataFrame):
    c = Canvas(W, H, PALETTE["paper"], scale=2)

    f_eyebrow = c.font(24, "semibold")
    f_title = c.font(57, "bold")
    f_subtitle = c.font(29, "regular")
    f_axis = c.font(22, "regular")
    f_rank = c.font(23, "bold")
    f_label_route = c.font(23, "regular")
    f_value = c.font(24, "semibold")
    f_card_big = c.font(78, "bold")
    f_card_mid = c.font(30, "bold")
    f_card_text = c.font(25, "regular")
    f_footer = c.font(20, "regular")

    c.rounded((72, 64, W - 72, H - 72), 28, PALETTE["panel"], outline="#E6EAE5", width=1)

    c.text((LEFT, 122), "Passeggeri annui 2024-2025 | top 20 linee locali non AV", f_eyebrow, PALETTE["muted"])
    c.text((LEFT, 178), "La S8 è la 4ª linea locale più usata in Italia", f_title, PALETTE["ink"])
    c.text((LEFT, 247), "14,8 milioni di passeggeri annui sulla Lecco - Milano. Valori in milioni.", f_subtitle, PALETTE["muted"])

    legend_x = 1622
    c.rounded((legend_x, 108, legend_x + 614, 194), 18, "#F9FAF8", outline="#E2E7E1", width=1)
    c.rounded((legend_x + 28, 137, legend_x + 70, 158), 10, "#F79336")
    c.text((legend_x + 84, 158), "linee lombarde/TILO colorate", c.font(21, "regular"), PALETTE["ink"], anchor="lm")
    c.rounded((legend_x + 362, 137, legend_x + 404, 158), 10, PALETTE["neutral_bar"])
    c.text((legend_x + 418, 158), "altre linee", c.font(21, "regular"), PALETTE["ink"], anchor="lm")

    plot_bottom = TOP_Y + ROW_H * len(df) + 16
    for tick in [0, 5, 10, 15, 20]:
        x = PLOT_X + (tick / MAX_X) * PLOT_W
        c.line((x, TOP_Y - 26, x, plot_bottom), PALETTE["grid"], width=1)
        c.text((x, plot_bottom + 42), str(tick), f_axis, PALETTE["muted"], anchor="mm")
    c.text((PLOT_X + PLOT_W / 2, plot_bottom + 86), "Milioni di passeggeri annui", c.font(25, "regular"), PALETTE["ink"], anchor="mm")

    for _, row in df.iterrows():
        idx = int(row["rank"]) - 1
        y = TOP_Y + idx * ROW_H
        cy = y + BAR_H / 2
        value = float(row["central_mln"])
        bar_w = (value / MAX_X) * PLOT_W
        fill, outline, value_color = bar_colors(row)
        code = str(row["line_code"])

        rank_label = f'{int(row["rank"])}.'
        label = fit_text(c.draw, display_label(row), f_label_route, c.u(PLOT_X - LABEL_X - 76))

        label_color = PALETTE["s8_dark"] if code == "S8" else PALETTE["ink"]
        c.text((LABEL_X + 28, cy + 7), rank_label, f_rank, label_color, anchor="rm")
        c.text((LABEL_X + 58, cy + 7), label, f_label_route, label_color, anchor="lm")

        if code == "S8":
            c.rounded((PLOT_X - 6, y - 4, PLOT_X + bar_w + 6, y + BAR_H + 4), 5, blend(PALETTE["s8"], alpha=0.12), outline=PALETTE["s8_dark"], width=5)
            c.rounded((PLOT_X, y + 4, PLOT_X + bar_w, y + BAR_H - 4), 3, PALETTE["s8"], outline=None)
            label = f"{fmt_mln(value)} mln  ← 4ª in Italia"
            c.text((PLOT_X + bar_w + 24, cy + 8), label, c.font(30, "bold"), PALETTE["s8_dark"], anchor="lm")
        else:
            c.rounded((PLOT_X, y, PLOT_X + bar_w, y + BAR_H), 3, fill, outline=None)
            if code in LOMBARD_LINES:
                c.rectangle((PLOT_X, y, PLOT_X + 8, y + BAR_H), fill=outline)
            c.text((PLOT_X + bar_w + 16, cy + 7), fmt_mln(value), f_value, value_color, anchor="lm")

    card_x, card_y, card_w, card_h = 1998, 516, 300, 380
    c.rounded((card_x + 8, card_y + 10, card_x + card_w + 8, card_y + card_h + 10), 24, PALETTE["shadow"])
    c.rounded((card_x, card_y, card_x + card_w, card_y + card_h), 24, "#FFF4F5", outline="#F0B8C5", width=2)
    c.text((card_x + 28, card_y + 76), "4ª", f_card_big, PALETTE["s8_dark"])
    c.text((card_x + 28, card_y + 164), "linea in Italia", f_card_mid, PALETTE["s8_dark"])
    c.line((card_x + 28, card_y + 200, card_x + card_w - 28, card_y + 200), "#F1C4CC", width=2)
    c.text((card_x + 28, card_y + 252), "14,8 mln", c.font(44, "bold"), PALETTE["ink"])
    c.text((card_x + 28, card_y + 294), "passeggeri annui", f_card_text, PALETTE["muted"])
    c.rounded((card_x + 28, card_y + 336, card_x + card_w - 28, card_y + 372), 12, "#FFFFFF", outline="#F0CDD3", width=1)
    c.text((card_x + card_w / 2, card_y + 360), "nel 2019: fuori top 20", c.font(20, "semibold"), PALETTE["s8_dark"], anchor="mm")

    note_y = H - 118
    c.line((LEFT, note_y - 24, W - LEFT, note_y - 24), "#E6EAE5", width=1)
    source = (
        "Fonte: elaborazione su dati Trenord, Cotral, Trenitalia e Regioni. "
        "Per la Lombardia: campagne di frequentazione 2025 (maggio, luglio, novembre). "
        "R = dato ufficiale; S = stima; L25 = dato Lombardia 2025."
    )
    source = fit_text(c.draw, source, f_footer, c.u(W - 2 * LEFT))
    c.text((LEFT, note_y + 4), source, f_footer, PALETTE["muted"])

    c.save_png(PNG_PATH)


def draw_chart_svg(df: pd.DataFrame):
    svg = svg_start(W, H, PALETTE["paper"])
    svg.append(svg_rect(72, 64, W - 144, H - 144, PALETTE["panel"], rx=28, stroke="#E6EAE5"))
    svg.append(svg_text(LEFT, 122, "Passeggeri annui 2024-2025 | top 20 linee locali non AV", 24, PALETTE["muted"], "semibold"))
    svg.append(svg_text(LEFT, 178, "La S8 è la 4ª linea locale più usata in Italia", 57, PALETTE["ink"], "bold"))
    svg.append(svg_text(LEFT, 247, "14,8 milioni di passeggeri annui sulla Lecco - Milano. Valori in milioni.", 29, PALETTE["muted"]))

    legend_x = 1622
    svg.append(svg_rect(legend_x, 108, 614, 86, "#F9FAF8", rx=18, stroke="#E2E7E1"))
    svg.append(svg_rect(legend_x + 28, 137, 42, 21, "#F79336", rx=10))
    svg.append(svg_text(legend_x + 84, 158, "linee lombarde/TILO colorate", 21, PALETTE["ink"]))
    svg.append(svg_rect(legend_x + 362, 137, 42, 21, PALETTE["neutral_bar"], rx=10))
    svg.append(svg_text(legend_x + 418, 158, "altre linee", 21, PALETTE["ink"]))

    plot_bottom = TOP_Y + ROW_H * len(df) + 16
    for tick in [0, 5, 10, 15, 20]:
        x = PLOT_X + (tick / MAX_X) * PLOT_W
        svg.append(svg_line(x, TOP_Y - 26, x, plot_bottom, PALETTE["grid"]))
        svg.append(svg_text(x, plot_bottom + 48, str(tick), 22, PALETTE["muted"], anchor="middle"))
    svg.append(svg_text(PLOT_X + PLOT_W / 2, plot_bottom + 92, "Milioni di passeggeri annui", 25, PALETTE["ink"], anchor="middle"))

    temp_canvas = Canvas(W, H, PALETTE["paper"], scale=1)
    route_font = temp_canvas.font(22, "regular")
    for _, row in df.iterrows():
        idx = int(row["rank"]) - 1
        y = TOP_Y + idx * ROW_H
        cy = y + BAR_H / 2
        value = float(row["central_mln"])
        bar_w = (value / MAX_X) * PLOT_W
        fill, outline, value_color = bar_colors(row)
        code = str(row["line_code"])
        rank_label = f'{int(row["rank"])}.'
        label = fit_text(temp_canvas.draw, display_label(row), route_font, PLOT_X - LABEL_X - 76)
        label_color = PALETTE["s8_dark"] if code == "S8" else PALETTE["ink"]

        svg.append(svg_text(LABEL_X + 28, cy + 8, rank_label, 23, label_color, "bold", anchor="end"))
        svg.append(svg_text(LABEL_X + 58, cy + 8, label, 23, label_color))
        if code == "S8":
            svg.append(svg_rect(PLOT_X - 6, y - 4, bar_w + 12, BAR_H + 8, blend(PALETTE["s8"], alpha=0.12), rx=5, stroke=PALETTE["s8_dark"], sw=5))
            svg.append(svg_rect(PLOT_X, y + 4, bar_w, BAR_H - 8, PALETTE["s8"], rx=3))
            svg.append(svg_text(PLOT_X + bar_w + 24, cy + 10, f"{fmt_mln(value)} mln  ← 4ª in Italia", 30, PALETTE["s8_dark"], "bold"))
        else:
            svg.append(svg_rect(PLOT_X, y, bar_w, BAR_H, fill, rx=3))
            if code in LOMBARD_LINES:
                svg.append(svg_rect(PLOT_X, y, 8, BAR_H, outline))
            svg.append(svg_text(PLOT_X + bar_w + 16, cy + 8, fmt_mln(value), 24, value_color, "semibold"))

    card_x, card_y, card_w, card_h = 1998, 516, 300, 380
    svg.append(svg_rect(card_x + 8, card_y + 10, card_w, card_h, PALETTE["shadow"], rx=24))
    svg.append(svg_rect(card_x, card_y, card_w, card_h, "#FFF4F5", rx=24, stroke="#F0B8C5", sw=2))
    svg.append(svg_text(card_x + 28, card_y + 76, "4ª", 78, PALETTE["s8_dark"], "bold"))
    svg.append(svg_text(card_x + 28, card_y + 164, "linea in Italia", 30, PALETTE["s8_dark"], "bold"))
    svg.append(svg_line(card_x + 28, card_y + 200, card_x + card_w - 28, card_y + 200, "#F1C4CC", sw=2))
    svg.append(svg_text(card_x + 28, card_y + 252, "14,8 mln", 44, PALETTE["ink"], "bold"))
    svg.append(svg_text(card_x + 28, card_y + 294, "passeggeri annui", 25, PALETTE["muted"]))
    svg.append(svg_rect(card_x + 28, card_y + 336, card_w - 56, 36, "#FFFFFF", rx=12, stroke="#F0CDD3"))
    svg.append(svg_text(card_x + card_w / 2, card_y + 360, "nel 2019: fuori top 20", 20, PALETTE["s8_dark"], "semibold", anchor="middle"))

    note_y = H - 118
    svg.append(svg_line(LEFT, note_y - 24, W - LEFT, note_y - 24, "#E6EAE5"))
    source = (
        "Fonte: elaborazione su dati Trenord, Cotral, Trenitalia e Regioni. "
        "Per la Lombardia: campagne di frequentazione 2025 (maggio, luglio, novembre). "
        "R = dato ufficiale; S = stima; L25 = dato Lombardia 2025."
    )
    svg.append(svg_text(LEFT, note_y + 4, source, 20, PALETTE["muted"]))
    svg.append(svg_end())
    SVG_PATH.write_text("\n".join(svg), encoding="utf-8")


def main():
    df = pd.read_excel(DATA_PATH, sheet_name="Top20")
    df = df.sort_values("rank").reset_index(drop=True)
    draw_chart_png(df)
    draw_chart_svg(df)
    print(PNG_PATH)
    print(SVG_PATH)


if __name__ == "__main__":
    main()

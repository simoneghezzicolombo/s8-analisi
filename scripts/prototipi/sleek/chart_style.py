from __future__ import annotations

from html import escape
from pathlib import Path
import colorsys

from PIL import Image, ImageDraw, ImageFont


PALETTE = {
    "paper": "#F7F8F6",
    "panel": "#FFFFFF",
    "ink": "#1F2933",
    "muted": "#667085",
    "soft": "#EEF1EE",
    "grid": "#DDE3DE",
    "axis": "#A8B0AA",
    "neutral_bar": "#D7DBD8",
    "neutral_bar_dark": "#AEB6B0",
    "s8": "#F8B1B0",
    "s8_dark": "#A75873",
    "shadow": "#D8DED7",
}


FONT_DIR = Path("C:/Windows/Fonts")
FONT_FILES = {
    "regular": [
        FONT_DIR / "segoeui.ttf",
        FONT_DIR / "arial.ttf",
    ],
    "semibold": [
        FONT_DIR / "seguisb.ttf",
        FONT_DIR / "segoeuib.ttf",
        FONT_DIR / "arialbd.ttf",
    ],
    "bold": [
        FONT_DIR / "segoeuib.ttf",
        FONT_DIR / "arialbd.ttf",
    ],
}


def _font_path(weight: str) -> Path | None:
    for path in FONT_FILES.get(weight, FONT_FILES["regular"]):
        if path.exists():
            return path
    return None


def load_font(size: int, weight: str = "regular", scale: int = 1) -> ImageFont.FreeTypeFont:
    path = _font_path(weight)
    if path is None:
        return ImageFont.load_default()
    return ImageFont.truetype(str(path), size * scale)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = str(value).strip().lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def blend(hex_color: str, background: str = "#FFFFFF", alpha: float = 0.25) -> str:
    fg = hex_to_rgb(hex_color)
    bg = hex_to_rgb(background)
    rgb = tuple(round(fg[i] * alpha + bg[i] * (1 - alpha)) for i in range(3))
    return rgb_to_hex(rgb)


def shade(hex_color: str, lightness_delta: float = 0.0, saturation_delta: float = 0.0) -> str:
    r, g, b = [c / 255 for c in hex_to_rgb(hex_color)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = min(1, max(0, l + lightness_delta))
    s = min(1, max(0, s + saturation_delta))
    nr, ng, nb = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex((round(nr * 255), round(ng * 255), round(nb * 255)))


def luminance(hex_color: str) -> float:
    channels = []
    for c in hex_to_rgb(hex_color):
        v = c / 255
        channels.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def fit_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width_px: int) -> str:
    if draw.textbbox((0, 0), text, font=font)[2] <= max_width_px:
        return text
    suffix = "..."
    low, high = 0, len(text)
    while low < high:
        mid = (low + high) // 2
        candidate = text[:mid].rstrip() + suffix
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width_px:
            low = mid + 1
        else:
            high = mid
    return text[: max(0, low - 1)].rstrip() + suffix


class Canvas:
    def __init__(self, width: int, height: int, background: str = PALETTE["paper"], scale: int = 2):
        self.width = width
        self.height = height
        self.scale = scale
        self.image = Image.new("RGB", (width * scale, height * scale), background)
        self.draw = ImageDraw.Draw(self.image)

    def u(self, value: float) -> int:
        return int(round(value * self.scale))

    def xy(self, values):
        return tuple(self.u(v) for v in values)

    def font(self, size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
        return load_font(size, weight, self.scale)

    def text(self, xy, text: str, font: ImageFont.ImageFont, fill: str, anchor: str | None = None):
        kwargs = {"font": font, "fill": fill}
        if anchor:
            kwargs["anchor"] = anchor
        self.draw.text(self.xy(xy), text, **kwargs)

    def line(self, xy, fill: str, width: int = 1):
        self.draw.line(self.xy(xy), fill=fill, width=self.u(width))

    def rectangle(self, xy, fill: str, outline: str | None = None, width: int = 1):
        self.draw.rectangle(self.xy(xy), fill=fill, outline=outline, width=self.u(width))

    def rounded(self, xy, radius: int, fill: str, outline: str | None = None, width: int = 1):
        self.draw.rounded_rectangle(self.xy(xy), radius=self.u(radius), fill=fill, outline=outline, width=self.u(width))

    def save_png(self, path: Path):
        image = self.image
        if self.scale != 1:
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        image.save(path, "PNG", optimize=True)


def svg_start(width: int, height: int, background: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{background}"/>',
        "<style>",
        "text{font-family:'Segoe UI',Arial,sans-serif;dominant-baseline:auto}",
        ".bold{font-weight:700}.semibold{font-weight:600}.regular{font-weight:400}",
        "</style>",
    ]


def svg_rect(x: float, y: float, w: float, h: float, fill: str, rx: float = 0, stroke: str | None = None, sw: float = 1) -> str:
    stroke_bits = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx:.1f}" fill="{fill}"{stroke_bits}/>'


def svg_line(x1: float, y1: float, x2: float, y2: float, stroke: str, sw: float = 1, dash: str | None = None) -> str:
    dash_bits = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{dash_bits}/>'


def svg_text(x: float, y: float, text: str, size: int, fill: str, weight: str = "regular", anchor: str = "start") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" class="{weight}">{escape(str(text))}</text>'


def svg_end() -> str:
    return "</svg>"

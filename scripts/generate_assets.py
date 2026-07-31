#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate profile banner + decorative activity graph (not account stats)."""

from __future__ import annotations

import hashlib
import math
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
POINTS = 28


def _seed_for(day: date) -> int:
    raw = ("Ashish8668-activity-" + day.isoformat()).encode()
    return int(hashlib.sha256(raw).hexdigest()[:8], 16)


def fake_series(today: date | None = None) -> tuple[list[date], list[float]]:
    today = today or date.today()
    dates = [today - timedelta(days=(POINTS - 1 - i)) for i in range(POINTS)]
    values: list[float] = []
    for i, d in enumerate(dates):
        seed = _seed_for(d)
        wave = (
            42
            + 28 * math.sin(i / 3.2)
            + 18 * math.cos(i / 5.1)
            + 12 * math.sin(i / 1.7 + (seed % 7) / 10)
            + (seed % 23)
        )
        values.append(max(8.0, min(98.0, wave)))
    return dates, values


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "segoeui.ttf",
        "arial.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate_banner(path: Path) -> None:
    w, h = 1200, 320
    img = Image.new("RGB", (w, h), "#0b1220")
    draw = ImageDraw.Draw(img, "RGBA")

    for cx, cy, r, color in (
        (980, 70, 120, (34, 211, 238, 28)),
        (1080, 230, 140, (52, 211, 153, 22)),
        (140, 250, 90, (56, 189, 248, 24)),
    ):
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(overlay).ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img, "RGBA")

    for y in range(64, h, 64):
        draw.line((0, y, w, y), fill=(148, 163, 184, 28), width=1)
    for x in range(160, w, 160):
        draw.line((x, 0, x, h), fill=(148, 163, 184, 28), width=1)

    for i, color in enumerate(((34, 211, 238), (56, 189, 248), (52, 211, 153))):
        draw.rectangle((i * 400, 0, (i + 1) * 400, 4), fill=color)

    draw.text((64, 58), "FULL STACK  |  AI / ML  |  BACKEND", font=_font(18), fill="#67e8f9")
    draw.text((64, 100), "Ashish Kamble", font=_font(52), fill="#f8fafc")
    draw.text(
        (64, 170),
        "Building production-ready systems with clean architecture",
        font=_font(22),
        fill="#cbd5e1",
    )
    draw.text((64, 230), "> shipping agents, APIs and scalable apps", font=_font(18), fill="#e2e8f0")
    draw.rectangle((500, 232, 510, 252), fill="#22d3ee")

    card = (760, 70, 1140, 250)
    draw.rounded_rectangle(card, radius=16, fill="#0b1324", outline="#1e293b", width=2)
    draw.ellipse((784, 88, 796, 100), fill="#f87171")
    draw.ellipse((804, 88, 816, 100), fill="#fbbf24")
    draw.ellipse((824, 88, 836, 100), fill="#34d399")
    mono = _font(16)
    lines = [
        ("const engineer = {", "#64748b"),
        ('  stack: ["MERN","AI","AWS"],', "#67e8f9"),
        ('  focus: "production systems",', "#86efac"),
        ('  mode: "ship fast, stay solid"', "#fda4af"),
        ("}", "#64748b"),
    ]
    y = 118
    for text, color in lines:
        draw.text((784, y), text, font=mono, fill=color)
        y += 24

    img.save(path, "PNG", optimize=True)


def generate_activity_png(path: Path, today: date | None = None) -> None:
    today = today or date.today()
    dates, values = fake_series(today)
    w, h = 900, 280
    pad_l, pad_r, pad_t, pad_b = 48, 24, 48, 44
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b

    def x_at(i: int) -> float:
        return pad_l + (i / (POINTS - 1)) * plot_w

    def y_at(v: float) -> float:
        return pad_t + plot_h - (v / 100.0) * plot_h

    img = Image.new("RGB", (w, h), "#0b1220")
    draw = ImageDraw.Draw(img, "RGBA")
    draw.text((pad_l, 14), "Build Pulse", font=_font(16), fill="#e2e8f0")
    draw.text(
        (w - pad_r, 16),
        "updated " + today.isoformat() + " | decorative",
        font=_font(11),
        fill="#64748b",
        anchor="ra",
    )
    draw.line((pad_l, pad_t, pad_l, pad_t + plot_h), fill="#1e293b")
    draw.line((pad_l, pad_t + plot_h, w - pad_r, pad_t + plot_h), fill="#1e293b")

    pts = [(x_at(i), y_at(v)) for i, v in enumerate(values)]
    area = [(pad_l, pad_t + plot_h)] + pts + [(x_at(POINTS - 1), pad_t + plot_h)]
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(overlay).polygon(area, fill=(34, 211, 238, 55))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    for i, v in enumerate(values):
        if i % 2:
            continue
        bx = x_at(i) - 4
        bh = (v / 100.0) * plot_h
        by = pad_t + plot_h - bh
        draw.rectangle((bx, by, bx + 8, pad_t + plot_h), fill="#164e63")

    for i in range(1, POINTS):
        draw.line([pts[i - 1], pts[i]], fill="#22d3ee", width=3)

    for i, _v in enumerate(values):
        if i % 4 == 0:
            r = 3
            draw.ellipse(
                (pts[i][0] - r, pts[i][1] - r, pts[i][0] + r, pts[i][1] + r),
                fill="#34d399",
            )

    label_idxs = list(range(0, POINTS, 4))
    if label_idxs[-1] != POINTS - 1:
        label_idxs.append(POINTS - 1)
    for i in label_idxs:
        draw.text(
            (x_at(i), h - 14),
            dates[i].strftime("%d %b"),
            font=_font(11),
            fill="#94a3b8",
            anchor="md",
        )

    img.save(path, "PNG", optimize=True)


def main() -> None:
    generate_banner(ROOT / "banner.png")
    generate_activity_png(ROOT / "activity-graph.png")
    print("Generated banner.png and activity-graph.png")


if __name__ == "__main__":
    main()

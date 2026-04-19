#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Composite minimal Reddit banner from existing Graphene creative PNG."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_REPO = Path(__file__).resolve().parent.parent
SRC = _REPO / "assets" / "banner-source.png"
OUT = _REPO / "banner-reddit-minimal.png"

# Output (Reddit link ad friendly)
OUT_W, OUT_H = 1200, 628

# Crop from source: graph-only (avoid headline bleed-in from original layout + top label)
CROP_LEFT_RATIO = 0.63
TOP_CROP = 118

# Typography
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

BG = (11, 14, 20)
WHITE = (245, 247, 250)
MUTED = (148, 163, 184)
TEAL = (45, 212, 191)
STANFORD = (140, 21, 21)
BERKELEY = (0, 50, 98)


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Missing source PNG: {SRC} (place your banner graphic there)")
    src = Image.open(SRC).convert("RGBA")
    w, h = src.size
    crop_x = int(w * CROP_LEFT_RATIO)
    graph = src.crop((crop_x, TOP_CROP, w, h))

    out = Image.new("RGB", (OUT_W, OUT_H), BG)

    margin_x = 44
    # Reserve left band for headline so the graph never paints over copy
    left_copy_end = 520
    graph_target_w = OUT_W - left_copy_end - 32
    graph_target_h = OUT_H - 48

    gw, gh = graph.size
    scale = min(graph_target_w / gw, graph_target_h / gh)
    new_w = max(1, int(gw * scale))
    new_h = max(1, int(gh * scale))
    graph_r = graph.resize((new_w, new_h), Image.Resampling.LANCZOS)

    gx = max(left_copy_end, OUT_W - new_w - 28)
    gy = (OUT_H - new_h) // 2
    out.paste(graph_r, (gx, gy), graph_r)

    draw = ImageDraw.Draw(out)
    font_head = ImageFont.truetype(FONT_BOLD, 40)
    font_small = ImageFont.truetype(FONT_REG, 17)
    font_url = ImageFont.truetype(FONT_BOLD, 22)

    headline = "Know what breaks\nbefore your users do."
    x = margin_x

    font_school = ImageFont.truetype(FONT_BOLD, 19)

    # Measure left block height for vertical centering
    line_h = []
    for line in headline.split("\n"):
        bbox = draw.textbbox((0, 0), line, font=font_head)
        line_h.append(bbox[3] - bbox[1] + 6)
    cred_h = 24  # Stanford | Berkeley only (no extra grey line)
    url_h = 28
    gap = 24
    block_h = sum(line_h) + gap + cred_h + gap + url_h
    y = max(56, (OUT_H - block_h) // 2)

    for line in headline.split("\n"):
        draw.text((x, y), line, fill=WHITE, font=font_head)
        bbox = draw.textbbox((0, 0), line, font=font_head)
        y += bbox[3] - bbox[1] + 6

    y += gap

    # Stanford | Berkeley (manual kerning via separate draws)
    s = "Stanford"
    mid = "  |  "
    b = "Berkeley"
    draw.text((x, y), s, fill=STANFORD, font=font_school)
    bx = x + draw.textlength(s, font=font_school)
    draw.text((bx, y), mid, fill=MUTED, font=font_small)
    bx += draw.textlength(mid, font=font_small)
    draw.text((bx, y), b, fill=BERKELEY, font=font_school)

    y += gap + 4
    draw.text((x, y), "trygraphene.dev", fill=TEAL, font=font_url)

    out.save(OUT, "PNG", optimize=True)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()

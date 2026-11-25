#!/usr/bin/env python3
"""Build-time renderer for the news-image-20261125 entry (round 2).

Draws entry.png at 1024x1024 with 2x supersampling, then downscales with
Lanczos. Deterministic: no randomness, no timestamps, fixed fonts.
Run: python3 render_image.py  (writes entry.png next to this file)
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SS = 2  # supersampling factor
W, H = 1024, 1024

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def S(v):
    return int(round(v * SS))


def font(path, size):
    return ImageFont.truetype(path, S(size))


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w (1024-space px)."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= S(max_w):
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, fnt, fill, max_w, max_lines, leading):
    """Draw wrapped text; returns number of lines drawn."""
    lines = wrap(draw, text, fnt, max_w)
    while len(lines) > max_lines:
        # shrink font by 1pt and re-wrap
        size = fnt.size // SS - 1
        if size < 11:
            lines = lines[:max_lines]
            break
        path = SANS_B if "Bold" in fnt.path and "Serif" not in fnt.path \
            else (SERIF_B if "Serif" in fnt.path else SANS)
        fnt = font(path, size)
        lines = wrap(draw, text, fnt, max_w)
    x, y = xy
    for ln in lines:
        draw.text((S(x), S(y)), ln, font=fnt, fill=fill)
        y += leading
    return len(lines)


def chip(draw, x, y, text, bg, fg="white"):
    """Small BEAT · REGION tag. Returns (w, h) in 1024-space."""
    f = font(SANS_B, 13)
    tw = draw.textlength(text, font=f) / SS
    pad_x, pad_y = 8, 4
    w, h = tw + 2 * pad_x, 13 + 2 * pad_y + 4
    draw.rectangle([S(x), S(y), S(x + w), S(y + h)], fill=bg)
    draw.text((S(x + pad_x), S(y + pad_y)), text, font=f, fill=fg)
    return w, h


def draw_mine(draw, cx, cy, r):
    """Naval mine: black spiked circle, fully below the water surface line."""
    draw.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], fill=(20, 20, 25))
    for k in range(8):
        a = math.pi * k / 4.0
        x1 = cx + (r - 2) * math.cos(a)
        y1 = cy + (r - 2) * math.sin(a)
        x2 = cx + (r + 7) * math.cos(a)
        y2 = cy + (r + 7) * math.sin(a)
        draw.line([S(x1), S(y1), S(x2), S(y2)], fill=(20, 20, 25), width=S(3))
        draw.ellipse([S(x2 - 2), S(y2 - 2), S(x2 + 2), S(y2 + 2)],
                     fill=(20, 20, 25))
    draw.ellipse([S(cx - r + 4), S(cy - r + 4), S(cx - r + 10), S(cy - r + 10)],
                 fill=(90, 100, 115))


def draw_tanker(draw, x, y, w, h, hull=(150, 40, 32), burning=False):
    """Side-view oil tanker floating on the surface line y+h."""
    deck = y + h * 0.42
    # hull
    draw.polygon([(S(x), S(deck)), (S(x + w), S(deck)),
                  (S(x + w - 8), S(y + h)), (S(x + 8), S(y + h))], fill=hull)
    draw.rectangle([S(x), S(deck - 6), S(x + w), S(deck)], fill=(210, 210, 205))
    # superstructure (stern, left)
    draw.rectangle([S(x + 8), S(deck - 26), S(x + 52), S(deck - 6)],
                   fill=(245, 245, 240))
    draw.rectangle([S(x + 14), S(deck - 20), S(x + 46), S(deck - 12)],
                   fill=(40, 90, 140))
    # funnel (bow side, right)
    draw.rectangle([S(x + w - 34), S(deck - 24), S(x + w - 18), S(deck - 6)],
                   fill=(200, 60, 40))
    # containers / tanks
    for i in range(3):
        cx0 = x + 60 + i * 34
        draw.ellipse([S(cx0), S(deck - 16), S(cx0 + 26), S(deck - 6)],
                     fill=(220, 225, 230))
    if burning:
        # flame above mid-deck
        fx = x + w * 0.55
        draw.polygon([(S(fx - 16), S(deck - 6)), (S(fx), S(deck - 52)),
                      (S(fx + 16), S(deck - 6))], fill=(255, 140, 0))
        draw.polygon([(S(fx - 9), S(deck - 6)), (S(fx), S(deck - 34)),
                      (S(fx + 9), S(deck - 6))], fill=(255, 220, 60))
        for i, (sx, sy, sr) in enumerate([(fx - 26, deck - 46, 10),
                                          (fx - 8, deck - 58, 12),
                                          (fx + 14, deck - 48, 9)]):
            draw.ellipse([S(sx - sr), S(sy - sr), S(sx + sr), S(sy + sr)],
                         fill=(120, 120, 125))


def draw_flag_eu(draw, x, y, w, h):
    draw.rectangle([S(x), S(y), S(x + w), S(y + h)], fill=(0, 51, 153))
    cx, cy = x + w / 2, y + h / 2
    for k in range(12):
        a = -math.pi / 2 + 2 * math.pi * k / 12
        px = cx + (w * 0.32) * math.cos(a)
        py = cy + (h * 0.32) * math.sin(a)
        draw.ellipse([S(px - 2), S(py - 2), S(px + 2), S(py + 2)],
                     fill=(255, 204, 0))


def draw_flag_id(draw, x, y, w, h):
    # thin outline so the white half stays visible on a white tile
    draw.rectangle([S(x), S(y), S(x + w), S(y + h / 2)], fill=(200, 20, 30))
    draw.rectangle([S(x), S(y + h / 2), S(x + w), S(y + h)], fill=(255, 255, 255))
    draw.rectangle([S(x), S(y), S(x + w), S(y + h)], outline=(150, 150, 155),
                   width=S(2))


def draw_flag_au(draw, x, y, w, h):
    """Australia: blue ensign, Union Jack canton, Southern Cross + big star."""
    draw.rectangle([S(x), S(y), S(x + w), S(y + h)], fill=(0, 0, 139))
    cw, ch = w / 2, h / 2
    # canton: simplified Union Jack (white saltire + cross, red cross)
    draw.rectangle([S(x), S(y), S(x + cw), S(y + ch)], fill=(0, 0, 139))
    draw.line([S(x), S(y), S(x + cw), S(y + ch)], fill=(255, 255, 255),
              width=S(3))
    draw.line([S(x + cw), S(y), S(x), S(y + ch)], fill=(255, 255, 255),
              width=S(3))
    draw.line([S(x + cw / 2), S(y), S(x + cw / 2), S(y + ch)],
              fill=(255, 255, 255), width=S(6))
    draw.line([S(x), S(y + ch / 2), S(x + cw), S(y + ch / 2)],
              fill=(255, 255, 255), width=S(6))
    draw.line([S(x + cw / 2), S(y), S(x + cw / 2), S(y + ch)],
              fill=(200, 20, 30), width=S(3))
    draw.line([S(x), S(y + ch / 2), S(x + cw), S(y + ch / 2)],
              fill=(200, 20, 30), width=S(3))
    # big seven-point star below the canton + Southern Cross stars
    for (sx, sy, sr) in [(x + cw / 2, y + ch + (h - ch) * 0.55, 5),
                          (x + w * 0.72, y + h * 0.30, 3),
                          (x + w * 0.82, y + h * 0.55, 3),
                          (x + w * 0.68, y + h * 0.62, 3),
                          (x + w * 0.90, y + h * 0.72, 3),
                          (x + w * 0.80, y + h * 0.85, 3)]:
        draw.ellipse([S(sx - sr), S(sy - sr), S(sx + sr), S(sy + sr)],
                     fill=(255, 255, 255))


def draw_flag_sb(draw, x, y, w, h):
    """Solomon Islands: blue upper triangle, green lower triangle,
    yellow diagonal band rising left to right, five white stars."""
    draw.rectangle([S(x), S(y), S(x + w), S(y + h)], fill=(0, 80, 160))
    draw.polygon([(S(x), S(y + h)), (S(x + w), S(y + h)), (S(x + w), S(y))],
                 fill=(0, 130, 60))
    # yellow diagonal band (lower-hoist to upper-fly)
    band = h * 0.16
    draw.polygon([(S(x), S(y + h)), (S(x), S(y + h - band)),
                  (S(x + w), S(y + band)), (S(x + w), S(y))],
                 fill=(255, 210, 0))
    for (sx, sy) in [(x + w * 0.10, y + h * 0.15), (x + w * 0.18, y + h * 0.10),
                     (x + w * 0.07, y + h * 0.32), (x + w * 0.20, y + h * 0.24),
                     (x + w * 0.14, y + h * 0.42)]:
        draw.ellipse([S(sx - 3), S(sy - 3), S(sx + 3), S(sy + 3)],
                     fill=(255, 255, 255))


def scene_hormuz(draw, box):
    """Strait of Hormuz diagram: headlands, sea surface line, tankers on it,
    mines clearly BELOW the surface (in the water, above the seabed)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # sky
    draw.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=(214, 232, 240))
    # headlands: Iran (top-left), Oman (top-right)
    draw.polygon([(S(x0), S(y0)), (S(x0 + w * 0.42), S(y0)),
                  (S(x0 + w * 0.30), S(y0 + h * 0.30)), (S(x0), S(y0 + h * 0.34))],
                 fill=(198, 178, 138))
    draw.polygon([(S(x1), S(y0)), (S(x1 - w * 0.40), S(y0)),
                  (S(x1 - w * 0.28), S(y0 + h * 0.30)), (S(x1), S(y0 + h * 0.34))],
                 fill=(198, 178, 138))
    # sea
    sea_y = y0 + h * 0.34
    draw.rectangle([S(x0), S(sea_y), S(x1), S(y1)], fill=(28, 96, 150))
    draw.rectangle([S(x0), S(sea_y), S(x1), S(sea_y + 4)], fill=(120, 190, 220))
    # seabed
    draw.polygon([(S(x0), S(y1)), (S(x1), S(y1)), (S(x1), S(y1 - 14)),
                  (S(x0 + w * 0.6), S(y1 - 22)), (S(x0), S(y1 - 10))],
                 fill=(120, 105, 80))
    # labels
    f_lab = font(SANS_B, 15)
    draw.text((S(x0 + 150), S(y0 + 8)), "IRAN", font=f_lab, fill=(90, 70, 40))
    draw.text((S(x1 - 62), S(y0 + 8)), "OMAN", font=f_lab, fill=(90, 70, 40))
    f_sea = font(SERIF_B, 20)
    t = "STRAIT OF HORMUZ"
    tw = draw.textlength(t, font=f_sea) / SS
    draw.text((S(x0 + (w - tw) / 2), S(sea_y + 30)), t, font=f_sea,
              fill=(255, 255, 255))
    # tankers on the surface: hulls dip below the waterline
    draw_tanker(draw, x0 + 40, sea_y - 20, 150, 40)
    draw_tanker(draw, x0 + w * 0.42, sea_y - 22, 170, 44, burning=True)
    draw_tanker(draw, x0 + w - 210, sea_y - 20, 150, 40, hull=(40, 60, 90))
    # mines BELOW the surface, above the seabed, with chains
    for (mx, my) in [(x0 + 130, sea_y + 78), (x0 + w * 0.52, sea_y + 95),
                     (x0 + w - 120, sea_y + 70)]:
        draw_mine(draw, mx, my, 11)
        # chain down toward seabed
        for cy in range(int(my + 14), int(y1 - 20), 8):
            draw.ellipse([S(mx - 2), S(cy), S(mx + 2), S(cy + 4)],
                         fill=(30, 30, 35))


def scene_rocket(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=(10, 16, 42))
    for (sx, sy, sr) in [(x0 + 30, y0 + 20, 2), (x0 + 120, y0 + 14, 2),
                          (x0 + 210, y0 + 30, 2), (x0 + 300, y0 + 12, 2),
                          (x0 + 400, y0 + 26, 2), (x0 + 70, y0 + 55, 1),
                          (x0 + 350, y0 + 60, 1), (x0 + 250, y0 + 8, 1)]:
        draw.ellipse([S(sx - sr), S(sy - sr), S(sx + sr), S(sy + sr)],
                     fill=(255, 255, 255))
    # orbit arc (kept inside the panel box)
    draw.arc([S(x0 + 20), S(y0 + 6), S(x1 - 10), S(y1 + 70)], 195, 345,
             fill=(255, 204, 0), width=S(3))
    # Tiangong station (top right)
    sx, sy = x1 - 120, y0 + 26
    draw.rectangle([S(sx), S(sy), S(sx + 66), S(sy + 14)], fill=(212, 175, 55))
    draw.rectangle([S(sx - 34), S(sy + 2), S(sx), S(sy + 12)], fill=(40, 90, 160))
    draw.rectangle([S(sx + 66), S(sy + 2), S(sx + 100), S(sy + 12)],
                   fill=(40, 90, 160))
    draw.ellipse([S(sx + 26), S(sy - 8), S(sx + 40), S(sy + 6)], fill=(230, 230, 230))
    # rocket (centre-left), nose up, Pakistan flag band
    rx, ry = x0 + 150, y0 + 34
    rw, rh = 46, 78
    draw.polygon([(S(rx), S(ry)), (S(rx + rw), S(ry)), (S(rx + rw), S(ry + 22)),
                  (S(rx), S(ry + 22))], fill=(245, 245, 240))
    draw.polygon([(S(rx), S(ry + 22)), (S(rx + rw), S(ry + 22)),
                  (S(rx + rw), S(ry + rh)), (S(rx), S(ry + rh))],
                 fill=(245, 245, 240))
    # nose cone
    draw.polygon([(S(rx), S(ry)), (S(rx + rw), S(ry)),
                  (S(rx + rw / 2), S(ry - 20))], fill=(200, 30, 40))
    # Pakistan flag band: green with white crescent + star
    draw.rectangle([S(rx), S(ry + 34), S(rx + rw), S(ry + 58)],
                   fill=(1, 80, 40))
    draw.ellipse([S(rx + 10), S(ry + 38), S(rx + 30), S(ry + 54)],
                 fill=(255, 255, 255))
    draw.ellipse([S(rx + 14), S(ry + 38), S(rx + 32), S(ry + 54)],
                 fill=(1, 80, 40))
    draw.ellipse([S(rx + 33), S(ry + 42), S(rx + 39), S(ry + 48)],
                 fill=(255, 255, 255))
    # fins + flame (kept well inside the panel: flame tip at +28)
    draw.polygon([(S(rx), S(ry + rh)), (S(rx - 14), S(ry + rh + 16)),
                  (S(rx), S(ry + rh + 8))], fill=(200, 30, 40))
    draw.polygon([(S(rx + rw), S(ry + rh)), (S(rx + rw + 14), S(ry + rh + 16)),
                  (S(rx + rw), S(ry + rh + 8))], fill=(200, 30, 40))
    draw.polygon([(S(rx + 8), S(ry + rh)), (S(rx + rw - 8), S(ry + rh)),
                  (S(rx + rw / 2), S(ry + rh + 28))], fill=(255, 140, 0))
    draw.polygon([(S(rx + 14), S(ry + rh)), (S(rx + rw - 14), S(ry + rh)),
                  (S(rx + rw / 2), S(ry + rh + 17))], fill=(255, 220, 60))
    # TIANGONG label: tucked directly under the station module, on a navy
    # patch so the orbit arc cannot strike through the text
    f_lab = font(SANS_B, 13)
    tw_lab = draw.textlength("TIANGONG", font=f_lab) / SS
    draw.rectangle([S(sx - 3), S(sy + 17), S(sx + tw_lab + 3), S(sy + 34)],
                   fill=(10, 16, 42))
    draw.text((S(sx), S(sy + 19)), "TIANGONG", font=f_lab,
              fill=(255, 204, 0))


def scene_trade(draw, box):
    """Three clean stat tiles — one figure per tile, flags correct and
    never overlapped: EU flag on the EU tile, Indonesia flag on the
    Indonesia tile, €600m on its own tile. No shared axis."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=(238, 240, 244))
    f_val = font(SANS_B, 28)
    f_cap = font(SANS, 13)
    tiles = [
        ("eu", "98.5%", "of EU tariff lines", "go duty-free"),
        ("id", "90%", "of Indonesian goods", "go duty-free"),
        (None, "\u20ac600m", "saved by EU exporters", "every year"),
    ]
    tw = 148
    gap = (w - 3 * tw) / 4
    # tiles start below the beat chip (chip ends ~y0+33) so no flag is covered
    th = h - 16 - 26
    for i, (flag, val, cap1, cap2) in enumerate(tiles):
        tx = x0 + gap + i * (tw + gap)
        ty = y0 + 34
        draw.rectangle([S(tx), S(ty), S(tx + tw), S(ty + th)],
                       fill=(255, 255, 255), outline=(180, 184, 190),
                       width=S(2))
        fy = ty + 8
        if flag == "eu":
            draw_flag_eu(draw, tx + (tw - 52) / 2, fy, 52, 30)
        elif flag == "id":
            draw_flag_id(draw, tx + (tw - 52) / 2, fy, 52, 30)
        else:
            # euro mark, centred where a flag sits on the other tiles
            f_eu = font(SERIF_B, 30)
            draw.text((S(tx + (tw - 22) / 2), S(fy - 2)), "\u20ac",
                      font=f_eu, fill=(0, 51, 153))
        vw = draw.textlength(val, font=f_val) / SS
        draw.text((S(tx + (tw - vw) / 2), S(ty + 46)), val, font=f_val,
                  fill=(15, 15, 20))
        for j, cap in enumerate((cap1, cap2)):
            cw = draw.textlength(cap, font=f_cap) / SS
            draw.text((S(tx + (tw - cw) / 2), S(ty + 84 + j * 16)), cap,
                      font=f_cap, fill=(40, 40, 45))


def scene_huawei(draw, box):
    """Courtroom: portrait phone (left), gavel with its head PERPENDICULAR
    to the handle (right), verdict numerals (top right), and a tidy wooden
    bench bar along the bottom — no loose stain."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=(24, 32, 54))
    # phone, portrait: 72 wide x 104 tall, top below the beat chip
    px, py, pw, ph = x0 + 26, y0 + 40, 72, 104
    draw.rounded_rectangle([S(px), S(py), S(px + pw), S(py + ph)], radius=S(10),
                           fill=(15, 15, 20), outline=(180, 180, 190),
                           width=S(2))
    f_ph = font(SANS_B, 13)
    t = "HUAWEI"
    tw = draw.textlength(t, font=f_ph) / SS
    draw.text((S(px + (pw - tw) / 2), S(py + 42)), t, font=f_ph,
              fill=(255, 255, 255))
    draw.ellipse([S(px + pw / 2 - 4), S(py + ph - 14), S(px + pw / 2 + 4),
                  S(py + ph - 6)], fill=(120, 120, 130))
    # gavel: handle runs up-right; head is a block across the handle,
    # long axis perpendicular to the handle (never a paddle)
    hx0, hy0 = x0 + 150, y0 + 112
    hx1, hy1 = x0 + 258, y0 + 44
    draw.line([S(hx0), S(hy0), S(hx1), S(hy1)], fill=(150, 105, 60),
              width=S(12))
    dx, dy = hx1 - hx0, hy1 - hy0
    ln = math.hypot(dx, dy)
    dx, dy = dx / ln, dy / ln
    pxn, pyn = -dy, dx  # perpendicular unit vector
    cx, cy = hx1 + 6 * dx, hy1 + 6 * dy
    draw.polygon([(S(cx - 15 * dx + 32 * pxn), S(cy - 15 * dy + 32 * pyn)),
                  (S(cx + 15 * dx + 32 * pxn), S(cy + 15 * dy + 32 * pyn)),
                  (S(cx + 15 * dx - 32 * pxn), S(cy + 15 * dy - 32 * pyn)),
                  (S(cx - 15 * dx - 32 * pxn), S(cy - 15 * dy - 32 * pyn))],
                 fill=(120, 80, 40))
    # bench bar: one tidy wooden strip along the bottom, gavel rests above it
    draw.rounded_rectangle([S(x0 + 140), S(y1 - 22), S(x1 - 130), S(y1 - 8)],
                           radius=S(4), fill=(120, 80, 40))
    draw.rectangle([S(x0 + 140), S(y1 - 22), S(x1 - 130), S(y1 - 18)],
                   fill=(165, 115, 60))
    # verdict numerals
    f_big = font(SERIF_B, 44)
    draw.text((S(x1 - 128), S(y0 + 18)), "10 / 12", font=f_big,
              fill=(255, 210, 60))
    f_lab = font(SANS_B, 13)
    draw.text((S(x1 - 128), S(y0 + 72)), "CHARGES: GUILTY", font=f_lab,
              fill=(255, 255, 255))


def scene_solomon(draw, box):
    """Treaty signing in Canberra: the Australian and Solomon Islands
    flags stand large behind a signing table; two leaders lean over the
    document, one holding the pen, a gold seal on the page."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=(222, 226, 230))
    # flag poles + flags: hung BELOW the beat chip (chip ends ~y0+33),
    # large, upright, correct orientation, down to the table top
    draw.rectangle([S(x0 + 20), S(y0 + 38), S(x0 + 24), S(y1 - 52)],
                   fill=(90, 70, 40))
    draw.rectangle([S(x1 - 24), S(y0 + 38), S(x1 - 20), S(y1 - 52)],
                   fill=(90, 70, 40))
    draw_flag_au(draw, x0 + 24, y0 + 38, 148, 66)
    draw_flag_sb(draw, x1 - 172, y0 + 38, 148, 66)
    # signing table
    draw.rectangle([S(x0 + 10), S(y1 - 52), S(x1 - 10), S(y1 - 8)],
                   fill=(90, 60, 35))
    draw.rectangle([S(x0 + 10), S(y1 - 52), S(x1 - 10), S(y1 - 44)],
                   fill=(140, 95, 55))
    # document on the table
    dx0, dy0 = x0 + w / 2 - 78, y1 - 96
    draw.rectangle([S(dx0), S(dy0), S(dx0 + 156), S(y1 - 50)],
                   fill=(255, 255, 255), outline=(120, 120, 125), width=S(2))
    for j in range(3):
        draw.rectangle([S(dx0 + 14), S(dy0 + 10 + j * 8), S(dx0 + 118),
                        S(dy0 + 13 + j * 8)], fill=(150, 150, 155))
    # gold seal on the document
    draw.ellipse([S(dx0 + 122), S(dy0 + 26), S(dx0 + 144), S(dy0 + 48)],
                 fill=(212, 175, 55), outline=(160, 120, 20), width=S(2))
    # two leaders leaning over the document (dark suits, heads bowed)
    for (hx, suit) in [(x0 + w / 2 - 118, (20, 30, 55)),
                        (x0 + w / 2 + 118, (45, 45, 50))]:
        # head kept below the beat chip (chip ends ~y0+33)
        draw.ellipse([S(hx - 15), S(dy0 - 24), S(hx + 15), S(dy0 + 6)],
                     fill=(210, 170, 135))
        draw.polygon([(S(hx - 34), S(y1 - 50)), (S(hx + 34), S(y1 - 50)),
                      (S(hx + 22), S(dy0 - 6)), (S(hx - 22), S(dy0 - 6))],
                     fill=suit)
        draw.polygon([(S(hx - 8), S(dy0 - 6)), (S(hx + 8), S(dy0 - 6)),
                      (S(hx + 4), S(dy0 + 16)), (S(hx - 4), S(dy0 + 16))],
                     fill=(255, 255, 255))
        # arm reaching to the document
        draw.line([S(hx + 10), S(dy0 + 4), S(x0 + w / 2 - 14 if hx < x0 + w / 2
                   else x0 + w / 2 + 14), S(dy0 + 22)], fill=suit, width=S(9))
    # pen in the right leader's hand, touching the page
    draw.line([S(x0 + w / 2 + 96), S(dy0 + 14), S(x0 + w / 2 + 66), S(dy0 + 26)],
              fill=(20, 20, 25), width=S(4))


def build():
    img = Image.new("RGB", (S(W), S(H)), (250, 248, 242))
    d = ImageDraw.Draw(img)
    navy = (11, 31, 58)

    # --- masthead: single navy band, date only ---
    d.rectangle([0, 0, S(W), S(90)], fill=navy)
    f_date = font(SERIF_B, 52)
    t = "WEDNESDAY, 25 NOVEMBER 2026"
    tw = d.textlength(t, font=f_date) / SS
    d.text((S((W - tw) / 2), S(16)), t, font=f_date, fill=(255, 255, 255))
    d.rectangle([0, S(90), S(W), S(94)], fill=(200, 160, 40))

    # --- hero panel (trimmed to 450: title + 2-line sub end ~14px above edge) ---
    hx0, hy0, hx1, hy1 = 16, 102, 1008, 450
    d.rectangle([S(hx0), S(hy0), S(hx1), S(hy1)], fill=(255, 255, 255),
                outline=(30, 30, 35), width=S(2))
    scene_hormuz(d, (hx0 + 2, hy0 + 2, hx1 - 2, hy0 + 224))
    chip(d, hx0 + 12, hy0 + 12, "ENERGY · GULF", navy)
    f_title = font(SERIF_B, 36)
    d.text((S(hx0 + 14), S(hy0 + 236)),
           "TANKERS HIT MINES IN STRAIT OF HORMUZ", font=f_title,
           fill=(15, 15, 20))
    f_sub = font(SANS, 20)
    text_block(d, (hx0 + 14, hy0 + 282),
               "Two tankers struck mines, exploded and caught fire in the "
               "strait that carries a fifth of the world's oil, amid the US "
               "blockade of Iran's ports. Trump warned ships testing it "
               "would end up \u201cat the bottom of the sea\u201d.",
               f_sub, (35, 35, 40), 960, 2, 26)

    # --- 2 x 2 grid (enlarged: 262 tall, taller scenes, uniform 17px subs) ---
    panels = [
        (16, 462, scene_rocket, "SPACE · ASIA",
         "PAKISTAN'S FIRST ASTRONAUT IN ORBIT",
         "Muhammad Zeeshan Ali, 40, flew aboard Shenzhou-24 and docked at "
         "Tiangong, its first foreign guest."),
        (520, 462, scene_trade, "TRADE · EUROPE–ASIA",
         "EU AND INDONESIA SIGN TRADE DEAL",
         "After 10 years of talks, duties fall on 90% of goods and EU "
         "exporters save \u20ac600m a year."),
        (16, 730, scene_huawei, "TECH · USA",
         "HUAWEI GUILTY ON 10 OF 12 CHARGES",
         "A Brooklyn jury convicted the telecom giant of bank fraud and "
         "stealing trade secrets; Huawei plans to appeal."),
        (520, 730, scene_solomon, "SECURITY · PACIFIC",
         "SOLOMONS SIGN SECURITY TREATY",
         "Wale and Albanese signed in Canberra: Australia is the primary "
         "security partner; no foreign base."),
    ]
    pw, ph = 488, 262
    for (px, py, scene, beat, title, sub) in panels:
        d.rectangle([S(px), S(py), S(px + pw), S(py + ph)], fill=(255, 255, 255),
                    outline=(30, 30, 35), width=S(2))
        scene(d, (px + 2, py + 2, px + pw - 2, py + 158))
        chip(d, px + 10, py + 10, beat, navy)
        f_t = font(SERIF_B, 22)
        text_block(d, (px + 12, py + 164), title, f_t, (15, 15, 20),
                   pw - 24, 2, 26)
        # title height: measure lines actually used
        nlines = len(wrap(d, title, f_t, pw - 24))
        f_s = font(SANS, 17)
        text_block(d, (px + 12, py + 164 + nlines * 26 + 2), sub, f_s,
                   (35, 35, 40), pw - 24, 2, 21)

    out = img.resize((W, H), Image.LANCZOS)
    out.save(os.path.join(HERE, "entry.png"), "PNG", optimize=True)
    print("wrote entry.png", out.size)


if __name__ == "__main__":
    build()

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
    draw.rectangle([S(x), S(y), S(x + w), S(y + h / 2)], fill=(200, 20, 30))
    draw.rectangle([S(x), S(y + h / 2), S(x + w), S(y + h)], fill=(255, 255, 255))


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
    # fins + flame
    draw.polygon([(S(rx), S(ry + rh)), (S(rx - 14), S(ry + rh + 16)),
                  (S(rx), S(ry + rh + 8))], fill=(200, 30, 40))
    draw.polygon([(S(rx + rw), S(ry + rh)), (S(rx + rw + 14), S(ry + rh + 16)),
                  (S(rx + rw), S(ry + rh + 8))], fill=(200, 30, 40))
    draw.polygon([(S(rx + 8), S(ry + rh)), (S(rx + rw - 8), S(ry + rh)),
                  (S(rx + rw / 2), S(ry + rh + 34))], fill=(255, 140, 0))
    draw.polygon([(S(rx + 14), S(ry + rh)), (S(rx + rw - 14), S(ry + rh)),
                  (S(rx + rw / 2), S(ry + rh + 20))], fill=(255, 220, 60))
    f_lab = font(SANS_B, 13)
    draw.text((S(x1 - 118), S(y0 + h - 22)), "TIANGONG", font=f_lab,
              fill=(255, 204, 0))


def scene_trade(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=(238, 240, 244))
    base = y1 - 26
    f_val = font(SANS_B, 14)
    f_cap = font(SANS, 12)
    bars = [
        ("90%", "duties cut", 90, (0, 51, 153), "eu"),
        ("€650m", "saved / year", 65, (0, 120, 110), "id"),
        ("50% to 0", "car duty", 50, (180, 60, 50), "eu"),
    ]
    bw = 74
    gap = (w - 3 * bw) / 4
    for i, (val, cap, pct, col, flag) in enumerate(bars):
        bx = x0 + gap + i * (bw + gap)
        bh = (h - 64) * pct / 100.0
        by = base - bh
        draw.rectangle([S(bx), S(by), S(bx + bw), S(base)], fill=col)
        if flag == "eu":
            draw_flag_eu(draw, bx + 18, by - 28, 38, 24)
        else:
            draw_flag_id(draw, bx + 18, by - 28, 38, 24)
        # value inside the bar top (white), never above the panel
        vw = draw.textlength(val, font=f_val) / SS
        draw.text((S(bx + (bw - vw) / 2), S(by + 5)), val, font=f_val,
                  fill=(255, 255, 255))
        cw = draw.textlength(cap, font=f_cap) / SS
        draw.text((S(bx + (bw - cw) / 2), S(base + 4)), cap, font=f_cap,
                  fill=(40, 40, 45))
    draw.line([S(x0 + 8), S(base), S(x1 - 8), S(base)], fill=(60, 60, 65),
              width=S(2))


def scene_huawei(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=(24, 32, 54))
    # phone with HUAWEI
    px, py, pw, ph = x0 + 28, y0 + 22, 96, 96
    draw.rounded_rectangle([S(px), S(py), S(px + pw), S(py + ph)], radius=S(10),
                           fill=(15, 15, 20), outline=(180, 180, 190),
                           width=S(2))
    f_ph = font(SANS_B, 15)
    t = "HUAWEI"
    tw = draw.textlength(t, font=f_ph) / SS
    draw.text((S(px + (pw - tw) / 2), S(py + 36)), t, font=f_ph,
              fill=(255, 255, 255))
    draw.ellipse([S(px + pw / 2 - 4), S(py + ph - 14), S(px + pw / 2 + 4),
                  S(py + ph - 6)], fill=(120, 120, 130))
    # gavel (diagonal)
    gx, gy = x0 + 190, y0 + 78
    ang = math.radians(-35)
    dx, dy = math.cos(ang), math.sin(ang)
    draw.line([S(gx - 70 * dx), S(gy - 70 * dy), S(gx + 70 * dx),
               S(gy + 70 * dy)], fill=(150, 105, 60), width=S(12))
    hx, hy = gx + 52 * dx, gy + 52 * dy
    pxn, pyn = -dy, dx
    draw.polygon([(S(hx - 30 * dx + 16 * pxn), S(hy - 30 * dy + 16 * pyn)),
                  (S(hx + 30 * dx + 16 * pxn), S(hy + 30 * dy + 16 * pyn)),
                  (S(hx + 30 * dx - 16 * pxn), S(hy + 30 * dy - 16 * pyn)),
                  (S(hx - 30 * dx - 16 * pxn), S(hy - 30 * dy - 16 * pyn))],
                 fill=(120, 80, 40))
    # sound block
    draw.ellipse([S(x0 + 330), S(y1 - 34), S(x0 + 420), S(y1 - 18)],
                 fill=(120, 80, 40))
    # verdict numerals
    f_big = font(SERIF_B, 44)
    draw.text((S(x1 - 128), S(y0 + 18)), "10 / 12", font=f_big,
              fill=(255, 210, 60))
    f_lab = font(SANS_B, 13)
    draw.text((S(x1 - 128), S(y0 + 72)), "CHARGES: GUILTY", font=f_lab,
              fill=(255, 255, 255))


def scene_elnino(draw, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=(24, 90, 150))
    # land hints: South America (left), Australia (right)
    draw.polygon([(S(x0), S(y0 + 20)), (S(x0 + 52), S(y0 + 10)),
                  (S(x0 + 44), S(y0 + h - 20)), (S(x0), S(y1))],
                 fill=(198, 178, 138))
    draw.polygon([(S(x1), S(y0 + 60)), (S(x1 - 58), S(y0 + 70)),
                  (S(x1 - 48), S(y1 - 10)), (S(x1), S(y1))],
                 fill=(198, 178, 138))
    # warm anomaly blob over the equatorial Pacific
    cx, cy = x0 + w * 0.52, y0 + h * 0.52
    draw.ellipse([S(cx - 150), S(cy - 34), S(cx + 150), S(cy + 34)],
                 fill=(230, 90, 40))
    draw.ellipse([S(cx - 105), S(cy - 22), S(cx + 105), S(cy + 22)],
                 fill=(245, 150, 50))
    draw.ellipse([S(cx - 60), S(cy - 12), S(cx + 60), S(cy + 12)],
                 fill=(255, 205, 80))
    # thermometer
    tx = x1 - 52
    draw.rounded_rectangle([S(tx), S(y0 + 18), S(tx + 16), S(y1 - 34)],
                           radius=S(8), fill=(255, 255, 255))
    draw.ellipse([S(tx - 7), S(y1 - 44), S(tx + 23), S(y1 - 14)],
                 fill=(220, 40, 30))
    draw.rectangle([S(tx + 5), S(y0 + 34), S(tx + 11), S(y1 - 30)],
                   fill=(220, 40, 30))
    f_lab = font(SANS_B, 15)
    draw.text((S(cx - 46), S(cy - 10)), "+4.0°C", font=f_lab, fill=(120, 30, 10))


def build():
    img = Image.new("RGB", (S(W), S(H)), (250, 248, 242))
    d = ImageDraw.Draw(img)
    navy = (11, 31, 58)

    # --- masthead: single navy band, date only ---
    d.rectangle([0, 0, S(W), S(90)], fill=navy)
    f_date = font(SERIF_B, 52)
    t = "TUESDAY, 25 NOVEMBER 2026"
    tw = d.textlength(t, font=f_date) / SS
    d.text((S((W - tw) / 2), S(16)), t, font=f_date, fill=(255, 255, 255))
    d.rectangle([0, S(90), S(W), S(94)], fill=(200, 160, 40))

    # --- hero panel ---
    hx0, hy0, hx1, hy1 = 16, 102, 1008, 506
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
               "Iran says oil tankers struck mines, exploded and caught fire "
               "in the strait that carries a fifth of the world's oil. Trump "
               "warned Iranian ships testing the US blockade would end up "
               "\u201cat the bottom of the sea\u201d.",
               f_sub, (35, 35, 40), 960, 2, 26)

    # --- 2 x 2 grid ---
    panels = [
        (16, 518, scene_rocket, "SPACE · ASIA",
         "PAKISTAN'S FIRST ASTRONAUT REACHES ORBIT",
         "Muhammad Zeeshan Ali, 40, flew aboard China's Shenzhou-24 to the "
         "Tiangong station — the first Pakistani in orbit, and the first "
         "foreign guest ever at the station."),
        (520, 518, scene_trade, "TRADE · EUROPE–ASIA",
         "EU AND INDONESIA SIGN TRADE DEAL",
         "After 10 years of talks, duties fall on 90% of goods and EU "
         "exporters save \u20ac650m a year, as both sides seek cover from "
         "Trump's tariffs."),
        (16, 770, scene_huawei, "TECH · USA",
         "HUAWEI GUILTY ON 10 OF 12 CHARGES",
         "A Brooklyn jury convicted the Chinese telecom giant of stealing "
         "trade secrets and bank fraud. Huawei faces billions in fines and "
         "plans to appeal."),
        (520, 770, scene_elnino, "CLIMATE · PACIFIC",
         "EL NIÑO HEADS FOR A STRONG PEAK",
         "The WMO is expanding preparedness as the event nears its "
         "late-2026 peak. Odds of strong-to-very-strong conditions into "
         "March 2027 top 79%."),
    ]
    pw, ph = 488, 240
    for (px, py, scene, beat, title, sub) in panels:
        d.rectangle([S(px), S(py), S(px + pw), S(py + ph)], fill=(255, 255, 255),
                    outline=(30, 30, 35), width=S(2))
        scene(d, (px + 2, py + 2, px + pw - 2, py + 142))
        chip(d, px + 10, py + 10, beat, navy)
        f_t = font(SERIF_B, 23)
        text_block(d, (px + 12, py + 147), title, f_t, (15, 15, 20),
                   pw - 24, 2, 26)
        # title height: measure lines actually used
        nlines = len(wrap(d, title, f_t, pw - 24))
        f_s = font(SANS, 16)
        text_block(d, (px + 12, py + 147 + nlines * 26 + 1), sub, f_s,
                   (35, 35, 40), pw - 24, 2, 19)

    out = img.resize((W, H), Image.LANCZOS)
    out.save(os.path.join(HERE, "entry.png"), "PNG", optimize=True)
    print("wrote entry.png", out.size)


if __name__ == "__main__":
    build()

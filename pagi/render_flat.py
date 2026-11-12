"""Renderer ARN-41 "Mana Lebih Hemat? #5 — ojol saat hujan" — gaya Flat 2D (sampel 1).
Salinan tools/render_polaroid.py (helper kartu, koin, Si Bocor, panah, Aru, logo, sfx) dengan frame Flat 2D
dari render_gaya_frame0.py (Aru basah + HP, counter Rp22.400 -> Rp30.000 dtk 1,6-2,6, hujan, pill judul).
Pemakaian (dari folder pagi/, setelah align.py -> timing.json):
  TOTAL=51.8 python3 render_flat.py events
  TOTAL=51.8 python3 render_flat.py stills 0,2,...
  TOTAL=51.8 python3 render_flat.py video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

import render_gaya_frame0 as G
from render_gaya_frame0 import (F, clamp, eio, rp, aru_phone, draw_counter, rain, pills, aru_origin, bob,
                                NAVY, TEAL, YEL, WHITE, CREAM, BROWN, GREY_T, RED, SAFE_X)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "51.8"))
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
GREEN = (46, 160, 110); INK = (60, 66, 92); LIGHT = (232, 238, 246)

TIM = json.load(open("timing.json"))
def cs(i): return TIM[i]["start"] + LEAD
def ce(i): return TIM[i]["end"] + LEAD

SCENE_CHUNK = [0, 6, 13, 18, 26, 30, 35, 40, 45, 50]
SC = [0.0] + [cs(i) - 0.25 for i in SCENE_CHUNK[1:]] + [TOTAL]
NS = len(SCENE_CHUNK)
FOLLOW = (10.4, 15.0)          # PRB-4: ajakan follow teks kecil dtk 10-15
NOTES = {
    0: ("tarif dasar: KP 667/2022 · naik saat hujan = contoh ilustrasi",),
    2: ("tarif ojol zona II maks Rp2.800/km · KP 667/2022",),
    3: ("Rp30.000 = contoh ilustrasi · tarif beda tiap aplikasi, kota, jam",),
    4: ("12 hari hujan & Rp30.000 = angka contoh ilustrasi",),
    5: ("Pertalite Rp10.000/l · detikOto, 1 Nov 2026", "192 km & 40 km/l = ilustrasi"),
    6: ("parkir ±Rp2.000/jam · Metro TV, 23 Agu 2026", "servis Jawa Pos 24 Agu 2026 · jas hujan GridOto · ilustrasi"),
    7: ("angka contoh ilustrasi · belum termasuk cicilan & pajak motor",),
}


def scene_of(t):
    for k in range(NS):
        if t < SC[k + 1]: return k
    return NS - 1


# ---------- easing (dari render_polaroid) ----------
def back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def pop(t, t0, d=0.35): return 0.0 if t < t0 else back((t - t0) / d)


# ---------- aset ----------
def trim(im): return im.crop(im.getbbox())
ARU = trim(Image.open(MEDIA + "/maskot/aru-syal-bendera.png").convert("RGBA"))
LOGO = trim(Image.open(MEDIA + "/brand/arunika-logo.png").convert("RGBA"))


@lru_cache(None)
def aru_h(h):
    r = h / ARU.height
    return ARU.resize((int(ARU.width * r), h), Image.LANCZOS)


@lru_cache(None)
def logo_w(w):
    r = w / LOGO.width
    return LOGO.resize((w, int(LOGO.height * r)), Image.LANCZOS)


def paste_c(dst, im, cx, cy, scale=1.0, angle=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01: return
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if abs(angle) > 0.05:
        im = im.rotate(angle, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    dst.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def draw_aru(layer, cx, bottom, h, t, angle_amp=2.0):
    im = aru_h(h)
    b = 7 * math.sin(2 * math.pi * 1.1 * t)
    ang = angle_amp * math.sin(2 * math.pi * 0.7 * t)
    paste_c(layer, im, cx, bottom - h / 2 + b, 1.0, ang)


def text_c(d, xy, s, font, fill, anchor="mm", **kw):
    d.text(xy, s, font=font, fill=fill, anchor=anchor, **kw)


def fit(name, size, s, maxw):
    f = F(name, size)
    while f.getlength(s) > maxw and size > 14:
        size -= 2; f = F(name, size)
    return f


# ---------- kartu flat (tanpa outline coklat; bayangan lembut) ----------
def card(w, h, fill=WHITE, r=30, outline=NAVY, ow=5):
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 12, w + 10, h + 12), r, fill=(20, 33, 91, 45))
    d.rounded_rectangle((0, 0, w, h), r, fill=fill, outline=outline, width=ow)
    return im, d


def coin(r=26):
    im = Image.new("RGBA", (2 * r + 6, 2 * r + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((3, 3, 2 * r + 3, 2 * r + 3), fill=(255, 194, 60), outline=(217, 154, 31), width=4)
    text_c(d, (r + 3, r + 3), "Rp", F("pb", int(r * 0.75)), (154, 106, 16))
    return im


@lru_cache(None)
def bocor_img():
    im = Image.new("RGBA", (300, 270), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line([(60, 200), (30, 185), (12, 150), (22, 125)], fill=(244, 163, 184), width=7, joint="curve")
    d.polygon([(150, 70), (255, 88), (246, 238), (142, 228)], fill=(201, 162, 107), outline=NAVY)
    d.line([(150, 70), (255, 88), (246, 238), (142, 228), (150, 70)], fill=NAVY, width=5)
    text_c(d, (200, 150), "Rp", F("pb", 46), (122, 90, 46))
    d.ellipse((214, 196, 232, 214), fill=NAVY)
    d.ellipse((40, 110, 190, 250), fill=(142, 138, 156), outline=NAVY, width=5)
    d.ellipse((72, 160, 158, 245), fill=(185, 181, 198))
    d.line([(80, 245), (64, 266)], fill=NAVY, width=6); d.line([(150, 245), (166, 266)], fill=NAVY, width=6)
    for ex in (40, 135):
        d.ellipse((ex, 8, ex + 58, 66), fill=(142, 138, 156), outline=NAVY, width=5)
        d.ellipse((ex + 12, 20, ex + 46, 54), fill=(244, 163, 184))
    d.ellipse((55, 38, 175, 150), fill=(142, 138, 156), outline=NAVY, width=5)
    d.ellipse((86, 78, 101, 97), fill=NAVY); d.ellipse((129, 78, 144, 97), fill=NAVY)
    d.line([(78, 68), (103, 78)], fill=NAVY, width=6); d.line([(152, 68), (127, 78)], fill=NAVY, width=6)
    d.ellipse((107, 102, 123, 116), fill=(196, 52, 140))
    d.arc((92, 104, 140, 134), 20, 150, fill=NAVY, width=4)
    return im


def arrow(d, x0, y0, x1, y1, col, w=16, head=34):
    ang = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 2: return
    hx, hy = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
    d.line([(x0, y0), (hx, hy)], fill=col, width=w)
    p = [(x1, y1), (hx + head * 0.6 * math.sin(ang), hy - head * 0.6 * math.cos(ang)),
         (hx - head * 0.6 * math.sin(ang), hy + head * 0.6 * math.cos(ang))]
    d.polygon(p, fill=col)


def dashed(d, pts, col, w=6, on=16, off=12, phase=0.0):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0); u = -phase % (on + off)
        while u < L:
            a, b = max(0, u), min(L, u + on)
            if b > a:
                d.line([(x0 + (x1 - x0) * a / L, y0 + (y1 - y0) * a / L),
                        (x0 + (x1 - x0) * b / L, y0 + (y1 - y0) * b / L)], fill=col, width=w)
            u += on + off


# ---------- ikon flat ----------
def icon_phone(d, cx, cy, s=1.0, alert=False):
    w, h = 90 * s, 160 * s
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(16 * s), fill=NAVY)
    d.rounded_rectangle((cx - w / 2 + 8 * s, cy - h / 2 + 14 * s, cx + w / 2 - 8 * s, cy + h / 2 - 14 * s),
                        int(8 * s), fill=(244, 247, 251))
    d.rectangle((cx - w / 2 + 8 * s, cy - h / 2 + 14 * s, cx + w / 2 - 8 * s, cy - h / 2 + 34 * s), fill=TEAL)
    d.ellipse((cx - 10 * s, cy + 10 * s, cx + 10 * s, cy + 30 * s), fill=RED)
    d.polygon([(cx - 9 * s, cy + 24 * s), (cx + 9 * s, cy + 24 * s), (cx, cy + 42 * s)], fill=RED)
    if alert:
        d.ellipse((cx + w / 2 - 22 * s, cy - h / 2 - 18 * s, cx + w / 2 + 22 * s, cy - h / 2 + 26 * s),
                  fill=RED, outline=WHITE, width=int(4 * s))
        text_c(d, (cx + w / 2, cy - h / 2 + 4 * s), "!", F("pb", int(34 * s)), WHITE)


def icon_motor(d, cx, cy, s=1.0, col=TEAL):
    r = 46 * s
    for wx in (-110, 110):
        d.ellipse((cx + wx * s - r, cy + 40 * s - r, cx + wx * s + r, cy + 40 * s + r), fill=NAVY)
        d.ellipse((cx + wx * s - r * 0.45, cy + 40 * s - r * 0.45, cx + wx * s + r * 0.45, cy + 40 * s + r * 0.45),
                  fill=(200, 205, 215))
    d.polygon([(cx - 120 * s, cy + 10 * s), (cx - 60 * s, cy - 40 * s), (cx + 40 * s, cy - 40 * s),
               (cx + 80 * s, cy + 10 * s), (cx + 40 * s, cy + 40 * s), (cx - 70 * s, cy + 40 * s)],
              fill=col, outline=NAVY)
    d.line([(cx - 120 * s, cy + 10 * s), (cx - 60 * s, cy - 40 * s), (cx + 40 * s, cy - 40 * s),
            (cx + 80 * s, cy + 10 * s), (cx + 40 * s, cy + 40 * s), (cx - 70 * s, cy + 40 * s),
            (cx - 120 * s, cy + 10 * s)], fill=NAVY, width=int(6 * s))
    d.rounded_rectangle((cx - 80 * s, cy - 62 * s, cx + 20 * s, cy - 36 * s), int(12 * s), fill=NAVY)  # jok
    d.line([(cx + 70 * s, cy), (cx + 110 * s, cy - 90 * s), (cx + 150 * s, cy - 90 * s)], fill=NAVY, width=int(10 * s))
    d.line([(cx + 110 * s, cy - 90 * s), (cx + 110 * s, cy + 40 * s)], fill=NAVY, width=int(8 * s))


def icon_cloud(d, cx, cy, s=1.0, col=(205, 214, 228)):
    for dx, dy, r in ((-60, 10, 50), (0, -20, 66), (64, 8, 48)):
        d.ellipse((cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s), fill=col)
    d.rectangle((cx - 60 * s, cy + 10 * s, cx + 64 * s, cy + 58 * s), fill=col)


def icon_drop(d, cx, cy, s=1.0, col=(127, 178, 238)):
    r = 16 * s
    d.polygon([(cx, cy - 2.2 * r), (cx - r * 0.95, cy - 0.2 * r), (cx + r * 0.95, cy - 0.2 * r)], fill=col)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)


def icon_house(d, cx, cy, s=1.0):
    d.polygon([(cx - 70 * s, cy), (cx, cy - 64 * s), (cx + 70 * s, cy)], fill=RED, outline=NAVY)
    d.rectangle((cx - 52 * s, cy, cx + 52 * s, cy + 80 * s), fill=WHITE, outline=NAVY, width=int(5 * s))
    d.rectangle((cx - 14 * s, cy + 34 * s, cx + 14 * s, cy + 80 * s), fill=NAVY)


def icon_office(d, cx, cy, s=1.0):
    d.rectangle((cx - 50 * s, cy - 80 * s, cx + 50 * s, cy + 80 * s), fill=TEAL, outline=NAVY, width=int(5 * s))
    for r_ in range(4):
        for c_ in range(2):
            x = cx - 30 * s + c_ * 38 * s; y = cy - 62 * s + r_ * 34 * s
            d.rectangle((x, y, x + 22 * s, y + 20 * s), fill=WHITE)


def icon_check(d, cx, cy, s=1.0, col=GREEN):
    d.ellipse((cx - 40 * s, cy - 40 * s, cx + 40 * s, cy + 40 * s), fill=col)
    d.line([(cx - 18 * s, cy), (cx - 4 * s, cy + 15 * s), (cx + 20 * s, cy - 14 * s)], fill=WHITE, width=int(10 * s),
           joint="curve")


def icon_jacket(d, cx, cy, s=1.0, col=YEL):
    p = [(cx - 30 * s, cy - 70 * s), (cx + 30 * s, cy - 70 * s), (cx + 80 * s, cy - 30 * s), (cx + 70 * s, cy + 10 * s),
         (cx + 50 * s, cy), (cx + 50 * s, cy + 80 * s), (cx - 50 * s, cy + 80 * s), (cx - 50 * s, cy),
         (cx - 70 * s, cy + 10 * s), (cx - 80 * s, cy - 30 * s)]
    d.polygon(p, fill=col); d.line(p + [p[0]], fill=NAVY, width=int(6 * s))
    d.line([(cx, cy - 64 * s), (cx, cy + 80 * s)], fill=NAVY, width=int(5 * s))


def icon_clock(d, cx, cy, s=1.0, t=0.0):
    r = 70 * s
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE, outline=NAVY, width=int(8 * s))
    a = -math.pi / 2 + t * 2.0
    d.line([(cx, cy), (cx + 0.7 * r * math.cos(a), cy + 0.7 * r * math.sin(a))], fill=NAVY, width=int(8 * s))
    d.line([(cx, cy), (cx, cy - 0.45 * r)], fill=RED, width=int(10 * s))
    d.ellipse((cx - 8 * s, cy - 8 * s, cx + 8 * s, cy + 8 * s), fill=NAVY)


# ---------- latar ----------
@lru_cache(None)
def base_bg():
    img = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(img)
    top, bot = (238, 241, 246), (246, 242, 236)
    for y in range(H):
        u = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[j] + (bot[j] - top[j]) * u) for j in range(3)))
    return img


@lru_cache(None)
def bg_scene0():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((150, 560, 950, 1360), fill=(220, 238, 243))
    for cx, cy, r in ((300, 610, 80), (390, 580, 100), (490, 615, 75)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(205, 214, 228))
    floor = 1440
    d.rectangle((0, floor, W, H), fill=(218, 223, 232))
    d.line([(0, floor), (W, floor)], fill=NAVY, width=5)
    d.ellipse((250, floor - 30, 840, floor + 40), fill=(170, 200, 236))
    return img


@lru_cache(None)
def bg_rest():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((90, 480, 990, 1380), fill=(226, 238, 244))
    d.rectangle((0, 1490, W, H), fill=(224, 228, 236))
    return img


@lru_cache(None)
def header():
    L = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F("pb", 34); s1 = "MANA LEBIH HEMAT?"; s2 = "#5"
    w1 = f.getlength(s1); w2 = f.getlength(s2)
    tot = w1 + w2 + 52 + 40 + 12
    x0 = (W - tot) / 2
    d.rounded_rectangle((x0, 30, x0 + w1 + 52, 96), 33, fill=NAVY)
    d.text((x0 + 26, 63), s1, font=f, fill=WHITE, anchor="lm")
    x1 = x0 + w1 + 52 + 12
    d.rounded_rectangle((x1, 30, x1 + w2 + 40, 96), 33, fill=YEL)
    d.text((x1 + 20, 63), s2, font=f, fill=NAVY, anchor="lm")
    return L


# ---------- subtitle 1 baris (PRB-37), gaya Flat 2D #4 ----------
def sub_chunk(t):
    for i, c in enumerate(TIM):
        s = 0.0 if i == 0 else cs(i)
        nxt = cs(i + 1) if i + 1 < len(TIM) else TOTAL
        e = min(nxt, ce(i) + 0.45)
        if s <= t < e:
            return i
    return None


@lru_cache(None)
def sub_layer(i):
    c = TIM[i]; words = c["text"].split()
    size = 66
    while True:
        f = F("pb", size); padx = 24; gap = 14
        ws = [f.getlength(w) + 2 * padx for w in words]
        tot = sum(ws) + gap * (len(ws) - 1)
        if tot <= W - 2 * SAFE_X - 20 or size <= 40: break
        size -= 2
    hh = size + 30
    L = Image.new("RGBA", (int(tot) + 12, hh + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    x = 0
    for w, ww in zip(words, ws):
        key = w in c["keys"]
        d.rounded_rectangle((x + 7, 8, x + ww + 7, hh + 8), 14, fill=(0, 0, 0, 40))
        d.rounded_rectangle((x, 0, x + ww, hh), 14, fill=YEL if key else NAVY)
        d.text((x + ww / 2, hh / 2 + 2), w, font=f, fill=NAVY if key else WHITE, anchor="mm")
        x += ww + gap
    return L


def draw_sub(img, t):
    i = sub_chunk(t)
    if i is None: return
    s0 = 0.0 if i == 0 else cs(i)
    sc = 0.85 + 0.15 * back((t - s0) / 0.22) if i != 0 else 1.0
    L = sub_layer(i)
    paste_c(img, L, W / 2, 1600, sc)


# ---------- adegan ----------
def scene0(img, t):
    """frame 0: Aru basah + HP, counter Rp22.400 -> Rp30.000 di dtk 1,6-2,6 (PRB-29/36/46)."""
    rain(img, t, n=70, col=(150, 176, 214), alpha=170, seed=3)
    sc = 2.5 + 0.06 * eio((t - 1.4) / 1.4)  # zoom pelan, visual berganti ~dtk 1,5
    A = aru_phone(2.5)
    ox, oy = aru_origin(2.5, 1452); oy += bob(t)
    if sc != 2.5:
        k = sc / 2.5
        A2 = A.resize((int(A.width * k), int(A.height * k)), Image.BICUBIC)
        cx = ox + A.width / 2; by = oy + A.height
        ox2, oy2 = cx - A2.width / 2, by - A2.height
        img.alpha_composite(A2, (int(ox2), int(oy2)))
        draw_counter(img, ox2, oy2, sc, t)
    else:
        img.alpha_composite(A, (int(ox), int(oy)))
        draw_counter(img, ox, oy, sc, t)
    pills(img, [["SEBERAPA", "MAHAL"], ["HUJAN?"]], 290, size=76)
    # "motor sendiri habis berapa?" -> lencana motor + tanda tanya
    p = pop(t, cs(4))
    if p > 0:
        L = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.ellipse((20, 20, 280, 280), fill=YEL, outline=NAVY, width=8)
        icon_motor(d, 150, 140, 0.62, col=TEAL)
        text_c(d, (150, 236), "?", F("pb", 64), NAVY)
        paste_c(img, L, 870, 640, 0.72 * p, 6 * math.sin(t * 4))


def scene1(img, t):
    """janji kemarin: kotak komentar teratas #4 masih kosong -> kesempatanmu (PRB-43)."""
    d = ImageDraw.Draw(img)
    cw, ch = 820, 600
    L, cd = card(cw, ch)
    cd.rounded_rectangle((0, 0, cw, 110), 30, fill=TEAL); cd.rectangle((0, 60, cw, 110), fill=TEAL)
    cd.rounded_rectangle((0, 0, cw, ch), 30, outline=NAVY, width=5)
    text_c(cd, (cw / 2, 56), "KOMENTAR TERATAS #4", F("pb", 46), WHITE)
    # avatar + baris kosong
    hot = t >= cs(11)
    av_col = YEL if hot else (215, 220, 230)
    cd.ellipse((50, 160, 150, 260), fill=av_col, outline=NAVY, width=5)
    text_c(cd, (100, 210), "?", F("pb", 56), NAVY)
    box = (180, 160, cw - 50, 440)
    if hot:
        cd.rounded_rectangle(box, 22, fill=(255, 244, 205))
        dashed(cd, [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3]), (box[0], box[1])],
               YEL, w=7, phase=(t * 60))
        msg = "namamu di sini?"
        n = int(clamp((t - cs(11) - 0.1) / 0.8) * len(msg))
        f = F("pb", 50)
        cd.text((box[0] + 30, 300), msg[:n], font=f, fill=NAVY, anchor="lm")
        if int(t * 2.5) % 2 == 0:
            x = box[0] + 34 + f.getlength(msg[:n])
            cd.rectangle((x, 272, x + 6, 330), fill=NAVY)
    else:
        dashed(cd, [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3]), (box[0], box[1])],
               (170, 178, 195), w=6)
        for k, ww in enumerate((420, 300)):
            cd.rounded_rectangle((box[0] + 30, 230 + k * 80, box[0] + 30 + ww, 258 + k * 80), 14, fill=(228, 232, 240))
    # baris like
    text_c(cd, (cw / 2, 520), "0 like   ·   0 balasan" if not hot else "like terbanyak = tampil di sini", F("pm", 34),
           GREY_T if not hot else RED)
    paste_c(img, L, W / 2, 800, pop(t, SC[1] + 0.05))
    # stempel KOSONG
    if not hot:
        p = pop(t, cs(10))
        if p > 0:
            S = Image.new("RGBA", (400, 140), (0, 0, 0, 0)); sd = ImageDraw.Draw(S)
            sd.rounded_rectangle((6, 6, 394, 134), 18, outline=RED, width=10)
            text_c(sd, (200, 72), "KOSONG", F("pb", 76), RED)
            paste_c(img, S, W / 2 + 120, 830, 1.6 - 0.6 * p if p < 1 else 1.0, -10, min(1, p))
    draw_aru(img, 300, 1460, 330, t)
    # gelembung Aru
    if hot:
        p = pop(t, cs(12))
        if p > 0:
            B = Image.new("RGBA", (420, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
            bd.rounded_rectangle((0, 0, 420, 110), 28, fill=NAVY)
            bd.polygon([(60, 105), (110, 105), (40, 148)], fill=NAVY)
            text_c(bd, (210, 55), "giliranmu!", F("pb", 46), YEL)
            paste_c(img, B, 640, 1210, p)


def scene2(img, t):
    """kantor 8 km, tarif dasar ±Rp22.400 (8 × Rp2.800, KP 667/2022)."""
    L, cd = card(820, 400)
    icon_house(cd, 110, 220, 1.0)
    icon_office(cd, 710, 210, 1.0)
    pts = [(190, 270), (330, 200), (480, 290), (630, 230)]
    dashed(cd, pts, YEL, w=10, phase=-t * 50)
    u = eout((t - SC[2] - 0.2) / 2.0)
    # motor kecil berjalan di rute
    seg = u * (len(pts) - 1); i = min(len(pts) - 2, int(seg)); f_ = seg - i
    mx = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f_; my = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f_
    icon_motor(cd, mx, my - 30, 0.35)
    if t >= cs(14):
        p = clamp((t - cs(14)) / 0.25)
        cd.rounded_rectangle((330, 60, 490, 140), 24, fill=NAVY)
        text_c(cd, (410, 100), "8 km", F("pb", int(30 + 18 * p)), WHITE)
    paste_c(img, L, W / 2, 680, pop(t, SC[2] + 0.05))
    # kartu tarif dasar
    p = pop(t, cs(16) - 0.1)
    if p > 0:
        T, td = card(560, 330, fill=WHITE)
        td.rounded_rectangle((0, 0, 560, 90), 30, fill=TEAL); td.rectangle((0, 50, 560, 90), fill=TEAL)
        td.rounded_rectangle((0, 0, 560, 330), 30, outline=NAVY, width=5)
        text_c(td, (280, 48), "TARIF DASAR OJOL", F("pb", 38), WHITE)
        v = int(round(22400 * eout((t - cs(17)) / 0.6) / 100.0) * 100)
        text_c(td, (280, 175), "±" + rp(v), F("pb", 84), NAVY)
        text_c(td, (280, 270), "8 km × Rp2.800/km", F("pm", 34), GREY_T)
        paste_c(img, T, 640, 1180, p)
    draw_aru(img, 220, 1470, 300, t)


def scene3(img, t):
    """pas hujan semua orang pesan -> tarif naik Rp22.400 -> Rp30.000 (contoh)."""
    d = ImageDraw.Draw(img)
    L = Image.new("RGBA", (W, 520), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    icon_cloud(ld, 540, 110, 1.4)
    rl = Image.new("RGBA", (W, 520), (0, 0, 0, 0)); rd = ImageDraw.Draw(rl)
    for k in range(14):
        x = 380 + (k * 53) % 330; y = (190 + (k * 97 + t * 900) % 330)
        rd.line([(x, y), (x - 10, y + 40)], fill=(127, 178, 238, 220), width=6)
    L.alpha_composite(rl)
    # HP pemesan muncul bertahap
    pos = [(170, 330), (330, 380), (750, 380), (910, 330), (250, 470), (830, 470), (420, 470), (660, 470)]
    t0 = cs(19); t1 = cs(21) + 0.3
    for j, (x, y) in enumerate(pos):
        tj = t0 + (t1 - t0) * j / len(pos)
        p = pop(t, tj, 0.3)
        if p > 0:
            ph = Image.new("RGBA", (160, 220), (0, 0, 0, 0)); pd = ImageDraw.Draw(ph)
            icon_phone(pd, 80, 120, 0.85, alert=True)
            paste_c(L, ph, x, y - 60, p * 0.85, 8 * math.sin(t * 5 + j))
    img.alpha_composite(L, (0, 400))
    # counter tarif
    p = pop(t, cs(22) - 0.15)
    if p > 0:
        T, td = card(700, 330, fill=WHITE)
        text_c(td, (350, 60), "TARIF PAS HUJAN", F("pb", 40), NAVY)
        u = eio((t - cs(23)) / 1.0)
        v = int(round((22400 + 7600 * u) / 100.0) * 100)
        hot = u > 0
        text_c(td, (310, 180), rp(v), F("pb", 104), RED if hot else NAVY)
        if hot:
            arrow(td, 620, 230, 620, 120, RED, w=18, head=40)
        if t >= cs(25):
            td.rounded_rectangle((210, 250, 490, 310), 24, fill=YEL)
            text_c(td, (350, 281), "contoh ilustrasi", F("pb", 30), NAVY)
        paste_c(img, T, W / 2, 1220, p)


def scene4(img, t):
    """12 hari hujan × pulang pergi = Rp720.000 sebulan."""
    cw, ch = 760, 560
    L, cd = card(cw, ch)
    cd.rounded_rectangle((0, 0, cw, 96), 30, fill=NAVY); cd.rectangle((0, 50, cw, 96), fill=NAVY)
    cd.rounded_rectangle((0, 0, cw, ch), 30, outline=NAVY, width=5)
    text_c(cd, (cw / 2, 50), "SEBULAN KERJA", F("pb", 42), WHITE)
    rainy = [1, 2, 5, 7, 8, 11, 12, 14, 16, 19, 20, 22]
    t0 = cs(26); t1 = cs(27) - 0.1
    for k in range(25):
        r_, c_ = divmod(k, 5)
        x = 60 + c_ * 132; y = 125 + r_ * 84
        cd.rounded_rectangle((x, y, x + 112, y + 70), 14, fill=LIGHT)
        cd.text((x + 14, y + 8), str(k + 1), font=F("pm", 24), fill=GREY_T)
        if k in rainy:
            j = rainy.index(k)
            tj = t0 + (t1 - t0) * j / 12
            if t >= tj:
                pp = clamp((t - tj) / 0.15)
                cd.rounded_rectangle((x, y, x + 112, y + 70), 14, fill=(200, 222, 248))
                cd.text((x + 14, y + 8), str(k + 1), font=F("pm", 24), fill=NAVY)
                icon_drop(cd, x + 74, y + 44, 0.9 * pp, col=(60, 120, 210))
    paste_c(img, L, W / 2, 790, pop(t, SC[4] + 0.05))
    if t >= cs(26) + 0.3:
        n = min(12, sum(1 for j in range(12) if t >= t0 + (t1 - t0) * j / 12))
        B = Image.new("RGBA", (300, 110), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 300, 100), 50, fill=(60, 120, 210))
        text_c(bd, (150, 50), f"{n} hari", F("pb", 50), WHITE)
        paste_c(img, B, 780, 470, pop(t, cs(26) + 0.3))
    p = pop(t, cs(27))
    if p > 0:
        B = Image.new("RGBA", (360, 110), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 360, 100), 50, fill=YEL)
        text_c(bd, (180, 50), "× 2 pulang pergi", F("pb", 38), NAVY)
        paste_c(img, B, 330, 470, p, -4)
    p = pop(t, cs(28))
    if p > 0:
        T, td = card(700, 250, fill=RED, outline=NAVY)
        u = eout((t - cs(28)) / 0.8)
        text_c(td, (350, 100), rp(int(round(720000 * u / 1000) * 1000)), F("pb", 100), WHITE)
        text_c(td, (350, 190), "Rp30.000 × 2 × 12 · sebulan", F("pm", 34), WHITE)
        paste_c(img, T, W / 2, 1270, p)


def scene5(img, t):
    """motor sendiri: bensin Rp48.000 — tapi ada yang bocor."""
    L = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    ld.ellipse((260, 330, 820, 390), fill=(200, 210, 225))
    icon_motor(ld, 540, 240, 1.5)
    paste_c(img, L, W / 2, 700 + 4 * math.sin(t * 6), pop(t, SC[5] + 0.05))
    p = pop(t, cs(31) - 0.1)
    if p > 0:
        T, td = card(760, 300)
        td.rounded_rectangle((40, 40, 150, 150), 24, fill=RED)
        td.rectangle((70, 70, 120, 110), fill=WHITE)
        td.text((185, 70), "BENSIN SEBULAN", font=F("pb", 40), fill=NAVY, anchor="lm")
        u = eout((t - cs(32)) / 0.6)
        td.text((185, 150), rp(int(round(48000 * u / 1000) * 1000)), font=F("pb", 84), fill=GREEN, anchor="lm")
        text_c(td, (380, 250), "192 km ÷ 40 km/l × Rp10.000", F("pm", 34), GREY_T)
        paste_c(img, T, W / 2, 1090, p)
    # Si Bocor
    tb = t - cs(33)
    if tb > 0:
        x = 1180 - 300 * eout(tb / 0.6)
        hop = abs(math.sin(tb * 10)) * 14
        for j in range(3):
            ct = tb - 0.3 - j * 0.18
            if ct > 0:
                paste_c(img, coin(), 820 + j * 40, 1250 + min(220, 700 * ct * ct), 1, ct * 200)
        paste_c(img, bocor_img(), x, 1400 - hop, 0.8)
        p = pop(t, cs(34))
        if p > 0:
            B = Image.new("RGBA", (380, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
            bd.rounded_rectangle((0, 0, 380, 110), 28, fill=NAVY)
            bd.polygon([(330, 60), (330, 100), (385, 90)], fill=NAVY)
            text_c(bd, (190, 55), "ada yang bocor!", F("pb", 40), YEL)
            paste_c(img, B, 560, 1380, p)


def scene6(img, t):
    """biaya pendamping: parkir, jas hujan, servis + oli per bulan; Si Bocor di parkir."""
    rows = [("P", "Parkir", "Rp6.000 × 12 hari", "Rp72.000", cs(35), RED),
            ("J", "Jas hujan", "Rp120 rb ÷ 6 bulan", "Rp20.000", cs(37), YEL),
            ("S", "Servis + oli", "±Rp120 rb ÷ 2 bulan", "Rp60.000", cs(38), TEAL)]
    for k, (ic, name, calc, val, t0, col) in enumerate(rows):
        p = pop(t, t0 - 0.05)
        if p <= 0: continue
        T, td = card(820, 220)
        td.rounded_rectangle((30, 40, 170, 180), 28, fill=col)
        if ic == "P":
            text_c(td, (100, 110), "P", F("pb", 96), WHITE)
        elif ic == "J":
            icon_jacket(td, 100, 112, 0.62, col=WHITE)
        else:
            td.ellipse((52, 62, 148, 158), outline=WHITE, width=16)
            td.rectangle((92, 40, 108, 70), fill=WHITE); td.rectangle((92, 150, 108, 180), fill=WHITE)
        td.text((200, 78), name, font=F("pb", 46), fill=NAVY, anchor="lm")
        td.text((200, 148), calc, font=F("pm", 32), fill=GREY_T, anchor="lm")
        td.text((790, 110), val, font=F("pb", 52), fill=NAVY, anchor="rm")
        paste_c(img, T, W / 2, 560 + k * 250, p)
    p = pop(t, cs(39))
    if p > 0:
        B = Image.new("RGBA", (400, 100), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 400, 90), 45, fill=NAVY)
        text_c(bd, (200, 45), "dibagi per bulan", F("pb", 38), WHITE)
        paste_c(img, B, 330, 1330, p, -3)
    # Si Bocor menunjuk parkir (bocor terbesar)
    paste_c(img, bocor_img(), 860, 1340 - abs(math.sin(t * 6)) * 10, 0.8 * pop(t, cs(35) + 0.2))
    p = pop(t, cs(36))
    if p > 0:
        B = Image.new("RGBA", (330, 90), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 330, 80), 40, fill=RED)
        text_c(bd, (165, 40), "bocor terbesar!", F("pb", 34), WHITE)
        paste_c(img, B, 760, 425, p, 4)


def scene7(img, t):
    """payoff: ojol Rp720.000 vs motor Rp200.000 -> selisih Rp520.000/bulan."""
    d = ImageDraw.Draw(img)
    base = 1060; maxh = 500
    bars = [("OJOL", 720000, RED, 330, SC[7] + 0.1), ("MOTOR", 200000, TEAL, 750, cs(41) - 0.1)]
    for name, v, col, x, t0 in bars:
        u = eout((t - t0) / 0.7)
        if u <= 0: continue
        h = maxh * v / 720000 * u
        d.rounded_rectangle((x - 130 + 8, base - h + 10, x + 130 + 8, base + 10), 26, fill=(20, 33, 91, 60))
        d.rounded_rectangle((x - 130, base - h, x + 130, base), 26, fill=col, outline=NAVY, width=5)
        text_c(d, (x, base - h - 50), rp(int(round(v * u / 1000) * 1000)), F("pb", 56), NAVY)
        text_c(d, (x, base + 50), name, F("pb", 46), NAVY)
    d.line([(160, base), (920, base)], fill=NAVY, width=6)
    p = pop(t, cs(43) - 0.05)
    if p > 0:
        T, td = card(760, 230, fill=YEL)
        text_c(td, (380, 70), "SELISIH", F("pb", 42), NAVY)
        text_c(td, (380, 158), "Rp520.000/bulan", F("pb", 74), NAVY)
        paste_c(img, T, W / 2, 1360, p, 1.5 * math.sin(t * 3))


def scene8(img, t):
    """tips: simpan jas hujan di jok; terpaksa ojol -> pesan sebelum deras."""
    p = pop(t, SC[8] + 0.05)
    if p > 0:
        T, td = card(820, 380)
        icon_motor(td, 230, 230, 0.95)
        icon_jacket(td, 210, 110, 0.7)
        td.text((450, 130), "Jas hujan", font=F("pb", 52), fill=NAVY, anchor="lm")
        td.text((450, 200), "selalu di jok", font=F("pb", 52), fill=TEAL, anchor="lm")
        if t >= cs(46): icon_check(td, 720, 300, 1.0)
        paste_c(img, T, W / 2, 680, p)
    p = pop(t, cs(47) - 0.05)
    if p > 0:
        T, td = card(820, 380)
        icon_cloud(td, 180, 150, 0.9)
        icon_clock(td, 190, 250, 0.8, t)
        td.text((360, 110), "Terpaksa ojol?", font=F("pb", 46), fill=NAVY, anchor="lm")
        td.text((360, 190), "pesan sebelum", font=F("pb", 52), fill=RED, anchor="lm")
        td.text((360, 260), "hujan deras", font=F("pb", 52), fill=RED, anchor="lm")
        if t >= cs(49): icon_check(td, 740, 320, 0.8)
        paste_c(img, T, W / 2, 1140, p)


def scene9(img, t):
    """penutup: kutipan + tim ojol vs tim jas hujan, bela di komentar."""
    p = pop(t, SC[9] + 0.05)
    if p > 0:
        T, td = card(820, 300, fill=NAVY)
        text_c(td, (410, 105), "Hujannya gratis,", F("pb", 54), WHITE)
        mahal = t >= cs(52)
        f = F("pb", 54); a, b = "buru-burunya yang ", "mahal."
        wa, wb = f.getlength(a), f.getlength(b); x0 = 410 - (wa + wb) / 2
        if mahal:
            td.rounded_rectangle((x0 + wa - 8, 160, x0 + wa + wb + 8, 240), 14, fill=YEL)
        td.text((x0, 200), a, font=f, fill=WHITE, anchor="lm")
        td.text((x0 + wa, 200), b, font=f, fill=NAVY if mahal else WHITE, anchor="lm")
        paste_c(img, T, W / 2, 620, p)
    for k, (s, col, t0) in enumerate((("TIM OJOL", RED, cs(53)), ("TIM JAS HUJAN", TEAL, cs(54)))):
        p = pop(t, t0)
        if p <= 0: continue
        f = F("pb", 46); w = int(f.getlength(s) + 70)
        B = Image.new("RGBA", (w + 12, 124), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((8, 12, w + 8, 122), 55, fill=(20, 33, 91, 60))
        bd.rounded_rectangle((0, 0, w, 110), 55, fill=col, outline=NAVY, width=5)
        text_c(bd, (w / 2, 55), s, f, WHITE)
        beat = 1 + 0.05 * math.sin((t - t0) * 7 + k * math.pi)
        paste_c(img, B, W / 2, 900 if k == 0 else 1080, p * beat, -2 if k == 0 else 2)
    text_c(ImageDraw.Draw(img), (W / 2, 990), "vs", F("pb", 44), NAVY) if t >= cs(54) else None
    p = pop(t, cs(55) - 0.05)
    if p > 0:
        B = Image.new("RGBA", (820, 240), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 820, 190), 34, fill=WHITE, outline=NAVY, width=5)
        bd.polygon([(110, 186), (180, 186), (90, 236)], fill=WHITE, outline=NAVY)
        bd.line([(112, 189), (178, 189)], fill=WHITE, width=8)
        text_c(bd, (410, 70), "Bela di komentar!", F("pb", 52), NAVY)
        text_c(bd, (410, 138), "like terbanyak tampil di part berikutnya + namamu", F("pm", 28), GREY_T)
        paste_c(img, B, W / 2, 1330, p)


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9]


def draw_notes(img, k):
    lines = NOTES.get(k)
    if not lines: return
    d = ImageDraw.Draw(img)
    for j, s in enumerate(lines):
        f = fit("pm", 28, s, W - 2 * SAFE_X)
        d.text((W / 2, 1712 + j * 40), s, font=f, fill=GREY_T, anchor="mm")


def frame(t):
    k = scene_of(t)
    ts = t - SC[k]
    img = (bg_scene0() if k == 0 else bg_rest()).copy()
    if k > 0:
        rain(img, t, n=36, col=(170, 190, 220), alpha=110, seed=5, length=50, width=3)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        SCENES[k](layer, t)
        s = 0.94 + 0.06 * back(ts / 0.4)
        if s < 0.999 or s > 1.001:
            paste_c(img, layer, W / 2, H / 2, s)
        else:
            img.alpha_composite(layer)
        img.alpha_composite(header(), (0, 240))  # header y≈300 (PRB-41); bukan di dtk 0-3
    else:
        scene0(img, t)
        if t >= CT_SRC:
            a = clamp((t - CT_SRC) / 0.3)
            L = Image.new("RGBA", (W, 60), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
            s_ = NOTES[0][0]; f = fit("pm", 28, s_, W - 2 * SAFE_X)
            ld.text((W / 2, 30), s_, font=f, fill=INK, anchor="mm")
            paste_c(img, L, W / 2, 1712, 1, 0, a)
    draw_sub(img, t)
    if k > 0:
        draw_notes(img, k)
    # ajakan follow, teks kecil dtk 10-15 (PRB-4), di bawah header
    if FOLLOW[0] <= t < FOLLOW[1]:
        f = F("pb", 30); s_ = "follow @kabar.arunika · tiap pagi 1 hitungan uang"
        tw = f.getlength(s_)
        pl = Image.new("RGBA", (int(tw) + 60, 60), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
        pd.rounded_rectangle((0, 0, tw + 60, 60), 30, fill=TEAL)
        pd.text((30, 30), s_, font=f, fill=WHITE, anchor="lm")
        a = min(clamp((t - FOLLOW[0]) / 0.25), clamp((FOLLOW[1] - t) / 0.25))
        paste_c(img, pl, W / 2, 1480, 1, 0, a)
    # logo kecil di penutup (≤1,5 dtk, PRB-3)
    la = clamp((t - (TOTAL - 1.5)) / 0.3)
    if la > 0:
        paste_c(img, logo_w(300), W / 2, 1730, 0.9 + 0.1 * back(la), 0, la)
    # progress bar: bukan di dtk 0-3 (PRB-34)
    if t >= 3.0:
        ImageDraw.Draw(img).rectangle((0, H - 14, int(W * t / TOTAL), H), fill=YEL)
    return img.convert("RGB")


CT_SRC = G.CT0  # sumber muncul bersama counter (PRB-39)


def events():
    ev = [{"t": SC[k], "sfx": "whoosh", "gain": 0.30} for k in range(1, NS)]
    ev.append({"t": G.CT0, "sfx": "pop", "gain": 0.3})        # counter mulai bergerak
    ev.append({"t": G.CT1, "sfx": "ding", "gain": 0.25})
    for i in (4, 10, 12, 14, 16, 26, 27, 28, 31, 35, 37, 38, 41, 46, 47, 49, 53, 54, 55):
        ev.append({"t": cs(i), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": cs(33), "sfx": "cring", "gain": 0.45})
    ev.append({"t": cs(36), "sfx": "cring", "gain": 0.35})
    ev.append({"t": cs(43), "sfx": "ding", "gain": 0.35})
    json.dump(sorted(ev, key=lambda e: e["t"]), open("events.json", "w"), indent=1)
    print(len(ev), "events")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "events":
        events()
    elif cmd == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        ims = []
        for tt in ts:
            im = frame(tt); im.save(f"still_{tt:.2f}.png"); ims.append(im.resize((360, 640)))
        cols = 6; rows = math.ceil(len(ims) / cols)
        sh = Image.new("RGB", (360 * cols, 640 * rows), WHITE)
        for j, im in enumerate(ims):
            sh.paste(im, ((j % cols) * 360, (j // cols) * 640))
        sh.save("sheet.png"); print("sheet.png")
    elif cmd == "video":
        out, a, b = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                              "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        n0, n1 = round(a * FPS), round(b * FPS)
        for n in range(n0, n1):
            p.stdin.write(frame(n / FPS).tobytes())
        p.stdin.close(); p.wait(); print(out, n1 - n0, "frames")

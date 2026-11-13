"""Renderer ARN-44 "Mana Lebih Hemat? #6 — emas buyback" — gaya Flat 2D latar terang (sampel 1).
Salinan render_flat.py (#5: helper kartu, koin, Si Bocor, panah, Aru, logo, subtitle, sfx) dengan frame 0 dari
render_gaya_emas.py (Aru memeluk emas 1 g, Si Bocor menggigit, counter Rp2.566.400 -> Rp2.375.000 dtk 1,6-2,6).
Pemakaian (dari folder kerja pagi/build/emas, setelah align_emas.py -> timing.json):
  TOTAL=51.6 python3 ../../render_flat_emas.py events
  TOTAL=51.6 python3 ../../render_flat_emas.py stills 0,2,...
  TOTAL=51.6 python3 ../../render_flat_emas.py video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw

import render_gaya_emas as E
from render_gaya_frame0 import (F, clamp, eio, rp, pills, NAVY, TEAL, YEL, WHITE, GREY_T, RED, SAFE_X)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "51.6"))
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
GREEN = (46, 160, 110); INK = (60, 66, 92); LIGHT = (232, 238, 246)
GOLD = (245, 190, 60); GOLD_D = (196, 138, 22); GOLD_L = (255, 224, 138)

TIM = json.load(open("timing.json"))
def cs(i): return TIM[i]["start"] + LEAD
def ce(i): return TIM[i]["end"] + LEAD

SCENE_CHUNK = [0, 6, 13, 17, 20, 24, 29, 34, 39, 45]
SC = [0.0] + [cs(i) - 0.25 for i in SCENE_CHUNK[1:]] + [TOTAL]
NS = len(SCENE_CHUNK)
FOLLOW = (10.4, 15.0)          # PRB-4: ajakan follow teks kecil dtk 10-15
SRC = "Logam Mulia 1 g, 10 Nov 2026 (Kontan/Fortune IDN)"
NOTES = {
    0: (SRC,),
    1: ("Kursi komentar teratas: masih kosong",),
    2: (SRC, "PPh 0,25% = Rp6.400 (Fortune IDN, 10 Nov 2026)"),
    3: (SRC,),
    4: ("selisih jual–buyback Rp185.000 + PPh beli Rp6.400",),
    5: ("Rp2.375.000 × 1,081 ≈ Rp2.566.400",),
    6: ("*ilustrasi, bukan prediksi · harga emas bisa naik & turun",),
    7: ("NPWP 1,5% · tanpa NPWP 3% · PMK 34/2017 · 1 gram: belum kena",),
    8: ("harga berubah tiap hari · cek logammulia.com",),
}


def scene_of(t):
    for k in range(NS):
        if t < SC[k + 1]: return k
    return NS - 1


# ---------- easing ----------
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


def card(w, h, fill=WHITE, r=30, outline=NAVY, ow=5):
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 12, w + 10, h + 12), r, fill=(20, 33, 91, 45))
    d.rounded_rectangle((0, 0, w, h), r, fill=fill, outline=outline, width=ow)
    return im, d


def head_card(w, h, title, col=TEAL, size=40, fill=WHITE):
    L, cd = card(w, h, fill=fill)
    cd.rounded_rectangle((0, 0, w, 96), 30, fill=col); cd.rectangle((0, 50, w, 96), fill=col)
    cd.rounded_rectangle((0, 0, w, h), 30, outline=NAVY, width=5)
    text_c(cd, (w / 2, 50), title, fit("pb", size, title, w - 60), WHITE if col != YEL else NAVY)
    return L, cd


def coin(r=26):
    im = Image.new("RGBA", (2 * r + 6, 2 * r + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((3, 3, 2 * r + 3, 2 * r + 3), fill=(255, 194, 60), outline=(217, 154, 31), width=4)
    text_c(d, (r + 3, r + 3), "Rp", F("pb", int(r * 0.75)), (154, 106, 16))
    return im


def gold_bar(d, cx, cy, s=1.0, label="1 g"):
    w, h = 180 * s, 100 * s
    p = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2 - 16 * s, cy + h / 2), (cx - w / 2 + 16 * s, cy + h / 2)]
    d.polygon(p, fill=GOLD); d.line(p + [p[0]], fill=NAVY, width=max(2, int(6 * s)), joint="curve")
    d.line([(cx - w / 2 + 14 * s, cy - h / 2 + 14 * s), (cx - 10 * s, cy - h / 2 + 14 * s)], fill=GOLD_L, width=max(2, int(8 * s)))
    if label:
        text_c(d, (cx, cy + 8 * s), label, F("pb", int(40 * s)), (122, 84, 10))


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


def icon_check(d, cx, cy, s=1.0, col=GREEN):
    d.ellipse((cx - 40 * s, cy - 40 * s, cx + 40 * s, cy + 40 * s), fill=col)
    d.line([(cx - 18 * s, cy), (cx - 4 * s, cy + 15 * s), (cx + 20 * s, cy - 14 * s)], fill=WHITE, width=int(10 * s),
           joint="curve")


def icon_cross(d, cx, cy, s=1.0, col=RED):
    d.ellipse((cx - 40 * s, cy - 40 * s, cx + 40 * s, cy + 40 * s), fill=col)
    for a, b in (((-15, -15), (15, 15)), ((15, -15), (-15, 15))):
        d.line([(cx + a[0] * s, cy + a[1] * s), (cx + b[0] * s, cy + b[1] * s)], fill=WHITE, width=int(10 * s))


def bubble(text, col=NAVY, fg=YEL, size=44, tail="left"):
    f = F("pb", size); w = int(f.getlength(text) + 70)
    B = Image.new("RGBA", (w, 150), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
    bd.rounded_rectangle((0, 0, w, 110), 28, fill=col)
    if tail == "left":
        bd.polygon([(50, 105), (100, 105), (30, 148)], fill=col)
    else:
        bd.polygon([(w - 100, 105), (w - 50, 105), (w - 30, 148)], fill=col)
    text_c(bd, (w / 2, 55), text, f, fg)
    return B


def stamp(text, col=RED, size=70):
    f = F("pb", size); w = int(f.getlength(text) + 80)
    S = Image.new("RGBA", (w, size + 70), (0, 0, 0, 0)); sd = ImageDraw.Draw(S)
    sd.rounded_rectangle((6, 6, w - 6, size + 64), 18, outline=col, width=10)
    text_c(sd, (w / 2, (size + 70) / 2), text, f, col)
    return S


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
    d.ellipse((140, 600, 940, 1400), fill=(252, 236, 196))
    for k in range(10):
        a = k * math.pi / 5; r0, r1 = 420, 470
        d.line([(540 + r0 * math.cos(a), 1000 + r0 * math.sin(a)), (540 + r1 * math.cos(a), 1000 + r1 * math.sin(a))],
               fill=(250, 214, 120), width=10)
    floor = 1440
    d.rectangle((0, floor, W, H), fill=(218, 223, 232)); d.line([(0, floor), (W, floor)], fill=NAVY, width=5)
    return img


@lru_cache(None)
def bg_rest():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((90, 480, 990, 1380), fill=(250, 240, 214))
    d.rectangle((0, 1490, W, H), fill=(224, 228, 236))
    return img


@lru_cache(None)
def header():
    L = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F("pb", 34); s1 = "MANA LEBIH HEMAT?"; s2 = "#6"
    w1 = f.getlength(s1); w2 = f.getlength(s2)
    tot = w1 + w2 + 52 + 40 + 12
    x0 = (W - tot) / 2
    d.rounded_rectangle((x0, 30, x0 + w1 + 52, 96), 33, fill=NAVY)
    d.text((x0 + 26, 63), s1, font=f, fill=WHITE, anchor="lm")
    x1 = x0 + w1 + 52 + 12
    d.rounded_rectangle((x1, 30, x1 + w2 + 40, 96), 33, fill=YEL)
    d.text((x1 + 20, 63), s2, font=f, fill=NAVY, anchor="lm")
    return L


# ---------- subtitle 1 baris (PRB-37) ----------
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
    paste_c(img, sub_layer(i), W / 2, 1600, sc)


# ---------- adegan ----------
def scene0(img, t):
    """frame 0 = sampel 1: Aru memeluk emas, Si Bocor menggigit, counter Rp2.566.400 -> Rp2.375.000 dtk 1,6-2,6."""
    sc = 2.45 + 0.08 * eio((t - 1.4) / 1.4)   # zoom pelan, visual berganti ~dtk 1,5
    E.hero(img, t, sc, 540, 1450, "#FCECC4")
    pills(img, [["EMAS,", "KOK"], ["LANGSUNG", "RUGI?"]], 290, size=76, keyword="RUGI")
    # "kapan balik modal?" -> lencana kalender + tanda tanya
    p = pop(t, cs(5))
    if p > 0:
        L = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.ellipse((20, 20, 280, 280), fill=YEL, outline=NAVY, width=8)
        d.rounded_rectangle((85, 80, 215, 200), 16, fill=WHITE, outline=NAVY, width=7)
        d.rectangle((88, 83, 212, 115), fill=RED)
        text_c(d, (150, 160), "?", F("pb", 72), NAVY)
        paste_c(img, L, 870, 640, 0.72 * p, 6 * math.sin(t * 4))


def scene1(img, t):
    """komentar teratas #5: janjinya tampil di sini, masih kosong -> kursinya menunggu namamu (PRB-43)."""
    cw, ch = 820, 600
    L, cd = card(cw, ch)
    cd.rounded_rectangle((0, 0, cw, 110), 30, fill=TEAL); cd.rectangle((0, 60, cw, 110), fill=TEAL)
    cd.rounded_rectangle((0, 0, cw, ch), 30, outline=NAVY, width=5)
    text_c(cd, (cw / 2, 56), "KOMENTAR TERATAS #5", F("pb", 46), WHITE)
    hot = t >= cs(11)
    cd.ellipse((50, 160, 150, 260), fill=YEL if hot else (215, 220, 230), outline=NAVY, width=5)
    text_c(cd, (100, 210), "?", F("pb", 56), NAVY)
    box = (180, 160, cw - 50, 440)
    rect = [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3]), (box[0], box[1])]
    if hot:
        cd.rounded_rectangle(box, 22, fill=(255, 244, 205))
        dashed(cd, rect, YEL, w=7, phase=(t * 60))
        msg = "namamu di sini?"
        n = int(clamp((t - cs(12) + 0.2) / 0.8) * len(msg))
        f = F("pb", 50)
        cd.text((box[0] + 30, 300), msg[:n], font=f, fill=NAVY, anchor="lm")
        if int(t * 2.5) % 2 == 0:
            x = box[0] + 34 + f.getlength(msg[:n])
            cd.rectangle((x, 272, x + 6, 330), fill=NAVY)
    else:
        dashed(cd, rect, (170, 178, 195), w=6)
        for k, ww in enumerate((420, 300)):
            cd.rounded_rectangle((box[0] + 30, 230 + k * 80, box[0] + 30 + ww, 258 + k * 80), 14, fill=(228, 232, 240))
    text_c(cd, (cw / 2, 520), "like terbanyak = tampil di sini" if t >= cs(9) else "0 komentar · #5 ojol vs jas hujan",
           F("pm", 34), RED if t >= cs(9) else GREY_T)
    paste_c(img, L, W / 2, 800, pop(t, SC[1] + 0.05))
    if not hot:
        p = pop(t, cs(10))
        if p > 0:
            paste_c(img, stamp("KOSONG", size=76), W / 2 + 120, 830, 1.6 - 0.6 * p if p < 1 else 1.0, -10, min(1, p))
    draw_aru(img, 300, 1430, 300, t)
    if hot:
        p = pop(t, cs(12))
        if p > 0:
            paste_c(img, bubble("giliranmu!", size=46), 640, 1210, p)


def scene2(img, t):
    """harga beli emas Antam 1 g: Rp2.560.000 + PPh 0,25% Rp6.400 = Rp2.566.400."""
    L, cd = card(820, 330, fill=(255, 248, 228))
    gold_bar(cd, 190, 170, 1.4, "1 g")
    cd.text((360, 120), "EMAS ANTAM", font=F("pb", 56), fill=NAVY, anchor="lm")
    cd.text((360, 200), "1 gram", font=F("pb", 56), fill=GOLD_D, anchor="lm")
    if t >= cs(14):
        cd.rounded_rectangle((360, 240, 640, 300), 30, fill=NAVY)
        text_c(cd, (500, 270), "Logam Mulia", F("pb", 32), WHITE)
    paste_c(img, L, W / 2, 640, pop(t, SC[2] + 0.05))
    p = pop(t, cs(15) - 0.1)
    if p > 0:
        T, td = head_card(820, 470, "HARGA BELI", col=NAVY)
        u = eout((t - cs(15)) / 0.9)
        td.text((60, 175), "Harga emas", font=F("pm", 40), fill=GREY_T, anchor="lm")
        td.text((760, 175), rp(int(round(2560000 * u / 1000) * 1000)), font=F("pb", 60), fill=NAVY, anchor="rm")
        if t >= cs(16) - 0.05:
            q = clamp((t - cs(16) + 0.05) / 0.3)
            td.text((60, 265), "+ PPh 0,25%", font=F("pm", 40), fill=GREY_T, anchor="lm")
            td.text((760, 265), "Rp6.400", font=F("pb", 60), fill=RED, anchor="rm")
            td.line([(60, 320), (760, 320)], fill=NAVY, width=4)
            if q >= 1 or t >= cs(16) + 0.3:
                td.rounded_rectangle((40, 345, 780, 440), 24, fill=YEL)
                td.text((70, 392), "Total", font=F("pb", 46), fill=NAVY, anchor="lm")
                td.text((760, 392), "Rp2.566.400", font=F("pb", 64), fill=NAVY, anchor="rm")
        paste_c(img, T, W / 2, 1150, p)


def scene3(img, t):
    """tapi dijual balik? cuma Rp2.375.000 (buyback)."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[3] + 0.05)
    if p > 0:
        T, td = card(760, 220, fill=WHITE)
        gold_bar(td, 120, 110, 0.8, "")
        td.text((240, 70), "BELI", font=F("pb", 42), fill=GREY_T, anchor="lm")
        td.text((240, 145), "Rp2.566.400", font=F("pb", 76), fill=NAVY, anchor="lm")
        paste_c(img, T, W / 2, 610, p)
    if t >= cs(17) + 0.6:
        u = eout((t - cs(17) - 0.6) / 0.6)
        arrow(d, W / 2, 740, W / 2, 740 + 200 * u, RED, w=22, head=48)
        if u > 0.3:
            B = bubble("dijual balik?", col=RED, fg=WHITE, size=40, tail="left")
            paste_c(img, B, 790, 830, min(1, u * 1.3), 3)
    p = pop(t, cs(18) - 0.05)
    if p > 0:
        T, td = card(760, 260, fill=(253, 232, 228), outline=RED, ow=7)
        gold_bar(td, 120, 130, 0.8, "")
        td.text((240, 80), "BUYBACK", font=F("pb", 42), fill=RED, anchor="lm")
        v = 2566400 - (2566400 - 2375000) * eout((t - cs(19)) / 0.9)
        td.text((240, 165), rp(int(round(v / 100) * 100)), font=F("pb", 80), fill=RED, anchor="lm")
        paste_c(img, T, W / 2, 1110, p)
    draw_aru(img, 880, 1480, 240, t)
    p = pop(t, cs(19) + 0.6)
    if p > 0:
        paste_c(img, bubble("cuma segini?!", size=40, tail="right"), 560, 1330, p)


def scene4(img, t):
    """selisih Rp185.000 + pajak beli Rp6.400 = Rp191.400 -> itu bocornya (Si Bocor)."""
    rows = [("Selisih jual–buyback", "Rp185.000", cs(20) - 0.05, NAVY),
            ("+ Pajak beli (PPh)", "Rp6.400", cs(21) - 0.05, NAVY)]
    for k, (name, val, t0, col) in enumerate(rows):
        p = pop(t, t0)
        if p <= 0: continue
        T, td = card(820, 170)
        td.rounded_rectangle((26, 35, 126, 135), 24, fill=GOLD if k == 0 else TEAL)
        text_c(td, (76, 85), "−" if k == 0 else "%", F("pb", 64), NAVY if k == 0 else WHITE)
        td.text((150, 85), name, font=fit("pb", 40, name, 360), fill=NAVY, anchor="lm")
        td.text((790, 85), val, font=F("pb", 50), fill=col, anchor="rm")
        paste_c(img, T, W / 2, 560 + k * 200, p)
    p = pop(t, cs(22) - 0.05)
    if p > 0:
        T, td = card(820, 250, fill=RED)
        text_c(td, (410, 70), "NILAI SUSUT", F("pb", 40), WHITE)
        u = eout((t - cs(22)) / 0.8)
        text_c(td, (410, 160), "−" + rp(int(round(191400 * u / 100) * 100)), F("pb", 96), WHITE)
        paste_c(img, T, W / 2, 1040, p, 1.2 * math.sin(t * 3))
    tb = t - cs(23) + 0.1
    if tb > 0:
        x = 1180 - 330 * eout(tb / 0.6)
        hop = abs(math.sin(tb * 10)) * 14
        for j in range(3):
            ct = tb - 0.3 - j * 0.18
            if ct > 0:
                paste_c(img, coin(), 700 + j * 50, 1220 + min(200, 700 * ct * ct), 1, ct * 200)
        paste_c(img, bocor_img(), x, 1380 - hop, 0.8)
        p = pop(t, cs(23) + 0.2)
        if p > 0:
            paste_c(img, bubble("itu bocornya!", size=42, tail="right"), 470, 1330, p)


def scene5(img, t):
    """buyback harus naik ±8,1% (Rp2.375.000 -> Rp2.566.400) baru balik modal."""
    d = ImageDraw.Draw(img)
    base = 1200; x0b, x1b = 300, 780
    hb = 420; hm = 420 * 2566400 / 2375000
    p = eout((t - SC[5] - 0.05) / 0.6)
    if p > 0:
        # batang buyback sekarang
        h = hb * p
        d.rounded_rectangle((x0b - 120 + 8, base - h + 10, x0b + 120 + 8, base + 10), 26, fill=(20, 33, 91, 60))
        d.rounded_rectangle((x0b - 120, base - h, x0b + 120, base), 26, fill=RED, outline=NAVY, width=5)
        if p > 0.9:
            text_c(d, (x0b, base - h + 50), "Rp2.375.000", fit("pb", 40, "Rp2.375.000", 220), WHITE)
        text_c(d, (x0b, base + 50), "BUYBACK HARI INI", fit("pb", 34, "BUYBACK HARI INI", 300), NAVY)
    # batang target (garis modal)
    ty = base - hm
    dashed(d, [(160, ty), (920, ty)], NAVY, w=6, phase=t * 40)
    d.rounded_rectangle((330, ty - 95, 750, ty - 25), 35, fill=NAVY)
    text_c(d, (540, ty - 60), "modal Rp2.566.400", F("pb", 36), WHITE)
    u = eio((t - cs(25)) / 1.2)
    if t >= cs(25):
        h = hb + (hm - hb) * u
        col = TEAL if u < 1 else GREEN
        d.rounded_rectangle((x1b - 120 + 8, base - h + 10, x1b + 120 + 8, base + 10), 26, fill=(20, 33, 91, 60))
        d.rounded_rectangle((x1b - 120, base - h, x1b + 120, base), 26, fill=col, outline=NAVY, width=5)
        text_c(d, (x1b, base + 50), "HARUS NAIK", F("pb", 34), NAVY)
        arrow(d, x1b, base - 60, x1b, base - h + 70, WHITE, w=16, head=36)
    d.line([(160, base), (920, base)], fill=NAVY, width=6)
    p = pop(t, cs(26) - 0.05)
    if p > 0:
        T, td = card(420, 170, fill=YEL)
        pct = 8.1 * eout((t - cs(26)) / 0.8)
        text_c(td, (210, 85), f"+{pct:.1f}%".replace(".", ","), F("pb", 96), NAVY)
        paste_c(img, T, 540, 560, p, -3)
    p = pop(t, cs(28))
    if p > 0:
        B = Image.new("RGBA", (460, 110), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 460, 100), 50, fill=GREEN)
        text_c(bd, (230, 50), "baru balik modal", F("pb", 44), WHITE)
        paste_c(img, B, W / 2, 1380, p)


def scene6(img, t):
    """kalau naik 1% sebulan -> ±8 bulan; kalau turun -> lebih lama (ilustrasi)."""
    cw, ch = 820, 560
    L, cd = head_card(cw, ch, "KALAU NAIK 1% SEBULAN*", col=NAVY, size=42)
    t0 = cs(31) - 0.1; t1 = cs(31) + 1.0
    late = t >= cs(32)
    for k in range(12):
        r_, c_ = divmod(k, 4)
        x = 50 + c_ * 186; y = 130 + r_ * 135
        lit = k < 8 and t >= t0 + (t1 - t0) * k / 8
        fill = (255, 236, 180) if lit else LIGHT
        if k >= 8 and late:
            fill = (253, 226, 222)
        cd.rounded_rectangle((x, y, x + 160, y + 112), 18, fill=fill, outline=NAVY if lit else (200, 206, 218), width=4)
        cd.text((x + 16, y + 12), f"bln {k + 1}", font=F("pm", 26), fill=NAVY if lit else GREY_T)
        if lit:
            gold_bar(cd, x + 80, y + 72, 0.32, "")
        if k == 7 and lit:
            icon_check(cd, x + 136, y + 18, 0.5)
        if k >= 8 and late:
            text_c(cd, (x + 80, y + 70), "?", F("pb", 48), RED)
    paste_c(img, L, W / 2, 820, pop(t, SC[6] + 0.05))
    p = pop(t, cs(31))
    if p > 0:
        B = Image.new("RGBA", (360, 110), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 360, 100), 50, fill=YEL)
        text_c(bd, (180, 50), "±8 bulan", F("pb", 56), NAVY)
        paste_c(img, B, 330, 1200, p, -3)
    p = pop(t, cs(32))
    if p > 0:
        T, td = card(380, 150, fill=RED)
        arrow(td, 70, 30, 70, 125, WHITE, w=16, head=34)
        td.text((130, 50), "harga turun?", font=F("pb", 34), fill=WHITE, anchor="lm")
        td.text((130, 105), "lebih lama", font=F("pb", 40), fill=YEL if t >= cs(33) else WHITE, anchor="lm")
        paste_c(img, T, 760, 1210, p, 3)


def scene7(img, t):
    """pajak buyback PPh 22: baru kena di atas Rp10 juta, 1,5% (NPWP) / 3% (tanpa NPWP); 1 gram belum kena."""
    p = pop(t, SC[7] + 0.05)
    if p > 0:
        T, td = head_card(820, 560, "PAJAK BUYBACK (PPh 22)", col=TEAL, size=42)
        if t >= cs(36) - 0.05:
            td.text((60, 160), "Kena kalau jual", font=F("pm", 40), fill=GREY_T, anchor="lm")
            td.text((60, 225), "di atas Rp10 juta", font=F("pb", 60), fill=NAVY, anchor="lm")
        if t >= cs(38) - 0.05:
            q = pop(t, cs(38) - 0.05)
            for k, (lab, val) in enumerate((("punya NPWP", "1,5%"), ("tanpa NPWP", "3%"))):
                x = 50 + k * 370
                td.rounded_rectangle((x, 300, x + 350, 500), 24, fill=YEL if k == 0 else LIGHT, outline=NAVY, width=4)
                text_c(td, (x + 175, 360), lab, F("pm", 34), NAVY)
                text_c(td, (x + 175, 440), val, F("pb", int(80 * min(1.0, q))) if q > 0.1 else F("pb", 10), NAVY)
        paste_c(img, T, W / 2, 800, p)
    p = pop(t, cs(38) + 0.5)
    if p > 0:
        T, td = card(640, 150, fill=WHITE, outline=GREEN, ow=7)
        gold_bar(td, 90, 75, 0.5, "")
        td.text((170, 75), "1 gram: belum kena", font=F("pb", 46), fill=GREEN, anchor="lm")
        paste_c(img, T, W / 2, 1270, p, -2)


def scene8(img, t):
    """sebelum beli: cek harga buyback-nya dulu, bukan cuma harga jual."""
    p = pop(t, SC[8] + 0.05)
    if p > 0:
        T, td = head_card(820, 520, "SEBELUM BELI, CEK:", col=NAVY, size=44)
        # baris harga jual (dicoret pelan saat "bukan cuma harga jual")
        on_buy = t >= cs(41) - 0.05
        td.rounded_rectangle((40, 140, 780, 290), 24, fill=LIGHT)
        td.text((80, 215), "Harga jual", font=F("pb", 44), fill=GREY_T, anchor="lm")
        td.text((760, 215), "Rp2.560.000", font=F("pb", 44), fill=GREY_T, anchor="rm")
        if t >= cs(44):
            u = eout((t - cs(44)) / 0.4)
            td.line([(70, 215), (70 + 690 * u, 215)], fill=RED, width=8)
        # baris harga buyback (disorot)
        td.rounded_rectangle((40, 330, 780, 480), 24, fill=YEL if on_buy else LIGHT, outline=NAVY if on_buy else LIGHT,
                             width=5)
        td.text((80, 405), "Harga buyback", font=F("pb", 44), fill=NAVY, anchor="lm")
        td.text((760, 405), "Rp2.375.000", font=F("pb", 44), fill=NAVY, anchor="rm")
        paste_c(img, T, W / 2, 790, p)
        if on_buy:
            q = pop(t, cs(41) + 0.1)
            L = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
            ld.ellipse((20, 20, 130, 130), outline=NAVY, width=14); ld.ellipse((34, 34, 116, 116), fill=(255, 255, 255, 120))
            ld.line([(118, 118), (180, 180)], fill=NAVY, width=22)
            paste_c(img, L, 860 + 10 * math.sin(t * 5), 1120, q)
    draw_aru(img, 260, 1450, 280, t)
    if t >= cs(41):
        paste_c(img, bubble("cek dulu!", size=44), 560, 1250, pop(t, cs(41)))


def scene9(img, t):
    """penutup: yang bikin susut = jual buru-buru; tim simpan vs tim jual cepat, bela di komentar."""
    p = pop(t, SC[9] + 0.05)
    if p > 0:
        T, td = card(820, 300, fill=NAVY)
        text_c(td, (410, 105), "Yang bikin susut:", F("pb", 54), WHITE)
        hot = t >= cs(46)
        f = F("pb", 60); s_ = "jual buru-buru."
        wv = f.getlength(s_)
        if hot:
            td.rounded_rectangle((410 - wv / 2 - 14, 160, 410 + wv / 2 + 14, 245), 14, fill=YEL)
        text_c(td, (410, 203), s_, f, NAVY if hot else WHITE)
        paste_c(img, T, W / 2, 620, p)
    for k, (s, col, t0) in enumerate((("TIM SIMPAN", TEAL, cs(47)), ("TIM JUAL CEPAT", RED, cs(48)))):
        p = pop(t, t0)
        if p <= 0: continue
        f = F("pb", 46); w = int(f.getlength(s) + 70)
        B = Image.new("RGBA", (w + 12, 124), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((8, 12, w + 8, 122), 55, fill=(20, 33, 91, 60))
        bd.rounded_rectangle((0, 0, w, 110), 55, fill=col, outline=NAVY, width=5)
        text_c(bd, (w / 2, 55), s, f, WHITE)
        beat = 1 + 0.05 * math.sin((t - t0) * 7 + k * math.pi)
        paste_c(img, B, W / 2, 900 if k == 0 else 1080, p * beat, -2 if k == 0 else 2)
    if t >= cs(48):
        text_c(ImageDraw.Draw(img), (W / 2, 990), "vs", F("pb", 44), NAVY)
    p = pop(t, cs(49) - 0.05)
    if p > 0:
        B = Image.new("RGBA", (820, 240), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 820, 190), 34, fill=WHITE, outline=NAVY, width=5)
        bd.polygon([(110, 186), (180, 186), (90, 236)], fill=WHITE, outline=NAVY)
        bd.line([(112, 189), (178, 189)], fill=WHITE, width=8)
        text_c(bd, (410, 70), "Bela di komentar!", F("pb", 52), NAVY)
        text_c(bd, (410, 138), "like terbanyak tampil di #7 + namamu", F("pm", 30), GREY_T)
        paste_c(img, B, W / 2, 1310, p)
    # PRB-39: disclaimer di layar (di atas subtitle, tidak bertabrakan dengan logo penutup)
    if t >= SC[9] + 0.3:
        d = ImageDraw.Draw(img)
        text_c(d, (W / 2, 1490), "Bukan saran investasi", F("pm", 30), INK)


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9]


def draw_notes(img, k):
    lines = NOTES.get(k)
    if not lines: return
    d = ImageDraw.Draw(img)
    for j, s in enumerate(lines):
        f = fit("pm", 28, s, W - 2 * SAFE_X)
        d.text((W / 2, 1712 + j * 40), s, font=f, fill=GREY_T, anchor="mm")


CT_SRC = E.CT0  # sumber muncul bersama counter (PRB-39)


def frame(t):
    k = scene_of(t)
    ts = t - SC[k]
    img = (bg_scene0() if k == 0 else bg_rest()).copy()
    if k > 0:
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
    if FOLLOW[0] <= t < FOLLOW[1]:
        f = F("pb", 30); s_ = "follow @kabar.arunika · tiap pagi 1 hitungan uang"
        tw = f.getlength(s_)
        pl = Image.new("RGBA", (int(tw) + 60, 60), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
        pd.rounded_rectangle((0, 0, tw + 60, 60), 30, fill=TEAL)
        pd.text((30, 30), s_, font=f, fill=WHITE, anchor="lm")
        a = min(clamp((t - FOLLOW[0]) / 0.25), clamp((FOLLOW[1] - t) / 0.25))
        paste_c(img, pl, W / 2, 1490, 1, 0, a)
    la = clamp((t - (TOTAL - 1.5)) / 0.3)
    if la > 0:
        paste_c(img, logo_w(300), W / 2, 1730, 0.9 + 0.1 * back(la), 0, la)
    if t >= 3.0:
        ImageDraw.Draw(img).rectangle((0, H - 14, int(W * t / TOTAL), H), fill=YEL)
    return img.convert("RGB")


def events():
    ev = [{"t": SC[k], "sfx": "whoosh", "gain": 0.30} for k in range(1, NS)]
    ev.append({"t": 0.05, "sfx": "cring", "gain": 0.35})        # koin jatuh frame 0
    ev.append({"t": E.CT0, "sfx": "pop", "gain": 0.3})          # counter mulai turun
    ev.append({"t": E.CT1, "sfx": "ding", "gain": 0.25})
    for i in (5, 10, 12, 15, 16, 18, 20, 21, 22, 26, 28, 31, 32, 36, 38, 41, 44, 47, 48, 49):
        ev.append({"t": cs(i), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": cs(23), "sfx": "cring", "gain": 0.45})
    ev.append({"t": cs(26), "sfx": "ding", "gain": 0.35})
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

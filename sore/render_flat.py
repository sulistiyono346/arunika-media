"""Renderer ARN-43 "Diam-diam Makan Listrik" — gaya Flat 2D latar terang.
Salinan pagi/render_flat.py (reel #5 ojol hujan, lolos QA): helper kartu, koin, Si Bocor, panah, Aru resmi,
logo, subtitle 1 baris, sfx. Adegan diganti: rice cooker mode hangat, kulkas, standby, dispenser.
Pemakaian (dari folder build/, setelah align.py -> timing.json):
  TOTAL=54.0 python3 ../render_flat.py events | stills 0,2,... | video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, rp, pills, NAVY, TEAL, YEL, WHITE, CREAM, BROWN, GREY_T, RED, SAFE_X)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "54.0"))
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
GREEN = (46, 160, 110); INK = (60, 66, 92); LIGHT = (232, 238, 246); ORANGE = (255, 138, 30)

TIM = json.load(open("timing.json"))
def cs(i): return TIM[i]["start"] + LEAD
def ce(i): return TIM[i]["end"] + LEAD

SCENE_CHUNK = [0, 4, 10, 15, 20, 26, 33, 39, 45, 52]
SC = [0.0] + [cs(i) - 0.25 for i in SCENE_CHUNK[1:]] + [TOTAL]
NS = len(SCENE_CHUNK)
FOLLOW = (10.4, 15.0)          # PRB-4: ajakan follow teks kecil dtk 10-15
CLOSE = TOTAL - 1.2            # penutup <=1,5 dtk (PRB-3), setelah VO selesai
CT0, CT1 = 1.5, 2.5            # counter Rp0 -> Rp80.000 (PRB-29/36/46)
NOTES = {
    0: ("asumsi rice cooker mode hangat 77 W nyala 24 jam × 30 hari",),
    2: ("sumber: Metro TV News, 29 Okt 2026",),
    3: ("*angka contoh ilustrasi · 10 W × 24 jam × 30 hari",),
    4: ("*angka contoh ilustrasi · 1 kWh/hari × 30 hari",),
    5: ("sumber: Okezone via RCTI+, 13 Agu 2026",),
    6: ("77 W mode hangat · keterangan PLN via detikFinance, 13 Jun 2017",),
    7: ("sumber: PLN via detikFinance, 13 Jun 2017 · tarif R-1 1.300 VA",
        "semua angka perkiraan · tergantung daya, umur alat, cara pakai"),
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
ARU_M = ImageOps.mirror(ARU)
LOGO = trim(Image.open(MEDIA + "/brand/arunika-logo.png").convert("RGBA"))


@lru_cache(None)
def aru_h(h, mirror=False):
    src = ARU_M if mirror else ARU
    r = h / src.height
    return src.resize((int(src.width * r), h), Image.LANCZOS)


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


def draw_aru(layer, cx, bottom, h, t, angle_amp=2.0, mirror=False, jump=0.0):
    im = aru_h(h, mirror)
    b = 7 * math.sin(2 * math.pi * 1.1 * t) - jump
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


def coin(r=26):
    im = Image.new("RGBA", (2 * r + 6, 2 * r + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((3, 3, 2 * r + 3, 2 * r + 3), fill=(255, 194, 60), outline=(217, 154, 31), width=4)
    text_c(d, (r + 3, r + 3), "Rp", F("pb", int(r * 0.75)), (154, 106, 16))
    return im


BOC = (142, 138, 156)
@lru_cache(None)
def bocor_img(mode="normal"):
    im = Image.new("RGBA", (300, 270), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line([(60, 200), (30, 185), (12, 150), (22, 125)], fill=(244, 163, 184), width=7, joint="curve")
    d.polygon([(150, 70), (255, 88), (246, 238), (142, 228)], fill=(201, 162, 107), outline=NAVY)
    d.line([(150, 70), (255, 88), (246, 238), (142, 228), (150, 70)], fill=NAVY, width=5)
    text_c(d, (200, 150), "Rp", F("pb", 46), (122, 90, 46))
    d.ellipse((214, 196, 232, 214), fill=NAVY)
    d.ellipse((40, 110, 190, 250), fill=BOC, outline=NAVY, width=5)
    d.ellipse((72, 160, 158, 245), fill=(185, 181, 198))
    d.line([(80, 245), (64, 266)], fill=NAVY, width=6); d.line([(150, 245), (166, 266)], fill=NAVY, width=6)
    for ex in (40, 135):
        d.ellipse((ex, 8, ex + 58, 66), fill=BOC, outline=NAVY, width=5)
        d.ellipse((ex + 12, 20, ex + 46, 54), fill=(244, 163, 184))
    d.ellipse((55, 38, 175, 150), fill=BOC, outline=NAVY, width=5)
    if mode == "sleep":
        d.arc((84, 80, 104, 96), 20, 160, fill=NAVY, width=5); d.arc((127, 80, 147, 96), 20, 160, fill=NAVY, width=5)
    else:
        d.ellipse((86, 78, 101, 97), fill=NAVY); d.ellipse((129, 78, 144, 97), fill=NAVY)
        d.line([(78, 68), (103, 78)], fill=NAVY, width=6); d.line([(152, 68), (127, 78)], fill=NAVY, width=6)
    d.ellipse((107, 102, 123, 116), fill=(196, 52, 140))
    if mode == "bite":   # gigi menggigit
        d.rectangle((100, 118, 130, 134), fill=WHITE, outline=NAVY, width=3); d.line([(115, 118), (115, 134)], fill=NAVY, width=3)
    else:
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


def icon_check(d, cx, cy, s=1.0, col=GREEN):
    d.ellipse((cx - 40 * s, cy - 40 * s, cx + 40 * s, cy + 40 * s), fill=col)
    d.line([(cx - 18 * s, cy), (cx - 4 * s, cy + 15 * s), (cx + 20 * s, cy - 14 * s)], fill=WHITE, width=int(10 * s),
           joint="curve")


# ---------- ikon alat (flat, tanpa merek) ----------
def rice_cooker(d, cx, cy, s=1.0, lamp=True, t=0.0, label=True):
    """badan rice cooker; lampu HANGAT oranye berkedip lembut. Return titik colokan kabel (belakang kanan)."""
    d.rounded_rectangle((cx - 170 * s, cy - 60 * s, cx + 170 * s, cy + 150 * s), int(60 * s), fill=WHITE, outline=NAVY,
                        width=int(7 * s))
    d.chord((cx - 180 * s, cy - 190 * s, cx + 180 * s, cy + 30 * s), 180, 360, fill=TEAL, outline=NAVY, width=int(7 * s))
    d.rounded_rectangle((cx - 50 * s, cy - 215 * s, cx + 50 * s, cy - 175 * s), int(18 * s), fill=NAVY)
    d.line([(cx - 175 * s, cy - 78 * s), (cx + 175 * s, cy - 78 * s)], fill=NAVY, width=int(7 * s))
    # panel depan
    d.rounded_rectangle((cx - 100 * s, cy - 10 * s, cx + 100 * s, cy + 110 * s), int(20 * s), fill=(236, 240, 246),
                        outline=NAVY, width=int(4 * s))
    lx, ly = cx - 50 * s, cy + 30 * s
    if lamp:
        g = 0.75 + 0.25 * math.sin(t * 5)
        for k, a in ((44, 50), (32, 90)):
            r = k * s * (0.9 + 0.1 * g)
            d.ellipse((lx - r, ly - r, lx + r, ly + r), fill=(255, 160, 40, int(a * g)))
        d.ellipse((lx - 18 * s, ly - 18 * s, lx + 18 * s, ly + 18 * s), fill=ORANGE, outline=NAVY, width=int(3 * s))
    else:
        d.ellipse((lx - 18 * s, ly - 18 * s, lx + 18 * s, ly + 18 * s), fill=(200, 205, 215), outline=NAVY, width=int(3 * s))
    d.ellipse((cx + 32 * s, ly - 18 * s, cx + 68 * s, ly + 18 * s), fill=(200, 205, 215), outline=NAVY, width=int(3 * s))
    if label:
        text_c(d, (lx, cy + 82 * s), "HANGAT", F("pb", int(22 * s)), ORANGE if lamp else GREY_T)
    return (cx + 165 * s, cy + 110 * s)


def socket(d, cx, cy, s=1.0):
    d.rounded_rectangle((cx - 55 * s, cy - 55 * s, cx + 55 * s, cy + 55 * s), int(18 * s), fill=WHITE, outline=NAVY,
                        width=int(5 * s))
    d.ellipse((cx - 36 * s, cy - 36 * s, cx + 36 * s, cy + 36 * s), fill=(225, 230, 238))
    for dx in (-14, 14):
        d.ellipse((cx + (dx - 6) * s, cy - 6 * s, cx + (dx + 6) * s, cy + 6 * s), fill=NAVY)


def plug(d, cx, cy, s=1.0, col=NAVY):
    d.rounded_rectangle((cx - 30 * s, cy - 40 * s, cx + 30 * s, cy + 30 * s), int(10 * s), fill=col)
    for dx in (-12, 12):
        d.rectangle((cx + (dx - 4) * s, cy - 62 * s, cx + (dx + 4) * s, cy - 40 * s), fill=(160, 166, 180))


def cable(d, pts, s=1.0):
    d.line(pts, fill=NAVY, width=int(10 * s), joint="curve")


def fridge(d, cx, cy, s=1.0):
    w, h = 300 * s, 600 * s
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(30 * s), fill=(214, 236, 246), outline=NAVY,
                        width=int(7 * s))
    d.line([(cx - w / 2, cy - h / 2 + 200 * s), (cx + w / 2, cy - h / 2 + 200 * s)], fill=NAVY, width=int(7 * s))
    for y0, y1 in ((cy - h / 2 + 60 * s, cy - h / 2 + 150 * s), (cy - h / 2 + 250 * s, cy - h / 2 + 380 * s)):
        d.rounded_rectangle((cx + w / 2 - 50 * s, y0, cx + w / 2 - 30 * s, y1), int(8 * s), fill=NAVY)
    d.rectangle((cx - w / 2 + 30 * s, cy + h / 2, cx - w / 2 + 60 * s, cy + h / 2 + 20 * s), fill=NAVY)
    d.rectangle((cx + w / 2 - 60 * s, cy + h / 2, cx + w / 2 - 30 * s, cy + h / 2 + 20 * s), fill=NAVY)


def dispenser(d, cx, cy, s=1.0, hot=0.0, t=0.0):
    # galon
    d.rounded_rectangle((cx - 110 * s, cy - 330 * s, cx + 110 * s, cy - 120 * s), int(50 * s), fill=(190, 220, 248),
                        outline=NAVY, width=int(6 * s))
    d.rectangle((cx - 40 * s, cy - 130 * s, cx + 40 * s, cy - 100 * s), fill=NAVY)
    # badan
    d.rounded_rectangle((cx - 150 * s, cy - 110 * s, cx + 150 * s, cy + 300 * s), int(26 * s), fill=WHITE, outline=NAVY,
                        width=int(7 * s))
    d.rounded_rectangle((cx - 110 * s, cy - 60 * s, cx + 110 * s, cy + 70 * s), int(16 * s), fill=(236, 240, 246))
    for dx, col in ((-50, RED), (50, (60, 120, 210))):
        d.rounded_rectangle((cx + (dx - 18) * s, cy - 40 * s, cx + (dx + 18) * s, cy + 10 * s), int(8 * s), fill=col)
    d.rectangle((cx - 110 * s, cy + 70 * s, cx + 110 * s, cy + 82 * s), fill=NAVY)
    # elemen pemanas (kaca intip)
    d.rounded_rectangle((cx - 110 * s, cy + 110 * s, cx + 110 * s, cy + 270 * s), int(14 * s), fill=(60, 66, 92))
    col = tuple(int((120 + 135 * hot) if j == 0 else (80 + 30 * hot) if j == 1 else 80) for j in range(3))
    pts = [(cx - 85 * s + k * 34 * s, cy + (140 if k % 2 == 0 else 240) * s) for k in range(6)]
    if hot > 0:
        g = 0.7 + 0.3 * math.sin(t * 8)
        d.line(pts, fill=(255, 120, 40, int(120 * hot * g)), width=int(26 * s), joint="curve")
    d.line(pts, fill=col, width=int(12 * s), joint="curve")


def tv(d, cx, cy, s=1.0, led=True):
    d.rounded_rectangle((cx - 230 * s, cy - 150 * s, cx + 230 * s, cy + 130 * s), int(16 * s), fill=NAVY)
    d.rectangle((cx - 210 * s, cy - 130 * s, cx + 210 * s, cy + 100 * s), fill=(40, 46, 70))
    d.polygon([(cx - 60 * s, cy + 190 * s), (cx + 60 * s, cy + 190 * s), (cx + 25 * s, cy + 130 * s),
               (cx - 25 * s, cy + 130 * s)], fill=NAVY)
    if led:
        d.ellipse((cx + 180 * s, cy + 106 * s, cx + 200 * s, cy + 124 * s), fill=(255, 40, 40))
        d.ellipse((cx + 172 * s, cy + 98 * s, cx + 208 * s, cy + 132 * s), fill=(255, 40, 40, 90))


def meter(d, cx, cy, s=1.0, t=0.0, speed=1.0):
    d.rounded_rectangle((cx - 120 * s, cy - 150 * s, cx + 120 * s, cy + 150 * s), int(24 * s), fill=WHITE, outline=NAVY,
                        width=int(6 * s))
    d.ellipse((cx - 85 * s, cy - 110 * s, cx + 85 * s, cy + 60 * s), fill=(236, 240, 246), outline=NAVY, width=int(4 * s))
    a = -math.pi / 2 + t * speed * 6
    d.line([(cx, cy - 25 * s), (cx + 70 * s * math.cos(a), cy - 25 * s + 70 * s * math.sin(a))], fill=RED, width=int(8 * s))
    d.ellipse((cx - 9 * s, cy - 34 * s, cx + 9 * s, cy - 16 * s), fill=NAVY)
    text_c(d, (cx, cy + 105 * s), "kWh", F("pb", int(40 * s)), NAVY)


def bolt(d, cx, cy, s=1.0, col=YEL):
    p = [(cx + 10 * s, cy - 80 * s), (cx - 45 * s, cy + 10 * s), (cx - 2 * s, cy + 10 * s), (cx - 15 * s, cy + 80 * s),
         (cx + 45 * s, cy - 15 * s), (cx + 2 * s, cy - 15 * s)]
    d.polygon(p, fill=col, outline=NAVY); d.line(p + [p[0]], fill=NAVY, width=int(5 * s))


def bubble(text, size=44, fg=YEL, bg=NAVY, tail="left", pad=36):
    f = F("pb", size); w = int(f.getlength(text) + 2 * pad); h = size + 46
    B = Image.new("RGBA", (w + 4, h + 44), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
    bd.rounded_rectangle((0, 0, w, h), 28, fill=bg)
    if tail == "left":
        bd.polygon([(50, h - 4), (100, h - 4), (36, h + 40)], fill=bg)
    elif tail == "right":
        bd.polygon([(w - 50, h - 4), (w - 100, h - 4), (w - 36, h + 40)], fill=bg)
    text_c(bd, (w / 2, h / 2 + 1), text, f, fg)
    return B


def value_card(big, small=None, w=640, fill=WHITE, col=NAVY, tag=None, tagcol=YEL):
    h = 210 if small else 160
    T, td = card(w, h, fill=fill)
    text_c(td, (w / 2, 92 if small else h / 2), big, fit("pb", 90, big, w - 60), col)
    if small:
        text_c(td, (w / 2, 172), small, fit("pm", 32, small, w - 40), GREY_T)
    if tag:
        f = F("pb", 30); tw = f.getlength(tag) + 40
        td.rounded_rectangle((w - tw - 18, -2, w - 18, 46), 22, fill=tagcol)
    return T, (tag, w)


def put_value(img, cx, cy, big, small=None, p=1.0, w=640, col=NAVY, tag=None, angle=0.0):
    if p <= 0: return
    h = 210 if small else 160
    T = Image.new("RGBA", (w + 16, h + 50), (0, 0, 0, 0))
    C, td = card(w, h)
    text_c(td, (w / 2, 92 if small else h / 2), big, fit("pb", 90, big, w - 60), col)
    if small:
        text_c(td, (w / 2, 172), small, fit("pm", 32, small, w - 40), GREY_T)
    T.alpha_composite(C, (0, 34))
    if tag:
        d = ImageDraw.Draw(T); f = F("pb", 30); tw = f.getlength(tag) + 40
        d.rounded_rectangle((w - tw - 10, 6, w - 10, 62), 26, fill=YEL, outline=NAVY, width=3)
        text_c(d, (w - 10 - tw / 2, 34), tag, f, NAVY)
    paste_c(img, T, cx, cy, p, angle)


# ---------- latar ----------
@lru_cache(None)
def base_bg():
    img = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(img)
    top, bot = (240, 244, 249), (248, 244, 237)
    for y in range(H):
        u = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[j] + (bot[j] - top[j]) * u) for j in range(3)))
    return img


@lru_cache(None)
def bg_kitchen():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    # ubin dapur + meja
    for y in range(560, 1300, 90):
        d.line([(0, y), (W, y)], fill=(226, 232, 240), width=3)
    for x in range(0, W, 120):
        d.line([(x, 560), (x, 1300)], fill=(226, 232, 240), width=3)
    d.rectangle((0, 1300, W, 1380), fill=(214, 186, 150)); d.line([(0, 1300), (W, 1300)], fill=NAVY, width=5)
    d.rectangle((0, 1380, W, H), fill=(226, 230, 238))
    return img


@lru_cache(None)
def bg_rest():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((90, 480, 990, 1380), fill=(228, 238, 246))
    d.rectangle((0, 1490, W, H), fill=(226, 230, 238))
    return img


@lru_cache(None)
def header():
    """pill = kolom Judul layar (bukan label seri); hanya setelah dtk 3 (PRB-34), y≈300 (PRB-41)."""
    L = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F("pb", 34); s1 = "DIAM-DIAM MAKAN"; s2 = "LISTRIK"
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
    if t >= CLOSE: return
    i = sub_chunk(t)
    if i is None: return
    s0 = 0.0 if i == 0 else cs(i)
    sc = 0.85 + 0.15 * back((t - s0) / 0.22) if i != 0 else 1.0
    paste_c(img, sub_layer(i), W / 2, 1600, sc)


# ---------- adegan ----------
def counter_val(t):
    return int(round(80000 * eio((t - CT0) / (CT1 - CT0)) / 1000.0) * 1000)


def scene0(img, t):
    """frame 0: Si Bocor menggigit kabel rice cooker (lampu HANGAT), Aru menoleh kaget; counter Rp0->Rp80.000 dtk 1,5-2,5."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    end = rice_cooker(d, 600, 1110, 1.05, True, t)
    socket(d, 990, 1060, 0.8)
    cable(d, [end, (800, 1250), (900, 1200), (990, 1110)], 1.0)
    plug(d, 990, 1095, 0.55)
    # percikan di titik gigitan
    bx, by = 860, 1225
    for k in range(5):
        a = k * 1.25 + t * 9
        r0, r1 = 30, 55 + 12 * math.sin(t * 20 + k)
        d.line([(bx + r0 * math.cos(a), by + r0 * math.sin(a)), (bx + r1 * math.cos(a), by + r1 * math.sin(a))], fill=YEL, width=7)
    paste_c(L, bocor_img("bite"), bx + 30, by - 20 + 4 * math.sin(t * 14), 0.78, -8)
    # koin "cring" jatuh dari kabel
    for j in range(3):
        ct = t - 0.15 - j * 0.35
        if ct > 0:
            paste_c(L, coin(24), 820 + j * 55, by + 40 + min(70, 500 * ct * ct), 1, ct * 260)
    # Aru menoleh kaget (dicermin menghadap rice cooker) + tanda seru
    jump = 26 * max(0.0, math.sin(clamp(t / 0.35) * math.pi))
    draw_aru(L, 190, 1400, 470, t, 1.5, mirror=True, jump=jump)
    p = pop(t, 0.12)
    if p > 0:
        E = Image.new("RGBA", (120, 160), (0, 0, 0, 0)); ed = ImageDraw.Draw(E)
        ed.ellipse((10, 10, 110, 110), fill=RED, outline=NAVY, width=5); text_c(ed, (60, 60), "!", F("pb", 72), WHITE)
        paste_c(L, E, 300, 860, 0.7 * p if t > 0.12 else 0.7)
    # counter tagihan (bergerak dtk 1,5-2,5)
    v = counter_val(t); hot = v > 0
    C, cd = card(780, 190, fill=WHITE)
    bolt(cd, 90, 95, 0.75)
    cd.text((160, 95), rp(v), font=F("pb", 96), fill=RED if hot else NAVY, anchor="lm")
    if t >= CT1:
        a = clamp((t - CT1) / 0.25)
        cd.text((162 + F("pb", 96).getlength(rp(80000)) + 10, 128), "/bln", font=F("pb", 40), fill=GREY_T, anchor="lm")
    sc = 1.0 + (0.12 * back((t - CT0) / 0.35) if t >= CT0 else 0.0) - (0.12 * clamp((t - CT1 - 0.2) / 0.4))
    paste_c(L, C, W / 2, 700, sc)
    if hot:
        arrow(d, 970, 740, 970, 640, RED, w=16, head=36)
    # zoom pelan ke counter mulai dtk 1,5 (visual berganti)
    z = 1.0 + 0.06 * eio((t - 1.4) / 1.2)
    if z > 1.001:
        Z = L.resize((int(W * z), int(H * z)), Image.BICUBIC)
        cx, cy = W / 2 * z, 700 * z
        img.alpha_composite(Z.crop((int(cx - W / 2), int(cy - 700), int(cx - W / 2) + W, int(cy - 700) + H)))
    else:
        img.alpha_composite(L)
    pills(img, [["Diam-diam", "makan"], ["LISTRIK"]], 290, size=70, keyword="LISTRIK")


def scene1(img, t):
    """mitos kulkas: label MITOS ATAU FAKTA?, Si Bocor sembunyi di balik kulkas (jawaban ditahan)."""
    d = ImageDraw.Draw(img)
    # Si Bocor mengintip dari balik kulkas (digambar dulu, tertutup kulkas)
    peek = 0.5 + 0.5 * math.sin(t * 2.2)
    paste_c(img, bocor_img(), 700 + 60 * peek, 760, 0.7, -10)
    fridge(d, 560, 980, 1.0)
    p = pop(t, SC[1] + 0.1)
    if p > 0:
        B = Image.new("RGBA", (620, 110), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 620, 100), 50, fill=RED, outline=NAVY, width=5)
        text_c(bd, (310, 50), "MITOS ATAU FAKTA?", F("pb", 46), WHITE)
        paste_c(img, B, W / 2, 560, p, -2)
    draw_aru(img, 210, 1440, 330, t)
    p = pop(t, cs(6))
    if p > 0:
        paste_c(img, bubble("bener?", 50), 330, 1060, p)
    p = pop(t, cs(8))
    if p > 0:
        T, td = card(380, 120, fill=YEL)
        text_c(td, (190, 60), "hitung dulu!", F("pb", 48), NAVY)
        paste_c(img, T, 830, 1370, p, 3)


def scene2(img, t):
    """kartu sumber tarif R-1 1.300 VA Rp1.444,70/kWh (Okt-Des 2026)."""
    p = pop(t, SC[2] + 0.05)
    if p > 0:
        cw, ch = 840, 620
        T, td = card(cw, ch)
        td.rounded_rectangle((0, 0, cw, 110), 30, fill=NAVY); td.rectangle((0, 60, cw, 110), fill=NAVY)
        td.rounded_rectangle((0, 0, cw, ch), 30, outline=NAVY, width=5)
        text_c(td, (cw / 2, 56), "TARIF LISTRIK SEKARANG", F("pb", 46), WHITE)
        bolt(td, 130, 300, 1.1)
        td.text((230, 210), "R-1 · 1.300 VA", font=F("pb", 48), fill=TEAL, anchor="lm")
        u = eout((t - cs(12)) / 0.9)
        v = 1444.70 * u
        s = "Rp" + f"{int(v):,}".replace(",", ".") + "," + (f"{v:.2f}".split(".")[1] if u >= 1 else "00")
        td.text((230, 320), s, font=F("pb", 96), fill=NAVY, anchor="lm")
        td.text((230, 410), "per kWh", font=F("pb", 48), fill=GREY_T, anchor="lm")
        td.rounded_rectangle((60, 480, cw - 60, 570), 24, fill=LIGHT)
        text_c(td, (cw / 2, 525), "Okt–Des 2026 · Metro TV News, 29 Okt 2026", fit("pm", 32, "Okt–Des 2026 · Metro TV News, 29 Okt 2026", cw - 160), INK)
        paste_c(img, T, W / 2, 820, p)
    draw_aru(img, 230, 1470, 300, t)


def scene3(img, t):
    """charger + TV standby: lampu merah berkedip; ±Rp10.000/bln* (ilustrasi)."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[3] + 0.05)
    if p > 0:
        L = Image.new("RGBA", (W, 800), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        tv(ld, 560, 230, 1.0, led=(int(t * 3) % 2 == 0))
        # stopkontak bertumpuk dengan charger
        ld.rounded_rectangle((220, 560, 860, 660), 24, fill=WHITE, outline=NAVY, width=6)
        for k in range(4):
            x = 300 + k * 160
            ld.ellipse((x - 34, 576, x + 34, 644), fill=(225, 230, 238))
            plug(ld, x, 620 - 70, 0.6, col=(NAVY, TEAL, NAVY, RED)[k])
            ld.line([(x, 520), (x + 20 * math.sin(k), 420)], fill=NAVY, width=8)
        ld.ellipse((820, 590, 846, 616), fill=(255, 40, 40) if int(t * 3) % 2 == 0 else (120, 40, 40))
        paste_c(img, L, W / 2, 860, p)
    if t >= cs(16) and int(t * 3) % 2 == 0:
        paste_c(img, bubble("standby", 40, fg=WHITE, bg=RED, tail="right"), 800, 520, pop(t, cs(17)))
    put_value(img, W / 2, 1360, "±Rp10.000/bln*", "*ilustrasi: 10 watt, 24 jam", pop(t, cs(19) - 0.1), w=700,
              tag="ilustrasi")


def scene4(img, t):
    """kulkas: Si Bocor keluar dari balik kulkas lalu lari (bukan dia pelakunya); ±Rp43.000/bln*."""
    d = ImageDraw.Draw(img)
    fridge(d, 360, 900, 0.9)
    tb = t - cs(21)
    if tb > 0:
        x = 520 + 700 * eout(tb / 1.6) ** 1.5; hop = abs(math.sin(tb * 12)) * 18
        paste_c(img, bocor_img(), x, 1180 - hop, 0.7)
    else:
        paste_c(img, bocor_img(), 520, 700, 0.6, -10)
        fridge(d, 360, 900, 0.9)
    put_value(img, 770, 760, "±Rp43.000", "*ilustrasi: 1 kWh/hari", pop(t, cs(23) - 0.1), w=470, tag="ilustrasi")
    p = pop(t, cs(24))
    if p > 0:
        B = Image.new("RGBA", (380, 120), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 370, 110), 55, fill=GREEN, outline=NAVY, width=5)
        icon_check(bd, 62, 55, 0.8, col=WHITE)
        bd.line([(62 - 14, 55), (62 - 3, 67), (62 + 16, 44)], fill=GREEN, width=8)
        bd.text((120, 55), "WAJAR", font=F("pb", 54), fill=WHITE, anchor="lm")
        paste_c(img, B, 770, 1000, p, -4)
    draw_aru(img, 820, 1460, 280, t, mirror=True)


def scene5(img, t):
    """dispenser panas-dingin: elemen pemanas merah; ±Rp50.000/bln + sumber 1-1,4 kWh/hari."""
    d = ImageDraw.Draw(img)
    hot = clamp((t - cs(31)) / 0.4) if t >= cs(31) else 0.35
    L = Image.new("RGBA", (W, 760), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    dispenser(ld, 330, 380, 1.0, hot, t)
    paste_c(img, L, W / 2, 900, pop(t, SC[5] + 0.05))
    if t >= cs(31):
        for k in range(3):
            y = 1000 - ((t * 120 + k * 60) % 180)
            d.arc((260 + k * 40, y, 300 + k * 40, y + 60), 200, 340, fill=(255, 120, 40), width=6)
    p = pop(t, cs(28))
    if p > 0:
        paste_c(img, bubble("lebih rakus!", 42, fg=WHITE, bg=RED), 760, 600, p)
    put_value(img, 740, 900, "±Rp50.000", "1–1,4 kWh/hari", pop(t, cs(30) - 0.1), w=520)
    p = pop(t, cs(32))
    if p > 0:
        T, td = card(380, 110, fill=YEL)
        text_c(td, (190, 55), "pemanasnya!", F("pb", 46), NAVY)
        paste_c(img, T, 740, 1130, p, 3)


def scene6(img, t):
    """juaranya di dapur: Si Bocor tidur di atas rice cooker (lampu HANGAT), meteran berputar cepat."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[6] + 0.05)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    rice_cooker(ld, 430, 1120, 1.0, True, t)
    paste_c(L, bocor_img("sleep"), 430, 820 + 4 * math.sin(t * 2), 0.75)
    for k in range(3):
        u = ((t * 0.8 + k / 3) % 1)
        text_c(ld, (520 + 60 * u + k * 10, 720 - 120 * u), "z", F("pb", 40 + k * 10), (NAVY[0], NAVY[1], NAVY[2], int(255 * (1 - u))))
    meter(ld, 860, 1120, 0.9, t, speed=1 + 4 * clamp((t - cs(35)) / 1.0))
    paste_c(img, L, W / 2, H / 2, p if p > 0 else 0.01)
    q = pop(t, cs(33))
    if q > 0:
        B = Image.new("RGBA", (480, 130), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 470, 120), 60, fill=YEL, outline=NAVY, width=5)
        bd.polygon([(40, 85), (40, 35), (70, 60), (95, 25), (120, 60), (150, 35), (150, 85)], fill=NAVY)
        bd.text((175, 60), "JUARA #1", font=F("pb", 52), fill=NAVY, anchor="lm")
        paste_c(img, B, W / 2, 560, q, -2)


def scene7(img, t):
    """payoff: 77 W x 24 jam -> Rp80.000/bln -> Rp961.000/tahun; sumber; peringkat 1-4."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[7] + 0.05)
    if p > 0:
        T, td = card(840, 330)
        text_c(td, (420, 60), "77 W × 24 jam × 30 hari", F("pb", 46), TEAL)
        if t < cs(43):
            u = eout((t - cs(41)) / 0.7)
            text_c(td, (420, 175), rp(int(round(80000 * u / 1000) * 1000)) + "/bln", F("pb", 104), RED)
        else:
            u = eout((t - cs(43)) / 0.8)
            v = int(round((80000 + 881000 * u) / 1000) * 1000)
            text_c(td, (420, 175), rp(v) + "/thn", F("pb", 100), RED)
        if t >= cs(44):
            td.rounded_rectangle((250, 250, 590, 310), 28, fill=YEL)
            text_c(td, (420, 280), "hampir sejuta!", F("pb", 34), NAVY)
        paste_c(img, T, W / 2, 620, p)
    rows = [("rice cooker hangat", "±Rp80 rb", RED), ("dispenser", "±Rp50 rb", ORANGE),
            ("kulkas*", "±Rp43 rb", TEAL), ("standby*", "±Rp10 rb", GREY_T)]
    for k, (name, val, col) in enumerate(rows):
        q = pop(t, cs(40) + 0.15 * (3 - k))
        if q <= 0: continue
        T, td = card(760, 96, fill=WHITE if k else (255, 238, 232))
        td.ellipse((20, 14, 88, 82), fill=col); text_c(td, (54, 48), str(k + 1), F("pb", 42), WHITE)
        td.text((112, 48), name, font=F("pb", 40), fill=NAVY, anchor="lm")
        td.text((736, 48), val, font=F("pb", 40), fill=NAVY, anchor="rm")
        paste_c(img, T, W / 2, 900 + k * 112, q)


def scene8(img, t):
    """trik: Aru mencabut steker, "Hitung dulu!", counter turun ke Rp0; sisa nasi ke kulkas."""
    d = ImageDraw.Draw(img)
    pulled = clamp((t - cs(46) - 0.2) / 0.4)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    end = rice_cooker(ld, 330, 1000, 0.75, lamp=pulled < 1, t=t)
    socket(ld, 900, 1000, 0.8)
    px, py = 900 - 160 * eout(pulled), 1035 + 120 * eout(pulled)
    cable(ld, [end, (600, 1140), (px - 60, py + 60), (px, py + 20)], 0.9)
    plug(ld, px, py, 0.55)
    img.alpha_composite(L)
    draw_aru(img, 720, 1450, 300, t, mirror=False)
    if pulled > 0:
        paste_c(img, bubble("cabut!", 46, fg=NAVY, bg=YEL, tail="right"), 720, 885, pop(t, cs(46) + 0.4))
    # counter turun ke Rp0
    u = eout((t - cs(47)) / 0.8)
    v = int(round(80000 * (1 - u) / 1000) * 1000)
    C, cd = card(560, 170)
    bolt(cd, 80, 85, 0.65)
    cd.text((150, 85), rp(v), font=F("pb", 92), fill=GREEN if v == 0 else RED, anchor="lm")
    paste_c(img, C, W / 2, 560, pop(t, SC[8] + 0.05))
    # sisa nasi -> kulkas -> panaskan
    q = pop(t, cs(48))
    if q > 0:
        T, td = card(840, 130, fill=WHITE)
        steps = [("sisa nasi", TEAL), ("kulkas", (60, 120, 210)), ("panaskan", ORANGE)]
        x = 30
        for j, (s, col) in enumerate(steps):
            if j == 2 and t < cs(50): break
            if j == 1 and t < cs(49): break
            f = F("pb", 34); w_ = f.getlength(s) + 36
            td.rounded_rectangle((x, 35, x + w_, 95), 30, fill=col)
            td.text((x + 18, 65), s, font=f, fill=WHITE, anchor="lm"); x += w_
            if j < 2: arrow(td, x + 8, 65, x + 52, 65, NAVY, w=8, head=18); x += 62
        paste_c(img, T, W / 2, 745, q)
    p = pop(t, cs(46) + 0.6)
    if p > 0 and t < cs(48):
        T, td = card(360, 110, fill=YEL)
        text_c(td, (180, 55), "Hitung dulu!", F("pb", 46), NAVY)
        paste_c(img, T, 300, 1300, p, -3)


def scene9(img, t):
    """Si Bocor terbangun & kabur; ajakan komentar + like terbanyak dihitung di reel berikutnya (PRB-43)."""
    d = ImageDraw.Draw(img)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    rice_cooker(ld, 300, 1150, 0.7, True, t)
    img.alpha_composite(L)
    tb = t - cs(53)
    if tb < 0:
        paste_c(img, bocor_img("sleep"), 300, 940, 0.6)
    else:
        x = 300 + 900 * eout(clamp((tb - 0.4) / 1.4)) ** 1.6; hop = abs(math.sin(tb * 12)) * 20 if tb > 0.4 else 0
        paste_c(img, bocor_img(), x, 940 - hop - 30 * clamp(tb / 0.2), 0.6, -6)
        if tb < 0.8:
            text_c(d, (300, 790), "!", F("pb", 90), RED)
    p = pop(t, cs(55) - 0.1)
    if p > 0:
        B = Image.new("RGBA", (840, 260), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 840, 200), 34, fill=WHITE, outline=NAVY, width=5)
        bd.polygon([(640, 196), (720, 196), (760, 250)], fill=WHITE, outline=NAVY)
        bd.line([(642, 199), (718, 199)], fill=WHITE, width=8)
        text_c(bd, (420, 66), "Di rumahmu,", F("pb", 46), NAVY)
        text_c(bd, (420, 136), "apa paling boros?", F("pb", 58), RED)
        paste_c(img, B, W / 2, 560, p)
    draw_aru(img, 840, 1460, 300, t)
    p = pop(t, cs(57) - 0.1)
    if p > 0:
        T, td = card(860, 170, fill=YEL)
        text_c(td, (430, 56), "Tulis di komentar!", F("pb", 52), NAVY)
        text_c(td, (430, 122), "komentar like terbanyak dihitung di reel berikutnya", fit("pm", 30, "komentar like terbanyak dihitung di reel berikutnya", 820), NAVY)
        paste_c(img, T, W / 2, 850, p)


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9]


def draw_notes(img, k):
    lines = NOTES.get(k)
    if not lines: return
    d = ImageDraw.Draw(img)
    for j, s in enumerate(lines):
        f = fit("pm", 28, s, W - 2 * SAFE_X)
        d.text((W / 2, 1712 + j * 40), s, font=f, fill=GREY_T, anchor="mm")


def closing(img, t):
    a = clamp((t - CLOSE) / 0.25)
    if a <= 0: return
    O = Image.new("RGBA", (W, H), (248, 246, 240, int(250 * a)))
    img.alpha_composite(O)
    paste_c(img, logo_w(300), W / 2, 760, 0.9 + 0.1 * back(a), 0, a)
    T, td = card(860, 150, fill=NAVY)
    text_c(td, (430, 75), "Barang paling boros di rumahmu?", fit("pb", 50, "Barang paling boros di rumahmu?", 800), WHITE)
    paste_c(img, T, W / 2, 1050, back(a), 0, a)


def frame(t):
    k = scene_of(t)
    ts = t - SC[k]
    img = (bg_kitchen() if k in (0, 6, 8, 9) else bg_rest()).copy()
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
        if t >= CT0:
            a = clamp((t - CT0) / 0.3)
            L = Image.new("RGBA", (W, 60), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
            s_ = NOTES[0][0]; f = fit("pm", 28, s_, W - 2 * SAFE_X)
            ld.text((W / 2, 30), s_, font=f, fill=INK, anchor="mm")
            paste_c(img, L, W / 2, 1712, 1, 0, a)
    draw_sub(img, t)
    if k > 0 and t < CLOSE:
        draw_notes(img, k)
    if FOLLOW[0] <= t < FOLLOW[1]:
        f = F("pb", 30); s_ = "follow @kabar.arunika buat hitungan harian"
        tw = f.getlength(s_)
        pl = Image.new("RGBA", (int(tw) + 60, 60), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
        pd.rounded_rectangle((0, 0, tw + 60, 60), 30, fill=TEAL)
        pd.text((30, 30), s_, font=f, fill=WHITE, anchor="lm")
        a = min(clamp((t - FOLLOW[0]) / 0.25), clamp((FOLLOW[1] - t) / 0.25))
        paste_c(img, pl, W / 2, 1490, 1, 0, a)
    closing(img, t)
    if t >= 3.0:   # progress bar: bukan di dtk 0-3 (PRB-34)
        ImageDraw.Draw(img).rectangle((0, H - 14, int(W * t / TOTAL), H), fill=YEL)
    return img.convert("RGB")


def events():
    ev = [{"t": SC[k], "sfx": "whoosh", "gain": 0.30} for k in range(1, NS)]
    ev.append({"t": 0.15, "sfx": "cring", "gain": 0.4})     # koin jatuh frame 0
    ev.append({"t": CT0, "sfx": "pop", "gain": 0.3})        # counter mulai bergerak
    ev.append({"t": CT1, "sfx": "ding", "gain": 0.25})
    for i in (6, 8, 12, 17, 19, 23, 24, 28, 30, 32, 33, 40, 46, 48, 49, 50, 55, 57):
        ev.append({"t": cs(i), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": cs(21), "sfx": "cring", "gain": 0.3})
    ev.append({"t": cs(43), "sfx": "ding", "gain": 0.35})
    ev.append({"t": cs(53), "sfx": "cring", "gain": 0.35})
    ev.append({"t": CLOSE, "sfx": "ding", "gain": 0.25})
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

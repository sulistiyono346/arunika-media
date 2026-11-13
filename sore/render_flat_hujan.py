"""Renderer ARN-45 "Hujan deras 1 jam di Jakarta = berapa liter air?" -- gaya Flat 2D latar terang (sampel 1).
Salinan pagi/render_flat_emas.py (helper kartu, Si Bocor, panah, Aru resmi, logo, subtitle 1 baris, sfx) dengan
frame 0 dari render_gaya_hujan.py (Aru menengadah di bawah cutaway atap, galon menumpuk, counter 0 -> 38 dtk 1,5-2,5).
Perbaikan dari tahap sampel: rumah + tumpukan galon diturunkan 40 px supaya galon teratas tidak menyentuh pill judul.
Tanpa visual korban banjir / genangan dramatis; peta Jakarta flat + grid saja.
Pemakaian (dari folder kerja build, setelah align_hujan.py -> timing.json, vo.wav):
  TOTAL=53.6 python3 /path/sore/render_flat_hujan.py events
  TOTAL=53.6 python3 /path/sore/render_flat_hujan.py stills 0,2.2,...
  TOTAL=53.6 python3 /path/sore/render_flat_hujan.py video out.mp4 A B
"""
import json, math, os, random, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_gaya_hujan as Hm
from render_gaya_frame0 import F, clamp, eio, rain, NAVY, TEAL, YEL, WHITE, GREY_T, RED, SAFE_X

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "53.6"))
CLOSE = TOTAL - 1.5            # penutup logo kecil <=1,5 dtk (PRB-3), setelah VO selesai
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
GREEN = (46, 160, 110); INK = (60, 66, 92); LIGHT = (232, 238, 246)
WATER = (86, 160, 230); WATER_L = (176, 214, 246); WATER_D = (40, 110, 190)
ROOF = (232, 104, 72); LEAF = (98, 170, 80); LEAF_D = (62, 128, 56)

TIM = json.load(open("timing.json"))
def cs(i): return TIM[i]["start"] + LEAD
def ce(i): return TIM[i]["end"] + LEAD

SCENE_CHUNK = [0, 4, 8, 12, 16, 19, 23, 27, 31, 36]
SC = [0.0] + [cs(i) - 0.25 for i in SCENE_CHUNK[1:]] + [TOTAL]
NS = len(SCENE_CHUNK)
FOLLOW = (10.4, 15.0)          # PRB-4: ajakan follow teks kecil dtk 10-15
NOTES = {
    0: ("*ilustrasi: atap 36 m² · 720 L ≈ 38 galon 19 L",),
    2: ("Hujan sangat lebat >20 mm/jam · BMKG, diakses 13 Nov 2026",),
    3: ("20 mm = 0,02 m · 0,02 m × 1 m² = 0,02 m³ = 20 liter",),
    4: ("*ilustrasi: atap 36 m² · 36 × 20 L = 720 L",),
    5: ("660,98 km² · BPS, Luas Daerah Menurut Provinsi (data 2022)",),
    6: ("*jika hujan sangat lebat merata se-Jakarta selama 1 jam",),
    7: ("50 × 25 × 2 m = 2,5 juta L · 13,2 miliar ÷ 2,5 juta ≈ 5.300",),
}


def scene_of(t):
    for k in range(NS):
        if t < SC[k + 1]: return k
    return NS - 1


def num(v): return f"{int(v):,}".replace(",", ".")


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


def icon_check(d, cx, cy, s=1.0, col=GREEN):
    d.ellipse((cx - 40 * s, cy - 40 * s, cx + 40 * s, cy + 40 * s), fill=col)
    d.line([(cx - 18 * s, cy), (cx - 4 * s, cy + 15 * s), (cx + 20 * s, cy - 14 * s)], fill=WHITE, width=int(10 * s),
           joint="curve")


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
    sd.rounded_rectangle((6, 6, w - 6, size + 64), 18, fill=WHITE, outline=col, width=10)
    text_c(sd, (w / 2, (size + 70) / 2), text, f, col)
    return S


def pill(text, fill=NAVY, fg=WHITE, size=46, padx=36, h=None):
    f = F("pb", size); w = int(f.getlength(text) + 2 * padx); h = h or size + 44
    P = Image.new("RGBA", (w + 10, h + 12), (0, 0, 0, 0)); pd = ImageDraw.Draw(P)
    pd.rounded_rectangle((8, 10, w + 8, h + 10), h // 2, fill=(20, 33, 91, 55))
    pd.rounded_rectangle((0, 0, w, h), h // 2, fill=fill, outline=NAVY, width=4)
    text_c(pd, (w / 2, h / 2 + 1), text, f, fg)
    return P


# ---------- ikon adegan ----------
@lru_cache(None)
def bottle(h=110, full=1.0):
    """botol air 1 L generik (tanpa merek)."""
    w = int(h * 0.42); im = Image.new("RGBA", (w + 10, h + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    s = h / 110
    d.rounded_rectangle((5 + w * 0.32, 4, 5 + w * 0.68, 20 * s), int(3 * s), fill=TEAL, outline=NAVY, width=3)
    d.rounded_rectangle((5, 22 * s, 5 + w, h + 4), int(12 * s), fill=(236, 244, 252), outline=NAVY, width=4)
    if full > 0:
        top = 22 * s + (h - 18 * s) * (1 - full) + 6
        d.rounded_rectangle((9, max(top, 26 * s), 1 + w, h), int(9 * s), fill=WATER_L)
    d.line([(12, 34 * s), (12, h - 14 * s)], fill=(255, 255, 255, 220), width=max(3, int(5 * s)))
    return im


def pool(d, x0, y0, w, h, lanes=6, label=None, size=40, ow=6):
    d.rounded_rectangle((x0 - 14, y0 - 14, x0 + w + 14, y0 + h + 14), 20, fill=(236, 240, 246), outline=NAVY, width=ow)
    d.rectangle((x0, y0, x0 + w, y0 + h), fill=(98, 184, 236), outline=NAVY, width=max(2, ow - 2))
    for k in range(1, lanes):
        y = y0 + h * k / lanes
        for x in range(int(x0 + 8), int(x0 + w - 8), 22):
            d.line([(x, y), (x + 11, y)], fill=WHITE if (x // 22) % 2 else YEL, width=max(2, ow - 3))
    if label:
        text_c(d, (x0 + w / 2, y0 + h / 2), label, F("pb", size), WHITE, stroke_width=5, stroke_fill=NAVY)


def mini_house(d, cx, base, s=1.0, roof=ROOF, wall=(255, 246, 232), hl=False):
    w = 220 * s; hw = 150 * s
    d.rectangle((cx - w / 2 + 20 * s, base - hw, cx + w / 2 - 20 * s, base), fill=wall, outline=NAVY, width=max(2, int(5 * s)))
    d.rectangle((cx - 30 * s, base - 70 * s, cx + 10 * s, base), fill=(150, 200, 236), outline=NAVY, width=max(2, int(4 * s)))
    pts = [(cx - w / 2 - 10 * s, base - hw + 6 * s), (cx, base - hw - 110 * s), (cx + w / 2 + 10 * s, base - hw + 6 * s)]
    d.polygon(pts, fill=YEL if hl else roof, outline=NAVY)
    d.line(pts + [pts[0]], fill=NAVY, width=max(2, int(6 * s)), joint="curve")


# siluet DKI Jakarta (flat, perkiraan bentuk; tanpa genangan/korban)
JKT = [(0.00, 0.20), (0.10, 0.14), (0.20, 0.17), (0.31, 0.10), (0.44, 0.15), (0.55, 0.08), (0.67, 0.12),
       (0.80, 0.06), (0.91, 0.11), (1.00, 0.18), (0.97, 0.36), (0.91, 0.52), (0.85, 0.70), (0.75, 0.86),
       (0.63, 1.00), (0.53, 0.96), (0.45, 0.84), (0.37, 0.71), (0.21, 0.63), (0.08, 0.51), (0.03, 0.35)]


# ---------- latar ----------
@lru_cache(None)
def base_bg():
    img = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(img)
    top, bot = (232, 238, 246), (244, 244, 242)
    for y in range(H):
        u = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[j] + (bot[j] - top[j]) * u) for j in range(3)))
    return img


@lru_cache(None)
def bg_scene0():
    img = Image.new("RGBA", (W, H)); Hm.vgrad(img, (226, 234, 244), (240, 242, 246))
    d = ImageDraw.Draw(img)
    for cx, cy, r in ((230, 640, 90), (340, 610, 110), (450, 645, 80), (700, 630, 95), (810, 600, 110)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(200, 210, 226))           # awan hujan pucat
    return img


@lru_cache(None)
def bg_rest():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((90, 480, 990, 1380), fill=(224, 234, 246))
    d.rectangle((0, 1490, W, H), fill=(222, 228, 238))
    return img


@lru_cache(None)
def header():
    """pill = kolom Judul layar (bukan label seri); hanya setelah dtk 3 (PRB-34), y≈300 (PRB-41)."""
    L = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F("pb", 34); parts = [("SEBERAPA", NAVY, WHITE), ("BANYAK", YEL, NAVY), ("HUJAN SEJAM?", NAVY, WHITE)]
    ws = [f.getlength(s) + 48 for s, _, _ in parts]; gap = 10
    x = (W - sum(ws) - gap * (len(ws) - 1)) / 2
    for (s, bg, fg), w in zip(parts, ws):
        d.rounded_rectangle((x, 30, x + w, 96), 33, fill=bg)
        d.text((x + w / 2, 63), s, font=f, fill=fg, anchor="mm")
        x += w + gap
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
    paste_c(img, sub_layer(i), W / 2, 1610, sc)


# ---------- adegan ----------
DY0 = 40   # perbaikan sampel: rumah + galon turun 40 px (galon teratas tidak menyentuh pill judul di dtk ~2,2)


def scene0(img, t):
    """frame 0 = sampel 1: Aru menengadah di bawah cutaway atap, galon menumpuk, counter 0 -> 38 dtk 1,5-2,5."""
    rain(img, t, n=110, col=(120, 150, 200), alpha=170, seed=3, length=70, width=5)
    hero = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    floor = Hm.house(hero, t)
    d = ImageDraw.Draw(hero)
    d.rectangle((0, floor, W, H), fill=(214, 222, 232)); d.line([(0, floor), (W, floor)], fill=NAVY, width=5)
    Hm.aru(hero, t, floor + 8)
    Hm.draw_counter(hero, t)
    z = 1.0 + 0.05 * eio((t - 1.4) / 1.4)          # zoom pelan: visual berganti ~dtk 1,5
    py = 600                                         # pivot zoom di atas tumpukan galon
    paste_c(img, hero, W / 2 + (540 - W / 2), py + (H / 2 - py) * z + DY0, z)
    Hm.pills2(img, [["SEBERAPA", "BANYAK"], ["HUJAN", "SEJAM?"]], 290, size=72)


def scene1(img, t):
    """itu baru satu atap -> kalau sejakarta? deretan atap kota; coba tebak: berapa kolam olimpiade?"""
    d = ImageDraw.Draw(img)
    u = eout((t - cs(5) + 0.15) / 0.7)                # kamera mundur
    cols, rows = 5, 3
    gx = [200 + c * 170 for c in range(cols)]; gy = [600 + r * 150 for r in range(rows)]
    hc, hr = 2, 1
    if u > 0:
        for r in range(rows):
            for c in range(cols):
                if (r, c) == (hr, hc): continue
                p = pop(t, cs(5) - 0.1 + 0.04 * (r * cols + c), 0.3)
                if p > 0:
                    L = Image.new("RGBA", (220, 300), (0, 0, 0, 0))
                    mini_house(ImageDraw.Draw(L), 110, 290, 0.62)
                    paste_c(img, L, gx[c], gy[r] - 70, p)
    # rumah Aru: besar dulu, lalu mengecil ke slot tengah grid
    s = 1.9 - (1.9 - 0.62) * u
    cx = 540 + (gx[hc] - 540) * u; cy = 760 + (gy[hr] - 80 - 760) * u
    L = Image.new("RGBA", (440, 520), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    mini_house(ld, 220, 470, 1.0, hl=u > 0.5)
    for x, y in ((160, 236), (280, 236), (220, 180)):
        Hm.paste_c(L, Hm.galon(56), x, y)
    paste_c(img, L, cx, cy, s)
    p = pop(t, SC[1] + 0.2)
    if p > 0 and u < 0.6:
        paste_c(img, pill("38 galon", fill=YEL, fg=NAVY, size=44), 540, 1240, p * (1 - u / 0.6) if u > 0 else p)
    if u > 0.6:
        q = pop(t, cs(5) + 0.4)
        paste_c(img, pill("atapmu", fill=YEL, fg=NAVY, size=34), gx[hc], gy[hr] + 40, q)
    p = pop(t, cs(7) - 0.1)
    if p > 0:
        T = Image.new("RGBA", (820, 380), (0, 0, 0, 0)); td = ImageDraw.Draw(T)
        pool(td, 30, 40, 760, 300, lanes=6)
        paste_c(img, T, W / 2, 1190, p)
        q = pop(t, cs(7) + 0.35)
        if q > 0:
            paste_c(img, pill("? KOLAM", fill=YEL, fg=NAVY, size=86, padx=46), W / 2, 1190, q,
                    3 * math.sin(t * 5))
    if t >= cs(6):
        paste_c(img, bubble("coba tebak!", size=40, tail="left"), 300, 1440 - 40, pop(t, cs(6)))


def scene2(img, t):
    """patokan BMKG: hujan sangat lebat >20 mm/jam (gelas ukur terisi sampai garis 20 mm)."""
    d = ImageDraw.Draw(img)
    x0, x1, top, bot = 230, 430, 470, 1330
    mm_px = (bot - top - 60) / 30.0
    # tetes hujan masuk ke gelas ukur
    r = random.Random(9)
    for k in range(14):
        x = r.uniform(x0 + 20, x1 - 20); ph = r.random()
        y = 400 + ((t * 1.6 + ph) % 1.0) * (bot - 420)
        d.line([(x, y), (x - 6, y + 34)], fill=(120, 150, 200), width=5)
    lvl = 0.0
    if t >= cs(8) + 0.2:
        lvl = 20.0 * eio((t - cs(8) - 0.2) / (cs(10) + 0.6 - cs(8) - 0.2))
    if t >= cs(10) + 0.6:
        lvl = 20.0 + 2.0 * eout((t - cs(10) - 0.6) / 0.8)      # "lebih dari" 20 mm
    wy = bot - 10 - lvl * mm_px
    d.rounded_rectangle((x0 + 8, wy, x1 - 8, bot - 8), 18, fill=WATER_L)
    d.line([(x0 + 10, wy), (x1 - 10, wy)], fill=WATER, width=6)
    d.rounded_rectangle((x0, top, x1, bot), 24, outline=NAVY, width=8)
    d.line([(x0 - 20, top), (x1 + 20, top)], fill=NAVY, width=10)
    d.rounded_rectangle((x0 - 30, bot, x1 + 30, bot + 26), 10, fill=NAVY)
    for mm in range(0, 31, 5):
        y = bot - 10 - mm * mm_px
        long_ = mm % 10 == 0
        d.line([(x1 - (60 if long_ else 34), y), (x1 - 8, y)], fill=NAVY, width=5 if long_ else 3)
        if long_ and mm > 0:
            text_c(d, (x0 + 50, y), str(mm), F("pb", 34), NAVY)
    y20 = bot - 10 - 20 * mm_px
    hot = t >= cs(10)
    d.line([(x1 + 10, y20), (x1 + 70, y20)], fill=RED if hot else GREY_T, width=8)
    if hot:
        q = pop(t, cs(10))
        paste_c(img, pill("20 mm", fill=RED, fg=WHITE, size=46), x1 + 150, y20, q)
    text_c(d, (330, bot + 70), "gelas ukur hujan", F("pm", 32), INK)
    # kartu BMKG
    p = pop(t, SC[2] + 0.1)
    if p > 0:
        T, td = card(380, 170, fill=WHITE)
        text_c(td, (190, 60), "patokan", F("pm", 34), GREY_T)
        text_c(td, (190, 118), "BMKG", F("pb", 70), NAVY)
        paste_c(img, T, 760, 560, p)
    p = pop(t, cs(9) - 0.05)
    if p > 0:
        T, td = card(380, 230, fill=RED)
        text_c(td, (190, 70), "HUJAN", F("pb", 46), WHITE)
        text_c(td, (190, 150), "SANGAT LEBAT", fit("pb", 46, "SANGAT LEBAT", 340), YEL)
        paste_c(img, T, 760, 800, p, -2)
    p = pop(t, cs(10) + 0.1)
    if p > 0:
        T, td = card(380, 200, fill=YEL)
        text_c(td, (190, 80), ">20 mm", F("pb", 76), NAVY)
        text_c(td, (190, 155), "per jam", F("pb", 40), NAVY)
        paste_c(img, T, 760, 1060, p, 2)


def scene3(img, t):
    """kedengarannya tipis (lapisan air 2 cm), padahal tiap 1 m² = 20 liter (20 botol 1 L)."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[3] + 0.05)
    if p > 0:
        T = Image.new("RGBA", (860, 470), (0, 0, 0, 0)); td = ImageDraw.Draw(T)
        # ubin 1 x 1 m (perspektif), air setinggi 2 cm
        A, B, C, D = (130, 260), (430, 150), (790, 250), (490, 370)
        th = 26
        td.polygon([A, D, (D[0], D[1] + 40), (A[0], A[1] + 40)], fill=(178, 186, 204), outline=NAVY)
        td.polygon([D, C, (C[0], C[1] + 40), (D[0], D[1] + 40)], fill=(198, 204, 218), outline=NAVY)
        td.polygon([A, B, C, D], fill=(224, 228, 238), outline=NAVY)
        lift = th * eout((t - SC[3] - 0.2) / 0.6)
        if lift > 0:
            up = lambda q: (q[0], q[1] - lift)
            td.polygon([A, D, up(D), up(A)], fill=WATER)
            td.polygon([D, C, up(C), up(D)], fill=WATER_D)
            td.polygon([up(A), up(B), up(C), up(D)], fill=(150, 200, 244, 235))
        for a, b in ((A, B), (B, C), (C, D), (D, A)):
            td.line([a, b], fill=NAVY, width=5)
        if t >= cs(14) - 0.05:
            text_c(td, (300, 410), "1 m", F("pb", 40), NAVY)
            text_c(td, (690, 380), "1 m", F("pb", 40), NAVY)
        paste_c(img, T, W / 2, 640, p)
    q = pop(t, cs(12) + 0.3)
    if q > 0:
        paste_c(img, bubble("tipis: 2 cm", size=40, tail="left"), 300, 470, q)
    if t >= cs(14):
        paste_c(img, pill("1 m²", fill=NAVY, fg=YEL, size=48), 860, 470, pop(t, cs(14)))
    # 20 botol 1 L
    t0 = cs(15) - 0.15
    if t >= t0:
        n = int(clamp((t - t0) / 1.1) * 20 + 0.999)
        for k in range(n):
            r_, c_ = divmod(k, 10)
            pp = pop(t, t0 + k * 0.055, 0.25)
            paste_c(img, bottle(118), 196 + c_ * 76, 1010 + r_ * 150, pp)
        cnt = n
        paste_c(img, pill(f"{cnt} LITER", fill=YEL, fg=NAVY, size=64, padx=46), W / 2, 1360, pop(t, t0 + 0.2))


def scene4(img, t):
    """atap 36 m² (6 x 6 kotak) -> 720 liter, sejam saja."""
    p = pop(t, SC[4] + 0.05)
    if p > 0:
        T, td = head_card(560, 610, "ATAP 36 m²*", col=ROOF, size=44)
        lit_t0 = cs(16) + 0.2
        n = int(clamp((t - lit_t0) / 1.2) * 36) if t >= lit_t0 else 0
        for k in range(36):
            r_, c_ = divmod(k, 6)
            x = 40 + c_ * 80; y = 125 + r_ * 77
            td.rounded_rectangle((x, y, x + 72, y + 69), 10, fill=WATER_L if k < n else (246, 222, 214),
                                 outline=NAVY, width=3)
            if k < n:
                td.text((x + 36, y + 36), "20L", font=F("pb", 22), fill=WATER_D, anchor="mm")
        paste_c(img, T, W / 2, 740, p)
    p = pop(t, cs(17) - 0.1)
    if p > 0:
        T, td = card(820, 230, fill=WHITE)
        v = 720 * eout((t - cs(17)) / 1.0)
        td.text((60, 115), num(round(v)), font=F("pb", 120), fill=NAVY, anchor="lm")
        td.text((360, 140), "LITER", font=F("pb", 60), fill=WATER_D, anchor="lm")
        Hm.paste_c(T, Hm.galon(70), 640, 92)
        td.text((700, 92), "≈ 38", font=F("pb", 44), fill=NAVY, anchor="lm")
        td.text((640, 170), "galon 19 L", font=F("pm", 30), fill=GREY_T, anchor="mm")
        paste_c(img, T, W / 2, 1210, p)
    p = pop(t, cs(18))
    if p > 0:
        paste_c(img, stamp("SEJAM SAJA", col=RED, size=58), 760, 1380, p, -8)


def jkt_pts(x0, y0, w, h): return [(x0 + a * w, y0 + b * h) for a, b in JKT]


@lru_cache(None)
def jkt_mask(x0, y0, w, h):
    M = Image.new("L", (W, H), 0); ImageDraw.Draw(M).polygon(jkt_pts(x0, y0, w, h), fill=255)
    return M


def scene5(img, t):
    """seluruh Jakarta: 661 km² daratan (peta flat + grid menyala, sumber BPS)."""
    d = ImageDraw.Draw(img)
    x0, y0, w, h = 150, 520, 780, 600
    # laut (utara) -- datar, tanpa genangan
    d.rectangle((0, 400, W, 590), fill=(206, 226, 244))
    for k in range(6):
        x = (k * 190 + t * 40) % (W + 200) - 100
        d.arc((x, 440, x + 80, 480), 200, 340, fill=(150, 190, 230), width=5)
    text_c(d, (W / 2, 445), "Laut Jawa", F("pm", 30), (100, 140, 190))
    pts = jkt_pts(x0, y0, w, h)
    p = eout((t - SC[5] - 0.05) / 0.5)
    G = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(G)
    gd.polygon(pts, fill=(246, 236, 210))
    sweep = clamp((t - cs(19)) / (cs(21) + 0.4 - cs(19)))
    cell = 40
    for gx in range(x0, x0 + w, cell):
        lit = (gx - x0) / w < sweep
        for gy in range(y0, y0 + h, cell):
            if lit:
                gd.rectangle((gx + 3, gy + 3, gx + cell - 3, gy + cell - 3), fill=(255, 212, 110))
    for gx in range(x0, x0 + w + 1, cell):
        gd.line([(gx, y0), (gx, y0 + h)], fill=(214, 196, 160), width=2)
    for gy in range(y0, y0 + h + 1, cell):
        gd.line([(x0, gy), (x0 + w, gy)], fill=(214, 196, 160), width=2)
    a = G.getchannel("A"); from PIL import ImageChops
    G.putalpha(ImageChops.multiply(a, jkt_mask(x0, y0, w, h)))
    if p > 0:
        Gp = G
        if p < 0.999:
            al = Gp.getchannel("A").point(lambda v: int(v * p)); Gp = Gp.copy(); Gp.putalpha(al)
        img.alpha_composite(Gp)
        d = ImageDraw.Draw(img)
        d.line(pts + [pts[0]], fill=NAVY, width=7, joint="curve")
        text_c(d, (x0 + w * 0.5, y0 + h * 0.42), "JAKARTA", F("pb", 64), NAVY, stroke_width=6, stroke_fill=WHITE)
    p = pop(t, cs(21) - 0.05)
    if p > 0:
        T, td = card(640, 190, fill=YEL)
        v = 660.98 * eout((t - cs(21)) / 1.2)
        s_ = f"{v:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".") + " km²"
        text_c(td, (320, 95), s_, F("pb", 92), NAVY)
        paste_c(img, T, W / 2, 1250, p)
    if t >= cs(22):
        paste_c(img, pill("daratan", fill=NAVY, fg=WHITE, size=40), 830, 1390, pop(t, cs(22)))


def scene6(img, t):
    """kalau merata: 20 L × 661 juta m² = 13,2 miliar liter. Sejam!"""
    p = pop(t, SC[6] + 0.05)
    if p > 0:
        T, td = head_card(820, 330, "KALAU MERATA SE-JAKARTA*", col=NAVY, size=42)
        hot = t >= cs(24) - 0.05
        td.rounded_rectangle((40, 140, 330, 290), 24, fill=WATER_L if hot else LIGHT, outline=NAVY, width=4)
        text_c(td, (185, 200), "20 L", F("pb", 66), NAVY)
        text_c(td, (185, 262), "per m²", F("pm", 28), GREY_T)
        text_c(td, (380, 215), "×", F("pb", 80), RED if hot else GREY_T)
        td.rounded_rectangle((430, 140, 780, 290), 24, fill=(255, 236, 180) if hot else LIGHT, outline=NAVY, width=4)
        text_c(td, (605, 200), "661 juta", F("pb", 60), NAVY)
        text_c(td, (605, 262), "m² daratan", F("pm", 28), GREY_T)
        paste_c(img, T, W / 2, 640, p)
    if t >= cs(24):
        d = ImageDraw.Draw(img)
        u = eout((t - cs(24)) / 0.5)
        arrow(d, W / 2, 830, W / 2, 830 + 120 * u, RED, w=20, head=44)
    p = pop(t, cs(25) - 0.1)
    if p > 0:
        T, td = card(860, 300, fill=WHITE, outline=WATER_D, ow=7)
        v = 13_200_000_000 * eout((t - cs(25)) / 1.3)
        s_ = num(round(v / 1e6) * 1e6)
        text_c(td, (430, 120), s_, fit("pb", 104, "13.200.000.000", 800), WATER_D)
        text_c(td, (430, 230), "LITER  (±13,2 miliar)", F("pb", 44), NAVY)
        paste_c(img, T, W / 2, 1100, p)
    p = pop(t, cs(26))
    if p > 0:
        paste_c(img, stamp("SEJAM!", col=RED, size=76), 780, 1340, p, -10)


def scene7(img, t):
    """1 kolam olimpiade = 50 × 25 × 2 m = 2,5 juta L -> 5.300 kolam."""
    p = pop(t, SC[7] + 0.05)
    if p > 0:
        T, td = head_card(820, 380, "1 KOLAM OLIMPIADE", col=TEAL, size=44)
        pool(td, 60, 130, 330, 200, lanes=6, ow=5)
        td.text((440, 170), "50 × 25 × 2 m", font=F("pb", 40), fill=NAVY, anchor="lm")
        if t >= cs(28) - 0.05:
            q = clamp((t - cs(28) + 0.05) / 0.3)
            td.rounded_rectangle((430, 225, 790, 320), 24, fill=YEL)
            td.text((610, 272), "2,5 juta L", font=F("pb", int(50 * (0.6 + 0.4 * q))), fill=NAVY, anchor="mm")
        paste_c(img, T, W / 2, 640, p)
    t0 = cs(30) - 0.2
    if t >= t0:
        d = ImageDraw.Draw(img)
        n = int(clamp((t - t0) / 1.0) * 20)
        for k in range(n):
            r_, c_ = divmod(k, 4)
            x = 150 + c_ * 122; y = 900 + r_ * 92
            pool(d, x + 12, y + 12, 86, 52, lanes=3, ow=3)
        v = 5300 * eout((t - cs(30)) / 1.2)
        paste_c(img, pill(f"{num(max(1, round(v / 10) * 10))} KOLAM", fill=YEL, fg=NAVY, size=72, padx=44),
                450, 1060, pop(t, cs(30)))
    draw_aru(img, 880, 1450, 250, t)
    if t >= cs(30) + 0.5:
        paste_c(img, bubble("hitung dulu!", size=38, tail="right"), 790, 1160, pop(t, cs(30) + 0.5))


def scene8(img, t):
    """bersihkan talang sebelum puncak hujan: daun disapu, Si Bocor terlempar, air (38 galon) mengalir lewat pipa."""
    rain(img, t, n=50, col=(140, 165, 210), alpha=130, seed=21, length=60, width=4)
    d = ImageDraw.Draw(img)
    # atap (lereng) + talang + pipa turun
    d.polygon([(60, 430), (960, 640), (960, 760), (60, 550)], fill=ROOF, outline=NAVY)
    for k in range(1, 8):
        x = 60 + k * 112
        d.line([(x, 430 + (x - 60) * 210 / 900), (x, 550 + (x - 60) * 210 / 900)], fill=(190, 78, 52), width=5)
    d.line([(60, 550), (960, 760)], fill=NAVY, width=7)
    gx0, gx1, gy0, gy1 = 100, 900, 780, 860
    clean = t >= cs(32) + 0.3
    flow = t >= cs(33) - 0.2
    d.rounded_rectangle((gx0, gy0, gx1, gy1), 16, fill=(160, 166, 180), outline=NAVY, width=6)
    if flow:
        d.rectangle((gx0 + 10, gy0 + 34, gx1 - 10, gy1 - 10), fill=WATER)
        for k in range(10):
            x = gx0 + 20 + ((k * 80 + t * 260) % (gx1 - gx0 - 60))
            d.line([(x, gy0 + 46), (x + 30, gy0 + 46)], fill=WHITE, width=5)
    px0, px1 = 820, 890
    d.rectangle((px0, gy1 - 4, px1, 1400), fill=(170, 176, 190), outline=NAVY, width=6)
    d.rounded_rectangle((px0 - 30, 1380, px1 + 50, 1420), 12, fill=(170, 176, 190), outline=NAVY, width=6)
    if flow:
        for k in range(5):
            u = (t * 1.8 + k / 5) % 1.0
            d.ellipse((px1 + 40 + u * 40, 1395 + u * 30, px1 + 58 + u * 40, 1413 + u * 30), fill=WATER)
    # daun + Si Bocor tersangkut, lalu disapu
    r = random.Random(5)
    tc = cs(32)
    for k in range(18):
        lx = r.uniform(260, 700); ly = r.uniform(gy0 - 30, gy0 + 10); ang = r.uniform(0, 180)
        vx, vy = r.uniform(300, 700), r.uniform(-900, -500)
        if t >= tc:
            dt = t - tc - k * 0.015
            if dt > 0:
                lx += vx * dt; ly += vy * dt + 1400 * dt * dt; ang += 400 * dt
        if ly > H or lx > W + 60: continue
        L = Image.new("RGBA", (80, 44), (0, 0, 0, 0)); ldd = ImageDraw.Draw(L)
        ldd.ellipse((4, 4, 76, 40), fill=LEAF if k % 2 else LEAF_D, outline=NAVY, width=3)
        ldd.line([(10, 22), (70, 22)], fill=LEAF_D, width=3)
        paste_c(img, L, lx, ly, 1.0, ang)
    tb = t - (tc + 0.5)
    bx, by, ba = 470, gy0 - 40, -8
    if tb > 0:
        bx += 520 * tb; by += -900 * tb + 1500 * tb * tb; ba += 500 * tb
    if by < H + 100:
        paste_c(img, bocor_img(), bx, by, 0.48, ba)
    if not clean and t < tc:
        q = pop(t, SC[8] + 0.3)
        if q > 0:
            paste_c(img, bubble("tersangkut!", col=RED, fg=WHITE, size=36, tail="left"), 600, gy0 - 170, q)
    # sapu
    if tc - 0.2 <= t < tc + 0.9:
        u = clamp((t - tc + 0.2) / 1.1)
        sx = 220 + 560 * u; sy = gy0 - 40
        S = Image.new("RGBA", (200, 300), (0, 0, 0, 0)); sd = ImageDraw.Draw(S)
        sd.line([(100, 10), (100, 200)], fill=(150, 100, 50), width=14)
        sd.polygon([(60, 200), (140, 200), (170, 290), (30, 290)], fill=YEL, outline=NAVY)
        paste_c(img, S, sx, sy - 90, 1.0, -30 + 40 * math.sin(u * math.pi * 3))
    # 38 galon mengalir keluar lewat pipa
    if t >= cs(34) - 0.1:
        v = 38 - 38 * eio((t - cs(34)) / (cs(35) + 0.8 - cs(34)))
        G = Hm.galon(70)
        for k in range(3):
            u = ((t - cs(34)) * 1.2 + k / 3) % 1.0
            if v > 0.5:
                paste_c(img, G, px0 + 35, gy1 + 40 + u * 460, 0.8, 0)
        T, td = card(420, 170, fill=WHITE)
        Hm.paste_c(T, Hm.galon(90), 80, 85)
        td.text((150, 85), f"{round(v)}", font=F("pb", 96), fill=NAVY, anchor="lm")
        td.text((345, 110), "galon", font=F("pb", 32), fill=GREY_T, anchor="mm")
        paste_c(img, T, 420, 1080, pop(t, cs(34) - 0.1))
    if t >= cs(35):
        P = pill("   butuh jalan", fill=GREEN, fg=WHITE, size=46)
        icon_check(ImageDraw.Draw(P), 46, 45, 0.7, col=NAVY)
        paste_c(img, P, 420, 1300, pop(t, cs(35)))
    draw_aru(img, 200, 1460, 230, t)


def scene9(img, t):
    """ajakan komentar: talang rumahmu pernah meluap? PERNAH / BELUM + usulan terpilih tampil di reel berikutnya."""
    p = pop(t, SC[9] + 0.05)
    if p > 0:
        B = Image.new("RGBA", (860, 360), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((10, 12, 850, 312), 34, fill=(20, 33, 91, 45))
        bd.rounded_rectangle((0, 0, 840, 300), 34, fill=WHITE, outline=NAVY, width=5)
        bd.polygon([(110, 296), (180, 296), (90, 350)], fill=WHITE, outline=NAVY)
        bd.line([(112, 299), (178, 299)], fill=WHITE, width=8)
        text_c(bd, (420, 95), "Talang rumahmu", F("pb", 62), NAVY)
        text_c(bd, (420, 195), "pernah meluap?", F("pb", 62), RED if t >= cs(37) else NAVY)
        paste_c(img, B, W / 2, 640, p)
    for k, (s, col, t0) in enumerate((("PERNAH", RED, cs(37) + 0.2), ("BELUM", TEAL, cs(38)))):
        q = pop(t, t0)
        if q > 0:
            beat = 1 + 0.04 * math.sin((t - t0) * 7 + k * math.pi)
            paste_c(img, pill(s, fill=col, fg=WHITE, size=58, padx=50), 330 + k * 420, 925, q * beat, -2 + 4 * k)
    q = pop(t, cs(39) - 0.05)
    if q > 0:
        T, td = card(820, 250, fill=NAVY)
        text_c(td, (410, 70), "Tulis di komentar!", F("pb", 56), YEL)
        text_c(td, (410, 148), "usulan \"hitung apa lagi?\" like terbanyak", F("pm", 32), WHITE)
        text_c(td, (410, 200), "dihitung di reel berikutnya + namamu tampil", F("pm", 32), WHITE)
        paste_c(img, T, W / 2, 1140, q)
    draw_aru(img, 900, 1470, 190, t)


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9]


def draw_notes(img, k):
    lines = NOTES.get(k)
    if not lines: return
    d = ImageDraw.Draw(img)
    for j, s in enumerate(lines):
        f = fit("pm", 28, s, W - 2 * SAFE_X)
        d.text((W / 2, 1722 + j * 40), s, font=f, fill=GREY_T, anchor="mm")


CT_SRC = Hm.CT0  # catatan ilustrasi muncul bersama counter (PRB-39)


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
            paste_c(img, L, W / 2, 1722, 1, 0, a)
    draw_sub(img, t)
    if k > 0 and t < CLOSE:
        draw_notes(img, k)
    if FOLLOW[0] <= t < FOLLOW[1]:
        f = F("pb", 30); s_ = "follow @kabar.arunika · hitungan & fakta 1 menit"
        tw = f.getlength(s_)
        pl = Image.new("RGBA", (int(tw) + 60, 60), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
        pd.rounded_rectangle((0, 0, tw + 60, 60), 30, fill=TEAL)
        pd.text((30, 30), s_, font=f, fill=WHITE, anchor="lm")
        a = min(clamp((t - FOLLOW[0]) / 0.25), clamp((FOLLOW[1] - t) / 0.25))
        paste_c(img, pl, W / 2, 1490, 1, 0, a)
    la = clamp((t - CLOSE) / 0.3)
    if la > 0:
        paste_c(img, logo_w(300), W / 2, 1740, 0.9 + 0.1 * back(la), 0, la)
    if t >= 3.0:   # progress bar: bukan di dtk 0-3 (PRB-34)
        ImageDraw.Draw(img).rectangle((0, H - 14, int(W * t / TOTAL), H), fill=YEL)
    return img.convert("RGB")


def events():
    ev = [{"t": SC[k], "sfx": "whoosh", "gain": 0.30} for k in range(1, NS)]
    ev.append({"t": 0.05, "sfx": "pop", "gain": 0.3})           # galon mendarat frame 0
    ev.append({"t": Hm.CT0, "sfx": "pop", "gain": 0.3})         # counter mulai naik
    ev.append({"t": Hm.CT1, "sfx": "ding", "gain": 0.25})
    for i in (5, 7, 9, 10, 14, 15, 17, 18, 21, 22, 24, 25, 26, 28, 30, 34, 35, 37, 38, 39):
        ev.append({"t": cs(i), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": cs(32) + 0.5, "sfx": "cring", "gain": 0.45})  # Si Bocor terlempar
    ev.append({"t": cs(30), "sfx": "ding", "gain": 0.35})         # payoff 5.300 kolam
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

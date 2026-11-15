"""Renderer ARN-47 "Mana Lebih Hemat? #8 — bon makan bareng: bagi rata vs bayar masing-masing" — Flat 2D latar terang (PRB-31).
Salinan sore/render_flat_motor.py (helper kartu, koin, Si Bocor, panah, Aru, logo, subtitle, cek area aman, sfx) dengan:
- frame 0: bon raksasa (satu objek besar) berisi counter "KAMU BAYAR" Rp30.000 -> Rp60.000 bergerak dtk 1,6-2,6
  (PRB-29/36/46); Aru memegang piring nasi goreng kecil, Si Bocor menarik koin dari dompet Aru ke bon ("cring!");
  judul layar "SEBERAPA ADIL BAGI RATA?"; tanpa label seri/logo/progress bar dtk 0-3.
- 15 adegan (tiap <= 6 dtk), layar terbelah tim BAGI RATA vs tim MASING-MASING di adegan 8-11,
  ajakan kirim di puncak Rp1.560.000 (PRB-55), komentar terpilih @knarkha (#7) hanya di adegan terakhir (PRB-43/51).
- area aman (PRB-41): semua pill/bubble/kartu <= 800 px dan di x 130..950; `check` memindai tiap 0,1 dtk.
Pemakaian (dari folder kerja pagi/build/bon, setelah align_bon.py -> timing.json):
  TOTAL=64.4 python3 ../../render_flat_bon.py events | check | stills 0,2,... | video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, rp, NAVY, TEAL, YEL, WHITE, GREY_T, RED, SAFE_X)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "64.4"))
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
GREEN = (46, 160, 110); INK = (60, 66, 92); LIGHT = (232, 238, 246)
BODY = (224, 82, 63); BODY_D = (176, 56, 44)
MAXW, XMIN, XMAX = 800, 130, 950   # PRB-41

TIM = json.load(open("timing.json"))
def cs(i): return TIM[i]["start"] + LEAD
def ce(i): return TIM[i]["end"] + LEAD

SCENE_CHUNK = [0, 6, 11, 15, 19, 24, 28, 32, 34, 38, 41, 44, 49, 54, 57]
SC = [0.0] + [cs(i) - 0.25 for i in SCENE_CHUNK[1:]] + [TOTAL]
NS = len(SCENE_CHUNK)
FOLLOW = (10.6, 15.0)          # PRB-4: ajakan follow teks kecil dtk 10-15
PB_START = 3.5                 # progress bar mulai dtk 3,5
ILU = "*angka contoh ilustrasi; harga menu tiap orang beda"
NOTES = {k: (ILU,) for k in range(0, 8)}            # angka adegan 3-9 naskah (PRB-39: tanpa sumber -> label ilustrasi)
CT0, CT1 = 1.6, 2.6            # counter frame 0
C0, C1 = 30000, 60000
SHARE = (cs(33) - 0.3, cs(37) - 0.2)   # ajakan kirim di puncak angka (PRB-55 poin 3)


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


# ---------- pelacak area aman (PRB-41) ----------
BOXES = []   # (tag, lebar nominal, x0, x1) untuk frame yang sedang digambar
def track(tag, nw, x0, x1):
    BOXES.append((tag, nw, x0, x1))


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


def paste_c(dst, im, cx, cy, scale=1.0, angle=0.0, alpha=1.0, tag=None):
    if scale <= 0.01 or alpha <= 0.01: return
    nw = im.info.get("nw", im.width)       # lebar nominal elemen (tanpa bayangan)
    if tag:
        s = min(scale, 1.0)
        track(tag, nw, cx - nw * s / 2, cx + nw * s / 2)
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
    paste_c(layer, im, cx, bottom - h / 2 + b, 1.0, ang, tag="aru")


def text_c(d, xy, s, font, fill, anchor="mm", **kw):
    d.text(xy, s, font=font, fill=fill, anchor=anchor, **kw)


def fit(name, size, s, maxw):
    f = F(name, size)
    while f.getlength(s) > maxw and size > 14:
        size -= 2; f = F(name, size)
    return f


def card(w, h, fill=WHITE, r=30, outline=NAVY, ow=5):
    assert w <= MAXW, ("kartu", w)
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 12, w + 10, h + 12), r, fill=(20, 33, 91, 45))
    d.rounded_rectangle((0, 0, w, h), r, fill=fill, outline=outline, width=ow)
    im.info["nw"] = w
    return im, d


def head_card(w, h, title, col=TEAL, size=40, fill=WHITE):
    L, cd = card(w, h, fill=fill)
    cd.rounded_rectangle((0, 0, w, 96), 30, fill=col); cd.rectangle((0, 50, w, 96), fill=col)
    cd.rounded_rectangle((0, 0, w, h), 30, outline=NAVY, width=5)
    text_c(cd, (w / 2, 50), title, fit("pb", size, title, w - 60), WHITE if col != YEL else NAVY)
    return L, cd


def pill(text, fill=NAVY, fg=WHITE, size=50, padx=36, h=None, outline=NAVY):
    f = F("pb", size); w = int(f.getlength(text) + 2 * padx); h = h or size + 46
    assert w <= MAXW, ("pill", text, w)
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 10, w + 8, h + 10), h // 2, fill=(20, 33, 91, 55))
    d.rounded_rectangle((0, 0, w, h), h // 2, fill=fill, outline=outline, width=5)
    text_c(d, (w / 2, h / 2 + 2), text, f, fg)
    im.info["nw"] = w
    return im


def coin(r=26):
    im = Image.new("RGBA", (2 * r + 6, 2 * r + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((3, 3, 2 * r + 3, 2 * r + 3), fill=(255, 194, 60), outline=(217, 154, 31), width=4)
    text_c(d, (r + 3, r + 3), "Rp", F("pb", int(r * 0.75)), (154, 106, 16))
    return im


@lru_cache(None)
def bocor_img():
    """Si Bocor menarik karung "Rp" bolong (lubang di bawah karung)."""
    im = Image.new("RGBA", (300, 270), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line([(60, 200), (30, 185), (12, 150), (22, 125)], fill=(244, 163, 184), width=7, joint="curve")
    d.line([(170, 150), (205, 120)], fill=(150, 110, 60), width=6)              # tali tarik
    d.polygon([(150, 70), (255, 88), (246, 238), (142, 228)], fill=(201, 162, 107), outline=NAVY)
    d.line([(150, 70), (255, 88), (246, 238), (142, 228), (150, 70)], fill=NAVY, width=5)
    text_c(d, (200, 150), "Rp", F("pb", 46), (122, 90, 46))
    d.ellipse((210, 206, 236, 226), fill=NAVY)                                  # bolong
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
BOCOR_HOLE = (223, 216)   # titik lubang karung (koordinat bocor_img)


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


def bubble(text, col=NAVY, fg=YEL, size=44, tail="left"):
    f = F("pb", size); w = int(f.getlength(text) + 70)
    assert w <= MAXW, ("bubble", text, w)
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
    assert w <= MAXW, ("stamp", text, w)
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


FLOOR0 = 1440
@lru_cache(None)
def bg_scene0():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((140, 620, 940, 1420), fill=(252, 236, 196))
    for k in range(10):
        a = k * math.pi / 5; r0, r1 = 420, 470
        d.line([(540 + r0 * math.cos(a), 1020 + r0 * math.sin(a)), (540 + r1 * math.cos(a), 1020 + r1 * math.sin(a))],
               fill=(250, 214, 120), width=10)
    d.rectangle((0, FLOOR0, W, H), fill=(218, 223, 232)); d.line([(0, FLOOR0), (W, FLOOR0)], fill=NAVY, width=5)
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
    f = F("pb", 34); s1 = "MANA LEBIH HEMAT?"; s2 = "#8"
    w1 = f.getlength(s1); w2 = f.getlength(s2)
    tot = w1 + w2 + 52 + 40 + 12
    assert tot <= MAXW
    x0 = (W - tot) / 2
    d.rounded_rectangle((x0, 30, x0 + w1 + 52, 96), 33, fill=NAVY)
    d.text((x0 + 26, 63), s1, font=f, fill=WHITE, anchor="lm")
    x1 = x0 + w1 + 52 + 12
    d.rounded_rectangle((x1, 30, x1 + w2 + 40, 96), 33, fill=YEL)
    d.text((x1 + 20, 63), s2, font=f, fill=NAVY, anchor="lm")
    return L, x0, x0 + tot


def title_pills(img, rows, y, size=76, gap=16, keyword="ADIL"):
    """judul cover (kolom Judul layar): kotak per kata, ADIL kuning; tiap baris <= 800 px."""
    d = ImageDraw.Draw(img); f = F("pb", size); padx = 26; hh = size + 34
    for row, line in enumerate(rows):
        ws = [f.getlength(w) + 2 * padx for w in line]
        tot = sum(ws) + gap * (len(ws) - 1)
        assert tot <= MAXW, (line, tot)
        x = (W - tot) / 2; yy = y + row * (hh + 18)
        track("judul", tot, x, x + tot)
        for w, ww in zip(line, ws):
            key = w.strip("?") == keyword
            d.rounded_rectangle((x + 7, yy + 8, x + ww + 7, yy + hh + 8), 14, fill=(0, 0, 0, 40))
            d.rounded_rectangle((x, yy, x + ww, yy + hh), 14, fill=YEL if key else NAVY)
            d.text((x + ww / 2, yy + hh / 2 + 2), w, font=f, fill=NAVY if key else WHITE, anchor="mm")
            x += ww + gap


# ---------- subtitle 1 baris (PRB-37), lebar <= W-300 (PRB-41) ----------
SUB_MAX = W - 300
def sub_chunk(t):
    for i, c in enumerate(TIM):
        s = 0.0 if i == 0 else cs(i)
        nxt = cs(i + 1) if i + 1 < len(TIM) else TOTAL
        e = min(nxt, ce(i) + 0.45)
        if s <= t < e:
            return i
    return None


@lru_cache(None)
def sub_layer(i, part=0):
    c = TIM[i]; words = c["text"].split("|")[part].split()
    size = 66
    while True:
        f = F("pb", size); padx = 24; gap = 14
        ws = [f.getlength(w) + 2 * padx for w in words]
        tot = sum(ws) + gap * (len(ws) - 1)
        if tot <= SUB_MAX or size <= 40: break
        size -= 2
    assert tot <= SUB_MAX, (c["text"], tot)
    hh = size + 30
    L = Image.new("RGBA", (int(tot) + 12, hh + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    x = 0
    for w, ww in zip(words, ws):
        key = w in c["keys"]
        d.rounded_rectangle((x + 7, 8, x + ww + 7, hh + 8), 14, fill=(0, 0, 0, 40))
        d.rounded_rectangle((x, 0, x + ww, hh), 14, fill=YEL if key else NAVY)
        d.text((x + ww / 2, hh / 2 + 2), w, font=f, fill=NAVY if key else WHITE, anchor="mm")
        x += ww + gap
    L.info["nw"] = int(tot)
    return L


def draw_sub(img, t):
    i = sub_chunk(t)
    if i is None: return
    s0 = 0.0 if i == 0 else cs(i)
    part = 0
    parts = TIM[i]["text"].split("|")
    if len(parts) > 1:
        mid = cs(i) + (ce(i) - cs(i)) * len(parts[0]) / (len(parts[0]) + len(parts[1]))
        if t >= mid:
            part, s0 = 1, mid
    sc = 0.85 + 0.15 * back((t - s0) / 0.22) if i != 0 else 1.0
    paste_c(img, sub_layer(i, part), W / 2, 1600, sc, tag="subtitle")


# ---------- ikon & tokoh adegan ----------
EMOJI_F = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"


@lru_cache(None)
def emoji_img(ch, h):
    from PIL import ImageFont
    f = ImageFont.truetype(EMOJI_F, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = trim(im); r = h / im.height
    return im.resize((max(1, int(im.width * r)), h), Image.LANCZOS)


def pill_emoji(text, ch, fill=NAVY, fg=WHITE, size=46, padx=34):
    f = F("pb", size); e = emoji_img(ch, int(size * 1.05)); h = size + 46
    w = int(f.getlength(text) + 2 * padx + e.width + 14)
    assert w <= MAXW, ("pill", text, w)
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 10, w + 8, h + 10), h // 2, fill=(20, 33, 91, 55))
    d.rounded_rectangle((0, 0, w, h), h // 2, fill=fill, outline=NAVY, width=5)
    d.text((padx, h / 2 + 2), text, font=f, fill=fg, anchor="lm")
    im.alpha_composite(e, (int(padx + f.getlength(text) + 14), int(h / 2 - e.height / 2)))
    im.info["nw"] = w
    return im


def scaled(im, w):
    r = w / im.width
    return im.resize((w, max(1, int(im.height * r))), Image.LANCZOS)


@lru_cache(None)
def plate_img(w, kind="nasi"):
    im = Image.new("RGBA", (300, 210), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((8, 118, 292, 202), fill=WHITE, outline=NAVY, width=6)
    d.ellipse((50, 132, 250, 186), fill=(236, 240, 246))
    if kind == "nasi":
        d.chord((62, 50, 238, 200), 180, 360, fill=(226, 150, 72), outline=NAVY, width=6)
        for x, y in ((100, 100), (140, 80), (178, 104), (120, 118), (160, 120)):
            d.ellipse((x, y, x + 12, y + 8), fill=(176, 98, 40))
        d.ellipse((112, 46, 196, 92), fill=WHITE, outline=NAVY, width=5)          # telur ceplok
        d.ellipse((140, 56, 168, 82), fill=YEL)
        d.ellipse((206, 120, 246, 150), fill=(120, 190, 90), outline=NAVY, width=4)   # timun
    else:   # steak
        d.ellipse((60, 70, 220, 168), fill=(140, 72, 44), outline=NAVY, width=6)
        for k in range(4):
            d.line([(90 + k * 32, 92), (120 + k * 32, 150)], fill=(92, 44, 26), width=7)
        d.ellipse((200, 100, 262, 150), fill=(240, 206, 120), outline=NAVY, width=5)  # kentang
        d.ellipse((40, 128, 80, 156), fill=(120, 190, 90), outline=NAVY, width=4)
    return scaled(trim(im), w)


@lru_cache(None)
def drink_img(h, kind="teh"):
    im = Image.new("RGBA", (170, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == "teh":
        d.line([(110, 10), (88, 120)], fill=RED, width=12)                          # sedotan
        d.polygon([(30, 70), (140, 70), (126, 290), (44, 290)], fill=(230, 240, 250), outline=NAVY)
        d.polygon([(36, 110), (134, 110), (126, 284), (46, 284)], fill=(214, 120, 48))
        for x, y in ((54, 120), (92, 140), (62, 180)):
            d.rounded_rectangle((x, y, x + 34, y + 30), 6, fill=(250, 214, 170), outline=(255, 240, 220), width=3)
        d.line([(30, 70), (140, 70), (126, 290), (44, 290), (30, 70)], fill=NAVY, width=6)
    else:   # kopi susu (gelas plastik + tutup)
        d.rounded_rectangle((20, 50, 150, 82), 12, fill=WHITE, outline=NAVY, width=5)
        d.line([(110, 0), (96, 60)], fill=NAVY, width=10)
        d.polygon([(32, 82), (138, 82), (124, 290), (46, 290)], fill=(206, 160, 116), outline=NAVY)
        d.polygon([(34, 82), (136, 82), (133, 130), (37, 130)], fill=(240, 226, 206))
        d.line([(32, 82), (138, 82), (124, 290), (46, 290), (32, 82)], fill=NAVY, width=6)
    im = trim(im); r = h / im.height
    return im.resize((int(im.width * r), h), Image.LANCZOS)


@lru_cache(None)
def dia_img(h):
    """'dia' = teman yang selalu pesan paling mahal: rambut jambul, kacamata hitam, jaket merah, senyum puas."""
    im = Image.new("RGBA", (320, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    SK = (240, 196, 160)
    for x in (112, 168):                                                         # kaki
        d.rounded_rectangle((x, 400, x + 42, 520), 16, fill=(70, 74, 96), outline=NAVY, width=6)
        d.ellipse((x - 14, 500, x + 56, 540), fill=WHITE, outline=NAVY, width=6)
    d.line([(96, 270), (46, 360)], fill=NAVY, width=34); d.line([(96, 270), (46, 360)], fill=RED, width=22)
    d.line([(226, 270), (276, 200)], fill=NAVY, width=34); d.line([(226, 270), (276, 200)], fill=RED, width=22)
    d.ellipse((30, 344, 66, 380), fill=SK, outline=NAVY, width=5); d.ellipse((260, 172, 296, 208), fill=SK, outline=NAVY, width=5)
    d.rounded_rectangle((86, 240, 236, 420), 40, fill=RED, outline=NAVY, width=6)  # jaket
    d.polygon([(140, 244), (182, 244), (161, 300)], fill=WHITE)
    d.line([(161, 300), (161, 410)], fill=NAVY, width=5)
    d.ellipse((76, 60, 246, 240), fill=SK, outline=NAVY, width=6)                # kepala
    d.polygon([(76, 130), (88, 52), (130, 30), (150, 50), (190, 18), (210, 50), (250, 60), (246, 130),
               (226, 96), (100, 96)], fill=(40, 36, 52), outline=NAVY)          # rambut jambul
    d.rounded_rectangle((96, 128, 156, 168), 14, fill=(30, 30, 40)); d.rounded_rectangle((166, 128, 226, 168), 14, fill=(30, 30, 40))
    d.line([(156, 142), (166, 142)], fill=(30, 30, 40), width=6)
    d.line([(108, 138), (128, 138)], fill=(120, 120, 140), width=4)
    d.arc((126, 168, 206, 214), 10, 150, fill=NAVY, width=6)                     # senyum puas
    im = trim(im); r = h / im.height
    out = im.resize((int(im.width * r), h), Image.LANCZOS)
    return out


@lru_cache(None)
def wallet_img(w):
    im = Image.new("RGBA", (220, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 20, 214, 144), 22, fill=(120, 84, 52), outline=NAVY, width=6)
    d.rounded_rectangle((120, 58, 214, 106), 16, fill=(150, 108, 70), outline=NAVY, width=5)
    d.ellipse((176, 72, 194, 90), fill=YEL)
    d.rectangle((30, 6, 110, 30), fill=(88, 160, 110))                            # uang menyembul
    return scaled(im, w)


def bon_img(w, h, rows, t, total=None, zig=True):
    """kertas bon; rows = [(kiri, kanan, warna)]; dikembalikan (im, draw)."""
    assert w <= MAXW, ("bon", w)
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(0, 0), (w, 0), (w, h)]
    n = 14
    for k in range(n, -1, -1):
        pts.append((w * k / n, h - (18 if k % 2 else 0)))
    sh = [(x + 10, y + 12) for x, y in pts]
    d.polygon(sh, fill=(20, 33, 91, 45))
    d.polygon(pts, fill=(255, 253, 246))
    d.line(pts + [pts[0]], fill=NAVY, width=5)
    im.info["nw"] = w
    return im, d


def card_text(d, xy, s, size, maxw, col=NAVY, name="pb", anchor="mm"):
    d.text(xy, s, font=fit(name, size, s, maxw), fill=col, anchor=anchor)


# ---------- adegan ----------
def counter_value(t):
    v = C0 + (C1 - C0) * eio((t - CT0) / (CT1 - CT0))
    return int(round(v / 1000.0) * 1000)


def scene0(img, t):
    """frame 0: bon raksasa + counter KAMU BAYAR 30.000 -> 60.000, Aru + piring kecil, Si Bocor menarik koin."""
    z = 1.0 + 0.06 * eio((t - 1.4) / 1.4)          # kamera maju pelan, visual berganti ~dtk 1,5
    title_pills(img, [["SEBERAPA", "ADIL"], ["BAGI", "RATA?"]], 290)
    v = counter_value(t); hot = v > C0
    bw, bh = 500, 700
    B, bd = bon_img(bw, bh, None, t)
    text_c(bd, (bw / 2, 60), "BON · MEJA 4", F("pb", 40), NAVY)
    dashed(bd, [(36, 106), (bw - 36, 106)], (170, 178, 195), w=4)
    for k, (a_, b_) in enumerate((("Nasi goreng + es teh", "30.000"), ("Steak + kopi susu", "120.000"),
                                   ("Mi ayam + jeruk", "45.000"), ("Ayam geprek + teh", "45.000"))):
        y = 152 + k * 56
        bd.text((36, y), a_, font=F("pm", 28), fill=NAVY if k == 0 else GREY_T, anchor="lm")
        bd.text((bw - 36, y), b_, font=F("pb", 28), fill=NAVY if k == 0 else GREY_T, anchor="rm")
    bd.line([(36, 380), (bw - 36, 380)], fill=NAVY, width=4)
    text_c(bd, (bw / 2, 430), "KAMU BAYAR", F("pb", 42), RED if hot else NAVY)
    bd.rounded_rectangle((30, 470, bw - 30, 610), 26, fill=(253, 228, 222) if hot else (255, 244, 205),
                         outline=RED if hot else NAVY, width=6)
    text_c(bd, (bw / 2 - (22 if hot else 0), 540), rp(v), F("pb", 84), RED if hot else NAVY)
    if hot:
        a = clamp((t - CT0) / 0.3)
        arrow(bd, bw - 62, 590, bw - 62, 590 - 100 * a, RED, w=16, head=34)
    paste_c(img, B, 670, 980, z, -1.2 * math.sin(t * 2), tag="bon")
    # dompet Aru + koin ditarik Si Bocor ke bon
    wx, wy = 540, 1400
    paste_c(img, wallet_img(170), wx, wy, tag="dompet")
    for k, ph in enumerate((0.0, 0.33, 0.66)):
        u = (t * 1.2 + ph) % 1.0
        x = wx + (720 - wx) * u; y = wy - 40 - 90 * math.sin(math.pi * u) - 40 * u
        paste_c(img, coin(24), x, y, 1.0, u * 300, alpha=1 - 0.5 * u)
    hop = abs(math.sin(t * 6)) * 6
    paste_c(img, bocor_img(), 830, 1330 - hop, 0.62, -6, tag="bocor")
    draw_aru(img, 282, 1440, int(410 * z), t)
    paste_c(img, plate_img(140), 380, 1270 + 4 * math.sin(t * 3), tag="piring")
    p = pop(t, cs(3))
    if p > 0:
        L = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.ellipse((8, 8, 192, 192), fill=YEL, outline=NAVY, width=8)
        text_c(d, (100, 98), "?", F("pb", 110), NAVY)
        paste_c(img, L, 240, 760, 0.9 * p, 8 * math.sin(t * 4), tag="lencana ?")


def scene1(img, t):
    """satu meja, empat orang; nasi goreng + es tehmu Rp30.000."""
    p = pop(t, SC[1] + 0.05)
    if p > 0:
        T, td = head_card(800, 560, "SATU MEJA, 4 ORANG", col=TEAL, size=46)
        td.rounded_rectangle((150, 170, 650, 520), 60, fill=(214, 168, 120), outline=NAVY, width=6)  # meja
        seats = [(250, 260, "KAMU"), (550, 260, ""), (250, 440, ""), (550, 440, "")]
        for k, (x, y, lab) in enumerate(seats):
            on = t >= cs(7) - 0.1 + 0.12 * k
            if not on: continue
            me = k == 0
            td.ellipse((x - 62, y - 62, x + 62, y + 62), fill=YEL if me else WHITE, outline=NAVY, width=5)
            if me:
                text_c(td, (x, y), "KAMU", F("pb", 34), NAVY)
            else:
                td.ellipse((x - 26, y - 40, x + 26, y + 12), fill=(186, 192, 210))
                td.chord((x - 44, y + 6, x + 44, y + 80), 180, 360, fill=(186, 192, 210))
        paste_c(img, T, W / 2, 770, p, tag="kartu meja")
    p = pop(t, cs(8) - 0.05)
    if p > 0:
        T, td = card(800, 300, fill=WHITE)
        T.alpha_composite(plate_img(220), (30, 60))
        Dk = drink_img(200); T.alpha_composite(Dk, (262, 50))
        text_c(td, (560, 70), "PESANANMU", F("pb", 40), GREY_T)
        u = eout((t - cs(10)) / 0.8) if t >= cs(10) - 0.05 else 0
        if u > 0:
            td.rounded_rectangle((372, 120, 770, 240), 24, fill=YEL)
            text_c(td, (571, 180), rp(int(round(30000 * u / 1000) * 1000)), F("pb", 76), NAVY)
        paste_c(img, T, W / 2, 1250, p, tag="kartu pesananmu")


def scene2(img, t):
    """'dia' yang selalu pesan paling mahal: steak + kopi susu Rp120.000."""
    p = pop(t, SC[2] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Kamu pasti kenal dia", "👀", fill=YEL, fg=NAVY, size=48), W / 2,
                480 + 5 * math.sin(t * 3), p, -2, tag="pill kenal dia")
    q = pop(t, SC[2] + 0.15)
    if q > 0:
        b = 6 * math.sin(2 * math.pi * 1.1 * t)
        paste_c(img, dia_img(620), 330, 1060 + b, q, 2 * math.sin(t * 1.6), tag="dia")
    p = pop(t, cs(12))
    if p > 0:
        T, td = head_card(440, 560, "PESANAN DIA", col=RED, size=40)
        T.alpha_composite(plate_img(260), (24, 140))
        T.alpha_composite(drink_img(190, "kopi"), (300, 110))
        td.text((220, 360), "steak + kopi susu", font=F("pm", 32), fill=GREY_T, anchor="mm")
        u = eout((t - cs(14)) / 0.9) if t >= cs(14) - 0.05 else 0
        if u > 0:
            td.rounded_rectangle((24, 410, 416, 530), 24, fill=RED)
            text_c(td, (220, 470), rp(int(round(120000 * u / 1000) * 1000)), F("pb", 64), WHITE)
        paste_c(img, T, 720, 950, p, 2, tag="kartu pesanan dia")
    p = pop(t, cs(13))
    if p > 0:
        paste_c(img, stamp("PALING MAHAL", col=RED, size=52), 540, 1330, p, -5, tag="stempel paling mahal")


def scene3(img, t):
    """total Rp240.000, lalu dia bilang 'Patungan ya!' di kasir."""
    p = pop(t, SC[3] + 0.05)
    if p > 0:
        bw, bh = 700, 560
        B, bd = bon_img(bw, bh, None, t)
        text_c(bd, (bw / 2, 56), "BON · MEJA 4", F("pb", 42), NAVY)
        dashed(bd, [(36, 100), (bw - 36, 100)], (170, 178, 195), w=4)
        rows = (("Kamu", "Rp30.000", YEL), ("Dia", "Rp120.000", RED), ("Teman A", "Rp45.000", None),
                ("Teman B", "Rp45.000", None))
        for k, (a_, b_, col) in enumerate(rows):
            y = 145 + k * 66
            if col:
                bd.rounded_rectangle((26, y - 28, bw - 26, y + 28), 14, fill=(255, 244, 205) if col == YEL else (253, 228, 222))
            bd.text((50, y), a_, font=F("pm", 38), fill=NAVY, anchor="lm")
            bd.text((bw - 50, y), b_, font=F("pb", 38), fill=NAVY, anchor="rm")
        bd.line([(36, 418), (bw - 36, 418)], fill=NAVY, width=5)
        u = eout((t - cs(16)) / 0.9) if t >= cs(16) - 0.05 else 0
        bd.text((50, 478), "TOTAL", font=F("pb", 48), fill=NAVY, anchor="lm")
        if u > 0:
            bd.text((bw - 50, 478), rp(int(round(240000 * u / 1000) * 1000)), font=F("pb", 62), fill=NAVY, anchor="rm")
        paste_c(img, B, W / 2, 740, p, -1, tag="bon total")
    if t >= cs(17) - 0.1:
        q = pop(t, cs(17) - 0.1)
        paste_c(img, dia_img(400), 290, 1260 + 5 * math.sin(t * 7), q, tag="dia")
        L = pill("KASIR", fill=NAVY, fg=WHITE, size=40)
        paste_c(img, L, 800, 1090, q, tag="pill kasir")
    p = pop(t, cs(18))
    if p > 0:
        paste_c(img, bubble("\"Patungan ya!\"", col=RED, fg=WHITE, size=56), 640, 1250,
                p * (1 + 0.03 * math.sin(t * 9)), 3, tag="bubble patungan")


def scene4(img, t):
    """bagi rata: 240.000 / 4 = 60.000 masing-masing; padahal pesananmu cuma setengahnya."""
    p = pop(t, SC[4] + 0.05)
    if p > 0:
        T, td = card(800, 260, fill=WHITE)
        text_c(td, (400, 62), "BAGI RATA", F("pb", 44), TEAL)
        text_c(td, (400, 150), "Rp240.000 ÷ 4", F("pb", 64), NAVY)
        if t >= cs(21) - 0.05:
            u = eout((t - cs(21)) / 0.7)
            td.rounded_rectangle((150, 196, 650, 250), 26, fill=YEL)
            text_c(td, (400, 224), "= " + rp(int(round(60000 * u / 1000) * 1000)) + " / orang", F("pb", 38), NAVY)
        paste_c(img, T, W / 2, 610, p, tag="kartu bagi")
    d = ImageDraw.Draw(img)
    base = 1330; hmax = 460
    bars = [(330, "PESANANMU", "Rp30.000", 30, YEL, cs(22) - 0.1), (750, "KAMU BAYAR", "Rp60.000", 60, RED, cs(22) + 0.3)]
    for x, lab, val, v, col, t0 in bars:
        u = eout((t - t0) / 0.7)
        if u <= 0: continue
        h = hmax * v / 60 * u
        d.rounded_rectangle((x - 120 + 8, base - h + 10, x + 120 + 8, base + 10), 26, fill=(20, 33, 91, 60))
        d.rounded_rectangle((x - 120, base - h, x + 120, base), 26, fill=col, outline=NAVY, width=5)
        if u > 0.9:
            text_c(d, (x, base - h + 50), val, fit("pb", 46, val, 220), NAVY if col == YEL else WHITE)
        text_c(d, (x, base + 40), lab, fit("pb", 36, lab, 280), NAVY)
    if t >= cs(22) - 0.1:
        d.line([(170, base), (910, base)], fill=NAVY, width=6)
    q = pop(t, cs(23) + 0.1)
    if q > 0:
        paste_c(img, stamp("2× LIPAT!", col=RED, size=58), 560, 820 + 0, q, -7, tag="stempel 2x")


def scene5(img, t):
    """kamu nombok Rp30.000. Kecil? Tunggu dulu."""
    p = pop(t, SC[5] + 0.05)
    if p > 0:
        T, td = card(800, 360, fill=RED)
        text_c(td, (400, 76), "KAMU NOMBOK", F("pb", 56), WHITE)
        u = eout((t - cs(25)) / 0.8) if t >= cs(25) - 0.05 else 0
        text_c(td, (400, 210), "+" + rp(int(round(30000 * u / 1000) * 1000)), F("pb", 116), WHITE)
        text_c(td, (400, 310), "Rp60.000 − Rp30.000", F("pm", 36), (255, 226, 220))
        paste_c(img, T, W / 2, 680, p, 1.0 * math.sin(t * 3), tag="kartu nombok")
    draw_aru(img, 300, 1460, 420, t)
    p = pop(t, cs(26))
    if p > 0 and t < cs(27) - 0.05:
        paste_c(img, bubble("Kecil, kan?", size=50), 680, 1080, p, tag="bubble kecil")
    p = pop(t, cs(27) - 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Tunggu dulu…", "⏳", fill=YEL, fg=NAVY, size=54), 680, 1110, p, 3, tag="pill tunggu")


def scene6(img, t):
    """seminggu sekali nongkrong -> sebulan Rp120.000."""
    p = pop(t, SC[6] + 0.05)
    if p > 0:
        T, td = head_card(800, 640, "NOMBOK TIAP NONGKRONG", col=NAVY, size=42)
        t0 = cs(29) - 0.1; t1 = cs(30) + 0.2
        n = int(4 * clamp((t - t0) / (t1 - t0)) + 0.999) if t >= t0 else 0
        for k in range(4):
            y = 150 + k * 100
            lit = k < n
            td.rounded_rectangle((40, y, 760, y + 80), 20, fill=(253, 228, 222) if lit else LIGHT,
                                 outline=RED if lit else (205, 210, 222), width=4)
            td.text((70, y + 40), f"Minggu {k + 1}", font=F("pb", 38), fill=NAVY if lit else GREY_T, anchor="lm")
            if lit:
                td.text((730, y + 40), "+Rp30.000", font=F("pb", 42), fill=RED, anchor="rm")
        if t >= cs(31) - 0.05:
            u = eout((t - cs(31)) / 0.8)
            td.rounded_rectangle((30, 560, 770, 630), 22, fill=YEL)
            td.text((60, 595), "SEBULAN", font=F("pb", 40), fill=NAVY, anchor="lm")
            td.text((740, 595), rp(int(round(120000 * u / 1000) * 1000)), font=F("pb", 50), fill=NAVY, anchor="rm")
        paste_c(img, T, W / 2, 860, p, tag="kartu sebulan")


def scene7(img, t):
    """PUNCAK: setahun Rp1.560.000 (52 x Rp30.000) + ajakan kirim (overlay SHARE)."""
    p = pop(t, SC[7] + 0.05)
    if p > 0:
        T, td = card(800, 440, fill=WHITE, outline=RED, ow=8)
        text_c(td, (400, 70), "SETAHUN KAMU NOMBOK", F("pb", 48), RED)
        u = eio((t - cs(33)) / 1.6) if t >= cs(33) - 0.05 else 0
        v = 120000 + (1560000 - 120000) * u
        td.rounded_rectangle((40, 130, 760, 300), 30, fill=RED)
        text_c(td, (400, 215), rp(int(round(v / 1000) * 1000)), F("pb", 112), WHITE)
        text_c(td, (400, 370), "52 minggu × Rp30.000", F("pm", 42), GREY_T)
        paste_c(img, T, W / 2, 720, p * (1 + 0.02 * math.sin(t * 8)), -1.5, tag="kartu setahun")
    if t >= cs(33) + 1.3:
        paste_c(img, stamp("Rp1,56 JUTA!", col=NAVY, size=56), 700, 1030, pop(t, cs(33) + 1.3), 6, tag="stempel juta")


def share_card(img, t):
    """ajakan kirim di puncak angka (PRB-55 poin 3), 2 baris, teal."""
    if not (SHARE[0] <= t < SHARE[1]): return
    a = min(clamp((t - SHARE[0]) / 0.25), clamp((SHARE[1] - t) / 0.25))
    s = 0.85 + 0.15 * back((t - SHARE[0]) / 0.35)
    T, td = card(800, 190, fill=TEAL)
    e = emoji_img("📤", 70)
    text_c(td, (360, 62), "Kirim ke teman yang selalu", F("pb", 44), WHITE)
    text_c(td, (360, 128), "pesan paling mahal", F("pb", 50), YEL)
    T.alpha_composite(e, (690, 58))
    paste_c(img, T, W / 2, 1330 + 4 * math.sin(t * 5), s, 0, a, tag="kartu kirim")


SPLIT_Y = 470
ARGS_L = [("Hitung per orang", "di kasir itu RIBET", "🧾", 22),
          ("Minggu depan, bisa jadi", "KAMU yang paling mahal", "🔁", 23),
          ("Nongkrong soal TEMAN,", "bukan kalkulator", "🤝", 24)]


def split(img, t, k):
    """layar terbelah: kiri tim BAGI RATA, kanan tim BAYAR MASING-MASING; sisi aktif terang."""
    right = k == 11
    d = ImageDraw.Draw(img)
    cols = [(140, 530, TEAL, "BAGI RATA"), (550, 940, RED, "MASING-MASING")]
    for j, (x0, x1, col, lab) in enumerate(cols):
        act = (j == 1) == right
        fill = (255, 255, 255) if act else (232, 235, 242)
        d.rounded_rectangle((x0, SPLIT_Y, x1, 1470), 30, fill=fill, outline=col if act else (200, 205, 216), width=6)
        d.rounded_rectangle((x0, SPLIT_Y, x1, SPLIT_Y + 120), 30, fill=col if act else (190, 196, 210))
        d.rectangle((x0, SPLIT_Y + 70, x1, SPLIT_Y + 120), fill=col if act else (190, 196, 210))
        text_c(d, ((x0 + x1) / 2, SPLIT_Y + 34), "TIM", F("pb", 30), WHITE)
        text_c(d, ((x0 + x1) / 2, SPLIT_Y + 82), lab, fit("pb", 44, lab, x1 - x0 - 30), WHITE)
        track("kolom " + lab, x1 - x0, x0, x1)
    d.ellipse((540 - 42, SPLIT_Y + 170 - 42, 540 + 42, SPLIT_Y + 170 + 42), fill=YEL, outline=NAVY, width=5)
    text_c(d, (540, SPLIT_Y + 168), "vs", F("pb", 38), NAVY)
    # argumen tim bagi rata (menumpuk)
    nL = {8: 1, 9: 2, 10: 3}.get(k, 3)
    for i in range(nL):
        a1, a2, em, seg_chunk = ARGS_L[i]
        t0 = SC[8 + i] + 0.1
        p = pop(t, t0) if k == 8 + i else 1.0
        if p <= 0: continue
        y = SPLIT_Y + 250 + i * 290
        C = Image.new("RGBA", (360, 270), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
        act = not right
        cd.rounded_rectangle((0, 0, 360, 260), 24, fill=(232, 250, 246) if act else (240, 242, 246),
                             outline=TEAL if act else (200, 205, 216), width=4)
        C.alpha_composite(emoji_img(em, 80), (140, 18))
        text_c(cd, (180, 150), a1, fit("pb", 30, a1, 330), NAVY if act else GREY_T)
        text_c(cd, (180, 200), a2, fit("pb", 30, a2, 330), TEAL if act else GREY_T)
        C.info["nw"] = 360
        paste_c(img, C, 335, y, p, tag="argumen kiri")
    if k == 10 and t >= cs(43) - 0.1:   # kalkulator dicoret
        q = pop(t, cs(43) - 0.1)
        C = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
        C.alpha_composite(emoji_img("🧮", 200), (50, 50))
        cd.line([(40, 40), (260, 260)], fill=RED, width=22)
        cd.ellipse((20, 20, 280, 280), outline=RED, width=18)
        paste_c(img, C, 745, 900, 0.9 * q, tag="kalkulator coret")
    if k < 11:
        if k != 10:
            text_c(d, (745, 1000), "?", F("pb", 160), (200, 205, 216))
        return
    # tim bayar masing-masing membalas
    p = pop(t, SC[11] + 0.1)
    C = Image.new("RGBA", (360, 600), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
    cd.rounded_rectangle((0, 0, 360, 590), 24, fill=(253, 236, 232), outline=RED, width=5)
    C.alpha_composite(emoji_img("🙅", 110), (125, 26))
    for j, (s_, col) in enumerate((("Teman yang", NAVY), ("BAIK nggak", RED), ("bikin temannya", NAVY), ("NOMBOK", RED))):
        if t >= cs(46) - 0.1 + 0.25 * j or j < 2 and t >= cs(44):
            text_c(cd, (180, 210 + j * 62), s_, fit("pb", 40, s_, 330), col)
    if t >= cs(48) - 0.05:
        cd.rounded_rectangle((30, 470, 330, 560), 22, fill=RED)
        text_c(cd, (180, 515), "−Rp30.000", F("pb", 46), WHITE)
    C.info["nw"] = 360
    paste_c(img, C, 745, SPLIT_Y + 470, p, tag="argumen kanan")


def scene8(img, t): split(img, t, 8)
def scene9(img, t): split(img, t, 9)
def scene10(img, t): split(img, t, 10)
def scene11(img, t): split(img, t, 11)


def scene12(img, t):
    """jalan tengah: camilan bareng dibagi rata, makanan & minuman bayar masing-masing."""
    p = pop(t, SC[12] + 0.05)
    if p > 0:
        paste_c(img, pill("JALAN TENGAH", fill=YEL, fg=NAVY, size=60), W / 2, 500, p, -2, tag="pill jalan tengah")
    rows = [("🍟", "Camilan bareng", "BAGI RATA", TEAL, cs(50) - 0.1, 760),
            ("🍛", "Makanan & minuman", "MASING-MASING", RED, cs(52) - 0.1, 1110)]
    for em, a_, b_, col, t0, y in rows:
        q = pop(t, t0)
        if q <= 0: continue
        T, td = card(800, 290, fill=WHITE, outline=col, ow=7)
        T.alpha_composite(emoji_img(em, 130), (40, 30))
        td.text((210, 95), a_, font=fit("pb", 52, a_, 560), fill=NAVY, anchor="lm")
        td.rounded_rectangle((40, 180, 760, 260), 40, fill=col)
        text_c(td, (400, 221), b_, F("pb", 54), WHITE)
        paste_c(img, T, W / 2, y, q, tag="kartu " + b_)


def scene13(img, t):
    """sepakati sebelum pesan; nasi goreng bayar harga nasi goreng."""
    p = pop(t, SC[13] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Sepakati SEBELUM pesan", "🤝", fill=NAVY, fg=WHITE, size=48), W / 2, 500, p, -2,
                tag="pill sepakati")
    q = pop(t, SC[13] + 0.3)
    if q > 0:
        T, td = card(800, 520, fill=WHITE, outline=GREEN, ow=7)
        T.alpha_composite(plate_img(330), (40, 120))
        text_c(td, (400, 64), "NASI GORENG BAYAR…", F("pb", 46), NAVY)
        td.text((420, 210), "harga", font=F("pm", 44), fill=GREY_T, anchor="lm")
        td.text((420, 270), "nasi goreng", font=F("pb", 50), fill=NAVY, anchor="lm")
        if t >= cs(56) - 0.05:
            td.rounded_rectangle((400, 340, 770, 460), 26, fill=GREEN)
            text_c(td, (585, 400), "Rp30.000", F("pb", 66), WHITE)
        paste_c(img, T, W / 2, 900, q, tag="kartu harga nasi goreng")
    draw_aru(img, 290, 1470, 300, t)
    if t >= cs(56):
        r = pop(t, cs(56) + 0.2)
        if r > 0:
            icon_check(ImageDraw.Draw(img), 760, 1300, 1.3 * min(1.0, r))


KOMEN = None
def komen_crop():
    global KOMEN
    if KOMEN is None:
        im = Image.open(MEDIA + "/komentar/2026-11-14_mlh7_knarkha.png").convert("RGBA")
        im = im.crop((0, 1236, 1060, 1424))      # baris komentar @knarkha (#7)
        KOMEN = scaled(im, 740)
    return KOMEN


def scene14(img, t):
    """penutup: tim RATA atau tim MASING-MASING? Komen! + terima kasih @knarkha (#7)."""
    for k, (s, col, t0) in enumerate((("TIM RATA", TEAL, SC[14] + 0.05), ("TIM MASING-MASING", RED, cs(58)))):
        p = pop(t, t0)
        if p <= 0: continue
        beat = 1 + 0.04 * math.sin((t - t0) * 7 + k * math.pi)
        paste_c(img, pill(s, fill=col, fg=WHITE, size=54, h=116), W / 2, 520 if k == 0 else 720, p * beat,
                -2 if k == 0 else 2, tag=s)
    if t >= cs(58):
        text_c(ImageDraw.Draw(img), (W / 2, 620), "atau", F("pb", 40), NAVY)
    p = pop(t, cs(58) + 0.4)
    if p > 0:
        B = Image.new("RGBA", (800, 250), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 800, 200), 34, fill=YEL, outline=NAVY, width=5)
        bd.polygon([(110, 196), (180, 196), (90, 246)], fill=YEL, outline=NAVY)
        bd.line([(112, 197), (178, 197)], fill=YEL, width=8)
        text_c(bd, (400, 66), "Tim RATA atau tim MASING-MASING?", fit("pb", 44, "Tim RATA atau tim MASING-MASING?", 740), NAVY)
        text_c(bd, (400, 140), "Komen!", F("pb", 60), NAVY)
        B.info["nw"] = 800
        paste_c(img, B, W / 2, 940, p, tag="bubble komen")
    p = pop(t, SC[14] + 0.3)
    if p > 0:
        K = komen_crop()
        T, td = card(800, K.height + 110, fill=WHITE, outline=(200, 205, 216), ow=4)
        td.text((40, 50), "Makasih @knarkha (#7):", font=F("pb", 36), fill=TEAL, anchor="lm")
        T.alpha_composite(K, (30, 92))
        paste_c(img, T, W / 2, 1290, p, tag="kartu knarkha")


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10, scene11,
          scene12, scene13, scene14]


def draw_notes(img, k):
    lines = NOTES.get(k)
    if not lines: return
    d = ImageDraw.Draw(img)
    for j, s in enumerate(lines):
        f = fit("pm", 28, s, MAXW)
        track("catatan", f.getlength(s), W / 2 - f.getlength(s) / 2, W / 2 + f.getlength(s) / 2)
        d.text((W / 2, 1712 + j * 40), s, font=f, fill=GREY_T, anchor="mm")


FOLLOW_S = "follow @kabar.arunika · tiap hari 1 hitungan uang"


def follow_pill():
    f = fit("pb", 30, FOLLOW_S, MAXW - 60); tw = f.getlength(FOLLOW_S)
    pl = Image.new("RGBA", (int(tw) + 60, 60), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
    pd.rounded_rectangle((0, 0, tw + 60, 60), 30, fill=TEAL)
    pd.text((30, 30), FOLLOW_S, font=f, fill=WHITE, anchor="lm")
    assert pl.width <= MAXW, pl.width
    return pl


def frame(t):
    BOXES.clear()
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
        Hd, hx0, hx1 = header()
        img.alpha_composite(Hd, (0, 240))  # header y≈300 (PRB-41); bukan di dtk 0-3
        track("header", hx1 - hx0, hx0, hx1)
    else:
        scene0(img, t)
        if t >= CT0:
            a = clamp((t - CT0) / 0.3)
            L = Image.new("RGBA", (W, 60), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
            s_ = NOTES[0][0]; f = fit("pm", 28, s_, MAXW)
            ld.text((W / 2, 30), s_, font=f, fill=INK, anchor="mm")
            track("catatan", f.getlength(s_), W / 2 - f.getlength(s_) / 2, W / 2 + f.getlength(s_) / 2)
            paste_c(img, L, W / 2, 1712, 1, 0, a)
    share_card(img, t)
    draw_sub(img, t)
    if k > 0:
        draw_notes(img, k)
    if FOLLOW[0] <= t < FOLLOW[1]:
        a = min(clamp((t - FOLLOW[0]) / 0.25), clamp((FOLLOW[1] - t) / 0.25))
        paste_c(img, follow_pill(), W / 2, 1490, 1, 0, a, tag="pill follow")
    la = clamp((t - (TOTAL - 1.5)) / 0.3)
    if la > 0:
        paste_c(img, logo_w(300), W / 2, 1730, 0.9 + 0.1 * back(la), 0, la, tag="logo")
    if t >= PB_START:
        ImageDraw.Draw(img).rectangle((0, H - 14, int(W * (t - PB_START) / (TOTAL - PB_START)), H), fill=YEL)
    return img.convert("RGB")


def check(step=0.1):
    """pindai semua frame: elemen > 800 px atau keluar dari x 130..950 (PRB-41)."""
    bad = {}; widest = {}
    n = int(TOTAL / step)
    for j in range(n + 1):
        t = min(TOTAL - 0.01, j * step)
        frame(t)
        for tag, nw, x0, x1 in BOXES:
            widest[tag] = max(widest.get(tag, 0), nw)
            if (tag not in ("aru", "bocor", "dia") and nw > MAXW + 0.5) or x0 < XMIN - 0.5 or x1 > XMAX + 0.5:
                bad.setdefault(tag, []).append((round(t, 1), round(nw), round(x0), round(x1)))
    for tag in sorted(widest, key=lambda k: -widest[k]):
        print(f"{tag:22s} lebar maks {widest[tag]:6.0f}")
    if bad:
        for tag, v in bad.items():
            print("PELANGGARAN", tag, len(v), v[:4])
        sys.exit(1)
    print("OK: semua elemen <= 800 px dan di dalam x 130..950")


def events():
    ev = [{"t": SC[k], "sfx": "whoosh", "gain": 0.30} for k in range(1, NS)]
    ev.append({"t": 0.05, "sfx": "cring", "gain": 0.35})        # koin jatuh frame 0
    ev.append({"t": CT0, "sfx": "pop", "gain": 0.3})            # counter mulai naik
    ev.append({"t": CT1, "sfx": "ding", "gain": 0.25})
    for i in (3, 8, 10, 12, 13, 14, 16, 18, 21, 22, 23, 26, 27, 31, 43, 46, 48, 50, 52, 55, 56, 58):
        ev.append({"t": cs(i), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": cs(25), "sfx": "cring", "gain": 0.4})       # kamu nombok
    ev.append({"t": cs(33), "sfx": "cring", "gain": 0.45})      # counter setahun
    ev.append({"t": cs(33) + 1.6, "sfx": "ding", "gain": 0.35})  # Rp1.560.000 (puncak)
    ev.append({"t": SHARE[0] + 0.2, "sfx": "klik", "gain": 0.3})
    json.dump(sorted(ev, key=lambda e: e["t"]), open("events.json", "w"), indent=1)
    print(len(ev), "events")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "events":
        events()
    elif cmd == "check":
        check()
    elif cmd == "scenes":
        for k in range(NS):
            print(k, round(SC[k], 2), round(SC[k + 1], 2), round(SC[k + 1] - SC[k], 2))
    elif cmd == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        ims = []
        for tt in ts:
            im = frame(tt); im.save(f"still_{tt:.2f}.png"); ims.append(im.resize((360, 640)))
        cols = 6; rows = math.ceil(len(ims) / cols)
        sh = Image.new("RGB", (360 * cols, 640 * rows), WHITE)
        for j, im in enumerate(ims):
            sh.paste(im, ((j % cols) * 360, (j // cols) * 640))
        sh.save(os.environ.get("SHEET", "sheet.png")); print("sheet")
    elif cmd == "video":
        out, a, b = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                              "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        n0, n1 = round(a * FPS), round(b * FPS)
        for n in range(n0, n1):
            p.stdin.write(frame(n / FPS).tobytes())
        p.stdin.close(); p.wait(); print(out, n1 - n0, "frames")

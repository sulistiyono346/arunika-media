"""Renderer ARN-57 "Kok suaramu di rekaman terdengar aneh?" -- Flat 2D latar terang (#F2F4F7).
Adaptasi render_flat_ngantuk.py (helper kartu, pill, bubble, Aru, subtitle, cek area aman, sfx):
- frame 0 (PRB-34/36/46): HP raksasa memutar voice note, Aru meringis, Si Bocor menekan play; angka besar "2" (jalur suara)
  turun jadi "1" di dtk ~2; visual berganti (zoom ke wajah Aru) di dtk ~1,5. Judul layar = pill kecil
  "Suaramu, kok BEDA di rekaman?" (BEDA kuning); tanpa logo / label seri / progress bar di dtk 0-3.
- 12 adegan + penutup 1,5 dtk (tiap adegan <= 6 dtk); sumber di layar (PRB-39); follow dtk 10,6-15 (PRB-4);
  ajakan kirim di puncak A6 dtk ~27,5-31 (PRB-55); pertanyaan dua kubu di akhir.
- area aman (PRB-41): semua pill/bubble/kartu <= 800 px dan di x 130..950; `check` memindai tiap 0,1 dtk.
Pemakaian (dari sore/build/suara, setelah align_suara.py -> timing.json):
  TOTAL=53.3 python3 ../../render_flat_suara.py events | check | scenes | stills 0,2,... | video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, NAVY, TEAL, YEL, WHITE, GREY_T, RED)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "53.3"))
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
GREEN = (46, 160, 110); INK = (60, 66, 92); LIGHT = (232, 238, 246); SKIN = (254, 211, 176)
WOOD = (214, 168, 120); WOOD_D = (176, 128, 84)
MAXW, XMIN, XMAX = 800, 130, 950   # PRB-41

TIM = json.load(open("timing.json"))
def cs(i): return TIM[i]["start"] + LEAD
def ce(i): return TIM[i]["end"] + LEAD
def seg0(s):   # chunk pertama segmen s
    return next(i for i, c in enumerate(TIM) if c["seg"] == s)
def chunk_of(text):
    return next(i for i, c in enumerate(TIM) if c["text"] == text)

SCENE_SEG = [0, 2, 6, 10, 13, 15, 16, 19, 21, 23, 26, 28]
SCENE_OFF = {4: 0.5}
SC = [0.0] + [cs(seg0(s)) - SCENE_OFF.get(k, 0.25) for k, s in enumerate(SCENE_SEG) if k > 0] + [TOTAL - 1.5, TOTAL]
NS = len(SCENE_SEG) + 1        # 12 adegan + penutup
FOLLOW = (10.6, 15.0)          # PRB-4: ajakan follow teks kecil dtk 10-15
PB_START = 3.5
SA = "Scientific American · Timothy E. Hullar, Washington Univ."
NOTES = {3: (SA,), 4: (SA,), 5: (SA,),
         6: ("Scientific American · Discover Magazine, 29 Mei 2021",),
         8: ("Hughes & Harrison, jurnal Perception, 2013", "ScienceDaily, 12 Sep 2013"),
         9: ("Hughes & Harrison, Perception, 2013",)}
ZOOM_T = 1.45                  # visual berganti dtk ~1,5 (zoom ke wajah Aru)
FLIP = 2.0                     # "2" -> "1" (counter bergerak dtk ~2, PRB-29/46)
SHARE = (cs(seg0(17)) - 0.3, SC[7] - 0.2)   # ajakan kirim di puncak A6 (dtk ~27,5-30,7)


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
BOXES = []
def track(tag, nw, x0, x1):
    BOXES.append((tag, nw, x0, x1))


# ---------- aset ----------
def trim(im): return im.crop(im.getbbox())
ARU_RAW = Image.open(MEDIA + "/maskot/aru-syal-bendera.png").convert("RGBA")
ARU_BOX = ARU_RAW.getbbox()
LOGO = trim(Image.open(MEDIA + "/brand/arunika-logo.png").convert("RGBA"))


@lru_cache(None)
def aru_face(kind):
    """kind: normal | wince (meringis) | shock (kaget, mulut O)."""
    im = ARU_RAW.copy()
    if kind != "normal":
        d = ImageDraw.Draw(im)
        for x0 in (330, 486):
            d.ellipse((x0, 360, x0 + 84, 456), fill=SKIN)
        d.line([(320, 318), (417, 342)], fill=SKIN, width=30); d.line([(483, 342), (578, 318)], fill=SKIN, width=30)
        d.rectangle((384, 500, 516, 560), fill=SKIN)
        if kind == "wince":
            d.line([(326, 346), (414, 322)], fill=NAVY, width=14); d.line([(486, 322), (574, 346)], fill=NAVY, width=14)
            d.line([(338, 378), (398, 408), (338, 438)], fill=NAVY, width=13, joint="curve")
            d.line([(562, 378), (502, 408), (562, 438)], fill=NAVY, width=13, joint="curve")
            d.line([(396, 540), (422, 516), (448, 540), (474, 516), (502, 540)], fill=NAVY, width=11, joint="curve")
        else:
            d.line([(326, 322), (414, 306)], fill=NAVY, width=14); d.line([(486, 306), (574, 322)], fill=NAVY, width=14)
            for cx in (372, 528):
                d.ellipse((cx - 34, 366, cx + 34, 450), fill=WHITE, outline=NAVY, width=8)
                d.ellipse((cx - 10, 396, cx + 10, 424), fill=NAVY)
            d.ellipse((418, 498, 482, 580), fill=(120, 40, 50), outline=NAVY, width=10)
    return im.crop(ARU_BOX)


def aru_xy(rx, ry, cx, bottom, h):
    """titik (rx, ry) pada gambar Aru mentah -> koordinat layar bila Aru digambar draw_aru(cx, bottom, h) tanpa bob."""
    r = h / (ARU_BOX[3] - ARU_BOX[1])
    return cx + (rx - ARU_BOX[0] - (ARU_BOX[2] - ARU_BOX[0]) / 2) * r, bottom - h + (ry - ARU_BOX[1]) * r


@lru_cache(None)
def aru_h(h, kind="normal"):
    A = aru_face(kind); r = h / A.height
    return A.resize((int(A.width * r), h), Image.LANCZOS)


@lru_cache(None)
def logo_w(w):
    r = w / LOGO.width
    return LOGO.resize((w, int(LOGO.height * r)), Image.LANCZOS)


def paste_c(dst, im, cx, cy, scale=1.0, angle=0.0, alpha=1.0, tag=None):
    if scale <= 0.01 or alpha <= 0.01: return
    nw = im.info.get("nw", im.width)
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


def draw_aru(layer, cx, bottom, h, t, kind="normal", angle_amp=2.0, extra=0.0, bob=7):
    im = aru_h(h, kind)
    b = bob * math.sin(2 * math.pi * 1.1 * t)
    ang = angle_amp * math.sin(2 * math.pi * 0.7 * t) + extra
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
    B.info["nw"] = w
    return B


def stamp(text, col=RED, size=70):
    f = F("pb", size); w = int(f.getlength(text) + 80)
    assert w <= MAXW, ("stamp", text, w)
    S = Image.new("RGBA", (w, size + 70), (0, 0, 0, 0)); sd = ImageDraw.Draw(S)
    sd.rounded_rectangle((6, 6, w - 6, size + 64), 18, fill=(255, 255, 255, 215), outline=col, width=10)
    text_c(sd, (w / 2, (size + 70) / 2), text, f, col)
    S.info["nw"] = w
    return S


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


# ---------- latar ----------
BG = (242, 244, 247)
@lru_cache(None)
def base_bg():
    img = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(img)
    top, bot = BG, (248, 245, 240)
    for y in range(H):
        u = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[j] + (bot[j] - top[j]) * u) for j in range(3)))
    return img


DESK_Y = 1300
@lru_cache(None)
def bg_office():
    """frame 0: dinding kantor terang + meja kayu di depan."""
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.rectangle((0, 1180, W, DESK_Y), fill=(230, 234, 241))                      # lis dinding
    for x in (40, 960):                                                          # jendela samping (dekor)
        d.rounded_rectangle((x - 80, 760, x + 80, 1080), 16, fill=(222, 236, 248), outline=(200, 208, 222), width=6)
    return img


@lru_cache(None)
def desk_layer():
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((0, DESK_Y, W, DESK_Y + 46), fill=WOOD, outline=NAVY, width=5)
    d.rectangle((0, DESK_Y + 46, W, H), fill=WOOD_D)
    d.line([(0, DESK_Y + 46), (W, DESK_Y + 46)], fill=NAVY, width=5)
    return L


@lru_cache(None)
def bg_rest():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((90, 480, 990, 1380), fill=(255, 246, 232))
    d.rectangle((0, 1490, W, H), fill=(226, 230, 237))
    return img


@lru_cache(None)
def header():
    """pill kecil judul layar (kolom Judul layar), y≈300 (PRB-41); BEDA disorot kuning."""
    f = F("pb", 38); s1 = "Suaramu, kok "; s2 = "BEDA"; s3 = " di rekaman?"
    w1, w2, w3 = f.getlength(s1), f.getlength(s2), f.getlength(s3)
    padx, kp = 30, 14
    tot = w1 + w2 + 2 * kp + w3 + 2 * padx + 6
    assert tot <= MAXW, tot
    L = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    x0 = (W - tot) / 2
    d.rounded_rectangle((x0 + 6, 36, x0 + tot + 6, 104), 34, fill=(20, 33, 91, 50))
    d.rounded_rectangle((x0, 30, x0 + tot, 98), 34, fill=NAVY)
    x = x0 + padx
    d.text((x, 65), s1, font=f, fill=WHITE, anchor="lm"); x += w1
    d.rounded_rectangle((x, 38, x + w2 + 2 * kp, 92), 14, fill=YEL)
    d.text((x + kp, 66), s2, font=f, fill=NAVY, anchor="lm"); x += w2 + 2 * kp + 3
    d.text((x, 65), s3, font=f, fill=WHITE, anchor="lm")
    return L, x0, x0 + tot


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


# ---------- ikon & tokoh ----------
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



# ---------- Si Bocor (dari tools/render_polaroid.py) ----------
@lru_cache(None)
def bocor_img(mode="normal"):
    im = Image.new("RGBA", (300, 270), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line([(60, 200), (30, 185), (12, 150), (22, 125)], fill=(244, 163, 184), width=7, joint="curve")
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
    if mode == "giggle":                                   # cekikikan: mulut terbuka lebar, pipi merona
        d.chord((88, 108, 142, 148), 0, 180, fill=(120, 40, 50), outline=NAVY, width=4)
        d.ellipse((66, 104, 88, 120), fill=(244, 163, 184)); d.ellipse((142, 104, 164, 120), fill=(244, 163, 184))
    elif mode == "cover":                                  # menutup mulut menahan tawa
        d.ellipse((84, 100, 146, 146), fill=(244, 163, 184), outline=NAVY, width=5)
    else:
        d.arc((92, 104, 140, 134), 20, 150, fill=NAVY, width=4)
    im.info["nw"] = 300
    return im


def bocor_h(h, mode="normal"):
    b = bocor_img(mode); r = h / b.height
    o = b.resize((int(b.width * r), h), Image.LANCZOS); o.info["nw"] = o.width
    return o


# ---------- elemen gambar ----------
def sine_wave(d, x0, x1, cy, amp, cycles, phase, col, width=10, n=120):
    pts = [(x0 + (x1 - x0) * k / n, cy + amp * math.sin(2 * math.pi * cycles * k / n + phase)) for k in range(n + 1)]
    d.line(pts, fill=col, width=width, joint="curve")


def bars(d, x0, x1, cy, hmax, t, n=18, col=TEAL, speed=7.0, w=None):
    step = (x1 - x0) / n; w = w or step * 0.55
    for k in range(n):
        v = 0.25 + 0.75 * abs(math.sin(t * speed + k * 0.9) * math.cos(t * speed * 0.37 + k * 0.4))
        x = x0 + step * (k + 0.5)
        d.rounded_rectangle((x - w / 2, cy - hmax * v / 2, x + w / 2, cy + hmax * v / 2), int(w / 2), fill=col)


def play_btn(d, cx, cy, r, col=YEL, tri=NAVY):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col, outline=NAVY, width=6)
    d.polygon([(cx - r * 0.3, cy - r * 0.45), (cx - r * 0.3, cy + r * 0.45), (cx + r * 0.5, cy)], fill=tri)


def phone(w, h, t, playing=True, label_big=None):
    """HP tegak (kartu) dengan gelembung voice note berisi gelombang."""
    P, pd = card(w, h, fill=WHITE, r=60, outline=NAVY, ow=9)
    pd.rounded_rectangle((26, 26, w - 26, h - 26), 38, fill=(230, 238, 248))
    pd.rounded_rectangle((w / 2 - 50, 36, w / 2 + 50, 54), 9, fill=NAVY)
    return P, pd


def star(d, cx, cy, r, fill, outline=NAVY):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5; rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline, width=4)


@lru_cache(None)
def silhouette(h):
    im = Image.new("RGBA", (120, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 80, 110, 170), 40, fill=(120, 128, 156), outline=NAVY, width=5)
    d.ellipse((30, 8, 90, 78), fill=(150, 158, 184), outline=NAVY, width=5)
    r = h / 170
    o = im.resize((int(120 * r), h), Image.LANCZOS); o.info["nw"] = o.width
    return o


def path_arrow(d, pts, col, g, w=16, head=34, outline=None):
    """polyline dengan kepala panah, digambar sebagian sesuai progres g (0..1)."""
    if g <= 0: return
    segs = list(zip(pts, pts[1:])); lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs]
    tot = sum(lens); goal = tot * clamp(g); out = [pts[0]]; acc = 0
    for (a, b), L in zip(segs, lens):
        if acc + L <= goal: out.append(b); acc += L
        else:
            u = (goal - acc) / L; out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)); break
    if len(out) < 2: return
    if outline:
        d.line(out, fill=outline, width=w + 10, joint="curve")
    d.line(out, fill=col, width=w, joint="curve")
    if g >= 0.98:
        (x0, y0), (x1, y1) = out[-2], out[-1]
        ang = math.atan2(y1 - y0, x1 - x0)
        hx, hy = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
        p = [(x1, y1), (hx + head * 0.6 * math.sin(ang), hy - head * 0.6 * math.cos(ang)),
             (hx - head * 0.6 * math.sin(ang), hy + head * 0.6 * math.cos(ang))]
        d.polygon(p, fill=col, outline=outline)


# posisi Aru pada adegan kepala (adegan 3-5)
HA = dict(cx=540, bottom=1480, h=800)
def AP(rx, ry): return aru_xy(rx, ry, HA["cx"], HA["bottom"], HA["h"])


def head_paths(img, t, air_g, bone_g, bone_w=20, air_a=1.0):
    """jalur udara (toska, mulut -> telinga di luar kepala) dan jalur tulang (kuning, rahang -> telinga)."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    LA = Image.new("RGBA", (W, H), (0, 0, 0, 0)); da = ImageDraw.Draw(LA)
    mx, my = AP(450, 535); el = AP(200, 425); er = AP(700, 425)
    for sgn, (ex, ey) in ((-1, el), (1, er)):
        pts = [(mx + sgn * 50, my + 22), (mx + sgn * 150, my + 16), (mx + sgn * 212, my - 28), (ex + sgn * 2, ey + 6)]
        path_arrow(da, pts, TEAL, air_g, w=20, head=38, outline=NAVY)
    for sgn, (ex, ey) in ((-1, el), (1, er)):
        pts = [(mx + sgn * 8, my - 222), (mx + sgn * 86, my - 212), (mx + sgn * 156, my - 166), (ex - sgn * 26, ey - 14)]
        path_arrow(d, pts, YEL, bone_g, w=bone_w, head=36, outline=NAVY)
    if air_a < 0.999:
        LA.putalpha(LA.getchannel("A").point(lambda v: int(v * air_a)))
    img.alpha_composite(LA); img.alpha_composite(L)


# ---------- latar ----------
@lru_cache(None)
def bg_rest():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((90, 480, 990, 1380), fill=(255, 246, 232))
    d.rectangle((0, 1490, W, H), fill=(226, 230, 237))
    return img


# ---------- adegan ----------
def scene0(img, t):
    """frame 0: Aru meringis, HP raksasa memutar voice note, Si Bocor menekan play; badge '2' -> '1'; zoom dtk ~1,5."""
    base = bg_rest().copy()
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ax, ab, ah = 340, 1500, 640
    kind = "wince" if t >= 0.35 else "normal"
    draw_aru(L, ax, ab, ah, t, kind=kind, angle_amp=2.5 if t < ZOOM_T else 1.0, bob=5)
    # HP raksasa (di depan tangan Aru)
    P, pd = phone(430, 800, t)
    play_press = clamp((t - 0.3) / 0.12) * clamp(1 - (t - 0.5) / 0.15)
    bw = 340
    pd.rounded_rectangle((45, 150, 45 + bw, 330), 36, fill=NAVY)
    bars(pd, 105, 45 + bw - 30, 240, 100, t, n=12, col=TEAL if t < 0.3 else YEL, speed=9)
    pd.text((215, 372), "0:07", font=F("pm", 42), fill=GREY_T, anchor="mm")
    pr = 105 - 12 * play_press
    play_btn(pd, 215, 560, pr)
    if t >= 0.3:
        for k in range(2):
            u = ((t - 0.3) * 1.6 + k * 0.5) % 1.0
            rr = pr + 70 * u
            pd.ellipse((215 - rr, 560 - rr, 215 + rr, 560 + rr), outline=(255, 184, 0, int(200 * (1 - u))), width=6)
    pd.text((215, 700), "voice note", font=F("pm", 40), fill=NAVY, anchor="mm")
    paste_c(L, P, 735, 1010, 1.0, -2 + 1.5 * math.sin(t * 5), tag="HP raksasa")
    # Si Bocor menekan play: melompat-lompat cekikikan di atas HP
    hop = 18 * abs(math.sin(t * 7))
    paste_c(L, bocor_h(190, "giggle"), 830, 560 - hop, 1.0, 6 * math.sin(t * 9), tag="bocor")
    # zoom ke wajah Aru dtk ~1,5
    z = 1 + 0.15 * eio((t - ZOOM_T) / 0.45)
    fx, fy = 400, 1030
    if z > 1.001:
        L = L.resize((int(W * z), int(H * z)), Image.BICUBIC)
        L = L.crop((int(fx * z - fx), int(fy * z - fy), int(fx * z - fx) + W, int(fy * z - fy) + H))
    base.alpha_composite(L)
    img.alpha_composite(base)
    # badge angka besar "2" -> "1" (dtk 2)
    dd = ImageDraw.Draw(img)
    flip = clamp((t - FLIP) / 0.3)
    v = "2" if t < FLIP else "1"
    col = YEL if t < FLIP else RED
    B = Image.new("RGBA", (330, 360), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
    bd.ellipse((14, 20, 324, 330), fill=(20, 33, 91, 55))
    bd.ellipse((0, 0, 310, 310), fill=NAVY, outline=NAVY, width=6)
    sy = 1.0 if t < FLIP else 0.5 + 0.5 * back(flip)
    G = Image.new("RGBA", (310, 310), (0, 0, 0, 0)); gd = ImageDraw.Draw(G)
    text_c(gd, (155, 118), v, F("pb", 230), col)
    text_c(gd, (155, 238), "jalur suara", F("pb", 32), WHITE)
    B.alpha_composite(G.resize((310, max(1, int(310 * sy)))) if sy < 0.999 else G, (0, int(155 * (1 - sy))))
    B.info["nw"] = 310
    shake = 7 * math.sin(t * 45) * clamp(1 - (t - FLIP) / 0.35) if t >= FLIP else 0
    paste_c(img, B, 300 + shake, 640, 1.0, 0, tag="badge angka")
    q = pop(t, ZOOM_T + 0.2)
    if q > 0:
        paste_c(img, bubble("Aduh!", col=WHITE, fg=NAVY, size=56, tail="left"), 700, 720, q, 3, tag="bubble aduh")


def scene1(img, t):
    """Aru menunjuk kepalanya sendiri, tanda tanya besar: Coba TEBAK."""
    p = pop(t, SC[1] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Coba TEBAK", "🤔", fill=YEL, fg=NAVY, size=60), W / 2, 520, p, -2, tag="pill tebak")
    draw_aru(img, 520, 1500, 760, t, angle_amp=1.5)
    d = ImageDraw.Draw(img)
    q = pop(t, SC[1] + 0.3)
    if q > 0:
        hx, hy = aru_xy(450, 300, 520, 1500, 760)
        u = eout((t - SC[1] - 0.3) / 0.4)
        arrow(d, 860, 800 + 20 * math.sin(t * 6), 860 - 120 * u + 0, 800 + 20 * math.sin(t * 6) - 20, YEL, w=20, head=44) if False else None
        paste_c(img, pill("INI KEPALAKU", fill=NAVY, fg=WHITE, size=40), 770, 760, q, 3, tag="pill kepala") if False else None
        # tanda tanya besar di atas kepala
        Q = Image.new("RGBA", (240, 260), (0, 0, 0, 0)); qd = ImageDraw.Draw(Q)
        qd.ellipse((10, 10, 230, 230), fill=YEL, outline=NAVY, width=8)
        text_c(qd, (120, 126), "?", F("pb", 170), NAVY)
        Q.info["nw"] = 220
        paste_c(img, Q, 800, 780 + 8 * math.sin(t * 3), q * (1 + 0.05 * math.sin(t * 8)), 6 * math.sin(t * 2), tag="tanda tanya")
    r = pop(t, cs(seg0(5)) - 0.1)
    if r > 0:
        paste_c(img, bubble("Kenapa beda?", col=NAVY, fg=WHITE, size=52, tail="right"), 560, 650, r, -2, tag="bubble kenapa")


def scene2(img, t):
    """chat grup: voice note terkirim -> dengar ulang -> hapus untuk semua; teman mengangguk."""
    p = pop(t, SC[2] + 0.05)
    if p > 0:
        T, td = head_card(780, 560, "GRUP TEMAN", col=TEAL, size=42)
        t_vn = cs(seg0(6)); t_re = cs(seg0(7)); t_del = cs(seg0(8))
        vn = clamp(1 - (t - t_del - 0.5) / 0.4) if t >= t_del + 0.5 else 1.0
        q = pop(t, t_vn)
        if q > 0 and vn > 0:
            B = Image.new("RGBA", (520, 120), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
            bd.rounded_rectangle((0, 0, 520, 120), 30, fill=NAVY)
            play_btn(bd, 70, 60, 38)
            bars(bd, 130, 400, 60, 70, t, n=14, col=WHITE, speed=8)
            bd.text((470, 60), "0:07", font=F("pm", 32), fill=WHITE, anchor="mm")
            if vn < 0.999: B.putalpha(B.getchannel("A").point(lambda v: int(v * vn)))
            T.alpha_composite(B, (int(230 + 16 * (1 - q) * 20), 150))
        if t >= t_re and t < t_del:
            R = pill_emoji("DENGAR ULANG", "🎧", fill=YEL, fg=NAVY, size=38, padx=26)
            T.alpha_composite(R, (140, 300))
        if t >= t_del - 0.05:
            u = pop(t, t_del - 0.05)
            Bt = Image.new("RGBA", (520, 100), (0, 0, 0, 0)); btd = ImageDraw.Draw(Bt)
            press = clamp(1 - (t - t_del - 0.35) / 0.1) if t > t_del + 0.3 else 1
            btd.rounded_rectangle((0, 0, 520, 100), 28, fill=RED if press > 0.5 else (170, 40, 30), outline=NAVY, width=5)
            text_c(btd, (260, 52), "Hapus untuk semua", F("pb", 42), WHITE)
            T.alpha_composite(Bt.resize((int(520 * min(1, u)), int(100 * min(1, u))), Image.BICUBIC) if u < 1 else Bt, (130, 410))
        T.info["nw"] = 780
        paste_c(img, T, W / 2, 740, p, tag="chat grup")
    # teman-teman (siluet) mengangguk
    q = pop(t, cs(seg0(9)) - 0.1)
    if q > 0:
        for k, x in enumerate((600, 720, 840)):
            nod = 8 * max(0, math.sin(2 * math.pi * 1.3 * t + k))
            paste_c(img, silhouette(170), x, 1355 + nod, q, 0, tag="teman")
        paste_c(img, bubble("ya, memang begitu suaramu", col=WHITE, fg=NAVY, size=34, tail="right"), 640, 1150, q, 2,
                tag="bubble teman")
    draw_aru(img, 270, 1450, 400, t, kind="wince", angle_amp=3.0, bob=4)


def scene3(img, t):
    """potongan kepala Aru: panah toska lewat udara, panah kuning lewat tulang kepala."""
    p = pop(t, cs(seg0(11)) - 0.1)
    if p > 0:
        paste_c(img, pill("DUA jalur", fill=YEL, fg=NAVY, size=58), W / 2, 520, p, -2, tag="pill dua jalur")
    draw_aru(img, HA["cx"], HA["bottom"], HA["h"], 0.0, bob=0, angle_amp=0)
    air_g = eout((t - cs(chunk_of("UDARA,"))) / 0.9) if t >= cs(chunk_of("UDARA,")) else 0
    bone_g = eout((t - cs(chunk_of("DAN TULANG KEPALA."))) / 0.9) if t >= cs(chunk_of("DAN TULANG KEPALA.")) else 0
    head_paths(img, t, air_g, bone_g)
    if air_g > 0:
        paste_c(img, pill("UDARA", fill=TEAL, fg=WHITE, size=40), 260, 1190, pop(t, cs(chunk_of("UDARA,"))), -3, tag="label udara")
    if bone_g > 0:
        paste_c(img, pill("TULANG", fill=YEL, fg=NAVY, size=40), 810, 800, pop(t, cs(chunk_of("DAN TULANG KEPALA."))), 3,
                tag="label tulang")


def scene4(img, t):
    """tulang memperkuat getaran nada rendah: panah kuning menebal, gelombang lebar & dalam."""
    draw_aru(img, HA["cx"], HA["bottom"], HA["h"], 0.0, bob=0, angle_amp=0)
    head_paths(img, t, 1.0, 1.0, bone_w=20 + int(18 * eio((t - cs(seg0(14))) / 0.6)), air_a=0.35)
    p = pop(t, SC[4] + 0.15)
    if p > 0:
        T, td = card(780, 220, fill=WHITE, outline=NAVY)
        text_c(td, (390, 40), "NADA RENDAH", F("pb", 38), NAVY)
        sine_wave(td, 40, 740, 135, 55, 2.2, -t * 3.0, YEL, width=16)
        sine_wave(td, 40, 740, 135, 55, 2.2, -t * 3.0, NAVY, width=4)
        paste_c(img, T, W / 2, 560, p, tag="kartu nada rendah")


def scene5(img, t):
    """dari dalam suaramu lebih berat: Aru bergaya penyiar, mikrofon, gelombang dalam."""
    draw_aru(img, 440, 1480, 760, t, angle_amp=1.5, bob=5)
    d = ImageDraw.Draw(img)
    p = pop(t, SC[5] + 0.1)
    if p > 0:
        paste_c(img, bubble("Haaalo… selamat malam…", col=NAVY, fg=YEL, size=44, tail="left"), 600, 620, p, -2, tag="bubble berat")
    q = pop(t, cs(chunk_of("LEBIH BERAT.")) - 0.2)
    if q > 0:
        paste_c(img, stamp("LEBIH BERAT", col=RED, size=64), 650, 1290, q, -6, tag="stempel berat")
    em = emoji_img("🎙️", 170)
    paste_c(img, em, 800, 1180, pop(t, SC[5] + 0.2), 8, tag="mic")
    sine_wave(d, 150, 950, 1500 + 0, 0, 1, 0, WHITE, 1) if False else None


def scene6(img, t):
    """PAYOFF: mikrofon HP cuma menangkap jalur udara; jalur tulang putus; 2 jalur -> 1 jalur; Aru kaget."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[6] + 0.05)
    t_mic = cs(seg0(16)); t_cut = cs(chunk_of("HILANG,")); t_one = cs(seg0(18))
    if p > 0:
        T, td = head_card(780, 330, "MIKROFON HP", col=NAVY, size=40)
        T.alpha_composite(emoji_img("🗣️", 120), (70, 150))
        T.alpha_composite(emoji_img("📱", 130), (580, 150))
        g = eout((t - t_mic) / 0.8) if t >= t_mic else 0
        path_arrow(td, [(200, 190), (380, 190), (560, 190)], TEAL, g, w=18, head=36, outline=NAVY)
        if t >= t_mic:
            td.text((380, 150), "udara", font=F("pb", 30), fill=TEAL, anchor="mm")
        if t >= t_cut - 0.5:
            gb = eout((t - (t_cut - 0.5)) / 0.4)
            path_arrow(td, [(200, 250), (290, 270), (380, 280)], YEL, gb, w=16, head=0, outline=NAVY)
            if t >= t_cut:
                a = clamp(1 - (t - t_cut - 0.2) / 0.5)
                cx = 400 + 5 * math.sin(t * 40) * clamp(1 - (t - t_cut) / 0.3)
                if a > 0:
                    td.line([(cx - 36, 255), (cx + 36, 305)], fill=RED, width=14); td.line([(cx - 36, 305), (cx + 36, 255)], fill=RED, width=14)
                td.text((560, 290), "tulang: putus", font=F("pb", 32), fill=RED, anchor="mm")
        T.info["nw"] = 780
        paste_c(img, T, W / 2, 620, p, tag="kartu mikrofon")
    q = pop(t, t_one - 0.1)
    if q > 0:
        C, cd = card(700, 220, fill=WHITE, outline=RED, ow=7)
        f = F("pb", 110)
        text_c(cd, (130, 112), "2", f, GREY_T); cd.line([(80, 150), (180, 70)], fill=RED, width=12)
        arrow(cd, 215, 112, 330, 112, NAVY, w=14, head=32)
        text_c(cd, (440, 112), "1", F("pb", 160), RED)
        text_c(cd, (600, 82), "jalur", F("pb", 40), NAVY); text_c(cd, (600, 134), "saja", F("pb", 40), NAVY)
        paste_c(img, C, W / 2, 905, q * (1 + 0.03 * math.sin(t * 9)), 0, tag="kartu 2 ke 1")
    draw_aru(img, 300, 1325, 340, t, kind="shock", angle_amp=3.0, bob=4)
    paste_c(img, bocor_h(210, "cover"), 700, 1215 - 8 * abs(math.sin(t * 8)), 1.0, 4 * math.sin(t * 9), tag="bocor")


def share_card(img, t):
    """ajakan kirim di puncak A6 (PRB-55 poin 3)."""
    if not (SHARE[0] <= t < SHARE[1]): return
    a = min(clamp((t - SHARE[0]) / 0.25), clamp((SHARE[1] - t) / 0.25))
    s = 0.85 + 0.15 * back((t - SHARE[0]) / 0.35)
    T, td = card(800, 190, fill=TEAL)
    l1 = "Kirim ke teman yang benci"; l2 = "dengar voice note sendiri"
    text_c(td, (400, 62), l1, fit("pb", 44, l1, 720), WHITE)
    text_c(td, (400, 128), l2, fit("pb", 46, l2, 720), YEL)
    paste_c(img, T, W / 2, 1415 + 4 * math.sin(t * 5), s, 0, a, tag="kartu kirim")


def scene7(img, t):
    """bantahan: Si Bocor mengangkat papan TIM REKAMAN JELEK; Aru menggeleng, 'eits'."""
    p = pop(t, SC[7] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("memang JELEK?", "🤨", fill=YEL, fg=NAVY, size=56), W / 2, 520, p, -2, tag="pill jelek")
    draw_aru(img, 365, 1470, 640, t, kind="wince", angle_amp=7.0 * (1 if t < cs(seg0(20)) else 0.3), bob=4)
    q = pop(t, SC[7] + 0.3)
    if q > 0:
        S, sd = card(520, 190, fill=WHITE, outline=RED, ow=7)
        sd.line([(260, 190), (260, 330)], fill=NAVY, width=10) if False else None
        text_c(sd, (260, 62), "TIM REKAMAN", F("pb", 54), RED); text_c(sd, (260, 128), "JELEK", F("pb", 62), RED)
        S.info["nw"] = 520
        paste_c(img, S, 680, 870 + 6 * math.sin(t * 4), q, -3, tag="papan rekaman jelek")
        paste_c(img, bocor_h(250, "giggle"), 760, 1220 - 8 * abs(math.sin(t * 6)), q, 0, tag="bocor")
    r = pop(t, cs(seg0(19)) + 0.9)
    if r > 0:
        paste_c(img, bubble("Eits!", col=NAVY, fg=YEL, size=60, tail="left"), 380, 800, r, -3, tag="bubble eits")
    r = pop(t, cs(seg0(20)) - 0.05)
    if r > 0:
        paste_c(img, stamp("BELUM TENTU", col=TEAL, size=58), 560, 1360, r, -5, tag="stempel belum tentu")


def wave_tile(w, h, label, t, col=TEAL, hl=False):
    C, cd = card(w, h, fill=WHITE, outline=YEL if hl else NAVY, ow=8 if hl else 5)
    cd.text((w / 2, 48), "🎧" if False else "", font=F("pb", 20), fill=NAVY, anchor="mm")
    e = emoji_img("🎧", 64); C.alpha_composite(e, (int(w / 2 - e.width / 2), 14))
    bars(cd, 22, w - 22, 140, 90, t + hash(label) % 7, n=6, col=YEL if hl else col, speed=8, w=14)
    pill_bg = YEL if hl else (232, 238, 246)
    cd.rounded_rectangle((10, h - 62, w - 10, h - 14), 20, fill=pill_bg)
    text_c(cd, (w / 2, h - 38), label, fit("pb", 30, label, w - 30), NAVY)
    C.info["nw"] = w
    return C


def scene8(img, t):
    """studi 2013: 80 orang; di antara banyak gelombang, satu berlabel 'punyamu' DISELIPKAN diam-diam."""
    p = pop(t, SC[8] + 0.05)
    t_st = cs(seg0(22))
    if p > 0:
        u = eout((t - SC[8] - 0.2) / 1.2)
        T, td = card(780, 230, fill=NAVY, outline=NAVY)
        text_c(td, (390, 80), f"{int(round(80 * u))} ORANG", F("pb", 84), YEL)
        if t >= t_st - 0.05:
            l = F("pb", 46); a = "suaranya "; b = "DISELIPKAN"
            wa, wb = l.getlength(a), l.getlength(b); x0 = 390 - (wa + wb) / 2
            td.text((x0, 176), a, font=l, fill=WHITE, anchor="lm"); td.text((x0 + wa, 176), b, font=l, fill=YEL, anchor="lm")
        else:
            text_c(td, (390, 176), "peserta studi 2013", F("pb", 40), WHITE)
        paste_c(img, T, W / 2, 640, p, tag="kartu 80 orang")
    xs = (240, 440, 640, 840)
    for k, (x, lab) in enumerate(zip(xs[:3], ("suara A", "suara B", "suara C"))):
        q = pop(t, SC[8] + 0.35 + 0.12 * k)
        if q > 0: paste_c(img, wave_tile(180, 250, lab, t), (240, 440, 640)[k], 1050, q, 0, tag="tile")
    if t >= t_st:
        u = eout((t - t_st) / 0.5)
        paste_c(img, wave_tile(180, 250, "punyamu", t, hl=True), 840, 1050 - 150 * (1 - u), 1.0, 0, tag="tile punyamu")
        paste_c(img, emoji_img("🤫", 90), 840, 1240, pop(t, t_st + 0.3), 0, tag="shh")


def scene9(img, t):
    """hasil: bintang naik untuk 'punyamu'; Aru tersipu; Si Bocor menurunkan papan; 'cuma kaget'."""
    p = pop(t, SC[9] + 0.05)
    t_m = cs(seg0(24)); t_k = cs(seg0(25))
    if p > 0:
        paste_c(img, wave_tile(260, 250, "punyamu", t, hl=True), 540, 660, p, 0, tag="tile punyamu")
        n = int(clamp((t - t_m) / 1.6) * 5.99) if t >= t_m else 0
        S = Image.new("RGBA", (560, 110), (0, 0, 0, 0)); sd = ImageDraw.Draw(S)
        for k in range(5):
            star(sd, 56 + 112 * k, 56, 46, YEL if k < n else (214, 218, 230))
        S.info["nw"] = 560
        paste_c(img, S, 540, 900, p, 0, tag="bintang")
    q = pop(t, t_m + 0.1)
    if q > 0:
        paste_c(img, pill("LEBIH MENARIK", fill=YEL, fg=NAVY, size=52), 700, 1010, q, -2, tag="pill menarik")
    shock = t >= t_k
    draw_aru(img, 330, 1470, 560, t, kind="shock" if shock else "normal", angle_amp=2.0, bob=5)
    drop = eio((t - SC[9] - 1.0) / 0.8)
    S2, sd2 = card(330, 120, fill=WHITE, outline=RED, ow=6)
    text_c(sd2, (165, 62), "REKAMAN JELEK", fit("pb", 30, "REKAMAN JELEK", 300), RED)
    S2.info["nw"] = 330
    paste_c(img, S2, 770, 1180 + 120 * drop, 1.0, 6 * drop, max(0.0, 1 - 1.2 * drop), tag="papan turun")
    paste_c(img, bocor_h(210, "normal"), 790, 1350 + 30 * drop, 1.0, 0, tag="bocor")
    r = pop(t, t_k)
    if r > 0:
        paste_c(img, bubble("cuma kaget!", col=NAVY, fg=YEL, size=48, tail="left"), 700, 1170, r, 2, tag="bubble kaget")


def scene10(img, t):
    """dua-duanya suaramu; putar voice note-mu lagi malam ini."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[10] + 0.05)
    if p > 0:
        for j, (x, em, lab) in enumerate(((330, "🗣️", "KEPALA"), (750, "📱", "REKAMAN"))):
            C, cd = card(330, 330, fill=WHITE, outline=NAVY)
            C.alpha_composite(emoji_img(em, 150), (int(165 - emoji_img(em, 150).width / 2), 40))
            cd.rounded_rectangle((20, 230, 310, 300), 24, fill=TEAL if j == 0 else YEL)
            text_c(cd, (165, 266), lab, F("pb", 40), WHITE if j == 0 else NAVY)
            paste_c(img, C, x, 700, p, -1.5 if j == 0 else 1.5, tag="kartu " + lab)
        d.ellipse((540 - 52, 700 - 52, 540 + 52, 700 + 52), fill=YEL, outline=NAVY, width=6)
        text_c(d, (540, 698), "=", F("pb", 78), NAVY)
        q = pop(t, cs(seg0(26)) + 0.5)
        if q > 0:
            paste_c(img, pill("dua-duanya SUARAMU", fill=NAVY, fg=WHITE, size=44), W / 2, 960, q, -1, tag="pill suaramu")
    t_pt = cs(seg0(27))
    q = pop(t, t_pt - 0.05)
    if q > 0:
        paste_c(img, pill_emoji("MALAM INI", "🌙", fill=NAVY, fg=YEL, size=44), W / 2, 1090, q, -2, tag="pill malam")
        C, cd = card(700, 190, fill=WHITE, outline=NAVY)
        press = clamp((t - t_pt - 0.5) / 0.12) * clamp(1 - (t - t_pt - 0.7) / 0.15)
        play_btn(cd, 100, 95, 62 - 8 * press)
        bars(cd, 190, 640, 95, 100, t, n=16, col=TEAL if t < t_pt + 0.6 else YEL, speed=8)
        paste_c(img, C, W / 2, 1290, q, 0, tag="kartu putar")


def scene11(img, t):
    """layar dibagi dua: TIM KEPALA vs TIM REKAMAN; pertanyaan dua kubu."""
    d = ImageDraw.Draw(img)
    t_k = cs(seg0(29)); t_r = cs(seg0(30))
    p = pop(t, SC[11] + 0.05)
    if p > 0:
        paste_c(img, pill("SUARA ASLIMU?", fill=YEL, fg=NAVY, size=56), W / 2, 520, p, -2, tag="pill aslimu")
    cols = [(140, 530, TEAL, "KEPALA", "🗣️", t_k, t_r), (550, 940, RED, "REKAMAN", "📱", t_r, TOTAL)]
    y0, y1 = 640, 1300
    for j, (x0, x1, col, lab, em, a0, a1) in enumerate(cols):
        act = a0 <= t < a1 or t < t_k
        q = pop(t, SC[11] + 0.1 + 0.12 * j)
        if q <= 0: continue
        C = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
        cd.rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), 30, fill=WHITE if act else (232, 235, 242),
                             outline=col if act else (200, 205, 216), width=7)
        cd.rounded_rectangle((0, 0, x1 - x0 - 1, 150), 30, fill=col if act else (190, 196, 210))
        cd.rectangle((0, 100, x1 - x0 - 1, 150), fill=col if act else (190, 196, 210))
        text_c(cd, ((x1 - x0) / 2, 44), "TIM", F("pb", 34), WHITE)
        text_c(cd, ((x1 - x0) / 2, 104), lab, fit("pb", 58, lab, x1 - x0 - 30), WHITE)
        e = emoji_img(em, 190)
        C.alpha_composite(e, (int((x1 - x0) / 2 - e.width / 2), 230))
        if j == 0:
            sine_wave(cd, 40, x1 - x0 - 40, 520, 50 if act else 25, 1.5, -t * 4, TEAL if act else (190, 196, 210), width=14)
        else:
            sine_wave(cd, 40, x1 - x0 - 40, 520, 14, 4, -t * 6, RED if act else (190, 196, 210), width=8)
        C.info["nw"] = x1 - x0
        beat = 1 + (0.03 * math.sin(t * 8) if (a0 <= t < a1) else 0)
        paste_c(img, C, (x0 + x1) / 2, (y0 + y1) / 2, q * beat, -1.5 if j == 0 else 1.5, tag="kolom " + lab)
    if t >= SC[11] + 0.2:
        d.ellipse((540 - 48, 970 - 48, 540 + 48, 970 + 48), fill=YEL, outline=NAVY, width=6)
        text_c(d, (540, 968), "vs", F("pb", 42), NAVY)


def scene12(img, t):
    """penutup <= 1,5 dtk, tanpa VO: logo kecil + ajakan komentar."""
    u = t - SC[12]
    la = clamp(u / 0.25)
    paste_c(img, logo_w(420), W / 2, 760, 0.9 + 0.1 * back(la), 0, la, tag="logo")
    q = pop(t, SC[12] + 0.1)
    if q > 0:
        B, bd = card(800, 230, fill=YEL, outline=NAVY)
        l1 = "Tim KEPALA atau tim REKAMAN?"
        text_c(bd, (400, 78), l1, fit("pb", 46, l1, 740), NAVY)
        text_c(bd, (400, 164), "Tulis di komentar", F("pb", 48), NAVY)
        paste_c(img, B, W / 2, 1080, q, 0, tag="kartu komen")


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10, scene11, scene12]
assert len(SCENES) == NS


def draw_notes(img, k):
    lines = NOTES.get(k)
    if not lines: return
    d = ImageDraw.Draw(img)
    for j, s in enumerate(lines):
        f = fit("pm", 28, s, MAXW)
        track("catatan", f.getlength(s), W / 2 - f.getlength(s) / 2, W / 2 + f.getlength(s) / 2)
        d.text((W / 2, 1712 + j * 40), s, font=f, fill=GREY_T, anchor="mm")


FOLLOW_S = "Follow @kabar.arunika · fakta sehari-hari 1 menit"


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
    if k == 0:
        img = bg_rest().copy()
        scene0(img, t)
    else:
        img = bg_rest().copy()
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        SCENES[k](layer, t)
        s = 0.94 + 0.06 * back(ts / 0.4)
        if s < 0.999 or s > 1.001:
            paste_c(img, layer, W / 2, H / 2, s)
        else:
            img.alpha_composite(layer)
    Hd, hx0, hx1 = header()
    img.alpha_composite(Hd, (0, 236))      # pill kecil judul layar, y≈300 (PRB-41); bukan kartu judul besar
    track("pill judul", hx1 - hx0, hx0, hx1)
    if t >= 3.3 and k != 12:
        paste_c(img, logo_w(210), W / 2, 190, 1, 0, clamp((t - 3.3) / 0.3), tag="logo kecil")   # logo baru setelah dtk 3
    share_card(img, t)
    draw_sub(img, t)
    draw_notes(img, k)
    if FOLLOW[0] <= t < FOLLOW[1]:
        a = min(clamp((t - FOLLOW[0]) / 0.25), clamp((FOLLOW[1] - t) / 0.25))
        paste_c(img, follow_pill(), W / 2, 1490, 1, 0, a, tag="pill follow")
    if t >= PB_START:
        ImageDraw.Draw(img).rectangle((0, H - 14, int(W * (t - PB_START) / (TOTAL - PB_START)), H), fill=YEL)
    return img.convert("RGB")


def check(step=0.1):
    bad = {}; widest = {}
    n = int(TOTAL / step)
    for j in range(n + 1):
        t = min(TOTAL - 0.01, j * step)
        frame(t)
        for tag, nw, x0, x1 in BOXES:
            widest[tag] = max(widest.get(tag, 0), nw)
            if (tag not in ("aru", "bos") and nw > MAXW + 0.5) or x0 < XMIN - 0.5 or x1 > XMAX + 0.5:
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
    for tt in (0.35, 0.8):
        ev.append({"t": tt, "sfx": "klik", "gain": 0.4})              # play ditekan
    ev.append({"t": ZOOM_T, "sfx": "pop", "gain": 0.3})
    ev.append({"t": FLIP, "sfx": "ding", "gain": 0.3})                # 2 -> 1
    for i in (seg0(3), seg0(5), seg0(6), seg0(8), seg0(9), seg0(11), chunk_of("UDARA,"), chunk_of("DAN TULANG KEPALA."),
              seg0(14), seg0(16), chunk_of("HILANG,"), seg0(18), seg0(20), seg0(22), seg0(24), seg0(25), seg0(26),
              seg0(27), seg0(29), seg0(30)):
        ev.append({"t": cs(i), "sfx": "pop", "gain": 0.26})
    ev.append({"t": cs(seg0(8)) + 0.35, "sfx": "klik", "gain": 0.45})   # hapus ditekan
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": cs(seg0(18)), "sfx": "ding", "gain": 0.35})         # 2 jalur -> 1 jalur (puncak)
    ev.append({"t": SHARE[0] + 0.2, "sfx": "klik", "gain": 0.3})
    ev.append({"t": SC[12] + 0.1, "sfx": "pop", "gain": 0.3})
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

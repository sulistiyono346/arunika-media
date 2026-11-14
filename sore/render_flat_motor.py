"""Renderer ARN-46 "Mana Lebih Hemat? #7 — motor cash vs kredit" — gaya Flat 2D latar terang (sama dengan #6, PRB-31).
Salinan pagi/render_flat_emas.py (helper kartu, koin, Si Bocor, panah, Aru, logo, subtitle, sfx) dengan:
- frame 0: Aru menuntun satu motor matik besar, bayangan motor kedua (transparan), Si Bocor menarik karung "Rp"
  bolong + koin jatuh ("cring!"); counter Rp19.174.000 -> Rp42.171.000 bergerak dtk 1,6-2,6 (PRB-29/36/46);
  tanpa label seri/logo/progress bar dtk 0-3.
- area aman (PRB-41): semua pill/bubble/kartu <= 800 px dan berada di x 130..950; subtitle <= W-300.
  Perintah `check` memindai frame tiap 0,1 dtk dan melaporkan elemen yang melanggar.
- progress bar mulai dtk 3,5.
Pemakaian (dari folder kerja sore/build/motor, setelah align_motor.py -> timing.json):
  TOTAL=52.0 python3 ../../render_flat_motor.py events
  TOTAL=52.0 python3 ../../render_flat_motor.py check
  TOTAL=52.0 python3 ../../render_flat_motor.py stills 0,2,...
  TOTAL=52.0 python3 ../../render_flat_motor.py video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, rp, NAVY, TEAL, YEL, WHITE, GREY_T, RED, SAFE_X)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "52.0"))
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
GREEN = (46, 160, 110); INK = (60, 66, 92); LIGHT = (232, 238, 246)
BODY = (224, 82, 63); BODY_D = (176, 56, 44)
MAXW, XMIN, XMAX = 800, 130, 950   # PRB-41

TIM = json.load(open("timing.json"))
def cs(i): return TIM[i]["start"] + LEAD
def ce(i): return TIM[i]["end"] + LEAD

SCENE_CHUNK = [0, 6, 12, 17, 21, 26, 30, 34, 39, 45]
SC = [0.0] + [cs(i) - 0.25 for i in SCENE_CHUNK[1:-1]] + [cs(45) - 0.4, TOTAL]   # adegan 10 maju 0,15 dtk -> tiap adegan <= 6 dtk
NS = len(SCENE_CHUNK)
FOLLOW = (10.4, 15.0)          # PRB-4: ajakan follow teks kecil dtk 10-15
PB_START = 3.5                 # progress bar mulai dtk 3,5
SRC = "Simulasi BeAT CBS, Jakarta–Tangerang (detikOto, 6 Jan 2026)"
NOTES = {   # PRB-39: kartu sumber di layar
    0: (SRC,),
    1: ("Kursi komentar teratas: masih kosong",),
    2: (SRC,),
    3: (SRC,),
    4: (SRC,),
    5: (SRC,),
    6: ("*hitungan Arunika, semua biaya dianggap bunga",),
    7: (SRC,),
    8: ("skema beda tiap dealer & pembiayaan · cek penawaran resmi",),
}
CT0, CT1 = 1.6, 2.6            # counter frame 0
C0, C1 = 19174000, 42171000


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


# ---------- motor matik generik (tanpa logo merek), menghadap kanan; kanvas 560x380 ----------
MOTOR_W, MOTOR_H = 560, 380
HANDLE = (405, 66)


@lru_cache(None)
def motor_img(w, ghost=False):
    im = Image.new("RGBA", (MOTOR_W, MOTOR_H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    body = (170, 182, 205) if ghost else BODY
    ink = (120, 132, 160) if ghost else NAVY
    dark = (150, 160, 182) if ghost else (52, 52, 64)
    for cx in (140, 440):                                       # roda
        d.ellipse((cx - 64, 236, cx + 64, 364), fill=ink)
        d.ellipse((cx - 44, 256, cx + 44, 344), fill=(214, 220, 232) if not ghost else (205, 212, 226))
        d.ellipse((cx - 15, 285, cx + 15, 315), fill=ink)
    d.rectangle((228, 238, 366, 262), fill=dark, outline=ink, width=4)        # dek kaki
    d.polygon([(58, 252), (64, 192), (108, 150), (252, 140), (304, 168), (316, 252)], fill=body, outline=ink)
    d.line([(58, 252), (64, 192), (108, 150), (252, 140), (304, 168), (316, 252), (58, 252)], fill=ink, width=6,
           joint="curve")
    d.line([(92, 214), (282, 198)], fill=WHITE if not ghost else (226, 230, 240), width=10)
    d.ellipse((52, 198, 74, 228), fill=BODY_D if not ghost else ink)           # lampu belakang
    d.rounded_rectangle((94, 116, 300, 152), 16, fill=dark, outline=ink, width=5)   # jok
    d.line([(404, 108), (440, 300)], fill=ink, width=14)                       # garpu depan
    d.polygon([(330, 262), (352, 152), (380, 92), (410, 82), (420, 102), (400, 172), (372, 262)], fill=body, outline=ink)
    d.line([(330, 262), (352, 152), (380, 92), (410, 82), (420, 102), (400, 172), (372, 262)], fill=ink, width=6,
           joint="curve")
    d.polygon([(390, 252), (440, 224), (494, 250), (484, 264), (440, 244), (400, 264)], fill=body, outline=ink)
    d.polygon([(412, 90), (452, 98), (442, 122), (408, 114)], fill=(255, 240, 190) if not ghost else WHITE, outline=ink)
    d.line([(368, 74), (446, 60)], fill=ink, width=12)                         # setang
    d.line([(392, 72), (384, 40)], fill=ink, width=6)
    d.ellipse((366, 20, 398, 44), fill=(214, 220, 232), outline=ink, width=4)  # spion
    r = w / MOTOR_W
    out = im.resize((w, int(MOTOR_H * r)), Image.LANCZOS)
    if ghost:
        a = out.getchannel("A").point(lambda v: int(v * 0.42)); out.putalpha(a)
    return out


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
    f = F("pb", 34); s1 = "MANA LEBIH HEMAT?"; s2 = "#7"
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


def title_pills(img, rows, y, size=76, gap=16, keyword="DOBEL"):
    """judul cover (kolom Judul layar): kotak per kata, DOBEL kuning; tiap baris <= 800 px."""
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
def sub_layer(i):
    c = TIM[i]; words = c["text"].split()
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
    sc = 0.85 + 0.15 * back((t - s0) / 0.22) if i != 0 else 1.0
    paste_c(img, sub_layer(i), W / 2, 1600, sc, tag="subtitle")


# ---------- adegan ----------
def counter_value(t):
    v = C0 + (C1 - C0) * eio((t - CT0) / (CT1 - CT0))
    return int(round(v / 1000.0) * 1000)


def scene0(img, t):
    """frame 0: Aru menuntun motor besar, bayangan motor kedua, Si Bocor + karung bolong, counter naik dtk 1,6-2,6."""
    z = 1.0 + 0.08 * eio((t - 1.4) / 1.4)        # kamera maju pelan, visual berganti ~dtk 1,5
    cx0, fl = 560, FLOOR0 - 10
    mw = int(620 * z); r = mw / MOTOR_W; mh = MOTOR_H * r
    roll = 6 * math.sin(t * 2.2)                 # motor maju-mundur pelan (dituntun)
    # bayangan motor kedua (transparan) di belakang kiri
    gx = cx0 - 110 * z + 0.6 * roll; gy = fl - 70 * z
    G = motor_img(int(mw * 0.9), True)
    paste_c(img, G, gx, gy - G.height / 2, tag="motor bayangan")
    # Aru di balik setang
    hx = cx0 - mw / 2 + HANDLE[0] * r + roll
    draw_aru(img, hx - 30 * z, fl - 40 * z, int(560 * z), t)
    M = motor_img(mw)
    paste_c(img, M, cx0 + roll, fl - mh / 2, tag="motor")
    # Si Bocor + karung bolong, koin jatuh dari lubang
    bs = 0.75 * z; bx = cx0 - 270 * z; by = fl - 100 * z
    hop = abs(math.sin(t * 6)) * 6
    hole = (bx + (BOCOR_HOLE[0] - 150) * bs, by + (BOCOR_HOLE[1] - 135) * bs)
    for k, ph in enumerate((0.0, 0.33, 0.66)):
        u = (t * 1.3 + ph) % 1.0
        paste_c(img, coin(int(22 * z)), hole[0] + 8 * k - 8, hole[1] + u * 120 * z, 1.0, u * 220, alpha=1 - 0.6 * u)
    paste_c(img, bocor_img(), bx, by - hop, bs, tag="bocor")
    # judul layar (pill judul, bukan pengganti subtitle)
    title_pills(img, [["KREDIT", "MOTOR,"], ["KOK", "DOBEL?"]], 290)
    # counter harga: frame 0 = Rp19.174.000 (cash), naik ke Rp42.171.000 (total kredit) dtk 1,6-2,6
    v = counter_value(t); hot = v > C0
    T, td = card(680, 170, fill=(253, 232, 228) if hot else WHITE, outline=RED if hot else NAVY, ow=7)
    s = rp(v); f = fit("pb", 92, "Rp42.171.000", 520)
    td.text((300, 85), s, font=f, fill=RED if hot else NAVY, anchor="mm")
    if hot:
        a = clamp((t - CT0) / 0.3)
        arrow(td, 612, 130, 612, 130 - 90 * a, RED, w=18, head=38)
    paste_c(img, T, 540, 690, 1.0, -1.5 * math.sin(t * 2), tag="counter")
    # "coba tebak, selisihnya berapa?" -> lencana tanda tanya
    p = pop(t, cs(4))
    if p > 0:
        L = Image.new("RGBA", (220, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.ellipse((10, 10, 210, 210), fill=YEL, outline=NAVY, width=8)
        text_c(d, (110, 108), "?", F("pb", 120), NAVY)
        paste_c(img, L, 255, 880, 0.9 * p, 8 * math.sin(t * 4), tag="lencana ?")


def scene1(img, t):
    """komentar teratas #6: janjinya tampil di sini, masih kosong -> giliranmu (PRB-43)."""
    cw, ch = 800, 600
    L, cd = card(cw, ch)
    cd.rounded_rectangle((0, 0, cw, 110), 30, fill=TEAL); cd.rectangle((0, 60, cw, 110), fill=TEAL)
    cd.rounded_rectangle((0, 0, cw, ch), 30, outline=NAVY, width=5)
    text_c(cd, (cw / 2, 56), "KOMENTAR TERATAS #6", F("pb", 46), WHITE)
    hot = t >= cs(11)
    cd.ellipse((50, 160, 150, 260), fill=YEL if hot else (215, 220, 230), outline=NAVY, width=5)
    text_c(cd, (100, 210), "?", F("pb", 56), NAVY)
    box = (180, 160, cw - 50, 440)
    rect = [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3]), (box[0], box[1])]
    if hot:
        cd.rounded_rectangle(box, 22, fill=(255, 244, 205))
        dashed(cd, rect, YEL, w=7, phase=(t * 60))
        msg = "namamu di sini?"
        n = int(clamp((t - cs(11) + 0.1) / 0.8) * len(msg))
        f = F("pb", 50)
        cd.text((box[0] + 30, 300), msg[:n], font=f, fill=NAVY, anchor="lm")
        if int(t * 2.5) % 2 == 0:
            x = box[0] + 34 + f.getlength(msg[:n])
            cd.rectangle((x, 272, x + 6, 330), fill=NAVY)
    else:
        dashed(cd, rect, (170, 178, 195), w=6)
        for k, ww in enumerate((400, 290)):
            cd.rounded_rectangle((box[0] + 30, 230 + k * 80, box[0] + 30 + ww, 258 + k * 80), 14, fill=(228, 232, 240))
    on = t >= cs(8)
    text_c(cd, (cw / 2, 520), "like terbanyak = tampil di sini" if on else "0 komentar · #6 emas buyback",
           F("pm", 34), RED if on else GREY_T)
    paste_c(img, L, W / 2, 800, pop(t, SC[1] + 0.05), tag="kartu komentar")
    if not hot:
        p = pop(t, cs(10))
        if p > 0:
            paste_c(img, stamp("KOSONG", size=76), W / 2 + 110, 830, 1.6 - 0.6 * p if p < 1 else 1.0, -10, min(1, p),
                    tag="stempel KOSONG")
    draw_aru(img, 300, 1430, 300, t)
    if hot:
        p = pop(t, cs(11))
        if p > 0:
            paste_c(img, bubble("giliranmu!", size=46), 640, 1210, p, tag="bubble giliranmu")


def scene2(img, t):
    """patokan Honda BeAT CBS, bayar cash Rp19.174.000 (~19,2 juta)."""
    p = pop(t, SC[2] + 0.05)
    if p > 0:
        T, td = card(800, 300, fill=(255, 248, 236))
        Mi = motor_img(250)
        T.alpha_composite(Mi, (30, int(150 - Mi.height / 2)))
        td.text((310, 105), "HONDA BeAT", font=F("pb", 60), fill=NAVY, anchor="lm")
        td.text((310, 175), "CBS", font=F("pb", 52), fill=BODY, anchor="lm")
        if t >= cs(13):
            td.rounded_rectangle((310, 215, 700, 270), 28, fill=NAVY)
            text_c(td, (505, 243), "Jakarta–Tangerang", F("pb", 30), WHITE)
        paste_c(img, T, W / 2, 640, p, tag="kartu BeAT")
    p = pop(t, cs(14) - 0.1)
    if p > 0:
        T, td = head_card(800, 330, "BAYAR CASH", col=GREEN, size=46)
        u = eout((t - cs(14)) / 1.0)
        text_c(td, (400, 220), rp(int(round(19174000 * u / 1000) * 1000)), F("pb", 104), NAVY)
        paste_c(img, T, W / 2, 1050, p, tag="kartu cash")
    p = pop(t, cs(16))
    if p > 0:
        paste_c(img, pill("≈ Rp19,2 juta", fill=YEL, fg=NAVY, size=56), W / 2, 1320, p, -2, tag="pill 19,2")


def scene3(img, t):
    """kredit: DP Rp4.900.000, cicilan Rp793.000/bulan."""
    p = pop(t, SC[3] + 0.05)
    if p > 0:
        T, td = head_card(800, 470, "KREDIT", col=RED, size=50)
        if t >= cs(18) - 0.05:
            td.text((50, 175), "DP", font=F("pm", 40), fill=GREY_T, anchor="lm")
            u = eout((t - cs(18)) / 0.8)
            td.text((750, 175), rp(int(round(4900000 * u / 1000) * 1000)), font=F("pb", 60), fill=NAVY, anchor="rm")
        if t >= cs(19) - 0.05:
            td.line([(50, 245), (750, 245)], fill=LIGHT, width=4)
            td.text((50, 320), "Cicilan", font=F("pm", 40), fill=GREY_T, anchor="lm")
            td.text((50, 372), "per bulan", font=F("pm", 30), fill=GREY_T, anchor="lm")
        if t >= cs(20) - 0.05:
            q = clamp((t - cs(20) + 0.05) / 0.3)
            td.rounded_rectangle((330, 290, 770, 410), 24, fill=YEL)
            text_c(td, (550, 352), "Rp793.000", F("pb", int(74 * (0.6 + 0.4 * q))), NAVY)
        paste_c(img, T, W / 2, 790, p, tag="kartu kredit")
    draw_aru(img, 290, 1470, 280, t)
    p = pop(t, cs(20) + 0.6)
    if p > 0:
        paste_c(img, bubble("cuma 700 ribuan?", size=40), 620, 1270, p, tag="bubble 700 ribuan")


def scene4(img, t):
    """kedengarannya ringan... masalahnya 47 bulan, hampir 4 tahun."""
    early = t < cs(23)
    p = pop(t, SC[4] + 0.05)
    if p > 0:
        fl = 6 * math.sin(t * 3)
        P = pill("Rp793.000 / bulan", fill=WHITE, fg=NAVY, size=52)
        paste_c(img, P, W / 2, 470 + fl, p, 2 * math.sin(t * 2), tag="pill cicilan")
        if early:
            draw_aru(img, 420, 1440, 420, t)
            q = pop(t, SC[4] + 0.3)
            if q > 0:
                paste_c(img, bubble("ringan, kan?", size=46, tail="left"), 700, 920, q, tag="bubble ringan")
        if t >= cs(21) + 0.3 and early:
            paste_c(img, stamp("RINGAN?", col=GREEN, size=60), 770, 600, pop(t, cs(21) + 0.3), -8, tag="stempel ringan")
    if t >= cs(23) - 0.1:
        cw, ch = 800, 640
        T, td = head_card(cw, ch, "BAYAR TIAP BULAN, SELAMA…", col=NAVY, size=40)
        t0 = cs(24) - 0.1; t1 = cs(24) + 1.3
        n = int(47 * clamp((t - t0) / (t1 - t0)))
        for k in range(48):
            r_, c_ = divmod(k, 8)
            x = 34 + c_ * 92; y = 126 + r_ * 82
            lit = k < n
            fill = (255, 214, 205) if lit else LIGHT
            if k == 47: fill = WHITE
            td.rounded_rectangle((x, y, x + 80, y + 68), 14, fill=fill, outline=RED if lit else (205, 210, 222), width=3)
            if lit:
                text_c(td, (x + 40, y + 34), str(k + 1), F("pb", 28), RED)
        if t >= cs(25) - 0.05:   # garis per tahun
            for yr in range(1, 4):
                y = 126 + yr * 2 * 82 - 7
                dashed(td, [(30, y), (cw - 30, y)], NAVY, w=4, phase=t * 30)
        paste_c(img, T, W / 2, 960, pop(t, cs(23) - 0.1), tag="kalender 47")
        p = pop(t, cs(24) + 0.2)
        if p > 0:
            v = max(1, min(47, n))
            paste_c(img, pill(f"{v} BULAN", fill=RED, fg=WHITE, size=64), 370, 1370, p, -2, tag="pill 47 bulan")
        p = pop(t, cs(25))
        if p > 0:
            paste_c(img, stamp("≈ 4 TAHUN", col=NAVY, size=54), 760, 1370, p, 6, tag="stempel 4 tahun")


def scene5(img, t):
    """total kredit Rp42.171.000 -> selisih dengan cash Rp22.997.000 (~Rp23 juta)."""
    p = pop(t, SC[5] + 0.05)
    if p > 0:
        T, td = head_card(800, 470, "TOTAL BAYAR KREDIT", col=NAVY, size=44)
        td.text((50, 165), "DP", font=F("pm", 40), fill=GREY_T, anchor="lm")
        td.text((750, 165), "Rp4.900.000", font=F("pb", 50), fill=NAVY, anchor="rm")
        td.text((50, 245), "Rp793.000 × 47", font=F("pm", 40), fill=GREY_T, anchor="lm")
        td.text((750, 245), "Rp37.271.000", font=F("pb", 50), fill=NAVY, anchor="rm")
        td.line([(50, 300), (750, 300)], fill=NAVY, width=4)
        if t >= cs(27) - 0.05:
            u = eout((t - cs(27)) / 1.0)
            td.rounded_rectangle((30, 325, 770, 445), 24, fill=YEL)
            td.text((60, 385), "Total", font=F("pb", 46), fill=NAVY, anchor="lm")
            td.text((750, 385), rp(int(round(42171000 * u / 1000) * 1000)), font=F("pb", 68), fill=NAVY, anchor="rm")
        paste_c(img, T, W / 2, 700, p, tag="kartu total")
    p = pop(t, cs(28) - 0.05)
    if p > 0:
        T, td = card(800, 300, fill=RED)
        text_c(td, (400, 62), "SELISIH DENGAN CASH", F("pb", 40), WHITE)
        u = eout((t - cs(29)) / 0.9) if t >= cs(29) else 0
        text_c(td, (400, 160), "+" + rp(int(round(22997000 * u / 1000) * 1000)), F("pb", 96), WHITE)
        s_ = "Rp42.171.000 − Rp19.174.000"
        text_c(td, (400, 250), s_, fit("pm", 34, s_, 700), (255, 226, 220))
        paste_c(img, T, W / 2, 1150, p, 1.0 * math.sin(t * 3), tag="kartu selisih")
    p = pop(t, cs(29) + 0.4)
    if p > 0:
        paste_c(img, pill("±Rp23 JUTA", fill=YEL, fg=NAVY, size=60), W / 2, 1405, p, -3, tag="pill 23 juta")


def scene6(img, t):
    """selisih lebih mahal dari motornya; setara bunga ±5% sebulan (*hitungan Arunika)."""
    d = ImageDraw.Draw(img)
    base = 1060; hmax = 400
    bars = [(330, "HARGA MOTOR", "Rp19,2 jt", 19.174, NAVY, SC[6] + 0.05),
            (750, "BIAYA KREDIT", "Rp23 jt", 22.997, RED, SC[6] + 0.35)]
    for x, lab, val, v, col, t0 in bars:
        u = eout((t - t0) / 0.7)
        if u <= 0: continue
        h = hmax * v / 22.997 * u
        d.rounded_rectangle((x - 110 + 8, base - h + 10, x + 110 + 8, base + 10), 26, fill=(20, 33, 91, 60))
        d.rounded_rectangle((x - 110, base - h, x + 110, base), 26, fill=col, outline=NAVY, width=5)
        if u > 0.9:
            text_c(d, (x, base - h + 50), val, fit("pb", 46, val, 200), WHITE)
        text_c(d, (x, base + 40), lab, fit("pb", 34, lab, 280), NAVY)
        if x == 330 and u > 0:
            Mi = motor_img(170)
            img.alpha_composite(Mi, (int(x - Mi.width / 2), int(base - h - Mi.height - 6)))
    d.line([(160, base), (920, base)], fill=NAVY, width=6)
    p = pop(t, cs(30) + 0.1)
    if p > 0:
        paste_c(img, stamp("LEBIH MAHAL!", col=RED, size=62), 560, 520, p, -6, tag="stempel lebih mahal")
    p = pop(t, cs(32) - 0.05)
    if p > 0:
        T, td = card(800, 270, fill=WHITE, outline=RED, ow=7)
        text_c(td, (400, 62), "SETARA BUNGA", F("pb", 42), GREY_T)
        q = 5 * eout((t - cs(33)) / 0.8) if t >= cs(33) else 0
        text_c(td, (400, 165), f"±{q:.0f}% sebulan*", F("pb", 92), RED)
        paste_c(img, T, W / 2, 1290, p, -1.5, tag="kartu bunga")


def scene7(img, t):
    """tenor 11 bulan: cicilan Rp1.762.000, total Rp24.282.000, selisih Rp5.108.000 (~5,1 juta)."""
    p = pop(t, SC[7] + 0.05)
    if p > 0:
        T, td = head_card(800, 470, "KALAU TENOR 11 BULAN?", col=TEAL, size=44)
        td.text((50, 165), "DP", font=F("pm", 40), fill=GREY_T, anchor="lm")
        td.text((750, 165), "Rp4.900.000", font=F("pb", 50), fill=NAVY, anchor="rm")
        if t >= cs(36) - 0.05:
            td.text((50, 245), "Cicilan × 11", font=F("pm", 40), fill=GREY_T, anchor="lm")
            td.text((690, 245), "Rp1.762.000", font=F("pb", 50), fill=RED, anchor="rm")
            q = clamp((t - cs(36)) / 0.3)
            arrow(td, 730, 270, 730, 270 - 50 * q - 1, RED, w=12, head=26)
        td.line([(50, 300), (750, 300)], fill=NAVY, width=4)
        if t >= cs(37) - 0.05:
            td.rounded_rectangle((30, 325, 770, 445), 24, fill=LIGHT)
            td.text((60, 385), "Total", font=F("pb", 46), fill=NAVY, anchor="lm")
            td.text((750, 385), "Rp24.282.000", font=F("pb", 62), fill=NAVY, anchor="rm")
        paste_c(img, T, W / 2, 700, p, tag="kartu 11 bulan")
    p = pop(t, cs(37) + 0.3)
    if p > 0:
        T, td = head_card(800, 330, "SELISIH DENGAN CASH", col=NAVY, size=40)
        rows = [("47 bln", 22.997, "Rp23 jt", RED), ("11 bln", 5.108, "Rp5,1 jt", GREEN)]
        for k, (lab, v, val, col) in enumerate(rows):
            y = 150 + k * 100
            td.text((40, y), lab, font=F("pb", 40), fill=NAVY, anchor="lm")
            u = eout((t - cs(37) - 0.3 - (0.5 if k else 0)) / 0.7)
            bw = 400 * v / 22.997 * u
            if bw > 2:
                td.rounded_rectangle((190, y - 32, 190 + bw, y + 32), 20, fill=col)
            if u > 0.8:
                td.text((190 + bw + 16, y), val, font=F("pb", 42), fill=col, anchor="lm")
        paste_c(img, T, W / 2, 1180, p, tag="kartu banding")


def scene8(img, t):
    """sebelum tanda tangan, minta rincian tertulis: admin, asuransi, total sampai lunas."""
    p = pop(t, SC[8] + 0.05)
    if p > 0:
        T, td = head_card(800, 600, "SEBELUM TANDA TANGAN", col=NAVY, size=46)
        if t >= cs(41) - 0.05:
            td.rounded_rectangle((40, 125, 760, 200), 20, fill=YEL)
            text_c(td, (400, 163), "minta rincian TERTULIS:", F("pb", 42), NAVY)
        items = [("Biaya admin", cs(42)), ("Asuransi", cs(43)), ("Total sampai lunas", cs(44))]
        for k, (s_, t0) in enumerate(items):
            y = 275 + k * 105
            on = t >= t0 - 0.05
            td.rounded_rectangle((40, y - 42, 760, y + 42), 20, fill=(232, 246, 238) if on else LIGHT)
            td.rounded_rectangle((62, y - 26, 114, y + 26), 10, fill=WHITE, outline=NAVY, width=4)
            if on:
                icon_check(td, 88, y, 0.62 * min(1.0, pop(t, t0 - 0.05)))
            td.text((140, y), s_, font=F("pb", 46), fill=NAVY if on else GREY_T, anchor="lm")
        paste_c(img, T, W / 2, 800, p, tag="kartu rincian")
    draw_aru(img, 290, 1470, 280, t)
    p = pop(t, cs(41) + 0.3)
    if p > 0:
        paste_c(img, bubble("bandingkan TOTAL!", size=40), 620, 1260, p, tag="bubble total")


def scene9(img, t):
    """penutup: satu motor, harganya bisa dua; tim nabung vs tim kredit, bela di komentar."""
    p = pop(t, SC[9] + 0.05)
    if p > 0:
        T, td = card(800, 300, fill=NAVY)
        G = motor_img(250, True); M = motor_img(250)
        T.alpha_composite(G, (330, 30)); T.alpha_composite(M, (520, 40))
        td.text((50, 95), "1 motor", font=F("pb", 60), fill=WHITE, anchor="lm")
        hot = t >= cs(46)
        f = F("pb", 54); s_ = "harga 2"
        if hot:
            td.rounded_rectangle((36, 165, 60 + f.getlength(s_) + 10, 250), 16, fill=YEL)
        td.text((50, 207), s_, font=f, fill=NAVY if hot else WHITE, anchor="lm")
        paste_c(img, T, W / 2, 620, p, tag="kartu 1 motor")
    for k, (s, col, t0) in enumerate((("TIM NABUNG", TEAL, cs(47)), ("TIM KREDIT", RED, cs(48) + 0.1))):
        p = pop(t, t0)
        if p <= 0: continue
        beat = 1 + 0.04 * math.sin((t - t0) * 7 + k * math.pi)
        paste_c(img, pill(s, fill=col, fg=WHITE, size=50, h=110), W / 2, 900 if k == 0 else 1080, p * beat,
                -2 if k == 0 else 2, tag=s)
    if t >= cs(48) + 0.1:
        text_c(ImageDraw.Draw(img), (W / 2, 990), "vs", F("pb", 44), NAVY)
    p = pop(t, cs(49) - 0.05)
    if p > 0:
        B = Image.new("RGBA", (800, 240), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 800, 190), 34, fill=WHITE, outline=NAVY, width=5)
        bd.polygon([(110, 186), (180, 186), (90, 236)], fill=WHITE, outline=NAVY)
        bd.line([(112, 189), (178, 189)], fill=WHITE, width=8)
        text_c(bd, (400, 70), "Bela di komentar!", F("pb", 52), NAVY)
        text_c(bd, (400, 138), "like terbanyak tampil di #8 + namamu", F("pm", 30), GREY_T)
        paste_c(img, B, W / 2, 1310, p, tag="bubble bela")
    if t >= SC[9] + 0.3:   # PRB-39: disclaimer di layar penutup
        text_c(ImageDraw.Draw(img), (W / 2, 1490), "Bukan saran keuangan", F("pm", 30), INK)


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9]


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
            if (tag not in ("aru", "motor", "motor bayangan", "bocor") and nw > MAXW + 0.5) or x0 < XMIN - 0.5 or x1 > XMAX + 0.5:
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
    for i in (4, 10, 11, 13, 14, 16, 18, 20, 21, 24, 25, 27, 28, 32, 36, 37, 42, 43, 44, 47, 48, 49):
        ev.append({"t": cs(i), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": cs(29), "sfx": "cring", "gain": 0.45})
    ev.append({"t": cs(30) + 0.1, "sfx": "ding", "gain": 0.35})
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

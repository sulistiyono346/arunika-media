"""Renderer ARN-53 "Kok nyamuk lebih suka gigit kamu daripada temanmu?" — Flat 2D latar terang (#F2F4F7).
Adaptasi render_flat_ngantuk.py (helper kartu, pill, stempel, bubble, Aru, logo, subtitle, cek area aman, sfx):
- frame 0 (PRB-34/36/46): satu adegan + satu aksi — kamar terang, empat tikar berjajar, tiga teman tidur pulas
  (label kecil abu "0"), cuma Aru yang terjaga, menggaruk, dikitari satu nyamuk besar; counter bentol di Aru
  0 -> 7 mulai dtk 0,5, nilai akhir 7 di dtk 2,0 dan ditahan sampai akhir adegan close-up (dtk ~6,5).
  Dtk 1,5 visual berganti: zoom ke Aru + lengan bentol + bubble "darah manis?". Judul layar hanya pill kecil
  di atas (bukan kartu judul besar); tanpa logo / label seri / progress bar di dtk 0-3 (progress bar mulai 3,5).
- 11 layar (frame 0 + close-up = adegan pembuka, lalu 9 adegan; tiap <= 6 dtk); sumber kecil di layar (PRB-39);
  puncak "100×" dengan counter 1 -> 100 yang berhenti & ditahan >= 1,5 dtk + teks layar ajakan kirim (PRB-55);
  "informasi umum, bukan saran medis" di adegan tindakan; follow dtk 10,6-15 (PRB-4); penutup logo <= 1,5 dtk.
- area aman (PRB-41): semua pill/bubble/kartu <= 800 px dan di x 130..950; `check` memindai tiap 0,1 dtk.
Pemakaian (dari folder kerja sore/build/nyamuk, setelah align_nyamuk.py -> timing.json):
  TOTAL=54.4 python3 ../../render_flat_nyamuk.py events | check | scenes | counters | stills 0,2,... | video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, NAVY, TEAL, YEL, WHITE, GREY_T, RED)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "54.4"))
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
GREEN = (46, 160, 110); INK = (60, 66, 92); LIGHT = (232, 238, 246); SKIN = (254, 211, 176)
MAT = (236, 214, 170); MAT_D = (206, 178, 128); BUMP = (226, 70, 70)
MAXW, XMIN, XMAX = 800, 130, 950   # PRB-41

TIM = json.load(open("timing.json"))
def cs(i): return TIM[i]["start"] + LEAD
def ce(i): return TIM[i]["end"] + LEAD
def seg0(s):   # chunk pertama segmen s
    return next(i for i, c in enumerate(TIM) if c["seg"] == s)
def chunk_of(text):
    return next(i for i, c in enumerate(TIM) if c["text"] == text)

ZOOM_T = 1.5                    # visual berganti dtk ~1,5 (zoom ke lengan Aru)
SCENE_SEG = [0, None, 4, 7, 10, 12, 15, 17, 20, 23, 26]
SCENE_OFF = {3: 0.05}           # adegan 3 mulai sedikit lebih lambat supaya adegan 3 <= 6 dtk
SC = [0.0, ZOOM_T] + [cs(seg0(s)) - SCENE_OFF.get(k, 0.25) for k, s in enumerate(SCENE_SEG) if k > 1] + [TOTAL]
NS = len(SCENE_SEG)
FOLLOW = (10.6, 15.0)           # PRB-4: ajakan follow teks kecil dtk 10-15
PB_START = 3.5                  # progress bar mulai dtk 3,5
NOTES = {3: ("Cameron Webb, Univ. Sydney · The Conversation, Des 2012",),
         4: ("Current Biology, Jul 2015",),
         5: ("Cell, Okt 2022",),
         6: ("Cell, Okt 2022 · studi kecil: 8 orang + 56 orang uji tambahan",),
         7: ("J Med Entomol 2004 · Acta Tropica 2014",),
         9: ("WHO, Agu 2025 · informasi umum, bukan saran medis",)}
BITE0, BITE1, BITES = 0.5, 2.0, 7          # counter bentol 0 -> 7 (PRB-29/46), nilai akhir di dtk 2,0
T100 = cs(chunk_of("100× LIPAT")) - 0.15    # counter 1 -> 100 (puncak)
T100_END = T100 + 1.0
SHARE = (T100 - 0.1, SC[7] - 0.2)           # ajakan kirim di puncak angka (PRB-55 poin 3)


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
# posisi bentol di Aru (koordinat gambar asli 900x1200): lengan kanan, lengan kiri terangkat, kepala
BUMP_XY = [(652, 832), (232, 612), (612, 262), (668, 878), (270, 668), (300, 285), (642, 470)]


def bites_at(t):
    return int(clamp((t - BITE0) / (BITE1 - BITE0)) * BITES + 1e-9)


@lru_cache(None)
def aru_face(n=0, kind="normal"):
    """n bentol merah di lengan & kepala; kind: normal | sniff (mata terpejam, senyum)."""
    im = ARU_RAW.copy(); d = ImageDraw.Draw(im)
    if kind == "sniff":
        for x0 in (330, 486):
            d.ellipse((x0, 360, x0 + 84, 456), fill=SKIN)
        for x0 in (340, 496):
            d.arc((x0, 384, x0 + 66, 432), 195, 345, fill=NAVY, width=12)
    for (x, y) in BUMP_XY[:n]:
        d.ellipse((x - 22, y - 22, x + 22, y + 22), fill=(250, 160, 150))
        d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=BUMP)
    return im.crop(ARU_BOX)


@lru_cache(None)
def aru_h(h, n=0, kind="normal"):
    A = aru_face(n, kind); r = h / A.height
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


def draw_aru(layer, cx, bottom, h, t, n=0, kind="normal", angle_amp=2.0, extra=0.0, bob=7):
    im = aru_h(h, n, kind)
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


def icon_x(d, cx, cy, s=1.0, col=RED):
    d.ellipse((cx - 40 * s, cy - 40 * s, cx + 40 * s, cy + 40 * s), fill=col)
    k = 15 * s
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=WHITE, width=int(10 * s))
    d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=WHITE, width=int(10 * s))


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


FLOOR_Y = 960
MATS = [185, 420, 660, 895]     # empat tikar berjajar; Aru di tikar ke-2
@lru_cache(None)
def bg_room():
    """frame 0: kamar terang, lampu menyala, lantai kayu muda, empat tikar."""
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.rectangle((0, FLOOR_Y, W, H), fill=(234, 226, 212))
    d.line([(0, FLOOR_Y), (W, FLOOR_Y)], fill=(210, 200, 182), width=6)
    d.rounded_rectangle((820, 470, 1000, 720), 16, fill=(222, 236, 248), outline=(200, 208, 222), width=6)  # jendela
    d.line([(910, 470), (910, 720)], fill=(200, 208, 222), width=6)
    d.line([(540, 380), (540, 430)], fill=(190, 196, 210), width=5)                                       # lampu
    d.chord((480, 410, 600, 500), 180, 360, fill=YEL, outline=NAVY, width=5)
    for cx in MATS:
        d.rounded_rectangle((cx - 105, 1010, cx + 105, 1560), 22, fill=MAT, outline=MAT_D, width=6)
        for y in range(1050, 1540, 46):
            d.line([(cx - 95, y), (cx + 95, y)], fill=MAT_D, width=3)
    return img


@lru_cache(None)
def bg_rest():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((90, 480, 990, 1380), fill=(255, 246, 232))
    d.rectangle((0, 1490, W, H), fill=(226, 230, 237))
    return img


@lru_cache(None)
def header():
    """pill kecil judul layar (kolom Judul layar), y≈300 (PRB-41); KAMU disorot kuning."""
    f = F("pb", 38); s1 = "Nyamuk, kok pilih "; s2 = "KAMU"; s3 = "?"
    w1, w2, w3 = f.getlength(s1), f.getlength(s2), f.getlength(s3)
    padx, kp = 30, 14
    tot = w1 + w2 + 2 * kp + w3 + 2 * padx + 6
    assert tot <= MAXW
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


@lru_cache(None)
def mosq_img(s, wing):
    """nyamuk Aedes flat: badan hitam belang putih, sayap transparan mengepak (wing 0..3), belalai panjang."""
    S = 240
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    dark = (40, 44, 60)
    for k, (x0, y0) in enumerate([(100, 130), (120, 132), (140, 130)]):          # kaki
        d.line([(x0, y0), (x0 - 30 + 30 * k, y0 + 60), (x0 - 40 + 40 * k, y0 + 96)], fill=dark, width=5)
    d.ellipse((86, 104, 206, 146), fill=dark, outline=NAVY, width=4)              # perut
    for x in (120, 146, 172):
        d.line([(x, 108), (x - 4, 142)], fill=WHITE, width=6)
    d.ellipse((62, 98, 106, 138), fill=dark, outline=NAVY, width=4)               # dada
    d.ellipse((34, 100, 70, 132), fill=dark, outline=NAVY, width=4)               # kepala
    d.ellipse((42, 106, 56, 120), fill=(220, 60, 60))                             # mata
    d.line([(38, 120), (0, 150)], fill=dark, width=5)                             # belalai
    flap = [0, 20, 40, 20][wing % 4]
    wl = Image.new("RGBA", (S, S), (0, 0, 0, 0)); wd = ImageDraw.Draw(wl)
    wd.ellipse((70, 30 + flap, 170, 110), fill=(190, 220, 245, 170), outline=(120, 150, 190, 230), width=4)
    wd.ellipse((90, 20 + flap * 1.2, 200, 100), fill=(200, 228, 250, 150), outline=(120, 150, 190, 230), width=4)
    im = Image.alpha_composite(wl, im)
    im = trim(im)
    r = s / im.width
    return im.resize((int(im.width * r), max(1, int(im.height * r))), Image.LANCZOS)


def draw_mosq(img, cx, cy, s, t, flip=False, alpha=1.0):
    m = mosq_img(int(s), int(t * 40) % 4)
    if flip: m = m.transpose(Image.FLIP_LEFT_RIGHT)
    paste_c(img, m, cx, cy, 1.0, 6 * math.sin(t * 7), alpha)


def sleeper(d, cx, top, hair, blanket, t, k):
    """teman tidur pulas (tampak atas) di tikar: bantal, kepala, selimut."""
    d.rounded_rectangle((cx - 80, top, cx + 80, top + 90), 26, fill=WHITE, outline=(200, 206, 222), width=5)
    d.ellipse((cx - 56, top + 4, cx + 56, top + 116), fill=SKIN, outline=NAVY, width=6)
    d.chord((cx - 56, top + 4, cx + 56, top + 90), 180, 360, fill=hair, outline=NAVY, width=6)
    for ex in (-22, 22):
        d.arc((cx + ex - 14, top + 66, cx + ex + 14, top + 86), 20, 160, fill=NAVY, width=5)
    br = 4 * math.sin(t * 2.2 + k)                                         # napas naik-turun
    d.rounded_rectangle((cx - 95, top + 110 - br, cx + 95, top + 470), 34, fill=blanket, outline=NAVY, width=6)
    d.line([(cx - 95, top + 170 - br), (cx + 95, top + 170 - br)], fill=WHITE, width=8)


def zzz(d, x, y, t, size=40, col=NAVY):
    for k in range(3):
        u = (t * 0.7 + k / 3) % 1.0
        f = F("pb", int(size * (0.7 + 0.5 * u)))
        a = int(255 * min(1, (1 - u) * 2))
        d.text((x + 40 * u + 18 * k, y - 100 * u), "z", font=f, fill=col + (a,), anchor="mm")


@lru_cache(None)
def counter_card(n, big=False):
    """counter bentol Aru (merah) — angka ilustrasi di dalam adegan, bukan data."""
    w, h = (330, 250) if big else (250, 190)
    C, cd = card(w, h, fill=WHITE, outline=RED, ow=7)
    text_c(cd, (w / 2, h * 0.42), str(n), F("pb", 150 if big else 112), RED)
    text_c(cd, (w / 2, h * 0.84), "BENTOL", F("pb", 40 if big else 32), NAVY)
    return C


@lru_cache(None)
def zero_badge():
    C, cd = card(100, 86, fill=(236, 239, 244), outline=(176, 182, 198), ow=4, r=24)
    text_c(cd, (50, 43), "0", F("pb", 56), (150, 156, 172))
    return C


def blood_drop(d, cx, cy, r, col=RED, label=None, fsize=60):
    d.polygon([(cx, cy - 1.9 * r), (cx - 0.86 * r, cy - 0.5 * r), (cx + 0.86 * r, cy - 0.5 * r)], fill=col)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    d.line([(cx, cy - 1.9 * r), (cx - 0.9 * r, cy - 0.42 * r)], fill=NAVY, width=6)
    d.line([(cx, cy - 1.9 * r), (cx + 0.9 * r, cy - 0.42 * r)], fill=NAVY, width=6)
    d.arc((cx - r, cy - r, cx + r, cy + r), -20, 200, fill=NAVY, width=6)
    d.ellipse((cx - 0.5 * r, cy - 0.5 * r, cx - 0.2 * r, cy - 0.1 * r), fill=(255, 170, 160))
    if label:
        text_c(d, (cx, cy + 0.1 * r), label, F("pb", fsize), WHITE)


def co2_puff(d, cx, cy, s, a):
    col = (190, 205, 225, int(255 * a))
    for dx, dy, rr in ((-30, 0, 36), (14, -14, 42), (52, 4, 32)):
        d.ellipse((cx + (dx - rr) * s, cy + (dy - rr) * s, cx + (dx + rr) * s, cy + (dy + rr) * s), fill=col)
    d.text((cx + 12 * s, cy - 4 * s), "CO2", font=F("pb", int(30 * s)), fill=NAVY + (int(255 * a),), anchor="mm")


# ---------- adegan ----------
def scene0(img, t):
    """frame 0: kamar berempat, tiga teman tidur pulas (0), Aru terjaga menggaruk, dikitari nyamuk; 0 -> 7."""
    d = ImageDraw.Draw(img)
    hair = [(70, 52, 40), None, (40, 40, 48), (120, 72, 40)]
    blank = [(120, 170, 220), None, (240, 150, 130), (150, 200, 150)]
    for k, cx in enumerate(MATS):
        if k == 1: continue
        sleeper(d, cx, 1030, hair[k], blank[k], t, k)
        paste_c(img, zero_badge(), cx, 920, 1.0, tag="label 0")
        zzz(d, cx + 60, 1010, t + k * 0.3, size=34)
    n = bites_at(t)
    ax = MATS[1]
    scratch = 4 * math.sin(t * 22)                                  # menggaruk (lengan kiri terangkat)
    draw_aru(img, ax, 1500, 560, t, n=n, angle_amp=1.5, extra=scratch, bob=4)
    # nyamuk besar mengitari kepala Aru saja
    a = t * 3.6
    draw_mosq(img, ax + 210 * math.cos(a), 1080 + 120 * math.sin(a), 150, t, flip=math.sin(a) < 0)
    # counter bentol Aru
    if t >= BITE0 - 0.2:
        q = pop(t, BITE0 - 0.2, 0.3)
        bump = 1 + 0.12 * clamp(1 - ((t - BITE0) % ((BITE1 - BITE0) / BITES)) / 0.12) if t < BITE1 + 0.05 else 1
        paste_c(img, counter_card(n), ax + 10, 700, q * bump, -3, tag="counter bentol")


def scene1(img, t):
    """zoom ke Aru: lengan & kepala penuh bentol, counter besar 7, bubble "darah manis?"."""
    n = bites_at(t)
    draw_aru(img, 470, 2060, 1240, t, n=n, angle_amp=1.0, extra=3 * math.sin(t * 20), bob=3)
    a = t * 3.0
    draw_mosq(img, 640 + 250 * math.cos(a), 760 + 90 * math.sin(a), 220, t, flip=math.sin(a) < 0)
    bump = 1 + 0.12 * clamp(1 - ((t - BITE0) % ((BITE1 - BITE0) / BITES)) / 0.12) if t < BITE1 + 0.05 else 1
    paste_c(img, counter_card(n, big=True), 760, 560, bump, 4, tag="counter bentol")
    paste_c(img, pill("teman sekamar: 0", fill=(236, 239, 244), fg=(130, 136, 152), size=34,
                      outline=(176, 182, 198)), 330, 470, pop(t, ZOOM_T + 0.1), -2, tag="pill teman 0")
    q = pop(t, ZOOM_T + 0.15)
    if q > 0:
        B = bubble("darah manis?", col=YEL, fg=NAVY, size=54, tail="left")
        paste_c(img, B, 380, 620 + 6 * math.sin(t * 3), q, 3, tag="bubble darah manis")
    r = pop(t, cs(seg0(2)))
    if r > 0:
        paste_c(img, pill_emoji("KATANYA…", "🍬", fill=NAVY, fg=WHITE, size=44), 330, 810, r, -4, tag="pill katanya")


def scene2(img, t):
    """Aru mengangkat dua kartu tebakan: darah manis? atau…; lalu mencium lengannya sendiri."""
    p = pop(t, SC[2] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Coba TEBAK", "🤔", fill=YEL, fg=NAVY, size=60), W / 2, 470, p, -2, tag="pill tebak")
    sniff_t = cs(chunk_of("KAMU PENGIN CIUM"))
    sniff = t >= sniff_t
    draw_aru(img, W / 2, 1520, 470, t, n=7, kind="sniff" if sniff else "normal", extra=-8 if sniff else 0)
    cards = [("🍬", "DARAH MANIS?", 310, cs(seg0(5)) - 0.1, -8), ("❓", "ATAU…", 770, cs(seg0(5)) + 0.35, 8)]
    for k, (em, lab, x, t0, ang) in enumerate(cards):
        q = pop(t, t0)
        if q <= 0: continue
        big = k == 1 and sniff
        C, cd = card(330, 330, fill=WHITE, outline=NAVY if not big else RED, ow=7 if big else 5)
        C.alpha_composite(emoji_img(em, 160), (int(165 - emoji_img(em, 160).width / 2), 40))
        text_c(cd, (165, 280), lab, fit("pb", 42, lab, 300), RED if big else NAVY)
        s = q * (1.12 + 0.05 * math.sin(t * 9) if big else 1.0)
        paste_c(img, C, x, 770 + 10 * math.sin(t * 3 + k), s, ang + 3 * math.sin(t * 2 + k), tag="kartu tebak")
    if sniff:
        paste_c(img, pill_emoji("cium lenganmu", "👃", fill=NAVY, fg=WHITE, size=44), W / 2, 990,
                pop(t, sniff_t), 2, tag="pill cium")


def scene3(img, t):
    """papan tersangka: tetes darah manis (gula) -> kata ahli serangga -> stempel MITOS."""
    p = pop(t, SC[3] + 0.02)
    if p > 0:
        T, td = head_card(800, 640, "PAPAN TERSANGKA", col=RED, size=46)
        td.rectangle((24, 110, 776, 620), fill=(226, 230, 238))
        for k in range(7):
            y = 160 + k * 66
            td.line([(24, y), (776, y)], fill=(196, 202, 216), width=4)
            td.text((40, y), f"{180 - k * 10}", font=F("pm", 24), fill=(150, 156, 172), anchor="lm")
        u = eout((t - SC[3] - 0.15) / 0.8)
        blood_drop(td, 400, 330 + 200 * (1 - u), 90, label="")
        for k, (sx, sy) in enumerate(((520, 230), (560, 300), (250, 280))):     # kubus gula
            if u > 0.6:
                td.rounded_rectangle((sx, sy, sx + 54, sy + 54), 8, fill=WHITE, outline=NAVY, width=4)
        if u > 0.95:
            td.rounded_rectangle((170, 510, 630, 596), 16, fill=NAVY)
            text_c(td, (400, 553), "DARAH MANIS", F("pb", 48), YEL)
        paste_c(img, T, W / 2, 820, p, tag="papan tersangka")
    q = pop(t, cs(seg0(8)))
    if q > 0:
        T, td = card(800, 170, fill=WHITE, outline=TEAL, ow=6)
        T.alpha_composite(emoji_img("🔬", 96), (40, 34))
        td.text((170, 62), "Kata ahli serangga", font=F("pb", 44), fill=NAVY, anchor="lm")
        td.text((170, 118), "Cameron Webb, Univ. Sydney", font=F("pm", 34), fill=GREY_T, anchor="lm")
        paste_c(img, T, W / 2, 1300, q, tag="kartu ahli")
    r = pop(t, cs(seg0(9)) + 0.1)
    if r > 0:
        paste_c(img, stamp("MITOS!", col=RED, size=96), W / 2, 830, r * (1 + 0.03 * math.sin(t * 9)), -10,
                tag="stempel mitos")


def scene4(img, t):
    """yang dicium duluan: napas (CO2) Aru melayang ke nyamuk jauh; jarak 10-50 m."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[4] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Dicium duluan: NAPASMU", "💨", fill=YEL, fg=NAVY, size=48), W / 2, 470, p, -2,
                tag="pill napas")
    draw_aru(img, 290, 1440, 500, t, n=7, angle_amp=1.5)
    for k in range(5):                                                   # embusan CO2 melayang ke kanan
        u = ((t - SC[4]) * 0.35 + k / 5) % 1.0
        if t - SC[4] < k * 0.5: continue
        co2_puff(d, 400 + 460 * u, 1000 - 160 * u + 20 * math.sin(t * 2 + k), 0.8 + 0.5 * u,
                 min(1, (1 - u) * 2.2) * min(1, u * 6))
    mx = 800 + 30 * math.sin(t * 2)
    draw_mosq(img, mx, 760 + 30 * math.sin(t * 3), 170, t, flip=True)
    q = pop(t, cs(seg0(11)) - 0.1)
    if q > 0:
        dashed(d, [(300, 1220), (820, 1220)], NAVY, w=6, on=22, off=14)
        arrow(d, 760, 1220, 830, 1220, NAVY, w=8, head=26); arrow(d, 360, 1220, 290, 1220, NAVY, w=8, head=26)
        paste_c(img, pill("10–50 m", fill=RED, fg=WHITE, size=60), 560, 1220, q, -2, tag="pill jarak")


def scene5(img, t):
    """semua orang bernapas (CO2 sama) -> pembedanya di kulit: asam dari minyak kulit (kaca pembesar)."""
    d = ImageDraw.Draw(img)
    t_skin = cs(seg0(13))
    if t < t_skin:
        p = pop(t, SC[5] + 0.05)
        T, td = head_card(800, 520, "SEMUA ORANG BERNAPAS", col=TEAL, size=44)
        for k, (cx, hair) in enumerate(((150, (70, 52, 40)), (400, None), (650, (40, 40, 48)))):
            if hair is None:
                A = aru_h(300, 7); T.alpha_composite(A, (int(cx - A.width / 2), 190))
            else:
                td.ellipse((cx - 85, 220, cx + 85, 390), fill=SKIN, outline=NAVY, width=6)
                td.chord((cx - 85, 220, cx + 85, 330), 180, 360, fill=hair, outline=NAVY, width=6)
                for ex in (-30, 30):
                    td.ellipse((cx + ex - 9, 300, cx + ex + 9, 320), fill=NAVY)
                td.rounded_rectangle((cx - 70, 400, cx + 70, 500), 30, fill=(120, 170, 220), outline=NAVY, width=6)
            co2_puff(td, cx + 50, 160 + 10 * math.sin(t * 3 + k), 0.7, 1.0)
        paste_c(img, T, W / 2, 900, p, tag="kartu semua bernapas")
        q = pop(t, cs(chunk_of("BERNAPAS, KAN?")))
        if q > 0:
            paste_c(img, pill("CO2 = SAMA", fill=NAVY, fg=YEL, size=52), W / 2, 1280, q, 2, tag="pill sama")
        return
    p = pop(t, t_skin)
    paste_c(img, pill_emoji("Pembedanya di KULIT", "🧐", fill=YEL, fg=NAVY, size=50), W / 2, 470, p, -2,
            tag="pill kulit")
    L = Image.new("RGBA", (640, 640), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    ld.ellipse((20, 20, 620, 620), fill=(252, 214, 182), outline=NAVY, width=14)
    for k in range(9):                                                   # pori + tetes minyak kulit
        a = k * 2.4; rr = 60 + 200 * ((k * 0.37) % 1)
        x = 320 + rr * math.cos(a); y = 320 + rr * math.sin(a)
        ld.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(214, 160, 130))
        g = 0.5 + 0.5 * math.sin(t * 4 + k)
        ld.ellipse((x + 12, y - 30 - 6 * g, x + 46, y + 4 - 6 * g), fill=(255, 214, 90), outline=(200, 140, 20), width=4)
    L.info["nw"] = 640
    paste_c(img, L, 470, 960, p, 0, tag="kaca pembesar")
    ImageDraw.Draw(img).line([(700, 1190), (850, 1340)], fill=NAVY, width=40)
    q = pop(t, cs(seg0(14)))
    if q > 0:
        paste_c(img, pill("ASAM dari minyak kulit", fill=RED, fg=WHITE, size=44), W / 2, 1360, q, -2, tag="pill asam")
    draw_mosq(img, 820 + 20 * math.sin(t * 3), 620 + 20 * math.cos(t * 2), 140, t, flip=True)


def count100(t):
    if t < T100: return 1
    u = eout((t - T100) / (T100_END - T100))
    return max(1, int(round(1 + 99 * u)))


def scene6(img, t):
    """PUNCAK: counter besar 1x -> 100x (berhenti & ditahan), terfavorit vs paling aman + ajakan kirim."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[6] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("SATU STUDI", "🔬", fill=NAVY, fg=WHITE, size=50), W / 2, 470, p, -2, tag="pill studi")
    v = count100(t)
    done = t >= T100_END
    T, td = card(640, 300, fill=WHITE, outline=RED, ow=8)
    text_c(td, (320, 140), f"{v}×", F("pb", 190), RED)
    text_c(td, (320, 262), "LEBIH MENARIK", F("pb", 40), NAVY)
    beat = 1 + (0.06 * back(clamp((t - T100_END) / 0.3)) * clamp(1 - (t - T100_END) / 0.6) if done else 0)
    paste_c(img, T, W / 2, 720, pop(t, SC[6] + 0.15) * beat, -2, tag="counter 100x")
    q = pop(t, SC[6] + 0.4)
    if q > 0:
        for k, (x, lab, col, nm) in enumerate(((330, "TERFAVORIT", RED, 6), (750, "PALING AMAN", GREEN, 1))):
            C, cd = card(380, 300, fill=WHITE, outline=col, ow=6)
            cd.rounded_rectangle((0, 0, 380, 70), 30, fill=col); cd.rectangle((0, 40, 380, 70), fill=col)
            cd.rounded_rectangle((0, 0, 380, 300), 30, outline=NAVY, width=5)
            text_c(cd, (190, 36), lab, F("pb", 36), WHITE)
            cd.ellipse((140, 130, 240, 230), fill=SKIN, outline=NAVY, width=6)
            for j in range(nm):
                a = t * 3 + j * 2 * math.pi / max(nm, 1)
                m = mosq_img(70, int(t * 40 + j) % 4)
                C.alpha_composite(m, (int(190 + 120 * math.cos(a) - m.width / 2),
                                      int(180 + 70 * math.sin(a) - m.height / 2)))
            paste_c(img, C, x, 1090, q, -2 if k == 0 else 2, tag="kartu " + lab)


def share_card(img, t):
    """ajakan kirim sebagai teks layar di puncak angka 100x (PRB-55 poin 3)."""
    if not (SHARE[0] <= t < SHARE[1]): return
    a = min(clamp((t - SHARE[0]) / 0.25), clamp((SHARE[1] - t) / 0.25))
    s = 0.85 + 0.15 * back((t - SHARE[0]) / 0.35)
    T, td = card(800, 170, fill=TEAL)
    e = emoji_img("📤", 70)
    T.alpha_composite(e, (40, 50))
    td.text((140, 56), "Kirim ke teman yang selalu", font=F("pb", 42), fill=WHITE, anchor="lm")
    td.text((140, 118), "jadi korban nyamuk", font=F("pb", 52), fill=YEL, anchor="lm")
    paste_c(img, T, W / 2, 1405 + 4 * math.sin(t * 5), s, 0, a, tag="kartu kirim")


def scene7(img, t):
    """golongan darah O: huruf O besar di tetes darah + dua kartu studi saling silang (✓ vs ✗)."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[7] + 0.05)
    if p > 0:
        L = Image.new("RGBA", (360, 440), (0, 0, 0, 0))
        blood_drop(ImageDraw.Draw(L), 180, 280, 140, label="O", fsize=170)
        L.info["nw"] = 300
        paste_c(img, L, W / 2, 700, p * (1 + 0.02 * math.sin(t * 5)), 0, tag="tetes O")
    items = [(cs(seg0(18)), "Studi 2004", "O lebih sering dihinggapi", True, 1040, -3),
             (cs(seg0(19)), "Studi 2014", "malah sebaliknya", False, 1250, 3)]
    for t0, a, b, ok, y, ang in items:
        q = pop(t, t0)
        if q <= 0: continue
        C, cd = card(800, 170, fill=WHITE, outline=GREEN if ok else RED, ow=6)
        (icon_check if ok else icon_x)(cd, 80, 85, 1.0)
        cd.text((150, 58), a, font=F("pb", 46), fill=NAVY, anchor="lm")
        cd.text((150, 118), b, font=F("pm", 38), fill=GREY_T, anchor="lm")
        paste_c(img, C, W / 2, y, q, ang, tag="kartu studi")
    r = pop(t, cs(seg0(19)) + 0.6)
    if r > 0:
        paste_c(img, stamp("BUKTI LEMAH", col=RED, size=50), 730, 500, r, 8, tag="stempel lemah")


def scene8(img, t):
    """tim darah manis setengah benar: kamu (kulitmu) ✓, darahnya ✗."""
    p = pop(t, SC[8] + 0.05)
    if p > 0:
        paste_c(img, pill("SETENGAH BENAR", fill=YEL, fg=NAVY, size=60), W / 2, 470, p, -2, tag="pill setengah")
    cols = [(330, "KAMU", "kulitmu", GREEN, True, cs(seg0(21))), (750, "DARAHNYA", "bukan", RED, False, cs(seg0(22)))]
    for j, (x, lab, sub, col, ok, t0) in enumerate(cols):
        q = pop(t, SC[8] + 0.3 + 0.15 * j)
        if q <= 0: continue
        C, cd = card(380, 560, fill=WHITE, outline=col, ow=7)
        cd.rounded_rectangle((0, 0, 380, 100), 30, fill=col); cd.rectangle((0, 60, 380, 100), fill=col)
        cd.rounded_rectangle((0, 0, 380, 560), 30, outline=NAVY, width=5)
        text_c(cd, (190, 52), lab, F("pb", 48), WHITE)
        if ok:
            A = aru_h(300, 7); C.alpha_composite(A, (int(190 - A.width / 2), 130))
            for k in range(3):
                m = mosq_img(60, int(t * 40 + k) % 4)
                a = t * 3 + k * 2.1
                C.alpha_composite(m, (int(190 + 140 * math.cos(a) - 30), int(230 + 60 * math.sin(a) - 20)))
        else:
            blood_drop(cd, 190, 330, 90)
        text_c(cd, (190, 480), sub, F("pb", 44), NAVY)
        if t >= t0:
            (icon_check if ok else icon_x)(cd, 320, 160, 1.0)
        paste_c(img, C, x, 920, q, -2 if j == 0 else 2, tag="kolom " + lab)
    r = pop(t, cs(chunk_of("LEBIH MENGGODA,")))
    if r > 0:
        paste_c(img, bubble("lebih menggoda", col=NAVY, fg=YEL, size=48, tail="left"), 400,
                1300, r, -2, tag="bubble menggoda")


def scene9(img, t):
    """yang bisa diubah malam ini: lotion antinyamuk, baju panjang, kelambu (+ bukan saran medis)."""
    p = pop(t, SC[9] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("BISA DIUBAH MALAM INI", "✅", fill=YEL, fg=NAVY, size=50), W / 2, 470, p, -2,
                tag="pill bisa diubah")
    rows = [(cs(seg0(24)), "🧴", "Lotion antinyamuk", "DEET · picaridin · IR3535", 720),
            (cs(chunk_of("BAJU PANJANG,")), "👕", "Baju panjang", "tutup kulit", 960),
            (cs(chunk_of("DAN KELAMBU.")), "🛏️", "Kelambu & kasa jendela", "halangi nyamuk", 1200)]
    if t < rows[0][0] - 0.1:                                            # malam ini (sebelum kartu pertama)
        paste_c(img, emoji_img("🌙", 260), W / 2, 900 + 8 * math.sin(t * 3), pop(t, SC[9] + 0.2), -6)
    for k, (t0, em, a, b, y) in enumerate(rows):
        q = pop(t, t0 - 0.1)
        if q <= 0: continue
        C, cd = card(800, 190, fill=WHITE, outline=GREEN, ow=6)
        e = emoji_img(em, 110); C.alpha_composite(e, (int(95 - e.width / 2), 40))
        cd.text((190, 70), a, font=fit("pb", 46, a, 580), fill=NAVY, anchor="lm")
        cd.text((190, 132), b, font=F("pm", 36), fill=GREY_T, anchor="lm")
        icon_check(cd, 730, 95, 0.8)
        paste_c(img, C, W / 2, y, q, 0, tag="kartu tindakan")


def scene10(img, t):
    """penutup: layar dibagi dua, tim KORBAN 🦟 vs tim AMAN 😴; 'Komen 1 kata'."""
    d = ImageDraw.Draw(img)
    t_k = cs(chunk_of("KORBAN NYAMUK,")); t_a = cs(chunk_of("TIDUR AMAN?"))
    cols = [(140, 530, RED, "KORBAN", "🦟", "korban nyamuk", t_k, t_a),
            (550, 940, TEAL, "AMAN", "😴", "tidur aman", t_a, TOTAL)]
    y0, y1 = 470, 1250
    for j, (x0, x1, col, lab, em, sal, a0, a1) in enumerate(cols):
        act = a0 <= t < a1 or t < t_k
        p = pop(t, SC[10] + 0.05 + 0.12 * j)
        if p <= 0: continue
        C = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
        cd.rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), 30, fill=WHITE if act else (232, 235, 242),
                             outline=col if act else (200, 205, 216), width=7)
        cd.rounded_rectangle((0, 0, x1 - x0 - 1, 150), 30, fill=col if act else (190, 196, 210))
        cd.rectangle((0, 100, x1 - x0 - 1, 150), fill=col if act else (190, 196, 210))
        text_c(cd, ((x1 - x0) / 2, 44), "TIM", F("pb", 34), WHITE)
        text_c(cd, ((x1 - x0) / 2, 104), lab, F("pb", 58), WHITE)
        e = emoji_img(em, 230)
        C.alpha_composite(e, (int((x1 - x0) / 2 - e.width / 2), 260))
        text_c(cd, ((x1 - x0) / 2, 620), sal, F("pb", 42), NAVY if act else GREY_T)
        C.info["nw"] = x1 - x0
        beat = 1 + (0.03 * math.sin(t * 8) if (a0 <= t < a1) else 0)
        paste_c(img, C, (x0 + x1) / 2, (y0 + y1) / 2, p * beat, -1.5 if j == 0 else 1.5, tag="kolom " + lab)
    if t >= SC[10] + 0.2:
        d.ellipse((540 - 48, 860 - 48, 540 + 48, 860 + 48), fill=YEL, outline=NAVY, width=6)
        text_c(d, (540, 858), "vs", F("pb", 42), NAVY)
    p = pop(t, t_k - 0.2)
    if p > 0:
        B, bd = card(800, 150, fill=YEL, outline=NAVY)
        text_c(bd, (400, 50), "Tim KORBAN atau tim AMAN?", fit("pb", 50, "Tim KORBAN atau tim AMAN?", 740), NAVY)
        text_c(bd, (400, 112), "Komen 1 kata", F("pb", 42), NAVY)
        paste_c(img, B, W / 2, 1385, p, tag="kartu komen")


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10]
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
        img = bg_room().copy()
        scene0(img, t)
    else:
        img = (bg_room() if k == 1 else bg_rest()).copy()
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        SCENES[k](layer, t)
        s = (0.80 + 0.20 * eout(ts / 0.3)) if k == 1 else 0.94 + 0.06 * back(ts / 0.4)   # adegan 1: zoom masuk
        if s < 0.999 or s > 1.001:
            paste_c(img, layer, W / 2, H / 2, s)
        else:
            img.alpha_composite(layer)
    Hd, hx0, hx1 = header()
    img.alpha_composite(Hd, (0, 236))      # pill kecil judul layar, y≈300 (PRB-41); bukan kartu judul besar
    track("pill judul", hx1 - hx0, hx0, hx1)
    share_card(img, t)
    draw_sub(img, t)
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
    bad = {}; widest = {}
    n = int(TOTAL / step)
    for j in range(n + 1):
        t = min(TOTAL - 0.01, j * step)
        frame(t)
        for tag, nw, x0, x1 in BOXES:
            widest[tag] = max(widest.get(tag, 0), nw)
            if tag == "aru":
                continue
            if nw > MAXW + 0.5 or x0 < XMIN - 0.5 or x1 > XMAX + 0.5:
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
    for j in range(1, BITES + 1):                                       # tiap bentol bertambah
        ev.append({"t": BITE0 + (BITE1 - BITE0) * j / BITES, "sfx": "pop", "gain": 0.28})
    ev.append({"t": BITE1, "sfx": "ding", "gain": 0.3})
    ev.append({"t": ZOOM_T + 0.15, "sfx": "pop", "gain": 0.3})
    for i in (seg0(2), seg0(5), chunk_of("KAMU PENGIN CIUM"), seg0(8), seg0(11), seg0(13), seg0(14),
              seg0(18), seg0(19), seg0(21), seg0(22), seg0(24), chunk_of("BAJU PANJANG,"), chunk_of("DAN KELAMBU."),
              chunk_of("KORBAN NYAMUK,"), chunk_of("TIDUR AMAN?")):
        ev.append({"t": cs(i), "sfx": "pop", "gain": 0.26})
    ev.append({"t": cs(seg0(9)) + 0.1, "sfx": "klik", "gain": 0.45})   # stempel MITOS
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": T100_END, "sfx": "ding", "gain": 0.35})               # 100x (puncak)
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
    elif cmd == "counters":
        print("bentol: 0 -> 7, nilai akhir di dtk", BITE1, "ditahan sampai", round(SC[2], 2),
              "(", round(SC[2] - BITE1, 2), "dtk )")
        print("100x: 1 -> 100 mulai", round(T100, 2), "nilai akhir di dtk", round(T100_END, 2), "ditahan sampai",
              round(SC[7], 2), "(", round(SC[7] - T100_END, 2), "dtk )")
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

"""Renderer ARN-50 "Kok kamu ngantuk habis makan siang?" — Flat 2D latar terang (#F2F4F7).
Adaptasi pagi/render_flat_bon.py (helper kartu, pill, stempel, bubble, Aru, logo, subtitle, cek area aman, sfx):
- frame 0 (PRB-34/36/46): satu adegan + satu aksi — Aru di meja kantor, piring kosong di samping, jam digital besar
  di dinding bergerak 13.59 -> 14.00 (detik berjalan sejak dtk 0, angka berganti dtk ~1,8), bohlam di atas kepala
  Aru berkedip lalu padam, kepala terkulai; dtk ~1,5 piring nasi besar + "?" muncul. Judul layar hanya pill kecil
  di atas (bukan kartu judul besar); tanpa logo / label seri / progress bar di dtk 0-3.
- 11 adegan (tiap <= 6 dtk); sumber kecil di layar (PRB-39) adegan 4-7 + "bukan saran medis" adegan 9;
  ajakan kirim di puncak 922 vs 305 kkal (PRB-55); follow dtk 10,6-15 (PRB-4); penutup logo <= 1,5 dtk.
- area aman (PRB-41): semua pill/bubble/kartu <= 800 px dan di x 130..950; `check` memindai tiap 0,1 dtk.
Pemakaian (dari folder kerja sore/build/ngantuk, setelah align_ngantuk.py -> timing.json):
  TOTAL=54.6 python3 ../../render_flat_ngantuk.py events | check | scenes | stills 0,2,... | video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, NAVY, TEAL, YEL, WHITE, GREY_T, RED)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "54.6"))
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

SCENE_SEG = [0, 2, 6, 9, 11, 15, 17, 21, 24, 27, 30]
SCENE_OFF = {4: 0.0, 7: 0.0}   # adegan 4 & 7 mulai tepat di awal ucapan supaya tiap adegan <= 6 dtk
SC = [0.0] + [cs(seg0(s)) - SCENE_OFF.get(k, 0.25) for k, s in enumerate(SCENE_SEG) if k > 0] + [TOTAL]
NS = len(SCENE_SEG)
FOLLOW = (10.6, 15.0)          # PRB-4: ajakan follow teks kecil dtk 10-15
PB_START = 3.5                 # progress bar mulai dtk 3,5
NOTES = {4: ("Sleep Foundation, \"Why Do I Get Sleepy After Eating?\", 28 Okt 2025",),
         5: ("Monk, Clinics in Sports Medicine, Apr 2005",),
         6: ("grafik skematis · Sleep Foundation, 28 Okt 2025",),
         7: ("Reyner dkk., Physiology & Behavior 2012", "uji simulator · 12 pengemudi pria kurang tidur"),
         9: ("informasi umum, bukan saran medis",)}
FLIP = 1.8                     # jam 13.59 -> 14.00 (counter bergerak dtk ~2, PRB-29/46)
BULB_OFF = 2.45                # bohlam berkedip 2,0-2,45 lalu padam
DROOP = (2.45, 3.0)            # kepala terkulai
PLATE_T = 1.5                  # piring nasi besar + "?" (visual berganti ~dtk 1,5)
SHARE = (cs(chunk_of("3× LIPAT")) - 0.3, SC[8] - 0.2)   # ajakan kirim di puncak angka (PRB-55 poin 3)


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
    """kind: normal | sleepy (mata terpejam) | yawn (terpejam + mulut menguap)."""
    im = ARU_RAW.copy()
    if kind != "normal":
        d = ImageDraw.Draw(im)
        for x0 in (330, 486):                                       # tutup mata + alis
            d.ellipse((x0, 360, x0 + 84, 456), fill=SKIN)
        d.line([(320, 318), (417, 342)], fill=SKIN, width=30); d.line([(483, 342), (578, 318)], fill=SKIN, width=30)
        d.line([(326, 334), (414, 340)], fill=NAVY, width=14); d.line([(486, 340), (574, 334)], fill=NAVY, width=14)
        for x0 in (340, 496):                                       # mata terpejam
            d.arc((x0, 384, x0 + 66, 432), 15, 165, fill=NAVY, width=12)
        d.rectangle((384, 500, 516, 560), fill=SKIN)                # tutup mulut
        if kind == "yawn":
            d.ellipse((414, 494, 486, 584), fill=(120, 40, 50), outline=NAVY, width=10)
        else:
            d.line([(424, 530), (476, 530)], fill=NAVY, width=10)
    return im.crop(ARU_BOX)


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
    """pill kecil judul layar (kolom Judul layar), y≈300 (PRB-41); NGANTUK disorot kuning."""
    f = F("pb", 38); s1 = "Habis makan, kok "; s2 = "NGANTUK"; s3 = "?"
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


@lru_cache(None)
def plate_img(w, heap=1.0):
    """piring nasi putih; heap 0 = piring kosong, 0.5 = setengah porsi, 1 = porsi besar."""
    im = Image.new("RGBA", (300, 240), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((8, 148, 292, 232), fill=WHITE, outline=NAVY, width=6)
    d.ellipse((50, 162, 250, 216), fill=(236, 240, 246))
    if heap > 0.01:
        hw = 95 * (0.55 + 0.45 * heap); hh = 140 * heap
        d.chord((150 - hw, 190 - hh, 150 + hw, 190 + hh), 180, 360, fill=(252, 252, 248), outline=NAVY, width=6)
        for k in range(int(10 * heap) + 2):
            a = k * 2.399; rr = 0.75 * math.sqrt((k + 0.5) / (10 * heap + 2))
            x = 150 + hw * rr * math.cos(a); y = 190 - hh * 0.55 * (1 - rr) - 14 + 18 * abs(math.sin(a)) * rr
            d.ellipse((x - 7, y - 4, x + 7, y + 4), outline=(214, 214, 206), width=3)
    else:
        d.arc((70, 168, 230, 210), 200, 340, fill=(205, 212, 226), width=4)
    im = trim(im)
    return scaled(im, w)


@lru_cache(None)
def boss_img(h):
    """bos presentasi: jas biru tua, dasi merah, kacamata, tangan kanan menunjuk ke layar."""
    im = Image.new("RGBA", (340, 580), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x in (112, 168):
        d.rounded_rectangle((x, 400, x + 42, 530), 16, fill=(52, 58, 84), outline=NAVY, width=6)
        d.ellipse((x - 14, 508, x + 56, 548), fill=(40, 36, 52), outline=NAVY, width=6)
    d.line([(96, 270), (40, 120)], fill=NAVY, width=36); d.line([(96, 270), (40, 120)], fill=(58, 76, 154), width=24)
    d.ellipse((20, 92, 60, 132), fill=SKIN, outline=NAVY, width=5)
    d.line([(226, 270), (250, 380)], fill=NAVY, width=36); d.line([(226, 270), (250, 380)], fill=(58, 76, 154), width=24)
    d.ellipse((232, 368, 270, 406), fill=SKIN, outline=NAVY, width=5)
    d.rounded_rectangle((86, 240, 236, 420), 40, fill=(58, 76, 154), outline=NAVY, width=6)
    d.polygon([(136, 244), (186, 244), (161, 330)], fill=WHITE)
    d.polygon([(154, 252), (168, 252), (172, 320), (161, 336), (150, 320)], fill=RED)
    d.ellipse((76, 60, 246, 240), fill=SKIN, outline=NAVY, width=6)
    d.chord((76, 52, 246, 170), 180, 360, fill=(70, 60, 56), outline=NAVY, width=6)
    for x in (104, 170):
        d.rounded_rectangle((x, 132, x + 50, 170), 12, outline=NAVY, width=5)
        d.ellipse((x + 18, 144, x + 32, 160), fill=NAVY)
    d.line([(154, 148), (170, 148)], fill=NAVY, width=5)
    d.arc((126, 172, 196, 214), 10, 170, fill=NAVY, width=6)
    im = trim(im); r = h / im.height
    out = im.resize((int(im.width * r), h), Image.LANCZOS)
    out.info["nw"] = out.width
    return out


def bulb(d, cx, cy, r, on, glow=1.0):
    if on and glow > 0:
        for k in range(10):
            a = k * math.pi / 5 - math.pi / 2
            if math.sin(a) > 0.6: continue
            d.line([(cx + (r + 18) * math.cos(a), cy + (r + 18) * math.sin(a)),
                    (cx + (r + 18 + 40 * glow) * math.cos(a), cy + (r + 18 + 40 * glow) * math.sin(a))],
                   fill=YEL, width=10)
    fill = (255, 214, 64) if on else (196, 200, 212)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=NAVY, width=6)
    d.rounded_rectangle((cx - r * 0.45, cy + r * 0.8, cx + r * 0.45, cy + r * 1.35), 8, fill=(150, 156, 172),
                        outline=NAVY, width=5)
    d.arc((cx - r * 0.35, cy - r * 0.2, cx + r * 0.35, cy + r * 0.5), 200, 340, fill=NAVY if not on else (220, 140, 0),
          width=5)


def clock_face(d, cx, cy, r, t, sleepy=1.0, hh=14, mm=0):
    """jam dinding berwajah: jarum jam, mata mengantuk."""
    d.ellipse((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), fill=NAVY)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE)
    for k in range(12):
        a = k * math.pi / 6
        d.line([(cx + 0.82 * r * math.sin(a), cy - 0.82 * r * math.cos(a)),
                (cx + 0.92 * r * math.sin(a), cy - 0.92 * r * math.cos(a))], fill=NAVY, width=6)
    ah = (hh % 12 + mm / 60) * math.pi / 6; am = mm * math.pi / 30
    d.line([(cx, cy), (cx + 0.45 * r * math.sin(ah), cy - 0.45 * r * math.cos(ah))], fill=NAVY, width=12)
    d.line([(cx, cy), (cx + 0.7 * r * math.sin(am), cy - 0.7 * r * math.cos(am))], fill=NAVY, width=8)
    for ex in (-0.35, 0.35):                                           # mata (kelopak turun)
        x = cx + ex * r; y = cy + 0.28 * r; er = 0.15 * r
        d.ellipse((x - er, y - er, x + er, y + er), fill=WHITE, outline=NAVY, width=5)
        d.ellipse((x - er * 0.45, y - er * 0.2, x + er * 0.45, y + er * 0.7), fill=NAVY)
        lid = er * (0.2 + 1.5 * sleepy * (0.75 + 0.25 * math.sin(t * 2.2)))
        d.chord((x - er, y - er, x + er, y - er + 2 * min(lid, er * 1.9)), 180, 360, fill=(200, 206, 222))
        d.line([(x - er, y - er + min(lid, er * 1.9)), (x + er, y - er + min(lid, er * 1.9))], fill=NAVY, width=5)
    d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=RED)


def zzz(d, x, y, t, size=46, col=NAVY):
    for k in range(3):
        u = (t * 0.7 + k / 3) % 1.0
        f = F("pb", int(size * (0.7 + 0.5 * u)))
        a = int(255 * min(1, (1 - u) * 2))
        d.text((x + 50 * u + 20 * k, y - 120 * u), "z", font=f, fill=col + (a,), anchor="mm")


# ---------- adegan ----------
def clock_digits(t):
    """detik berjalan sejak dtk 0: 13.59:57 -> 58 -> 59 -> 14.00:00 di FLIP."""
    if t < FLIP:
        sec = 57 + min(2, int(t / 0.6))
        return "13.59", sec
    return "14.00", 0


def scene0(img, t):
    """frame 0: Aru di meja kantor, jam 13.59 -> 14.00, bohlam berkedip lalu padam, kepala terkulai."""
    d = ImageDraw.Draw(img)
    # jam digital besar di dinding
    hm, sec = clock_digits(t)
    flip = clamp((t - FLIP) / 0.25)
    T, td = card(620, 270, fill=NAVY, r=36, outline=NAVY)
    td.rounded_rectangle((20, 20, 600, 250), 26, fill=(14, 22, 64))
    col = RED if t >= FLIP else YEL
    f = F("pb", 168)
    sy = 1.0 if t < FLIP else 0.4 + 0.6 * back(flip)
    D = Image.new("RGBA", (560, 210), (0, 0, 0, 0)); dd = ImageDraw.Draw(D)
    text_c(dd, (230, 112), hm, f, col)
    if sy < 0.999:
        D = D.resize((560, max(1, int(210 * sy))), Image.BICUBIC)
    T.alpha_composite(D, (20, int(30 + 105 * (1 - sy))))
    td.rounded_rectangle((470, 96, 586, 176), 18, fill=(40, 52, 110))
    text_c(td, (528, 137), f":{sec:02d}", F("pb", 46), WHITE)
    shake = 6 * math.sin(t * 40) * clamp(1 - (t - FLIP) / 0.4) if t >= FLIP else 0
    paste_c(img, T, W / 2 + shake, 540, 1.0, tag="jam digital")
    # piring kosong di meja (sebelah Aru)
    # Aru: normal -> mengantuk (mata terpejam) saat lampu padam; kepala terkulai
    dr = eio((t - DROOP[0]) / (DROOP[1] - DROOP[0]))
    kind = "normal" if t < BULB_OFF else "sleepy"
    ah = 560; ax = 400
    draw_aru(img, ax + 18 * dr, DESK_Y + 170 + 26 * dr, ah, t, kind=kind, angle_amp=2.0 * (1 - dr), extra=-13 * dr,
             bob=6 * (1 - dr))
    img.alpha_composite(desk_layer())
    paste_c(img, plate_img(250, 0.0), 790, DESK_Y - 4, tag="piring kosong")
    # bohlam di atas kepala Aru: menyala, berkedip 2,0-2,45, lalu padam
    on = t < 2.0 or (t < BULB_OFF and int((t - 2.0) / 0.075) % 2 == 1)
    by = 790 + 30 * dr
    bulb(d, ax + 30 * dr, by, 58, on, glow=0.45 + 0.1 * math.sin(t * 8))
    # piring nasi besar + "?" muncul dtk ~1,5
    p = pop(t, PLATE_T)
    if p > 0:
        L = Image.new("RGBA", (420, 360), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        L.alpha_composite(plate_img(330, 1.0), (20, 100))
        ld.ellipse((270, 10, 400, 140), fill=YEL, outline=NAVY, width=7)
        text_c(ld, (335, 72), "?", F("pb", 96), NAVY)
        L.info["nw"] = 380
        paste_c(img, L, 760, 1040 + 6 * math.sin(t * 3), p, 4 * math.sin(t * 2.5), tag="piring nasi ?")
    if t >= DROOP[1] - 0.2:
        zzz(ImageDraw.Draw(img), ax + 170, 830, t - DROOP[1])


def scene1(img, t):
    """Aru mengangkat dua kartu tebakan: nasi dan tanda tanya; 'Coba TEBAK'."""
    p = pop(t, SC[1] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Coba TEBAK", "🤔", fill=YEL, fg=NAVY, size=60), W / 2, 500, p, -2, tag="pill tebak")
    draw_aru(img, W / 2, 1500, 520, t)
    cards = [("🍚", "NASI?", 300, cs(seg0(3)) - 0.1, -8), ("❓", "ATAU…", 780, cs(seg0(3)) + 0.25, 8)]
    for k, (em, lab, x, t0, ang) in enumerate(cards):
        q = pop(t, t0)
        if q <= 0: continue
        big = k == 1 and t >= cs(seg0(4))
        C, cd = card(300, 340, fill=WHITE, outline=NAVY if not big else RED, ow=7 if big else 5)
        C.alpha_composite(emoji_img(em, 170), (int(150 - emoji_img(em, 170).width / 2), 40))
        text_c(cd, (150, 285), lab, F("pb", 46), RED if big else NAVY)
        s = q * (1.12 + 0.05 * math.sin(t * 9) if big else 1.0)
        paste_c(img, C, x, 900 + 10 * math.sin(t * 3 + k), s, ang + 3 * math.sin(t * 2 + k), tag="kartu tebak")


def scene2(img, t):
    """ruang rapat habis makan siang: bos presentasi, Aru di meja mulai mengangguk."""
    p = pop(t, SC[2] + 0.05)
    if p > 0:
        T, td = head_card(760, 420, "RAPAT · 13.30", col=NAVY, size=42)
        bars = [(0.45, TEAL), (0.7, TEAL), (0.55, YEL), (0.9, RED)]
        for k, (v, col) in enumerate(bars):
            u = eout((t - SC[2] - 0.3 - 0.12 * k) / 0.5)
            x = 120 + k * 150; h = 230 * v * u
            td.rounded_rectangle((x, 380 - h, x + 100, 380), 12, fill=col, outline=NAVY, width=4)
        td.line([(90, 382), (690, 382)], fill=NAVY, width=5)
        paste_c(img, T, 520, 720, p, tag="layar presentasi")
    q = pop(t, cs(seg0(8)) - 0.1)
    if q > 0:
        bb = 4 * math.sin(t * 5)
        paste_c(img, boss_img(560), 790, 1150 + bb, q, 2 * math.sin(t * 2.4), tag="bos")
    nod = 0.0
    if t >= cs(seg0(8)):
        nod = 7 * max(0, math.sin(2 * math.pi * 1.3 * t))
    draw_aru(img, 360, 1420, 440, t, kind="normal" if t < cs(seg0(8)) else "sleepy", angle_amp=1.0, extra=-nod)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((150, 1280, 640, 1350), 20, fill=WOOD, outline=NAVY, width=5)
    d.rectangle((190, 1350, 220, 1470), fill=WOOD_D); d.rectangle((570, 1350, 600, 1470), fill=WOOD_D)
    paste_c(img, plate_img(150, 0.0), 500, 1272, tag="piring kosong")


def scene3(img, t):
    """close-up: kepala Aru mengangguk-angguk… bukan karena setuju."""
    d = ImageDraw.Draw(img)
    nod = 9 * max(0, math.sin(2 * math.pi * 1.4 * t)) + 4
    draw_aru(img, W / 2, 1640, 880, t, kind="sleepy", angle_amp=0.5, extra=-nod, bob=4)
    q = pop(t, cs(seg0(9)) + 0.2)
    if q > 0:
        paste_c(img, bubble("Mm… mm…", col=NAVY, fg=WHITE, size=46, tail="left"), 730, 560, q, 3, tag="bubble mm")
        for k, y in enumerate((700, 820)):
            off = 14 * math.sin(2 * math.pi * 1.4 * t + k * math.pi)
            arrow(d, 860, y - 40 + off, 860, y + 40 + off, YEL, w=14, head=30)
    q = pop(t, cs(seg0(10)) + 0.1)
    if q > 0:
        paste_c(img, stamp("BUKAN SETUJU", col=RED, size=62), W / 2, 1180, q, -7, tag="stempel bukan setuju")
    zzz(ImageDraw.Draw(img), 300, 700, t)


def scene4(img, t):
    """papan tersangka: piring nasi digiring masuk; karbohidrat memang bikin ngantuk… tapi."""
    p = pop(t, SC[4] + 0.02)
    if p > 0:
        T, td = head_card(800, 700, "PAPAN TERSANGKA", col=RED, size=46)
        td.rectangle((24, 110, 776, 680), fill=(226, 230, 238))
        for k in range(8):
            y = 160 + k * 66
            td.line([(24, y), (776, y)], fill=(196, 202, 216), width=4)
            td.text((40, y), f"{180 - k * 10}", font=F("pm", 24), fill=(150, 156, 172), anchor="lm")
        u = eout((t - SC[4] - 0.15) / 0.9)
        px = -180 + (400 + 180) * u
        T.alpha_composite(plate_img(380, 1.0), (int(px - 190), 230))
        if u > 0.95:
            q = pop(t, cs(seg0(12)) - 0.1)
            if q > 0:
                td.rounded_rectangle((210, 560, 590, 650), 16, fill=NAVY)
                text_c(td, (400, 606), "TERSANGKA #1", F("pb", 48), YEL)
        paste_c(img, T, W / 2, 860, p, tag="papan tersangka")
    q = pop(t, cs(seg0(13)))
    if q > 0:
        T, td = card(800, 150, fill=WHITE, outline=GREEN, ow=6)
        icon_check(td, 80, 75, 0.9)
        td.text((150, 52), "Karbohidrat tinggi", font=F("pb", 44), fill=NAVY, anchor="lm")
        td.text((150, 106), "memang bikin lebih ngantuk", font=F("pm", 36), fill=GREY_T, anchor="lm")
        paste_c(img, T, W / 2, 1340, q, tag="kartu karbo")
    q = pop(t, cs(seg0(14)))
    if q > 0:
        paste_c(img, bubble("TAPI…", col=YEL, fg=NAVY, size=72, tail="right"), 760, 425, q * (1 + 0.04 * math.sin(t * 9)),
                6, tag="bubble tapi")


def scene5(img, t):
    """meja makan kosong (tanpa makan siang), Aru tetap menguap."""
    p = pop(t, SC[5] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Peneliti menemukan", "🔬", fill=NAVY, fg=WHITE, size=48), W / 2, 470, p, -2,
                tag="pill peneliti")
    q = pop(t, SC[5] + 0.25)
    if q > 0:
        T, td = head_card(800, 430, "TANPA MAKAN SIANG", col=TEAL, size=46)
        td.rounded_rectangle((60, 170, 740, 400), 30, fill=WOOD, outline=NAVY, width=5)
        td.ellipse((250, 200, 550, 370), fill=(250, 240, 214), outline=(214, 190, 150), width=4)   # alas makan
        dashed(td, [(310, 285), (400, 230), (490, 285), (400, 340), (310, 285)], (170, 150, 120), w=5)
        td.ellipse((330, 245, 470, 325), outline=RED, width=10); td.line([(345, 315), (455, 255)], fill=RED, width=10)
        td.rounded_rectangle((590, 116, 760, 168), 16, fill=NAVY)
        text_c(td, (675, 142), "14.00", F("pb", 38), YEL)
        paste_c(img, T, W / 2, 820, q, tag="kartu tanpa makan")
    draw_aru(img, 290, 1500, 430, t, kind="yawn", angle_amp=3.0)
    r = pop(t, SC[5] + 0.6)
    if r > 0:
        paste_c(img, bubble("Hoaam…", col=WHITE, fg=NAVY, size=48, tail="left"), 680, 1130, r, 2, tag="bubble hoaam")
    r = pop(t, cs(chunk_of("TETAP DATANG")))
    if r > 0:
        paste_c(img, stamp("TETAP NGANTUK", col=RED, size=50), 690, 1320, r, -6, tag="stempel tetap")


def scene6(img, t):
    """jam tubuh berwajah + grafik skematis 'sinyal melek' turun di awal siang."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[6] + 0.05)
    if p > 0:
        L = Image.new("RGBA", (320, 320), (0, 0, 0, 0))
        clock_face(ImageDraw.Draw(L), 160, 160, 130, t, sleepy=0.6)
        L.info["nw"] = 280
        paste_c(img, L, 330, 610, p, 4 * math.sin(t * 2), tag="jam tubuh")
    q = pop(t, cs(seg0(18)) + 0.3)
    if q > 0:
        paste_c(img, pill("JAM TUBUH", fill=YEL, fg=NAVY, size=50), 720, 610, q, 3, tag="pill jam tubuh")
    q = pop(t, SC[6] + 0.3)
    if q > 0:
        T, td = card(800, 560, fill=WHITE)
        text_c(td, (400, 50), "SINYAL MELEK OTAK", F("pb", 44), NAVY)
        x0, x1, yb, yt = 70, 740, 470, 120
        td.line([(x0, yb), (x1, yb)], fill=NAVY, width=5); td.line([(x0, yb), (x0, yt)], fill=NAVY, width=5)
        labs = [("pagi", 0.12), ("siang", 0.42), ("sore", 0.66), ("malam", 0.92)]
        for s, u in labs:
            td.text((x0 + (x1 - x0) * u, yb + 36), s, font=F("pm", 30), fill=GREY_T, anchor="mm")
        def yv(u):   # skematis: naik pagi, turun awal siang, naik sore, turun malam
            v = 0.15 + 0.75 * (1 - math.exp(-u * 6)) - 0.42 * math.exp(-((u - 0.42) / 0.07) ** 2) - 0.8 * max(0, u - 0.78) ** 1.2 * 3
            return yb - (yb - yt) * clamp(v, 0.02, 1)
        dip_t = cs(seg0(19)) - 0.1
        if t >= dip_t:
            td.rectangle((x0 + (x1 - x0) * 0.33, yt - 10, x0 + (x1 - x0) * 0.52, yb - 3), fill=(255, 234, 170))
            td.text((x0 + (x1 - x0) * 0.425, yt + 6), "AWAL SIANG", font=F("pb", 28), fill=NAVY, anchor="mm")
        g = clamp((t - SC[6] - 0.6) / (cs(seg0(20)) - SC[6] - 0.3))
        pts = [(x0 + (x1 - x0) * u, yv(u)) for u in [k / 80 for k in range(int(80 * g) + 1)]]
        if len(pts) > 1:
            td.line(pts, fill=TEAL, width=12, joint="curve")
        if t >= cs(seg0(20)):
            u = 0.42; xx = x0 + (x1 - x0) * u; yy = yv(u)
            r = pop(t, cs(seg0(20)))
            arrow(td, xx + 110, yy - 150 * r, xx + 110, yy + 10, RED, w=14, head=32)
            td.text((xx + 150, yy - 70), "TURUN", font=F("pb", 34), fill=RED, anchor="lm")
        paste_c(img, T, W / 2, 1100, q, tag="grafik sinyal")


def scene7(img, t):
    """simulator: 922 vs 305 kkal, mobil keluar jalur (PUNCAK) + ajakan kirim (overlay SHARE)."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[7] + 0.05)
    if p > 0:
        T, td = card(800, 380, fill=WHITE, outline=RED, ow=7)
        text_c(td, (400, 44), "MAKAN SIANG DI UJI SIMULATOR", fit("pb", 36, "MAKAN SIANG DI UJI SIMULATOR", 720), NAVY)
        T.alpha_composite(plate_img(210, 0.45), (65, 150))
        text_c(td, (170, 310), "305 kkal", F("pb", 54), TEAL)
        text_c(td, (400, 200), "vs", F("pb", 54), NAVY)
        t0 = cs(chunk_of("3× LIPAT")) - 0.1
        u = eio((t - t0) / 1.0) if t >= t0 else 0
        PL = plate_img(int(210 + 60 * u), 0.45 + 0.55 * u)
        T.alpha_composite(PL, (int(600 - PL.width / 2), int(255 - PL.height)))
        v = int(round(305 + (922 - 305) * u))
        text_c(td, (600, 310), f"{v} kkal", F("pb", 64 if u > 0.5 else 54), RED)
        paste_c(img, T, W / 2, 700, p * (1 + 0.015 * math.sin(t * 8)), -1, tag="kartu kkal")
    q = pop(t, cs(seg0(22)) - 0.1)
    if q > 0:
        T, td = card(800, 300, fill=(92, 98, 116), outline=NAVY, ow=6)
        td.rectangle((6, 6, 794, 294), fill=(92, 98, 116))
        for y in (40, 260):
            td.line([(10, y), (790, y)], fill=WHITE, width=8)
        dashed(td, [(10, 150), (790, 150)], YEL, w=8, on=50, off=40, phase=t * 600)
        ol = clamp((t - cs(chunk_of("BIKIN PENGEMUDI"))) / 1.4)
        cy = 205 - ol * 140 * (0.6 + 0.4 * math.sin(t * 5))
        cx = 400 + 16 * math.sin(t * 3)
        ang = -12 * ol * math.cos(t * 5)
        C = Image.new("RGBA", (200, 110), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
        cd.rounded_rectangle((4, 10, 196, 100), 30, fill=RED, outline=NAVY, width=6)
        cd.rounded_rectangle((60, 22, 140, 88), 16, fill=(180, 214, 240), outline=NAVY, width=4)
        for wx in (40, 160):
            for wy in (4, 96):
                cd.rounded_rectangle((wx - 18, wy - 8, wx + 18, wy + 8), 4, fill=NAVY)
        C = C.rotate(ang, Image.BICUBIC, expand=True)
        T.alpha_composite(C, (int(cx - C.width / 2), int(cy - C.height / 2)))
        paste_c(img, T, W / 2, 1110, q, tag="jalan simulator")
    r = pop(t, cs(chunk_of("MAKIN OLENG.")))
    if r > 0:
        paste_c(img, stamp("KELUAR JALUR!", col=RED, size=54), 700, 990, r, 6, tag="stempel keluar jalur")


def share_card(img, t):
    """ajakan kirim di puncak angka (PRB-55 poin 3)."""
    if not (SHARE[0] <= t < SHARE[1]): return
    a = min(clamp((t - SHARE[0]) / 0.25), clamp((SHARE[1] - t) / 0.25))
    s = 0.85 + 0.15 * back((t - SHARE[0]) / 0.35)
    T, td = card(800, 170, fill=TEAL)
    e = emoji_img("😴", 64)
    text_c(td, (370, 54), "Kirim ke teman yang", F("pb", 44), WHITE)
    text_c(td, (370, 118), "tumbang tiap jam 2", F("pb", 52), YEL)
    T.alpha_composite(e, (690, 52))
    paste_c(img, T, W / 2, 1405 + 4 * math.sin(t * 5), s, 0, a, tag="kartu kirim")


def scene8(img, t):
    """jam tubuh mematikan saklar lampu; porsi besar bikin ruangan makin gelap."""
    d = ImageDraw.Draw(img)
    off_t = cs(chunk_of("MEMATIKAN LAMPU,"))
    big_t = cs(chunk_of("PORSI BESAR"))
    on = t < off_t
    d.line([(540, 560), (540, 650)], fill=NAVY, width=6)
    bulb(d, 540, 720, 80, on, glow=0.9 + 0.1 * math.sin(t * 8))
    L = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    clock_face(ImageDraw.Draw(L), 150, 150, 120, t, sleepy=0.8)
    paste_c(img, L, 300, 1080, pop(t, SC[8] + 0.1), 3 * math.sin(t * 2), tag="jam tubuh")
    # tangan jam -> saklar
    sw_u = eio((t - off_t + 0.3) / 0.3)
    d.line([(420, 1080), (505 - 10 * sw_u, 1060)], fill=NAVY, width=14)
    d.rounded_rectangle((500, 990, 590, 1130), 16, fill=WHITE, outline=NAVY, width=6)
    ty = 1030 + 60 * sw_u
    d.rounded_rectangle((528, ty - 26, 562, ty + 26), 10, fill=NAVY if on else (150, 156, 172))
    q = pop(t, big_t)
    if q > 0:
        paste_c(img, plate_img(330, 1.0), 770, 1150, q * (1 + 0.03 * math.sin(t * 6)), tag="piring besar")
    # gelap bertahap
    dark = 0.0
    if t >= off_t: dark = 0.32 * eio((t - off_t) / 0.3)
    if t >= big_t: dark += 0.25 * eio((t - big_t) / 0.6)
    if dark > 0:
        Dk = Image.new("RGBA", (W, H), (14, 20, 52, int(255 * dark)))
        img.alpha_composite(Dk)
    p = pop(t, SC[8] + 0.05)
    if p > 0:
        paste_c(img, pill("DUA-DUANYA BENAR", fill=YEL, fg=NAVY, size=58), W / 2, 470, p, -2, tag="pill dua-duanya")
    if t >= off_t:
        paste_c(img, pill("JAM TUBUH", fill=NAVY, fg=WHITE, size=38), 300, 1280, pop(t, off_t), tag="label jam")
    if q > 0:
        paste_c(img, pill("PORSI BESAR", fill=RED, fg=WHITE, size=38), 770, 1320, q, tag="label porsi")


def scene9(img, t):
    """besok coba: porsi nasi lebih kecil, lalu jalan sebentar kena matahari."""
    p = pop(t, SC[9] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("BESOK COBA", "✅", fill=YEL, fg=NAVY, size=56), W / 2, 470, p, -2, tag="pill besok coba")
    q = pop(t, cs(seg0(28)) - 0.1)
    if q > 0:
        T, td = card(800, 340, fill=WHITE, outline=GREEN, ow=6)
        td.ellipse((24, 24, 104, 104), fill=GREEN); text_c(td, (64, 64), "1", F("pb", 54), WHITE)
        u = eio((t - cs(chunk_of("LEBIH KECIL,"))) / 0.7)
        T.alpha_composite(plate_img(280, 1.0 - 0.5 * u), (110, int(320 - plate_img(280, 1.0 - 0.5 * u).height)))
        td.text((440, 130), "PORSI NASI", font=F("pb", 52), fill=NAVY, anchor="lm")
        if u > 0:
            td.rounded_rectangle((430, 180, 770, 270), 24, fill=YEL)
            text_c(td, (600, 226), "LEBIH KECIL", F("pb", 46), NAVY)
        paste_c(img, T, W / 2, 760, q, tag="kartu porsi kecil")
    q = pop(t, cs(seg0(29)) - 0.1)
    if q > 0:
        T, td = card(800, 340, fill=(255, 248, 226), outline=GREEN, ow=6)
        td.ellipse((24, 24, 104, 104), fill=GREEN); text_c(td, (64, 64), "2", F("pb", 54), WHITE)
        sun = emoji_img("☀️", 130)
        T.alpha_composite(sun, (640, 20))
        td.text((130, 64), "JALAN SEBENTAR", font=F("pb", 46), fill=NAVY, anchor="lm")
        td.text((130, 120), "kena matahari", font=F("pm", 38), fill=GREY_T, anchor="lm")
        td.line([(30, 318), (770, 318)], fill=(214, 200, 160), width=6)
        u = clamp((t - cs(seg0(29))) / 3.5)
        A = aru_h(170)
        T.alpha_composite(A, (int(120 + 460 * u), int(150 + 4 * abs(math.sin(t * 8)))))
        paste_c(img, T, W / 2, 1180, q, tag="kartu jalan")


def scene10(img, t):
    """penutup: layar dibagi dua, tim NASI vs tim JAM; 'Komen 1 kata'."""
    d = ImageDraw.Draw(img)
    t_n = cs(chunk_of("SALAHIN NASI,")); t_j = cs(chunk_of("SALAHIN JAM?"))
    cols = [(140, 530, TEAL, "NASI", "🍚", t_n, t_j), (550, 940, RED, "JAM", "⏰", t_j, TOTAL)]
    y0, y1 = 470, 1250
    for j, (x0, x1, col, lab, em, a0, a1) in enumerate(cols):
        act = a0 <= t < a1 or t < t_n
        p = pop(t, SC[10] + 0.05 + 0.12 * j)
        if p <= 0: continue
        C = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
        cd.rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), 30, fill=WHITE if act else (232, 235, 242),
                             outline=col if act else (200, 205, 216), width=7)
        cd.rounded_rectangle((0, 0, x1 - x0 - 1, 150), 30, fill=col if act else (190, 196, 210))
        cd.rectangle((0, 100, x1 - x0 - 1, 150), fill=col if act else (190, 196, 210))
        text_c(cd, ((x1 - x0) / 2, 44), "TIM", F("pb", 34), WHITE)
        text_c(cd, ((x1 - x0) / 2, 104), lab, F("pb", 62), WHITE)
        e = emoji_img(em, 230)
        C.alpha_composite(e, (int((x1 - x0) / 2 - e.width / 2), 260))
        sal = "salahin " + lab.lower()
        text_c(cd, ((x1 - x0) / 2, 620), sal, F("pb", 44), NAVY if act else GREY_T)
        C.info["nw"] = x1 - x0
        beat = 1 + (0.03 * math.sin(t * 8) if (a0 <= t < a1) else 0)
        paste_c(img, C, (x0 + x1) / 2, (y0 + y1) / 2, p * beat, -1.5 if j == 0 else 1.5, tag="kolom " + lab)
    if t >= SC[10] + 0.2:
        d.ellipse((540 - 48, 860 - 48, 540 + 48, 860 + 48), fill=YEL, outline=NAVY, width=6)
        text_c(d, (540, 858), "vs", F("pb", 42), NAVY)
    p = pop(t, t_n - 0.2)
    if p > 0:
        B, bd = card(800, 150, fill=YEL, outline=NAVY)
        text_c(bd, (400, 50), "Tim NASI atau tim JAM?", F("pb", 50), NAVY)
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
        img = bg_office().copy()
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
    for tt in (0.05, 0.65, 1.25):
        ev.append({"t": tt, "sfx": "klik", "gain": 0.35})          # detik jam berjalan
    ev.append({"t": PLATE_T, "sfx": "pop", "gain": 0.3})
    ev.append({"t": FLIP, "sfx": "ding", "gain": 0.3})              # 14.00
    ev.append({"t": BULB_OFF, "sfx": "klik", "gain": 0.4})          # bohlam padam
    for i in (seg0(3), seg0(4), seg0(8), seg0(10), seg0(12), seg0(13), seg0(14), chunk_of("TETAP DATANG"),
              seg0(19), seg0(20), seg0(22), chunk_of("MAKIN OLENG."), seg0(24), chunk_of("PORSI BESAR"),
              chunk_of("LEBIH KECIL,"), seg0(29), chunk_of("SALAHIN NASI,"), chunk_of("SALAHIN JAM?")):
        ev.append({"t": cs(i), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": cs(chunk_of("MEMATIKAN LAMPU,")), "sfx": "klik", "gain": 0.45})   # saklar
    ev.append({"t": cs(chunk_of("3× LIPAT")) + 1.0, "sfx": "ding", "gain": 0.35})      # 922 kkal (puncak)
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

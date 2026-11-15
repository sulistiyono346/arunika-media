"""Renderer ARN-49 "Mana Lebih Hemat? #9 — uang dipinjam teman setahun" — Flat 2D latar terang (PRB-31).
Salinan render_flat_bon.py (helper kartu, koin, Si Bocor, pill, bubble, stempel, subtitle, cek area aman, sfx) dengan:
- frame 0 (PRB-36): satu adegan + satu aksi — Aru menyodorkan uang raksasa "Rp1.000.000" ke teman, Si Bocor
  menggerogoti pojok uang ("kriuk!") sampai lembarnya mengecil; satu counter besar Rp1.000.000 turun dan berhenti di
  "Rp9??.???" dtk 2,0 (PRB-29/46). Judul layar hanya pill kecil "Utang teman, diam-diam SUSUT" (tanpa kartu judul
  besar). Tanpa label seri/logo/progress bar dtk 0-3; visual berganti ~dtk 1,5 (gigitan + lembar mengecil).
- 19 adegan (tiap <= 6 dtk); counter Rp968.700 (adegan 7, ditahan sampai adegan 8) dan +Rp37.500 (adegan 10,
  ditahan sampai adegan 11) berhenti di nilai akhir >= 1,5 dtk; sumber kecil BPS Okt 2026 & LPS 3,75% (PRB-39);
  "*angka contoh ilustrasi" untuk Rp1 juta; ajakan kirim di puncak Rp968.700 (PRB-55); layar terbelah tim NUNGGU vs
  tim LANGSUNG TAGIH (adegan 12-15); tanpa adegan komentar part sebelumnya (PRB-51).
- area aman (PRB-41): semua pill/bubble/kartu <= 800 px dan di x 130..950; `check` memindai tiap 0,1 dtk.
Pemakaian (dari folder kerja pagi/build/pinjam, setelah align_pinjam.py -> timing.json):
  TOTAL=73.6 python3 ../../render_flat_pinjam.py events | check | scenes | stills 0,2,... | video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, rp, NAVY, TEAL, YEL, WHITE, GREY_T, RED, SAFE_X)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "73.6"))
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
GREEN = (46, 160, 110); INK = (60, 66, 92); LIGHT = (232, 238, 246)
BODY = (224, 82, 63); BODY_D = (176, 56, 44)
MAXW, XMIN, XMAX = 800, 130, 950   # PRB-41

TIM = json.load(open("timing.json"))
def cs(i): return TIM[i]["start"] + LEAD
def ce(i): return TIM[i]["end"] + LEAD




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
def dia_img(h):
    """'dia' = teman yang pinjam uang: rambut jambul, kacamata hitam, jaket merah, senyum puas."""
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


def card_text(d, xy, s, size, maxw, col=NAVY, name="pb", anchor="mm"):
    d.text(xy, s, font=fit(name, size, s, maxw), fill=col, anchor=anchor)



# ---------- konstanta per reel ----------
def sg(si): return next(c["start"] for c in TIM if c["seg"] == si) + LEAD     # awal segmen VO (dtk video)
def sge(si): return [c["end"] for c in TIM if c["seg"] == si][-1] + LEAD


SCENE_SEG = [0, 2, 4, 8, 11, 14, 17, 19, 20, 22, 24, 26, 28, 30, 31, 32, 35, 39, 41]
SC = [0.0] + [sg(i) - 0.25 for i in SCENE_SEG[1:]] + [TOTAL]
NS = len(SCENE_SEG)
FOLLOW = (10.8, 15.0)          # PRB-4: ajakan follow teks kecil dtk 10-15 (adegan 3)
PB_START = 3.5                 # progress bar mulai dtk 3,5
ILU = "*angka contoh ilustrasi"
SRC_BPS = "Inflasi tahunan Okt 2026 · BPS, rilis 2 Nov 2026"
SRC_LPS = ("Bunga penjaminan LPS bank umum, 1 Okt 2026–Jan 2027", "bunga tiap bank bisa lebih rendah · " + ILU)
NOTES = {1: (ILU,), 2: (ILU,), 3: (ILU,), 4: (ILU,), 5: (SRC_BPS,), 6: (SRC_BPS, ILU),
         7: ("daya beli Rp1 jt setelah setahun, inflasi 3,23% (dibulatkan)", SRC_BPS + " · " + ILU),
         8: ("Rp1.000.000 − Rp968.700 · inflasi BPS Okt 2026",), 9: SRC_LPS,
         10: ("Rp1 jt × 3,75% setahun · " + ILU, "Bunga penjaminan LPS bank umum, 1 Okt 2026–Jan 2027"),
         11: ("Inflasi BPS Okt 2026 3,23% · bunga penjaminan LPS 3,75%", ILU)}
CT0, CT1 = 0.45, 2.0           # counter frame 0: turun lalu BERHENTI di "Rp9??.???" dtk 2,0
P0, P1 = sg(19) + 0.05, sg(19) + 0.85      # counter puncak Rp1.000.000 -> Rp968.700
D0, D1 = sg(25) + 0.05, sg(25) + 0.95      # counter deposito +Rp0 -> +Rp37.500
SHARE = (P1 + 0.1, SC[8] + 1.6)            # ajakan kirim di puncak angka (PRB-55 poin 3)
MONEY_G, MONEY_D = (122, 196, 140), (52, 128, 84)


def scene_of(t):
    for k in range(NS):
        if t < SC[k + 1]: return k
    return NS - 1


@lru_cache(None)
def money_base(w):
    """uang raksasa Rp1.000.000 (lembar hijau)."""
    h = int(w * 0.5)
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 12, w + 10, h + 12), 26, fill=(20, 33, 91, 45))
    d.rounded_rectangle((0, 0, w, h), 26, fill=MONEY_G, outline=NAVY, width=6)
    d.rounded_rectangle((22, 22, w - 22, h - 22), 18, outline=MONEY_D, width=4)
    d.ellipse((40, h / 2 - 70, 180, h / 2 + 70), fill=(176, 224, 186), outline=MONEY_D, width=4)
    text_c(d, (110, h / 2), "1jt", F("pb", int(w * 0.06)), MONEY_D)
    text_c(d, (w / 2 + 70, h / 2 - 8), "Rp1.000.000", fit("pb", int(w * 0.11), "Rp1.000.000", w - 260), NAVY)
    text_c(d, (w / 2 + 70, h / 2 + int(w * 0.085)), "SATU JUTA RUPIAH", F("pm", int(w * 0.035)), MONEY_D)
    im.info["nw"] = w
    return im


def money_img(w, bite=0.0):
    """uang + gigitan Si Bocor di pojok kanan atas (bite 0..1)."""
    im = money_base(w).copy()
    if bite > 0.01:
        a = im.getchannel("A"); ad = ImageDraw.Draw(a)
        R = int(w * 0.09)
        bites = [(w - 10, 10), (w - 10 - R * 1.1, 6), (w - 6, 10 + R * 1.1), (w - 10 - R * 2.0, 14),
                 (w - 14, 10 + R * 2.0), (w - 10 - R * 1.5, 10 + R * 1.2)]
        n = bite * len(bites)
        for k, (x, y) in enumerate(bites):
            f = clamp(n - k)
            if f <= 0: break
            r = R * f
            ad.ellipse((x - r, y - r, x + r, y + r), fill=0)
        im.putalpha(a)
    im.info["nw"] = w
    return im


def big_num(text, col=NAVY, size=150, fill=WHITE, outline=NAVY, w=None):
    f = fit("pb", size, text, (w or MAXW) - 70)
    w = w or min(MAXW, int(f.getlength(text) + 90)); h = size + 70
    L, d = card(w, h, fill=fill, outline=outline, ow=7)
    text_c(d, (w / 2, h / 2 + 4), text, f, col)
    return L


def note_lines(img, lines, y0=1712):
    d = ImageDraw.Draw(img)
    for j, s in enumerate(lines):
        f = fit("pm", 28, s, MAXW)
        track("catatan", f.getlength(s), W / 2 - f.getlength(s) / 2, W / 2 + f.getlength(s) / 2)
        d.text((W / 2, y0 + j * 40), s, font=f, fill=GREY_T, anchor="mm")


# ---------- adegan ----------
def counter0(t):
    """Rp1.000.000 turun; berhenti & disamarkan jadi Rp9??.??? di dtk 2,0 (nilai asli dibuka di adegan 7)."""
    if t < CT0: return "Rp1.000.000", False
    if t >= CT1: return "Rp9??.???", True
    u = eio((t - CT0) / (CT1 - CT0))
    v = 1000000 - 23000 * u - (137 * int(t * 30)) % 900 * u
    return rp(int(round(v / 100.0) * 100)), False


def title_pill(img):
    """judul layar = pill kecil (bukan kartu judul besar, PRB-36): 'Utang teman, diam-diam SUSUT'."""
    f = F("pb", 40); a = "Utang teman, diam-diam "; b = "SUSUT"
    wa, wb = f.getlength(a), f.getlength(b); w = int(wa + wb + 24 + 60); h = 82
    P = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    d.rounded_rectangle((8, 10, w + 8, h + 10), h // 2, fill=(20, 33, 91, 55))
    d.rounded_rectangle((0, 0, w, h), h // 2, fill=NAVY)
    d.text((30, h / 2 + 2), a, font=f, fill=WHITE, anchor="lm")
    d.rounded_rectangle((30 + wa - 4, 12, 30 + wa + wb + 20, h - 12), 14, fill=YEL)
    d.text((30 + wa + 8, h / 2 + 2), b, font=f, fill=NAVY, anchor="lm")
    P.info["nw"] = w
    paste_c(img, P, W / 2, 320, tag="pill judul")


def scene0(img, t):
    """frame 0: uang raksasa dari Aru ke teman, Si Bocor menggerogoti pojok uang, counter Rp1.000.000 turun."""
    title_pill(img)
    s, done = counter0(t)
    hot = t >= CT0
    f = F("pb", 112)
    L, d = card(780, 200, fill=(253, 228, 222) if hot else WHITE, outline=RED if hot else NAVY, ow=7)
    text_c(d, (360 if hot else 390, 102), s, f, RED if hot else NAVY)
    if hot and not done:
        arrow(d, 720, 45, 720, 45 + 110 * clamp((t - CT0) / 0.3), RED, w=18, head=38)
    sc = 1.0 + (0.06 * back((t - CT1) / 0.3) - 0.06 * clamp((t - CT1 - 0.3) / 0.3) if t >= CT1 else 0)
    paste_c(img, L, W / 2, 520, sc, tag="counter")
    # uang mengecil mulai dtk ~1,5 (visual berganti)
    shrink = 1.0 - 0.16 * eio((t - 1.5) / 1.2)
    bite = clamp((t - 0.35) / 2.4)
    mx, my = 560 + 30 * eio((t - 0.2) / 1.6), 930
    paste_c(img, money_img(700, bite), mx, my + 6 * math.sin(t * 3), shrink, -4 + 2 * math.sin(t * 1.3), tag="uang")
    # Si Bocor di pojok kanan atas uang, mengunyah
    chew = abs(math.sin(t * 11)) * 8
    bx = min(850, mx + 350 * shrink - 70); by = my - 175 * shrink + 20
    paste_c(img, bocor_img(), bx, by - chew, 0.6, -14 + 6 * math.sin(t * 11), tag="bocor")
    for k in range(5):                                           # remah uang berjatuhan
        u = (t * 1.4 + k * 0.21) % 1.0
        if t < 0.4: break
        x = bx - 30 + 22 * k - 10 * u; y = by + 60 + 260 * u
        ImageDraw.Draw(img).rounded_rectangle((x, y, x + 18, y + 12), 3, fill=MONEY_G, outline=MONEY_D, width=2)
    p = pop(t, 1.5)
    if p > 0:
        paste_c(img, bubble("kriuk!", col=YEL, fg=NAVY, size=46, tail="right"), bx - 190, by - 20, p, 6,
                tag="bubble kriuk")
    draw_aru(img, 270, 1450, 440, t)
    paste_c(img, dia_img(470), 820, 1450 - 235 + 4 * math.sin(t * 5), 1.0, 0, tag="dia")


def scene1(img, t):
    """coba tebak: 12 bulan, setahun hilang berapa?"""
    p = pop(t, SC[1] + 0.05)
    if p > 0:
        T, td = head_card(800, 520, "1 TAHUN = 12 BULAN", col=NAVY, size=46)
        t0 = sg(3) - 0.2
        n = int(12 * clamp((t - t0) / 1.0) + 0.999) if t >= t0 else 0
        for k in range(12):
            x = 60 + (k % 6) * 118; y = 140 + (k // 6) * 130
            lit = k < n
            td.rounded_rectangle((x, y, x + 100, y + 110), 16, fill=(253, 228, 222) if lit else LIGHT,
                                 outline=RED if lit else (205, 210, 222), width=4)
            text_c(td, (x + 50, y + 40), str(k + 1), F("pb", 40), RED if lit else GREY_T)
            if lit:
                text_c(td, (x + 50, y + 82), "−?", F("pb", 30), RED)
        td.rounded_rectangle((60, 410, 740, 495), 26, fill=RED)
        text_c(td, (400, 452), "HILANG: Rp???", F("pb", 54), WHITE)
        paste_c(img, T, W / 2, 800, p, tag="kartu 12 bulan")
    q = pop(t, sg(3) + 0.6)
    if q > 0:
        L = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.ellipse((8, 8, 192, 192), fill=YEL, outline=NAVY, width=8)
        text_c(d, (100, 98), "?", F("pb", 110), NAVY)
        paste_c(img, L, 800, 1250, q, 8 * math.sin(t * 4), tag="lencana ?")
    draw_aru(img, 300, 1470, 360, t)


def scene2(img, t):
    """kamu pasti kenal dia: pinjam satu juta, 'Bulan depan ya, pasti!'"""
    p = pop(t, SC[2] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Kamu pasti kenal dia", "👀", fill=YEL, fg=NAVY, size=48), W / 2,
                480 + 5 * math.sin(t * 3), p, -2, tag="pill kenal dia")
    q = pop(t, SC[2] + 0.15)
    if q > 0:
        paste_c(img, dia_img(600), 330, 1150 + 6 * math.sin(2 * math.pi * 1.1 * t), q, 2 * math.sin(t * 1.6), tag="dia")
    draw_aru(img, 790, 1460, 380, t)
    if t >= sg(5) - 0.1:
        u = eio((t - sg(5)) / 0.8)
        paste_c(img, money_img(380), 700 - 300 * u, 1000 - 60 * math.sin(math.pi * u), 1.0, -6 * u, tag="uang")
    r = pop(t, sg(6) - 0.05)
    if r > 0:
        paste_c(img, bubble("\"Bulan depan ya, pasti!\"", col=RED, fg=WHITE, size=50), 540, 690,
                r * (1 + 0.03 * math.sin(t * 9)), 2, tag="bubble janji")


def scene3(img, t):
    """bulan depan lewat, tiga bulan lewat; dia malah posting liburan."""
    p = pop(t, SC[3] + 0.05)
    if p > 0:
        T, td = head_card(800, 330, "JANJI \"BULAN DEPAN\"", col=NAVY, size=44)
        marks = [sg(8) + 0.2, sg(9) - 0.05, sg(9) + 0.45, sg(10) + 0.2]
        for k in range(4):
            x = 40 + k * 185
            td.rounded_rectangle((x, 130, x + 165, 300), 18, fill=WHITE, outline=NAVY, width=4)
            td.rectangle((x + 4, 134, x + 161, 170), fill=TEAL)
            text_c(td, (x + 82, 152), "BULAN", F("pb", 24), WHITE)
            text_c(td, (x + 82, 232), str(k + 1), F("pb", 70), NAVY)
            if t >= marks[k]:
                u = clamp((t - marks[k]) / 0.2)
                td.line([(x + 20, 150), (x + 20 + 125 * u, 150 + 135 * u)], fill=RED, width=14)
                td.line([(x + 145, 150), (x + 145 - 125 * u, 150 + 135 * u)], fill=RED, width=14)
        paste_c(img, T, W / 2, 640, p, tag="kartu bulan")
    q = pop(t, sg(10) - 0.05)
    if q > 0:
        P, pd = card(340, 470, fill=(40, 44, 60), r=44, outline=NAVY, ow=6)
        pd.rounded_rectangle((20, 50, 320, 420), 20, fill=(150, 210, 240))
        pd.rectangle((20, 300, 320, 420), fill=(250, 226, 160))
        P.alpha_composite(emoji_img("🏖️", 150), (95, 110))
        pd.text((36, 440), "dia · liburan", font=F("pb", 26), fill=WHITE, anchor="lm")
        h = pop(t, sg(10) + 0.5)
        if h > 0:
            pd.ellipse((240, 316, 300, 376), fill=RED)
            pd.ellipse((254, 334, 272, 352), fill=WHITE); pd.ellipse((268, 334, 286, 352), fill=WHITE)
            pd.polygon([(255, 347), (285, 347), (270, 364)], fill=WHITE)
        paste_c(img, P, 720, 1110, q, 4 * math.sin(t * 2), tag="hp liburan")
    draw_aru(img, 320, 1440, 400, t, angle_amp=4)
    if t >= sg(10) + 0.1:
        paste_c(img, bubble("Lho?!", col=YEL, fg=NAVY, size=46), 330, 960, pop(t, sg(10) + 0.1), tag="bubble lho")


def scene4(img, t):
    """setahun kemudian uangmu balik utuh. Aman, kan?"""
    p = pop(t, SC[4] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("12 bulan kemudian…", "📅", fill=NAVY, fg=WHITE, size=48), W / 2, 480, p, -2,
                tag="pill 12 bulan")
    if t >= sg(12) - 0.2:
        u = eio((t - (sg(12) - 0.2)) / 0.9)
        paste_c(img, money_img(560), 660 - 120 * u, 800 + 60 * u, 1.0, 6 * (1 - u), tag="uang")
        if u >= 1:
            paste_c(img, stamp("UTUH", col=GREEN, size=64), 760, 1060, pop(t, sg(12) + 0.7), -8, tag="stempel utuh")
    draw_aru(img, 320, 1460, 400, t)
    r = pop(t, sg(13) - 0.05)
    if r > 0:
        paste_c(img, bubble("Aman, kan?", col=NAVY, fg=YEL, size=52), 640, 1220, r, tag="bubble aman")


def scene5(img, t):
    """tunggu dulu: inflasi tahunan BPS Oktober 3,23%."""
    p = pop(t, SC[5] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Tunggu dulu…", "⏳", fill=YEL, fg=NAVY, size=52), W / 2, 480, p, 3, tag="pill tunggu")
    q = pop(t, sg(15) - 0.05)
    if q > 0:
        T, td = head_card(800, 520, "INFLASI TAHUNAN · OKT 2026", col=RED, size=44)
        u = eout((t - sg(16)) / 0.8) if t >= sg(16) - 0.05 else 0
        v = 3.23 * u
        text_c(td, (400, 270), f"{v:.2f}%".replace(".", ",") if u > 0 else "?,??%", F("pb", 190), RED)
        text_c(td, (400, 440), "harga-harga naik dalam setahun", F("pm", 38), GREY_T)
        if u > 0:
            arrow(td, 700, 360, 700, 360 - 170 * u, RED, w=16, head=36)
        paste_c(img, T, W / 2, 820, q, tag="kartu inflasi")
    draw_aru(img, 300, 1470, 300, t)


def scene6(img, t):
    """kalau harga naik segitu, daya beli satu jutamu tinggal…"""
    p = pop(t, SC[6] + 0.05)
    if p > 0:
        T, td = head_card(800, 640, "Rp1 JUTA, SETAHUN LAGI", col=NAVY, size=46)
        base = 560; hmax = 380
        u1 = eout((t - sg(17) - 0.5) / 0.8)
        u2 = eout((t - sg(18) - 0.2) / 0.9)
        for x, lab, v0, v1, u, col in ((220, "HARGA", 100, 103.23, u1, RED), (580, "DAYA BELI", 100, 96.87, u2, TEAL)):
            v = v0 + (v1 - v0) * u
            h = hmax * (v - 90) / 14
            td.rounded_rectangle((x - 110, base - h, x + 110, base), 22, fill=col, outline=NAVY, width=5)
            text_c(td, (x, base - h - 34), lab, F("pb", 36), NAVY)
            if u > 0:
                arrow(td, x + 140, base - h + 20, x + 140,
                      base - h + 20 + (-90 if col == RED else 90) * u, col, w=12, head=28)
        dashed(td, [(80, base - hmax * 10 / 14), (720, base - hmax * 10 / 14)], (170, 178, 195), w=4)
        text_c(td, (400, base - hmax * 10 / 14 - 20), "hari ini", F("pm", 26), GREY_T)
        paste_c(img, T, W / 2, 860, p, tag="kartu daya beli")
    q = pop(t, sg(18) + 1.2)
    if q > 0:
        L = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.ellipse((8, 8, 192, 192), fill=YEL, outline=NAVY, width=8)
        text_c(d, (100, 98), "?", F("pb", 110), NAVY)
        paste_c(img, L, 800, 1300, q, 8 * math.sin(t * 4), tag="lencana ?")


def peak_value(t):
    u = eio((t - P0) / (P1 - P0)) if t >= P0 else 0.0
    return 968700 if u >= 1 else int(round((1000000 - 31300 * u) / 100.0) * 100)


def scene7(img, t):
    """PUNCAK: daya beli Rp1 jt setelah setahun -> Rp968.700 (counter berhenti, ditahan sampai adegan 8)."""
    p = pop(t, SC[7] + 0.05)
    if p > 0:
        T, td = card(800, 460, fill=WHITE, outline=RED, ow=8)
        text_c(td, (400, 66), "DAYA BELI Rp1 JT", F("pb", 52), RED)
        text_c(td, (400, 122), "setelah setahun dipinjam", F("pm", 38), GREY_T)
        td.rounded_rectangle((40, 170, 760, 360), 30, fill=RED)
        text_c(td, (400, 266), rp(peak_value(t)), F("pb", 120), WHITE)
        if t >= P1:
            text_c(td, (400, 412), "−Rp31.300", F("pb", 50), RED)
        paste_c(img, T, W / 2, 720, p * (1 + 0.02 * math.sin(t * 8)), -1.5, tag="kartu puncak")


def scene8(img, t):
    """Rp31 ribu menguap tanpa ada yang nyolong: Si Bocor kabur membawa koin −Rp31.300."""
    T, td = card(640, 190, fill=WHITE, outline=RED, ow=6)
    text_c(td, (320, 50), "daya beli tinggal", F("pm", 34), GREY_T)
    text_c(td, (320, 124), "Rp968.700", F("pb", 84), RED)
    paste_c(img, T, W / 2, 560, 1.0, 0, tag="kartu 968.700")
    u = clamp((t - SC[8] - 0.2) / 2.6)
    bx = 300 + 560 * eio(u)
    hop = abs(math.sin(t * 9)) * 14
    C = Image.new("RGBA", (300, 120), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
    cd.rounded_rectangle((0, 0, 300, 110), 55, fill=(255, 194, 60), outline=(217, 154, 31), width=6)
    text_c(cd, (150, 56), "−Rp31.300", F("pb", 50), (120, 80, 10))
    C.info["nw"] = 300
    paste_c(img, C, min(800, bx - 10), 860 - hop, 1.0, -6, tag="koin 31.300")
    paste_c(img, bocor_img(), min(830, bx + 40), 1050 - hop, 0.7, 4 * math.sin(t * 9), tag="bocor")
    r = pop(t, sg(21) - 0.05)
    if r > 0:
        paste_c(img, pill_emoji("menguap", "💨", fill=YEL, fg=NAVY, size=50), 360, 1350, r, -4, tag="pill menguap")


def scene9(img, t):
    """belum selesai: deposito berbunga 3,75% (bunga penjaminan LPS)."""
    p = pop(t, SC[9] + 0.05)
    if p > 0:
        paste_c(img, pill("BELUM SELESAI…", fill=NAVY, fg=YEL, size=54), W / 2, 480, p, -2, tag="pill belum")
    q = pop(t, SC[9] + 0.3)
    if q > 0:
        T, td = head_card(800, 520, "KALAU DI DEPOSITO", col=GREEN, size=48)
        T.alpha_composite(emoji_img("🏦", 90), (36, 120))
        u = eout((t - sg(23) - 1.2) / 0.8) if t >= sg(23) + 1.15 else 0
        text_c(td, (430, 280), f"{3.75 * u:.2f}%".replace(".", ",") if u > 0 else "?,??%", F("pb", 170), GREEN)
        text_c(td, (400, 440), "bunga setahun (LPS)", F("pm", 40), GREY_T)
        paste_c(img, T, W / 2, 900, q, tag="kartu deposito")


def dep_value(t):
    u = eout((t - D0) / (D1 - D0)) if t >= D0 else 0.0
    return 37500 if u >= 1 else int(round(37500 * u / 100.0) * 100)


def scene10(img, t):
    """satu jutamu malah tumbuh Rp37.500 (counter berhenti, ditahan sampai adegan 11)."""
    p = pop(t, SC[10] + 0.05)
    if p > 0:
        T, td = card(800, 520, fill=WHITE, outline=GREEN, ow=8)
        text_c(td, (400, 66), "Rp1 JT DI DEPOSITO", F("pb", 52), GREEN)
        text_c(td, (400, 122), "setahun malah tumbuh", F("pm", 38), GREY_T)
        td.rounded_rectangle((40, 170, 760, 360), 30, fill=GREEN)
        text_c(td, (400, 266), "+" + rp(dep_value(t)), F("pb", 120), WHITE)
        if t >= D1:
            text_c(td, (400, 440), "= Rp1.037.500", F("pb", 60), NAVY)
        paste_c(img, T, W / 2, 780, p * (1 + 0.02 * math.sin(t * 8)), 1.2, tag="kartu deposito tumbuh")
    draw_aru(img, 290, 1470, 300, t)


def scene11(img, t):
    """jadi dia pinjam tanpa bunga, kamu yang nanggung: dua batang Rp968.700 vs Rp1.037.500."""
    d = ImageDraw.Draw(img)
    base, hmax = 1300, 640
    bars = [(330, "DIPINJAM TEMAN", "Rp968.700", 968.7, RED, "−Rp31.300"),
            (750, "DI DEPOSITO", "Rp1.037.500", 1037.5, GREEN, "+Rp37.500")]
    for k, (x, lab, val, v, col, dv) in enumerate(bars):
        u = eout((t - SC[11] - 0.05 - 0.15 * k) / 0.6)
        if u <= 0: continue
        h = (hmax * (v - 700) / 340) * u
        d.rounded_rectangle((x - 150 + 8, base - h + 10, x + 150 + 8, base + 10), 26, fill=(20, 33, 91, 60))
        d.rounded_rectangle((x - 150, base - h, x + 150, base), 26, fill=col, outline=NAVY, width=5)
        text_c(d, (x, base - h + 56), val, fit("pb", 52, val, 280), WHITE)
        text_c(d, (x, base - h + 116), dv, fit("pb", 42, dv, 280), YEL if col == RED else WHITE)
        text_c(d, (x, base + 44), lab, fit("pb", 38, lab, 300), NAVY)
        track("batang " + lab, 300, x - 150, x + 150)
    d.line([(160, base), (920, base)], fill=NAVY, width=6)
    q = pop(t, sg(27) - 0.05)
    if q > 0:
        paste_c(img, stamp("KAMU YANG NANGGUNG", col=RED, size=54), W / 2, 520, q, -4, tag="stempel nanggung")


SPLIT_Y = 470
ARGS_L = [("Nagih teman", "itu CANGGUNG", "😬"),
          ("Rp30 ribuan vs", "PERTEMANAN", "🤝"),
          ("Dia juga pernah", "NOLONGIN kamu", "🫶")]


def split(img, t, k):
    """layar terbelah: kiri tim NUNGGU, kanan tim LANGSUNG TAGIH; sisi aktif terang."""
    right = k == 15
    d = ImageDraw.Draw(img)
    cols = [(140, 530, TEAL, "NUNGGU"), (550, 940, RED, "LANGSUNG TAGIH")]
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
    nL = {12: 1, 13: 2, 14: 3}.get(k, 3)
    starts = [SC[12] + 0.3, SC[13] + 0.1, SC[14] + 0.1]
    for i in range(nL):
        a1, a2, em = ARGS_L[i]
        p = pop(t, starts[i])
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
    if k < 15:
        text_c(d, (745, 1000), "?", F("pb", 160), (200, 205, 216))
        return
    p = pop(t, SC[15] + 0.1)
    C = Image.new("RGBA", (360, 600), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
    cd.rounded_rectangle((0, 0, 360, 590), 24, fill=(253, 236, 232), outline=RED, width=5)
    C.alpha_composite(emoji_img("🙅", 110), (125, 26))
    lines = (("Justru karena", NAVY, sg(33) - 0.1), ("TEMAN,", RED, sg(33) + 0.5), ("jangan biarkan", NAVY, sg(34) - 0.1),
             ("utang jadi", NAVY, sg(34) + 0.6), ("GANJALAN", RED, sg(34) + 1.2))
    for j, (s_, col, t0) in enumerate(lines):
        if t >= t0:
            text_c(cd, (180, 200 + j * 72), s_, fit("pb", 42, s_, 330), col)
    C.info["nw"] = 360
    paste_c(img, C, 745, SPLIT_Y + 470, p, tag="argumen kanan")


def scene12(img, t): split(img, t, 12)
def scene13(img, t): split(img, t, 13)
def scene14(img, t): split(img, t, 14)
def scene15(img, t): split(img, t, 15)


def scene16(img, t):
    """jalan tengah: ubah 'bulan depan' jadi tanggal, sejak awal."""
    p = pop(t, SC[16] + 0.05)
    if p > 0:
        paste_c(img, pill("JALAN TENGAH", fill=YEL, fg=NAVY, size=60), W / 2, 480, p, -2, tag="pill jalan tengah")
    q = pop(t, SC[16] + 0.35)
    if q > 0:
        B = bubble("\"Bulan depan ya\"", col=(150, 156, 176), fg=WHITE, size=50)
        bd = ImageDraw.Draw(B)
        if t >= sg(36) + 0.4:
            u = clamp((t - sg(36) - 0.4) / 0.25)
            bd.line([(20, 55), (20 + (B.width - 40) * u, 55)], fill=RED, width=12)
        B.info["nw"] = B.width
        paste_c(img, B, W / 2, 700, q, -2, tag="bubble bulan depan")
    r = pop(t, sg(37) - 0.05)
    if r > 0:
        T, td = card(420, 440, fill=WHITE, outline=NAVY, ow=6)
        td.rounded_rectangle((0, 0, 420, 110), 30, fill=RED); td.rectangle((0, 60, 420, 110), fill=RED)
        text_c(td, (210, 56), "BALIKIN TGL", F("pb", 44), WHITE)
        text_c(td, (210, 270), "25", F("pb", 200), NAVY)
        if t >= sg(37) + 0.4:
            u = clamp((t - sg(37) - 0.4) / 0.4)
            td.arc((70, 150, 350, 400), -90, -90 + 360 * u, fill=YEL, width=14)
        paste_c(img, T, 400, 1100, r, 3, tag="kalender 25")
    s = pop(t, sg(38) - 0.05)
    if s > 0:
        paste_c(img, stamp("SEJAK AWAL", col=GREEN, size=50), 740, 1330, s, -8, tag="stempel sejak awal")


def scene17(img, t):
    """lewat tanggal, ingatkan santai lewat chat pribadi, bukan sindiran grup."""
    p = pop(t, SC[17] + 0.05)
    if p > 0:
        T, td = card(760, 600, fill=(236, 244, 240), r=40, outline=NAVY, ow=6)
        td.rounded_rectangle((0, 0, 760, 100), 40, fill=TEAL); td.rectangle((0, 50, 760, 100), fill=TEAL)
        td.ellipse((30, 20, 90, 80), fill=WHITE)
        text_c(td, (60, 50), "D", F("pb", 36), TEAL)
        td.text((110, 50), "Chat pribadi · Dia", font=F("pb", 38), fill=WHITE, anchor="lm")
        if t >= sg(39) + 0.5:
            u = pop(t, sg(39) + 0.5)
            m = "Hai, udah tgl 25 nih,"
            m2 = "balikin ya"
            td.rounded_rectangle((200, 150, 730, 300), 26, fill=(214, 246, 200))
            td.text((230, 195), m, font=F("pm", 38), fill=NAVY, anchor="lm")
            td.text((230, 255), m2, font=F("pm", 38), fill=NAVY, anchor="lm")
            T.alpha_composite(emoji_img("🙏", 46), (470, 232))
        if t >= sg(39) + 1.8:
            td.rounded_rectangle((30, 340, 420, 440), 26, fill=WHITE)
            td.text((60, 390), "Siap, maaf ya!", font=F("pm", 38), fill=NAVY, anchor="lm")
        paste_c(img, T, W / 2, 800, p, tag="chat pribadi")
    q = pop(t, sg(40) - 0.1)
    if q > 0:
        T, td = card(760, 190, fill=(240, 242, 246), r=30, outline=(200, 205, 216), ow=4)
        td.text((40, 60), "Grup · Geng Nongkrong", font=F("pb", 32), fill=GREY_T, anchor="lm")
        td.text((40, 130), "\"Ada yang lupa bayar utang nih…\"", font=fit("pm", 34, "\"Ada yang lupa bayar utang nih…\"", 680),
                fill=GREY_T, anchor="lm")
        if t >= sg(40) + 0.2:
            u = clamp((t - sg(40) - 0.2) / 0.25)
            td.line([(30, 30), (30 + 700 * u, 30 + 130 * u)], fill=RED, width=14)
            td.line([(730, 30), (730 - 700 * u, 30 + 130 * u)], fill=RED, width=14)
        paste_c(img, T, W / 2, 1290, q, -2, tag="grup coret")


def scene18(img, t):
    """penutup: Tim TAGIH atau tim NUNGGU? Komen!"""
    for k, (s, col, t0) in enumerate((("TIM LANGSUNG TAGIH", RED, SC[18] + 0.05), ("TIM NUNGGU", TEAL, sg(42)))):
        p = pop(t, t0)
        if p <= 0: continue
        beat = 1 + 0.04 * math.sin((t - t0) * 7 + k * math.pi)
        paste_c(img, pill(s, fill=col, fg=WHITE, size=54, h=116), W / 2, 520 if k == 0 else 720, p * beat,
                -2 if k == 0 else 2, tag=s)
    if t >= sg(42):
        text_c(ImageDraw.Draw(img), (W / 2, 620), "atau", F("pb", 40), NAVY)
    p = pop(t, sg(42) + 0.4)
    if p > 0:
        B = Image.new("RGBA", (800, 250), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 800, 200), 34, fill=YEL, outline=NAVY, width=5)
        bd.polygon([(110, 196), (180, 196), (90, 246)], fill=YEL, outline=NAVY)
        bd.line([(112, 197), (178, 197)], fill=YEL, width=8)
        s = "Tim TAGIH atau tim NUNGGU?"
        text_c(bd, (400, 66), s, fit("pb", 48, s, 740), NAVY)
        text_c(bd, (400, 140), "Komen!", F("pb", 60), NAVY)
        B.info["nw"] = 800
        paste_c(img, B, W / 2, 940, p, tag="bubble komen")
    draw_aru(img, W / 2, 1470, 330, t)


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10, scene11,
          scene12, scene13, scene14, scene15, scene16, scene17, scene18]
assert len(SCENES) == NS


@lru_cache(None)
def header():
    L = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F("pb", 34); s1 = "MANA LEBIH HEMAT?"; s2 = "#9"
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


def share_card(img, t):
    """ajakan kirim di puncak angka (PRB-55 poin 3), 2 baris, teal."""
    if not (SHARE[0] <= t < SHARE[1]): return
    a = min(clamp((t - SHARE[0]) / 0.25), clamp((SHARE[1] - t) / 0.25))
    s = 0.85 + 0.15 * back((t - SHARE[0]) / 0.35)
    T, td = card(800, 190, fill=TEAL)
    e = emoji_img("📤", 70)
    text_c(td, (360, 62), "Kirim ke teman yang masih", F("pb", 44), WHITE)
    text_c(td, (360, 128), "punya utang ke kamu", F("pb", 50), YEL)
    T.alpha_composite(e, (690, 58))
    paste_c(img, T, W / 2, 1290 + 4 * math.sin(t * 5), s, 0, a, tag="kartu kirim")


FOLLOW_S = "follow @kabar.arunika · tiap pagi 1 hitungan uang"


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
        img.alpha_composite(Hd, (0, 240))  # header y≈300 (PRB-41); baru setelah dtk 3
        track("header", hx1 - hx0, hx0, hx1)
    else:
        scene0(img, t)
        if t >= CT0:                       # label ilustrasi untuk Rp1 juta
            a = clamp((t - CT0) / 0.3)
            L = Image.new("RGBA", (W, 60), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
            f = fit("pm", 28, ILU, MAXW)
            ld.text((W / 2, 30), ILU, font=f, fill=INK, anchor="mm")
            track("catatan", f.getlength(ILU), W / 2 - f.getlength(ILU) / 2, W / 2 + f.getlength(ILU) / 2)
            paste_c(img, L, W / 2, 1712, 1, 0, a)
    share_card(img, t)
    draw_sub(img, t)
    if k > 0 and k in NOTES:
        note_lines(img, NOTES[k])
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
    ev.append({"t": 0.4, "sfx": "pop", "gain": 0.3})            # gigitan pertama
    ev.append({"t": 1.5, "sfx": "pop", "gain": 0.32})           # "kriuk!"
    ev.append({"t": CT1, "sfx": "ding", "gain": 0.25})          # counter berhenti Rp9??.???
    for si in (3, 5, 6, 8, 9, 10, 12, 13, 15, 16, 18, 21, 23, 26, 27, 29, 33, 34, 36, 37, 38, 40, 42):
        ev.append({"t": sg(si), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": sg(5), "sfx": "cring", "gain": 0.35})       # uang diserahkan
    ev.append({"t": P0, "sfx": "cring", "gain": 0.45})          # counter puncak
    ev.append({"t": P1, "sfx": "ding", "gain": 0.35})           # Rp968.700
    ev.append({"t": SC[8] + 0.2, "sfx": "cring", "gain": 0.4})  # Si Bocor kabur
    ev.append({"t": D1, "sfx": "ding", "gain": 0.3})            # +Rp37.500
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
        print("puncak", round(P1, 2), "->", round(SC[9], 2), "| deposito", round(D1, 2), "->", round(SC[12], 2))
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

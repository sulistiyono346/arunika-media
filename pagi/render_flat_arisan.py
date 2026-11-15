"""Renderer ARN-51 "Mana Lebih Hemat? #10 — arisan dapat pertama vs terakhir" — Flat 2D latar terang (PRB-31).
Salinan render_flat_pinjam.py (helper kartu, koin, Si Bocor, pill, bubble, stempel, subtitle, cek area aman, sfx) dengan:
- frame 0 (PRB-36): satu adegan + satu aksi — Aru membuka gulungan kertas arisan besar "10" (kaget), Si Bocor
  menggerogoti koin emas ("kriuk!"); satu counter besar dari Rp0 turun dan BERHENTI di "−Rp7?.???" dtk 2,0
  (nilai akhir −Rp70.300 dibuka di adegan 9). Judul layar hanya pill kecil "Urutan arisan, diam-diam MAHAL".
  Tanpa label seri/logo/progress bar dtk 0-3; visual berganti ~dtk 1,5 (gulungan terbuka penuh + gigitan).
- 19 adegan (tiap <= 6 dtk); counter 3,75% (adegan 7), −Rp70.300 (adegan 9, ditahan di adegan 10), +Rp70.300
  (adegan 10), ±Rp140 RIBU (adegan 11, PUNCAK) berhenti di nilai akhir >= 1,5 dtk; sumber kecil LPS 3,75%;
  "*angka contoh ilustrasi"; ajakan kirim di puncak; layar terbelah tim ARISAN vs tim NABUNG SENDIRI (12-15).
- area aman (PRB-41): semua pill/bubble/kartu <= 800 px dan di x 130..950; `check` memindai tiap 0,1 dtk.
Pemakaian (dari folder kerja pagi/build_arisan, setelah align_arisan.py -> timing.json):
  TOTAL=68.4 python3 ../render_flat_arisan.py events | check | scenes | stills 0,2,... | video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, rp, NAVY, TEAL, YEL, WHITE, GREY_T, RED, SAFE_X)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "68.4"))
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


SCENE_SEG = [0, 1, 3, 7, 8, 12, 13, 16, 17, 18, 19, 21, 23, 25, 27, 28, 30, 33, 36]
SC = [0.0] + [sg(i) - 0.25 for i in SCENE_SEG[1:]] + [TOTAL]
NS = len(SCENE_SEG)
FOLLOW = (10.6, 15.0)          # PRB-4: ajakan follow teks kecil dtk 10-15 (adegan 3-4)
PB_START = 3.5                 # progress bar mulai dtk 3,5
ILU = "*angka contoh ilustrasi"
SRC_LPS = ("Bunga penjaminan LPS bank umum, periode 1 Okt 2026–Jan 2027",
           "detikFinance 3 Nov 2026 · bunga tiap bank bisa lebih rendah")
DEP_NOTE = "bunga 3,75%/thn, setor awal bulan selama 10 bulan, sebelum pajak, dibulatkan"
NOTES = {1: (ILU,), 4: (ILU,), 5: (ILU,), 6: (ILU,), 7: SRC_LPS, 8: (DEP_NOTE, ILU), 9: (DEP_NOTE, ILU),
         10: ("saldo Rp4,5 jt turun ke 0 selama 9 bulan · bunga 3,75%/thn · dibulatkan", ILU),
         11: ("selisih no. 1 vs no. 10 (Rp140.625), contoh ilustrasi, dibulatkan",),
         15: ("tgl 25 = tanggal contoh · " + ILU,)}
CT0, CT1 = 0.45, 2.0                       # counter frame 0: turun lalu BERHENTI di "−Rp7?.???" dtk 2,0
L0, L1 = sg(16) + 1.2, sg(16) + 2.0        # 3,75%
D0, D1 = sg(18) + 1.0, sg(18) + 1.8        # no. 10: −Rp70.300 (ditahan sampai akhir adegan 10)
G0, G1 = SC[10] + 0.3, SC[10] + 1.1        # no. 1: +Rp70.300
P0, P1 = sg(21) + 0.5, sg(22) - 0.15       # PUNCAK ±Rp140 RIBU
SHARE = (P1 + 0.1, SC[12] + 0.8)           # ajakan kirim di puncak angka
PAPER, PAPER_D = (255, 246, 232), (226, 206, 170)
GOLD, GOLD_D = (255, 194, 60), (217, 154, 31)


def scene_of(t):
    for k in range(NS):
        if t < SC[k + 1]: return k
    return NS - 1


def note_lines(img, lines, y0=1712):
    d = ImageDraw.Draw(img)
    for j, s in enumerate(lines):
        f = fit("pm", 28, s, MAXW)
        track("catatan", f.getlength(s), W / 2 - f.getlength(s) / 2, W / 2 + f.getlength(s) / 2)
        d.text((W / 2, y0 + j * 40), s, font=f, fill=GREY_T, anchor="mm")


def scroll_img(w, num, unroll=1.0, col=RED, label="URUTAN"):
    """gulungan kertas arisan: dua gulungan (atas/bawah), kertas terbuka sebesar unroll (0..1)."""
    hmax = int(w * 1.05); hh = int(hmax * (0.18 + 0.82 * clamp(unroll)))
    rr = int(w * 0.09)
    im = Image.new("RGBA", (w + 40, hh + 2 * rr + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, x1 = 20, w + 20; y0 = rr; y1 = rr + hh
    d.rectangle((x0 + 14, y0 + 10, x1 + 14, y1 + 10), fill=(20, 33, 91, 40))
    d.rectangle((x0 + 12, y0, x1 - 12, y1), fill=PAPER, outline=NAVY, width=6)
    for k in range(4):
        yy = y0 + 30 + k * (hh - 60) / 3
        if 30 < yy - y0 < hh - 30:
            d.line([(x0 + 40, yy), (x0 + 90, yy)], fill=PAPER_D, width=4)
    if unroll > 0.45:
        a = clamp((unroll - 0.45) / 0.4)
        f = F("pb", int(w * 0.62 * (0.7 + 0.3 * a)))
        cy = (y0 + y1) / 2 + int(w * 0.06)
        text_c(d, (x0 + w / 2, cy), num, f, col)
        text_c(d, (x0 + w / 2, y0 + int(w * 0.13)), label, F("pb", int(w * 0.09)), GREY_T)
    for yy in (y0, y1):
        d.rounded_rectangle((0, yy - rr, w + 40, yy + rr), rr, fill=PAPER_D, outline=NAVY, width=6)
        d.ellipse((w + 40 - 2 * rr + 8, yy - rr + 8, w + 40 - 8, yy + rr - 8), outline=NAVY, width=4)
    im.info["nw"] = w + 40
    return im


def gold_coin(r, bite=0.0, label="Rp"):
    im = Image.new("RGBA", (2 * r + 10, 2 * r + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((5, 5, 2 * r + 5, 2 * r + 5), fill=GOLD, outline=GOLD_D, width=max(4, r // 10))
    d.ellipse((5 + r * 0.22, 5 + r * 0.22, 2 * r + 5 - r * 0.22, 2 * r + 5 - r * 0.22), outline=GOLD_D, width=4)
    text_c(d, (r + 5, r + 5), label, F("pb", int(r * 0.6)), (154, 106, 16))
    if bite > 0.01:
        a = im.getchannel("A"); ad = ImageDraw.Draw(a)
        pts = [(2 * r - 4, r * 0.45), (2 * r + 4, r * 0.95), (2 * r - 10, r * 1.45), (2 * r - 30, r * 0.7)]
        n = bite * len(pts)
        for k, (x, y) in enumerate(pts):
            f = clamp(n - k)
            if f <= 0: break
            rr = r * 0.32 * f
            ad.ellipse((x - rr, y - rr, x + rr, y + rr), fill=0)
        im.putalpha(a)
    return im


def big_card_counter(title, sub, value, col, done, extra=None, w=800, h=470):
    T, td = card(w, h, fill=WHITE, outline=col, ow=8)
    text_c(td, (w / 2, 64), title, fit("pb", 50, title, w - 60), col)
    if sub: text_c(td, (w / 2, 120), sub, fit("pm", 36, sub, w - 60), GREY_T)
    td.rounded_rectangle((40, 160, w - 40, 350), 30, fill=col)
    text_c(td, (w / 2, 256), value, fit("pb", 120, value, w - 120), WHITE)
    if done and extra:
        text_c(td, (w / 2, 410), extra, fit("pb", 46, extra, w - 60), NAVY)
    return T


def counter0(t):
    """Rp0 turun; berhenti & disamarkan jadi −Rp7?.??? di dtk 2,0 (nilai asli −Rp70.300 dibuka di adegan 9)."""
    if t < CT0: return "Rp0", False
    if t >= CT1: return "−Rp7?.???", True
    u = eio((t - CT0) / (CT1 - CT0))
    v = 70300 * u + ((137 * int(t * 30)) % 900) * u * (1 - u)
    return "−" + rp(int(round(v / 100.0) * 100)), False


def title_pill(img):
    """judul layar = pill kecil (bukan kartu judul besar, PRB-36): 'Urutan arisan, diam-diam MAHAL'."""
    f = F("pb", 40); a = "Urutan arisan, diam-diam "; b = "MAHAL"
    wa, wb = f.getlength(a), f.getlength(b); w = int(wa + wb + 24 + 60); h = 82
    P = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    d.rounded_rectangle((8, 10, w + 8, h + 10), h // 2, fill=(20, 33, 91, 55))
    d.rounded_rectangle((0, 0, w, h), h // 2, fill=NAVY)
    d.text((30, h / 2 + 2), a, font=f, fill=WHITE, anchor="lm")
    d.rounded_rectangle((30 + wa - 4, 12, 30 + wa + wb + 20, h - 12), 14, fill=YEL)
    d.text((30 + wa + 8, h / 2 + 2), b, font=f, fill=NAVY, anchor="lm")
    P.info["nw"] = w
    paste_c(img, P, W / 2, 320, tag="pill judul")


def counter_card(img, t, cy, s, done, hot, scale=1.0):
    f = F("pb", 112)
    L, d = card(780, 200, fill=(253, 228, 222) if hot else WHITE, outline=RED if hot else NAVY, ow=7)
    text_c(d, (360 if hot else 390, 102), s, f, RED if hot else NAVY)
    if hot and not done:
        arrow(d, 720, 45, 720, 45 + 110 * clamp((t - CT0) / 0.3), RED, w=18, head=38)
    paste_c(img, L, W / 2, cy, scale, tag="counter")


def surprise(img, x, y, t, t0):
    p = pop(t, t0)
    if p <= 0: return
    d = ImageDraw.Draw(img)
    for k, (dx, dy, ang) in enumerate(((-60, 0, -25), (0, -30, 0), (60, 0, 25))):
        L = Image.new("RGBA", (40, 90), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.rounded_rectangle((10, 0, 30, 55), 8, fill=RED); ld.ellipse((10, 64, 30, 84), fill=RED)
        paste_c(img, L, x + dx * p, y + dy * p - 4 * math.sin(t * 9 + k), p, ang)


def scene0(img, t):
    """frame 0: Aru membuka gulungan arisan "10" (kaget), Si Bocor menggerogoti koin, counter turun & berhenti."""
    title_pill(img)
    s, done = counter0(t)
    hot = t >= CT0
    sc = 1.0 + (0.06 * back((t - CT1) / 0.3) - 0.06 * clamp((t - CT1 - 0.3) / 0.3) if t >= CT1 else 0)
    counter_card(img, t, 520, s, done, hot, sc)
    # gulungan terbuka: 0,2 -> 1,5 dtk (visual berganti ~1,5: "10" tampil penuh + gigitan koin)
    un = eio((t - 0.1) / 1.4)
    S = scroll_img(440, "10", un)
    paste_c(img, S, 600, 980 + 4 * math.sin(t * 2.5), 1.0 + 0.05 * pop(t, 1.5) - 0.05 * clamp((t - 1.85) / 0.3),
            -3 + 1.5 * math.sin(t * 1.4), tag="gulungan 10")
    draw_aru(img, 290, 1450, 430, t)
    surprise(img, 290, 1000, t, 1.5)
    # Si Bocor menggerogoti koin emas di kanan bawah
    chew = abs(math.sin(t * 11)) * 8
    bx, by = 800, 1310
    paste_c(img, gold_coin(70, clamp((t - 0.35) / 2.2)), bx - 110, by - 40 - chew * 0.5, 1.0, 10 * math.sin(t * 3),
            tag="koin")
    paste_c(img, bocor_img(), bx, by - chew, 0.6, -10 + 6 * math.sin(t * 11), tag="bocor")
    for k in range(5):                                           # remah koin berjatuhan
        if t < 0.4: break
        u = (t * 1.4 + k * 0.21) % 1.0
        x = bx - 60 + 18 * k - 10 * u; y = by + 10 + 120 * u
        ImageDraw.Draw(img).ellipse((x, y, x + 14, y + 14), fill=GOLD, outline=GOLD_D, width=2)
    p = pop(t, 1.5)
    if p > 0:
        paste_c(img, bubble("kriuk!", col=YEL, fg=NAVY, size=46, tail="right"), 720, 1140, p, 6, tag="bubble kriuk")


def scene1(img, t):
    """coba tebak, berapa? counter tersamar tetap tampil (nilai baru dibuka di adegan 9)."""
    counter_card(img, t, 560, "−Rp7?.???", True, True)
    p = pop(t, SC[1] + 0.05)
    if p > 0:
        paste_c(img, scroll_img(300, "10", 1.0), 640, 1000, p, 4, tag="gulungan 10")
    q = pop(t, sg(2) - 0.05)
    if q > 0:
        L = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.ellipse((8, 8, 192, 192), fill=YEL, outline=NAVY, width=8)
        text_c(d, (100, 98), "?", F("pb", 110), NAVY)
        paste_c(img, L, 820, 800, q, 8 * math.sin(t * 4), tag="lencana ?")
    draw_aru(img, 300, 1470, 380, t)


def glass_img(n_in=8):
    im = Image.new("RGBA", (300, 380), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(n_in):
        x = 70 + (k % 4) * 42; y = 220 + (k // 4) * 52
        d.rounded_rectangle((x, y, x + 34, y + 70), 10, fill=PAPER, outline=NAVY, width=3)
    d.polygon([(20, 20), (280, 20), (240, 370), (60, 370)], fill=(190, 225, 245, 120))
    d.line([(20, 20), (60, 370), (240, 370), (280, 20)], fill=NAVY, width=7)
    d.ellipse((20, 6, 280, 36), outline=NAVY, width=6)
    d.line([(50, 60), (80, 330)], fill=(255, 255, 255, 200), width=10)
    im.info["nw"] = 300
    return im


def scene2(img, t):
    """kamu pasti kenal: gelas dikocok, 'Bu Yanti!', semua tepuk tangan."""
    p = pop(t, SC[2] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Kamu pasti kenal", "👀", fill=YEL, fg=NAVY, size=48), W / 2, 480, p, -2,
                tag="pill kenal")
    shake = 0.0
    if sg(4) - 0.1 <= t < sg(5) - 0.2:
        shake = 14 * math.sin((t - sg(4)) * 34)
    q = pop(t, SC[2] + 0.2)
    if q > 0:
        paste_c(img, glass_img(), 420, 900 + abs(shake) * 0.6, q, shake, tag="gelas")
    # satu gulungan jatuh keluar
    tf = sg(5) - 0.3
    if t >= tf:
        u = eout((t - tf) / 0.5)
        paste_c(img, scroll_img(150, "B", 1.0, col=TEAL, label="NAMA"), 560 + 160 * u, 760 + 360 * u - 160 * math.sin(math.pi * u),
                1.0, 200 * (1 - u), tag="gulungan jatuh")
    r = pop(t, sg(5) - 0.05)
    if r > 0:
        paste_c(img, bubble("\"Bu Yanti!\"", col=RED, fg=WHITE, size=56, tail="right"), 640, 660,
                r * (1 + 0.03 * math.sin(t * 9)), 3, tag="bubble yanti")
    for k, (x, y, t0) in enumerate(((260, 1250, sg(6) - 0.05), (560, 1330, sg(6) + 0.2), (860, 1240, sg(6) + 0.45))):
        e = pop(t, t0)
        if e > 0:
            paste_c(img, emoji_img("👏", 120), x, y - 10 * abs(math.sin(t * 10 + k)), e, 10 * math.sin(t * 10 + k))
    draw_aru(img, 820, 1460, 340, t)


NAMES = ["Bu Yanti", "Bu Rina", "Bu Sri", "Bu Ani", "Bu Tini", "Bu Lilis", "Bu Dewi", "Bu Nur", "Bu Wati", "???"]


def scene3(img, t):
    """selalu ada satu nama yang keluar paling akhir: 9 tercentang, 1 tersisa."""
    p = pop(t, SC[3] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Kamu pasti kenal dia", "👀", fill=YEL, fg=NAVY, size=46), W / 2, 470, p, -2,
                tag="pill kenal dia")
    d = ImageDraw.Draw(img)
    for k, nm in enumerate(NAMES):
        x0 = 150 if k % 2 == 0 else 555; y0 = 560 + (k // 2) * 160
        t0 = SC[3] + 0.15 + 0.13 * k
        if t < t0: continue
        last = k == 9
        hot = last and t >= sg(7) + 1.3
        fill = (253, 228, 222) if hot else (WHITE if last else (232, 246, 238))
        d.rounded_rectangle((x0 + 8, y0 + 10, x0 + 383, y0 + 130), 26, fill=(20, 33, 91, 40))
        d.rounded_rectangle((x0, y0, x0 + 375, y0 + 120), 26, fill=fill, outline=RED if hot else NAVY, width=5)
        text_c(d, (x0 + 60, y0 + 60), str(k + 1), F("pb", 44), RED if last else GREEN)
        d.text((x0 + 110, y0 + 60), nm, font=F("pb", 40), fill=RED if last else NAVY, anchor="lm")
        if not last:
            icon_check(d, x0 + 325, y0 + 60, 0.6)
        track("nama", 375, x0, x0 + 375)
    s = pop(t, sg(7) + 1.3)
    if s > 0:
        paste_c(img, stamp("PALING AKHIR", col=RED, size=48), 742, 1430 - 30, s, -6, tag="stempel akhir")


def scene4(img, t):
    """tiga angka contoh, tampil bertahap 3 ketukan."""
    rows = [(sg(9) - 0.05, "👥", "10 orang", NAVY), (sg(10) - 0.05, "💵", "Rp500.000/bulan*", TEAL),
            (sg(11) + 0.5, "💰", "cair Rp5.000.000", GREEN)]
    for j, (t0, em, s, col) in enumerate(rows):
        p = pop(t, t0)
        if p <= 0: continue
        T, td = card(780, 190, fill=WHITE, outline=col, ow=7)
        e = emoji_img(em, 90)
        T.alpha_composite(e, (40, int(97 - e.height / 2)))
        text_c(td, (40 + e.width + (780 - 40 - e.width) / 2, 97), s, fit("pb", 70, s, 780 - e.width - 100), col)
        paste_c(img, T, W / 2, 620 + j * 250, p, -1.5 + 1.5 * j, tag="kartu angka")
    draw_aru(img, 220, 1470, 260, t)


def duo(img, t, k):
    """dua kartu bersisian: NO. 1 = pinjam tanpa bunga / NO. 10 = nabung tanpa bunga."""
    right = k == 6
    specs = [(335, "NO. 1", "1", TEAL, ("= pinjam", "Rp5 jt", "tanpa bunga"), "🤑", SC[5] + 0.1),
             (745, "NO. 10", "10", RED, ("= nabung", "10 bulan", "tanpa bunga"), "🐢", SC[6] + 0.1)]
    for j, (cx, lab, num, col, lines, em, t0) in enumerate(specs):
        act = (j == 1) == right
        shown = j == 0 or right
        T, td = card(380, 820, fill=WHITE if act else (240, 242, 246), outline=col if act else (200, 205, 216), ow=6)
        td.rounded_rectangle((0, 0, 380, 110), 30, fill=col if act else (190, 196, 210))
        td.rectangle((0, 60, 380, 110), fill=col if act else (190, 196, 210))
        text_c(td, (190, 56), lab, F("pb", 56), WHITE)
        if shown:
            S = scroll_img(190, num, 1.0, col=col if act else GREY_T)
            T.alpha_composite(S, (int(190 - S.width / 2), 140))
            T.alpha_composite(emoji_img(em, 90), (145, 420))
            p_txt = pop(t, t0 + 0.3)
            if p_txt > 0:
                for i, s in enumerate(lines):
                    text_c(td, (190, 570 + i * 70), s, fit("pb", 50 if i != 1 else 56, s, 340),
                           (col if i != 0 else NAVY) if act else GREY_T)
        else:
            text_c(td, (190, 460), "?", F("pb", 200), (200, 205, 216))
        paste_c(img, T, cx, 930, 1.0 if j == 0 or not right else pop(t, t0), 0, tag="kartu " + lab)


def scene5(img, t): duo(img, t, 5)
def scene6(img, t): duo(img, t, 6)


def scene7(img, t):
    """padahal bunga penjaminan LPS 3,75% (counter berhenti di 3,75%)."""
    p = pop(t, SC[7] + 0.05)
    if p > 0:
        paste_c(img, pill("PADAHAL…", fill=NAVY, fg=YEL, size=54), W / 2, 470, p, -2, tag="pill padahal")
    q = pop(t, SC[7] + 0.3)
    if q > 0:
        T, td = head_card(800, 560, "BUNGA PENJAMINAN LPS", col=GREEN, size=48)
        T.alpha_composite(emoji_img("🏦", 90), (36, 125))
        u = eout((t - L0) / (L1 - L0)) if t >= L0 else 0
        text_c(td, (430, 300), f"{3.75 * u:.2f}%".replace(".", ",") if u > 0 else "?,??%", F("pb", 180), GREEN)
        text_c(td, (400, 480), "bank umum, per tahun", F("pm", 40), GREY_T)
        paste_c(img, T, W / 2, 900, q, tag="kartu LPS")
    draw_aru(img, 250, 1470, 260, t)


def scene8(img, t):
    """setor sendiri Rp500 rb ke deposito tiap bulan: kalender 1 -> 10 terisi."""
    T, td = head_card(800, 640, "SETOR SENDIRI · Rp500 RB/BULAN", col=TEAL, size=42)
    n = int(10 * clamp((t - SC[8] - 0.3) / 2.4) + 0.999) if t >= SC[8] + 0.3 else 0
    for k in range(10):
        x = 40 + (k % 5) * 148; y = 130 + (k // 5) * 150
        lit = k < n
        td.rounded_rectangle((x, y, x + 128, y + 128), 18, fill=(214, 244, 238) if lit else LIGHT,
                             outline=TEAL if lit else (205, 210, 222), width=4)
        text_c(td, (x + 64, y + 40), f"BLN {k + 1}", F("pb", 26), TEAL if lit else GREY_T)
        if lit:
            td.ellipse((x + 40, y + 66, x + 88, y + 114), fill=GOLD, outline=GOLD_D, width=3)
    tot = 500000 * n
    td.rounded_rectangle((40, 450, 760, 600), 26, fill=TEAL)
    text_c(td, (400, 525), "deposito " + rp(tot), F("pb", 56), WHITE)
    paste_c(img, T, W / 2, 820, 1.0, 0, tag="kartu setor")
    paste_c(img, pill("3,75%/thn", fill=GREEN, fg=WHITE, size=44), 760, 1250, pop(t, SC[8] + 0.6), 4,
            tag="pill 3,75")
    draw_aru(img, 280, 1470, 280, t)


def neg_value(t):
    u = eout((t - D0) / (D1 - D0)) if t >= D0 else 0.0
    return 70300 if u >= 1 else int(round(70300 * u / 100.0) * 100)


def pos_value(t):
    u = eout((t - G0) / (G1 - G0)) if t >= G0 else 0.0
    return 70300 if u >= 1 else int(round(70300 * u / 100.0) * 100)


def scene9(img, t):
    """bulan kesepuluh dapat bunga ±Rp70.300 -> itu yang lepas dari si NO. 10; Si Bocor menggondol koin."""
    p = pop(t, SC[9] + 0.05)
    if p > 0:
        T = big_card_counter("BUNGA 10 BULAN", "yang lepas dari si NO. 10", "−" + rp(neg_value(t)), RED,
                             t >= D1, "≈ Rp70 ribu")
        paste_c(img, T, W / 2, 740, p * (1 + 0.02 * math.sin(t * 8)), -1.2, tag="kartu −70.300")
    u = clamp((t - SC[9] - 0.3) / 2.4)
    bx = 300 + 520 * eio(u)
    hop = abs(math.sin(t * 9)) * 14
    C = Image.new("RGBA", (300, 120), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
    cd.rounded_rectangle((0, 0, 300, 110), 55, fill=GOLD, outline=GOLD_D, width=6)
    text_c(cd, (150, 56), "+Rp70 rb", F("pb", 52), (120, 80, 10))
    C.info["nw"] = 300
    paste_c(img, C, min(790, bx - 10), 1140 - hop, 1.0, -6, tag="koin 70 rb")
    paste_c(img, bocor_img(), min(830, bx + 40), 1320 - hop, 0.62, 4 * math.sin(t * 9), tag="bocor")


def scene10(img, t):
    """si NO. 1 kebalikannya: Rp5 jt di deposito, bayar iuran dari situ -> +Rp70.300."""
    T, td = card(640, 170, fill=(253, 236, 232), outline=RED, ow=6)
    text_c(td, (320, 48), "si NO. 10 kehilangan", F("pm", 32), GREY_T)
    text_c(td, (320, 116), "−Rp70.300", F("pb", 76), RED)
    paste_c(img, T, W / 2, 540, 1.0, 0, tag="kartu kecil −70.300")
    p = pop(t, SC[10] + 0.05)
    if p > 0:
        T = big_card_counter("SI NO. 1 · Rp5 JT DI DEPOSITO", "bayar iuran dari situ", "+" + rp(pos_value(t)), GREEN,
                             t >= G1, "≈ Rp70 ribu")
        paste_c(img, T, W / 2, 920, p * (1 + 0.02 * math.sin(t * 8)), 1.2, tag="kartu +70.300")
    draw_aru(img, 220, 1470, 240, t)


def peak_value(t):
    u = eio((t - P0) / (P1 - P0)) if t >= P0 else 0.0
    return 140 if u >= 1 else int(140 * u)


def scene11(img, t):
    """PUNCAK: jarak no. 1 vs no. 10 = ±Rp140 RIBU (counter berhenti, ditahan sampai akhir adegan)."""
    p = pop(t, SC[11] + 0.05)
    if p > 0:
        v = peak_value(t)
        T = big_card_counter("JARAK NO. 1 vs NO. 10", "+Rp70 rb  vs  −Rp70 rb", f"±Rp{v} RIBU", RED, t >= P1, "selisih si pertama & si terakhir")
        paste_c(img, T, W / 2, 720, p * (1 + 0.02 * math.sin(t * 8)), -1.5, tag="kartu puncak")


SPLIT_Y = 470
ARGS_L = [("Tanpa kocokan,", "uang habis JAJAN", "🍢"),
          ("Arisan itu REM,", "malu telat SETOR", "😳"),
          ("Kumpulnya nggak", "bisa DIHITUNG", "☕")]


def split(img, t, k):
    """layar terbelah: kiri tim ARISAN, kanan tim NABUNG SENDIRI; sisi aktif terang."""
    right = k == 15
    d = ImageDraw.Draw(img)
    cols = [(140, 530, TEAL, "ARISAN"), (550, 940, GREEN, "NABUNG SENDIRI")]
    for j, (x0, x1, col, lab) in enumerate(cols):
        act = (j == 1) == right
        fill = (255, 255, 255) if act else (232, 235, 242)
        d.rounded_rectangle((x0, SPLIT_Y, x1, 1440), 30, fill=fill, outline=col if act else (200, 205, 216), width=6)
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
        y = SPLIT_Y + 300 + i * 270
        C = Image.new("RGBA", (360, 250), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
        act = not right
        cd.rounded_rectangle((0, 0, 360, 240), 24, fill=(232, 250, 246) if act else (240, 242, 246),
                             outline=TEAL if act else (200, 205, 216), width=4)
        C.alpha_composite(emoji_img(em, 76), (142, 14))
        text_c(cd, (180, 138), a1, fit("pb", 32, a1, 330), NAVY if act else GREY_T)
        text_c(cd, (180, 190), a2, fit("pb", 32, a2, 330), TEAL if act else GREY_T)
        C.info["nw"] = 360
        paste_c(img, C, 335, y, p, tag="argumen kiri")
    if k < 15:
        text_c(d, (745, 1000), "?", F("pb", 160), (200, 205, 216))
        return
    p = pop(t, SC[15] + 0.1)
    C = Image.new("RGBA", (360, 760), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
    cd.rounded_rectangle((0, 0, 360, 750), 24, fill=(232, 246, 238), outline=GREEN, width=5)
    text_c(cd, (180, 70), "Remnya cukup", F("pb", 38), NAVY)
    if t >= sg(29) - 0.1:
        text_c(cd, (180, 130), "AUTODEBET", F("pb", 50), GREEN)
    # HP notifikasi
    cd.rounded_rectangle((50, 190, 310, 700), 36, fill=(40, 44, 60), outline=NAVY, width=6)
    cd.rounded_rectangle((66, 230, 294, 670), 18, fill=(214, 228, 244))
    if t >= sg(29) + 0.5:
        q = clamp((t - sg(29) - 0.5) / 0.3)
        y0 = 260 + 30 * (1 - q)
        cd.rounded_rectangle((76, y0, 284, y0 + 200), 18, fill=WHITE, outline=GREEN, width=4)
        C.alpha_composite(emoji_img("🏦", 40), (90, int(y0 + 14)))
        cd.text((136, y0 + 34), "Autodebet", font=F("pb", 24), fill=NAVY, anchor="lm")
        text_c(cd, (180, y0 + 100), "Rp500.000", fit("pb", 40, "Rp500.000", 180), GREEN)
        text_c(cd, (180, y0 + 156), "tgl 25 · gajian", fit("pm", 26, "tgl 25 · gajian", 180), GREY_T)
    if t >= sg(29) + 1.3:
        icon_check(cd, 180, 560, 0.9)
    C.info["nw"] = 360
    paste_c(img, C, 745, SPLIT_Y + 560, p, tag="argumen kanan")


def scene12(img, t): split(img, t, 12)
def scene13(img, t): split(img, t, 13)
def scene14(img, t): split(img, t, 14)
def scene15(img, t): split(img, t, 15)


def paths(img, t, k):
    """jalan tengah: dua jalur. 1) butuh cepat -> minta urutan AWAL; 2) nggak buru-buru -> kumpulnya ikut, nabung sendiri."""
    p = pop(t, SC[16] + 0.05) if k == 16 else 1.0
    paste_c(img, pill("JALAN TENGAH", fill=YEL, fg=NAVY, size=60), W / 2, 470, p, -2, tag="pill jalan tengah")
    specs = [(sg(31) - 0.1, sg(32) - 0.05, "⚡", "BUTUH CEPAT?", ("minta urutan", "AWAL"), TEAL, 760, "1"),
             (SC[17] + 0.05, sg(34) - 0.05, "🐢", "NGGAK BURU-BURU?", ("kumpulnya ikut,", "nabung sendiri"), GREEN, 1150, None)]
    for j, (t0, t1, em, head, res, col, cy, num) in enumerate(specs):
        q = pop(t, t0)
        if q <= 0: continue
        act = (k == 16) == (j == 0)
        T, td = card(800, 330, fill=WHITE if act else (240, 242, 246), outline=col if act else (200, 205, 216), ow=6)
        e = emoji_img(em, 70)
        T.alpha_composite(e, (30, int(72 - e.height / 2)))
        td.text((50 + e.width, 72), head, font=fit("pb", 50, head, 700 - e.width), fill=col if act else GREY_T, anchor="lm")
        if t >= t1:
            arrow(td, 70, 150, 70, 270, col if act else GREY_T, w=14, head=30)
            td.text((130, 190), res[0], font=F("pb", 52), fill=NAVY if act else GREY_T, anchor="lm")
            td.text((130, 262), res[1], font=F("pb", 56), fill=col if act else GREY_T, anchor="lm")
            if num:
                S = scroll_img(130, num, 1.0, col=col if act else GREY_T)
                T.alpha_composite(S, (800 - S.width - 40, 140))
        paste_c(img, T, W / 2, cy, q, -1 if j == 0 else 1, tag="jalur %d" % j)


def scene16(img, t): paths(img, t, 16)
def scene17(img, t): paths(img, t, 17)


def scene18(img, t):
    """penutup: Tim DULUAN atau tim BELAKANGAN? Komen!"""
    for k, (s, col, t0) in enumerate((("TIM DULUAN", TEAL, SC[18] + 0.05), ("TIM BELAKANGAN", RED, sg(37)))):
        p = pop(t, t0)
        if p <= 0: continue
        beat = 1 + 0.04 * math.sin((t - t0) * 7 + k * math.pi)
        paste_c(img, pill(s, fill=col, fg=WHITE, size=54, h=116), W / 2, 520 if k == 0 else 720, p * beat,
                -2 if k == 0 else 2, tag=s)
    if t >= sg(37):
        text_c(ImageDraw.Draw(img), (W / 2, 620), "atau", F("pb", 40), NAVY)
    p = pop(t, sg(37) + 0.4)
    if p > 0:
        B = Image.new("RGBA", (800, 250), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 800, 200), 34, fill=YEL, outline=NAVY, width=5)
        bd.polygon([(110, 196), (180, 196), (90, 246)], fill=YEL, outline=NAVY)
        bd.line([(112, 197), (178, 197)], fill=YEL, width=8)
        s = "Tim DULUAN atau tim BELAKANGAN?"
        text_c(bd, (400, 66), s, fit("pb", 46, s, 740), NAVY)
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
    f = F("pb", 34); s1 = "MANA LEBIH HEMAT?"; s2 = "#10"
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
    """ajakan kirim di puncak angka (teks layar ★), 2 baris, teal."""
    if not (SHARE[0] <= t < SHARE[1]): return
    a = min(clamp((t - SHARE[0]) / 0.25), clamp((SHARE[1] - t) / 0.25))
    s = 0.85 + 0.15 * back((t - SHARE[0]) / 0.35)
    T, td = card(800, 190, fill=TEAL)
    e = emoji_img("📤", 70)
    text_c(td, (360, 62), "Kirim ke grup arisanmu", F("pb", 48), WHITE)
    text_c(td, (360, 130), "(atau ke ibumu)", F("pb", 50), YEL)
    T.alpha_composite(e, (690, 58))
    paste_c(img, T, W / 2, 1270 + 4 * math.sin(t * 5), s, 0, a, tag="kartu kirim")


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
    ev.append({"t": 1.5, "sfx": "pop", "gain": 0.32})           # "kriuk!" + gulungan terbuka
    ev.append({"t": CT1, "sfx": "ding", "gain": 0.25})          # counter berhenti −Rp7?.???
    for si in (2, 5, 6, 9, 10, 11, 13, 22, 24, 26, 29, 31, 32, 34, 37):
        ev.append({"t": sg(si), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": L1, "sfx": "ding", "gain": 0.28})           # 3,75%
    ev.append({"t": SC[9] + 0.3, "sfx": "cring", "gain": 0.4})  # Si Bocor menggondol koin
    ev.append({"t": D1, "sfx": "ding", "gain": 0.3})            # −Rp70.300
    ev.append({"t": G1, "sfx": "ding", "gain": 0.3})            # +Rp70.300
    ev.append({"t": P0, "sfx": "cring", "gain": 0.45})          # counter puncak
    ev.append({"t": P1, "sfx": "ding", "gain": 0.35})           # ±Rp140 RIBU
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
        print("LPS", round(L1, 2), "->", round(SC[8], 2), "| -70.300", round(D1, 2), "->", round(SC[11], 2), "| +70.300", round(G1, 2), "->", round(SC[11], 2), "| puncak", round(P1, 2), "->", round(SC[12], 2), "| share", [round(x, 2) for x in SHARE])
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

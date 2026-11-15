"""Renderer ARN-52 "Mana Lebih Hemat? #11 — nikah di gedung vs di rumah" — Flat 2D latar terang (PRB-31).
Salinan render_flat_arisan.py (helper kartu, koin, Si Bocor, pill, bubble, stempel, subtitle, cek area aman, sfx) dengan:
- frame 0 (PRB-36, tanpa kartu judul besar): tenda biru besar di depan rumah; Aru di bawahnya menatap ke atas,
  Si Bocor di atap tenda menggigit tali, koin jatuh ("cring!"). Satu counter besar Rp0 naik dan BERHENTI di
  "Rp16.350.000" dtk 2,0 (total pos pendamping, dibuka ulang di adegan 9). Judul layar hanya pill kecil
  "Nikah di RUMAH, hemat?". Tanpa label seri/logo/progress bar dtk 0-3; visual berganti ~dtk 1,5 (tenda melorot).
- 20 adegan (tiap <= 6 dtk); counter Rp6.600.000 / Rp4.200.000 / Rp5.550.000 (adegan 6-8), Rp16.350.000 (struk,
  adegan 9), Rp6.500.000 (gedung, adegan 10), ≈Rp9.850.000 (PUNCAK adegan 11) berhenti di nilai akhir >= 1,5 dtk;
  sumber kecil PestaHub Bekasi Barat & Popbela; "*angka contoh ilustrasi"; ajakan kirim di puncak; layar terbelah
  tim RUMAH vs tim GEDUNG (12-15); 3 kartu tanya bergantian (17); timbangan (18).
- area aman (PRB-41): semua pill/bubble/kartu <= 800 px dan di x 130..950; `check` memindai tiap 0,1 dtk.
Pemakaian (dari folder kerja pagi/build_nikah, setelah align_nikah.py -> timing.json):
  TOTAL=66.9 python3 ../render_flat_nikah.py events | check | scenes | stills 0,2,... | video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, rp, NAVY, TEAL, YEL, WHITE, GREY_T, RED, SAFE_X)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "66.9"))
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





def big_card_counter(title, sub, value, col, done, extra=None, w=800, h=470):
    T, td = card(w, h, fill=WHITE, outline=col, ow=8)
    text_c(td, (w / 2, 64), title, fit("pb", 50, title, w - 60), col)
    if sub: text_c(td, (w / 2, 120), sub, fit("pm", 36, sub, w - 60), GREY_T)
    td.rounded_rectangle((40, 160, w - 40, 350), 30, fill=col)
    text_c(td, (w / 2, 256), value, fit("pb", 120, value, w - 120), WHITE)
    if done and extra:
        text_c(td, (w / 2, 410), extra, fit("pb", 46, extra, w - 60), NAVY)
    return T


def bon_img(w, h):
    """kertas struk bergerigi bawah; dikembalikan (im, draw)."""
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


# ---------- konstanta per reel ----------
def sg(si): return next(c["start"] for c in TIM if c["seg"] == si) + LEAD     # awal segmen VO (dtk video)
def sge(si): return [c["end"] for c in TIM if c["seg"] == si][-1] + LEAD


SCENE_SEG = [0, 1, 3, 5, 7, 9, 10, 12, 14, 16, 17, 18, 19, 20, 22, 23, 27, 28, 31, 35]
SC = [0.0] + [sg(i) - 0.25 for i in SCENE_SEG[1:]] + [TOTAL]
NS = len(SCENE_SEG)
FOLLOW = (10.9, 15.6)          # PRB-4: ajakan follow teks kecil dtk 10-15 (adegan 4-5)
PB_START = 3.5                 # progress bar mulai dtk 3,5
ILU = "*angka contoh ilustrasi"
SRC_PH = "Harga estimasi PestaHub Bekasi Barat, 15 Mar 2026"
NOTES = {1: (ILU,), 5: ("*contoh ilustrasi: 300 tamu, tenda 10×20 m, 300 kursi",),
         6: ("tenda serut 200 m² × Rp33.000 · " + ILU, SRC_PH),
         7: ("kursi Futura + cover 300 × Rp14.000 · " + ILU, SRC_PH),
         8: ("genset silent 60 kVA Rp2,8 jt + sound 3000 W Rp2,75 jt", SRC_PH),
         9: ("tenda + kursi + genset & sound, belum termasuk katering", ILU),
         10: ("Sewa gedung siang di Bekasi ±Rp6,5 jt · Popbela, 3 Des 2025", "isi sewa beda tiap gedung"),
         11: ("Rp16.350.000 − Rp6.500.000, belum termasuk katering", ILU),
         18: ("dipinjam: sisa genset & sound ±Rp5,55 jt · semua sewa: ±Rp16,35 jt", ILU)}
TOT = 16350000
CT0, CT1 = 0.45, 2.0                       # counter frame 0: naik lalu BERHENTI di Rp16.350.000 dtk 2,0


def land(k, numseg):
    """counter adegan k: mulai SC[k]+0,35, berhenti paling lambat 1,6 dtk sebelum adegan berakhir."""
    return SC[k] + 0.35, min(sg(numseg) - 0.1, SC[k + 1] - 1.6)


CNT = {6: (land(6, 11), 6600000), 7: (land(7, 13), 4200000), 8: (land(8, 15), 5550000),
       9: ((SC[9] + 0.4, SC[10] - 1.6), TOT), 10: ((SC[10] + 0.8, SC[11] - 1.6), 6500000), 11: ((SC[11] + 0.12, SC[12] - 1.6), 9850000)}
SHARE = (CNT[11][0][1] + 0.1, SC[12] + 0.6)   # ajakan kirim di puncak angka
BL, BL_D, BL_L = (52, 120, 206), (34, 86, 160), (120, 176, 236)
GOLD, GOLD_D = (255, 194, 60), (217, 154, 31)
ROPE = (150, 110, 60)


def cval(k, t):
    (a, b), v = CNT[k]
    if t < a: return 0, False
    if t >= b: return v, True
    u = eio((t - a) / (b - a))
    return int(round(v * u / 50000.0) * 50000), False


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


# ---------- gambar ----------
@lru_cache(None)
def tent_img(w, sag=0):
    """tenda biru (terpal) dengan atap runcing, rumbai bergelombang, dua tiang. sag = atap melorot (px)."""
    im = Image.new("RGBA", (820, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x in (80, 740):
        d.rectangle((x - 11, 190, x + 11, 630), fill=(205, 210, 222), outline=NAVY, width=4)
    pk = (410, 30 + sag)
    d.polygon([(20, 200), pk, (800, 200)], fill=BL)
    for k in range(1, 6):
        d.line([pk, (20 + k * 130, 200)], fill=BL_L, width=6)
    d.line([(20, 200), pk, (800, 200)], fill=NAVY, width=7, joint="curve")
    d.rectangle((20, 196, 800, 248), fill=BL_D, outline=NAVY, width=5)
    for k in range(13):
        x0 = 20 + k * 60
        d.chord((x0, 222, x0 + 60, 282), 0, 180, fill=BL_D, outline=NAVY, width=4)
    if sag:
        d.line([(300, 120 + sag * 0.6), (340, 150 + sag * 0.6), (320, 175 + sag * 0.6)], fill=NAVY, width=5)
    return scaled(im, w)


@lru_cache(None)
def house_img(w, col=(236, 206, 170)):
    im = Image.new("RGBA", (700, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((70, 220, 630, 550), fill=col, outline=NAVY, width=7)
    d.polygon([(20, 236), (350, 20), (680, 236)], fill=(214, 92, 70), outline=NAVY)
    d.line([(20, 236), (350, 20), (680, 236), (20, 236)], fill=NAVY, width=7)
    d.rectangle((300, 360, 400, 550), fill=(150, 100, 60), outline=NAVY, width=6)
    for x in (130, 470):
        d.rectangle((x, 300, x + 100, 400), fill=(200, 228, 250), outline=NAVY, width=6)
        d.line([(x + 50, 300), (x + 50, 400)], fill=NAVY, width=4)
    return scaled(im, w)


@lru_cache(None)
def gedung_img(w):
    im = Image.new("RGBA", (700, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(40, 170), (350, 20), (660, 170)], fill=(236, 238, 244), outline=NAVY)
    d.line([(40, 170), (350, 20), (660, 170), (40, 170)], fill=NAVY, width=7)
    text_c(d, (350, 120), "GEDUNG", F("pb", 46), NAVY)
    d.rectangle((60, 170, 640, 210), fill=(214, 218, 230), outline=NAVY, width=6)
    for k in range(6):
        x = 95 + k * 100
        d.rectangle((x, 210, x + 50, 500), fill=WHITE, outline=NAVY, width=6)
    d.rectangle((40, 500, 660, 550), fill=(214, 218, 230), outline=NAVY, width=6)
    d.rectangle((300, 330, 400, 500), fill=GOLD, outline=NAVY, width=5)
    return scaled(im, w)


def kuali_img(t):
    im = Image.new("RGBA", (520, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(3):                                    # uap
        x = 160 + k * 100; ph = t * 3 + k
        pts = [(x + 14 * math.sin(ph + j * 0.9), 120 - j * 22) for j in range(6)]
        d.line(pts, fill=(200, 205, 216), width=8, joint="curve")
    a = 1.2 * math.sin(t * 5)                                # sutil diaduk
    d.line([(260 + 60 * a, 170), (330 + 90 * a, 40)], fill=(150, 100, 60), width=14)
    d.chord((30, 120, 490, 340), 0, 180, fill=(60, 62, 76), outline=NAVY, width=7)
    d.ellipse((30, 160, 490, 240), fill=(226, 150, 72), outline=NAVY, width=7)
    d.ellipse((0, 180, 50, 220), outline=NAVY, width=8); d.ellipse((470, 180, 520, 220), outline=NAVY, width=8)
    im.info["nw"] = 520
    return im


def scale_img(tilt, lt, rt, lcol, rcol):
    """timbangan; tilt > 0 = sisi kiri turun (lebih mahal)."""
    im = Image.new("RGBA", (800, 620), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(400, 120), (330, 560), (470, 560)], fill=(214, 218, 230), outline=NAVY)
    d.line([(400, 120), (330, 560), (470, 560), (400, 120)], fill=NAVY, width=6)
    d.rounded_rectangle((260, 550, 540, 600), 20, fill=(190, 196, 210), outline=NAVY, width=6)
    ang = math.radians(12 * tilt)
    L = 300
    lx, ly = 400 - L * math.cos(ang), 120 + L * math.sin(ang)
    rx, ry = 400 + L * math.cos(ang), 120 - L * math.sin(ang)
    d.line([(lx, ly), (rx, ry)], fill=NAVY, width=16)
    d.ellipse((384, 104, 416, 136), fill=YEL, outline=NAVY, width=5)
    for (x, y, txt, col) in ((lx, ly, lt, lcol), (rx, ry, rt, rcol)):
        d.line([(x, y), (x - 80, y + 150)], fill=NAVY, width=5); d.line([(x, y), (x + 80, y + 150)], fill=NAVY, width=5)
        d.chord((x - 100, y + 110, x + 100, y + 200), 0, 180, fill=col, outline=NAVY, width=6)
        d.rounded_rectangle((x - 95, y + 30, x + 95, y + 112), 18, fill=WHITE, outline=col, width=5)
        text_c(d, (x, y + 72), txt, fit("pb", 40, txt, 175), col)
    im.info["nw"] = 800
    return im


# ---------- frame 0 ----------
FLOOR0 = 1440
@lru_cache(None)
def bg_scene0():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((120, 640, 960, 1480), fill=(252, 236, 196))
    d.rectangle((0, FLOOR0, W, H), fill=(218, 223, 232)); d.line([(0, FLOOR0), (W, FLOOR0)], fill=NAVY, width=5)
    img.alpha_composite(house_img(720), (180, 790))
    return img


def title_pill(img):
    """judul layar = pill kecil (bukan kartu judul besar, PRB-36): 'Nikah di RUMAH, hemat?' (RUMAH kuning)."""
    f = F("pb", 42); a, b, c = "Nikah di ", "RUMAH", ", hemat?"
    wa, wb, wc = f.getlength(a), f.getlength(b), f.getlength(c); w = int(wa + wb + wc + 24 + 60); h = 84
    P = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    d.rounded_rectangle((8, 10, w + 8, h + 10), h // 2, fill=(20, 33, 91, 55))
    d.rounded_rectangle((0, 0, w, h), h // 2, fill=NAVY)
    d.text((30, h / 2 + 2), a, font=f, fill=WHITE, anchor="lm")
    d.rounded_rectangle((30 + wa - 4, 12, 30 + wa + wb + 20, h - 12), 14, fill=YEL)
    d.text((30 + wa + 8, h / 2 + 2), b, font=f, fill=NAVY, anchor="lm")
    d.text((30 + wa + wb + 24, h / 2 + 2), c, font=f, fill=WHITE, anchor="lm")
    P.info["nw"] = w
    paste_c(img, P, W / 2, 320, tag="pill judul")


def counter0(t):
    if t < CT0: return "Rp0", False
    if t >= CT1: return rp(TOT), True
    u = eio((t - CT0) / (CT1 - CT0))
    v = TOT * u + ((137 * int(t * 30)) % 900) * 1000 * u * (1 - u)
    return rp(int(round(v / 50000.0) * 50000)), False


def counter_card(img, t, cy, s, done, hot, scale=1.0, t0=CT0):
    L, d = card(780, 200, fill=(253, 228, 222) if hot else WHITE, outline=RED if hot else NAVY, ow=7)
    text_c(d, (360 if hot else 390, 102), s, fit("pb", 112, s, 620), RED if hot else NAVY)
    if hot:
        k = clamp((t - t0) / 0.3)
        arrow(d, 720, 160, 720, 160 - 115 * k, RED, w=18, head=38)
    paste_c(img, L, W / 2, cy, scale, tag="counter")


def falling_coins(img, t, x0, y0, y1, t0, n=6, spread=150):
    if t < t0: return
    for k in range(n):
        u = ((t - t0) * 1.1 + k / n) % 1.0
        x = x0 - spread / 2 + spread * ((k * 37) % n) / n + 12 * math.sin(t * 4 + k)
        y = y0 + (y1 - y0) * u * u
        paste_c(img, coin(22), x, y, 1.0, 40 * math.sin(t * 6 + k))


def scene0(img, t):
    """frame 0: tenda biru melorot, Si Bocor menggigit tali, koin jatuh; counter naik & berhenti Rp16.350.000."""
    title_pill(img)
    s, done = counter0(t)
    hot = t >= CT0
    sc = 1.0 + (0.06 * back((t - CT1) / 0.3) - 0.06 * clamp((t - CT1 - 0.3) / 0.3) if t >= CT1 else 0)
    counter_card(img, t, 520, s, done, hot, sc)
    sag = int(70 * eio((t - 1.3) / 0.4))                           # visual berganti ~dtk 1,5: atap melorot
    T = tent_img(800, sag // 10 * 10)
    img.alpha_composite(T, (int(W / 2 - T.width / 2), FLOOR0 - T.height + 6))
    ty = FLOOR0 - T.height + 6
    # tali dari atap ke patok kanan, ditarik Si Bocor
    chew = abs(math.sin(t * 11)) * 8
    bx, by = 700, ty + 120 + sag * 0.5 - chew
    d = ImageDraw.Draw(img)
    pull = 10 * math.sin(t * 11)
    d.line([(bx - 20, by + 50), (840 + pull, by + 160), (930, FLOOR0 - 4)], fill=ROPE, width=9, joint="curve")
    d.rectangle((918, FLOOR0 - 30, 942, FLOOR0 + 4), fill=(150, 100, 60), outline=NAVY, width=3)
    paste_c(img, bocor_img(), bx, by, 0.55, 14 + 6 * math.sin(t * 11), tag="bocor")
    draw_aru(img, 330, FLOOR0, 420, t)
    falling_coins(img, t, 640, ty + 300, FLOOR0 - 20, 0.3, n=5, spread=170)
    if t >= 1.5:
        falling_coins(img, t, 470, ty + 260, FLOOR0 - 20, 1.5, n=4, spread=120)
    p = pop(t, 1.5)
    if p > 0:
        paste_c(img, bubble("cring!", col=YEL, fg=NAVY, size=48, tail="right"), 780, 760, p, 6, tag="bubble cring")


def scene1(img, t):
    """coba tebak, bocornya di mana? counter Rp16.350.000 tetap tampil, tiga lencana ? di tenda."""
    counter_card(img, t, 560, rp(TOT), True, True, t0=-9)
    T = tent_img(620, 60)
    paste_c(img, T, W / 2, 1110, 1.0)
    for k, (x, y, t0) in enumerate(((330, 980, sg(2) - 0.1), (540, 1250, sg(2) + 0.15), (760, 980, sg(2) + 0.4))):
        q = pop(t, t0)
        if q <= 0: continue
        L = Image.new("RGBA", (160, 160), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.ellipse((6, 6, 154, 154), fill=YEL, outline=NAVY, width=7)
        text_c(ld, (80, 78), "?", F("pb", 90), NAVY)
        L.info["nw"] = 160
        paste_c(img, L, x, y, q, 8 * math.sin(t * 4 + k), tag="lencana ?")
    draw_aru(img, 230, 1470, 300, t)


def scene2(img, t):
    """kamu pasti kenal: tetangga mengaduk kuali besar sejak subuh (jam 04.30)."""
    p = pop(t, SC[2] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Kamu pasti kenal", "👀", fill=YEL, fg=NAVY, size=48), W / 2, 470, p, -2,
                tag="pill kenal")
    q = pop(t, sg(4) - 0.1)
    if q > 0:
        C, cd = card(300, 150, fill=NAVY, outline=NAVY)
        C.alpha_composite(emoji_img("🕓", 70), (24, 40))
        text_c(cd, (190, 75), "04.30", F("pb", 60), YEL)
        paste_c(img, C, 780, 660, q, 4, tag="jam subuh")
    K = kuali_img(t)
    paste_c(img, K, 600, 1130, pop(t, SC[2] + 0.15), tag="kuali")
    paste_c(img, emoji_img("🧕", 230), 260, 960 + 6 * math.sin(t * 6), pop(t, SC[2] + 0.3), 6 * math.sin(t * 5))
    paste_c(img, emoji_img("👵", 170), 860, 990 + 6 * math.sin(t * 6 + 1), pop(t, sg(4) + 0.5), -6 * math.sin(t * 5))


def scene3(img, t):
    """tante di kursi tamu: 'Kapan nyusul?' (lucu); Aru salah tingkah."""
    paste_c(img, emoji_img("🪑", 260), 330, 1230, pop(t, SC[3] + 0.05))
    paste_c(img, emoji_img("👵", 240), 330, 1040 + 5 * math.sin(t * 7), pop(t, SC[3] + 0.1), 4 * math.sin(t * 4))
    q = pop(t, sg(6) - 0.1)
    if q > 0:
        paste_c(img, bubble("\"Kapan nyusul?\"", col=RED, fg=WHITE, size=56, tail="left"), 560, 760,
                q * (1 + 0.03 * math.sin(t * 9)), -3, tag="bubble nyusul")
        paste_c(img, emoji_img("💍", 90), 830, 640, q, 10 * math.sin(t * 5))
    draw_aru(img, 790, 1470, 340, t)
    r = pop(t, sg(6) + 0.2)
    if r > 0:
        paste_c(img, emoji_img("😅", 90), 900, 1080, r)


def scene4(img, t):
    """'rumah sendiri gratis' (stempel GRATIS), lalu halaman kosong tanpa kursi."""
    swap = sg(8) - 0.1
    if t < swap:
        paste_c(img, house_img(600), W / 2, 950, pop(t, SC[4] + 0.05))
        s = pop(t, sg(7) + 0.9)
        if s > 0:
            paste_c(img, stamp("GRATIS", col=GREEN, size=80), 560, 1170, s, -8, tag="stempel gratis")
    else:
        u = eout((t - swap) / 0.4)
        paste_c(img, house_img(int(600 - 260 * u)), W / 2, 950 - 330 * u, 1.0)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((150, 820, 930, 1420), 30, fill=(232, 236, 226), outline=NAVY, width=5)
        track("halaman", 780, 150, 930)
        for r_ in range(3):
            for c_ in range(5):
                x = 200 + c_ * 146; y = 870 + r_ * 150
                dashed(d, [(x, y), (x + 100, y), (x + 100, y + 110), (x, y + 110), (x, y)], (170, 178, 195), w=5,
                       phase=t * 30)
        q = pop(t, sg(8) + 1.4)
        if q > 0:
            paste_c(img, pill("0 KURSI", fill=RED, fg=WHITE, size=60), W / 2, 1120, q, -4, tag="pill 0 kursi")


def scene5(img, t):
    """contoh ilustrasi: 300 tamu di Bekasi."""
    p = pop(t, SC[5] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Bekasi", "📍", fill=NAVY, fg=WHITE, size=50), W / 2, 470, p, -2, tag="pill bekasi")
    rows = [(SC[5] + 0.2, "👥", "300 tamu"), (SC[5] + 0.6, "⛺", "tenda 10×20 m"), (SC[5] + 1.0, "🪑", "300 kursi")]
    for j, (t0, em, s) in enumerate(rows):
        q = pop(t, t0)
        if q <= 0: continue
        T, td = card(760, 170, fill=WHITE, outline=TEAL, ow=6)
        e = emoji_img(em, 90)
        T.alpha_composite(e, (40, int(87 - e.height / 2)))
        td.text((170, 87), s, font=F("pb", 66), fill=NAVY, anchor="lm")
        paste_c(img, T, W / 2, 660 + j * 220, q, -1.5 + 1.5 * j, tag="kartu contoh")
    q = pop(t, SC[5] + 1.3)
    if q > 0:
        paste_c(img, stamp("CONTOH*", col=RED, size=56), 760, 1330, q, -8, tag="stempel contoh")


ITEMS = {6: ("TENDA 200 m²", "tenda serut · Rp33.000/m²", "⛺", "≈ Rp6,6 juta", BL),
         7: ("300 KURSI", "Futura + cover · Rp14.000/kursi", "🪑", "≈ Rp4,2 juta", TEAL),
         8: ("GENSET + SOUND", "60 kVA Rp2,8 jt + 3000 W Rp2,75 jt", "🔊", "≈ Rp5,55 juta", (214, 120, 40))}
TALLY = [(6, "Tenda", "Rp6,6 jt"), (7, "Kursi", "Rp4,2 jt"), (8, "Genset+sound", "Rp5,55 jt")]


def tally(img, t, upto):
    """strip rekap di bawah: pos yang sudah berhenti tetap tampil (nilai akhir ditahan)."""
    x = 140
    for k, lab, val in TALLY:
        if k > upto: break
        (a, b), _ = CNT[k]
        if t < b: break
        q = pop(t, b) if k == upto else 1.0
        w = 250
        C, cd = card(w, 120, fill=WHITE, outline=ITEMS[k][4], ow=5, r=24)
        text_c(cd, (w / 2, 38), lab, fit("pm", 30, lab, w - 30), GREY_T)
        text_c(cd, (w / 2, 86), val, fit("pb", 42, val, w - 30), ITEMS[k][4])
        paste_c(img, C, x + w / 2, 1330, q, tag="rekap")
        x += w + 15


def item_scene(img, t, k):
    title, sub, em, extra, col = ITEMS[k]
    paste_c(img, emoji_img(em, 130), W / 2, 470, pop(t, SC[k] + 0.05), 6 * math.sin(t * 3))
    v, done = cval(k, t)
    T = big_card_counter(title, sub, rp(v), col, done, extra)
    paste_c(img, T, W / 2, 860, pop(t, SC[k] + 0.1) * (1 + 0.02 * math.sin(t * 8)), -1.2 + 1.2 * (k - 6))
    track("kartu " + title, 800, W / 2 - 400, W / 2 + 400)
    tally(img, t, k)


def scene6(img, t): item_scene(img, t, 6)
def scene7(img, t): item_scene(img, t, 7)
def scene8(img, t): item_scene(img, t, 8)


def scene9(img, t):
    """struk panjang total Rp16.350.000 + piring kosong (belum termasuk katering)."""
    bw, bh = 560, 900
    B, bd = bon_img(bw, bh)
    text_c(bd, (bw / 2, 60), "STRUK SEWA", F("pb", 46), NAVY)
    dashed(bd, [(36, 110), (bw - 36, 110)], (170, 178, 195), w=4)
    rows = (("Tenda 200 m²", "6.600.000"), ("300 kursi", "4.200.000"), ("Genset 60 kVA", "2.800.000"),
            ("Sound 3000 W", "2.750.000"), ("Nasi", "–"))
    for j, (a_, b_) in enumerate(rows):
        y = 170 + j * 70
        bd.text((36, y), a_, font=F("pm", 36), fill=NAVY if j < 4 else GREY_T, anchor="lm")
        bd.text((bw - 36, y), b_, font=F("pb", 36), fill=NAVY if j < 4 else GREY_T, anchor="rm")
    bd.line([(36, 530), (bw - 36, 530)], fill=NAVY, width=5)
    text_c(bd, (bw / 2, 590), "TOTAL", F("pb", 46), RED)
    v, done = cval(9, t)
    bd.rounded_rectangle((26, 640, bw - 26, 800), 26, fill=(253, 228, 222), outline=RED, width=6)
    text_c(bd, (bw / 2, 720), rp(v), fit("pb", 84, rp(v), bw - 90), RED)
    u = eout((t - SC[9]) / 0.6)
    paste_c(img, B, 440, 880 + 300 * (1 - u), 1.0, -2, tag="struk")
    q = pop(t, sg(16) + 0.2)
    if q > 0:
        paste_c(img, emoji_img("🍽", 150), 830, 1220, q, 6 * math.sin(t * 4))
        paste_c(img, bubble("nasi: 0", col=NAVY, fg=YEL, size=40, tail="left"), 830, 1060, q, 4, tag="bubble nasi")


def scene10(img, t):
    """gedung siang di Bekasi disewa ±Rp6.500.000 (counter berhenti)."""
    paste_c(img, gedung_img(640), W / 2, 760, pop(t, SC[10] + 0.05))
    v, done = cval(10, t)
    T, td = card(720, 230, fill=WHITE, outline=GREEN, ow=7)
    text_c(td, (360, 50), "sewa gedung siang", F("pm", 38), GREY_T)
    td.rounded_rectangle((30, 90, 690, 210), 26, fill=GREEN)
    text_c(td, (360, 150), rp(v), F("pb", 92), WHITE)
    paste_c(img, T, W / 2, 1180, pop(t, SC[10] + 0.25), 1.5, tag="kartu gedung")
    draw_aru(img, 235, 1475, 170, t)


def scene11(img, t):
    """PUNCAK: selisih ≈ Rp9.850.000 (counter berhenti, ditahan sampai akhir adegan)."""
    p = pop(t, SC[11] + 0.05)
    if p > 0:
        v, done = cval(11, t)
        T = big_card_counter("SELISIHNYA", "Rp16,35 jt  −  Rp6,5 jt", "≈ " + rp(v), RED, done,
                             "belum termasuk katering")
        paste_c(img, T, W / 2, 720, p * (1 + 0.02 * math.sin(t * 8)), -1.5, tag="kartu puncak")


SPLIT_Y = 470
ARGS_L = [("🪑", "Kursi", "pinjam RT"), ("⛺", "Tenda", "patungan keluarga"), ("🍲", "Tetangga masak", "nggak ada di paket")]
ARGS_R = [("🕓", "4 jam beres"), ("🚧", "tanpa tutup jalan"), ("🍽", "tanpa cuci piring")]


def split(img, t, k):
    """layar terbelah: kiri tim RUMAH, kanan tim GEDUNG; sisi aktif terang."""
    right = k == 15
    d = ImageDraw.Draw(img)
    cols = [(140, 530, TEAL, "RUMAH"), (550, 940, GREEN, "GEDUNG")]
    for j, (x0, x1, col, lab) in enumerate(cols):
        act = (j == 1) == right
        fill = (255, 255, 255) if act else (232, 235, 242)
        d.rounded_rectangle((x0, SPLIT_Y, x1, 1440), 30, fill=fill, outline=col if act else (200, 205, 216), width=6)
        d.rounded_rectangle((x0, SPLIT_Y, x1, SPLIT_Y + 120), 30, fill=col if act else (190, 196, 210))
        d.rectangle((x0, SPLIT_Y + 70, x1, SPLIT_Y + 120), fill=col if act else (190, 196, 210))
        text_c(d, ((x0 + x1) / 2, SPLIT_Y + 34), "TIM", F("pb", 30), WHITE)
        text_c(d, ((x0 + x1) / 2, SPLIT_Y + 82), lab, fit("pb", 48, lab, x1 - x0 - 30), WHITE)
        track("kolom " + lab, x1 - x0, x0, x1)
    d.ellipse((540 - 42, SPLIT_Y + 170 - 42, 540 + 42, SPLIT_Y + 170 + 42), fill=YEL, outline=NAVY, width=5)
    text_c(d, (540, SPLIT_Y + 168), "vs", F("pb", 38), NAVY)
    nL = {12: 0, 13: 2, 14: 3}.get(k, 3)
    starts = [sg(20) - 0.05, sg(21) - 0.05, SC[14] + 0.1]
    if nL == 0:
        text_c(d, (335, 1000), "?", F("pb", 160), (170, 200, 196))
    for i in range(nL):
        em, a1, a2 = ARGS_L[i]
        p = pop(t, starts[i])
        if p <= 0: continue
        y = SPLIT_Y + 300 + i * 270
        C = Image.new("RGBA", (360, 250), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
        act = not right
        hl = i == 2 and act
        cd.rounded_rectangle((0, 0, 360, 240), 24, fill=(255, 244, 205) if hl else ((232, 250, 246) if act else (240, 242, 246)),
                             outline=(GOLD_D if hl else TEAL) if act else (200, 205, 216), width=5 if hl else 4)
        C.alpha_composite(emoji_img(em, 76), (142, 14))
        text_c(cd, (180, 138), a1, fit("pb", 34, a1, 330), NAVY if act else GREY_T)
        text_c(cd, (180, 190), a2, fit("pb", 32, a2, 330), TEAL if act else GREY_T)
        C.info["nw"] = 360
        paste_c(img, C, 335, y, p, tag="argumen kiri")
    if k < 15:
        text_c(d, (745, 1000), "?", F("pb", 160), (200, 205, 216))
        return
    for i, (em, s) in enumerate(ARGS_R):
        p = pop(t, sg(24 + i) - 0.05)
        if p <= 0: continue
        y = SPLIT_Y + 300 + i * 270
        C = Image.new("RGBA", (360, 250), (0, 0, 0, 0)); cd = ImageDraw.Draw(C)
        cd.rounded_rectangle((0, 0, 360, 240), 24, fill=(232, 246, 238), outline=GREEN, width=5)
        e = emoji_img(em, 90)
        C.alpha_composite(e, (int(180 - e.width / 2), 18))
        if i == 2:
            cd.line([(120, 30), (240, 110)], fill=RED, width=12)
        text_c(cd, (180, 170), s, fit("pb", 36, s, 330), NAVY)
        C.info["nw"] = 360
        paste_c(img, C, 745, y, p, tag="argumen kanan")


def scene12(img, t): split(img, t, 12)
def scene13(img, t): split(img, t, 13)
def scene14(img, t): split(img, t, 14)
def scene15(img, t): split(img, t, 15)


def scene16(img, t):
    """jalan tengah: sebelum DP, tanyakan 3 hal."""
    paste_c(img, pill("JALAN TENGAH", fill=YEL, fg=NAVY, size=60), W / 2, 470, pop(t, SC[16] + 0.05), -2,
            tag="pill jalan tengah")
    q = pop(t, SC[16] + 0.25)
    if q > 0:
        T, td = head_card(800, 560, "SEBELUM BAYAR DP", col=NAVY, size=50)
        T.alpha_composite(emoji_img("📝", 150), (60, 200))
        text_c(td, (500, 300), "TANYA", F("pb", 90), NAVY)
        n = sg(27) + 1.0
        text_c(td, (500, 430), "3 HAL" if t >= n else "…", F("pb", 110), RED)
        paste_c(img, T, W / 2, 900, q, -1, tag="kartu DP")
    draw_aru(img, 240, 1470, 260, t)


QS = [("1", "Kursi & sound", "termasuk?", "🔊"), ("2", "Lewat jam,", "dendanya berapa?", "⏰"),
      ("3", "Boleh bawa", "katering sendiri?", "🍛")]


def scene17(img, t):
    """tiga kartu tanya muncul bergantian (ganti tiap segmen VO)."""
    paste_c(img, pill_emoji("Tanya sebelum DP", "☝", fill=NAVY, fg=WHITE, size=46), W / 2, 470, 1.0, -2,
            tag="pill tanya")
    i = 0 if t < sg(29) - 0.1 else (1 if t < sg(30) - 0.1 else 2)
    t0 = [SC[17] + 0.05, sg(29) - 0.1, sg(30) - 0.1][i]
    num, a, b, em = QS[i]
    T, td = card(800, 560, fill=WHITE, outline=TEAL, ow=8)
    td.ellipse((40, 40, 190, 190), fill=YEL, outline=NAVY, width=6)
    text_c(td, (115, 113), num, F("pb", 100), NAVY)
    T.alpha_composite(emoji_img(em, 140), (580, 50))
    text_c(td, (400, 320), a, fit("pb", 76, a, 720), NAVY)
    text_c(td, (400, 430), b, fit("pb", 76, b, 720), TEAL)
    paste_c(img, T, W / 2, 900, pop(t, t0), -1.5 + 1.5 * i, tag="kartu tanya")
    d = ImageDraw.Draw(img)
    for j in range(3):
        x = W / 2 - 70 + 70 * j
        d.ellipse((x - 18, 1250 - 18, x + 18, 1250 + 18), fill=TEAL if j <= i else (205, 210, 222), outline=NAVY, width=4)


def scene18(img, t):
    """timbangan: dipinjam -> RUMAH menang; semua sewa -> GEDUNG lebih hemat."""
    B = t >= sg(33) - 0.1
    lab = "Semua SEWA?" if B else "Kursi & tenda DIPINJAM?"
    t0 = sg(33) - 0.1 if B else SC[18] + 0.05
    paste_c(img, pill(lab, fill=RED if B else TEAL, fg=WHITE, size=50), W / 2, 470, pop(t, t0), -2, tag="pill timbang")
    if B:
        tilt = eout((t - t0) / 0.5) * 1.0 + (1 - eout((t - t0) / 0.5)) * -0.6
        S = scale_img(tilt, "Rp16,35 jt", "Rp6,5 jt", TEAL, GREEN)
    else:
        tilt = -0.6 * eout((t - SC[18] - 0.3) / 0.6)
        S = scale_img(tilt, "Rp5,55 jt", "Rp6,5 jt", TEAL, GREEN)
    paste_c(img, S, W / 2, 940, 1.0, tag="timbangan")
    d = ImageDraw.Draw(img)
    text_c(d, (W / 2 - 300, 1275), "RUMAH", F("pb", 50), TEAL)
    text_c(d, (W / 2 + 300, 1275), "GEDUNG", F("pb", 50), GREEN)
    if B:
        s = pop(t, sg(34) + 0.1)
        if s > 0:
            paste_c(img, stamp("GEDUNG LEBIH HEMAT", col=GREEN, size=54), W / 2, 1395, s, -3, tag="stempel gedung")
    else:
        s = pop(t, sg(32) - 0.05)
        if s > 0:
            paste_c(img, stamp("RUMAH MENANG", col=TEAL, size=60), W / 2, 1395, s, -3, tag="stempel rumah")


def scene19(img, t):
    """penutup: Tim GEDUNG atau tim RUMAH? Komen!"""
    for k, (s, col, t0) in enumerate((("TIM GEDUNG", GREEN, SC[19] + 0.05), ("TIM RUMAH", TEAL, sg(36)))):
        p = pop(t, t0)
        if p <= 0: continue
        beat = 1 + 0.04 * math.sin((t - t0) * 7 + k * math.pi)
        paste_c(img, pill(s, fill=col, fg=WHITE, size=54, h=116), W / 2, 520 if k == 0 else 720, p * beat,
                -2 if k == 0 else 2, tag=s)
    if t >= sg(36):
        text_c(ImageDraw.Draw(img), (W / 2, 620), "atau", F("pb", 40), NAVY)
    p = pop(t, sg(36) + 0.3)
    if p > 0:
        B = Image.new("RGBA", (800, 250), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 800, 200), 34, fill=YEL, outline=NAVY, width=5)
        bd.polygon([(110, 196), (180, 196), (90, 246)], fill=YEL, outline=NAVY)
        bd.line([(112, 197), (178, 197)], fill=YEL, width=8)
        s = "Tim GEDUNG atau tim RUMAH?"
        text_c(bd, (400, 66), s, fit("pb", 50, s, 740), NAVY)
        text_c(bd, (400, 140), "Komen!", F("pb", 60), NAVY)
        B.info["nw"] = 800
        paste_c(img, B, W / 2, 940, p, tag="bubble komen")
    draw_aru(img, W / 2, 1440, 300, t)
    s = "bukan saran keuangan"
    f = F("pm", 28)
    track("catatan", f.getlength(s), W / 2 - f.getlength(s) / 2, W / 2 + f.getlength(s) / 2)
    ImageDraw.Draw(img).text((W / 2, 1490), s, font=f, fill=GREY_T, anchor="mm")


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10, scene11,
          scene12, scene13, scene14, scene15, scene16, scene17, scene18, scene19]
assert len(SCENES) == NS


@lru_cache(None)
def header():
    L = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F("pb", 34); s1 = "MANA LEBIH HEMAT?"; s2 = "#11"
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
    text_c(td, (370, 62), "Kirim ke pasangan / teman", fit("pb", 46, "Kirim ke pasangan / teman", 640), WHITE)
    text_c(td, (370, 132), "yang mau nikah tahun depan", fit("pb", 46, "yang mau nikah tahun depan", 640), YEL)
    T.alpha_composite(e, (700, 58))
    paste_c(img, T, W / 2, 1270 + 4 * math.sin(t * 5), s, 0, a, tag="kartu kirim")


FOLLOW_S = "Follow @kabar.arunika · tiap pagi 1 hitungan uang"


def follow_pill():
    f = fit("pb", 30, FOLLOW_S, MAXW - 60); tw = f.getlength(FOLLOW_S)
    pl = Image.new("RGBA", (int(tw) + 60, 60), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
    pd.rounded_rectangle((0, 0, tw + 60, 60), 30, fill=TEAL)
    pd.text((30, 30), FOLLOW_S, font=f, fill=WHITE, anchor="lm")
    assert pl.width <= MAXW, pl.width
    pl.info["nw"] = pl.width
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
        if t >= CT0:                       # label ilustrasi untuk counter
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
            if (tag not in ("aru", "bocor") and nw > MAXW + 0.5) or x0 < XMIN - 0.5 or x1 > XMAX + 0.5:
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
    ev.append({"t": 0.35, "sfx": "cring", "gain": 0.3})         # koin pertama jatuh
    ev.append({"t": 1.5, "sfx": "cring", "gain": 0.4})          # "cring!" + tenda melorot
    ev.append({"t": CT1, "sfx": "ding", "gain": 0.25})          # counter berhenti Rp16.350.000
    for si in (2, 4, 6, 8, 20, 21, 24, 25, 26, 29, 30, 32, 34, 36):
        ev.append({"t": sg(si), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    for k in (6, 7, 8, 9, 10):
        ev.append({"t": CNT[k][0][1], "sfx": "ding", "gain": 0.28})
    ev.append({"t": CNT[11][0][0], "sfx": "cring", "gain": 0.45})  # counter puncak
    ev.append({"t": CNT[11][0][1], "sfx": "ding", "gain": 0.35})   # ≈ Rp9.850.000
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
        for k, ((a, b), v) in CNT.items():
            print("counter adegan", k, rp(v), "berhenti", round(b, 2), "tahan sampai", round(SC[k + 1], 2),
                  "=", round(SC[k + 1] - b, 2), "dtk")
        print("share", [round(x, 2) for x in SHARE])
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

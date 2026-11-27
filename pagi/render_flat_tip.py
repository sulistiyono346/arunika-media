"""Renderer ARN-68 "Kenapa TIP beda tiap negara?" -- Flat 2D latar terang (PRB-31), VO Maliq Nganjuk 47,8 dtk.
Helper (kartu, koin, Si Bocor, pill, bubble, struk, subtitle 1 baris, cek area aman) disalin dari render_flat_amplop.py.
- frame 0 (PRB-29/34/36/46): Aru memegang struk besar, jari menunjuk baris "Service 5%" disorot kuning; dtk ~1,5 zoom
  ke baris Service; counter "TIP ?%" berputar 0->20% berhenti dtk 2,0; judul = pill kecil; "*struk contoh ilustrasi".
  Tanpa label seri/logo/progress bar dtk 0-3.
- 10 adegan (tiap <= 6 dtk), sumber kecil di layar, follow dtk 10-15, ajakan kirim di angka 95%, split tim tip vs
  tim pas harga, kartu layak simpan "PATOKAN TIP" (PRB-62), penutup 2 tombol + logo kecil <= 1,5 dtk.
Pemakaian (dari folder kerja pagi/build_tip, setelah align_tip.py -> timing.json):
  TOTAL=48.6 python3 ../render_flat_tip.py events | check | scenes | stills 0,2,... | video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, rp, NAVY, TEAL, YEL, WHITE, GREY_T, RED, SAFE_X)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "48.6"))
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




# =====================================================================
# ---------- ARN-68 per reel ----------
# =====================================================================
def sg(si): return next(c["start"] for c in TIM if c["seg"] == si) + LEAD     # awal segmen VO (dtk video)
def sge(si): return [c["end"] for c in TIM if c["seg"] == si][-1] + LEAD


SCENE_SEG = [0, 2, 6, 9, 11, 14, 17, 21, 25, 30]
SC = [0.0] + [sg(i) - 0.25 for i in SCENE_SEG[1:]] + [TOTAL]
NS = len(SCENE_SEG)
FOLLOW = (10.0, 15.0)                   # PRB-4/63: ajakan follow teks kecil dtk 10-15
PB_START = 3.5                          # progress bar baru setelah dtk 3
HEADER_T = 3.0                          # pill kategori + logo baru setelah dtk 3 (PRB-34)
CT0, CT1 = 0.9, 2.0                     # counter "TIP ?%" berputar 0 -> 20% dan berhenti dtk 2,0
GOLD, GOLD_D = (255, 194, 60), (217, 154, 31)
BL = (52, 120, 206)
GREEN = (46, 160, 110)
WOOD, WOOD_D = (196, 140, 92), (150, 100, 62)
SK = (240, 196, 160)
SHARE = (sg(16), SC[6] - 0.05)          # ajakan kirim tepat saat "95 persennya" diucapkan
NOTES = {0: ("*struk contoh ilustrasi",),
         2: ("Pew Research Center, 9 Nov 2023",),
         3: ("upah tunai minimum federal, US Dept. of Labor",),
         4: ("JNTO, japan.travel",),
         5: ("Permenaker 7/2016, bila uang servis dipungut", "*struk contoh ilustrasi"),
         6: ("kumparan, 14 Jan 2021",),
         8: ("Pew Research Center 2023 · JNTO · Permenaker 7/2016",)}


def scene_of(t):
    for k in range(NS):
        if t < SC[k + 1]: return k
    return NS - 1


def note_lines(img, lines, y0=1712, a=1.0):
    L = Image.new("RGBA", (W, 50 * len(lines) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for j, s in enumerate(lines):
        f = fit("pm", 28, s, MAXW)
        track("catatan", f.getlength(s), W / 2 - f.getlength(s) / 2, W / 2 + f.getlength(s) / 2)
        d.text((W / 2, 25 + j * 40), s, font=f, fill=GREY_T if j else INK, anchor="mm")
    paste_c(img, L, W / 2, y0 + L.height / 2 - 25, 1, 0, a)


# ---------- benda ----------
RECEIPT = [("Nasi goreng", "45.000"), ("Es teh manis", "10.000"), ("Subtotal", "55.000"),
           ("Service 5%", "2.750"), ("TOTAL", "57.750")]
SERV_ROW = 3


@lru_cache(None)
def receipt_img(w=560, hl=0.0):
    """struk restoran (contoh ilustrasi); hl = 0..1 sorot kuning baris Service."""
    h = 120 + 92 * len(RECEIPT) + 60
    im, d = bon_img(w, h)
    text_c(d, (w / 2, 56), "STRUK", F("pb", 46), NAVY)
    dashed(d, [(36, 100), (w - 36, 100)], (170, 176, 196), w=4)
    y = 150
    for j, (a, b) in enumerate(RECEIPT):
        if j == SERV_ROW and hl > 0:
            d.rounded_rectangle((20, y - 38, 20 + (w - 40) * hl, y + 38), 14, fill=YEL)
        if j == len(RECEIPT) - 1:
            dashed(d, [(36, y - 50), (w - 36, y - 50)], (170, 176, 196), w=4)
        f = F("pb" if j in (SERV_ROW, len(RECEIPT) - 1) else "pm", 40)
        d.text((44, y), a, font=f, fill=NAVY, anchor="lm")
        d.text((w - 44, y), b, font=f, fill=NAVY, anchor="rm")
        y += 92
    return im


@lru_cache(None)
def bill_folder(w=300):
    im = Image.new("RGBA", (w + 10, int(w * 1.35) + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    h = int(w * 1.35)
    d.rounded_rectangle((0, 0, w, h), 18, fill=(40, 44, 64), outline=NAVY, width=6)
    d.rounded_rectangle((26, 30, w - 26, h - 30), 10, fill=(255, 253, 246))
    for k in range(5):
        yy = 80 + k * 52
        d.line((50, yy, w - 110, yy), fill=(170, 176, 196), width=8)
        d.line((w - 90, yy, w - 50, yy), fill=(170, 176, 196), width=8)
    d.text((50, h - 80), "TIP: ____", font=F("pb", 34), fill=NAVY, anchor="lm")
    return im


@lru_cache(None)
def clock_img(r=150):
    im = Image.new("RGBA", (2 * r + 20, 2 * r + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = r + 10
    d.ellipse((c - r, c - r, c + r, c + r), fill=WHITE, outline=NAVY, width=10)
    for k in range(12):
        a = k * math.pi / 6
        d.line((c + (r - 30) * math.sin(a), c - (r - 30) * math.cos(a), c + (r - 12) * math.sin(a), c - (r - 12) * math.cos(a)),
               fill=NAVY, width=8 if k % 3 == 0 else 4)
    return im


def clock(img, cx, cy, t, r=150, speed=1.0):
    paste_c(img, clock_img(r), cx, cy)
    d = ImageDraw.Draw(img)
    a1 = t * 2.4 * speed; a2 = t * 0.2 * speed
    d.line((cx, cy, cx + (r - 40) * math.sin(a1), cy - (r - 40) * math.cos(a1)), fill=RED, width=8)
    d.line((cx, cy, cx + (r - 70) * math.sin(a2), cy - (r - 70) * math.cos(a2)), fill=NAVY, width=12)
    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=NAVY)


@lru_cache(None)
def big_coin(r=150, label="US$2,13"):
    im = Image.new("RGBA", (2 * r + 20, 2 * r + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = r + 10
    d.ellipse((c - r + 8, c - r + 12, c + r + 8, c + r + 12), fill=(20, 33, 91, 50))
    d.ellipse((c - r, c - r, c + r, c + r), fill=GOLD, outline=GOLD_D, width=10)
    d.ellipse((c - r + 26, c - r + 26, c + r - 26, c + r - 26), outline=(240, 170, 40), width=5)
    text_c(d, (c, c - 18), label, fit("pb", 74, label, 2 * r - 60), (120, 80, 10))
    text_c(d, (c, c + 56), "/jam", F("pb", 50), (120, 80, 10))
    im.info["nw"] = 2 * r
    return im


@lru_cache(None)
def envelope_small(w=200):
    h = int(w * 0.62)
    im = Image.new("RGBA", (w + 10, h + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, h), fill=WHITE, outline=NAVY, width=5)
    d.line([(0, 0), (w / 2, h * 0.55), (w, 0)], fill=NAVY, width=5)
    d.ellipse((w / 2 - 16, h * 0.55 - 16, w / 2 + 16, h * 0.55 + 16), fill=RED)
    return im


@lru_cache(None)
def person_img(h, kind):
    """tokoh pendukung sederhana: 'kasir' (Jepang, celemek), 'driver' (helm toska), 'pelayan'."""
    im = Image.new("RGBA", (300, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    body = {"kasir": (60, 70, 110), "driver": (46, 160, 110), "pelayan": (40, 44, 64)}[kind]
    for x in (104, 160):
        d.rounded_rectangle((x, 400, x + 40, 520), 16, fill=(70, 74, 96), outline=NAVY, width=6)
        d.ellipse((x - 12, 500, x + 52, 538), fill=(40, 40, 50), outline=NAVY, width=5)
    d.rounded_rectangle((80, 240, 224, 420), 40, fill=body, outline=NAVY, width=6)
    if kind in ("kasir", "pelayan"):
        d.rounded_rectangle((104, 290, 200, 420), 14, fill=WHITE, outline=NAVY, width=5)
    d.ellipse((72, 70, 232, 230), fill=SK, outline=NAVY, width=6)
    if kind == "driver":
        d.chord((62, 40, 242, 200), 180, 360, fill=TEAL, outline=NAVY, width=6)
        d.rectangle((62, 112, 242, 128), fill=TEAL, outline=NAVY, width=5)
    else:
        d.chord((72, 62, 232, 190), 180, 360, fill=(40, 36, 52), outline=NAVY, width=6)
    d.ellipse((116, 140, 130, 156), fill=NAVY); d.ellipse((172, 140, 186, 156), fill=NAVY)
    d.arc((124, 160, 180, 196), 20, 160, fill=NAVY, width=5)
    im = trim(im); r = h / im.height
    return im.resize((int(im.width * r), h), Image.LANCZOS)


@lru_cache(None)
def phone_img(w=360, pressed=False):
    h = int(w * 1.9)
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 12, w + 10, h + 12), 46, fill=(20, 33, 91, 50))
    d.rounded_rectangle((0, 0, w, h), 46, fill=(40, 44, 64), outline=NAVY, width=6)
    d.rounded_rectangle((18, 40, w - 18, h - 40), 28, fill=WHITE)
    text_c(d, (w / 2, 100), "Perjalanan selesai", fit("pb", 30, "Perjalanan selesai", w - 70), NAVY)
    text_c(d, (w / 2, 160), "Beri bintang", F("pm", 34), GREY_T)
    for k in range(5):                      # bintang digambar (Poppins tidak punya glyph bintang)
        cx_, cy_ = w / 2 + (k - 2) * 44, 214
        pts = [(cx_ + (18 if j % 2 == 0 else 8) * math.sin(j * math.pi / 5), cy_ - (18 if j % 2 == 0 else 8) * math.cos(j * math.pi / 5)) for j in range(10)]
        d.polygon(pts, fill=GOLD, outline=GOLD_D)
    for k, s in enumerate(("Rp2.000", "Rp5.000", "Rp10.000")):
        y = 290 + k * 66
        sel = pressed and k == 1
        d.rounded_rectangle((44, y - 26, w - 44, y + 26), 26, fill=TEAL if sel else (236, 240, 246), outline=NAVY, width=4)
        text_c(d, (w / 2, y + 1), s, F("pb", 32), WHITE if sel else NAVY)
    bc = YEL if not pressed else GREEN
    d.rounded_rectangle((34, h - 170, w - 34, h - 80), 45, fill=bc, outline=NAVY, width=5)
    text_c(d, (w / 2, h - 124), "Tambah tip", F("pb", 42), NAVY if not pressed else WHITE)
    im.info["nw"] = w
    return im


def flag(d, kind, x, y, w=74):
    h = int(w * 0.66)
    if kind == "us":
        for k in range(7):
            d.rectangle((x, y + k * h / 7, x + w, y + (k + 1) * h / 7), fill=RED if k % 2 == 0 else WHITE)
        d.rectangle((x, y, x + w * 0.45, y + h * 4 / 7), fill=(40, 60, 140))
    elif kind == "jp":
        d.rectangle((x, y, x + w, y + h), fill=WHITE)
        d.ellipse((x + w / 2 - h * 0.3, y + h * 0.2, x + w / 2 + h * 0.3, y + h * 0.8), fill=(200, 30, 50))
    else:
        d.rectangle((x, y, x + w, y + h / 2), fill=(206, 32, 41)); d.rectangle((x, y + h / 2, x + w, y + h), fill=WHITE)
    d.rectangle((x, y, x + w, y + h), outline=NAVY, width=3)


# ---------- judul & counter frame 0 ----------
def title_pill(img, cy=330):
    """judul layar = pill kecil (PRB-36): 'Kenapa TIP beda tiap negara?' (TIP kuning)."""
    a, b, c = "Kenapa ", "TIP", " beda tiap negara?"
    f = F("pb", 44)
    wa, wb, wc = f.getlength(a), f.getlength(b), f.getlength(c)
    w = int(wa + wb + wc + 24 + 60); h = 84
    assert w <= 780, w
    P = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    d.rounded_rectangle((8, 10, w + 8, h + 10), h // 2, fill=(20, 33, 91, 55))
    d.rounded_rectangle((0, 0, w, h), h // 2, fill=NAVY)
    d.text((30, h / 2 + 2), a, font=f, fill=WHITE, anchor="lm")
    d.rounded_rectangle((30 + wa - 4, 12, 30 + wa + wb + 16, h - 12), 14, fill=YEL)
    d.text((30 + wa + 6, h / 2 + 2), b, font=f, fill=NAVY, anchor="lm")
    d.text((30 + wa + wb + 24, h / 2 + 2), c, font=f, fill=WHITE, anchor="lm")
    P.info["nw"] = w
    paste_c(img, P, W / 2, cy, tag="pill judul")


def tip_counter(img, t, cx, cy):
    if t < CT0 - 0.3: return
    a = pop(t, CT0 - 0.3, 0.3)
    if t < CT0: v = 0
    elif t >= CT1: v = 20
    else: v = int(round(20 * eio((t - CT0) / (CT1 - CT0)) + ((7 * int(t * 30)) % 5) * (1 - (t - CT0) / (CT1 - CT0))))
    v = min(20, v)
    s = f"{v}%" if t < CT1 else "20%?"
    L, d = card(380, 170, fill=YEL if t >= CT1 else WHITE, outline=NAVY, ow=7)
    text_c(d, (190, 38), "TIP", F("pb", 40), NAVY)
    text_c(d, (190, 110), s, F("pb", 92), NAVY)
    bump = 1.0 + (0.08 * back((t - CT1) / 0.3) - 0.08 * clamp((t - CT1 - 0.3) / 0.3) if t >= CT1 else 0)
    paste_c(img, L, cx, cy, a * bump, 4 * math.sin(t * 9) if t < CT1 else 0, tag="counter tip")


def finger(d, x, y, ang=200):
    """jari telunjuk Aru menunjuk (lingkaran tangan + jari)."""
    a = math.radians(ang)
    d.line((x, y, x + 60 * math.cos(a), y + 60 * math.sin(a)), fill=NAVY, width=30)
    d.line((x, y, x + 60 * math.cos(a), y + 60 * math.sin(a)), fill=(255, 211, 176), width=20)
    d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=(255, 211, 176), outline=NAVY, width=6)


def scene0(img, t):
    """frame 0: Aru memegang struk besar, jari menunjuk baris Service 5% (sorot kuning);
    ~dtk 1,5 kamera zoom ke baris Service; counter TIP 0->20% berhenti dtk 2,0."""
    z = eio((t - 1.3) / 0.5)                    # zoom ke baris Service (visual berganti ~dtk 1,5)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_aru(L, 300, 1500, 560, t)
    hl = clamp((t - 0.15) / 0.4)
    R = receipt_img(560, round(hl, 2))
    rx, ry = 640, 900
    paste_c(L, R, rx, ry + 4 * math.sin(t * 2.5), 1.0, -3, tag="struk")
    d = ImageDraw.Draw(L)
    sy = ry - R.height / 2 + 150 + 92 * SERV_ROW
    finger(d, 330 + 6 * math.sin(t * 6), sy + 20, -10)
    if z > 0:
        s = 1 + 0.3 * z
        cx, cy = rx * (1 - z) + (W / 2 + 60) * z, sy * (1 - z) + 1000 * z
        big = L.resize((int(W * s), int(H * s)), Image.BICUBIC)
        ox = int(rx * s - cx); oy = int(sy * s - cy)
        L = big.crop((ox, oy, ox + W, oy + H))
    img.alpha_composite(L)
    title_pill(img)
    tip_counter(img, t, 760, 1370)


# ---------- adegan ----------
def table(d, y, x0=120, x1=960):
    d.rounded_rectangle((x0, y, x1, y + 46), 12, fill=WOOD, outline=NAVY, width=6)
    d.rectangle((x0 + 50, y + 46, x0 + 74, y + 360), fill=WOOD_D); d.rectangle((x1 - 74, y + 46, x1 - 50, y + 360), fill=WOOD_D)


def scene1(img, t):
    """meja restoran Amerika, Aru memegang bill; angka besar '20%?' berkedip."""
    d = ImageDraw.Draw(img)
    table(d, 1180)
    paste_c(img, person_img(380, "pelayan"), 830, 1000 + 4 * math.sin(t * 3), 1.0, tag="pelayan")
    draw_aru(img, 330, 1440, 460, t)
    paste_c(img, bill_folder(230), 520, 1090, pop(t, SC[1] + 0.1), -8 + 3 * math.sin(t * 3), tag="bill")
    paste_c(img, pill("RESTORAN AMERIKA", fill=WHITE, fg=NAVY, size=40), W / 2, 470, pop(t, SC[1] + 0.05), tag="pill tempat")
    p = pop(t, sg(5))
    if p > 0:
        blink = 1.0 if int((t - sg(5)) * 3) % 2 == 0 else 0.55
        L = Image.new("RGBA", (520, 260), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.text((260, 130), "20%?", font=F("pb", 190), fill=YEL, anchor="mm", stroke_width=10, stroke_fill=NAVY)
        L.info["nw"] = F("pb", 190).getlength("20%?") + 20
        paste_c(img, L, W / 2, 700, p, 0, blink, tag="angka 20%")
    elif t >= sg(2):
        q = pop(t, sg(2))
        L = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.ellipse((6, 6, 194, 194), fill=YEL, outline=NAVY, width=7)
        text_c(ld, (100, 98), "?", F("pb", 120), NAVY)
        L.info["nw"] = 200
        paste_c(img, L, W / 2, 700, q, 8 * math.sin(t * 4), tag="lencana ?")


def scene2(img, t):
    """bar besar 57% terisi, label tip <=15%."""
    d = ImageDraw.Draw(img)
    p = pop(t, SC[2] + 0.1)
    paste_c(img, pill("SURVEI PEW · AMERIKA", fill=NAVY, fg=WHITE, size=40), W / 2, 470, p, tag="pill pew")
    x0, x1, y0, y1 = 170, 910, 640, 820
    d.rounded_rectangle((x0, y0, x1, y1), 40, fill=WHITE, outline=NAVY, width=7)
    fill = 0.57 * eio((t - sg(7)) / 1.4)
    if fill > 0.01:
        d.rounded_rectangle((x0 + 10, y0 + 10, x0 + 10 + (x1 - x0 - 20) * fill / 1.0, y1 - 10), 32, fill=TEAL)
    pct = int(round(fill * 100))
    text_c(d, (W / 2, 560), f"{pct}%", F("pb", 130), NAVY)
    track("angka 57", F("pb", 130).getlength("57%"), W / 2 - 150, W / 2 + 150)
    q = pop(t, sg(7) + 1.2)
    if q > 0:
        paste_c(img, pill("tip ≤15% saat makan", fill=YEL, fg=NAVY, size=50), W / 2, 920, q, tag="label 15")
        text_c(d, (W / 2, 1010), "dari orang dewasa AS", F("pm", 40), INK)
    draw_aru(img, 780, 1430, 330, t)
    paste_c(img, coin(40), 600 + 10 * math.sin(t * 5), 1260 - 40 * abs(math.sin(t * 4)), 1.0, 20 * math.sin(t * 3))


def scene3(img, t):
    """jam dinding + koin 'US$2,13/jam'."""
    clock(img, 330, 760, t - SC[3], 170, speed=3.0)
    p = pop(t, sg(10) + 1.0)
    paste_c(img, big_coin(160), 720, 820, p, 6 * math.sin(t * 3), tag="koin upah")
    paste_c(img, person_img(400, "pelayan"), 300, 1240, 1.0, tag="pelayan")
    q = pop(t, sg(10))
    if q > 0:
        paste_c(img, pill("upah tunai pelayan", fill=NAVY, fg=WHITE, size=44), 680, 1100, q, tag="pill upah")
    if t >= sg(9) and t < sg(10):
        paste_c(img, bubble("kenapa?", col=YEL, fg=NAVY, size=46), 700, 1240, pop(t, sg(9)), tag="bubble kenapa")
    draw_aru(img, 760, 1430, 300, t)


def scene4(img, t):
    """meja kasir Jepang, amplop kecil; Aru menyodorkan koin; teks 'TIP: tidak lazim'."""
    d = ImageDraw.Draw(img)
    paste_c(img, pill("KASIR DI JEPANG", fill=WHITE, fg=NAVY, size=40), W / 2, 470, pop(t, SC[4] + 0.05), tag="pill tempat")
    paste_c(img, person_img(400, "kasir"), 790, 990 + 3 * math.sin(t * 2), 1.0, tag="kasir")
    d.rounded_rectangle((560, 1160, 1000, 1200), 10, fill=(214, 70, 70), outline=NAVY, width=6)
    d.rectangle((580, 1200, 980, 1440), fill=(236, 226, 210), outline=NAVY, width=6)
    paste_c(img, envelope_small(150), 680, 1120, pop(t, sg(13)), -6, tag="amplop")
    reach = eout((t - SC[4] - 0.3) / 0.6)
    draw_aru(img, 300, 1440, 440, t)
    # koin disodorkan, lalu ditolak halus (kembali)
    back_k = eio((t - sg(13) - 1.2) / 0.5)
    cx = 430 + 120 * reach - 90 * back_k
    paste_c(img, coin(34), cx, 1080, 1.0, 10 * math.sin(t * 6))
    p = pop(t, sg(13) + 1.4)
    if p > 0:
        paste_c(img, stamp("TIP: tidak lazim", col=RED, size=62), W / 2, 720, p, -4, tag="stempel lazim")
    elif t >= sg(12):
        paste_c(img, pill("kebalikannya", fill=TEAL, fg=WHITE, size=50), W / 2, 720, pop(t, sg(12)), tag="pill balik")


def receipt_split(img, t, k0):
    """struk A1 kembali; baris Service pecah jadi diagram 95% · 3% · 2%."""
    d = ImageDraw.Draw(img)
    R = receipt_img(520, 1.0)
    paste_c(img, R, W / 2, 900 - 140 * eio((t - sg(16) + 0.4) / 0.5), 0.85 - 0.2 * eio((t - sg(16) + 0.4) / 0.5), -2, tag="struk")
    k = eio((t - sg(16)) / 0.7)
    if k <= 0: return
    parts = [(0.95, "95%", "pekerja", TEAL), (0.03, "3%", "risiko kerusakan", RED), (0.02, "2%", "pengembangan SDM", BL)]
    x0, x1, y0, y1 = 150, 930, 1090, 1200
    x = x0
    for fr, lab, _, col in parts:
        w_ = (x1 - x0) * fr * k
        d.rectangle((x, y0, x + w_, y1), fill=col)
        x += w_
    d.rectangle((x0, y0, x0 + (x1 - x0) * k, y1), outline=NAVY, width=6)
    if k > 0.9:
        text_c(d, (x0 + (x1 - x0) * 0.47, (y0 + y1) / 2 + 2), "95% PEKERJA", F("pb", 58), WHITE)
        f = F("pb", 34)
        d.text((x0, y1 + 44), "3% risiko kerusakan alat", font=f, fill=RED, anchor="lm")
        d.text((x0, y1 + 92), "2% pengembangan SDM", font=f, fill=BL, anchor="lm")
        track("label persen", 600, x0, x0 + 600)


def scene5(img, t):
    paste_c(img, pill("UANG SERVIS HOTEL · INDONESIA", fill=NAVY, fg=WHITE, size=38), W / 2, 470,
            pop(t, sg(15)), tag="pill servis")
    receipt_split(img, t, 5)


def scene6(img, t):
    """HP tombol 'Tambah tip' (tanpa logo merek), koin melompat ke helm driver."""
    pressed = t >= sg(20) - 0.2
    paste_c(img, phone_img(340, pressed), 340, 900, pop(t, SC[6] + 0.05), -3, tag="hp")
    paste_c(img, person_img(420, "driver"), 790, 1180, 1.0, tag="driver")
    paste_c(img, pill("SUKARELA", fill=GREEN, fg=WHITE, size=46), 760, 560, pop(t, sg(18)), tag="pill sukarela")
    if pressed:
        u = clamp((t - sg(20) + 0.2) / 0.8)
        x = 380 + (790 - 380) * u; y = 1150 - 420 * math.sin(math.pi * u) + (1000 - 1150) * u
        if u < 1:
            paste_c(img, coin(36), x, y, 1.0, 360 * u)
        q = pop(t, sg(20) + 0.6)
        if q > 0:
            paste_c(img, pill("100% ke driver", fill=YEL, fg=NAVY, size=46), 740, 720, q, tag="pill 100")


def scene7(img, t):
    """split: kiri Aru TIM TIP memegang koin; kanan Si Bocor TIM PAS HARGA memeluk dompet; bubble bergantian."""
    d = ImageDraw.Draw(img)
    d.rectangle((0, 520, W / 2, 1480), fill=(224, 247, 243)); d.rectangle((W / 2, 520, W, 1480), fill=(255, 240, 214))
    d.line((W / 2, 520, W / 2, 1480), fill=NAVY, width=7)
    paste_c(img, pill("TIM TIP", fill=TEAL, fg=WHITE, size=46), 330, 600, pop(t, SC[7] + 0.05), tag="pill tim tip")
    paste_c(img, pill("TIM PAS HARGA", fill=NAVY, fg=YEL, size=40, padx=26), 750, 600, pop(t, SC[7] + 0.2), tag="pill pas")
    act_l = t < sg(23) - 0.1
    draw_aru(img, 300, 1460, 470 if act_l else 430, t)
    paste_c(img, coin(34), 430, 1080 - 20 * abs(math.sin(t * 5)), 1.0, 0)
    # Si Bocor memeluk dompet erat (gemetar)
    sh = 4 * math.sin(t * 40) if not act_l else 0
    paste_c(img, bocor_img(), 760 + sh, 1270, 1.35 if not act_l else 1.2, 0, tag="bocor")
    paste_c(img, wallet_img(170), 700 + sh, 1320, 1.0, -12)
    if t >= sg(22) - 0.1 and act_l:
        paste_c(img, bubble("itu terima kasih!", col=TEAL, fg=WHITE, size=40), 340, 820, pop(t, sg(22) - 0.1), tag="bubble kiri")
    if t >= sg(24) - 0.1:
        paste_c(img, bubble("kan sudah bayar servis!", col=NAVY, fg=YEL, size=36, tail="right"), 690, 820,
                pop(t, sg(24) - 0.1), tag="bubble kanan")


@lru_cache(None)
def save_card():
    w, h = 800, 760
    L, d = card(w, h, fill=WHITE)
    d.rounded_rectangle((0, 0, w, 120), 30, fill=NAVY); d.rectangle((0, 70, w, 120), fill=NAVY)
    d.rounded_rectangle((0, 0, w, h), 30, outline=NAVY, width=5)
    rich_title = [("PATOKAN ", False), ("TIP", True)]
    f = F("pb", 64)
    wsum = sum(f.getlength(s) for s, _ in rich_title); x = w / 2 - wsum / 2
    for s, k in rich_title:
        ww = f.getlength(s)
        if k: d.rounded_rectangle((x - 8, 22, x + ww + 8, 100), 14, fill=YEL)
        d.text((x, 62), s, font=f, fill=NAVY if k else WHITE, anchor="lm"); x += ww
    rows = [("us", "Amerika", "tip lazim, mayoritas ≤15%", "(Pew)"),
            ("jp", "Jepang", "tip tidak lazim", "(JNTO)"),
            ("id", "Indonesia", "ada service = tip opsional", "tanpa service = tip sukarela")]
    y = 180
    for kind, neg, a, b in rows:
        flag(d, kind, 40, y - 4, 90)
        d.text((150, y + 14), neg, font=F("pb", 46), fill=NAVY, anchor="lm")
        d.text((150, y + 70), a, font=fit("pm", 38, a, w - 190), fill=INK, anchor="lm")
        d.text((150, y + 116), b, font=fit("pm", 34, b, w - 190), fill=GREY_T, anchor="lm")
        y += 170
    s = "simpan buat pas bayar bareng"; fs = F("pb", 40); e = emoji_img("📌", 46)
    tw = fs.getlength(s) + 14 + e.width; x0 = w / 2 - tw / 2
    d.rounded_rectangle((x0 - 26, h - 92, x0 + tw + 26, h - 28), 32, fill=YEL)
    d.text((x0, h - 60), s, font=fs, fill=NAVY, anchor="lm")
    L.alpha_composite(e, (int(x0 + fs.getlength(s) + 14), int(h - 61 - e.height / 2)))
    return L


def scene8(img, t):
    """kartu layak simpan (PRB-62) sepanjang adegan (±5,8 dtk)."""
    paste_c(img, save_card(), W / 2, 900, pop(t, SC[8] + 0.05, 0.4), 0, tag="kartu simpan")
    paste_c(img, aru_h(240), 870, 1390 + 5 * math.sin(t * 5), 1.0, 0, tag="aru")


def scene9(img, t):
    """dua tombol besar TIP / PAS HARGA + 'Jawab 1 kata di komentar'."""
    for j, (x, lab, col, fg) in enumerate(((330, "TIP", TEAL, WHITE), (750, "PAS HARGA", NAVY, YEL))):
        p = pop(t, SC[9] + 0.05 + 0.15 * j)
        if p <= 0: continue
        L, d = card(360, 200, fill=col, r=50)
        text_c(d, (180, 100), lab, fit("pb", 76, lab, 320), fg)
        hot = (j == 0 and t < sg(31)) or (j == 1 and t >= sg(31))
        paste_c(img, L, x, 760, p * (1.06 if hot else 1.0), 0, tag="tombol " + lab)
    text_c(ImageDraw.Draw(img), (W / 2, 900), "atau", F("pb", 40), NAVY)
    q = pop(t, SC[9] + 0.5)
    if q > 0:
        paste_c(img, pill_emoji("Jawab 1 kata di komentar", "👇", fill=YEL, fg=NAVY, size=46), W / 2, 1010, q, tag="pill komen")
    draw_aru(img, 360, 1440, 300, t)
    paste_c(img, bocor_img(), 760, 1330, 0.9, 0, tag="bocor")


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9]
assert len(SCENES) == NS


@lru_cache(None)
def header():
    """pill kategori biru tua kiri atas + logo kecil kanan atas (y≈300, PRB-41)."""
    L = Image.new("RGBA", (W, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F("pb", 32); s = "UANG SEHARI-HARI · BEDA NEGARA"
    w1 = f.getlength(s) + 52
    d.rounded_rectangle((XMIN, 30, XMIN + w1, 94), 32, fill=NAVY)
    d.text((XMIN + 26, 63), s, font=f, fill=WHITE, anchor="lm")
    lg = logo_w(190)
    L.alpha_composite(lg, (int(XMAX - lg.width), int(62 - lg.height / 2)))
    return L, (XMIN, XMIN + w1), (XMAX - lg.width, XMAX)


@lru_cache(None)
def share_layer():
    T, td = card(800, 170, fill=TEAL)
    f = F("pb", 40)
    td.text((400, 52), "Kirim ke teman yang bilang", font=f, fill=WHITE, anchor="mm")
    l2 = "'udah termasuk service kok'"
    f2 = fit("pb", 40, l2, 640)
    e = emoji_img("📤", 54); tw = f2.getlength(l2)
    x0 = (800 - tw - 68) / 2
    td.text((x0, 118), l2, font=f2, fill=YEL, anchor="lm")
    T.alpha_composite(e, (int(x0 + tw + 14), int(118 - e.height / 2)))
    return T


def share_card(img, t):
    if not (SHARE[0] <= t < SHARE[1]): return
    a = min(clamp((t - SHARE[0]) / 0.2), clamp((SHARE[1] - t) / 0.2))
    s = 0.85 + 0.15 * back((t - SHARE[0]) / 0.35)
    paste_c(img, share_layer(), W / 2, 1440 + 4 * math.sin(t * 5), s, 0, a, tag="kartu kirim")


FOLLOW_S = ("Follow, besok: kenapa kabel", "chargermu selalu putus di ujung?")


@lru_cache(None)
def follow_pill():
    f1 = F("pb", 32); f2 = fit("pb", 32, FOLLOW_S[1], MAXW - 60)
    w = int(max(f1.getlength(FOLLOW_S[0]), f2.getlength(FOLLOW_S[1])) + 60)
    pl = Image.new("RGBA", (w, 100), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
    pd.rounded_rectangle((0, 0, w, 100), 26, fill=TEAL)
    pd.text((w / 2, 30), FOLLOW_S[0], font=f1, fill=YEL, anchor="mm")
    pd.text((w / 2, 70), FOLLOW_S[1], font=f2, fill=WHITE, anchor="mm")
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
    else:
        scene0(img, t)
    if t >= HEADER_T:
        Hd, (p0, p1), (l0, l1) = header()
        paste_c(img, Hd, W / 2, 240 + 65, 1, 0, clamp((t - HEADER_T) / 0.3))
        track("header pill", p1 - p0, p0, p1); track("header logo", l1 - l0, l0, l1)
    share_card(img, t)
    draw_sub(img, t)
    if k in NOTES:
        note_lines(img, NOTES[k], a=clamp(ts / 0.3) if k else 1.0)
    if FOLLOW[0] <= t < FOLLOW[1]:
        a = min(clamp((t - FOLLOW[0]) / 0.25), clamp((FOLLOW[1] - t) / 0.25))
        paste_c(img, follow_pill(), W / 2, 1480, 1, 0, a, tag="pill follow")
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
            if tag in ("aru", "bocor", "pelayan", "kasir", "driver", "struk"):
                continue   # ilustrasi boleh dekat tepi
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
    ev.append({"t": 0.2, "sfx": "pop", "gain": 0.3})            # sorot baris Service
    ev.append({"t": 1.4, "sfx": "whoosh", "gain": 0.22})        # zoom ke baris Service
    for j in range(6):
        ev.append({"t": round(CT0 + j * (CT1 - CT0) / 6, 3), "sfx": "klik", "gain": 0.25})
    ev.append({"t": CT1, "sfx": "ding", "gain": 0.3})           # counter berhenti 20%?
    ev.append({"t": sg(5), "sfx": "pop", "gain": 0.3})          # 20%? muncul
    ev.append({"t": sg(7) + 1.4, "sfx": "ding", "gain": 0.28})  # bar 57% penuh
    ev.append({"t": sg(10) + 1.0, "sfx": "cring", "gain": 0.4}) # koin US$2,13
    ev.append({"t": sg(13) + 1.4, "sfx": "pop", "gain": 0.3})   # stempel tidak lazim
    ev.append({"t": sg(16), "sfx": "ding", "gain": 0.3})        # 95% pekerja
    ev.append({"t": SHARE[0] + 0.1, "sfx": "klik", "gain": 0.3})
    ev.append({"t": sg(20) - 0.2, "sfx": "klik", "gain": 0.35}) # tombol tambah tip
    ev.append({"t": sg(20) + 0.6, "sfx": "cring", "gain": 0.4}) # koin ke helm driver
    ev.append({"t": SC[7] + 0.2, "sfx": "cring", "gain": 0.35}) # Si Bocor muncul
    for si in (22, 24):
        ev.append({"t": sg(si) - 0.1, "sfx": "pop", "gain": 0.26})
    ev.append({"t": SC[8] + 0.05, "sfx": "pop", "gain": 0.3})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": SC[9] + 0.5, "sfx": "pop", "gain": 0.26})
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
        print("share", [round(x, 2) for x in SHARE], "follow", FOLLOW)
    elif cmd == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        ims = []
        for tt in ts:
            im = frame(tt); im.save(f"still_{tt:.2f}.png"); ims.append(im.resize((360, 640)))
        cols_ = 6; rows = math.ceil(len(ims) / cols_)
        sh = Image.new("RGB", (360 * cols_, 640 * rows), WHITE)
        for j, im in enumerate(ims):
            sh.paste(im, ((j % cols_) * 360, (j // cols_) * 640))
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

"""Renderer ARN-59 "Mana Lebih Hemat? #14 — Amplop kondangan" — Flat 2D latar terang (PRB-31).
Salinan render_flat_ldr.py (helper kartu, koin, Si Bocor, pill, bubble, timbangan, subtitle, cek area aman, sfx) dengan:
- frame 0 (PRB-29/34/36/46, satu fokus): Aru + pasangan melangkah ke meja tamu, Aru memegang SATU amplop besar,
  Si Bocor mengintip dari amplop, koin jatuh ("cring!"). Counter piring prasmanan Rp0 naik dan BERHENTI di
  "2 porsi = Rp100.000" dtk 2,0 + sumber kecil. Visual berganti ~dtk 1,5: meja tamu + kotak amplop.
  Judul layar = pill kecil "Datang berdua, amplop SATU?". Tanpa label seri/logo/progress bar dtk 0-3.
- 21 adegan (tiap <= 6 dtk); setiap angka punya teks sumber kecil; ajakan kirim di puncak Rp360.000; layar terbelah
  tim HITUNG vs tim SILATURAHMI; kartu layak simpan "PATOKAN AMPLOP" ±3 dtk (PRB-62); penutup tim vs tim.
- area aman (PRB-41): semua pill/bubble/kartu <= 800 px dan di x 130..950; `check` memindai tiap 0,1 dtk.
Pemakaian (dari folder kerja pagi/build_amplop, setelah align_amplop.py -> timing.json):
  TOTAL=63.7 python3 ../render_flat_amplop.py events | check | scenes | stills 0,2,... | video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, rp, NAVY, TEAL, YEL, WHITE, GREY_T, RED, SAFE_X)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "63.7"))
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


SCENE_SEG = [0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 25, 27, 29, 30, 32, 34, 36]
SC = [0.0] + [sg(i) - 0.25 for i in SCENE_SEG[1:]] + [TOTAL]
NS = len(SCENE_SEG)
FOLLOW = (SC[3] + 0.35, SC[5] - 0.05)   # PRB-4/63: ajakan follow teks kecil di adegan 4-5 (dtk ~9,6-14,9)
PB_START = 3.5                          # progress bar mulai dtk 3,5
CT0, CT1 = 0.45, 2.0                    # counter frame 0: naik lalu BERHENTI di Rp100.000 dtk 2,0
SRC0 = "*contoh hitungan · katering Rp35–60 rb/orang, Kupinang.id 27 Mei 2026"
NOTES = {4: ("katering gedung serbaguna Rp35–60 rb/orang", "Kupinang.id, 27 Mei 2026 · Rp50 rb = tengah kisaran"),
         5: ("*contoh hitungan dari tarif Kupinang.id",),
         6: ("amplop rekan kerja · Kontan MomsMoney, 12 Agu 2026",),
         7: ("*contoh hitungan",),
         8: ("amplop Rp50 rb fresh graduate · Mojok, 24 Apr 2026",),
         10: ("Pertalite Rp10.000/L · iNews, 19 Nov 2026 · 2 liter PP = asumsi",),
         11: ("*contoh hitungan · amplop Rp100 rb + bensin Rp20 rb",),
         12: ("*contoh hitungan dari tarif Kupinang.id",),
         16: ("cara hitung katering: undangan × 2 · Antara, 29 Jul 2024",),
         18: ("Kupinang.id, 27 Mei 2026",)}


def land(k, numseg, v, after=0.25):
    """counter adegan k: mulai SC[k]+0,35, berhenti saat angka diucapkan (paling lambat 1,2 dtk sebelum adegan habis)."""
    return (SC[k] + 0.35, min(sg(numseg) + after, SC[k + 1] - 1.2)), v


def quick(k, a, b, v): return (SC[k] + a, SC[k] + b), v


CNT = {4: land(4, 8, 50000, 0.4), 5: land(5, 10, 100000, 0.2), 10: land(10, 18, 20000, 0.2),
       11: land(11, 20, 360000, 0.5), 12: land(12, 22, 250000, 0.6)}
SHARE = (CNT[11][0][1], SC[12] - 0.05)     # ajakan kirim muncul tepat saat total Rp360.000
GOLD, GOLD_D = (255, 194, 60), (217, 154, 31)
BL, BL_D = (52, 120, 206), (34, 86, 160)
PINK = (232, 92, 140)
WOOD, WOOD_D = (196, 140, 92), (150, 100, 62)
ENV, ENV_D = (255, 247, 230), (232, 214, 182)


def cval(k, t):
    (a, b), v = CNT[k]
    if t < a: return 0, False
    if t >= b: return v, True
    u = eio((t - a) / (b - a))
    return int(round(v * u / 10000) * 10000), False


def scene_of(t):
    for k in range(NS):
        if t < SC[k + 1]: return k
    return NS - 1


def note_lines(img, lines, y0=1712):
    d = ImageDraw.Draw(img)
    for j, s in enumerate(lines):
        f = fit("pm", 28, s, MAXW)
        track("catatan", f.getlength(s), W / 2 - f.getlength(s) / 2, W / 2 + f.getlength(s) / 2)
        d.text((W / 2, y0 + j * 40), s, font=f, fill=GREY_T if j else INK, anchor="mm")


# ---------- latar ----------
@lru_cache(None)
def bg_rest():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((90, 480, 990, 1380), fill=(250, 240, 214))
    d.rectangle((0, 1490, W, H), fill=(224, 228, 236))
    return img


@lru_cache(None)
def bg_scene0(hall=False):
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((120, 640, 960, 1480), fill=(252, 236, 196))
    if hall:   # untaian janur/bendera hias pesta di atas meja tamu
        pts = [(0, 760), (270, 820), (540, 840), (810, 820), (W, 760)]
        d.line(pts, fill=(150, 120, 70), width=5, joint="curve")
        for k in range(1, 12):
            x = k * W / 12; y = 760 + 80 * math.sin(math.pi * x / W)
            col = (TEAL, YEL, PINK)[k % 3]
            d.polygon([(x - 26, y), (x + 26, y), (x, y + 52)], fill=col, outline=NAVY)
    d.rectangle((0, FLOOR0, W, H), fill=(218, 223, 232)); d.line([(0, FLOOR0), (W, FLOOR0)], fill=NAVY, width=5)
    return img


# ---------- gambar ----------
@lru_cache(None)
def envelope_img(w, label=True):
    """amplop putih tipis; tutup segitiga, tulisan 'Rp' kecil."""
    h = int(w * 0.62)
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 12, w + 10, h + 12), 18, fill=(20, 33, 91, 45))
    d.rounded_rectangle((0, 0, w, h), 18, fill=ENV, outline=NAVY, width=max(3, w // 90))
    d.line([(0, 6), (w / 2, h * 0.56), (w, 6)], fill=NAVY, width=max(3, w // 90))
    d.polygon([(6, 6), (w / 2, h * 0.54), (w - 6, 6)], fill=ENV_D)
    d.line([(0, h - 4), (w * 0.4, h * 0.5)], fill=ENV_D, width=max(2, w // 120))
    d.line([(w, h - 4), (w * 0.6, h * 0.5)], fill=ENV_D, width=max(2, w // 120))
    if label:
        d.ellipse((w / 2 - w * 0.09, h * 0.47, w / 2 + w * 0.09, h * 0.47 + w * 0.18), fill=RED, outline=NAVY, width=3)
        text_c(d, (w / 2, h * 0.47 + w * 0.09), "♥" if False else "Rp", F("pb", max(14, int(w * 0.07))), WHITE)
    im.info["nw"] = w
    return im


@lru_cache(None)
def plate_img(w, food=True):
    h = int(w * 0.42)
    im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((4, 4, w + 4, h + 4), fill=WHITE, outline=NAVY, width=max(3, w // 60))
    d.ellipse((w * 0.16, h * 0.18, w * 0.84, h * 0.82), outline=(200, 206, 218), width=max(2, w // 90))
    if food:
        d.ellipse((w * 0.22, h * 0.10, w * 0.58, h * 0.62), fill=(250, 250, 244), outline=NAVY, width=3)  # nasi
        d.ellipse((w * 0.48, h * 0.22, w * 0.78, h * 0.68), fill=(206, 98, 52), outline=NAVY, width=3)     # rendang
        d.ellipse((w * 0.30, h * 0.46, w * 0.52, h * 0.80), fill=(92, 170, 90), outline=NAVY, width=3)     # sayur
    im.info["nw"] = w
    return im


@lru_cache(None)
def pot_img(w):
    """panci katering dengan uap."""
    im = Image.new("RGBA", (w, int(w * 0.9)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(3):
        x = w * (0.32 + 0.18 * k)
        d.arc((x - 20, w * 0.02, x + 20, w * 0.3), 100, 260, fill=(170, 178, 195), width=7)
    d.rounded_rectangle((w * 0.08, w * 0.36, w * 0.92, w * 0.86), 26, fill=(190, 198, 214), outline=NAVY, width=6)
    d.rounded_rectangle((w * 0.02, w * 0.30, w * 0.98, w * 0.42), 14, fill=(214, 220, 232), outline=NAVY, width=6)
    d.rounded_rectangle((w * 0.42, w * 0.22, w * 0.58, w * 0.31), 8, fill=NAVY)
    for x in (0.0, 0.92):
        d.rounded_rectangle((w * x, w * 0.5, w * x + w * 0.1, w * 0.6), 6, fill=NAVY)
    return im


@lru_cache(None)
def person_img(h, kind):
    """tokoh pendukung flat sederhana. kind: 'pasangan' (kerudung toska), 'om' (kumis, batik), 'tante' (kerudung pink),
    'anak1' (rambut, kaos kuning), 'anak2' (kuncir, kaos toska), 'anak3' (balita)."""
    im = Image.new("RGBA", (320, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    SK = (240, 196, 160)
    shirt = {"pasangan": (250, 250, 250), "om": (160, 92, 50), "tante": (120, 84, 160), "anak1": YEL,
             "anak2": TEAL, "anak3": (250, 140, 150)}[kind]
    if kind in ("pasangan", "tante"):   # gamis panjang
        d.polygon([(100, 250), (220, 250), (250, 520), (70, 520)], fill=shirt, outline=NAVY)
        d.line([(100, 250), (70, 520), (250, 520), (220, 250)], fill=NAVY, width=6)
        for x in (110, 180):
            d.ellipse((x - 6, 510, x + 50, 540), fill=(70, 74, 96), outline=NAVY, width=5)
    else:
        for x in (112, 168):
            d.rounded_rectangle((x, 400, x + 42, 520), 16, fill=(70, 74, 96), outline=NAVY, width=6)
            d.ellipse((x - 14, 500, x + 56, 540), fill=WHITE, outline=NAVY, width=6)
        d.rounded_rectangle((86, 240, 236, 420), 40, fill=shirt, outline=NAVY, width=6)
        if kind == "om":   # motif batik
            for (x, y) in ((120, 290), (190, 300), (150, 360), (210, 380), (110, 390)):
                d.ellipse((x - 12, y - 12, x + 12, y + 12), outline=(250, 214, 120), width=5)
    for side in (-1, 1):   # lengan
        x0 = 160 + side * 70
        d.line([(x0, 270), (x0 + side * 30, 380)], fill=NAVY, width=32)
        d.line([(x0, 270), (x0 + side * 30, 380)], fill=shirt, width=20)
        d.ellipse((x0 + side * 30 - 18, 370, x0 + side * 30 + 18, 406), fill=SK, outline=NAVY, width=5)
    d.ellipse((76, 60, 246, 240), fill=SK, outline=NAVY, width=6)                       # kepala
    if kind in ("pasangan", "tante"):
        col = TEAL if kind == "pasangan" else PINK
        d.chord((62, 40, 260, 250), 160, 380, fill=col, outline=NAVY, width=6)
        d.polygon([(70, 160), (96, 250), (226, 250), (252, 160), (240, 290), (82, 290)], fill=col, outline=NAVY)
        d.ellipse((96, 92, 226, 236), fill=SK, outline=NAVY, width=5)
    elif kind == "om":
        d.chord((76, 50, 246, 170), 180, 360, fill=(40, 36, 52))
        d.rounded_rectangle((100, 26, 222, 76), 14, fill=(30, 30, 40))                    # peci
        d.line([(128, 196), (160, 186), (192, 196)], fill=(40, 36, 52), width=10)          # kumis
    elif kind == "anak2":
        d.chord((76, 56, 246, 176), 180, 360, fill=(60, 44, 36))
        d.ellipse((230, 90, 276, 136), fill=(60, 44, 36))
    else:
        d.chord((76, 56, 246, 170), 180, 360, fill=(60, 44, 36))
    d.ellipse((126, 140, 142, 160), fill=NAVY); d.ellipse((180, 140, 196, 160), fill=NAVY)
    d.arc((132, 176, 190, 214), 20, 160, fill=NAVY, width=5)
    im = trim(im); r = h / im.height
    out = im.resize((int(im.width * r), h), Image.LANCZOS)
    out.info["nw"] = out.width
    return out


@lru_cache(None)
def box_img(w):
    """kotak amplop di meja tamu (bercelah)."""
    h = int(w * 0.9)
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 10, w + 8, h + 10), 16, fill=(20, 33, 91, 45))
    d.rounded_rectangle((0, 0, w, h), 16, fill=(255, 232, 150), outline=NAVY, width=6)
    d.rounded_rectangle((w * 0.2, 22, w * 0.8, 44), 8, fill=NAVY)
    d.rounded_rectangle((w * 0.1, h * 0.38, w * 0.9, h * 0.72), 12, fill=WHITE, outline=NAVY, width=4)
    text_c(d, (w / 2, h * 0.55), "AMPLOP", fit("pb", 40, "AMPLOP", w * 0.7), NAVY)
    im.info["nw"] = w
    return im


def title_pill(img):
    """judul layar = pill kecil (bukan kartu judul besar, PRB-36): 'Datang berdua, amplop SATU?' (SATU? kuning)."""
    a, b = "Datang berdua, amplop ", "SATU?"
    size = 46
    while True:
        f = F("pb", size)
        wa, wb = f.getlength(a), f.getlength(b)
        w = int(wa + wb + 24 + 60)
        if w <= 780: break
        size -= 2
    h = 84
    P = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(P)
    d.rounded_rectangle((8, 10, w + 8, h + 10), h // 2, fill=(20, 33, 91, 55))
    d.rounded_rectangle((0, 0, w, h), h // 2, fill=NAVY)
    d.text((30, h / 2 + 2), a, font=f, fill=WHITE, anchor="lm")
    d.rounded_rectangle((30 + wa - 4, 12, 30 + wa + wb + 20, h - 12), 14, fill=YEL)
    d.text((30 + wa + 8, h / 2 + 2), b, font=f, fill=NAVY, anchor="lm")
    P.info["nw"] = w
    paste_c(img, P, W / 2, 320, tag="pill judul")


def counter0(t):
    if t < CT0: return 0, False
    if t >= CT1: return 100000, True
    u = eio((t - CT0) / (CT1 - CT0))
    v = 100000 * u + ((137 * int(t * 30)) % 9) * 1000 * u * (1 - u)
    return int(round(v / 10000.0) * 10000), False


def counter_card(img, t, cy, scale=1.0):
    v, done = counter0(t)
    hot = t >= CT0
    L, d = card(780, 210, fill=(255, 244, 214) if done else WHITE, outline=GOLD_D if done else NAVY, ow=7)
    for j in range(2):
        L.alpha_composite(plate_img(130), (40 + j * 70, 34 + j * 52))
    text_c(d, (150, 182), "2 porsi", F("pb", 34), NAVY)
    s = rp(v)
    text_c(d, (520, 105), ("= " if done else "") + s, fit("pb", 104, "= " + s, 470), NAVY)
    paste_c(img, L, W / 2, cy, scale, tag="counter")


def falling_coins(img, t, x0, y0, y1, t0, n=6, spread=150):
    if t < t0: return
    for k in range(n):
        u = ((t - t0) * 1.1 + k / n) % 1.0
        x = x0 - spread / 2 + spread * ((k * 37) % n) / n + 12 * math.sin(t * 4 + k)
        y = y0 + (y1 - y0) * u * u
        paste_c(img, coin(22), x, y, 1.0, 40 * math.sin(t * 6 + k))


def hand(d, x, y, r=26):
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 211, 176), outline=NAVY, width=6)


def scene0(img, t):
    """frame 0: Aru + pasangan melangkah, Aru memegang SATU amplop besar, Si Bocor mengintip dari amplop, koin jatuh;
    counter 2 porsi naik & berhenti Rp100.000 dtk 2,0; ~dtk 1,5 meja tamu + kotak amplop muncul."""
    title_pill(img)
    sc = 1.0 + (0.06 * back((t - CT1) / 0.3) - 0.06 * clamp((t - CT1 - 0.3) / 0.3) if t >= CT1 else 0)
    counter_card(img, t, 560, sc)
    sp = eio((t - 1.3) / 0.4)                   # visual berganti ~dtk 1,5
    walk = 40 * (1 - eout(t / 1.6))
    d = ImageDraw.Draw(img)
    if sp > 0:                                  # meja tamu + kotak amplop masuk dari kanan
        tx = 30 * (1 - sp)
        d.rounded_rectangle((560 + tx, 1250, 1000 + tx, 1290), 10, fill=WOOD, outline=NAVY, width=5)
        d.rectangle((600 + tx, 1290, 620 + tx, FLOOR0), fill=WOOD_D); d.rectangle((940 + tx, 1290, 960 + tx, FLOOR0), fill=WOOD_D)
        paste_c(img, box_img(230), 790 + tx, 1250 - 110, 1.0, 0, sp, tag="kotak amplop")
        text_c(d, (780 + tx, 1360), "MEJA TAMU", F("pb", 34), NAVY)
    paste_c(img, person_img(400, "pasangan"), 470 - walk, FLOOR0 - 200 + 5 * math.sin(t * 7 + 1), 1.0,
            1.5 * math.sin(t * 3), tag="pasangan")
    draw_aru(img, 312 - walk, FLOOR0, 430, t)
    ex = 600 - walk + 170 * sp; ey = 1060 - 130 * sp
    es = 1.0 - 0.25 * sp
    paste_c(img, envelope_img(420), ex, ey + 4 * math.sin(t * 3), es, -4 + 2 * math.sin(t * 2), tag="amplop")
    chew = abs(math.sin(t * 11)) * 8
    paste_c(img, bocor_img(), ex + 80 * es, ey - 150 * es - chew, 0.48 * es, -10 + 6 * math.sin(t * 11), tag="bocor")
    if sp < 0.5:
        hand(d, 430 - walk, 1150); hand(d, 470 - walk, 1010)
    falling_coins(img, t, ex + 120, ey + 90, FLOOR0 - 20, 0.3, n=4, spread=90)
    p = pop(t, 1.5)
    if p > 0:
        paste_c(img, bubble("cring!", col=YEL, fg=NAVY, size=48, tail="left"), 640, 1310, p, -4, tag="bubble cring")


def scene1(img, t):
    """coba tebak siapa yang tekor: layar terbelah KAMU (dompet) vs PENGANTIN (panci katering), tanda ? di tengah."""
    d = ImageDraw.Draw(img)
    for k, (x, lab, col, im, t0) in enumerate(((330, "KAMU", BL, wallet_img(280), SC[1] + 0.05),
                                               (750, "PENGANTIN", TEAL, pot_img(300), SC[1] + 0.2))):
        p = pop(t, t0)
        if p <= 0: continue
        paste_c(img, im, x, 880 + 6 * math.sin(t * 3 + k), p, 3 * math.sin(t * 2 + k))
        paste_c(img, pill(lab, fill=col, fg=WHITE, size=46), x, 1080, p, tag="pill " + lab)
    d.line([(540, 620), (540, 1160)], fill=(200, 205, 216), width=6)
    q = pop(t, sg(3) - 0.05)
    if q > 0:
        L = Image.new("RGBA", (180, 180), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.ellipse((6, 6, 174, 174), fill=YEL, outline=NAVY, width=7)
        text_c(ld, (90, 88), "?", F("pb", 110), NAVY)
        L.info["nw"] = 180
        paste_c(img, L, W / 2, 680, q, 8 * math.sin(t * 4), tag="lencana ?")
    draw_aru(img, W / 2, 1480, 290, t)


FAM = [("om", 380), ("tante", 360), ("anak1", 260), ("anak2", 240), ("anak3", 190)]


def family(img, t, t_list, x0=230, dx=150, bottom=1440, scale=1.0):
    for j, ((kind, h), t0) in enumerate(zip(FAM, t_list)):
        p = pop(t, t0)
        if p <= 0: continue
        hh = int(h * scale)
        paste_c(img, person_img(hh, kind), x0 + dx * j, bottom - hh / 2 + 4 * math.sin(t * 6 + j), p,
                1.5 * math.sin(t * 3 + j), tag="keluarga")


def scene2(img, t):
    """kamu pasti kenal: om ramah datang berlima, satu amplop di tangan (hangat)."""
    p = pop(t, SC[2] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Kamu pasti kenal", "👀", fill=YEL, fg=NAVY, size=48), W / 2, 470, p, -2, tag="pill kenal")
    a = sg(4) + 1.2
    family(img, t, [SC[2] + 0.15, a, a + 0.15, a + 0.3, a + 0.45])
    q = pop(t, sg(4) + 1.5)
    if q > 0:
        L = Image.new("RGBA", (130, 130), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.ellipse((4, 4, 126, 126), fill=NAVY); text_c(ld, (65, 64), "×5", F("pb", 54), YEL)
        L.info["nw"] = 130
        paste_c(img, L, 800, 760, q, 6 * math.sin(t * 4), tag="lencana x5")
    r = pop(t, sg(5) - 0.05)
    if r > 0:
        paste_c(img, envelope_img(120), 300, 1310 - 10 * abs(math.sin(t * 5)), r, -8, tag="amplop om")
        paste_c(img, bubble("1 amplop", col=NAVY, fg=YEL, size=44, tail="left"), 360, 800, r, -2, tag="bubble 1 amplop")


def scene3(img, t):
    """hitung dari dapur pengantin: panci katering + deretan piring yang terus bertambah."""
    paste_c(img, pill("DAPUR PENGANTIN", fill=TEAL, fg=WHITE, size=52), W / 2, 470, pop(t, SC[3] + 0.05), -2, tag="pill dapur")
    paste_c(img, pot_img(340), W / 2, 760 + 5 * math.sin(t * 3), pop(t, SC[3] + 0.1), tag="panci")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((150, 1180, 930, 1210), 10, fill=WOOD, outline=NAVY, width=5)
    for r_ in range(2):
        for c_ in range(5):
            k = r_ * 5 + c_
            q = pop(t, SC[3] + 0.3 + 0.1 * k)
            if q > 0:
                paste_c(img, plate_img(130), 230 + 155 * c_, 1150 - 120 * r_ if r_ else 1150, q, tag="piring")


def amount_card(title, sub, value, col, extra=None, w=800, h=470, fill=WHITE):
    T, td = card(w, h, fill=fill, outline=col, ow=8)
    text_c(td, (w / 2, 64), title, fit("pb", 48, title, w - 60), col)
    if sub: text_c(td, (w / 2, 122), sub, fit("pm", 38, sub, w - 60), GREY_T)
    td.rounded_rectangle((40, 160, w - 40, 350), 30, fill=col)
    text_c(td, (w / 2, 256), value, fit("pb", 120, value, w - 120), WHITE)
    if extra:
        text_c(td, (w / 2, 410), extra, fit("pb", 44, extra, w - 60), NAVY)
    return T


def item_scene(img, t, k, title, sub, col, extra, icon, cy=860):
    paste_c(img, icon, W / 2, 500, pop(t, SC[k] + 0.05), 6 * math.sin(t * 3))
    v, done = cval(k, t)
    T = amount_card(title, sub, rp(v), col, extra if done else None)
    paste_c(img, T, W / 2, cy, pop(t, SC[k] + 0.1) * (1 + 0.02 * math.sin(t * 8)), -1.2)
    track("kartu " + title, 800, W / 2 - 400, W / 2 + 400)


def scene4(img, t):
    item_scene(img, t, 4, "KATERING GEDUNG SERBAGUNA", "Rp35–60 rb/orang, ambil tengahnya", TEAL, "per orang",
               plate_img(220))


def scene5(img, t):
    item_scene(img, t, 5, "KAMU BERDUA MAKAN", "2 × Rp50.000", TEAL, "= 2 porsi untuk pengantin",
               emoji_img("👫", 170))


def scene6(img, t):
    """amplop rekan kerja biasanya Rp100-200 rb."""
    paste_c(img, envelope_img(280), W / 2, 520, pop(t, SC[6] + 0.05), 6 * math.sin(t * 3), tag="amplop")
    q = pop(t, sg(11) + 1.6)
    T = amount_card("AMPLOP REKAN KERJA", "biasanya", "Rp100–200 rb" if q > 0 else "Rp…", BL,
                    "isi umum ke kondangan kantor" if q > 0 else None)
    paste_c(img, T, W / 2, 900, pop(t, SC[6] + 0.1) * (1 + 0.04 * (q > 0) * math.sin((t - sg(11) - 1.6) * 9) * (t - sg(11) < 2.2)), 1.2)
    track("kartu amplop", 800, W / 2 - 400, W / 2 + 400)


def scale_img(tilt, lt, rt, lcol, rcol):
    """timbangan; tilt > 0 = sisi kiri turun (lebih berat)."""
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


def scale_scene(img, t, k, tilt_to, lt, rt, t_tilt):
    tilt = tilt_to * eout((t - t_tilt) / 0.6)
    paste_c(img, scale_img(round(tilt, 2), lt, rt, BL, TEAL), W / 2, 900, pop(t, SC[k] + 0.1), tag="timbangan")
    d = ImageDraw.Draw(img)
    text_c(d, (W / 2 - 300, 1215), "AMPLOP", F("pb", 40), BL)
    text_c(d, (W / 2 + 290, 1215), "MAKAN 2 ORANG", F("pb", 36), TEAL)
    return tilt


def scene7(img, t):
    """isi Rp100 rb? Pas: timbangan seimbang Rp100.000 = Rp100.000."""
    paste_c(img, pill("Isi Rp100.000?", fill=NAVY, fg=WHITE, size=50), W / 2, 470, pop(t, SC[7] + 0.05), -2, tag="pill isi")
    scale_scene(img, t, 7, 0.0, "Rp100 rb", "Rp100 rb", SC[7])
    q = pop(t, sg(13) - 0.05)
    if q > 0:
        S = stamp("PAS!", col=GREEN, size=80); S.info["nw"] = S.width
        paste_c(img, S, W / 2, 1340, q * 1.0, -8, tag="stempel pas")
        icon_check(ImageDraw.Draw(img), W / 2 + 190, 1340, 0.9 * q)


def scene8(img, t):
    """isi Rp50 rb? timbangan miring ke sisi makan, Si Bocor menggigit sisi pengantin; -Rp50.000."""
    paste_c(img, pill("Isi Rp50.000?", fill=NAVY, fg=WHITE, size=50), W / 2, 470, pop(t, SC[8] + 0.05), -2, tag="pill isi")
    tilt = scale_scene(img, t, 8, -1.0, "Rp50 rb", "Rp100 rb", SC[8] + 0.35)
    q = pop(t, SC[8] + 0.6)
    if q > 0:
        ry = 900 - 310 + 300 * math.sin(math.radians(12 * -tilt)) + 190
        paste_c(img, bocor_img(), W / 2 + 300, ry - 70 + 6 * math.sin(t * 9), 0.38 * q, -12 + 8 * math.sin(t * 11), tag="bocor")
    r = pop(t, sg(15) + 0.3)
    if r > 0:
        paste_c(img, pill("PENGANTIN −Rp50.000", fill=RED, fg=WHITE, size=50), W / 2, 1340, r, 2, tag="pill tekor")


def scene9(img, t):
    """tapi kamu juga keluar ongkos: balik ke sisi KAMU, Aru menyalakan motor (asap knalpot)."""
    paste_c(img, pill("SISI KAMU", fill=BL, fg=WHITE, size=54), W / 2, 470, pop(t, SC[9] + 0.05), -2, tag="pill sisi kamu")
    shake = 4 * math.sin(t * 40) if t > SC[9] + 0.6 else 0
    paste_c(img, emoji_img("🛵", 380), 640 + shake, 1060, pop(t, SC[9] + 0.15), tag="motor")
    if t > SC[9] + 0.6:
        for k in range(4):
            u = ((t - SC[9]) * 1.4 + k / 4) % 1.0
            r = 20 + 40 * u
            a = int(200 * (1 - u))
            L = Image.new("RGBA", (int(2 * r) + 4, int(2 * r) + 4), (0, 0, 0, 0))
            ImageDraw.Draw(L).ellipse((2, 2, 2 * r + 2, 2 * r + 2), fill=(170, 178, 195, a))
            img.alpha_composite(L, (int(860 + 120 * u - r), int(1150 - 60 * u - r)))
    draw_aru(img, 330, 1440, 380, t)


def scene10(img, t):
    item_scene(img, t, 10, "BENSIN PULANG PERGI", "2 L × Rp10.000", BL, "per kondangan", emoji_img("⛽", 170))


@lru_cache(None)
def invite_img(w, n=0):
    h = int(w * 0.66)
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 10, w + 8, h + 10), 14, fill=(20, 33, 91, 50))
    d.rounded_rectangle((0, 0, w, h), 14, fill=(255, 250, 238), outline=NAVY, width=5)
    d.rounded_rectangle((10, 10, w - 10, h - 10), 10, outline=GOLD_D, width=3)
    text_c(d, (w / 2, h * 0.34), "UNDANGAN", fit("pb", 34, "UNDANGAN", w - 40), NAVY)
    text_c(d, (w / 2, h * 0.66), ("Sabtu", "Minggu", "Sabtu")[n % 3], F("pm", 26), GREY_T)
    im.info["nw"] = w
    return im


def scene11(img, t):
    """PUNCAK: tiga undangan jatuh ke tangan Aru, counter 3 × (Rp100.000 + Rp20.000) = Rp360.000 + ajakan kirim."""
    v, done = cval(11, t)
    T = amount_card("MINGGU INI: 3 UNDANGAN", "3 × (Rp100.000 + Rp20.000)", rp(v), RED, "melayang" if done else None)
    sc = pop(t, SC[11] + 0.1) * (1 + (0.05 * math.sin((t - CNT[11][0][1]) * 10) if done and t - CNT[11][0][1] < 0.6 else 0))
    paste_c(img, T, W / 2, 700, sc, -1.2)
    track("kartu puncak", 800, W / 2 - 400, W / 2 + 400)
    draw_aru(img, 300, 1300, 330, t)
    for j in range(3):
        t0 = SC[11] + 0.2 + 0.35 * j
        if t < t0: continue
        u = eout((t - t0) / 0.5)
        y = 960 + (1080 + 18 * j - 960) * u
        paste_c(img, invite_img(190, j), 560 + 70 * j, y - (1 - u) * 200, 1.0, (-12 + 12 * j) * (1 - 0.5 * u), tag="undangan")
    if done:
        falling_coins(img, t, 760, 1040, 1300, CNT[11][0][1], n=4, spread=120)


def scene12(img, t):
    """om yang berlima: lima piring di prasmanan, 5 × Rp50.000 = Rp250.000."""
    v, done = cval(12, t)
    T = amount_card("OM BERLIMA MAKAN", "5 × Rp50.000", rp(v), TEAL, "amplopnya tetap satu" if done else None)
    paste_c(img, T, W / 2, 680, pop(t, SC[12] + 0.1), 1.2)
    track("kartu om", 800, W / 2 - 400, W / 2 + 400)
    for j in range(5):
        q = pop(t, SC[12] + 0.3 + 0.12 * j)
        if q > 0:
            paste_c(img, plate_img(120), 240 + 150 * j, 1010, q, tag="piring")
    family(img, t, [SC[12] + 0.2 + 0.05 * j for j in range(5)], bottom=1440, scale=0.82)


COLS = [(140, 530, BL, "HITUNG"), (550, 940, TEAL, "SILATURAHMI")]
SPLIT_Y = 470


def cols(img, active):
    d = ImageDraw.Draw(img)
    for j, (x0, x1, col, lab) in enumerate(COLS):
        act = j == active
        fill = (255, 255, 255) if act else (232, 235, 242)
        d.rounded_rectangle((x0, SPLIT_Y, x1, 1440), 30, fill=fill, outline=col if act else (200, 205, 216), width=6)
        d.rounded_rectangle((x0, SPLIT_Y, x1, SPLIT_Y + 120), 30, fill=col if act else (190, 196, 210))
        d.rectangle((x0, SPLIT_Y + 70, x1, SPLIT_Y + 120), fill=col if act else (190, 196, 210))
        text_c(d, ((x0 + x1) / 2, SPLIT_Y + 34), "TIM", F("pb", 30), WHITE)
        text_c(d, ((x0 + x1) / 2, SPLIT_Y + 82), lab, fit("pb", 48, lab, x1 - x0 - 30), WHITE)
        track("kolom " + lab, x1 - x0, x0, x1)
    d.ellipse((540 - 42, SPLIT_Y + 170 - 42, 540 + 42, SPLIT_Y + 170 + 42), fill=YEL, outline=NAVY, width=5)
    text_c(d, (540, SPLIT_Y + 168), "vs", F("pb", 38), NAVY)


def scene13(img, t):
    """layar terbelah tim HITUNG vs tim SILATURAHMI (warna netral): 'Tunggu, tim silaturahmi menjawab.'"""
    cols(img, 1)
    paste_c(img, emoji_img("🧮", 220) if False else wallet_img(260), 335, 1060, pop(t, SC[13] + 0.05))
    paste_c(img, emoji_img("🤝", 230), 745, 1060, pop(t, SC[13] + 0.1))
    q = pop(t, SC[13] + 0.1)
    if q > 0:
        paste_c(img, bubble("Tunggu!", col=TEAL, fg=WHITE, size=56, tail="right"), 745, 830, q * (1 + 0.03 * math.sin(t * 9)), 3,
                tag="bubble tunggu")


def scene14(img, t):
    """kondangan itu doa, bukan jual beli: pengantin menyalami tamu (Aru)."""
    p = pop(t, sg(26) - 0.1)
    paste_c(img, pill("doa, bukan jual beli", fill=YEL, fg=NAVY, size=54), W / 2, 470, max(p, 0.0) if p > 0 else 0,
            -2, tag="pill doa")
    paste_c(img, emoji_img("🤵", 300), 300, 1000, pop(t, SC[14] + 0.05), 2 * math.sin(t * 2))
    paste_c(img, emoji_img("👰", 300), 470, 1000, pop(t, SC[14] + 0.12), -2 * math.sin(t * 2))
    q = pop(t, SC[14] + 0.6)
    if q > 0:
        paste_c(img, emoji_img("🤝", 140), 640, 1180 + 6 * math.sin(t * 8), q)
    draw_aru(img, 800, 1440, 380, t)
    r = pop(t, SC[14] + 0.3)
    if r > 0:
        paste_c(img, bubble("Barakallah!", col=NAVY, fg=YEL, size=42, tail="left"), 400, 720, r, -2, tag="bubble doa")


def scene15(img, t):
    """amplop berangkat sekarang, kembali 'waktu kamu nikah' (panah melingkar)."""
    d = ImageDraw.Draw(img)
    for j, (x, top, low, em, t0) in enumerate(((300, "SEKARANG", "kamu kondangan", "💌", SC[15] + 0.1),
                                               (780, "NANTI", "waktu kamu nikah", "💍", sg(28) + 1.2))):
        q = pop(t, t0)
        if q <= 0: continue
        C, cd = head_card(320, 380, top, col=BL if j == 0 else TEAL, size=42)
        e = emoji_img(em, 130)
        C.alpha_composite(e, (int(160 - e.width / 2), 130))
        text_c(cd, (160, 320), low, fit("pb", 34, low, 290), NAVY)
        paste_c(img, C, x, 940, q, 2 * math.sin(t * 3 + j), tag="kartu " + top)
    a = clamp((t - SC[15] - 0.4) / 1.6)
    if a > 0:   # busur atas: berangkat; busur bawah: kembali
        n = 40
        top_pts = [(300 + 480 * u, 720 - 140 * math.sin(math.pi * u)) for u in [i / n for i in range(int(n * a) + 1)]]
        if len(top_pts) > 1: d.line(top_pts, fill=BL, width=8, joint="curve")
        b = clamp((t - sg(28) - 0.6) / 1.4)
        if b > 0:
            bot = [(780 - 480 * u, 1160 + 140 * math.sin(math.pi * u)) for u in [i / n for i in range(int(n * b) + 1)]]
            if len(bot) > 1:
                d.line(bot, fill=TEAL, width=8, joint="curve")
                (xa, ya), (xb, yb) = bot[-2], bot[-1]
                arrow(d, xa, ya, xb, yb, TEAL, w=8, head=34)
            ex, ey = bot[-1]
        else:
            ex, ey = top_pts[-1]
        paste_c(img, envelope_img(110, False), ex, ey, 1.0, 0)


def scene16(img, t):
    """kartu undangan '1 undangan = 2 orang'."""
    q = pop(t, SC[16] + 0.1)
    C, cd = card(760, 620, fill=(255, 250, 238), outline=GOLD_D, ow=8)
    cd.rounded_rectangle((18, 18, 742, 602), 22, outline=GOLD_D, width=3)
    text_c(cd, (380, 90), "UNDANGAN PERNIKAHAN", F("pb", 46), NAVY)
    text_c(cd, (380, 150), "catatan katering pengantin", F("pm", 34), GREY_T)
    r = clamp((t - sg(29) - 2.0) / 0.3)
    s1 = "1 undangan = 2 orang"
    text_c(cd, (380, 260), s1, fit("pb", 66, s1, 600), NAVY)
    e = emoji_img("👫", 190)
    C.alpha_composite(e, (int(380 - e.width / 2), 330))
    if r > 0:
        cd.rounded_rectangle((50, 212, 710, 308), 20, outline=GREEN, width=6)
    paste_c(img, C, W / 2, 900, q, -1.5, tag="kartu undangan")
    if r > 0:
        icon_check(ImageDraw.Draw(img), 880, 600, r)


def scene17(img, t):
    """yang bikin tekor bukan berdua (redup), tapi datang melebihi undangan (menyala kuning)."""
    dim = clamp((t - sg(30) - 1.3) / 0.5)
    for j, (x, em, l1, l2, t_on) in enumerate(((330, "👫", "DATANG", "BERDUA", SC[17] + 0.1),
                                                (750, "👪", "MELEBIHI", "UNDANGAN", sg(31) + 0.4))):
        q = pop(t, SC[17] + 0.1 + 0.1 * j)
        lit = (j == 0 and t >= t_on and dim < 1) or (j == 1 and t >= t_on)
        C, cd = card(380, 440, fill=(255, 236, 160) if (lit and j == 1) else WHITE,
                     outline=GOLD_D if (lit and j == 1) else NAVY, ow=9 if lit and j == 1 else 6)
        ee = emoji_img(em, 140)
        C.alpha_composite(ee, (int(190 - ee.width / 2), 40))
        text_c(cd, (190, 250), l1, fit("pb", 56, l1, 340), NAVY)
        text_c(cd, (190, 320), l2, fit("pb", 56, l2, 340), NAVY)
        alpha = 1.0 - 0.6 * dim if j == 0 else 1.0
        sc = q * (1.0 + (0.06 * math.sin((t - t_on) * 9) if j == 1 and lit and t - t_on < 0.6 else 0))
        paste_c(img, C, x, 950, sc, 0, alpha, tag="pos " + l2)
        if j == 0 and t >= SC[17] + 0.3:
            icon_check(ImageDraw.Draw(img), x + 150, 760, 0.8)
    if dim > 0.3:
        text_c(ImageDraw.Draw(img), (330, 1215), "bukan ini", F("pb", 44), GREY_T)
    if t >= sg(31) + 0.4:
        text_c(ImageDraw.Draw(img), (750, 1215), "ini penyebabnya", F("pb", 40), RED)


def scene18(img, t):
    """KARTU LAYAK SIMPAN (PRB-62): PATOKAN AMPLOP = porsi × orang yang datang."""
    q = pop(t, SC[18] + 0.05)
    C, cd = head_card(800, 900, "PATOKAN AMPLOP", col=NAVY, size=52)
    s = "= porsi × orang yang datang"
    cd.rounded_rectangle((30, 120, 770, 220), 22, fill=YEL)
    text_c(cd, (400, 170), s, fit("pb", 52, s, 700), NAVY)
    rows = [("Sendiri", "1 porsi"), ("Berdua", "2 porsi"), ("Bawa anak", "+ porsi per anak")]
    for j, (a, b) in enumerate(rows):
        y = 290 + 90 * j
        cd.text((60, y), a, font=F("pm", 44), fill=GREY_T, anchor="lm")
        cd.text((740, y), b, font=fit("pb", 46, b, 420), fill=NAVY, anchor="rm")
    dashed(cd, [(50, 548), (750, 548)], (190, 196, 210), w=4)
    for j, (a, b) in enumerate((("Gedung serbaguna", "Rp35–60 rb/orang"), ("Hotel premium", "Rp250–400 rb/orang"))):
        y = 610 + 80 * j
        cd.text((50, y), a, font=F("pm", 32), fill=GREY_T, anchor="lm")
        cd.text((750, y), b, font=fit("pb", 40, b, 380), fill=TEAL if j == 0 else BL, anchor="rm")
    P = pill_emoji("simpan buat undangan berikutnya", "📌", fill=WHITE, fg=NAVY, size=32, padx=26)
    C.alpha_composite(P, (int(400 - P.width / 2), 790))
    paste_c(img, C, W / 2, 960, q, 0, tag="kartu patokan")


@lru_cache(None)
def phone_img(done):
    w, h = 340, 600
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 10, w + 8, h + 10), 44, fill=(20, 33, 91, 50))
    d.rounded_rectangle((0, 0, w, h), 44, fill=NAVY)
    d.rounded_rectangle((18, 50, w - 18, h - 40), 26, fill=(244, 247, 251))
    d.rounded_rectangle((130, 18, 210, 32), 7, fill=(60, 70, 120))
    text_c(d, (w / 2, 110), "TRANSFER", F("pb", 40), NAVY)
    text_c(d, (w / 2, 165), "ke rekening", F("pm", 30), GREY_T)
    text_c(d, (w / 2, 205), "pengantin", F("pb", 34), NAVY)
    e = emoji_img("💌", 110)
    im.alpha_composite(e, (int(w / 2 - e.width / 2), 250))
    d.rounded_rectangle((50, 420, w - 50, 500), 40, fill=GREEN if done else TEAL)
    text_c(d, (w / 2, 460), "TERKIRIM" if done else "KIRIM", F("pb", 38), WHITE)
    im.info["nw"] = w
    return im


def scene19(img, t):
    """nggak bisa datang? transfer tetap dihitung: HP transfer ke rekening pengantin, centang."""
    done = t >= sg(35) + 0.3
    paste_c(img, phone_img(done), 640, 930, pop(t, SC[19] + 0.05), 3 * math.sin(t * 2), tag="hp")
    if done:
        icon_check(ImageDraw.Draw(img), 800, 650, 1.3 * back((t - sg(35) - 0.3) / 0.3))
    draw_aru(img, 300, 1440, 360, t)


def scene20(img, t):
    """penutup: Tim SATU amplop atau MASING-MASING? Komen satu kata!"""
    for k, (s, col, t0) in enumerate((("TIM SATU AMPLOP", BL, SC[20] + 0.05), ("TIM MASING-MASING", TEAL, sg(37)))):
        p = pop(t, t0)
        if p <= 0: continue
        beat = 1 + 0.04 * math.sin((t - t0) * 7 + k * math.pi)
        paste_c(img, pill(s, fill=col, fg=WHITE, size=52, h=116), W / 2, 520 if k == 0 else 720, p * beat,
                -2 if k == 0 else 2, tag=s)
    if t >= sg(37):
        text_c(ImageDraw.Draw(img), (W / 2, 620), "atau", F("pb", 40), NAVY)
    p = pop(t, sg(37) + 0.3)
    if p > 0:
        B = Image.new("RGBA", (800, 250), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 800, 200), 34, fill=YEL, outline=NAVY, width=5)
        bd.polygon([(110, 196), (180, 196), (90, 246)], fill=YEL, outline=NAVY)
        bd.line([(112, 197), (178, 197)], fill=YEL, width=8)
        s = "Tim SATU amplop atau MASING-MASING?"
        text_c(bd, (400, 66), s, fit("pb", 48, s, 740), NAVY)
        text_c(bd, (400, 140), "Komen satu kata!", F("pb", 56), NAVY)
        B.info["nw"] = 800
        paste_c(img, B, W / 2, 940, p, tag="bubble komen")
    draw_aru(img, W / 2, 1440, 300, t)
    s = "*contoh hitungan ilustrasi, bukan saran keuangan"
    f = fit("pm", 28, s, MAXW)
    track("catatan", f.getlength(s), W / 2 - f.getlength(s) / 2, W / 2 + f.getlength(s) / 2)
    ImageDraw.Draw(img).text((W / 2, 1490), s, font=f, fill=GREY_T, anchor="mm")


SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10, scene11,
          scene12, scene13, scene14, scene15, scene16, scene17, scene18, scene19, scene20]
assert len(SCENES) == NS


@lru_cache(None)
def header():
    L = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F("pb", 34); s1 = "MANA LEBIH HEMAT?"; s2 = "#14"
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


@lru_cache(None)
def share_layer():
    T, td = card(780, 170, fill=TEAL)
    f = F("pb", 38)
    td.text((390, 52), "Kirim ke teman yang", font=f, fill=WHITE, anchor="mm")
    l2 = "minggu ini dapat 3 undangan"
    e = emoji_img("📤", 56); tw = f.getlength(l2)
    x0 = (780 - tw - 70) / 2
    td.text((x0, 118), l2, font=f, fill=YEL, anchor="lm")
    T.alpha_composite(e, (int(x0 + tw + 14), int(118 - e.height / 2)))
    return T


def share_card(img, t):
    """ajakan kirim tepat di angka puncak Rp360.000 (teks layar)."""
    if not (SHARE[0] <= t < SHARE[1]): return
    a = min(clamp((t - SHARE[0]) / 0.2), clamp((SHARE[1] - t) / 0.2))
    s = 0.85 + 0.15 * back((t - SHARE[0]) / 0.35)
    paste_c(img, share_layer(), W / 2, 1390 + 4 * math.sin(t * 5), s, 0, a, tag="kartu kirim")


FOLLOW_S = ("Follow, besok: rice cooker,", "mode warm-nya makan listrik berapa?")


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
    img = (bg_scene0(t >= 1.4) if k == 0 else bg_rest()).copy()
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
        if t >= CT0:                       # sumber kecil untuk counter Rp100.000
            a = clamp((t - CT0) / 0.3)
            L = Image.new("RGBA", (W, 60), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
            f = fit("pm", 28, SRC0, MAXW)
            ld.text((W / 2, 30), SRC0, font=f, fill=INK, anchor="mm")
            track("catatan", f.getlength(SRC0), W / 2 - f.getlength(SRC0) / 2, W / 2 + f.getlength(SRC0) / 2)
            paste_c(img, L, W / 2, 1712, 1, 0, a)
    share_card(img, t)
    draw_sub(img, t)
    if k > 0 and k in NOTES:
        note_lines(img, NOTES[k])
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
    ev.append({"t": 1.5, "sfx": "cring", "gain": 0.4})          # "cring!" + meja tamu
    ev.append({"t": CT1, "sfx": "ding", "gain": 0.25})          # counter berhenti Rp100.000
    for si in (3, 5, 13, 15, 24, 26, 28, 31, 35, 37):
        ev.append({"t": sg(si), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    for k, ((a, b), v) in CNT.items():
        ev.append({"t": b, "sfx": "ding", "gain": 0.28})
    ev.append({"t": SC[8] + 0.6, "sfx": "cring", "gain": 0.4})    # Si Bocor menggigit sisi pengantin
    ev.append({"t": SHARE[0] + 0.1, "sfx": "klik", "gain": 0.3})
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
            print("counter adegan", k, rp(v), "mulai", round(a, 2), "berhenti", round(b, 2), "tahan sampai", round(SC[k + 1], 2),
                  "=", round(SC[k + 1] - b, 2), "dtk")
        print("share", [round(x, 2) for x in SHARE], "follow", [round(x, 2) for x in FOLLOW])
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

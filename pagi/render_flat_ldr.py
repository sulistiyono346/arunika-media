"""Renderer ARN-56 "Mana Lebih Hemat? #13 — LDR vs satu kota" — Flat 2D latar terang (PRB-31).
Salinan render_flat_umr.py (helper kartu, koin, Si Bocor, pill, bubble, stempel, timbangan, subtitle, cek area aman, sfx) dengan:
- frame 0 (PRB-36, tanpa kartu judul besar): tiket kereta raksasa dipeluk Aru, Si Bocor menggigit ujungnya, koin jatuh
  ("cring!"). Counter besar Rp0 naik dan BERHENTI di Rp1.300.000 dtk 2,0 + sumber kecil. Visual berganti ~dtk 1,5:
  tiket terbelah, kiri dua orang di satu motor, kanan dua HP video call. Judul layar = pill kecil "LDR vs sekota, MAHAL mana?".
  Tanpa label seri/logo/progress bar dtk 0-3.
- 21 adegan (tiap <= 6 dtk); SETIAP angka utama (harga & hasil hitungan Rp920 rb, Rp1,3 jt, Rp848 rb, Rp720 rb) punya
  teks sumber kecil di bawahnya (pelajaran QA #12); ajakan kirim "Kirim ke pasanganmu 📤" di puncak timbangan
  (Rp1.300.000 vs Rp920.000); layar terbelah tim LDR vs tim SATU KOTA; timbangan berbalik dua kali; penutup tim vs tim.
- area aman (PRB-41): semua pill/bubble/kartu <= 800 px dan di x 130..950; `check` memindai tiap 0,1 dtk.
Pemakaian (dari folder kerja pagi/build_ldr, setelah align_ldr.py -> timing.json):
  TOTAL=66.5 python3 ../render_flat_ldr.py events | check | scenes | stills 0,2,... | video out.mp4 A B
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import (F, clamp, eio, rp, NAVY, TEAL, YEL, WHITE, GREY_T, RED, SAFE_X)

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "66.5"))
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


SCENE_SEG = [0, 2, 4, 5, 7, 9, 11, 12, 14, 15, 17, 18, 20, 23, 25, 26, 29, 31, 32, 34, 37]
SC = [0.0] + [sg(i) - 0.25 for i in SCENE_SEG[1:]] + [TOTAL]
NS = len(SCENE_SEG)
FOLLOW = (10.6, 15.0)          # PRB-4: ajakan follow teks kecil dtk 10-15
PB_START = 3.5                 # progress bar mulai dtk 3,5
TOT_LDR, TOT_KOTA, LDR2, KOTA2 = 1300000, 920000, 848000, 720000
CT0, CT1 = 0.45, 2.0           # counter frame 0: naik lalu BERHENTI di Rp1.300.000 dtk 2,0
SRC0 = "*contoh hitungan LDR sebulan · tarif KAI, OYO, XXI, HokBen"
NOTES = {4: ("tiket XXI Rp45–70 rb · detikcom, 11 Apr 2026",),
         5: ("paket berdua HokBen Rp100 rb · Kontan, 27 Jul 2026",),
         6: ("Pertalite Rp10.000/L · iNews, 11 Nov 2026 · 3 liter = asumsi",),
         7: ("*contoh hitungan dari tarif XXI, HokBen, Pertamina",),
         9: ("KA Gajahwong ekonomi premium Rp300–370 rb", "Dealls, 9 Feb 2026"),
         10: ("OYO Jogja kamar AC Rp100–160 rb/malam", "oyorooms.com, dicek 16 Nov 2026"),
         11: ("*contoh hitungan dari tarif XXI & HokBen",),
         12: ("*contoh hitungan dari tarif KAI, OYO, XXI, HokBen, Pertamina",),
         14: ("kereta ekonomi Jakarta–Yogyakarta mulai Rp74 rb", "Metro TV (tiket.com), 30 Mei 2026"),
         15: ("*contoh hitungan: Rp148 rb + Rp300 rb + Rp400 rb", "dari tarif KAI, OYO, XXI, HokBen"),
         17: ("*contoh hitungan: Rp920 rb − 2 × Rp100 rb", "dari tarif XXI, HokBen, Pertamina")}


def land(k, numseg, v):
    """counter adegan k: mulai SC[k]+0,35, berhenti paling lambat 1,6 dtk sebelum adegan berakhir."""
    return (SC[k] + 0.35, min(sg(numseg) - 0.1, SC[k + 1] - 1.6)), v


def quick(k, a, b, v): return (SC[k] + a, SC[k] + b), v


CNT = {4: quick(4, 0.15, 0.6, 100000), 5: quick(5, 0.15, 0.6, 100000), 6: quick(6, 0.15, 0.6, 30000),
       7: land(7, 13, TOT_KOTA), 9: land(9, 16, 600000), 10: quick(10, 0.3, 0.9, 300000),
       11: quick(11, 0.3, 0.9, 400000), 14: quick(14, 0.5, 1.3, 148000), 15: quick(15, 0.6, 1.4, LDR2),
       17: quick(17, 0.1, 0.6, KOTA2)}
SHARE = (SC[12] + 0.5, SC[13] - 0.05)         # ajakan kirim di puncak timbangan
GOLD, GOLD_D = (255, 194, 60), (217, 154, 31)
BL, BL_D, BL_L = (52, 120, 206), (34, 86, 160), (120, 176, 236)
PINK = (232, 92, 140)


def cval(k, t):
    (a, b), v = CNT[k]
    if t < a: return 0, False
    if t >= b: return v, True
    u = eio((t - a) / (b - a))
    step = 50000 if v >= 1000000 else 10000
    return int(round(v * u / step) * step), False


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


# ---------- gambar ----------
@lru_cache(None)
def bg_rest():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((90, 480, 990, 1380), fill=(250, 240, 214))
    d.rectangle((0, 1490, W, H), fill=(224, 228, 236))
    return img


@lru_cache(None)
def bg_scene0():
    img = base_bg().copy(); d = ImageDraw.Draw(img)
    d.ellipse((120, 640, 960, 1480), fill=(252, 236, 196))
    d.rectangle((0, FLOOR0, W, H), fill=(218, 223, 232)); d.line([(0, FLOOR0), (W, FLOOR0)], fill=NAVY, width=5)
    return img


@lru_cache(None)
def ticket_full(w, h, split):
    """tiket kereta raksasa (kertas krem, takik kiri-kanan). split=True: tanpa teks, kiri motor berdua, kanan dua HP."""
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 12, w + 10, h + 12), 34, fill=(20, 33, 91, 45))
    d.rounded_rectangle((0, 0, w, h), 34, fill=(255, 250, 236), outline=NAVY, width=6)
    for cx in (0, w):
        d.ellipse((cx - 34, h / 2 - 34, cx + 34, h / 2 + 34), fill=(0, 0, 0, 0))
        d.arc((cx - 34, h / 2 - 34, cx + 34, h / 2 + 34), 270 if cx == 0 else 90, 90 if cx == 0 else 270, fill=NAVY, width=6)
    if not split:
        d.rounded_rectangle((0, 0, w, 110), 34, fill=TEAL); d.rectangle((0, 60, w, 110), fill=TEAL)
        d.rounded_rectangle((0, 0, w, h), 34, outline=NAVY, width=6)
        text_c(d, (w / 2, 56), "TIKET KERETA", F("pb", 58), WHITE)
        tr = emoji_img("🚆", 150)
        im.alpha_composite(tr, (int(w * 0.64 - tr.width / 2), 140))
        text_c(d, (w * 0.64, 340), "JAKARTA", F("pb", 54), NAVY)
        text_c(d, (w * 0.64, 400), "– JOGJA", F("pb", 54), NAVY)
        dashed(d, [(w * 0.36, 448), (w - 50, 448)], (170, 178, 195), w=4)
        text_c(d, (w * 0.64, 492), "PP · sebulan sekali", F("pm", 34), GREY_T)
    else:
        mo = emoji_img("🛵", 190); co = emoji_img("💑", 130)
        im.alpha_composite(co, (int(w * 0.26 - co.width / 2), int(h * 0.30 - co.height / 2)))
        im.alpha_composite(mo, (int(w * 0.26 - mo.width / 2), int(h * 0.62 - mo.height / 2)))
        ph = emoji_img("📱", 150); hr = emoji_img("💗", 70)
        im.alpha_composite(ph, (int(w * 0.64 - ph.width / 2), int(h * 0.50 - ph.height / 2)))
        im.alpha_composite(ph, (int(w * 0.86 - ph.width / 2), int(h * 0.50 - ph.height / 2)))
        im.alpha_composite(hr, (int(w * 0.75 - hr.width / 2), int(h * 0.24 - hr.height / 2)))
    im.info["nw"] = w
    return im


def half_img(im, side):
    """belah gambar di tengah dengan tepi sobekan bergerigi; side 0 = kiri, 1 = kanan."""
    w_, h_ = im.size; mid = w_ // 2 + 4
    pts = [(mid + (24 if (k % 2) else -24), y) for k, y in enumerate(range(0, h_ + 50, 50))]
    poly = ([(0, 0)] + pts + [(0, h_)]) if side == 0 else ([(w_, 0)] + pts + [(w_, h_)])
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).polygon(poly, fill=255)
    out = im.copy(); out.putalpha(ImageChops.multiply(im.getchannel("A"), m))
    ImageDraw.Draw(out).line(pts, fill=NAVY, width=5)
    out.info["nw"] = im.info.get("nw", w_)
    return out


@lru_cache(None)
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


def title_pill(img):
    """judul layar = pill kecil (bukan kartu judul besar, PRB-36): 'LDR vs sekota, MAHAL mana?' (MAHAL kuning)."""
    a, b, c = "LDR vs sekota, ", "MAHAL", " mana?"
    size = 44
    while True:
        f = F("pb", size)
        wa, wb, wc = f.getlength(a), f.getlength(b), f.getlength(c)
        w = int(wa + wb + wc + 24 + 60)
        if w <= 780: break
        size -= 2
    h = 84
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
    if t >= CT1: return rp(TOT_LDR), True
    u = eio((t - CT0) / (CT1 - CT0))
    v = TOT_LDR * u + ((137 * int(t * 30)) % 900) * 1000 * u * (1 - u)
    return rp(int(round(v / 50000.0) * 50000)), False


def counter_card(img, t, cy, s, done, hot, scale=1.0, t0=CT0):
    L, d = card(780, 200, fill=(255, 232, 232) if hot else WHITE, outline=RED if hot else NAVY, ow=7)
    text_c(d, (350 if hot else 390, 102), s, fit("pb", 112, s, 620), NAVY)
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


def hand(d, x, y, r=26):
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 211, 176), outline=NAVY, width=6)


def scene0(img, t):
    """frame 0: tiket kereta raksasa dipeluk Aru, Si Bocor menggigit ujungnya, koin jatuh; counter naik & berhenti Rp1.300.000."""
    title_pill(img)
    s, done = counter0(t)
    hot = t >= CT0
    sc = 1.0 + (0.06 * back((t - CT1) / 0.3) - 0.06 * clamp((t - CT1 - 0.3) / 0.3) if t >= CT1 else 0)
    counter_card(img, t, 560, s, done, hot, sc)
    sp = eio((t - 1.3) / 0.4)                                   # visual berganti ~dtk 1,5: tiket terbelah
    cx, cy = 540, 1010
    if sp <= 0:
        paste_c(img, ticket_full(660, 540, False), cx, cy + 4 * math.sin(t * 3), 1.0, 1.5 * math.sin(t * 2))
    else:
        base = ticket_full(660, 540, True)
        paste_c(img, half_img(base, 0), cx - 64 * sp, cy + 12 * sp, 1.0, 6 * sp)
        paste_c(img, half_img(base, 1), cx + 64 * sp, cy + 12 * sp, 1.0, -6 * sp)
    chew = abs(math.sin(t * 11)) * 8
    bx, by = 820 + 25 * sp, 745 - chew
    d = ImageDraw.Draw(img)
    if sp <= 0:
        d.polygon([(800, 742), (870, 742), (870, 806)], fill=(246, 242, 232), outline=NAVY)    # ujung tiket tergigit
    paste_c(img, bocor_img(), bx, by, 0.55, 14 + 6 * math.sin(t * 11), tag="bocor")
    draw_aru(img, 300, FLOOR0, 430, t)
    hand(d, 215 - 20 * sp, 1180); hand(d, 400 + 20 * sp, 1180)
    falling_coins(img, t, 860, 800, FLOOR0 - 20, 0.3, n=5, spread=130)
    if t >= 1.5:
        falling_coins(img, t, 700, 1000, FLOOR0 - 20, 1.5, n=4, spread=120)
    p = pop(t, 1.5)
    if p > 0:
        paste_c(img, bubble("cring!", col=YEL, fg=NAVY, size=48, tail="right"), 770, 1290, p, 6, tag="bubble cring")


def scene1(img, t):
    """coba tebak, mana lebih mahal sebulan: dua dompet bersisian (LDR | SATU KOTA) dengan tanda ?."""
    for k, (x, lab, col, t0) in enumerate(((320, "LDR", BL, SC[1] + 0.05), (760, "SATU KOTA", TEAL, SC[1] + 0.2))):
        p = pop(t, t0)
        if p <= 0: continue
        paste_c(img, wallet_img(300), x, 900 + 6 * math.sin(t * 3 + k), p, 3 * math.sin(t * 2 + k))
        paste_c(img, pill(lab, fill=col, fg=WHITE, size=44), x, 1060, p, tag="pill " + lab)
    for k, (x, t0) in enumerate(((320, sg(3) - 0.05), (760, sg(3) + 0.15))):
        q = pop(t, t0)
        if q <= 0: continue
        L = Image.new("RGBA", (160, 160), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.ellipse((6, 6, 154, 154), fill=YEL, outline=NAVY, width=7)
        text_c(ld, (80, 78), "?", F("pb", 90), NAVY)
        L.info["nw"] = 160
        paste_c(img, L, x, 700, q, 8 * math.sin(t * 4 + k), tag="lencana ?")
    q = pop(t, SC[1] + 0.3)
    if q > 0:
        L = Image.new("RGBA", (110, 110), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.ellipse((4, 4, 106, 106), fill=YEL, outline=NAVY, width=6)
        text_c(ld, (55, 54), "vs", F("pb", 42), NAVY)
        paste_c(img, L, W / 2, 900, q)
    draw_aru(img, W / 2, 1480, 290, t)


def scene2(img, t):
    """kamu pasti kenal: teman berlari bawa ransel di peron Stasiun Pasar Senen, jam 'Jumat 19.30' (hangat)."""
    p = pop(t, SC[2] + 0.05)
    if p > 0:
        paste_c(img, pill_emoji("Kamu pasti kenal", "👀", fill=YEL, fg=NAVY, size=48), W / 2, 470, p, -2,
                tag="pill kenal")
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1250, W, 1290), fill=(200, 206, 218)); d.line([(0, 1250), (W, 1250)], fill=NAVY, width=5)
    for x in range(0, W, 120):
        d.rectangle((x, 1250, x + 60, 1262), fill=YEL)                         # garis kuning peron
    q = pop(t, SC[2] + 0.15)
    if q > 0:
        paste_c(img, pill("STASIUN PASAR SENEN", fill=NAVY, fg=WHITE, size=42), W / 2, 610, q, tag="papan stasiun")
    r = pop(t, SC[2] + 0.35)
    if r > 0:
        C, cd = card(330, 150, fill=WHITE, outline=NAVY, ow=6, r=26)
        cd.ellipse((24, 30, 114, 120), fill=(255, 246, 226), outline=NAVY, width=5)
        cd.line([(69, 75), (69, 44)], fill=NAVY, width=6); cd.line([(69, 75), (94, 92)], fill=NAVY, width=6)
        text_c(cd, (222, 54), "Jumat", F("pb", 40), NAVY)
        text_c(cd, (222, 104), "19.30", F("pb", 48), RED)
        paste_c(img, C, 760, 790, r, 2 * math.sin(t * 3), tag="jam")
    u = eout((t - SC[2] - 0.05) / 0.6)
    paste_c(img, emoji_img("🚆", 300), 330 - 200 * (1 - u), 1090, clamp(u * 2))
    run = clamp((t - sg(4) - 1.2) / 3.0)
    rx = 880 - 230 * run
    paste_c(img, emoji_img("🏃", 250), rx, 1110 - abs(math.sin(t * 9)) * 18, pop(t, sg(4) + 1.4), 4 * math.sin(t * 9))
    paste_c(img, emoji_img("🎒", 110), rx + 70, 1060 - abs(math.sin(t * 9)) * 18, pop(t, sg(4) + 1.6), 8 * math.sin(t * 9))


def calendar(w, h, mode, t, times=(), title="NOVEMBER"):
    """kalender bulan (Senin pertama, 1 Nov = Minggu). mode: 'sabtu' (4 Sabtu menyala bergiliran),
    'satu' (tanggal 21 dilingkari), 'nonton' (🍿 di 4 Sabtu, 2 dicoret)."""
    L, d = head_card(w, h, title, col=TEAL if mode != "satu" else BL, size=46)
    days = ["Sn", "Sl", "Rb", "Km", "Jm", "Sb", "Mg"]
    x0, cw = 30, (w - 60) / 7
    y0 = 150; ch = (h - y0 - 24) / 6
    for j, s in enumerate(days):
        text_c(d, (x0 + cw * (j + 0.5), 124), s, F("pb", 30), RED if j == 5 else GREY_T)
    sat = [7, 14, 21, 28]
    for n in range(1, 31):
        idx = n + 5                       # 1 Nov di kolom Minggu (indeks 6)
        r_, c_ = idx // 7, idx % 7
        cx, cy = x0 + cw * (c_ + 0.5), y0 + ch * (r_ + 0.5)
        lit = False
        if mode == "sabtu" and n in sat:
            k = sat.index(n); lit = k < len(times) and t >= times[k]
        if mode == "nonton" and n in sat:
            lit = True
        if lit:
            d.rounded_rectangle((cx - cw / 2 + 5, cy - ch / 2 + 4, cx + cw / 2 - 5, cy + ch / 2 - 4), 14,
                                fill=(255, 226, 140), outline=GOLD_D, width=4)
        if mode == "nonton" and n in sat:
            e = emoji_img("🍿", int(ch * 0.62))
            L.alpha_composite(e, (int(cx - e.width / 2), int(cy - e.height / 2)))
            k = sat.index(n)
            if k in (1, 3):
                tt = times[0] if k == 1 else times[1]
                a = clamp((t - tt) / 0.25)
                if a > 0:
                    s_ = ch * 0.38 * a
                    d.line([(cx - s_, cy - s_), (cx + s_, cy + s_)], fill=RED, width=9)
                    d.line([(cx - s_, cy + s_), (cx + s_, cy - s_)], fill=RED, width=9)
            continue
        text_c(d, (cx, cy), str(n), F("pb", 34), NAVY if lit or c_ != 5 else RED)
        if mode == "satu" and n == 21:
            a = clamp((t - times[0]) / 0.3) if times else 1
            if a > 0:
                d.arc((cx - 40, cy - 34, cx + 40, cy + 34), -90, -90 + 360 * a, fill=RED, width=7)
    return L


def scene3(img, t):
    """satu kota dulu: kalender dengan 4 Sabtu menyala bergiliran."""
    paste_c(img, pill("SATU KOTA", fill=TEAL, fg=WHITE, size=54), W / 2, 470, pop(t, SC[3] + 0.05), -2, tag="pill satu kota")
    t0 = sg(6) + 0.3
    times = [t0 + 0.22 * j for j in range(4)]
    paste_c(img, calendar(780, 640, "sabtu", t, times), W / 2, 920, pop(t, SC[3] + 0.15), -1, tag="kalender")


def item_scene(img, t, k, title, sub, col, extra, icon, ytop=860):
    paste_c(img, icon, W / 2, 500, pop(t, SC[k] + 0.05), 6 * math.sin(t * 3))
    v, done = cval(k, t)
    T = big_card_counter(title, sub, rp(v), col, done, extra)
    paste_c(img, T, W / 2, ytop, pop(t, SC[k] + 0.1) * (1 + 0.02 * math.sin(t * 8)), -1.2)
    track("kartu " + title, 800, W / 2 - 400, W / 2 + 400)


def scene4(img, t):
    item_scene(img, t, 4, "NONTON BERDUA", "Rp50.000 × 2 tiket", TEAL, "per kencan", emoji_img("🍿", 170))


def scene5(img, t):
    item_scene(img, t, 5, "MAKAN BERDUA", "paket berdua", TEAL, "per kencan", emoji_img("🍱", 170))


def scene6(img, t):
    item_scene(img, t, 6, "BENSIN", "3 L × Rp10.000", TEAL, "per kencan", emoji_img("⛽", 170))


def scene7(img, t):
    item_scene(img, t, 7, "SATU KOTA SEBULAN", "Rp230.000 × 4 Sabtu", GREEN, "per bulan", emoji_img("🛵", 170))


def scene8(img, t):
    """LDR Jakarta-Jogja: peta kecil, garis rel bergerak, kereta jalan; kalender 1 tanggal dilingkari."""
    paste_c(img, pill("LDR Jakarta–Jogja", fill=BL, fg=WHITE, size=50), W / 2, 470, pop(t, SC[8] + 0.05), -2, tag="pill ldr")
    q = pop(t, SC[8] + 0.15)
    if q > 0:
        M, md = card(800, 520, fill=(236, 244, 236), outline=NAVY, ow=7)
        md.polygon([(40, 300), (200, 250), (380, 280), (560, 330), (760, 360), (760, 500), (40, 500)], fill=(222, 234, 214))
        A, B = (150, 150), (650, 390)
        dashed(md, [A, (400, 230), B], NAVY, w=10, on=22, off=14, phase=t * 60)
        for (x, y), lab, col in ((A, "Jakarta", BL), (B, "Jogja", TEAL)):
            md.ellipse((x - 26, y - 26, x + 26, y + 26), fill=col, outline=NAVY, width=6)
        text_c(md, (150, 80), "Jakarta", F("pb", 46), BL)
        text_c(md, (620, 460), "Jogja", F("pb", 46), TEAL)
        u = ((t - SC[8]) / 3.0) % 1.0
        px = A[0] + (400 - A[0]) * u * 2 if u < 0.5 else 400 + (B[0] - 400) * (u - 0.5) * 2
        py = A[1] + (230 - A[1]) * u * 2 if u < 0.5 else 230 + (B[1] - 230) * (u - 0.5) * 2
        e = emoji_img("🚆", 90)
        M.alpha_composite(e, (int(px - e.width / 2), int(py - e.height / 2 - 40)))
        paste_c(img, M, W / 2, 850, q, -1, tag="peta")
    r = pop(t, sg(14) + 2.2)
    if r > 0:
        C, cd = card(520, 190, fill=WHITE, outline=BL, ow=6, r=26)
        cd.ellipse((30, 40, 140, 150), fill=(255, 246, 226), outline=NAVY, width=5)
        text_c(cd, (85, 97), "21", F("pb", 46), NAVY)
        cd.arc((22, 32, 148, 158), 0, 360, fill=RED, width=7)
        text_c(cd, (330, 70), "ketemu", F("pm", 40), GREY_T)
        text_c(cd, (330, 130), "sebulan sekali", F("pb", 44), BL)
        paste_c(img, C, W / 2, 1270, r, 1, tag="kartu sebulan")


def scene9(img, t):
    item_scene(img, t, 9, "KERETA PULANG PERGI", "Rp300.000 × 2 · ekonomi premium", BL, "1 orang, PP", emoji_img("🚆", 170))


def scene10(img, t):
    item_scene(img, t, 10, "PENGINAPAN JOGJA", "Rp150.000 × 2 malam", BL, "kamar AC", emoji_img("🏨", 170))


def scene11(img, t):
    item_scene(img, t, 11, "2 KENCAN DI SANA", "2 × Rp200.000 (nonton + makan)", BL, "tanpa bensin", emoji_img("🍿", 170))


def scene12(img, t):
    """PUNCAK: timbangan Rp1.300.000 vs Rp920.000 (LDR turun), Si Bocor di dompet LDR, setahun + ajakan kirim."""
    paste_c(img, pill("Rp1.300.000 vs Rp920.000", fill=NAVY, fg=WHITE, size=48), W / 2, 470, pop(t, SC[12] + 0.05), -2,
            tag="pill puncak")
    tilt = 1.0 * eout((t - SC[12] - 0.2) / 0.6)
    paste_c(img, scale_img(round(tilt, 2), "Rp1,3 jt", "Rp920 rb", BL, GREEN), W / 2, 860, pop(t, SC[12] + 0.1), tag="timbangan")
    d = ImageDraw.Draw(img)
    text_c(d, (W / 2 - 250, 1175), "LDR", F("pb", 44), BL)
    text_c(d, (W / 2 + 270, 1175), "SATU KOTA", F("pb", 42), GREEN)
    q = pop(t, SC[12] + 0.5)
    if q > 0:
        paste_c(img, bocor_img(), 200, 1010 + 6 * math.sin(t * 8), 0.42 * q, 10 * math.sin(t * 6), tag="bocor")
        falling_coins(img, t, 175, 1060, 1440, SC[12] + 0.7, n=3, spread=30)
    r = pop(t, sg(21) - 0.1)
    if r > 0:
        s = "setahun: Rp15,6 jt vs Rp11 jt"
        paste_c(img, pill(s, fill=WHITE, fg=NAVY, size=38, outline=BL), W / 2, 1245, r, tag="pill setahun")


COLS = [(140, 530, BL, "LDR"), (550, 940, TEAL, "SATU KOTA")]
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
    """layar terbelah tim LDR vs tim SATU KOTA (warna netral): 'Tunggu, tim LDR menjawab.'"""
    cols(img, 0)
    paste_c(img, emoji_img("🚆", 240), 335, 1060, pop(t, SC[13] + 0.05))
    paste_c(img, emoji_img("🛵", 240), 745, 1060, pop(t, SC[13] + 0.1))
    q = pop(t, sg(23) - 0.05)
    if q > 0:
        paste_c(img, bubble("Tunggu!", col=BL, fg=WHITE, size=56, tail="left"), 335, 830, q * (1 + 0.03 * math.sin(t * 9)), -3,
                tag="bubble tunggu")


def scene14(img, t):
    item_scene(img, t, 14, "KERETA EKONOMI PP", "Rp74.000 × 2 · pesan jauh hari", BL, "bukan premium", emoji_img("🎫", 170))


def mini_scale(img, t, t0, a, b, la, ra, cy=1175):
    """timbangan kecil berbalik dari tilt a ke b, label LDR kiri | SATU KOTA kanan."""
    u = eout((t - t0) / 0.6)
    tilt = a + (b - a) * u
    paste_c(img, scale_img(round(tilt, 2), la, ra, BL, GREEN), W / 2, cy, 0.8, tag="timbangan kecil")
    d = ImageDraw.Draw(img)
    text_c(d, (W / 2 - 240, cy + 268), "LDR", F("pb", 38), BL)
    text_c(d, (W / 2 + 240, cy + 268), "SATU KOTA", F("pb", 38), GREEN)


def scene15(img, t):
    """bantahan LDR: total baru Rp848.000 < Rp920.000, timbangan berbalik."""
    p = pop(t, SC[15] + 0.05)
    v, done = cval(15, t)
    T = big_card_counter("TOTAL LDR BARU", "Rp148 rb + Rp300 rb + Rp400 rb", rp(v), BL, done, "lebih murah dari Rp920.000")
    paste_c(img, T, W / 2, 690, p * (1 + 0.02 * math.sin(t * 8)), -1.2)
    track("kartu ldr baru", 800, W / 2 - 400, W / 2 + 400)
    (a, b), _ = CNT[15]
    mini_scale(img, t, b - 0.2, 1.0, -0.8, "Rp848 rb", "Rp920 rb")


def scene16(img, t):
    """tim satu kota balas: nonton cukup dua minggu sekali (2 dari 4 bioskop dicoret)."""
    paste_c(img, pill("Tim SATU KOTA balas", fill=TEAL, fg=WHITE, size=50), W / 2, 470, pop(t, SC[16] + 0.05), -2,
            tag="pill balas")
    t0 = sg(30) + 0.5
    paste_c(img, calendar(780, 640, "nonton", t, (t0, t0 + 0.35)), W / 2, 920, pop(t, SC[16] + 0.15), 1, tag="kalender")


def scene17(img, t):
    """satu kota tinggal Rp720.000 < Rp848.000, timbangan berbalik lagi."""
    p = pop(t, SC[17] + 0.03)
    v, done = cval(17, t)
    T = big_card_counter("SATU KOTA BARU", "Rp920 rb − 2 × Rp100 rb", rp(v), GREEN, done, "lebih murah dari Rp848.000")
    paste_c(img, T, W / 2, 690, p * (1 + 0.02 * math.sin(t * 8)), 1.2)
    track("kartu kota baru", 800, W / 2 - 400, W / 2 + 400)
    (a, b), _ = CNT[17]
    mini_scale(img, t, b - 0.2, -0.8, 0.8, "Rp848 rb", "Rp720 rb")


def scene18(img, t):
    """penentunya bukan jarak, tapi seberapa sering ketemu (+ cara pesan): dua pos menyala kuning, jarak meredup."""
    dim = clamp((t - sg(32) - 0.6) / 0.6)
    S, sd = card(560, 220, fill=WHITE, outline=NAVY, ow=6)
    e = emoji_img("📍", 110)
    S.alpha_composite(e, (40, int(110 - e.height / 2)))
    text_c(sd, (330, 80), "JARAK", F("pb", 70), NAVY)
    text_c(sd, (330, 160), "Jakarta–Jogja", F("pm", 40), GREY_T)
    paste_c(img, S, W / 2, 640, pop(t, SC[18] + 0.05), 0, 1.0 - 0.65 * dim, tag="kartu jarak")
    if dim > 0.3:
        text_c(ImageDraw.Draw(img), (W / 2, 790), "bukan ini", F("pb", 44), GREY_T)
    for j, (x, em, l1, l2, t0) in enumerate(((330, "💞", "SERING", "KETEMU", sg(33) + 0.75),
                                              (750, "🎫", "CARA", "PESAN", sg(33) + 1.2))):
        lit = t >= t0
        q = pop(t, SC[18] + 0.2 + 0.1 * j)
        C, cd = card(380, 380, fill=(255, 236, 160) if lit else WHITE, outline=GOLD_D if lit else NAVY, ow=9 if lit else 6)
        ee = emoji_img(em, 130)
        C.alpha_composite(ee, (int(190 - ee.width / 2), 34))
        text_c(cd, (190, 232), l1, F("pb", 62), NAVY)
        text_c(cd, (190, 306), l2, F("pb", 62), NAVY)
        sc = q * (1.0 + (0.06 * math.sin((t - t0) * 9) if lit and t - t0 < 0.5 else 0))
        paste_c(img, C, x, 1090, sc, 0, tag="pos " + l1)


def scene19(img, t):
    """biar adil: Aru memegang dua kantong, kiri 'yang berangkat -> tiket', kanan 'yang ditunggu -> kencan'."""
    paste_c(img, pill("Patungan adil", fill=YEL, fg=NAVY, size=50), W / 2, 470, pop(t, SC[19] + 0.05), -2, tag="pill adil")
    for j, (x, em, l1, l2, col, t0) in enumerate(((330, "🎫", "yang berangkat", "tiket", BL, sg(35) - 0.05),
                                                   (750, "🍿", "yang ditunggu", "kencan", TEAL, sg(36) - 0.05))):
        q = pop(t, t0)
        if q <= 0: continue
        C, cd = card(380, 400, fill=WHITE, outline=col, ow=7)
        cd.ellipse((110, 24, 270, 184), fill=(255, 236, 160), outline=GOLD_D, width=6)    # kantong
        ee = emoji_img(em, 100)
        C.alpha_composite(ee, (int(190 - ee.width / 2), int(104 - ee.height / 2)))
        text_c(cd, (190, 250), l1, fit("pm", 42, l1, 340), GREY_T)
        f2 = fit("pb", 60, l2, 250); tw = f2.getlength(l2); xa = 190 - (tw + 66) / 2
        arrow(cd, xa, 332, xa + 52, 332, col, w=10, head=24)
        cd.text((xa + 66, 330), l2, font=f2, fill=col, anchor="lm")
        paste_c(img, C, x, 860 + 6 * math.sin(t * 4 + j), q, 2 * math.sin(t * 3 + j) - 2 + 4 * j, tag="kantong " + l2)
    draw_aru(img, W / 2, 1470, 330, t)


def scene20(img, t):
    """penutup: Tim LDR atau tim SATU KOTA? Komen!"""
    for k, (s, col, t0) in enumerate((("TIM LDR", BL, SC[20] + 0.05), ("TIM SATU KOTA", TEAL, sg(38)))):
        p = pop(t, t0)
        if p <= 0: continue
        beat = 1 + 0.04 * math.sin((t - t0) * 7 + k * math.pi)
        paste_c(img, pill(s, fill=col, fg=WHITE, size=54, h=116), W / 2, 520 if k == 0 else 720, p * beat,
                -2 if k == 0 else 2, tag=s)
    if t >= sg(38):
        text_c(ImageDraw.Draw(img), (W / 2, 620), "atau", F("pb", 40), NAVY)
    p = pop(t, sg(38) + 0.3)
    if p > 0:
        B = Image.new("RGBA", (800, 250), (0, 0, 0, 0)); bd = ImageDraw.Draw(B)
        bd.rounded_rectangle((0, 0, 800, 200), 34, fill=YEL, outline=NAVY, width=5)
        bd.polygon([(110, 196), (180, 196), (90, 246)], fill=YEL, outline=NAVY)
        bd.line([(112, 197), (178, 197)], fill=YEL, width=8)
        s = "Tim LDR atau tim SATU KOTA?"
        text_c(bd, (400, 66), s, fit("pb", 50, s, 740), NAVY)
        text_c(bd, (400, 140), "Komen!", F("pb", 60), NAVY)
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
    f = F("pb", 34); s1 = "MANA LEBIH HEMAT?"; s2 = "#13"
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
    """ajakan kirim di puncak timbangan (teks layar): 'Kirim ke pasanganmu 📤'."""
    if not (SHARE[0] <= t < SHARE[1]): return
    a = min(clamp((t - SHARE[0]) / 0.25), clamp((SHARE[1] - t) / 0.2))
    s = 0.85 + 0.15 * back((t - SHARE[0]) / 0.35)
    T, td = card(760, 130, fill=TEAL)
    e = emoji_img("📤", 70)
    txt = "Kirim ke pasanganmu"
    f = F("pb", 54); tw = f.getlength(txt)
    x0 = (760 - tw - 90) / 2
    td.text((x0, 66), txt, font=f, fill=WHITE, anchor="lm")
    T.alpha_composite(e, (int(x0 + tw + 20), int(66 - e.height / 2)))
    paste_c(img, T, W / 2, 1370 + 4 * math.sin(t * 5), s, 0, a, tag="kartu kirim")


FOLLOW_S = "Follow @kabar.arunika · hitung uang tiap pagi"


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
        if t >= CT0:                       # sumber kecil untuk counter Rp1.300.000
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
    ev.append({"t": 1.5, "sfx": "cring", "gain": 0.4})          # "cring!" + tiket terbelah
    ev.append({"t": CT1, "sfx": "ding", "gain": 0.25})          # counter berhenti Rp1.300.000
    for si in (1, 3, 8, 10, 16, 21, 22, 24, 27, 28, 30, 35, 36, 38):
        ev.append({"t": sg(si), "sfx": "pop", "gain": 0.26})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    for k, ((a, b), v) in CNT.items():
        ev.append({"t": b, "sfx": "ding", "gain": 0.28})
    ev.append({"t": SC[12] + 0.2, "sfx": "cring", "gain": 0.4})   # timbangan puncak
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
            print("counter adegan", k, rp(v), "mulai", round(a, 2), "berhenti", round(b, 2), "tahan sampai", round(SC[k + 1], 2),
                  "=", round(SC[k + 1] - b, 2), "dtk")
        print("share", [round(x, 2) for x in SHARE])
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

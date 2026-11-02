"""Renderer ARN-24 "Pertamax, kok telat naik?" — gaya B Polaroid doodle.
Pemakaian:
  python3 render.py events            -> events.json (sfx)
  python3 render.py stills t1,t2,...  -> still_<t>.png + sheet.png
  python3 render.py video out.mp4 A B -> frame A..B detik (tanpa audio)
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
LEAD = 0.3
TOTAL = float(os.environ.get("TOTAL", "25.9"))  # = durasi VO + LEAD + ±0,5 dtk
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
GF = "/usr/share/fonts/truetype/google-fonts/"

NAVY = (20, 33, 91); TEAL = (18, 194, 176); YEL = (255, 184, 0); WHITE = (255, 255, 255)
CREAM = (255, 246, 232); BROWN = (92, 64, 40); RED = (224, 82, 63); GREEN = (46, 160, 110)
GREY_T = (122, 114, 102); PHOTO = (233, 234, 230)


@lru_cache(None)
def F(name, size):
    if name == "pb": return ImageFont.truetype(GF + "Poppins-Bold.ttf", size)
    if name == "pm": return ImageFont.truetype(GF + "Poppins-Medium.ttf", size)
    if name == "lb":
        f = ImageFont.truetype(GF + "Lora-Variable.ttf", size); f.set_variation_by_name("Bold"); return f
    if name == "lbi":
        f = ImageFont.truetype(GF + "Lora-Italic-Variable.ttf", size); f.set_variation_by_name("Bold Italic"); return f
    if name == "cb": return ImageFont.truetype("/usr/share/fonts/X11/Type1/c0583bt_.pfb", size)
    raise KeyError(name)


TIM = json.load(open("timing.json"))
def cs(i): return TIM[i]["start"] + LEAD
def ce(i): return TIM[i]["end"] + LEAD

SC = [0.0, cs(5) - 0.25, cs(9) - 0.25, cs(13) - 0.25, cs(18) - 0.25, cs(23) - 0.25, TOTAL]
CAPTIONS = ["minyak dunia vs SPBU-mu", "harga BBM nonsubsidi: diubah tiap tgl 1",
            "patokan: tgl 25 s.d. 24 bulan lalu", "harga Nov = cermin minyak bulan lalu",
            "isi 30 liter sebulan", "Desember: naik atau turun?"]
JANJI_T = 2.0
FOLLOW = (10.6, 14.9)


def scene_of(t):
    for k in range(6):
        if t < SC[k + 1]: return k
    return 5


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def pop(t, t0, d=0.35): return 0.0 if t < t0 else back((t - t0) / d)


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


def paste_c(dst, im, cx, cy, scale=1.0, angle=0.0, alpha=1.0):
    """tempel im dengan pusat (cx,cy), skala & rotasi."""
    if scale <= 0.01 or alpha <= 0.01: return
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if abs(angle) > 0.05:
        im = im.rotate(angle, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    dst.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def draw_aru(layer, cx, bottom, h, t, angle_amp=2.0):
    im = aru_h(h)
    bob = 7 * math.sin(2 * math.pi * 1.1 * t)
    ang = angle_amp * math.sin(2 * math.pi * 0.7 * t)
    paste_c(layer, im, cx, bottom - h / 2 + bob, 1.0, ang)


def text_c(d, xy, s, font, fill, anchor="mm", **kw):
    d.text(xy, s, font=font, fill=fill, anchor=anchor, **kw)


# ---------- kartu ----------
def card(w, h, fill=CREAM, shadow=(214, 190, 160), r=26, outline=BROWN):
    im = Image.new("RGBA", (w + 14, h + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 12, w + 12, h + 12), r, fill=shadow)
    d.rounded_rectangle((0, 0, w, h), r, fill=fill, outline=outline, width=3)
    return im, d


def coin(r=26):
    im = Image.new("RGBA", (2 * r + 6, 2 * r + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((3, 3, 2 * r + 3, 2 * r + 3), fill=(255, 194, 60), outline=(217, 154, 31), width=4)
    text_c(d, (r + 3, r + 3), "Rp", F("pb", int(r * 0.75)), (154, 106, 16))
    return im


@lru_cache(None)
def bocor_img():
    im = Image.new("RGBA", (300, 270), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line([(60, 200), (30, 185), (12, 150), (22, 125)], fill=(244, 163, 184), width=7, joint="curve")
    d.polygon([(150, 70), (255, 88), (246, 238), (142, 228)], fill=(201, 162, 107), outline=NAVY)
    d.line([(150, 70), (255, 88), (246, 238), (142, 228), (150, 70)], fill=NAVY, width=5)
    text_c(d, (200, 150), "Rp", F("pb", 46), (122, 90, 46))
    d.ellipse((214, 196, 232, 214), fill=NAVY)
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


# ---------- ikon ----------
def icon_barrel(d, x, y, s=1.0):
    w, h = 120 * s, 150 * s
    d.rounded_rectangle((x, y, x + w, y + h), int(18 * s), fill=TEAL, outline=NAVY, width=5)
    for k in (0.25, 0.75):
        d.line([(x, y + h * k), (x + w, y + h * k)], fill=NAVY, width=5)
    d.ellipse((x + w * 0.38, y + h * 0.42, x + w * 0.62, y + h * 0.58), fill=NAVY)


def icon_drop(d, cx, cy, s=1.0):
    r = 45 * s
    d.polygon([(cx, cy - 2.1 * r), (cx - r * 0.95, cy - 0.2 * r), (cx + r * 0.95, cy - 0.2 * r)], fill=NAVY)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=NAVY)
    d.ellipse((cx - r * 0.45, cy - r * 0.4, cx - r * 0.15, cy - r * 0.05), fill=WHITE)


def icon_pump(d, x, y, s=1.0):
    d.rounded_rectangle((x, y, x + 110 * s, y + 170 * s), int(14 * s), fill=RED, outline=NAVY, width=5)
    d.rounded_rectangle((x + 18 * s, y + 20 * s, x + 92 * s, y + 70 * s), int(8 * s), fill=WHITE, outline=NAVY, width=4)
    d.line([(x + 110 * s, y + 60 * s), (x + 145 * s, y + 70 * s), (x + 145 * s, y + 150 * s)], fill=NAVY, width=7)
    d.rectangle((x + 136 * s, y + 140 * s, x + 158 * s, y + 175 * s), fill=NAVY)
    d.rectangle((x - 10 * s, y + 170 * s, x + 120 * s, y + 184 * s), fill=NAVY)


def icon_jerrycan(d, x, y, s=1.0):
    d.rounded_rectangle((x, y + 30 * s, x + 150 * s, y + 210 * s), int(20 * s), fill=RED, outline=NAVY, width=5)
    d.rounded_rectangle((x + 20 * s, y, x + 90 * s, y + 40 * s), int(10 * s), fill=RED, outline=NAVY, width=5)
    d.rectangle((x + 105 * s, y + 5 * s, x + 135 * s, y + 35 * s), fill=NAVY)
    d.line([(x + 30 * s, y + 80 * s), (x + 120 * s, y + 180 * s)], fill=(170, 50, 40), width=8)
    d.line([(x + 120 * s, y + 80 * s), (x + 30 * s, y + 180 * s)], fill=(170, 50, 40), width=8)


def arrow(d, x0, y0, x1, y1, col, w=16, head=34):
    ang = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 2: return
    hx, hy = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
    d.line([(x0, y0), (hx, hy)], fill=col, width=w)
    p = [(x1, y1), (hx + head * 0.6 * math.sin(ang), hy - head * 0.6 * math.cos(ang)),
         (hx - head * 0.6 * math.sin(ang), hy + head * 0.6 * math.cos(ang))]
    d.polygon(p, fill=col)


# ---------- isi foto per adegan (layer 860x760) ----------
PW, PH = 860, 760


@lru_cache(None)
def static_card(key):
    if key == "board":
        im, d = card(500, 220)
        text_c(d, (250, 52), "PERTAMAX di SPBU-mu", F("pm", 30), BROWN)
        text_c(d, (250, 125), "Rp15.950", F("pb", 78), NAVY)
        text_c(d, (250, 185), "per liter · 1 Nov 2026", F("pm", 24), GREY_T)
        return im
    if key == "janji":
        im = Image.new("RGBA", (560, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rectangle((10, 10, 560, 170), fill=(214, 190, 160)); d.rectangle((0, 0, 550, 160), fill=(255, 226, 120))
        f = F("lbi", 40)
        text_c(d, (275, 50), "Jawabannya ada di", f, NAVY)
        a, b = "kalender,", " bukan di kilang"
        wa, wb = f.getlength(a), f.getlength(b)
        x0 = 275 - (wa + wb) / 2
        d.rectangle((x0 - 8, 92, x0 + wa + 8, 142), fill=TEAL)
        d.text((x0, 117), a, font=f, fill=WHITE, anchor="lm")
        d.text((x0 + wa, 117), b, font=f, fill=NAVY, anchor="lm")
        return im
    if key == "q":
        im = Image.new("RGBA", (130, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse((5, 5, 125, 125), fill=YEL, outline=NAVY, width=5)
        text_c(d, (65, 62), "?", F("pb", 80), NAVY); return im
    if key == "tag1x":
        im, d = card(300, 100, fill=YEL, shadow=(214, 160, 20), outline=NAVY)
        text_c(d, (150, 50), "1× sebulan", F("pb", 44), NAVY); return im
    if key == "mops":
        im, d = card(380, 280)
        icon_barrel(d, 40, 70, 0.9)
        d.text((170, 95), "bensin", font=F("pb", 38), fill=NAVY, anchor="lm")
        d.text((170, 145), "Singapura", font=F("pb", 38), fill=NAVY, anchor="lm")
        d.text((170, 195), "(MOPS)", font=F("pm", 28), fill=GREY_T, anchor="lm")
        return im
    if key == "kurs":
        im, d = card(380, 280)
        text_c(d, (190, 80), "kurs dolar", F("pb", 38), NAVY)
        text_c(d, (95, 170), "$", F("pb", 80), GREEN)
        arrow(d, 140, 172, 230, 172, GREEN, w=12, head=28)
        text_c(d, (290, 170), "Rp", F("pb", 80), GREEN)
        return im
    if key == "hasil":
        im, d = card(520, 190, fill=NAVY, shadow=(10, 18, 55), outline=NAVY)
        text_c(d, (260, 70), "harga Pertamax", F("pb", 44), WHITE)
        text_c(d, (260, 132), "bulan berikutnya", F("pm", 34), YEL)
        return im
    if key == "okt":
        im, d = card(300, 330)
        text_c(d, (150, 55), "OKTOBER", F("pb", 40), NAVY)
        icon_drop(d, 150, 190, 1.0)
        text_c(d, (150, 290), "minyak dunia", F("pm", 28), GREY_T)
        return im
    if key == "nov":
        im, d = card(300, 330)
        text_c(d, (150, 55), "NOVEMBER", F("pb", 40), NAVY)
        icon_pump(d, 85, 95, 0.75)
        text_c(d, (150, 290), "Rp15.950", F("pb", 40), RED)
        return im
    if key == "can":
        im, d = card(400, 310)
        icon_jerrycan(d, 30, 50, 1.0)
        text_c(d, (290, 120), "30 L", F("pb", 70), NAVY)
        text_c(d, (290, 190), "sebulan", F("pm", 34), GREY_T)
        return im
    if key == "naik":
        im, d = card(340, 120, fill=YEL, shadow=(214, 160, 20), outline=NAVY)
        text_c(d, (170, 60), "+Rp1.000/L", F("pb", 50), NAVY); return im
    if key == "total":
        im, d = card(560, 220, fill=NAVY, shadow=(10, 18, 55), outline=NAVY)
        d.rounded_rectangle((40, 40, 520, 140), 20, fill=YEL)
        text_c(d, (280, 90), "+Rp30.000", F("pb", 76), NAVY)
        text_c(d, (280, 178), "keluar lebih banyak sebulan", F("pm", 30), WHITE)
        return im
    if key == "bubble":
        im = Image.new("RGBA", (560, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, 560, 110), 28, fill=NAVY)
        d.polygon([(70, 105), (120, 105), (60, 148)], fill=NAVY)
        text_c(d, (280, 55), "tulis tebakanmu di komentar", F("pb", 32), WHITE); return im
    raise KeyError(key)


def draw_chart(L, d, x, y, w, h, t):
    """garis harga minyak naik-turun yang terus bergerak."""
    pts = []
    for k in range(41):
        u = k / 40
        v = 0.5 + 0.28 * math.sin(u * 9 + t * 3.2) + 0.15 * math.sin(u * 23 - t * 5.1)
        pts.append((x + u * w, y + h * (1 - clamp(v, 0.05, 0.95))))
    d.line(pts, fill=RED, width=8, joint="curve")
    ex, ey = pts[-1]
    d.ellipse((ex - 11, ey - 11, ex + 11, ey + 11), fill=RED)


def scene_photo(k, t):
    L = Image.new("RGBA", (PW, PH), PHOTO + (255,)); d = ImageDraw.Draw(L)
    ts = t - SC[k]
    if k == 0:
        im, cd = card(500, 250)
        cd.text((30, 40), "minyak dunia", font=F("pm", 30), fill=BROWN, anchor="lm")
        cd.text((470, 40), "naik turun", font=F("pb", 26), fill=RED, anchor="rm")
        draw_chart(im, cd, 30, 75, 440, 150, t)
        L.alpha_composite(im, (30, 30))
        board = static_card("board")
        L.alpha_composite(board, (30, 300))
        d.line([(60, 540), (500, 540)], fill=TEAL, width=6)
        d.text((280, 565), "diam · nggak ikut naik", font=F("pb", 26), fill=TEAL, anchor="mm")
        draw_aru(L, 700, 735, 520, t)
        paste_c(L, static_card("q"), 610, 170, pop(t, cs(3)), 8 * math.sin(t * 4))
        paste_c(L, static_card("janji"), 290, 150, pop(t, JANJI_T), -3)
    elif k == 1:
        im, cd = card(460, 560)
        cd.rounded_rectangle((0, 0, 460, 120), 26, fill=RED); cd.rectangle((0, 60, 460, 120), fill=RED)
        text_c(cd, (230, 62), "NOVEMBER", F("pb", 52), WHITE)
        text_c(cd, (230, 330), "1", F("pb", 280), NAVY)
        text_c(cd, (230, 515), "harga BBM baru", F("pm", 32), GREY_T)
        prog = eout((t - cs(8)) / 0.7)
        if prog > 0:
            cd.arc((95, 190, 365, 470), -90, -90 + 360 * prog, fill=YEL, width=16)
        paste_c(L, im, 290, 360, pop(t, SC[1] + 0.05))
        paste_c(L, static_card("tag1x"), 620, 110, pop(t, cs(7)), 6)
        draw_aru(L, 700, 740, 430, t)
    elif k == 2:
        a = pop(t, cs(10)); b = pop(t, cs(11)); c = pop(t, cs(12))
        paste_c(L, static_card("mops"), 225, 180, a, -2)
        paste_c(L, static_card("kurs"), 640, 180, b, 2)
        g = eout((t - cs(12)) / 0.4)
        if g > 0:
            arrow(d, 225, 330, 225 + (330 - 225) * g, 330 + (430 - 330) * g, NAVY)
            arrow(d, 640, 330, 640 + (530 - 640) * g, 330 + (430 - 330) * g, NAVY)
        paste_c(L, static_card("hasil"), 400, 540, c)
        draw_aru(L, 760, 750, 300, t)
    elif k == 3:
        paste_c(L, static_card("nov"), 680, 230, pop(t, cs(14)), 2)
        paste_c(L, static_card("okt"), 180, 230, pop(t, cs(16)), -2)
        g = eout((t - cs(16) - 0.15) / 0.4)
        if g > 0:
            arrow(d, 345, 230, 345 + 165 * g, 230, YEL, w=22, head=44)
        hl = eout((t - cs(17)) / 0.35)
        if hl > 0:
            d.rectangle((40, 420, 40 + 300 * hl, 480), fill=YEL)
            d.text((190, 450), "= bulan lalu", font=F("pb", 40), fill=NAVY, anchor="mm")
        draw_aru(L, 430, 750, 280, t)
    elif k == 4:
        paste_c(L, static_card("can"), 235, 190, pop(t, SC[4] + 0.1), -2)
        paste_c(L, static_card("naik"), 640, 120, pop(t, cs(20)), 5)
        paste_c(L, static_card("total"), 520, 470, pop(t, cs(22)))
        tb = t - cs(20)
        if tb > 0:
            x = -200 + 330 * eout(tb / 0.6)
            hop = abs(math.sin(tb * 12)) * 14
            for j in range(3):
                ct = tb - j * 0.18
                if ct > 0:
                    paste_c(L, coin(), 330 + j * 40, 300 + min(380, 900 * ct * ct), 1, ct * 200)
            paste_c(L, bocor_img(), x, 610 - hop, 0.95)
    elif k == 5:
        im, cd = card(440, 500)
        cd.rounded_rectangle((0, 0, 440, 110), 26, fill=TEAL); cd.rectangle((0, 55, 440, 110), fill=TEAL)
        text_c(cd, (220, 57), "DESEMBER", F("pb", 50), WHITE)
        text_c(cd, (220, 300), "?", F("pb", 250), NAVY)
        paste_c(L, im, 430, 300, pop(t, SC[5] + 0.05), 4 * math.sin(t * 3))
        pu = 0.5 + 0.5 * math.sin(t * 6); pd = 1 - pu
        arrow(d, 110, 420, 110, 230 - 30 * pu, RED, w=26, head=56)
        text_c(d, (110, 465), "naik", F("pb", 36), RED)
        arrow(d, 750, 180, 750, 380 + 30 * pd, GREEN, w=26, head=56)
        text_c(d, (750, 430), "turun", F("pb", 36), GREEN)
        paste_c(L, static_card("bubble"), 360, 660, pop(t, cs(25)))
        draw_aru(L, 760, 755, 230, t)
    return L


# ---------- polaroid ----------
def typewriter(s, ts):
    n = int(clamp((ts - 0.25) / 1.1) * len(s))
    return s[:n]


def polaroid(k, t):
    PL = Image.new("RGBA", (940, 1000), (0, 0, 0, 0)); d = ImageDraw.Draw(PL)
    d.rectangle((14, 16, 940, 1000), fill=(0, 0, 0, 40))
    d.rectangle((0, 0, 926, 984), fill=WHITE)
    PL.alpha_composite(scene_photo(k, t), (33, 33))
    cap = typewriter(CAPTIONS[k], t - SC[k])
    d.text((463, 890), cap, font=F("cb", 36), fill=BROWN, anchor="mm")
    return PL


# ---------- subtitle ----------
def sub_chunk(t):
    for i, c in enumerate(TIM):
        s = 0.0 if i == 0 else cs(i)
        nxt = cs(i + 1) if i + 1 < len(TIM) else TOTAL
        e = min(nxt, ce(i) + 0.45)
        if s <= t < e:
            return i
    return None


def draw_sub(img, t):
    i = sub_chunk(t)
    if i is None: return
    c = TIM[i]; font = F("lb", 62)
    words = c["text"].split()
    pad, gap = 22, 14
    ws = [font.getbbox(w)[2] - font.getbbox(w)[0] + 2 * pad for w in words]
    tot = sum(ws) + gap * (len(ws) - 1)
    layer = Image.new("RGBA", (tot + 20, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    x = 0
    for w, ww in zip(words, ws):
        key = w in c["keys"]
        d.rounded_rectangle((x + 6, 14, x + ww + 6, 110), 14, fill=(0, 0, 0, 45))
        d.rounded_rectangle((x, 8, x + ww, 104), 14, fill=YEL if key else CREAM)
        d.text((x + ww / 2, 56), w, font=font, fill=NAVY if key else BROWN, anchor="mm")
        x += ww + gap
    s0 = 0.0 if i == 0 else cs(i)
    sc = 0.85 + 0.15 * back((t - s0) / 0.22) if i != 0 else 1.0
    if layer.width * sc > 1000: sc = 1000 / layer.width
    paste_c(img, layer, W / 2, 1468, sc)


# ---------- latar & header ----------
@lru_cache(None)
def base_bg():
    bg = Image.new("RGBA", (W, H))
    top, bot = (233, 220, 203), (242, 232, 218)
    d = ImageDraw.Draw(bg)
    for y in range(H):
        u = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[j] + (bot[j] - top[j]) * u) for j in range(3)) + (255,))
    # header
    f = F("pb", 30); s = "UANG SEHARI-HARI · BBM"
    tw = f.getbbox(s)[2]
    d.rounded_rectangle((44, 190, 44 + tw + 52, 254), 32, fill=NAVY)
    d.text((70, 222), s, font=f, fill=WHITE, anchor="lm")
    lg = logo_w(250)
    bg.alpha_composite(lg, (W - 44 - lg.width, 222 - lg.height // 2))
    d.text((48, 300), "now playing: kok bisa? · harga bbm", font=F("cb", 34), fill=BROWN, anchor="lm")
    return bg


@lru_cache(None)
def title_layer():
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for y in range(980, 1640):
        if y < 1170: a = (y - 980) / 190 * 0.80
        elif y < 1540: a = 0.80
        else: a = 0.80 * (1 - (y - 1540) / 100)
        d.line([(0, y), (W, y)], fill=NAVY + (int(255 * a),))
    f = F("pb", 96)
    def line(y, parts):
        tw = sum(f.getbbox(p)[2] for p, _ in parts)
        x = (W - tw) / 2
        for p, col in parts:
            d.text((x, y), p, font=f, fill=col, anchor="ls", stroke_width=9, stroke_fill=NAVY)
            x += f.getbbox(p)[2]
    line(1265, [("PERTAMAX, KOK", WHITE)])
    line(1375, [("TELAT", YEL), (" NAIK?", WHITE)])
    return L


def frame(t):
    img = base_bg().copy()
    k = scene_of(t)
    ts = t - SC[k]
    PL = polaroid(k, t)
    ang = [-1.8, 1.6, -1.4, 1.8, -1.6, 1.4][k]
    s = 0.93 + 0.07 * back(ts / 0.4) if k > 0 else 1.0
    paste_c(img, PL, W / 2, 875, s, ang)
    # selotip
    tape = Image.new("RGBA", (230, 64), (255, 214, 102, 190))
    paste_c(img, tape, W / 2, 392, 1, -3)
    # judul cover (adegan 1, pudar di awal adegan 2)
    ta = 1.0 if t < SC[1] else clamp(1 - (t - SC[1]) / 0.3)
    if ta > 0:
        tl = title_layer()
        if ta < 1:
            tl = tl.copy(); tl.putalpha(tl.getchannel("A").point(lambda v: int(v * ta)))
        img.alpha_composite(tl)
    draw_sub(img, t)
    d = ImageDraw.Draw(img)
    # ajakan follow (sebelum dtk 15)
    if FOLLOW[0] <= t < FOLLOW[1]:
        f = F("pb", 30); s_ = "follow @kabar.arunika · hitung-hitungan tiap hari"
        tw = f.getbbox(s_)[2]
        pl = Image.new("RGBA", (tw + 60, 60), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
        pd.rounded_rectangle((0, 0, tw + 60, 60), 30, fill=NAVY)
        pd.ellipse((18, 22, 34, 38), fill=TEAL)
        pd.text((44, 30), s_, font=f, fill=WHITE, anchor="lm")
        paste_c(img, pl, W / 2, 1585, pop(t, FOLLOW[0]))
    # catatan kaki
    note = {0: "*harga Pertamax wilayah Jawa, 1 Nov 2026",
            4: "*30 liter & naik Rp1.000 = angka contoh ilustrasi"}.get(k)
    if note:
        d.text((W / 2, 1660), note, font=F("pm", 26), fill=GREY_T, anchor="mm")
    # logo kecil di penutup (≤1,5 dtk)
    la = clamp((t - (TOTAL - 1.5)) / 0.3)
    if la > 0:
        paste_c(img, logo_w(300), W / 2, 1640, 0.9 + 0.1 * back(la), 0, la)
    # progress bar
    d.rectangle((0, H - 14, int(W * t / TOTAL), H), fill=YEL)
    return img.convert("RGB")


def events():
    ev = [{"t": SC[k], "sfx": "whoosh", "gain": 0.30} for k in range(1, 6)]
    for i in (3, 7, 10, 11, 12, 14, 16, 18, 25):
        ev.append({"t": cs(i), "sfx": "pop", "gain": 0.28})
    ev.append({"t": JANJI_T, "sfx": "pop", "gain": 0.28})
    ev.append({"t": FOLLOW[0], "sfx": "klik", "gain": 0.3})
    ev.append({"t": cs(20), "sfx": "cring", "gain": 0.45})
    ev.append({"t": cs(22), "sfx": "ding", "gain": 0.35})
    json.dump(ev, open("events.json", "w"), indent=1)
    print(len(ev), "events")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "events":
        events()
    elif cmd == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        ims = []
        for tt in ts:
            im = frame(tt); im.save(f"still_{tt:.2f}.png"); ims.append(im.resize((360, 640)))
        cols = 4; rows = math.ceil(len(ims) / cols)
        sh = Image.new("RGB", (360 * cols, 640 * rows), WHITE)
        for j, im in enumerate(ims):
            sh.paste(im, ((j % cols) * 360, (j // cols) * 640))
        sh.save("sheet.png"); print("sheet.png")
    elif cmd == "video":
        out, a, b = sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                              "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        n0, n1 = round(a * FPS), round(b * FPS)
        for n in range(n0, n1):
            p.stdin.write(frame(n / FPS).tobytes())
        p.stdin.close(); p.wait(); print(out, n1 - n0, "frames")

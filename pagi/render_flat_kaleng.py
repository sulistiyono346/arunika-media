"""Renderer ARN-62 "Tamu datang, minuman HANGAT?" -- REEL BISU 12 dtk tanpa VO (PRB-19), Flat 2D latar terang.
Helper (font, palet, pill, kartu, emoji, Aru resmi) dari render_flat_amplop.py / render_gaya_frame0.py.
Timing adegan = detik di naskah final kartu (tidak ada VO, jadi tidak ada align.py / timing.json).

Pemakaian (folder kerja bebas; skrip dipanggil dengan path lengkap):
  python3 render_flat_kaleng.py events                 -> events.json (sfx untuk mix_kaleng.py)
  python3 render_flat_kaleng.py check                  -> cek area aman x 130..950 (PRB-41)
  python3 render_flat_kaleng.py stills 0,0.6,1.6,...   -> still_*.png + sheet.png
  python3 render_flat_kaleng.py video out.mp4 0 12
"""
import json, math, os, sys, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_gaya_frame0 import F, clamp, eio, NAVY, TEAL, YEL, WHITE, CREAM, GREY_T, RED, SAFE_X

W, H, FPS = 1080, 1920, 30
TOTAL = 12.0
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
INK = (60, 66, 92); LIGHT = (232, 238, 246)
ICE = (214, 238, 252); WATER = (120, 186, 232); WATER_D = (70, 140, 200)
COLD = (52, 132, 220); HOT = (232, 96, 60)
MAXW = 800; XMIN, XMAX = SAFE_X, W - SAFE_X

# adegan sesuai naskah final: [1]0-1 [2]1-2 [3]2-4 [4]4-6 [5]6-8 [6]8-10,5 [7]10,5-12
SC = [0.0, 1.0, 2.0, 4.0, 6.0, 8.0, 10.5, TOTAL]
NS = len(SC) - 1
T_UI = 1.5          # timer & termometer muncul (dtk ~1,5)
T_PAY = 7.0         # termometer kanan tepat 5 C -> "2,5 MENIT" + cring + ajakan kirim
T_10J = 7.35        # time-lapse kulkas sampai "10 JAM"
LX, RX = 335, 745   # pusat sisi kiri / kanan


def scene_of(t):
    for k in range(NS):
        if t < SC[k + 1]: return k
    return NS - 1


def back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def pop(t, t0, d=0.35): return 0.0 if t < t0 else back((t - t0) / d)
def fade(t, t0, d=0.2): return clamp((t - t0) / d)


BOXES = []
def track(tag, nw, x0, x1): BOXES.append((tag, nw, x0, x1))


def trim(im): return im.crop(im.getbbox())
ARU = trim(Image.open(MEDIA + "/maskot/aru-syal-bendera.png").convert("RGBA"))   # 629x984, tangan kiri-atas (50,365)
LOGO = trim(Image.open(MEDIA + "/brand/arunika-logo.png").convert("RGBA"))


@lru_cache(None)
def aru_h(h, flip=False):
    r = h / ARU.height
    im = ARU.resize((int(ARU.width * r), h), Image.LANCZOS)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im


@lru_cache(None)
def logo_w(w):
    r = w / LOGO.width
    return LOGO.resize((w, int(LOGO.height * r)), Image.LANCZOS)


def paste_c(dst, im, cx, cy, scale=1.0, angle=0.0, alpha=1.0, tag=None):
    if scale <= 0.01 or alpha <= 0.01: return
    if tag and scale > 1 and im.info.get("nw", im.width) * scale > MAXW:
        scale = max(1.0, MAXW / im.info.get("nw", im.width))
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if abs(angle) > 0.05:
        im = im.rotate(angle, Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = im.getchannel("A").point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    if tag and scale > 1 and im.info.get("nw", im.width) * scale > MAXW:
        scale = max(1.0, MAXW / im.info.get("nw", im.width))      # overshoot pop tidak melewati 800 px
    if tag:
        nw = im.info.get("nw", im.width) * (scale if abs(scale - 1) > 1e-3 else 1)
        track(tag, nw, cx - nw / 2, cx + nw / 2)
    dst.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


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


@lru_cache(None)
def pill(text, fill=NAVY, fg=WHITE, size=50, padx=34):
    f = F("pb", size); w = int(f.getlength(text) + 2 * padx); h = size + 44
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 10, w + 8, h + 10), h // 2, fill=(20, 33, 91, 55))
    d.rounded_rectangle((0, 0, w, h), h // 2, fill=fill, outline=NAVY, width=5)
    text_c(d, (w / 2, h / 2 + 2), text, f, fg)
    im.info["nw"] = w
    return im


EMOJI_F = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
@lru_cache(None)
def emoji_img(ch, h):
    f = ImageFont.truetype(EMOJI_F, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = trim(im); r = h / im.height
    return im.resize((max(1, int(im.width * r)), h), Image.LANCZOS)


def rich_line(d, cx, cy, parts, f, base=NAVY, hl=YEL, hl_fg=NAVY, on_dark=False):
    """parts: [(teks, sorot?)] -> satu baris, kata sorot di kotak kuning."""
    widths = [f.getlength(s) for s, _ in parts]
    x = cx - sum(widths) / 2
    for (s, k), w_ in zip(parts, widths):
        if k:
            d.rounded_rectangle((x - 6, cy - f.size * 0.62, x + w_ + 6, cy + f.size * 0.62), 14, fill=hl)
            d.text((x, cy + 2), s, font=f, fill=hl_fg, anchor="lm")
        else:
            d.text((x, cy + 2), s, font=f, fill=(WHITE if on_dark else base), anchor="lm")
        x += w_
    return sum(widths)


# ---------- benda ----------
@lru_cache(None)
def can_img(w, cold=False):
    h = int(w * 1.72)
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    o = 10; ew = int(w * 0.16)
    body = (o, o + ew // 2, o + w, o + h - ew // 2)
    d.rounded_rectangle(body, 18, fill=(214, 220, 230), outline=NAVY, width=6)
    # label
    d.rectangle((o + 6, o + int(h * 0.22), o + w - 6, o + int(h * 0.78)), fill=(RED if not cold else TEAL))
    d.rectangle((o + 6, o + int(h * 0.43), o + w - 6, o + int(h * 0.53)), fill=WHITE)
    d.line((o + int(w * 0.24), o + int(h * 0.12), o + int(w * 0.24), o + int(h * 0.88)), fill=(255, 255, 255, 150), width=max(4, w // 14))
    d.rounded_rectangle(body, 18, outline=NAVY, width=6)
    # tutup
    d.ellipse((o + 4, o, o + w - 4, o + ew), fill=(236, 240, 246), outline=NAVY, width=5)
    d.ellipse((o + w * 0.42, o + ew * 0.25, o + w * 0.62, o + ew * 0.7), fill=(170, 178, 192))
    if cold:   # embun
        for (fx, fy, r) in [(0.7, 0.3, 7), (0.82, 0.48, 6), (0.62, 0.66, 8), (0.78, 0.8, 6), (0.35, 0.36, 6), (0.46, 0.84, 7), (0.2, 0.6, 5)]:
            x, y = o + fx * w, o + fy * h
            d.ellipse((x - r, y - r * 1.3, x + r, y + r), fill=(230, 246, 255), outline=(120, 170, 220), width=2)
    return im


def heat_lines(d, cx, top, t, n=3, gap=34, L=110, col=HOT, w=8):
    for j in range(n):
        x0 = cx + (j - (n - 1) / 2) * gap
        pts = []
        for s in range(0, L + 1, 6):
            y = top - s
            pts.append((x0 + 10 * math.sin(s / 16 + t * 9 + j * 1.7), y))
        d.line(pts, fill=col, width=w, joint="curve")


def ice_cube(d, x, y, s, ang=0):
    c, sn = math.cos(ang), math.sin(ang)
    pts = [(x + dx * c - dy * sn, y + dx * sn + dy * c) for dx, dy in [(-s, -s), (s, -s), (s, s), (-s, s)]]
    d.polygon(pts, fill=(236, 248, 255), outline=(120, 170, 220))
    d.line(pts + [pts[0]], fill=(110, 160, 214), width=4)
    d.line([pts[0], ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)], fill=WHITE, width=5)


def thermo(img, cx, top, temp, tag, t):
    """termometer vertikal: skala -20..30 C."""
    d = ImageDraw.Draw(img)
    h = 380; bx = cx; by = top + h + 34
    d.rounded_rectangle((bx - 26, top, bx + 26, top + h + 20), 26, fill=WHITE, outline=NAVY, width=6)
    frac = clamp((temp + 20) / 50)
    col = tuple(int(COLD[i] + (HOT[i] - COLD[i]) * clamp((temp - 5) / 16)) for i in range(3))
    d.rounded_rectangle((bx - 12, top + 14 + (1 - frac) * (h - 10), bx + 12, top + h + 20), 12, fill=col)
    d.ellipse((bx - 46, by - 46, bx + 46, by + 46), fill=col, outline=NAVY, width=6)
    for k in range(6):
        y = top + 24 + k * (h - 20) / 5
        d.line((bx + 26, y, bx + 42, y), fill=NAVY, width=4)
    track(tag, 92, bx - 46, bx + 46)
    return col


def temp_str(v):
    v = round(v)
    return ("−" if v < 0 else "") + f"{abs(v)}°C"


def timer_box(img, cx, cy, s, tag, col=NAVY):
    f = F("pb", 74)
    w = 330; h = 112
    L = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((8, 10, w + 8, h + 10), 28, fill=(20, 33, 91, 50))
    d.rounded_rectangle((0, 0, w, h), 28, fill=WHITE, outline=col, width=6)
    # ikon jam kecil
    d.ellipse((22, 30, 74, 82), outline=col, width=6)
    d.line((48, 56, 48, 40), fill=col, width=5); d.line((48, 56, 60, 62), fill=col, width=5)
    text_c(d, (w / 2 + 34, h / 2 + 4), s, fit("pb", 74, s, w - 110), col)
    L.info["nw"] = w
    paste_c(img, L, cx, cy, tag=tag)


# waktu & suhu (uji SINTEF 19 Des 2025: kaleng 0,33 L, 21 C; es+garam ke 5 C 2,5 menit; kulkas ke 5 C 10 jam)
def right_minutes(t):        # 0 -> 2,5 menit antara dtk 1,5 dan 7,0
    return 2.5 * clamp((t - T_UI) / (T_PAY - T_UI))
def right_temp(t):
    x = clamp((t - T_UI) / (T_PAY - T_UI))
    return 21 - 16 * (1 - math.exp(-2.6 * x)) / (1 - math.exp(-2.6))
def left_hours(t):
    if t < 6.0: return right_minutes(t) / 60
    m0 = right_minutes(6.0) / 60
    return m0 + (10 - m0) * eio((t - 6.0) / (T_10J - 6.0))
def left_temp(t):
    h = left_hours(t)
    # kulkas: ke 9 C dalam 2,5 jam, ke 5 C dalam 10 jam (kurva kasar)
    if h <= 2.5: return 21 - 12 * (1 - math.exp(-h * 1.2)) / (1 - math.exp(-3.0))
    return 9 - 4 * clamp((h - 2.5) / 7.5) ** 0.8


def fmt_right(t):
    sec = int(round(right_minutes(t) * 60))
    return f"{sec // 60}:{sec % 60:02d}"
def fmt_left(t):
    h = left_hours(t)
    if h < 1 / 60 * 10 and t < 6.0:
        sec = int(round(h * 3600)); return f"{sec // 60}:{sec % 60:02d}"
    hh = int(h); mm = int((h - hh) * 60)
    if t >= T_10J: hh, mm = 10, 0
    return f"{hh}j {mm:02d}m"


# ---------- latar ----------
@lru_cache(None)
def bg_room():
    img = Image.new("RGBA", (W, H), CREAM); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 1420), fill=(255, 241, 214))
    for x in range(0, W, 90):
        d.line((x, 0, x, 1420), fill=(250, 232, 200), width=30)
    d.rectangle((0, 1420, W, H), fill=(214, 178, 132))
    d.rectangle((0, 1420, W, 1440), fill=(180, 140, 96))
    # pintu kanan
    d.rounded_rectangle((800, 700, 1040, 1430), 12, fill=(176, 120, 72), outline=NAVY, width=6)
    d.rectangle((830, 740, 1010, 1040), outline=(140, 92, 52), width=6)
    d.rectangle((830, 1080, 1010, 1390), outline=(140, 92, 52), width=6)
    d.ellipse((822, 1060, 846, 1084), fill=YEL, outline=NAVY, width=4)
    # jendela kiri
    d.rounded_rectangle((40, 620, 260, 900), 10, fill=(190, 226, 250), outline=NAVY, width=6)
    d.line((150, 620, 150, 900), fill=NAVY, width=6); d.line((40, 760, 260, 760), fill=NAVY, width=6)
    # sofa
    d.rounded_rectangle((-40, 1220, 330, 1440), 40, fill=TEAL, outline=NAVY, width=6)
    d.rounded_rectangle((-40, 1150, 300, 1290), 40, fill=(14, 166, 150), outline=NAVY, width=6)
    return img


@lru_cache(None)
def bg_split():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W // 2, H), fill=(230, 240, 252))
    d.rectangle((W // 2, 0, W, H), fill=(224, 247, 243))
    d.rectangle((0, 1300, W, H), fill=(246, 242, 234))
    d.line((W // 2, 0, W // 2, 1420), fill=NAVY, width=8)  # berhenti di atas baris sumber (QA 26 Nov)
    return img


def bell(img, cx, cy, t, t0=0.0):
    L = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.pieslice((30, 30, 170, 190), 180, 360, fill=YEL, outline=NAVY, width=7)
    d.rectangle((30, 108, 170, 130), fill=YEL, outline=NAVY, width=7)
    d.rectangle((37, 100, 163, 116), fill=YEL)
    d.ellipse((86, 126, 114, 154), fill=YEL, outline=NAVY, width=6)
    d.ellipse((88, 14, 112, 38), fill=YEL, outline=NAVY, width=6)
    ang = 22 * math.sin((t - t0) * 26) * math.exp(-max(0, t - t0 - 0.8) * 2)
    paste_c(img, L, cx, cy, 1.0, ang, tag="bel")
    d2 = ImageDraw.Draw(img)
    for s in (1, -1):    # garis getar
        for j in range(2):
            r = 110 + j * 30
            d2.arc((cx - r, cy - r + 10, cx + r, cy + r + 10), (-35 if s > 0 else 180 - 10) , (10 if s > 0 else 215), fill=NAVY, width=6)


def bubble_tingtong(img, t, t0):
    a = pop(t, t0, 0.3)
    if a <= 0: return
    f = F("pb", 60); s = "TING-TONG!"
    w = int(f.getlength(s) + 60); h = 110
    L = Image.new("RGBA", (w + 12, h + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((8, 10, w + 8, h + 10), 30, fill=(20, 33, 91, 55))
    d.rounded_rectangle((0, 0, w, h), 30, fill=NAVY)
    d.polygon([(w - 90, h - 2), (w - 40, h - 2), (w - 30, h + 40)], fill=NAVY)
    text_c(d, (w / 2, h / 2 + 3), s, f, YEL)
    L.info["nw"] = w
    paste_c(img, L, 640, 560 + 4 * math.sin(t * 20), a, 0, tag="tingtong")


def title_top(img, t):
    """judul layar (kolom Judul layar): 'Tamu datang, minuman HANGAT?' 2 baris besar, HANGAT? kuning."""
    d = ImageDraw.Draw(img)
    f = F("pb", 78)
    l1 = "Tamu datang,"
    w1 = f.getlength(l1); track("judul", w1, W / 2 - w1 / 2, W / 2 + w1 / 2)
    sh = 2 * math.sin(t * 6)
    d.text((W / 2, 290 + sh), l1, font=f, fill=NAVY, anchor="mm")
    w2 = rich_line(d, W / 2, 392 + sh, [("minuman ", False), ("HANGAT?", True)], f)
    track("judul", w2, W / 2 - w2 / 2, W / 2 + w2 / 2)


def scene0(img, t):
    d = ImageDraw.Draw(img)
    title_top(img, t)
    bell(img, 905, 640, t, 0.0)
    bubble_tingtong(img, t, 0.12)
    # Aru: menoleh kaget (flip) di dtk ~0,45, lompat kecil
    turned = t >= 0.45
    hgt = 860
    jump = -40 * math.sin(math.pi * clamp((t - 0.45) / 0.3)) if t >= 0.45 else 0
    bob = 6 * math.sin(2 * math.pi * 1.4 * t)
    im = aru_h(hgt, turned)
    r = hgt / ARU.height
    cx = 470; bottom = 1560 + jump + bob
    x0 = cx - im.width / 2; y0 = bottom - hgt
    img.alpha_composite(im, (int(x0), int(y0)))
    track("aru", im.width, x0, x0 + im.width)
    hx = (50 if not turned else ARU.width - 50) * r + x0
    hy = 365 * r + y0
    can = can_img(150)
    cy = hy - 70
    heat_lines(d, hx, cy - can.height / 2 - 10, t, n=3, gap=38, L=130)
    paste_c(img, can, hx, cy, 1.0, 6 * math.sin(t * 7))
    if turned:   # tanda kaget
        a = pop(t, 0.45, 0.25)
        fx = F("pb", 110)
        L = Image.new("RGBA", (220, 160), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
        ld.text((40, 80), "!", font=fx, fill=RED, anchor="mm", stroke_width=6, stroke_fill=NAVY)
        ld.text((120, 70), "!", font=fx, fill=RED, anchor="mm", stroke_width=6, stroke_fill=NAVY)
        paste_c(img, L, cx + 180, y0 + 40, a)


# ---------- split ----------
def fridge(img, cx, top, t, can_in_t):
    d = ImageDraw.Draw(img)
    w, h = 300, 560
    x0, x1 = cx - w / 2, cx + w / 2
    d.rounded_rectangle((x0 + 10, top + 14, x1 + 10, top + h + 14), 26, fill=(20, 33, 91, 40))
    d.rounded_rectangle((x0, top, x1, top + h), 26, fill=(244, 248, 252), outline=NAVY, width=7)
    d.line((x0, top + 180, x1, top + 180), fill=NAVY, width=6)
    # bagian dalam (pintu bawah terbuka saat kaleng masuk)
    op = clamp((t - can_in_t + 0.25) / 0.2) * (1 - clamp((t - can_in_t - 0.35) / 0.25))
    d.rectangle((x0 + 16, top + 196, x1 - 16, top + h - 16), fill=(206, 226, 246))
    for yy in (top + 330, top + 450):
        d.line((x0 + 16, yy, x1 - 16, yy), fill=(160, 190, 222), width=6)
    # kaleng di rak
    k = eout((t - can_in_t) / 0.4)
    cyy = top + 330 - 76
    paste_c(img, can_img(84, cold=False), cx - 260 * (1 - k), cyy, 1.0)
    # pintu (tertutup -> tirai) : saat tertutup gambar panel penuh
    if op < 0.99:
        dw = (w - 32) * (1 - op)
        d.rounded_rectangle((x0 + 4, top + 186, x0 + 16 + dw, top + h - 4), 18, fill=(244, 248, 252), outline=NAVY, width=6)
        d.rounded_rectangle((x0 + dw - 6, top + 230, x0 + dw + 6, top + 330), 6, fill=(170, 180, 200))
    d.rounded_rectangle((x0 + 22, top + 40, x0 + 34, top + 140), 6, fill=(170, 180, 200))
    # salju / dingin kecil
    d.text((cx + 70, top + 92), "❄", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64), fill=COLD, anchor="mm")
    track("kulkas", w, x0, x1)


def basin(img, cx, top, t, dip_t, spin=False):
    d = ImageDraw.Draw(img)
    w = 330; h = 260; y0 = top + 220
    # kaleng dicelup
    k = eout((t - dip_t) / 0.45)
    can = can_img(96, cold=right_temp(t) < 10)
    can_y = (top - 20) + (y0 - 10 - (top - 20)) * k
    ang = 0
    if spin:
        ang = 10 * math.sin(t * 6)
    # baskom belakang
    d.ellipse((cx - w / 2, y0 - 40, cx + w / 2, y0 + 40), fill=WATER_D, outline=NAVY, width=6)
    paste_c(img, can, cx, can_y, 1.0, ang)
    # air depan + es (menutupi kaleng bagian bawah)
    poly = [(cx - w / 2, y0), (cx + w / 2, y0), (cx + w / 2 - 50, y0 + h), (cx - w / 2 + 50, y0 + h)]
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    ld.polygon(poly, fill=WATER + (235,))
    img.alpha_composite(L)
    for j, (dx, dy, s, a) in enumerate([(-120, 40, 30, 0.2), (-50, 20, 26, -0.3), (40, 46, 30, 0.5), (115, 26, 26, 0.1), (-90, 110, 28, -0.2), (70, 120, 28, 0.3), (0, 96, 24, 0.7)]):
        ice_cube(d, cx + dx, y0 + dy + 4 * math.sin(t * 3 + j), s, a + 0.05 * math.sin(t * 2 + j))
    d.line(poly + [poly[0]], fill=NAVY, width=7)
    d.rounded_rectangle((cx - w / 2 - 14, y0 - 12, cx + w / 2 + 14, y0 + 12), 12, fill=(240, 244, 250), outline=NAVY, width=6)
    # taburan garam
    gk = clamp((t - (dip_t - 0.4)) / 0.6)
    if 0 < gk < 1:
        for j in range(18):
            gx = cx + 120 + 30 * math.sin(j * 1.7); gy = top - 40 + ((j * 37 + gk * 300) % 200)
            d.rectangle((gx, gy, gx + 7, gy + 7), fill=WHITE, outline=(160, 160, 180))
    track("baskom", w + 28, cx - w / 2 - 14, cx + w / 2 + 14)
    return can_y


def label_pills(img, t, t0=1.0):
    a = pop(t, t0, 0.3)
    paste_c(img, pill("KULKAS", NAVY, WHITE, 60), LX, 330, a, tag="label kiri")
    paste_c(img, pill("ES + GARAM", NAVY, YEL, 52, 26), RX, 330, a, tag="label kanan")


def big_temp(img, cx, cy, temp, col, tag):
    d = ImageDraw.Draw(img); s = temp_str(temp)
    f = F("pb", 92)
    d.text((cx, cy), s, font=f, fill=col, anchor="mm", stroke_width=5, stroke_fill=WHITE)
    w = f.getlength(s); track(tag, w, cx - w / 2, cx + w / 2)


def small_note(img, s, cx, cy, size=34, col=INK, fill=WHITE, tag=None):
    f = fit("pb", size, s, 380)
    w = int(f.getlength(s) + 36); h = size + 26
    L = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, w, h), h // 2, fill=fill, outline=NAVY, width=4)
    text_c(d, (w / 2, h / 2 + 2), s, f, col)
    L.info["nw"] = w
    paste_c(img, L, cx, cy, tag=tag)


def source(img, lines, y0=1640, a=1.0):
    L = Image.new("RGBA", (W, 50 * len(lines) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for j, s in enumerate(lines):
        f = fit("pm", 30, s, MAXW)
        d.text((W / 2, 25 + j * 44), s, font=f, fill=INK if j == 0 else GREY_T, anchor="mm")
        track("sumber", f.getlength(s), W / 2 - f.getlength(s) / 2, W / 2 + f.getlength(s) / 2)
    paste_c(img, L, W / 2, y0 + L.height / 2 - 25, 1, 0, a)


@lru_cache(None)
def guess_pill():
    f = F("pb", 52)
    l1, l2 = "Tebak, kalengmu", "dingin duluan di mana?"
    w = int(max(f.getlength(l1), f.getlength(l2)) + 70); h = 170
    L = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((8, 10, w + 8, h + 10), 40, fill=(20, 33, 91, 60))
    d.rounded_rectangle((0, 0, w, h), 40, fill=NAVY)
    text_c(d, (w / 2, 52), l1, f, YEL); text_c(d, (w / 2, 118), l2, f, WHITE)
    L.info["nw"] = w
    return L


@lru_cache(None)
def share_layer():
    f = F("pb", 46)
    l1 = "Kirim ke teman yang kebagian"; l2 = "bawa minuman"
    w = int(f.getlength(l1) + 70); h = 168
    T, td = card(w, h, fill=NAVY)
    td.text((w / 2, 52), l1, font=f, fill=WHITE, anchor="mm")
    e = emoji_img("📤", 56); tw = f.getlength(l2)
    x0 = (w - tw - 70) / 2
    td.text((x0, 118), l2, font=f, fill=YEL, anchor="lm")
    T.alpha_composite(e, (int(x0 + tw + 14), int(118 - e.height / 2)))
    return T


def big_result(img, cx, cy, num, unit, t0, t, tag):
    a = pop(t, t0, 0.4)
    if a <= 0: return
    L = Image.new("RGBA", (420, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f1 = F("pb", 150); f2 = F("pb", 70)
    d.text((210, 92), num, font=f1, fill=YEL, anchor="mm", stroke_width=9, stroke_fill=NAVY)
    d.text((210, 205), unit, font=f2, fill=YEL, anchor="mm", stroke_width=7, stroke_fill=NAVY)
    L.info["nw"] = max(f1.getlength(num), f2.getlength(unit)) + 18
    paste_c(img, L, cx, cy, a, tag=tag)


def clock_spin(img, cx, cy, t):
    d = ImageDraw.Draw(img); r = 62
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=WHITE, outline=NAVY, width=7)
    a1 = t * 40; a2 = t * 3.3
    d.line((cx, cy, cx + 44 * math.sin(a1), cy - 44 * math.cos(a1)), fill=RED, width=6)
    d.line((cx, cy, cx + 30 * math.sin(a2), cy - 30 * math.cos(a2)), fill=NAVY, width=8)
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=NAVY)
    for k in range(3):
        aa = t * 12 + k * 2.1
        d.arc((cx - r - 22, cy - r - 22, cx + r + 22, cy + r + 22), math.degrees(aa), math.degrees(aa) + 40, fill=COLD, width=6)


def split_scene(img, t):
    img.alpha_composite(bg_split())
    label_pills(img, t)
    k = scene_of(t)
    # kiri: kulkas, kanan: baskom
    fridge(img, LX - 45, 600, t, 1.15)
    can_y = basin(img, RX - 25, 640, t, 1.2, spin=(4.0 <= t < 8.0))
    ui = pop(t, T_UI, 0.3)
    if ui > 0:
        # timer & termometer
        lt, rt = left_temp(t), right_temp(t)
        if t >= T_PAY: rt = 5
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        timer_box(L, LX, 470, fmt_left(t), "timer kiri")
        timer_box(L, RX, 470, fmt_right(t) if t < T_PAY else "2:30", "timer kanan", col=(NAVY if t < T_PAY else (14, 140, 120)))
        lc = thermo(L, 492, 700, lt, "termo kiri", t)
        rc = thermo(L, 950, 640, rt, "termo kanan", t)
        if t < T_PAY - 0.05:
            big_temp(L, LX, 1270, lt, lc, "suhu kiri")
            big_temp(L, RX, 1270, rt, rc, "suhu kanan")
        a = min(1.0, ui)
        if a < 0.999:
            L2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); L2.alpha_composite(L)
            al = L2.getchannel("A").point(lambda v: int(v * a)); L2.putalpha(al); img.alpha_composite(L2)
        else:
            img.alpha_composite(L)
    # adegan 3: pill tebak
    if 2.0 <= t < 4.0:
        a = min(pop(t, 2.05, 0.35), clamp((4.0 - t) / 0.15))
        paste_c(img, guess_pill(), W / 2, 1480 + 3 * math.sin(t * 5), a, tag="pill tebak")
    # adegan 4: putar pelan, label suhu medium
    if 4.0 <= t < 6.0:
        a = pop(t, 4.05, 0.3)
        d = ImageDraw.Draw(img)
        # ikon putar di atas kaleng kanan
        cx, cy = RX - 20, can_y - 40
        ang = (t - 4) * 160
        d.arc((cx - 86, cy - 86, cx + 86, cy + 86), ang, ang + 270, fill=TEAL, width=12)
        hx = cx + 86 * math.cos(math.radians(ang + 270)); hy = cy + 86 * math.sin(math.radians(ang + 270))
        d.ellipse((hx - 16, hy - 16, hx + 16, hy + 16), fill=TEAL, outline=NAVY, width=4)
        if a > 0:
            L = Image.new("RGBA", (W, 200), (0, 0, 0, 0))
            small_note(L, "air asin −16°C", RX, 100, 40, col=COLD, tag="lbl air asin")
            small_note(L, "udara ±4°C", LX, 100, 40, col=COLD, tag="lbl udara")
            paste_c(img, L, W / 2, 1400, a)
        source(img, ["suhu bak & kulkas · SINTEF, 19 Des 2025"], a=fade(t, 4.1))
    # adegan 5: PUNCAK
    if 6.0 <= t < 8.0:
        if t < T_10J + 0.3:
            clock_spin(img, LX - 30, 960, t)
        big_result(img, RX, 1290, "2,5", "MENIT", T_PAY, t, "angka 2,5 menit")
        big_result(img, LX, 1290, "10", "JAM", T_10J, t, "angka 10 jam")
        if t >= T_PAY:
            s = 0.85 + 0.15 * back((t - T_PAY) / 0.35)
            paste_c(img, share_layer(), W / 2, 1535 + 3 * math.sin(t * 5), s, 0, fade(t, T_PAY, 0.15), tag="kartu kirim")
            # cring: kilau es
            d = ImageDraw.Draw(img)
            g = clamp((t - T_PAY) / 0.5)
            if g < 1:
                for j in range(6):
                    aa = j * math.pi / 3; rr = 90 + 80 * g
                    x, y = RX - 20 + rr * math.cos(aa), can_y + rr * math.sin(aa)
                    d.line((x - 14, y, x + 14, y), fill=YEL, width=7); d.line((x, y - 14, x, y + 14), fill=YEL, width=7)
        source(img, ["kaleng 0,33 L, 21°C ke 5°C · SINTEF, 19 Des 2025"], y0=1665, a=fade(t, 6.05))


# ---------- adegan 6: kartu layak simpan ----------
@lru_cache(None)
def recipe_card():
    w, h = 800, 720
    L, d = card(w, h, fill=WHITE)
    d.rounded_rectangle((0, 0, w, 120), 30, fill=NAVY); d.rectangle((0, 70, w, 120), fill=NAVY)
    d.rounded_rectangle((0, 0, w, h), 30, outline=NAVY, width=5)
    f = F("pb", 64)
    rich_line(d, w / 2, 62, [("RESEP ", False), ("2,5 MENIT", True)], f, on_dark=True)
    rows = [("1 L air + 250 g garam", None), ("es batu banyak", "(±3× berat garam)"), ("rendam penuh,", "putar pelan sesekali")]
    y = 190
    for j, (a_, b_) in enumerate(rows):
        d.ellipse((40, y - 34, 108, y + 34), fill=TEAL, outline=NAVY, width=4)
        text_c(d, (74, y + 2), str(j + 1), F("pb", 44), WHITE)
        d.text((134, y + 2), a_, font=fit("pb", 52, a_, w - 170), fill=NAVY, anchor="lm")
        if b_:
            d.text((134, y + 58), b_, font=F("pm", 40), fill=INK, anchor="lm")
            y += 170
        else:
            y += 130
    # simpan
    s = "simpan buat pas kumpul"; fs = F("pb", 42); e = emoji_img("📌", 48)
    tw = fs.getlength(s) + 14 + e.width
    x0 = w / 2 - tw / 2
    d.rounded_rectangle((x0 - 26, h - 96, x0 + tw + 26, h - 30), 33, fill=YEL)
    d.text((x0, h - 62), s, font=fs, fill=NAVY, anchor="lm")
    L.alpha_composite(e, (int(x0 + fs.getlength(s) + 14), int(h - 63 - e.height / 2)))
    return L


@lru_cache(None)
def guest_img(h=380):
    im = Image.new("RGBA", (260, h + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 150, 200, h - 70), 50, fill=(232, 92, 140), outline=NAVY, width=6)
    d.rounded_rectangle((78, h - 90, 116, h), 14, fill=(85, 82, 94), outline=NAVY, width=5)
    d.rounded_rectangle((144, h - 90, 182, h), 14, fill=(85, 82, 94), outline=NAVY, width=5)
    d.ellipse((60, 10, 200, 150), fill=(240, 196, 160), outline=NAVY, width=6)
    d.chord((60, 6, 200, 120), 180, 360, fill=(60, 44, 40), outline=NAVY, width=6)
    d.ellipse((100, 76, 114, 92), fill=NAVY); d.ellipse((146, 76, 160, 92), fill=NAVY)
    d.arc((108, 92, 152, 124), 20, 160, fill=NAVY, width=5)
    return im


def scene_recipe(img, t):
    img.alpha_composite(bg_split())
    L = Image.new("RGBA", (W, H), (255, 255, 255, 0)); ImageDraw.Draw(L).rectangle((0, 0, W, H), fill=(255, 250, 240, 225))
    img.alpha_composite(L)
    a = pop(t, 8.0, 0.4)
    paste_c(img, recipe_card(), W / 2, 680, a, tag="kartu resep")
    # Aru menyodorkan kaleng dingin berembun ke tamu
    hgt = 420
    im = aru_h(hgt, True); r = hgt / ARU.height
    k = eout((t - 8.3) / 0.5)
    cx = 300; bottom = 1560 + 5 * math.sin(t * 8)
    x0 = cx - im.width / 2; y0 = bottom - hgt
    img.alpha_composite(im, (int(x0), int(y0)))
    track("aru", im.width, x0, x0 + im.width)
    hx = (ARU.width - 50) * r + x0 + 140 * k; hy = 365 * r + y0 + 30 * k
    paste_c(img, guest_img(), 800, 1560 - 190, 1.0)
    track("tamu", 260, 670, 930)
    paste_c(img, can_img(86, cold=True), hx, hy - 20, 1.0, -8 * k)
    source(img, ["SINTEF, 19 Des 2025 · es 3 : garam 1 = −18°C", "(Engineering ToolBox)"], y0=1640, a=fade(t, 8.2))


# ---------- adegan 7: penutup ----------
@lru_cache(None)
def final_pill():
    f = F("pb", 74)
    w, h = 800, 270
    L = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((8, 10, w + 8, h + 10), 50, fill=(20, 33, 91, 60))
    d.rounded_rectangle((0, 0, w, h), 50, fill=NAVY)
    rich_line(d, w / 2, 82, [("Tim ", False), ("KULKAS", True), (" atau", False)], f, on_dark=True)
    rich_line(d, w / 2, 190, [("tim ", False), ("ES + GARAM", True), ("?", False)], f, on_dark=True)
    L.info["nw"] = w
    return L


@lru_cache(None)
def follow_pill():
    f1 = F("pb", 44); f2 = F("pb", 44)
    l1 = "Follow, besok: kenapa hari"; l2a = "JUMAT"; l2b = " namanya Jumat?"
    w = int(max(f1.getlength(l1), f2.getlength(l2a + l2b)) + 70); h = 150
    L = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((8, 10, w + 8, h + 10), 36, fill=(20, 33, 91, 55))
    d.rounded_rectangle((0, 0, w, h), 36, fill=TEAL, outline=NAVY, width=5)
    text_c(d, (w / 2, 46), l1, f1, WHITE)
    rich_line(d, w / 2, 106, [(l2a, True), (l2b, False)], f2, on_dark=True)
    L.info["nw"] = w
    return L


def scene_end(img, t):
    img.alpha_composite(bg_split())
    # hasil akhir tetap terlihat samar (tanpa adegan baru)
    paste_c(img, pill("KULKAS", NAVY, WHITE, 60), LX, 330)
    paste_c(img, pill("ES + GARAM", NAVY, YEL, 52, 26), RX, 330)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(L).rectangle((0, 0, W, H), fill=(255, 250, 240, 170))
    img.alpha_composite(L)
    paste_c(img, final_pill(), W / 2, 720 + 4 * math.sin(t * 4), pop(t, 10.5, 0.4), tag="pill tim")
    paste_c(img, follow_pill(), W / 2, 1080, pop(t, 10.65, 0.35), tag="pill follow")
    paste_c(img, logo_w(260), W / 2, 1690, 0.9 + 0.1 * back((t - 10.5) / 0.3), 0, fade(t, 10.5, 0.3), tag="logo")


def frame(t):
    BOXES.clear()
    k = scene_of(t)
    if k == 0:
        img = bg_room().copy(); scene0(img, t)
    elif k == 5:
        img = Image.new("RGBA", (W, H), CREAM); scene_recipe(img, t)
    elif k == 6:
        img = Image.new("RGBA", (W, H), CREAM); scene_end(img, t)
    else:
        img = Image.new("RGBA", (W, H), CREAM); split_scene(img, t)
    # whoosh-zoom kecil di awal adegan
    ts = t - SC[k]
    if k > 0 and ts < 0.25:
        s = 1.04 - 0.04 * eout(ts / 0.25)
        big = img.resize((int(W * s), int(H * s)), Image.BICUBIC)
        img = big.crop(((big.width - W) // 2, (big.height - H) // 2, (big.width - W) // 2 + W, (big.height - H) // 2 + H))
    return img.convert("RGB")


def check(step=0.1):
    bad = {}; widest = {}
    for j in range(int(TOTAL / step) + 1):
        t = min(TOTAL - 0.01, j * step)
        frame(t)
        for tag, nw, x0, x1 in BOXES:
            widest[tag] = max(widest.get(tag, 0), nw)
            if tag in ("aru", "tamu", "kulkas", "baskom", "termo kiri", "termo kanan", "bel", "tingtong"):
                continue   # ilustrasi boleh dekat tepi
            if nw > MAXW + 0.5 or x0 < XMIN - 0.5 or x1 > XMAX + 0.5:
                bad.setdefault(tag, []).append((round(t, 1), round(nw), round(x0), round(x1)))
    for tag in sorted(widest, key=lambda k: -widest[k]):
        print(f"{tag:22s} lebar maks {widest[tag]:6.0f}")
    if bad:
        for tag, v in bad.items(): print("PELANGGARAN", tag, len(v), v[:4])
        sys.exit(1)
    print("OK: teks/kartu <= 800 px dan di dalam x 130..950")


def events():
    ev = [{"t": 0.05, "sfx": "tingtong", "gain": 0.55}]
    ev += [{"t": SC[k] - 0.12, "sfx": "whoosh", "gain": 0.3} for k in range(1, NS)]
    ev.append({"t": 0.45, "sfx": "pop", "gain": 0.3})               # Aru menoleh kaget
    ev.append({"t": 1.25, "sfx": "cring", "gain": 0.35})            # kaleng masuk es
    ev.append({"t": T_UI, "sfx": "pop", "gain": 0.3})
    tt = T_UI + 0.25
    while tt < T_PAY - 0.05:                                         # tik-tik timer
        ev.append({"t": round(tt, 3), "sfx": "tik", "gain": 0.28}); tt += 0.25
    ev.append({"t": 2.05, "sfx": "pop", "gain": 0.26})
    ev.append({"t": 4.05, "sfx": "pop", "gain": 0.26})
    ev.append({"t": T_PAY, "sfx": "cring", "gain": 0.55})           # "2,5 MENIT" + cring!
    ev.append({"t": T_PAY + 0.02, "sfx": "ding", "gain": 0.3})
    ev.append({"t": T_10J, "sfx": "ding", "gain": 0.25})
    ev.append({"t": 8.0, "sfx": "pop", "gain": 0.28})
    ev.append({"t": 8.6, "sfx": "cring", "gain": 0.3})              # kaleng dingin disodorkan
    ev.append({"t": 10.5, "sfx": "pop", "gain": 0.28})
    ev.append({"t": 10.65, "sfx": "klik", "gain": 0.3})
    json.dump(sorted(ev, key=lambda e: e["t"]), open("events.json", "w"), indent=1)
    print(len(ev), "events")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "events":
        events()
    elif cmd == "check":
        check()
    elif cmd == "stills":
        ts = [float(x) for x in sys.argv[2].split(",")]
        ims = []
        for tt in ts:
            im = frame(tt); im.save(f"still_{tt:.2f}.png"); ims.append(im.resize((360, 640)))
        cols_ = min(6, len(ims)); rows = math.ceil(len(ims) / cols_)
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

"""ARN-41 Mana Lebih Hemat? #5 (ojol saat hujan) -- sampel gaya frame 0 (gerbang pilih gaya).

Pemakaian (dari folder pagi/):
  python3 render_gaya_frame0.py            -> 3 PNG 1080x1920 (gaya1 Flat 2D, gaya2 Malam hujan, gaya3 Polaroid)
  python3 render_gaya_frame0.py 2.0        -> sama, tapi keadaan dtk 2.0 (counter sudah bergerak, cek still)

Struktur dipakai ulang untuk render penuh: frame(style, t) mengembalikan PIL Image; counter
Rp22.400 -> Rp30.000 digerakkan oleh counter_value(t) (frame 0 = Rp22.400, naik dtk 1,6-2,6).
Aru = assets/maskot/aru-syal-bendera.svg (PRB-18) yang diubah: basah, alis cemas, tangan kanan memegang HP besar.
Tanpa logo / label seri / progress bar di dtk 0-3 (PRB-34/46). Area aman x 130..950 (PRB-41).
"""
import math, os, subprocess, sys, tempfile
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
GF = "/usr/share/fonts/truetype/google-fonts/"
SAFE_X = 130

NAVY = (20, 33, 91); TEAL = (18, 194, 176); YEL = (255, 184, 0); WHITE = (255, 255, 255)
CREAM = (255, 246, 232); BROWN = (92, 64, 40); GREY_T = (122, 114, 102); RED = (224, 82, 63)
RAIN_L = (150, 176, 214)


@lru_cache(None)
def F(name, size):
    if name == "pb": return ImageFont.truetype(GF + "Poppins-Bold.ttf", size)
    if name == "pm": return ImageFont.truetype(GF + "Poppins-Medium.ttf", size)
    if name == "lb":
        f = ImageFont.truetype(GF + "Lora-Variable.ttf", size); f.set_variation_by_name("Bold"); return f
    if name == "cb": return ImageFont.truetype("/usr/share/fonts/X11/Type1/c0583bt_.pfb", size)
    raise KeyError(name)


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)


# ---------- counter (dtk ~2 wajib bergerak, PRB-29/36/46) ----------
C0, C1, CT0, CT1 = 22400, 30000, 1.6, 2.6
def counter_value(t):
    v = C0 + (C1 - C0) * eio((t - CT0) / (CT1 - CT0))
    return int(round(v / 100.0) * 100)
def rp(v): return "Rp" + f"{v:,}".replace(",", ".")


# ---------- Aru basah + HP besar (SVG, viewBox 0 0 380 430) ----------
ARU_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 380 430">
<g transform="translate(10,10)">
<rect x="116" y="296" width="28" height="62" rx="12" fill="#55525E" stroke="#14215B" stroke-width="6"/>
<rect x="156" y="296" width="28" height="62" rx="12" fill="#55525E" stroke="#14215B" stroke-width="6"/>
<ellipse cx="126" cy="364" rx="26" ry="14" fill="#FFB800" stroke="#14215B" stroke-width="6"/>
<ellipse cx="174" cy="364" rx="26" ry="14" fill="#FFB800" stroke="#14215B" stroke-width="6"/>
<path d="M108 236 Q72 214 68 178" fill="none" stroke="#14215B" stroke-width="28" stroke-linecap="round"/>
<path d="M108 236 Q72 214 68 178" fill="none" stroke="#FFD3B0" stroke-width="16" stroke-linecap="round"/>
<rect x="62" y="140" width="11" height="30" rx="5.5" fill="#FFD3B0" stroke="#14215B" stroke-width="5"/>
<circle cx="68" cy="176" r="14" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<path d="M104 214 Q100 300 112 312 L188 312 Q200 300 196 214 Q150 196 104 214 Z" fill="#14215B" stroke="#14215B" stroke-width="6" stroke-linejoin="round"/>
<path d="M120 250 q4 10 0 18 M168 262 q4 10 0 18 M140 286 q4 9 0 16" stroke="#3A4C9A" stroke-width="5" fill="none" stroke-linecap="round"/>
<circle cx="74" cy="142" r="15" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<circle cx="226" cy="142" r="15" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<circle cx="150" cy="136" r="80" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<path d="M92 92 Q118 62 160 58" fill="none" stroke="#FFFFFF" stroke-opacity="0.75" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="112" cy="160" rx="13" ry="8" fill="#FFB08A"/>
<ellipse cx="188" cy="160" rx="13" ry="8" fill="#FFB08A"/>
<path d="M108 112 L138 102" fill="none" stroke="#14215B" stroke-width="7" stroke-linecap="round"/>
<path d="M162 102 L192 112" fill="none" stroke="#14215B" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="124" cy="136" rx="10" ry="13" fill="#14215B"/>
<ellipse cx="176" cy="136" rx="10" ry="13" fill="#14215B"/>
<circle cx="127" cy="131" r="3.5" fill="#FFFFFF"/>
<circle cx="179" cy="131" r="3.5" fill="#FFFFFF"/>
<path d="M136 182 Q150 170 164 182 Q150 192 136 182 Z" fill="#7A2E3A" stroke="#14215B" stroke-width="5" stroke-linejoin="round"/>
<rect x="94" y="198" width="112" height="28" rx="14" fill="#12C2B0" stroke="#14215B" stroke-width="6"/>
<polygon points="104,206 56,224 64,248 110,230" fill="#12C2B0" stroke="#14215B" stroke-width="5" stroke-linejoin="round"/>
<polygon points="102,234 60,250 68,274 106,260" fill="#FFB800" stroke="#14215B" stroke-width="5" stroke-linejoin="round"/>
{drops}
<path d="M192 236 Q228 252 236 226" fill="none" stroke="#14215B" stroke-width="28" stroke-linecap="round"/>
<path d="M192 236 Q228 252 236 226" fill="none" stroke="#FFD3B0" stroke-width="16" stroke-linecap="round"/>
<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="22" fill="#14215B"/>
<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="12" fill="{scr}"/>
<rect x="{sx}" y="{sy}" width="{sw}" height="30" rx="12" fill="#12C2B0"/>
<rect x="{sx}" y="{sy2}" width="{sw}" height="12" fill="#12C2B0"/>
<path d="M{mx0} {my0} C {mx1} {my1}, {mx2} {my2}, {mx3} {my3}" fill="none" stroke="#FFB800" stroke-width="5" stroke-dasharray="9 7" stroke-linecap="round"/>
<circle cx="{mx0}" cy="{my0}" r="6" fill="#14215B"/>
<circle cx="{mx3}" cy="{my3}" r="7" fill="#E0523F"/>
{bike}
<line x1="{nx0}" y1="{ny}" x2="{nx1}" y2="{ny}" stroke="#14215B" stroke-opacity="0.12" stroke-width="2"/>
<circle cx="{hx}" cy="{hy}" r="14" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<path d="M{px} {wy} q-6 14 0 26" stroke="#9FC3EE" stroke-width="5" fill="none" stroke-linecap="round"/>
</g></svg>"""

# HP (koordinat viewBox, sebelum translate 10,10)
PX, PY, PW_, PH_ = 214, 70, 150, 300
SX, SY, SW, SH = PX + 9, PY + 22, PW_ - 18, PH_ - 40


def drop_path(x, y, s=1.0, col="#7FB2EE"):
    return (f'<path d="M{x} {y - 12*s} Q{x + 8*s} {y} {x} {y + 6*s} Q{x - 8*s} {y} {x} {y - 12*s} Z" '
            f'fill="{col}" stroke="#14215B" stroke-width="2.5"/>')


def bike_svg(cx, cy, s=1.0):
    # motor kecil di peta (ikon generik, tanpa merek aplikasi)
    return (f'<g transform="translate({cx},{cy}) scale({s})">'
            '<circle cx="-14" cy="6" r="7" fill="none" stroke="#14215B" stroke-width="4"/>'
            '<circle cx="14" cy="6" r="7" fill="none" stroke="#14215B" stroke-width="4"/>'
            '<path d="M-14 6 L-2 -4 L10 -4 L14 6" fill="none" stroke="#14215B" stroke-width="4" stroke-linejoin="round"/>'
            '<path d="M6 -4 L9 -12 L15 -12" fill="none" stroke="#14215B" stroke-width="4" stroke-linecap="round"/>'
            '<circle cx="-2" cy="-14" r="6" fill="#12C2B0" stroke="#14215B" stroke-width="3"/></g>')


@lru_cache(None)
def aru_phone(scale, screen="#F4F7FB"):
    """render Aru basah + HP (layar tanpa angka; angka counter digambar PIL agar bisa bergerak)."""
    drops = "".join([drop_path(104, 62, 1.0), drop_path(196, 70, 0.9), drop_path(232, 112, 0.8),
                     drop_path(78, 112, 0.8), drop_path(150, 44, 0.8)])
    mx0, my0 = SX + 22, SY + SH - 22
    mx3, my3 = SX + SW - 22, SY + 172
    svg = ARU_SVG.format(
        w=int(380 * scale), h=int(430 * scale), drops=drops,
        px=PX, py=PY, pw=PW_, ph=PH_, sx=SX, sy=SY, sw=SW, sh=SH, sy2=SY + 18, scr=screen,
        mx0=mx0, my0=my0, mx1=SX + 30, my1=SY + 190, mx2=SX + SW - 40, my2=SY + 250, mx3=mx3, my3=my3,
        bike=bike_svg(SX + SW / 2 - 6, SY + 214, 1.0),
        nx0=SX + 12, nx1=SX + SW - 12, ny=SY + 150,
        hx=PX + 4, hy=PY + 168, wy=PY + 200)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "a.svg"); o = os.path.join(td, "a.png")
        open(p, "w").write(svg)
        subprocess.run(["rsvg-convert", "-o", o, p], check=True)
        return Image.open(o).convert("RGBA").copy()


def screen_xy(ox, oy, scale, vx, vy):
    return ox + (vx + 10) * scale, oy + (vy + 10) * scale


def draw_counter(img, ox, oy, scale, t, dark=False):
    """angka tarif di layar HP: frame 0 = Rp22.400, naik ke Rp30.000 di dtk 1,6-2,6."""
    d = ImageDraw.Draw(img)
    cx, cy = screen_xy(ox, oy, scale, SX + SW / 2, SY + 112)
    v = counter_value(t)
    hot = v > C0
    f = F("pb", int(31 * scale))
    s = rp(v)
    while f.getlength(s) > (SW - 14) * scale:
        f = F("pb", f.size - 2)
    d.text((cx, cy), s, font=f, fill=RED if hot else NAVY, anchor="mm")
    # label kecil "tarif" (bagian UI, bukan teks layar utama) di bar teal
    for k in (-1, 0, 1):  # titik UI di bar (tanpa teks / merek aplikasi)
        lx, ly = screen_xy(ox, oy, scale, SX + SW / 2 + 12 * k, SY + 14)
        r = 2.6 * scale; d.ellipse((lx - r, ly - r, lx + r, ly + r), fill=WHITE)
    if hot:  # panah naik + sumber kecil muncul bersama counter (dtk ~2)
        ax, ay = screen_xy(ox, oy, scale, SX + SW / 2, SY + 80)
        a = clamp((t - CT0) / 0.3)
        d.polygon([(ax, ay - 22 * a), (ax - 20 * a, ay + 8 * a), (ax + 20 * a, ay + 8 * a)], fill=RED)


def rain(img, t, n=90, col=RAIN_L, alpha=150, seed=7, length=60, width=4):
    L = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    import random
    r = random.Random(seed)
    for _ in range(n):
        x = r.uniform(-100, W + 100); y0 = r.uniform(0, H); sp = r.uniform(900, 1300)
        y = (y0 + sp * t) % (H + 200) - 100
        x2 = x - 0.25 * length
        d.line([(x, y), (x2, y + length)], fill=col + (alpha,), width=width)
    img.alpha_composite(L)


# ---------- judul & subtitle ----------
def pills(img, words, y, size=76, gap=16, keyword="MAHAL", dark=False):
    """judul gaya kopi #4: kotak per kata, kata kunci kuning. words = list baris."""
    d = ImageDraw.Draw(img); f = F("pb", size); padx = 26; hh = size + 34
    for row, line in enumerate(words):
        ws = [f.getlength(w) + 2 * padx for w in line]
        tot = sum(ws) + gap * (len(ws) - 1)
        assert tot <= W - 2 * SAFE_X, (line, tot)
        x = (W - tot) / 2; yy = y + row * (hh + 18)
        for w, ww in zip(line, ws):
            key = w.strip("?") == keyword
            d.rounded_rectangle((x + 7, yy + 8, x + ww + 7, yy + hh + 8), 14, fill=(0, 0, 0, 40))
            d.rounded_rectangle((x, yy, x + ww, yy + hh), 14, fill=YEL if key else NAVY)
            d.text((x + ww / 2, yy + hh / 2 + 2), w, font=f, fill=NAVY if key else WHITE, anchor="mm")
            x += ww + gap


def sub_poppins(img, words, keys=(), y=1560, size=70):
    """subtitle gaya Flat 2D #4 (kotak navy, kata kunci kuning), 1 baris."""
    d = ImageDraw.Draw(img); f = F("pb", size); padx = 26; hh = size + 30; gap = 14
    ws = [f.getlength(w) + 2 * padx for w in words]
    tot = sum(ws) + gap * (len(ws) - 1); assert tot <= W - 300
    x = (W - tot) / 2
    for w, ww in zip(words, ws):
        key = w in keys
        d.rounded_rectangle((x + 7, y + 8, x + ww + 7, y + hh + 8), 14, fill=(0, 0, 0, 40))
        d.rounded_rectangle((x, y, x + ww, y + hh), 14, fill=YEL if key else NAVY)
        d.text((x + ww / 2, y + hh / 2 + 2), w, font=f, fill=NAVY if key else WHITE, anchor="mm")
        x += ww + gap


def sub_lora(img, words, keys=(), y=1540, size=64):
    """subtitle gaya Polaroid/ARN-24 (kotak krem, Lora Bold), 1 baris."""
    d = ImageDraw.Draw(img); f = F("lb", size); pad = 24; gap = 14
    ws = [f.getlength(w) + 2 * pad for w in words]
    tot = sum(ws) + gap * (len(ws) - 1); assert tot <= W - 300
    x = (W - tot) / 2
    for w, ww in zip(words, ws):
        key = w in keys
        d.rounded_rectangle((x + 6, y + 6, x + ww + 6, y + 102), 14, fill=(0, 0, 0, 45))
        d.rounded_rectangle((x, y, x + ww, y + 96), 14, fill=YEL if key else CREAM)
        d.text((x + ww / 2, y + 48), w, font=f, fill=NAVY if key else BROWN, anchor="mm")
        x += ww + gap


def title_big(img, y, size=96, dark=True):
    """judul besar 2 baris: SEBERAPA / MAHAL HUJAN? (MAHAL kuning), outline."""
    d = ImageDraw.Draw(img); f = F("pb", size)
    body = WHITE if dark else NAVY; stroke = NAVY if dark else WHITE
    def line(yy, parts):
        tw = sum(f.getlength(p) for p, _ in parts)
        assert tw <= W - 2 * SAFE_X, tw
        x = (W - tw) / 2
        for p, col in parts:
            d.text((x, yy), p, font=f, fill=col, anchor="ls", stroke_width=8,
                   stroke_fill=NAVY if col == YEL else stroke)
            x += f.getlength(p)
    line(y, [("SEBERAPA", body)])
    line(y + int(size * 1.12), [("MAHAL", YEL), (" HUJAN?", body)])


# subtitle frame 0 = potongan VO pertama ("Hujan,") -> total teks layar 4 kata (PRB-34)
SUB0 = (["HUJAN,"], ())


def bob(t): return 7 * math.sin(2 * math.pi * 1.1 * t)
FEET = 388  # dasar sepatu dalam viewBox (setelah translate)
def aru_origin(sc, floor_y, x=-20): return x, floor_y - FEET * sc


# ---------- GAYA 1: Flat 2D latar terang (gaya #4 kopi vs seduh) ----------
def frame_flat(t):
    img = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(img)
    top, bot = (238, 241, 246), (246, 242, 236)
    for y in range(H):
        u = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[j] + (bot[j] - top[j]) * u) for j in range(3)))
    d.ellipse((150, 560, 950, 1360), fill=(220, 238, 243))
    # awan hujan pucat
    for cx, cy, r in ((300, 610, 80), (390, 580, 100), (490, 615, 75)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(205, 214, 228))
    floor = 1440
    d.rectangle((0, floor, W, H), fill=(218, 223, 232))
    d.line([(0, floor), (W, floor)], fill=NAVY, width=5)
    d.ellipse((250, floor - 30, 840, floor + 40), fill=(170, 200, 236))  # genangan
    rain(img, t, n=70, col=(150, 176, 214), alpha=170, seed=3)
    sc = 2.5
    A = aru_phone(sc)
    ox, oy = aru_origin(sc, floor + 12); oy += bob(t)
    img.alpha_composite(A, (int(ox), int(oy)))
    draw_counter(img, ox, oy, sc, t)
    pills(img, [["SEBERAPA", "MAHAL"], ["HUJAN?"]], 290, size=76)
    sub_poppins(img, *SUB0, y=1560)
    return img


# ---------- GAYA 2: Malam hujan (gelap, palet baru) ----------
def frame_night(t):
    img = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(img)
    top, bot = (10, 16, 52), (26, 40, 104)
    for y in range(H):
        u = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[j] + (bot[j] - top[j]) * u) for j in range(3)))
    rain(img, t, n=120, col=(140, 160, 220), alpha=110, seed=11, length=80, width=3)
    floor = 1440
    d = ImageDraw.Draw(img)
    d.rectangle((0, floor, W, H), fill=(14, 22, 62))
    # pantulan aspal basah
    for k in range(6):
        d.line([(200 + k * 60, floor + 30 + k * 18), (880 - k * 40, floor + 30 + k * 18)],
               fill=(60, 80, 150), width=4)
    # cahaya layar HP menerangi Aru
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((330, 620, 1010, 1300), fill=(255, 220, 140, 110))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    sc = 2.5
    A = aru_phone(sc, screen="#FFF6E0")
    ox, oy = aru_origin(sc, floor + 12); oy += bob(t)
    img.alpha_composite(A, (int(ox), int(oy)))
    draw_counter(img, ox, oy, sc, t)
    rain(img, t + 0.37, n=40, col=(190, 205, 245), alpha=150, seed=5, length=70, width=4)
    title_big(img, 385, size=92, dark=True)
    sub_lora(img, ["Hujan,"], y=1560)
    return img


# ---------- GAYA 3: Polaroid (gaya ARN-24, tanpa header/logo di dtk 0-3) ----------
def frame_polaroid(t):
    img = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(img)
    top, bot = (233, 220, 203), (242, 232, 218)
    for y in range(H):
        u = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[j] + (bot[j] - top[j]) * u) for j in range(3)))
    # judul di atas polaroid (navy, MAHAL kuning)
    f = F("pb", 82)
    def line(yy, parts):
        tw = sum(f.getlength(p) for p, _ in parts); x = (W - tw) / 2
        assert tw <= W - 2 * SAFE_X
        for p, col in parts:
            d.text((x, yy), p, font=f, fill=col, anchor="ls", stroke_width=7 if col == YEL else 0, stroke_fill=NAVY)
            x += f.getlength(p)
    line(370, [("SEBERAPA", NAVY)])
    line(370 + 96, [("MAHAL", YEL), (" HUJAN?", NAVY)])
    # foto polaroid
    PWp, PHp = 800, 760
    photo = Image.new("RGBA", (PWp, PHp), (214, 224, 234, 255)); pd = ImageDraw.Draw(photo)
    pd.rectangle((0, 610, PWp, PHp), fill=(170, 180, 196))
    rain(photo, t, n=40, col=(120, 146, 190), alpha=150, seed=9, length=50, width=4)
    sc = 1.75
    A = aru_phone(sc)
    ox, oy = aru_origin(sc, 652, x=75); oy += bob(t)
    photo.alpha_composite(A, (int(ox), int(oy)))
    draw_counter(photo, ox, oy, sc, t)
    PL = Image.new("RGBA", (PWp + 80, PHp + 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(PL)
    ld.rectangle((14, 16, PWp + 80, PHp + 200), fill=(0, 0, 0, 40))
    ld.rectangle((0, 0, PWp + 66, PHp + 184), fill=WHITE)
    PL.alpha_composite(photo, (33, 33))
    # caption mesin ketik: kosong di frame 0 (typewriter mulai dtk 0,25)
    cap = "ongkos ojol pas hujan"; n = int(clamp((t - 0.25) / 1.1) * len(cap))
    ld.text(((PWp + 66) / 2, PHp + 110), cap[:n], font=F("cb", 36), fill=BROWN, anchor="mm")
    PL = PL.rotate(-1.8, Image.BICUBIC, expand=True)
    img.alpha_composite(PL, (int(W / 2 - PL.width / 2), int(1040 - PL.height / 2)))
    tape = Image.new("RGBA", (230, 64), (255, 214, 102, 190)).rotate(-3, Image.BICUBIC, expand=True)
    img.alpha_composite(tape, (int(W / 2 - tape.width / 2), int(1040 - PL.height / 2 - 26)))
    sub_lora(img, ["Hujan,"], y=1575)
    return img


STYLES = [("gaya1", "Flat 2D", frame_flat), ("gaya2", "Malam hujan", frame_night), ("gaya3", "Polaroid", frame_polaroid)]


if __name__ == "__main__":
    t = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    suf = "" if t == 0 else f"_t{t:.1f}"
    for key, name, fn in STYLES:
        out = os.path.join(HERE, f"2026-11-12_pagi_ojol-hujan_{key}{suf}.png")
        fn(t).convert("RGB").save(out)
        print(out, name)

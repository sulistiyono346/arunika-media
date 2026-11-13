"""ARN-45 Hujan deras 1 jam di Jakarta = berapa liter? -- sampel gaya frame 0 (gerbang pilih gaya).

Pemakaian (dari folder sore/):
  python3 render_gaya_hujan.py          -> 3 PNG 1080x1920 (sampel1 Flat 2D, sampel2 Malam hujan, sampel3 Split gelap)
  python3 render_gaya_hujan.py 2.2      -> keadaan dtk 2,2 (counter galon sudah naik, cek still)

Frame 0 (kartu "Untuk Produksi"): Aru di bawah cutaway atap rumah, hujan deras, Aru menengadah kaget;
galon-galon jatuh dan menumpuk di atap. Counter galon 0 -> 38 di muka atap bergerak dtk 1,5-2,5
(PRB-29/36/46). Tanpa logo / label seri / progress bar di dtk 0-3 (PRB-34/46). Area aman x 130..950 (PRB-41).
Teks layar frame 0 = judul "SEBERAPA BANYAK HUJAN SEJAM?" (4 kata, BANYAK kuning) + subtitle VO "HUJAN" = 5 kata.
Tanpa visual korban banjir / genangan dramatis. Helper dipakai ulang dari render_gaya_frame0.py.
"""
import math, os, random, subprocess, sys, tempfile
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter

from render_gaya_frame0 import (F, clamp, eio, rain, sub_poppins, sub_lora, W, H, SAFE_X,
                                NAVY, TEAL, YEL, WHITE, CREAM, BROWN, RED)

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------- counter galon 0 -> 38 (dtk 1,5-2,5) ----------
G0, G1, CT0, CT1 = 0, 38, 1.5, 2.5
def counter_value(t): return int(round(G0 + (G1 - G0) * eio((t - CT0) / (CT1 - CT0))))


# ---------- Aru menengadah kaget, dua tangan terangkat (SVG Aru resmi PRB-18; viewBox 0 0 360 420) ----------
ARU_UP_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 360 420">
<g transform="translate(30,30)">
<rect x="116" y="296" width="28" height="62" rx="12" fill="#55525E" stroke="#14215B" stroke-width="6"/>
<rect x="156" y="296" width="28" height="62" rx="12" fill="#55525E" stroke="#14215B" stroke-width="6"/>
<ellipse cx="126" cy="364" rx="26" ry="14" fill="#FFB800" stroke="#14215B" stroke-width="6"/>
<ellipse cx="174" cy="364" rx="26" ry="14" fill="#FFB800" stroke="#14215B" stroke-width="6"/>
<path d="M106 226 Q52 206 44 142" fill="none" stroke="#14215B" stroke-width="28" stroke-linecap="round"/>
<path d="M106 226 Q52 206 44 142" fill="none" stroke="#FFD3B0" stroke-width="16" stroke-linecap="round"/>
<circle cx="44" cy="136" r="15" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<path d="M194 226 Q248 206 256 142" fill="none" stroke="#14215B" stroke-width="28" stroke-linecap="round"/>
<path d="M194 226 Q248 206 256 142" fill="none" stroke="#FFD3B0" stroke-width="16" stroke-linecap="round"/>
<circle cx="256" cy="136" r="15" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<path d="M104 214 Q100 300 112 312 L188 312 Q200 300 196 214 Q150 196 104 214 Z" fill="#14215B" stroke="#14215B" stroke-width="6" stroke-linejoin="round"/>
<circle cx="74" cy="142" r="15" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<circle cx="226" cy="142" r="15" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<circle cx="150" cy="136" r="80" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<path d="M92 92 Q118 62 160 58" fill="none" stroke="#FFFFFF" stroke-opacity="0.7" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="112" cy="166" rx="13" ry="8" fill="#FFB08A"/>
<ellipse cx="188" cy="166" rx="13" ry="8" fill="#FFB08A"/>
<path d="M106 100 Q122 84 138 94" fill="none" stroke="#14215B" stroke-width="7" stroke-linecap="round"/>
<path d="M162 94 Q178 84 194 100" fill="none" stroke="#14215B" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="124" cy="128" rx="11" ry="14" fill="#FFFFFF" stroke="#14215B" stroke-width="4"/>
<ellipse cx="176" cy="128" rx="11" ry="14" fill="#FFFFFF" stroke="#14215B" stroke-width="4"/>
<circle cx="124" cy="121" r="6.5" fill="#14215B"/>
<circle cx="176" cy="121" r="6.5" fill="#14215B"/>
<ellipse cx="150" cy="186" rx="13" ry="16" fill="#7A2E3A" stroke="#14215B" stroke-width="5"/>
<path d="M214 92 q8 14 0 24 q-8 -10 0 -24 Z" fill="#9FD0F5" stroke="#14215B" stroke-width="3"/>
<path d="M86 96 q7 12 0 21 q-7 -9 0 -21 Z" fill="#9FD0F5" stroke="#14215B" stroke-width="3"/>
<rect x="94" y="198" width="112" height="28" rx="14" fill="#12C2B0" stroke="#14215B" stroke-width="6"/>
<polygon points="190,206 252,222 244,246 184,231" fill="#12C2B0" stroke="#14215B" stroke-width="5" stroke-linejoin="round"/>
<polygon points="184,236 232,248 224,272 180,261" fill="#FFB800" stroke="#14215B" stroke-width="5" stroke-linejoin="round"/>
</g></svg>"""
VB_W, VB_H, FEET = 360, 420, 378 + 30


@lru_cache(None)
def aru_up(scale):
    svg = ARU_UP_SVG.format(w=int(VB_W * scale), h=int(VB_H * scale))
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "a.svg"); o = os.path.join(td, "a.png")
        open(p, "w").write(svg)
        subprocess.run(["rsvg-convert", "-o", o, p], check=True)
        return Image.open(o).convert("RGBA").copy()


@lru_cache(None)
def galon(h=96, dark=False):
    """galon air 19 L (ikon generik, tanpa merek): badan biru muda transparan, tutup biru."""
    w = int(h * 0.72); im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    body = (176, 220, 246, 255) if not dark else (120, 170, 230, 255)
    s = h / 96
    d.rounded_rectangle((4, 26 * s, w + 4, h + 4), int(14 * s), fill=body, outline=NAVY, width=max(3, int(4 * s)))
    d.rounded_rectangle((w / 2 + 4 - 12 * s, 6 * s, w / 2 + 4 + 12 * s, 30 * s), int(4 * s), fill=(30, 110, 210),
                        outline=NAVY, width=max(2, int(3 * s)))
    for k in (52, 74):
        d.line([(10 * s, k * s), (w - 2 * s, k * s)], fill=(120, 170, 220), width=max(2, int(3 * s)))
    d.line([(14 * s, 36 * s), (14 * s, 86 * s)], fill=(255, 255, 255, 200), width=max(3, int(5 * s)))
    return im


def paste_c(dst, im, cx, cy, angle=0.0):
    if abs(angle) > 0.05: im = im.rotate(angle, Image.BICUBIC, expand=True)
    dst.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def bob(t): return 6 * math.sin(2 * math.pi * 1.1 * t)


# ---------- rumah cutaway: atap segitiga + ruang dalam, galon menumpuk di lereng atap ----------
APEX = (540, 650); EAVE_L = (150, 930); EAVE_R = (930, 930)


def slope_y(x):
    """y permukaan atap di x (lereng kiri / kanan)."""
    ax, ay = APEX
    if x <= ax: return ay + (ax - x) / (ax - EAVE_L[0]) * (EAVE_L[1] - ay)
    return ay + (x - ax) / (EAVE_R[0] - ax) * (EAVE_R[1] - ay)


# slot galon di atap (urutan menumpuk): baris bawah dulu, dekat talang
SLOTS = [(250, 0), (830, 0), (330, 0), (750, 0), (410, 0), (670, 0), (250, 1), (830, 1), (330, 1), (750, 1),
         (490, 0), (590, 0), (410, 1), (670, 1), (250, 2), (830, 2)]


def house(img, t, roof=(232, 104, 72), wall=(255, 246, 232), room=(246, 233, 210), dark=False, gh=92):
    d = ImageDraw.Draw(img)
    ax, ay = APEX; L, R = EAVE_L, EAVE_R
    floor = 1440
    # ruang dalam (cutaway: dinding depan dibuka)
    d.rectangle((200, 930, 880, floor), fill=room, outline=NAVY, width=6)
    d.rectangle((200, 930, 880, 960), fill=tuple(max(0, c - 30) for c in room))          # plafon
    d.rectangle((230, 1060, 360, 1220), fill=(150, 200, 236) if not dark else (255, 214, 120),
                outline=NAVY, width=5)                                                 # jendela
    d.line([(295, 1060), (295, 1220)], fill=NAVY, width=4); d.line([(230, 1140), (360, 1140)], fill=NAVY, width=4)
    # gable (muka atap) + counter
    d.polygon([(ax, ay + 40), (L[0] + 70, L[1]), (R[0] - 70, R[1])], fill=wall)
    # atap tebal dua lereng
    th = 46
    for (x0, y0) in (L, R):
        d.polygon([(ax, ay - th), (x0 + (-24 if x0 < ax else 24), y0 - th + 6), (x0, y0 + 10), (ax, ay + 18)],
                  fill=roof, outline=NAVY)
    d.line([(L[0] - 24, L[1] - th + 6), (ax, ay - th), (R[0] + 24, R[1] - th + 6)], fill=NAVY, width=7, joint="curve")
    d.line([(L[0], L[1] + 10), (ax, ay + 18), (R[0], R[1] + 10)], fill=NAVY, width=6, joint="curve")
    d.line([(L[0] - 24, L[1] - th + 6), (L[0], L[1] + 10)], fill=NAVY, width=6)
    d.line([(R[0] + 24, R[1] - th + 6), (R[0], R[1] + 10)], fill=NAVY, width=6)
    # garis genteng
    for k in range(1, 6):
        u = k / 6
        for (x0, y0) in (L, R):
            xa = ax + (x0 - ax) * u; ya = ay + (y0 - ay) * u
            d.line([(xa, ya - th + 6 * u), (xa + (6 if x0 < ax else -6), ya + 14)], fill=(190, 78, 52), width=5)
    # talang
    for x0 in (L[0], R[0]):
        d.rounded_rectangle((x0 - 40, L[1] + 6, x0 + 40, L[1] + 30), 8, fill=(150, 156, 170), outline=NAVY, width=4)
    # galon menumpuk (jumlah ikut counter) + galon jatuh
    n = int(round(counter_value(t) / G1 * len(SLOTS)))
    n = max(n, 2)                       # frame 0: dua galon baru mendarat (counter belum jalan)
    G = galon(gh, dark)
    for i, (x, row) in enumerate(SLOTS[:n]):
        y = slope_y(x) - th - G.height / 2 + 8 - row * (G.height - 12)
        paste_c(img, G, x, y, angle=(-6 if x < ax else 6))
    r = random.Random(4)
    for k in range(4):                  # galon jatuh dari langit
        x = [300, 700, 460, 820][k]; ph = k * 0.27
        u = (t * 0.9 + ph) % 1.0
        y = 610 + u * (slope_y(x) - 610 - th - 50)
        paste_c(img, G, x, y, angle=r.uniform(-25, 25) + 120 * u)
    return floor


def draw_counter(img, t, dark=False):
    """angka besar di muka atap: frame 0 = 0, naik ke 38 di dtk 1,5-2,5 (+ ikon galon & panah naik)."""
    d = ImageDraw.Draw(img); v = counter_value(t); hot = v > 0
    cx, cy = APEX[0] + 10, 840
    s = str(v)
    d.text((cx + 30, cy), s, font=F("pb", 120), fill=RED if hot else NAVY, anchor="mm",
           stroke_width=6, stroke_fill=WHITE)
    tw = F("pb", 120).getlength(s)
    paste_c(img, galon(78, dark), cx + 30 - tw / 2 - 52, cy + 4)
    if hot:
        a = clamp((t - CT0) / 0.3); ax = cx + 30 + tw / 2 + 36
        d.polygon([(ax, cy - 26 * a), (ax - 20 * a, cy + 8 * a), (ax + 20 * a, cy + 8 * a)], fill=RED)


def aru(img, t, floor, sc=1.45):
    A = aru_up(sc)
    ox = 560 - A.width / 2; oy = floor - FEET * sc + bob(t)
    img.alpha_composite(A, (int(ox), int(oy)))


def vgrad(img, top, bot):
    d = ImageDraw.Draw(img)
    for y in range(H):
        u = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[j] + (bot[j] - top[j]) * u) for j in range(3)))


def pills2(img, rows, y, size=76, keyword="BANYAK"):
    """judul pill (gaya Flat 2D): kotak navy per kata, kata kunci kuning."""
    d = ImageDraw.Draw(img); f = F("pb", size); padx, gap = 26, 16; hh = size + 34
    for r_, line in enumerate(rows):
        ws = [f.getlength(w) + 2 * padx for w in line]; tot = sum(ws) + gap * (len(ws) - 1)
        assert tot <= W - 2 * SAFE_X, (line, tot)
        x = (W - tot) / 2; yy = y + r_ * (hh + 18)
        for w, ww in zip(line, ws):
            key = w.strip("?") == keyword
            d.rounded_rectangle((x + 7, yy + 8, x + ww + 7, yy + hh + 8), 14, fill=(0, 0, 0, 40))
            d.rounded_rectangle((x, yy, x + ww, yy + hh), 14, fill=YEL if key else NAVY)
            d.text((x + ww / 2, yy + hh / 2 + 2), w, font=f, fill=NAVY if key else WHITE, anchor="mm")
            x += ww + gap


def title_outline(img, y, size, body, stroke):
    d = ImageDraw.Draw(img); f = F("pb", size)
    def line(yy, parts):
        tw = sum(f.getlength(p) for p, _ in parts); assert tw <= W - 2 * SAFE_X, tw
        x = (W - tw) / 2
        for p, col in parts:
            d.text((x, yy), p, font=f, fill=col, anchor="ls", stroke_width=8,
                   stroke_fill=NAVY if col == YEL else stroke)
            x += f.getlength(p)
    line(y, [("SEBERAPA ", body), ("BANYAK", YEL)])
    line(y + int(size * 1.15), [("HUJAN SEJAM?", body)])


SUB0 = ["HUJAN"]   # potongan VO pertama ("Hujan sejam, ...") -> total teks layar 5 kata


# ---------- SAMPEL 1: Flat 2D latar terang (rekomendasi data) ----------
def frame_flat(t):
    img = Image.new("RGBA", (W, H)); vgrad(img, (226, 234, 244), (240, 242, 246))
    d = ImageDraw.Draw(img)
    for cx, cy, r in ((230, 600, 90), (340, 570, 110), (450, 605, 80), (700, 590, 95), (810, 560, 110)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(200, 210, 226))           # awan hujan pucat
    rain(img, t, n=110, col=(120, 150, 200), alpha=170, seed=3, length=70, width=5)
    floor = house(img, t)
    d = ImageDraw.Draw(img)
    d.rectangle((0, floor, W, H), fill=(214, 222, 232)); d.line([(0, floor), (W, floor)], fill=NAVY, width=5)
    aru(img, t, floor + 8)
    draw_counter(img, t)
    pills2(img, [["SEBERAPA", "BANYAK"], ["HUJAN", "SEJAM?"]], 290, size=72)
    sub_poppins(img, SUB0, y=1560)
    return img


# ---------- SAMPEL 2: Malam hujan (gelap, cocok tema hujan) ----------
def frame_night(t):
    img = Image.new("RGBA", (W, H)); vgrad(img, (10, 16, 52), (26, 40, 104))
    rain(img, t, n=140, col=(140, 160, 220), alpha=120, seed=11, length=80, width=3)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((180, 900, 900, 1500), fill=(255, 210, 120, 90))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    floor = house(img, t, roof=(170, 70, 60), wall=(214, 206, 196), room=(250, 222, 170), dark=True)
    d = ImageDraw.Draw(img)
    d.rectangle((0, floor, W, H), fill=(14, 22, 62)); d.line([(0, floor), (W, floor)], fill=(60, 80, 150), width=5)
    aru(img, t, floor + 8)
    draw_counter(img, t, dark=True)
    rain(img, t + 0.37, n=50, col=(190, 205, 245), alpha=150, seed=5, length=70, width=4)
    title_outline(img, 400, 84, WHITE, NAVY)
    sub_lora(img, ["Hujan"], y=1560)
    return img


# ---------- SAMPEL 3: Split gelap (belahan diagonal, judul besar) ----------
def frame_split(t):
    img = Image.new("RGBA", (W, H)); vgrad(img, (12, 20, 60), (22, 34, 92))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 1240), (W, 980), (W, H), (0, H)], fill=(8, 13, 40))
    d.line([(0, 1240), (W, 980)], fill=YEL, width=8)
    rain(img, t, n=90, col=(120, 150, 220), alpha=110, seed=8, length=80, width=3)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((220, 560, 860, 1100), fill=(120, 190, 255, 90))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(100)))
    floor = house(img, t, roof=(18, 194, 176), wall=(232, 238, 248), room=(244, 236, 220))
    d = ImageDraw.Draw(img)
    d.rectangle((0, floor, W, H), fill=(8, 13, 40)); d.line([(0, floor), (W, floor)], fill=YEL, width=5)
    aru(img, t, floor + 8)
    draw_counter(img, t)
    title_outline(img, 400, 84, WHITE, NAVY)
    sub_poppins(img, SUB0, y=1580)
    return img


STYLES = [("sampel1", "Flat 2D", frame_flat), ("sampel2", "Malam hujan", frame_night),
          ("sampel3", "Split gelap", frame_split)]


if __name__ == "__main__":
    t = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    suf = "" if t == 0 else f"_t{t:.1f}"
    for key, name, fn in STYLES:
        out = os.path.join(HERE, f"2026-11-13_sore_hujan_{key}{suf}.png")
        fn(t).convert("RGB").save(out)
        print(out, name)

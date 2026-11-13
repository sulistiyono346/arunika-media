"""ARN-44 Mana Lebih Hemat? #6 (emas buyback) -- sampel gaya frame 0 (gerbang pilih gaya).

Pemakaian (dari folder pagi/):
  python3 render_gaya_emas.py          -> 3 PNG 1080x1920 (sampel1 Flat 2D, sampel2 Polaroid, sampel3 Split gelap)
  python3 render_gaya_emas.py 2.2      -> keadaan dtk 2,2 (counter sudah turun, cek still)

Frame 0 (kartu "Untuk Produksi"): Aru memeluk satu keping emas 1 gram ukuran besar, Si Bocor menggigit
sudutnya, koin jatuh. Counter di muka emas Rp2.566.400 -> Rp2.375.000 bergerak di dtk 1,6-2,6 (PRB-29/36/46).
Tanpa logo / label seri / progress bar di dtk 0-3 (PRB-34/46). Area aman x 130..950 (PRB-41).
Teks layar frame 0 = judul "EMAS, KOK LANGSUNG RUGI?" (4 kata, RUGI kuning) + subtitle VO "BELI" = 5 kata.
Helper (F, pills, sub_poppins, sub_lora, rp, eio) dipakai ulang dari render_gaya_frame0.py.
"""
import math, os, subprocess, sys, tempfile
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter

from render_gaya_frame0 import (F, clamp, eio, rp, pills, sub_poppins, sub_lora, W, H, SAFE_X,
                                NAVY, TEAL, YEL, WHITE, CREAM, BROWN, RED)

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD = (245, 190, 60); GOLD_D = (196, 138, 22)

# ---------- counter: harga beli -> harga buyback ----------
C0, C1, CT0, CT1 = 2566400, 2375000, 1.6, 2.6
def counter_value(t):
    v = C0 + (C1 - C0) * eio((t - CT0) / (CT1 - CT0))
    return int(round(v / 100.0) * 100)


# ---------- Aru memeluk emas (SVG Aru resmi tanpa lengan bawaan; viewBox 0 0 360 420) ----------
ARU_GOLD_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 360 420">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#FFE08A"/><stop offset="0.45" stop-color="#F5BE3C"/><stop offset="1" stop-color="#D99A1F"/></linearGradient></defs>
<g transform="translate(30,6)">
<rect x="116" y="296" width="28" height="62" rx="12" fill="#55525E" stroke="#14215B" stroke-width="6"/>
<rect x="156" y="296" width="28" height="62" rx="12" fill="#55525E" stroke="#14215B" stroke-width="6"/>
<ellipse cx="126" cy="364" rx="26" ry="14" fill="#FFB800" stroke="#14215B" stroke-width="6"/>
<ellipse cx="174" cy="364" rx="26" ry="14" fill="#FFB800" stroke="#14215B" stroke-width="6"/>
<path d="M104 214 Q100 300 112 312 L188 312 Q200 300 196 214 Q150 196 104 214 Z" fill="#14215B" stroke="#14215B" stroke-width="6" stroke-linejoin="round"/>
<circle cx="74" cy="142" r="15" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<circle cx="226" cy="142" r="15" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<circle cx="150" cy="136" r="80" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<ellipse cx="112" cy="160" rx="13" ry="8" fill="#FFB08A"/>
<ellipse cx="188" cy="160" rx="13" ry="8" fill="#FFB08A"/>
<path d="M108 112 L138 102" fill="none" stroke="#14215B" stroke-width="7" stroke-linecap="round"/>
<path d="M162 102 L192 112" fill="none" stroke="#14215B" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="124" cy="136" rx="10" ry="13" fill="#14215B"/>
<ellipse cx="176" cy="136" rx="10" ry="13" fill="#14215B"/>
<circle cx="127" cy="131" r="3.5" fill="#FFFFFF"/>
<circle cx="179" cy="131" r="3.5" fill="#FFFFFF"/>
<path d="M136 182 Q150 170 164 182 Q150 192 136 182 Z" fill="#7A2E3A" stroke="#14215B" stroke-width="5" stroke-linejoin="round"/>
<path d="M214 92 q8 14 0 24 q-8 -10 0 -24 Z" fill="#9FD0F5" stroke="#14215B" stroke-width="3"/>
<rect x="94" y="198" width="112" height="28" rx="14" fill="#12C2B0" stroke="#14215B" stroke-width="6"/>
<polygon points="190,206 258,220 250,245 184,231" fill="#12C2B0" stroke="#14215B" stroke-width="5" stroke-linejoin="round"/>
<polygon points="184,236 238,247 230,272 180,261" fill="#FFB800" stroke="#14215B" stroke-width="5" stroke-linejoin="round"/>
<!-- keping emas besar (dipeluk) -->
<path d="M30 240 L270 240 L254 330 L46 330 Z" fill="url(#g)" stroke="#14215B" stroke-width="7" stroke-linejoin="round"/>
<path d="M56 256 L244 256 L232 316 L68 316 Z" fill="none" stroke="#B9800F" stroke-width="4" stroke-linejoin="round" opacity="0.8"/>
<path d="M44 250 L120 250" stroke="#FFF3C4" stroke-width="7" stroke-linecap="round" opacity="0.9"/>
<!-- gigitan Si Bocor di sudut kanan bawah -->
<path d="M262 300 q-14 4 -12 16 q-12 2 -12 14 L258 330 Z" fill="{bg}" stroke="none"/>
<path d="M262 300 q-14 4 -12 16 q-12 2 -12 14" fill="none" stroke="#14215B" stroke-width="5" stroke-linecap="round"/>
<!-- lengan memeluk -->
<path d="M106 222 Q62 218 52 246" fill="none" stroke="#14215B" stroke-width="28" stroke-linecap="round"/>
<path d="M106 222 Q62 218 52 246" fill="none" stroke="#FFD3B0" stroke-width="16" stroke-linecap="round"/>
<circle cx="54" cy="250" r="15" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
<path d="M194 222 Q238 218 248 246" fill="none" stroke="#14215B" stroke-width="28" stroke-linecap="round"/>
<path d="M194 222 Q238 218 248 246" fill="none" stroke="#FFD3B0" stroke-width="16" stroke-linecap="round"/>
<circle cx="246" cy="250" r="15" fill="#FFD3B0" stroke="#14215B" stroke-width="6"/>
</g></svg>"""
VB_W, VB_H, TX, TY = 360, 420, 30, 6
BAR_FACE = (68, 256, 232, 316)  # bingkai dalam muka emas (koordinat sebelum translate)
FEET = 378 + TY


@lru_cache(None)
def aru_gold(scale, bg="#EEF1F6"):
    svg = ARU_GOLD_SVG.format(w=int(VB_W * scale), h=int(VB_H * scale), bg=bg)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "a.svg"); o = os.path.join(td, "a.png")
        open(p, "w").write(svg)
        subprocess.run(["rsvg-convert", "-o", o, p], check=True)
        return Image.open(o).convert("RGBA").copy()


def vb(ox, oy, sc, x, y): return ox + (x + TX) * sc, oy + (y + TY) * sc


def draw_counter(img, ox, oy, sc, t):
    """angka di muka emas: frame 0 = Rp2.566.400, turun ke Rp2.375.000 dtk 1,6-2,6 (merah + panah turun)."""
    d = ImageDraw.Draw(img)
    x0, y0 = vb(ox, oy, sc, BAR_FACE[0], BAR_FACE[1]); x1, y1 = vb(ox, oy, sc, BAR_FACE[2], BAR_FACE[3])
    v = counter_value(t); hot = v < C0
    s = rp(v); size = int(34 * sc); f = F("pb", size)
    while f.getlength(s) > (x1 - x0) - 24: size -= 2; f = F("pb", size)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 2
    d.text((cx, cy), s, font=f, fill=RED if hot else NAVY, anchor="mm")
    if hot:
        a = clamp((t - CT0) / 0.3); ax = x1 + 40 * sc / 2.6; ay = cy
        d.polygon([(ax, ay + 26 * a), (ax - 22 * a, ay - 8 * a), (ax + 22 * a, ay - 8 * a)], fill=RED)


@lru_cache(None)
def bocor_img():
    """Si Bocor (tikus abu, dari tools/render_polaroid.py) tanpa karung, mulut terbuka menggigit."""
    im = Image.new("RGBA", (200, 270), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line([(60, 200), (30, 185), (12, 150), (22, 125)], fill=(244, 163, 184), width=7, joint="curve")
    d.ellipse((40, 110, 190, 250), fill=(142, 138, 156), outline=NAVY, width=5)
    d.ellipse((72, 160, 158, 245), fill=(185, 181, 198))
    d.line([(80, 245), (64, 266)], fill=NAVY, width=6); d.line([(150, 245), (166, 266)], fill=NAVY, width=6)
    for ex in (40, 135):
        d.ellipse((ex, 8, ex + 58, 66), fill=(142, 138, 156), outline=NAVY, width=5)
        d.ellipse((ex + 12, 20, ex + 46, 54), fill=(244, 163, 184))
    d.ellipse((55, 38, 175, 150), fill=(142, 138, 156), outline=NAVY, width=5)
    d.ellipse((86, 78, 101, 97), fill=NAVY); d.ellipse((129, 78, 144, 97), fill=NAVY)
    d.line([(78, 68), (103, 78)], fill=NAVY, width=6); d.line([(152, 68), (127, 78)], fill=NAVY, width=6)
    d.ellipse((107, 100, 123, 114), fill=(196, 52, 140))
    d.ellipse((98, 116, 134, 142), fill=(122, 46, 58), outline=NAVY, width=4)   # mulut menggigit
    d.rectangle((108, 116, 124, 126), fill=WHITE)                              # gigi
    d.line([(116, 116), (116, 126)], fill=NAVY, width=2)
    return im


def coin(r=30):
    im = Image.new("RGBA", (2 * r + 6, 2 * r + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((3, 3, 2 * r + 3, 2 * r + 3), fill=(255, 194, 60), outline=(217, 154, 31), width=4)
    d.text((r + 3, r + 3), "Rp", font=F("pb", int(r * 0.75)), fill=(154, 106, 16), anchor="mm")
    return im


def paste_c(dst, im, cx, cy, scale=1.0, angle=0.0):
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if abs(angle) > 0.05: im = im.rotate(angle, Image.BICUBIC, expand=True)
    dst.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def bob(t): return 7 * math.sin(2 * math.pi * 1.1 * t)


def hero(img, t, sc, cx, floor_y, bg):
    """Aru + emas + Si Bocor di sudut kanan bawah + koin jatuh ("cring!")."""
    A = aru_gold(sc, bg)
    ox = cx - A.width / 2; oy = floor_y - FEET * sc + bob(t)
    img.alpha_composite(A, (int(ox), int(oy)))
    draw_counter(img, ox, oy, sc, t)
    # Si Bocor menggigit sudut kanan bawah emas
    bx, by = vb(ox, oy, sc, 262, 318)
    paste_c(img, bocor_img(), bx + 52 * sc / 2.6, by + 14 * sc / 2.6, 0.78 * sc / 2.6, angle=12)
    # koin jatuh dari sudut tergigit (frame 0 sudah lepas, terus jatuh)
    for k, (dx, ph) in enumerate(((-30, 0.0), (10, 0.45))):
        u = (t * 1.2 + ph) % 1.0
        yy = by + 40 * sc / 2.6 + u * 260 * sc / 2.6
        paste_c(img, coin(int(26 * sc / 2.6)), bx + dx * sc / 2.6, yy, 1.0, angle=u * 200)


def vgrad(img, top, bot):
    d = ImageDraw.Draw(img)
    for y in range(H):
        u = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[j] + (bot[j] - top[j]) * u) for j in range(3)))


SUB0 = ["BELI"]   # potongan VO pertama ("Beli emas, ...") -> total teks layar 5 kata


# ---------- SAMPEL 1: Flat 2D latar terang (gaya #5) ----------
def frame_flat(t):
    img = Image.new("RGBA", (W, H)); vgrad(img, (238, 241, 246), (246, 242, 236))
    d = ImageDraw.Draw(img)
    d.ellipse((140, 600, 940, 1400), fill=(252, 236, 196))          # lingkaran hangat emas
    for k in range(10):                                              # kilau
        a = k * math.pi / 5; r0, r1 = 420, 470
        d.line([(540 + r0 * math.cos(a), 1000 + r0 * math.sin(a)), (540 + r1 * math.cos(a), 1000 + r1 * math.sin(a))],
               fill=(250, 214, 120), width=10)
    floor = 1440
    d.rectangle((0, floor, W, H), fill=(218, 223, 232)); d.line([(0, floor), (W, floor)], fill=NAVY, width=5)
    hero(img, t, 2.45, 540, floor + 10, "#FCECC4")
    pills(img, [["EMAS,", "KOK"], ["LANGSUNG", "RUGI?"]], 290, size=76, keyword="RUGI")
    sub_poppins(img, SUB0, y=1560)
    return img


# ---------- SAMPEL 2: Polaroid (gaya ARN-24, tanpa header/logo di dtk 0-3) ----------
def frame_polaroid(t):
    img = Image.new("RGBA", (W, H)); vgrad(img, (233, 220, 203), (242, 232, 218))
    d = ImageDraw.Draw(img); f = F("pb", 84)
    def line(yy, parts):
        tw = sum(f.getlength(p) for p, _ in parts); x = (W - tw) / 2
        assert tw <= W - 2 * SAFE_X, tw
        for p, col in parts:
            d.text((x, yy), p, font=f, fill=col, anchor="ls", stroke_width=7 if col == YEL else 0, stroke_fill=NAVY)
            x += f.getlength(p)
    line(380, [("EMAS, KOK", NAVY)])
    line(380 + 100, [("LANGSUNG ", NAVY), ("RUGI?", YEL)])
    PWp, PHp = 800, 760
    photo = Image.new("RGBA", (PWp, PHp)); vgrad_p = ImageDraw.Draw(photo)
    for y in range(PHp):
        u = y / PHp; c0, c1 = (250, 238, 210), (240, 222, 190)
        vgrad_p.line([(0, y), (PWp, y)], fill=tuple(int(c0[j] + (c1[j] - c0[j]) * u) for j in range(3)))
    vgrad_p.rectangle((0, 640, PWp, PHp), fill=(200, 184, 160))
    hero(photo, t, 1.85, PWp / 2 - 20, 676, "#F6E8CC")
    PL = Image.new("RGBA", (PWp + 80, PHp + 200), (0, 0, 0, 0)); ld = ImageDraw.Draw(PL)
    ld.rectangle((14, 16, PWp + 80, PHp + 200), fill=(0, 0, 0, 40))
    ld.rectangle((0, 0, PWp + 66, PHp + 184), fill=WHITE)
    PL.alpha_composite(photo, (33, 33))
    cap = "emas antam 1 gram"; n = int(clamp((t - 0.25) / 1.1) * len(cap))   # mesin ketik, kosong di frame 0
    ld.text(((PWp + 66) / 2, PHp + 110), cap[:n], font=F("cb", 36), fill=BROWN, anchor="mm")
    PL = PL.rotate(-1.8, Image.BICUBIC, expand=True)
    img.alpha_composite(PL, (int(W / 2 - PL.width / 2), int(1050 - PL.height / 2)))
    tape = Image.new("RGBA", (230, 64), (255, 214, 102, 190)).rotate(-3, Image.BICUBIC, expand=True)
    img.alpha_composite(tape, (int(W / 2 - tape.width / 2), int(1050 - PL.height / 2 - 26)))
    sub_lora(img, ["Beli"], y=1590)
    return img


# ---------- SAMPEL 3: Split gelap (layar terbelah gelap; gaya reel 11.11) ----------
def frame_split(t):
    img = Image.new("RGBA", (W, H)); vgrad(img, (12, 20, 60), (22, 34, 92))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 1180), (W, 860), (W, H), (0, H)], fill=(8, 13, 40))          # belahan diagonal
    d.line([(0, 1180), (W, 860)], fill=YEL, width=8)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((200, 720, 880, 1400), fill=(255, 196, 70, 120))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(100)))
    hero(img, t, 2.45, 540, 1450, "#161C47")
    # judul besar putih, RUGI kuning (outline navy)
    f = F("pb", 90); d = ImageDraw.Draw(img)
    def line(yy, parts):
        tw = sum(f.getlength(p) for p, _ in parts); x = (W - tw) / 2
        assert tw <= W - 2 * SAFE_X, tw
        for p, col in parts:
            d.text((x, yy), p, font=f, fill=col, anchor="ls", stroke_width=8, stroke_fill=NAVY)
            x += f.getlength(p)
    line(400, [("EMAS, KOK", WHITE)])
    line(400 + 110, [("LANGSUNG ", WHITE), ("RUGI?", YEL)])
    sub_poppins(img, SUB0, y=1580)
    return img


STYLES = [("sampel1", "Flat 2D", frame_flat), ("sampel2", "Polaroid", frame_polaroid),
          ("sampel3", "Split gelap", frame_split)]


if __name__ == "__main__":
    t = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    suf = "" if t == 0 else f"_t{t:.1f}"
    for key, name, fn in STYLES:
        out = os.path.join(HERE, f"2026-11-13_pagi_emas_{key}{suf}.png")
        fn(t).convert("RGB").save(out)
        print(out, name)

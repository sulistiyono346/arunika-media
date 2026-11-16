"""ARN-57 "Kok suaramu di rekaman terdengar aneh?": waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 51,52 dtk), dibagi per suku kata. TANPA Scribe.
Pemetaan segmen -> kalimat dicek dengan hitungan suku kata per segmen (±6-7 suku kata/dtk).
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (sore/build/suara): python3 ../../align_suara.py"""
import json, re

SEGS = [(0.02, 1.24), (1.37, 2.52),                                     # 0-1   hook: voice note = suara asli
        (2.87, 3.97), (4.29, 4.88), (5.20, 5.64), (6.07, 6.65),         # 2-5   bukan; coba tebak
        (7.07, 8.09), (8.42, 9.27), (9.48, 10.09), (10.50, 12.30),      # 6-9   kirim, dengar ulang, hapus
        (12.65, 13.27), (13.69, 16.05), (16.54, 18.14),                 # 10-12 dua jalur
        (18.62, 19.23), (19.58, 21.75), (22.15, 24.77),                 # 13-15 nada rendah, lebih berat
        (25.21, 27.10), (27.53, 28.58), (28.94, 30.46),                 # 16-18 mikrofon: 1 jalur (puncak)
        (30.84, 32.88), (33.20, 33.96),                                 # 19-20 bantahan
        (34.41, 37.82), (38.13, 38.61),                                 # 21-22 studi 2013
        (39.02, 39.53), (39.84, 41.96), (42.49, 44.44),                 # 23-25 lebih menarik
        (44.86, 46.28), (46.64, 48.13), (48.58, 49.39), (49.72, 50.23), (50.62, 51.22)]  # 26-30 penutup

# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris pendek, 1 kata kunci (PRB-37)
CHUNKS = [
    [("SUARA DI", "suara di", []), ("VOICE NOTE-MU", "voice note mu", ["VOICE"])],
    [("ITU SUARA ASLIMU.", "itu suara aslimu", ["ASLIMU."])],
    [("YANG KAMU DENGAR", "yang kamu dengar", []), ("TIAP HARI?", "tiap hari", ["HARI?"])],
    [("BUKAN.", "bukan", ["BUKAN."])],
    [("COBA TEBAK,", "coba tebak", ["TEBAK,"])],
    [("KENAPA BEDA?", "kenapa beda", ["BEDA?"])],
    [("KAMU KIRIM", "kamu kirim", []), ("VOICE NOTE,", "voice note", ["NOTE,"])],
    [("DENGAR ULANG,", "dengar ulang", ["ULANG,"])],
    [("LALU HAPUS?", "lalu hapus", ["HAPUS?"])],
    [("PADAHAL ITU", "padahal itu", []), ("YANG DIDENGAR", "yang didengar", []), ("TEMANMU.", "temanmu", ["TEMANMU."])],
    [("KOK BISA?", "kok bisa", ["BISA?"])],
    [("SUARAMU SAMPAI", "suaramu sampai", []), ("KE TELINGAMU", "ke telingamu", []),
     ("LEWAT DUA JALUR:", "lewat dua jalur", ["DUA"])],
    [("UDARA,", "udara", ["UDARA,"]), ("DAN TULANG KEPALA.", "dan tulang kepala", ["TULANG"])],
    [("UNIKNYA,", "uniknya", ["UNIKNYA,"])],
    [("KEPALAMU MEMPERKUAT", "kepalamu memperkuat", []), ("GETARAN", "getaran", []),
     ("NADA RENDAH.", "nada rendah", ["RENDAH."])],
    [("JADI DARI DALAM,", "jadi dari dalam", []), ("SUARAMU TERDENGAR", "suaramu terdengar", []),
     ("LEBIH BERAT.", "lebih berat", ["BERAT."])],
    [("MIKROFON CUMA", "mikrofon cuma", []), ("MENANGKAP", "menangkap", []),
     ("JALUR UDARA.", "jalur udara", ["UDARA."])],
    [("JALUR TULANGNYA", "jalur tulangnya", []), ("HILANG,", "hilang", ["HILANG,"])],
    [("SUARAMU JADI", "suaramu jadi", []), ("TERASA ASING.", "terasa asing", ["ASING."])],
    [("TAPI KAN SUARAKU", "tapi kan suaraku", []), ("DI REKAMAN", "di rekaman", []),
     ("MEMANG JELEK?", "memang jelek", ["JELEK?"])],
    [("BELUM TENTU.", "belum tentu", ["BELUM"])],
    [("STUDI 2013", "studi dua ribu tiga belas", ["2013"]), ("MENYELIPKAN", "menyelipkan", []),
     ("REKAMAN SUARA", "rekaman suara", []), ("PESERTA SENDIRI,", "peserta sendiri", ["SENDIRI,"])],
    [("DIAM-DIAM.", "diam diam", ["DIAM-DIAM."])],
    [("HASILNYA?", "hasilnya", ["HASILNYA?"])],
    [("MEREKA MENILAI", "mereka menilai", []), ("SUARA SENDIRI", "suara sendiri", []),
     ("LEBIH MENARIK.", "lebih menarik", ["MENARIK."])],
    [("YANG BIKIN RISIH", "yang bikin risih", ["RISIH"]), ("MUNGKIN CUMA KAGET.", "mungkin cuma kaget", ["KAGET."])],
    [("DUA-DUANYA", "dua duanya", ["DUA-DUANYA"]), ("SUARAMU.", "suaramu", [])],
    [("PUTAR VOICE NOTE-MU", "putar voice note mu", ["PUTAR"]), ("LAGI MALAM INI.", "lagi malam ini", [])],
    [("SUARA ASLIMU:", "suara aslimu", ["ASLIMU:"])],
    [("KEPALA,", "kepala", ["KEPALA,"])],
    [("ATAU REKAMAN?", "atau rekaman", ["REKAMAN?"])],
]
assert len(SEGS) == len(CHUNKS), (len(SEGS), len(CHUNKS))


def syl(word):
    return max(1, len(re.findall(r"[aiueo]+", word.lower())))


out = []
for si, ((s, e), chunks) in enumerate(zip(SEGS, CHUNKS)):
    weights = [sum(syl(w) + 0.4 for w in sp.split()) for _, sp, _ in chunks]
    tot = sum(weights)
    t = s
    for (disp, sp, keys), wgt in zip(chunks, weights):
        d = (e - s) * wgt / tot
        out.append({"text": disp, "keys": keys, "seg": si, "start": round(t, 3), "end": round(t + d, 3)})
        t += d

json.dump(out, open("timing.json", "w"), ensure_ascii=False, indent=1)
for i, c in enumerate(out):
    print(i, c["seg"], c["start"], c["end"], c["text"])

"""ARN-59 Mana Lebih Hemat? #14 (Amplop kondangan): waktu chunk subtitle dari jeda VO nyata
(ffmpeg silencedetect n=-30dB d=0.12 pada vo.wav, 62,85 dtk). TANPA Scribe.
40 segmen bicara -> 38 frasa: 1,483-2,447 + 2,597-2,729 digabung ("amplopnya cuma satu"),
51,681-52,189 + 52,311-53,411 digabung ("tapi datang melebihi undangan").
Output: timing.json (waktu audio VO, tanpa LEAD). Field "seg" = indeks segmen (penanda adegan).
Jalankan dari folder kerja (pagi/build_amplop): python3 ../align_amplop.py"""
import json, re

SEGS = [(0.000, 1.139), (1.483, 2.729),                 # 0-1  hook
        (3.133, 3.553), (3.881, 4.682),                 # 2-3  coba tebak
        (5.301, 7.440), (7.637, 8.781),                 # 4-5  om berlima
        (9.215, 10.690),                                # 6    dapur pengantin
        (11.205, 12.477), (12.734, 14.471),             # 7-8  katering 50 rb
        (14.888, 15.975), (16.135, 16.912),             # 9-10 berdua 100 rb
        (17.271, 20.964),                               # 11   amplop rekan kerja
        (21.354, 22.294), (22.663, 23.112),             # 12-13 isi 100 rb? pas
        (23.419, 24.325), (24.657, 25.890),             # 14-15 isi 50 rb? tekor
        (26.274, 27.896),                               # 16   ongkos
        (28.127, 29.605), (29.860, 30.544),             # 17-18 bensin
        (30.879, 32.053), (32.311, 34.243),             # 19-20 tiga undangan, 360 rb
        (34.563, 35.266), (35.560, 37.212),             # 21-22 om berlima, 250 rb
        (37.521, 37.797), (38.105, 39.326),             # 23-24 tunggu, tim silaturahmi
        (39.668, 41.013), (41.190, 42.158),             # 25-26 doa
        (42.461, 43.224), (43.363, 45.352),             # 27-28 lagi pula, kembali
        (45.640, 49.271),                               # 29   1 undangan = 2 orang
        (49.499, 51.485), (51.681, 53.411),             # 30-31 jadi ... melebihi undangan
        (53.667, 54.680), (54.883, 56.362),             # 32-33 patokan
        (56.653, 57.345), (57.592, 58.862),             # 34-35 transfer
        (59.213, 60.984), (61.219, 62.565)]             # 36-37 penutup

# per segmen: (teks layar, kata yang diucapkan, kata kunci kuning) -- 1 baris pendek, 1 kata kunci (PRB-37)
CHUNKS = [
    [("DATANG BERDUA,", "kamu datang berdua", ["BERDUA,"])],
    [("AMPLOPNYA", "amplopnya", []), ("CUMA SATU.", "cuma satu", ["SATU."])],
    [("COBA TEBAK,", "coba tebak", ["TEBAK,"])],
    [("SIAPA YANG TEKOR?", "siapa yang tekor", ["TEKOR?"])],
    [("KAMU PASTI KENAL", "kamu pasti kenal", ["KENAL"]), ("OM YANG DATANG", "om yang datang", []),
     ("BERLIMA,", "berlima", ["BERLIMA,"])],
    [("AMPLOPNYA", "amplopnya", []), ("JUGA SATU.", "juga satu", ["SATU."])],
    [("HITUNG DARI", "hitung dari", []), ("DAPUR PENGANTIN.", "dapur pengantin", ["DAPUR"])],
    [("KATERING GEDUNG", "katering gedung", ["KATERING"]), ("SERBAGUNA,", "serbaguna", [])],
    [("SEKITAR", "sekitar", []), ("Rp50 RIBU", "lima puluh ribu", ["Rp50"]), ("PER ORANG.", "per orang", [])],
    [("KAMU BERDUA", "kamu berdua", ["BERDUA"]), ("MAKAN,", "makan", [])],
    [("Rp100 RIBU.", "seratus ribu", ["Rp100"])],
    [("PADAHAL", "padahal", ["PADAHAL"]), ("AMPLOP REKAN KERJA", "amplop rekan kerja", ["AMPLOP"]),
     ("BIASANYA", "biasanya", []), ("Rp100–200 RIBU.", "seratus sampai dua ratus ribu", ["Rp100–200"])],
    [("ISI Rp100 RIBU?", "isi seratus ribu", ["Rp100"])],
    [("PAS.", "pas", ["PAS."])],
    [("ISI Rp50 RIBU?", "isi lima puluh ribu", ["Rp50"])],
    [("PENGANTIN", "pengantin", []), ("YANG TEKOR.", "yang tekor", ["TEKOR."])],
    [("TAPI KAMU JUGA", "tapi kamu juga", []), ("KELUAR ONGKOS.", "keluar ongkos", ["ONGKOS."])],
    [("BENSIN PULANG PERGI", "bensin pulang pergi", ["BENSIN"]), ("DUA LITER,", "dua liter", [])],
    [("Rp20 RIBU.", "dua puluh ribu", ["Rp20"])],
    [("MINGGU INI", "minggu ini", []), ("TIGA UNDANGAN?", "tiga undangan", ["TIGA"])],
    [("Rp360 RIBU", "tiga ratus enam puluh ribu", ["Rp360"]), ("MELAYANG.", "melayang", [])],
    [("OM YANG BERLIMA?", "om yang berlima", ["BERLIMA?"])],
    [("MAKANNYA", "makannya", []), ("Rp250 RIBU.", "dua ratus lima puluh ribu", ["Rp250"])],
    [("TUNGGU,", "tunggu", ["TUNGGU,"])],
    [("TIM SILATURAHMI", "tim silaturahmi", ["SILATURAHMI"]), ("MENJAWAB.", "menjawab", [])],
    [("KONDANGAN ITU", "kondangan itu", []), ("DOA,", "doa", ["DOA,"])],
    [("BUKAN JUAL BELI.", "bukan jual beli", ["JUAL"])],
    [("LAGI PULA,", "lagi pula", ["PULA,"])],
    [("AMPLOPMU NANTI", "amplopmu nanti", []), ("KEMBALI", "kembali", ["KEMBALI"]),
     ("WAKTU KAMU NIKAH.", "waktu kamu nikah", ["NIKAH."])],
    [("DAN PENGANTIN", "dan pengantin", []), ("BIASANYA SUDAH", "biasanya sudah", []),
     ("MENGHITUNG", "menghitung", ["MENGHITUNG"]), ("1 UNDANGAN", "satu undangan", ["1"]),
     ("UNTUK 2 ORANG.", "untuk dua orang", ["2"])],
    [("JADI YANG BIKIN", "jadi yang bikin", []), ("TEKOR", "tekor", ["TEKOR"]), ("BUKAN BERDUA,", "bukan berdua", ["BERDUA,"])],
    [("TAPI DATANG", "tapi datang", []), ("MELEBIHI UNDANGAN.", "melebihi undangan", ["MELEBIHI"])],
    [("PATOKAN", "patokan", ["PATOKAN"]), ("GAMPANGNYA:", "gampangnya", [])],
    [("PORSI KALI", "porsi kali", ["PORSI"]), ("ORANG YANG DATANG.", "orang yang datang", ["DATANG."])],
    [("NGGAK BISA DATANG?", "nggak bisa datang", ["NGGAK"])],
    [("TRANSFER", "transfer", ["TRANSFER"]), ("TETAP DIHITUNG.", "tetap dihitung", [])],
    [("KAMU TIM", "kamu tim", []), ("SATU AMPLOP BERDUA,", "satu amplop berdua", ["SATU"])],
    [("ATAU AMPLOP", "atau amplop", []), ("MASING-MASING?", "masing masing", ["MASING-MASING?"])],
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
print(len(out), "chunk")

"""Timing ARN-40 dari jeda VO nyata (silencedetect). Output timing.json (waktu video = VO + LEAD)."""
import json
LEAD = 0.3
SEGS = [
 (0.00,1.57,"Mesin pesawatmu akan mati."),(2.07,2.58,"Keempatnya."),(3.13,4.53,"Lalu kamu harus memilih."),
 (5.01,6.31,"Malam di atas Jawa."),(6.80,7.72,"Kabin berasap,"),(8.16,8.84,"bau belerang."),
 (9.33,10.59,"Sayap berpendar biru."),(11.06,12.73,"Tapi radar cuaca bersih."),
 (13.18,14.23,"Satu mesin mati."),(14.57,15.03,"Lalu"),(15.20,15.88,"tiga lainnya."),
 (16.37,17.09,"Kapten bicara:"),(17.54,18.86,"Kita punya sedikit masalah."),(19.22,20.39,"Keempat mesin berhenti."),
 (20.86,21.98,"Kamu meluncur turun."),(22.38,22.96,"Di depan,"),(23.21,24.04,"pegunungan Jawa."),
 (24.49,25.09,"Dua pilihan."),(25.45,25.95,"Satu:"),(26.23,27.67,"lewati gunung ke Jakarta,"),(27.81,29.22,"sambil coba nyalakan mesin."),
 (29.60,29.98,"Dua:"),(30.24,30.68,"berbalik,"),(30.98,32.79,"mendarat darurat di Samudra Hindia."),
 (33.24,33.98,"Kamu pilih apa?"),(34.34,35.63,"Tulis satu atau dua."),
 (36.00,36.69,"Like terbanyak"),(36.90,38.38,"dibacakan di cerita berikutnya."),
 (38.89,40.14,"Kapten pasang batas:"),(40.38,41.53,"dua belas ribu kaki."),(41.92,42.57,"Di bawahnya,"),(42.82,43.15,"ke laut."),
 (43.53,45.35,"Di tiga belas ribu lima ratus kaki,"),(45.48,46.55,"satu mesin menyala."),(46.90,47.91,"Lalu yang lain."),
 (48.32,51.19,"Dua ratus enam puluh tiga orang mendarat selamat di Jakarta."),
 (51.58,52.19,"Pelakunya:"),(52.44,53.31,"abu Galunggung,"),(53.54,54.50,"tak terlihat radar."),(54.87,57.07,"Kini ada pusat peringatan abu vulkanik."),
]
# (teks layar, kata kunci kuning, jumlah kata yang diucapkan)
CHUNKS = [
 ("Mesin","",1),("pesawatmu akan mati.","mati",3),("Keempatnya.","Keempatnya",1),("Lalu kamu harus memilih.","memilih",4),
 ("Malam di atas Jawa.","Jawa",4),("Kabin berasap, bau belerang.","belerang",4),
 ("Sayap berpendar biru.","biru",3),("Tapi radar cuaca bersih.","bersih",4),
 ("Satu mesin mati.","mati",3),("Lalu tiga lainnya.","tiga",3),
 ("Kapten bicara:","Kapten",2),("“Kita punya sedikit masalah.","masalah",4),("Keempat mesin berhenti.”","berhenti",3),
 ("Kamu meluncur turun.","turun",3),("Di depan, pegunungan Jawa.","pegunungan",4),
 ("Dua pilihan.","Dua",2),("Satu: lewati gunung ke Jakarta,","Jakarta",5),("sambil coba nyalakan mesin.","mesin",4),
 ("Dua: berbalik,","berbalik",2),("mendarat darurat","darurat",2),("di Samudra Hindia.","Samudra Hindia",3),
 ("Kamu pilih apa?","apa",3),("Tulis 1 atau 2.","1 atau 2",4),
 ("Like terbanyak","Like",2),("dibacakan di cerita berikutnya.","dibacakan",4),
 ("Kapten pasang batas:","batas",3),("12.000 kaki.","12.000",4),("Di bawahnya, ke laut.","laut",4),
 ("Di 13.500 kaki,","13.500",7),("satu mesin menyala.","menyala",3),("Lalu yang lain.","lain",3),
 ("263 orang","263",6),("mendarat selamat di Jakarta.","selamat",4),
 ("Pelakunya:","Pelakunya",1),("abu Galunggung,","Galunggung",2),("tak terlihat radar.","radar",3),
 ("Kini ada pusat peringatan","peringatan",4),("abu vulkanik.","abu vulkanik",2),
]
words = []
for a, b, txt in SEGS:
    ws = txt.split(); w = [len(x) + 1 for x in ws]; tot = sum(w); t = a
    for x, wi in zip(ws, w):
        d = (b - a) * wi / tot; words.append((x, t + LEAD, t + d + LEAD)); t += d
assert sum(c[2] for c in CHUNKS) == len(words), (sum(c[2] for c in CHUNKS), len(words))
out = []; i = 0
for txt, kw, n in CHUNKS:
    ws = words[i:i + n]; i += n
    out.append({"text": txt, "kw": kw, "s": round(ws[0][1], 3), "e": round(ws[-1][2], 3), "spoken": " ".join(w[0] for w in ws)})
out[0]["s"] = 0.0
# tampil: dari s sampai awal chunk berikut (maks e+0.5)
for k, c in enumerate(out):
    nxt = out[k + 1]["s"] if k + 1 < len(out) else c["e"] + 0.4
    c["show_end"] = round(min(nxt, c["e"] + 0.5) if nxt - c["e"] > 0.5 else nxt, 3)
SC_CHUNK = [0, 4, 6, 8, 10, 13, 15, 18, 21, 23, 25, 28, 31, 33]
scenes = [0.0] + [round(out[c]["s"] - 0.15, 3) for c in SC_CHUNK[1:]]
VO_END = 57.36 + LEAD
CLOSE = round(out[-1]["e"] + 0.13, 3)
scenes.append(CLOSE)
TOTAL = round(CLOSE + 1.5, 2)
json.dump({"lead": LEAD, "chunks": out, "scenes": scenes, "total": TOTAL, "vo_end": VO_END}, open("timing.json", "w"), indent=1, ensure_ascii=False)
for k, c in enumerate(out): print(k, c["s"], c["show_end"], c["text"], "|", c["spoken"])
print("scenes", scenes, "TOTAL", TOTAL)
print("durasi adegan", [round(b - a, 2) for a, b in zip(scenes, scenes[1:] + [TOTAL])])

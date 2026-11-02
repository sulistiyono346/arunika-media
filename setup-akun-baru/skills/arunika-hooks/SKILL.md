---
name: "arunika-hooks"
description: "Audit dan tulis ulang hook reel Arunika (@kabar.arunika): beri skor 0–100, tandai hook lemah, keluarkan 3 hook pengganti yang lolos aturan frame 0."
---

# Arunika Hooks

Pemeriksa hook untuk reel explainer Arunika. Input: topik saja, ATAU naskah/kalimat pembuka yang sudah ada. Output: diagnosis + skor + 3 hook pengganti. Bahasa Indonesia santai, POV "kamu".

Skill ini pelengkap `arunika-reels`. Kalau aturan di sini bertabrakan dengan Formula retensi di `arunika-reels`, yang menang `arunika-reels` (itu berasal dari data Insight Arunika sendiri).

"Hook" = 3 lapis yang muncul bersamaan di detik 0–3: (1) kalimat VO pertama, (2) judul layar/cover, (3) visual frame 0. Ketiganya dinilai, bukan kalimatnya saja.

## Langkah

1. **Ambil hook-nya.** Kalau user hanya memberi topik, langsung ke langkah 4 (tulis 3 hook), lalu nilai ketiganya.
2. **Cek tanda bahaya** (daftar di bawah). Tandai setiap yang kena dengan ✗, yang setengah dengan ⚠.
3. **Beri skor** dengan rubrik 5 × 20 poin.
4. **Tulis ulang 3 hook** dari 3 tipe berbeda (lihat Tipe hook). Setiap hook berisi: kalimat VO pertama, judul layar 3–6 kata (1 kata kunci kuning, ditandai **tebal**), deskripsi visual frame 0, dan kalimat janji payoff detik 2–4.
5. **Nilai ketiganya** dan sarankan satu pilihan, dengan alasan 1 kalimat.

## Tanda bahaya (hook lemah)

- ✗ Sapaan/pembuka kosong: "Halo guys", "Hai, kali ini aku mau bahas…", "Di video ini…", "Pernah nggak sih kamu…" tanpa fakta setelahnya.
- ✗ Kalimat VO pertama mengulang judul layar (melanggar Formula retensi poin 3).
- ✗ Tidak ada informasi baru (angka, fakta, konflik) di kalimat pertama.
- ✗ Frame 0 kosong, karakter diam, atau tabel/teks kecil yang harus dibaca.
- ✗ Aru dan/atau Si Bocor tidak terlihat di frame 0.
- ✗ Tidak menyebut "kamu/-mu" — terdengar seperti ceramah dari luar.
- ✗ Gagal tanpa suara: kalau di-mute, penonton tidak paham konfliknya dari visual + teks layar saja.
- ⚠ Pertanyaan yang jawabannya bisa ditebak ("Mau hemat?" → "iya").
- ⚠ Topik di luar janji bio ("Hitung-hitungan uang harian & fakta dalam 1 menit"), mis. motivasi umum.
- ⚠ Tidak ada janji payoff di detik 2–4 ("…dan angka setahunnya bikin kaget").
- ⚠ Klaim angka tanpa sumber yang bisa dicantumkan di caption.
- ⚠ Judul tentang Arunika sendiri (di balik layar, pengumuman, promo).

## Rubrik skor (0–100)

Setiap dimensi 0–20:
1. **Jelas** — dalam 1 detik penonton tahu ini tentang apa, tanpa membaca kalimat panjang.
2. **Emosi** — memicu kaget, takut rugi, penasaran, atau "jangan-jangan aku juga?".
3. **Gangguan pola** — beda dari feed: gerakan, konflik, angka besar, onomatope, visual yang aneh.
4. **Taruhan** — ada yang dipertaruhkan untuk penonton (uangnya, kebiasaannya, tubuhnya).
5. **Janji** — penonton tahu akan dapat apa kalau menonton sampai payoff.

Patokan kasar: <40 tulis ulang total; 40–59 lemah; 60–79 layak; 80+ kuat. Rubrik ini kerangka dari artikel kreator (bukan riset ilmiah); angka retensi di artikel semacam itu tidak dipakai sebagai fakta. Yang jadi patokan sebenarnya adalah data Insight Arunika (target di `arunika-reels`: skip <35%, bertahan di detik 8 ≥50%).

## Tipe hook (pilih 3 yang berbeda saat menulis ulang)

1. **Bantahan** — "Cara hemat listrik yang kamu lakukan ternyata SALAH." Paling kuat di data @kokbisa.
2. **Celah penasaran** — buka pertanyaan yang baru terjawab di payoff: "Ada satu biaya di struk ojolmu yang nggak pernah kamu lihat."
3. **"Kalau…" / "Apa jadinya jika…"** — membalik skala: "Kalau uang kopimu setahun dikumpulkan, jadi apa?"
4. **Masalah yang dirasakan** — "Gajimu masuk tanggal 25. Tanggal 3, saldomu tinggal segini."
5. **A vs B** — dua pilihan sehari-hari bersisian, jawabannya mengejutkan: "Masak vs beli: bedanya bukan yang kamu kira."
6. **Dulu vs sekarang** — "Rp5.000 tahun 1990 vs 2026."
7. **"[Benda], kok [sifat]?"** — benda sehari-hari dibedah: "QRIS, kok langsung masuk?" Frame 0 = cutaway yang memperlihatkan dalamnya.
8. **POV** — penonton jadi tokoh: "Kamu pekerja UMR Jakarta. Hari ke-1, kamu…"
9. **Kejutan visual** — gambar yang menuntut penjelasan di frame 0 (Si Bocor memakan uang dari dompet, Pulau Jawa di atas Eropa).

Kombinasi terbaik biasanya: celah penasaran / bantahan (kalimat) + kejutan visual atau A vs B (frame 0).

## Bank hook (contoh terbukti — tiru mekanismenya, jangan kata-katanya)

Dari riset yang sudah tercatat di `arunika-reels`:
- "Buku dan guru IPA kalian SALAH!" (@kokbisa, 211 rb) — bantahan.
- "Apa jadinya jika dolar naik jadi Rp30.000?" (@kokbisa, 55 rb) — "apa jadinya".
- "Air rebusan pertama dibuang?" (@ctmverse, 2,7 jt) — mitos sehari-hari + sumber.
- "Masak vs beli: beda berapa?" (@ctmverse, 980 rb) — A vs B uang harian.
- "Jembatan, kok kuat?" (@kalbotau, 11,8 jt) — benda + kok, cutaway di cover, kegagalan pertama <10 dtk.
- "Jawa dipindah ke Eropa" (@semenitilmu, 259,7 rb like) — jawaban visual di frame 0.
- Gagal: "Cicilan HP 0%" (Arunika, 7 like) — cover pertanyaan statis + HP diam.

Cara menambah bank: user menempelkan kalimat pembuka + judul layar + views dari reel teratas (Arunika atau kreator pembanding). Tambahkan baris baru di sini dengan format `"hook" (akun, views) — mekanisme`. Kalau user menempelkan 10+ contoh dari satu akun, urutkan berdasarkan views, bandingkan 5 teratas vs 5 terbawah, dan tulis pola pembedanya.

## Format output

Kirim dalam blok kode, gaya log seperti ini, lalu 3 hook pengganti:

```
$ hooks scan ./reel-<topik>
Menganalisis hook...
✗ "<kalimat asli>" · <alasan>
✗ <tanda bahaya lain>
⚠ <peringatan>
Skor: <n>/100 (Jelas a · Emosi b · Pola c · Taruhan d · Janji e)
→ <jumlah> masalah. menulis ulang...
```

Lalu untuk setiap hook pengganti:
- **Tipe:** …
- **VO detik 0:** …
- **Judul layar:** … (**kata kunci** kuning)
- **Frame 0:** … (Aru/Si Bocor sedang apa)
- **Janji payoff detik 2–4:** …
- **Skor:** n/100

Tutup dengan: pilihan yang disarankan + alasan 1 kalimat. Kalau user setuju, hook terpilih dipakai di tahap Naskah `arunika-reels`.
---
name: "arunika-script-audit"
description: "Audit struktur naskah reel Arunika sebelum VO dan render: cek Hook, Konteks, Inti, Payoff, CTA, timing per detik, dan aturan retensi; keluarkan daftar perbaikan."
---

# Arunika Script Audit

Pemeriksa naskah reel explainer Arunika (@kabar.arunika), dijalankan setelah naskah per adegan selesai dan SEBELUM membuat VO di ElevenLabs (VO memakai kredit dan tidak dipercepat/diperlambat, jadi kesalahan struktur harus ketahuan di naskah).

Skill ini pelengkap `arunika-reels`. Semua aturan timing di bawah diambil dari Formula retensi di sana; kalau `arunika-reels` diperbarui, yang berlaku versi terbaru di sana.

## Struktur yang dicek

Struktur reel jualan (Hook → Problem → Solution → Proof → CTA booking) TIDAK dipakai. Arunika memakai struktur explainer:

| Bagian | Detik (format biasa 25–35 dtk) | Isi wajib |
|---|---|---|
| 1. HOOK | 0–2 | Fakta/angka/konflik baru, "kamu/-mu", Aru/Si Bocor bergerak. Tidak mengulang judul. |
| 2. JANJI | 2–4 | Janji payoff: "…dan angka setahunnya bikin kaget". |
| 3. KONTEKS / POV | 4–10 | Penonton jadi pelaku, persona & angka konkret. Ganti visual tiap 2–3 dtk. |
| 4. INTI | 10–20 | Maks 1 angka atau 1 ide per adegan. Ajakan follow teks kecil sebelum dtk 15. |
| 5. PAYOFF | 15–25 | Angka/perbandingan/jawaban yang dijanjikan. Bukan di detik terakhir. |
| 6. CTA + LOOP | ≤1,5 dtk terakhir | Pertanyaan komentar + logo kecil; frame terakhir menyambung ke frame 0. |

Format "Tangga masalah → solusi" (60–100 dtk) dicek berbeda: kegagalan pertama <10 dtk, setiap bab ≤12 dtk dan diakhiri kegagalan baru + 1 istilah, tidak ada pembuka/penutup panjang.

Serial interaktif (mis. "Simulasi Sebulan: Saldo Aru") tambah cek: HUD tampil, episode berakhir dengan keputusan terbuka, pilihan 🅰️/🅱️ ada di caption.

## Langkah

1. **Petakan naskah.** Hitung perkiraan detik setiap adegan (±2,2 kata per detik — kalibrasi dari VO asli ARN-17: 82 kata = 36,8 dtk; angka yang ditulis dengan huruf dihitung per kata). Tandai bagian mana yang diisi tiap adegan.
2. **Cek tiap bagian** dengan daftar di bawah. ✓ lolos, ✗ gagal, ⚠ perlu dicek.
3. **Cari kebocoran tengah**: adegan berisi 2+ angka, kalimat >15 kata, penjelasan yang mengulang, atau adegan >4 dtk tanpa ganti visual.
4. **Cek caption** (bukan bagian video tapi wajib).
5. **Keluarkan daftar perbaikan** berurutan dari yang paling berdampak, lalu tulis ulang HANYA adegan yang gagal (jangan tulis ulang naskah utuh kecuali diminta).

## Daftar cek

**Hook & janji**
- Adegan 1 maks ±7 kata (≤3 dtk)? Adegan pembuka yang panjang membuat janji payoff terlambat dan diduga ikut menaikkan skip (ARN-17: adegan 1 = 16 kata ±7 dtk, skip 42%).
- Kalimat 1 memberi informasi baru, bukan pertanyaan yang sama dengan judul layar?
- Ada "kamu/-mu" di 2 kalimat pertama?
- Frame 0: Aru/Si Bocor terlihat dan bergerak/konflik; tidak ada tabel atau teks kecil?
- Janji payoff muncul di detik 2–4?
- (Untuk audit hook mendalam, jalankan `arunika-hooks`.)

**Tengah**
- Maks 6 adegan, 1 adegan = 1 ide/1 angka?
- Visual berganti tiap 2–3 dtk?
- Ajakan follow (teks kecil) sebelum detik 15?
- Tidak ada pengulangan atau langkah hitung terlalu rinci?

**Payoff**
- Payoff muncul sebelum detik 25 dan sesuai janji di detik 2–4?
- Kalau topik menyentuh dompet: ditutup dengan 1 angka uang (sebulan/setahun)?
- Si Bocor muncul di bagian yang "bocor"?

**CTA & penutup**
- Serial interaktif: pilihan A/B diucapkan singkat (≤12 kata); rincian harga cukup di teks layar & caption.
- Penutup ≤1,5 dtk, pertanyaan komentar spesifik (bukan "gimana menurut kalian?" saja)?
- Tidak ada layar logo penuh 4–6 dtk?
- Frame terakhir menyambung ke frame 0 (loop)?

**Caption**
- Kalimat pertama = ajakan follow/serial?
- Ada ajakan "Kirim ke teman yang …" dengan situasi spesifik (wajib — share membawa reel ke orang asing)?
- Angka nyata punya sumber link; angka contoh diberi label ilustrasi?
- ±5 hashtag (#NamaSerial … #Arunika)?

**Total**
- Durasi VO ≤35 dtk (Tangga masalah → solusi ≤100 dtk)?
- Topik menepati janji bio "Hitung-hitungan uang harian & fakta dalam 1 menit"?

## Format output

Kirim dalam blok kode, gaya log:

```
// script-audit · reel-<topik>.txt
// 6 bagian · perkiraan <n> dtk
✓ HOOK    · <catatan singkat>
✗ JANJI   · tidak ada janji payoff di dtk 2–4
✓ KONTEKS · POV "kamu", persona jelas
⚠ INTI    · adegan 4 berisi 2 angka (±5 dtk)
✓ PAYOFF  · dtk 19, sesuai janji
✗ CTA     · tidak ada "kirim ke teman yang …" di caption
→ 2 gagal, 1 peringatan. belum siap VO.
```

Lalu:
1. **Perbaikan** (berurutan, maks 5 poin, masing-masing 1 kalimat).
2. **Adegan yang ditulis ulang** — hanya adegan yang gagal, dengan perkiraan detik.
3. Status akhir: `siap VO.` hanya jika tidak ada ✗. Peringatan ⚠ boleh lolos asal user setuju.
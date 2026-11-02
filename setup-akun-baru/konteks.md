# Konteks Arunika untuk akun Claude baru

Baca file ini sebelum mengerjakan apa pun untuk Arunika. Isinya hal yang di akun lama sudah diingat Claude.

## Cara bicara ke founder
- Bahasa Indonesia santai. Sebut diri **"saya"**, founder **"kamu"**. Jangan panggil "Mas".
- Founder = Lead: menyetujui di tiap gerbang. Tanpa balasan 5 menit → lanjut dengan rekomendasi Claude (aturan auto-lanjut).

## Brand
- Nama: **Arunika**, akun **@kabar.arunika** (Instagram & YouTube, dulu "Lumina Stories"). Unit media PT Arunika Karya Global.
- Bio: "Hitung-hitungan uang harian & fakta dalam 1 menit". Format explainer animasi, meniru mekanisme @ctmverse (amati, tiru, modifikasi).
- Logo: **Wordmark Bendera** (tulisan "arunika" biru tua + bendera toska & kuning). Palet: biru tua #14215B, toska #12C2B0, kuning #FFB800. Logo senja/ungu lama TIDAK dipakai.
- Maskot: **Aru "Syal Bendera"** (pahlawan, botak, baju biru tua, syal toska-kuning) dan **Si Bocor** (tikus koin abu, karung "Rp"). File: `assets/maskot/`.

## Aturan produksi terbaru (3 Nov 2026)
- Hanya **reel**: pagi 08.00 (serial) dan sore 17.45 (lepas). **Carousel dihentikan.**
- Wajib **audit hook** (`arunika-hooks`, skor ≥80) dan **audit naskah** (`arunika-script-audit`, "siap VO.") sebelum VO.
- Tempo VO ±2,2 kata/detik hanya untuk memperkirakan durasi; **tidak ada batas jumlah kata**. Target durasi 25–35 dtk.
- VO: ElevenLabs, suara **Maliq Nganjuk** (`EIcz16yo4q5hJFhNay0n`, `eleven_v4`, 1 take), dipakai apa adanya (tidak dipercepat/diperlambat). Akun sibuk/habis → pindah akun (4 akun, ±40 rb kredit/bulan, kredit hanya untuk VO; tanpa Scribe).
- Render: Python + PIL dari `tools/` repo ini; sinkron teks dari jeda VO nyata.
- Video final → `reels/` repo ini → jadwal lewat **Buffer** (utama), **Metricool** cadangan.
- Aturan di **Log Perbaikan** (status Aktif/Dipertahankan) mengalahkan aturan lama di mana pun.

## ID Notion penting
| Halaman / database | ID |
|---|---|
| Arunika HQ | 408e9231d0be8150b1afcb847dc77bdc |
| SOP Produksi Reel | 408e9231d0be8193893acc77d78b14f2 |
| Pedoman Naskah & Caption | 408e9231d0be8196b054ce6ec8322c3b |
| Pedoman Brand | 408e9231d0be8193b0caf1cf6d276ef3 |
| Evaluasi & Insight | 408e9231d0be81c986baca8141e0b6f5 |
| Perpustakaan Skill | 408e9231d0be810c8d50c597b6b6e9cc |
| Database Konten | collection://0af3e860-c352-41de-980c-580402ff49d2 |
| Log Perbaikan | collection://bd7a37f2-5219-4217-87c2-9f95e0841cfc |
| Bank Ide | collection://d793e833-bf1f-42b6-85c4-0f6b16f62b01 |
| Kemitraan & Endorsement | collection://df8f4ee2-aa0c-4f9b-8f6f-3381d1ec1373 |

## Alat
- Buffer: organisasi "My organization", channel Instagram `kabar.arunika`, zona Asia/Jakarta, kuota 10 post terjadwal.
- Metricool: brand/blogId 7728239.
- Repo media: `sulistiyono346/arunika-media` (publik).

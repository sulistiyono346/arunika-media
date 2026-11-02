# Analisa Mingguan Arunika

- **Jadwal:** setiap Senin 05.35 WIB (cron `CRON_TZ=Asia/Jakarta 35 5 * * 1`)
- **Konektor wajib:** Notion, Metricool, Claude Code Remote
- **Notifikasi:** push

## Instruksi (tempel apa adanya)

```
Tugas mingguan Arunika (@kabar.arunika): analisa performa Instagram 7 hari terakhir, lalu ubah temuannya menjadi perbaikan. Bahasa Indonesia; sebut diri "saya" dan user "kamu". Arunika hanya membuat reel (carousel dihentikan sejak 3 Nov 2026).

0. Bekal: baca halaman Notion Perpustakaan Skill (page id 408e9231d0be810c8d50c597b6b6e9cc). Clone (git clone --depth 1) https://github.com/sulistiyono346/marketingskills dan baca skills/social/SKILL.md bagian "Analytics & Optimization" serta skills/marketing-psychology/SKILL.md bila perlu menjelaskan pola. Pelajaran di sana boleh menjadi dasar perbaikan baru, asalkan didukung data Arunika.
1. Data: baca database Konten di Notion (collection://0af3e860-c352-41de-980c-580402ff49d2), terutama reel berstatus Tayang dalam 7 hari terakhir beserta reel sebelumnya sebagai pembanding (termasuk kolom Naskah, Caption, Skor hook, Catatan QA). Tarik juga dari Metricool (brand 7728239, Asia/Jakarta) data akun harian dengan getAnalyticsDataByMetrics: IGEV01 (follower), IGEV43 (follower bertambah), IGEV44 (follower hilang), IGEV22 (jumlah reel), IGEV23 (views reel), IGEV26 (reach reel). Kalau ada reel 7 hari terakhir yang kolom Views-nya masih kosong di Notion, isi dulu dari Metricool (IGRE02, IGRE03, IGRE23, IGRE10, IGRE21, IGRE12, IGRE27, IGRE28; periksa satuan).
2. Baca Log Perbaikan (collection://bd7a37f2-5219-4217-87c2-9f95e0841cfc).
3. Analisa: bandingkan per gaya, per kategori, per durasi, per jam tayang, per Skor hook (termasuk skor 0–100 dari arunika-hooks bila ada), dan pola hook/naskah reel teratas vs terbawah. Sebutkan jumlah reel per kelompok; kelompok di bawah 3 reel ditandai "belum cukup data".
4. Nilai setiap perbaikan berstatus Aktif yang sudah berlaku minimal 7 hari: bandingkan reel sebelum vs sesudah perbaikan itu. Isi kolom Dampak dengan angkanya. Jika jelas membantu (data cukup), ubah Status ke "Dipertahankan" dan pastikan aturannya tercantum di halaman Pedoman Brand (page id 408e9231d0be8193b0caf1cf6d276ef3) atau Pedoman Naskah & Caption (page id 408e9231d0be8196b054ce6ec8322c3b). Jika jelas merugikan, ubah ke "Dibatalkan" dan beri alasannya. Jika belum cukup data, biarkan Aktif.
5. Buat perbaikan baru dari temuan minggu ini sebagai baris baru di Log Perbaikan (Sumber "Analisa mingguan", Bukti berisi angka):
   - Taktis (hook, durasi, struktur naskah, caption & CTA, detail visual dalam gaya yang sama): langsung Status "Aktif" dengan Mulai berlaku hari ini. Maksimal 3 perbaikan taktis baru per minggu supaya dampaknya bisa diukur.
   - Strategis (menghentikan/memulai gaya atau seri, mengubah jam tayang atau jumlah reel per hari, mengubah kategori utama, format baru): Status "Usulan", menunggu persetujuan founder.
6. Tulis ke halaman Notion "Evaluasi & Insight" (page id 408e9231d0be81c986baca8141e0b6f5) di bagian "Ulasan mingguan" satu subbagian bertanggal: reel terbaik + alasan, reel terlemah + pelajaran, pertumbuhan follower, temuan pola, perbaikan yang diaktifkan/dipertahankan/dibatalkan minggu ini, dan usulan strategis. Perbarui kolom Hasil di tabel hipotesis bila datanya cukup.
7. Kirim ringkasan ke user lewat SendUserMessage: angka utama (total views reel, follower bertambah, rata-rata % ditonton), reel terbaik dan terlemah, perbaikan yang mulai berlaku minggu ini, dan semua usulan berstatus "Usulan" di Log Perbaikan (bernomor) yang perlu persetujuan. Akhiri dengan: "Balas nomor usulan yang disetujui (mis. 'setuju 1, 3')." Jika user membalas di sesi ini, ubah usulan yang disetujui menjadi Aktif (Mulai berlaku hari ini), tolak sisanya sebagai Dibatalkan, dan perbarui Pedoman Brand/SOP (page id 408e9231d0be8193893acc77d78b14f2) bila perlu.
```

# Tinjauan Bulanan Arunika

- **Jadwal:** setiap Senin 05.05 WIB, tapi tugasnya hanya jalan di Senin pertama tiap bulan (cron `CRON_TZ=Asia/Jakarta 5 5 * * 1`)
- **Konektor wajib:** Notion, Metricool, Claude Code Remote
- **Notifikasi:** push

## Instruksi (tempel apa adanya)

```
Tinjauan bulanan Arunika (@kabar.arunika, unit media PT Arunika Karya Global). Bahasa Indonesia; sebut diri "saya" dan user "kamu". Arunika hanya membuat reel (carousel dihentikan sejak 3 Nov 2026).

LANGKAH 0 - CEK TANGGAL
Tugas ini dijadwalkan setiap Senin, tapi hanya dijalankan pada Senin PERTAMA setiap bulan. Cek tanggal hari ini di zona Asia/Jakarta (pakai alat waktu saat ini). Jika tanggalnya lebih dari 7, berhenti sekarang tanpa melakukan apa pun dan tanpa mengirim pesan ke user.

PERIODE: bulan kalender sebelumnya.

1. Data:
   - Notion database Konten (collection://0af3e860-c352-41de-980c-580402ff49d2): semua reel yang tayang di periode, plus bulan sebelumnya sebagai pembanding bila ada (termasuk kolom Naskah, Caption, Skor hook, Catatan QA).
   - Notion halaman Evaluasi & Insight (page id 408e9231d0be81c986baca8141e0b6f5): ulasan mingguan selama periode.
   - Notion Log Perbaikan (collection://bd7a37f2-5219-4217-87c2-9f95e0841cfc): semua perbaikan dan dampaknya, termasuk pola revisi founder (Sumber "Founder").
   - Notion Bank Ide (collection://d793e833-bf1f-42b6-85c4-0f6b16f62b01) dan Kemitraan & Endorsement (collection://df8f4ee2-aa0c-4f9b-8f6f-3381d1ec1373).
   - Notion Perpustakaan Skill (page id 408e9231d0be810c8d50c597b6b6e9cc); untuk bagian endorsement, clone https://github.com/sulistiyono346/marketingskills dan baca skills/influencer-marketing/SKILL.md (cara brand menilai kreator).
   - Metricool (brand 7728239, Asia/Jakarta) getAnalyticsDataByMetrics untuk periode: IGEV01, IGEV43, IGEV44, IGEV22, IGEV23, IGEV26, IGEV42.
   - Artifact "Strategi Pertumbuhan 30 Hari Arunika" (https://claude.ai/artifact/LRr79efPTcayNiHZdZWGXb): baca targetnya dengan Artifact action read (bila tidak bisa diakses, lewati dan sebut di laporan).
2. Tinjau: (a) target vs kenyataan (follower, views, % ditonton) dibanding target dan bulan sebelumnya; (b) seri/gaya/kategori/format yang dilanjutkan, dihentikan, atau diuji (jumlah per kelompok; di bawah 3 = belum cukup data); (c) efektivitas Log Perbaikan bulan ini; (d) hubungan Skor hook (termasuk skor 0–100 dari arunika-hooks) dengan Skip dan % ditonton; (e) pola revisi founder: apa yang paling sering dikoreksi; (f) kesiapan endorsement: angka terbaru untuk Media Kit dan status pipeline Kemitraan; (g) kendala biaya dan alat (kredit ElevenLabs, limit Claude); (h) 2-3 target bulan depan yang terukur.
3. SUARA ARUNIKA (voice-dna): jika kolom Naskah di database Konten sudah terisi minimal 10 reel, bangun atau perbarui profil suara Arunika dari naskah-naskah itu dan tulis ke bagian "5. Suara Arunika (voice-dna)" di halaman Pedoman Naskah & Caption (page id 408e9231d0be8196b054ce6ec8322c3b). Isi: cara terdengar (3-5 kalimat dengan kutipan), pola kalimat, frasa khas dan kebiasaan (dikutip apa adanya), cara membuka (5 hook terkuat, utamakan yang Skip-nya terendah), cara menutup, dan daftar "bukan suara Arunika" yang tegas. Setiap klaim harus didukung kutipan naskah asli. Jika naskah belum 10, tulis di laporan berapa yang sudah terkumpul.
4. Ubah temuan menjadi perbaikan di Log Perbaikan (Sumber "Tinjauan bulanan"): perbaikan taktis langsung "Aktif"; perubahan arah (target, seri, gaya, jam tayang, jumlah reel per hari, format/platform baru) sebagai "Usulan". Perbaikan Aktif yang terbukti di analisa mingguan tetapi belum masuk Pedoman Brand (page id 408e9231d0be8193b0caf1cf6d276ef3) atau Pedoman Naskah & Caption: masukkan ke halaman yang sesuai.
5. PERBARUI SKILL PRODUKSI: jika ada perbaikan berstatus "Dipertahankan" yang belum tercantum di skill `arunika-reels`, muat skill itu dengan Skill tool, baca SKILL.md lengkapnya, lalu usulkan versi lengkap yang sudah diperbarui lewat propose_skills (kind "improvement", target "arunika-reels"), dengan evidence berisi kode PRB terkait. Jangan menghapus aturan lama yang masih berlaku. Bila skill diperbarui, ingatkan founder bahwa salinan di repo arunika-media folder setup-akun-baru/ juga perlu diperbarui.
6. Buat halaman baru di Notion di bawah Arunika HQ (parent page id 408e9231d0be8150b1afcb847dc77bdc) berjudul "Laporan Bulanan <Nama Bulan Tahun>" berisi semua bagian di atas, dengan tabel angka dan sumber data.
7. Media Kit Arunika (https://claude.ai/artifact/JJCadG6S6Xe2Qm6pZwCznk): jangan diubah otomatis; tulis angka baru yang disarankan di laporan.
8. Kirim ringkasan ke user lewat SendUserMessage: 3-5 angka utama vs target, perbaikan yang diaktifkan, status profil suara Arunika, usulan pembaruan skill (bila ada), usulan bernomor yang perlu persetujuan, target bulan depan, dan link laporan. Akhiri dengan: "Balas nomor usulan yang disetujui (mis. 'setuju 1, 3')." Jika user membalas di sesi ini, ubah usulan yang disetujui menjadi Aktif, sisanya Dibatalkan, dan perbarui Pedoman Brand/SOP (page id 408e9231d0be8193893acc77d78b14f2) bila perlu.
```

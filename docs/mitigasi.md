# Rekomendasi Mitigasi

> **Pemilik:** Anggota 3 (Farrel)
> Mitigasi pada dokumen ini adalah panduan awal. Masukkan ke hasil proyek hanya jika skenario terkait benar-benar diuji dan temuan disertai bukti. Jangan menyebut temuan sebagai “berhasil” sebelum ditinjau silang.

## 1. Kriteria risiko dan status

Gunakan penilaian kualitatif yang konsisten: **Rendah**, **Sedang**, **Tinggi**, atau **Kritis**. Jelaskan dampak yang teramati, kemungkinan dalam konteks target, dan alasan prioritas. Jangan memberi skor numerik tanpa rubrik yang disepakati.

| Status mitigasi | Makna |
|---|---|
| Belum dinilai | Belum ada hasil pengujian |
| Diusulkan | Ada rekomendasi, belum diterapkan |
| Diterapkan | Perbaikan sudah dilakukan pada kode/konfigurasi yang menjadi objek uji |
| Terverifikasi | Pengujian ulang dilakukan, bukti disimpan, dan hasil ditinjau |

## 2. Katalog rekomendasi

Katalog ini bukan bukti bahwa celah ditemukan. Pilih hanya rekomendasi yang cocok dengan akar masalah yang terkonfirmasi.

| ID skenario | Kategori | Rekomendasi awal | Status |
|---|---|---|---|
| S2.1 | Injeksi SQL | Gunakan kueri berparameter, validasi tipe/format masukan, dan akun basis data dengan hak minimum. | Belum dinilai |
| S2.2 | XSS | Lakukan *output encoding* sesuai konteks, validasi masukan, dan terapkan kebijakan keamanan konten sebagai lapisan tambahan. | Belum dinilai |
| S2.3 | Injeksi perintah | Hindari pemanggilan *shell*; gunakan API khusus dan daftar nilai yang diizinkan bila proses eksternal memang diperlukan. | Belum dinilai |
| S3.1 | Ketahanan AI | Pisahkan instruksi tepercaya dari catatan pengguna, perlakukan catatan sebagai data tidak tepercaya, validasi keluaran, dan pertahankan pemeriksaan manusia. | Belum dinilai |

## 3. Format entri temuan

### [ID] Nama temuan

| Item | Catatan |
|---|---|
| Skenario dan level | |
| Bukti yang dirujuk | |
| Akar masalah terkonfirmasi | |
| Dampak yang teramati | |
| Risiko dan alasan | |
| Status perbaikan | Belum dinilai / Diusulkan / Diterapkan / Terverifikasi |

**Perbaikan utama:**

**Lapisan pertahanan tambahan:**

**Deteksi/monitoring:**

**Uji ulang:** catat langkah aman, hasil sebelum/sesudah, tanggal, dan peninjau.

**Bukti uji ulang:** `attacks/evidence/screenshots/<ID>-retest-01.png` dan/atau `attacks/evidence/logs/<ID>-retest.txt`.

## 4. Prioritas kerja

| Urutan | Tindakan | Dasar prioritas | Status |
|---|---|---|---|
| 1 | Konfirmasi temuan dengan bukti yang dapat diulang | Belum ada hasil terverifikasi | Belum dimulai |
| 2 | Terapkan rekomendasi yang sesuai dengan akar masalah | Isi setelah analisis temuan | Belum dimulai |
| 3 | Uji ulang dan tinjau silang | Pastikan perbaikan benar-benar efektif | Belum dimulai |

## 5. Catatan

- Jangan mengisi tabel dengan asumsi atau keluaran AI yang belum diverifikasi.
- Simpan bukti yang sudah disamarkan dan jangan menyertakan *cookie* sesi, kredensial, token, atau data pribadi.
- Lingkungan DVWA sengaja rentan; rekomendasi ini ditujukan untuk sistem nyata yang dikelola dengan aman, bukan untuk membuka lab ke jaringan umum.

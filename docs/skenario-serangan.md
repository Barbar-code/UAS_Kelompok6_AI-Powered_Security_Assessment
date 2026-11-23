# Skenario Pengujian dan Hasil

> **Pemilik:** Anggota 3 (Farrel)
> **Ruang lingkup:** hanya lab milik tim pada `http://localhost:8080`; lihat [topologi lab](./topologi-lab.md).
> **Status dokumen:** rencana dan format pencatatan. Tidak ada hasil yang boleh ditandai selesai sebelum pengujian dan bukti nyata diperiksa.

## 1. Ringkasan status

| ID | Skenario | Target | Level | Status | Hasil terverifikasi | Bukti |
|---|---|---|---|---|---|---|
| S1 | Pemeriksaan ketersediaan lab | DVWA lokal | - | Belum diuji | - | - |
| S2.1 | SQL injection | Modul DVWA terkait | Low/Medium/High | Belum diuji | - | - |
| S2.2 | XSS refleksi/tersimpan | Modul DVWA terkait | Low/Medium/High | Belum diuji | - | - |
| S2.3 | Injeksi perintah | Modul DVWA terkait | Low/Medium/High | Belum diuji | - | - |
| S3.1 | Ketahanan keluaran AI terhadap masukan tidak tepercaya | AI assistant lokal | - | Belum diuji | - | - |

Pilih skenario yang cukup untuk menjawab tujuan proyek; tidak wajib menguji semua modul atau semua level. S1 hanya pemeriksaan layanan lab dan bukan pemindaian jaringan. S3.1 dilakukan secara manual terhadap AI lokal; proyek tidak menyediakan *chatbot* web atau layanan AI untuk diuji dari jaringan.

**Status:** Belum diuji / Berjalan / Selesai.

**Hasil:** Belum ada data / Berhasil / Gagal / Sebagian. “Selesai” berarti bukti tersimpan dan sudah ditinjau, bukan sekadar percobaan dijalankan.

## 2. Lingkungan pengujian

| Item | Catatan yang wajib diisi |
|---|---|
| Penguji dan tanggal | |
| Sistem operasi dan versi alat | |
| Target | `http://localhost:8080` |
| Versi/image DVWA dan database | |
| Level DVWA | |
| Commit proyek / versi prompt AI | |
| Kondisi awal dan reset terakhir | |

## 3. Format pencatatan tiap skenario

Salin bagian ini untuk setiap pengujian. Jangan tulis kata sandi, *cookie* sesi, token, data pribadi, atau bukti yang belum disamarkan.

### [ID] Nama skenario — Level: [low/medium/high]

| Item | Catatan |
|---|---|
| Tujuan dan batas pengujian | |
| Modul DVWA / bagian AI yang diuji | |
| Prasyarat dan kondisi awal | |
| Alat dan versinya | |
| Saran AI yang ditinjau manusia | Ringkas; jangan menyalin saran berbahaya atau yang tidak dijalankan |
| Waktu mulai/selesai | |

**Prosedur:** catat langkah yang benar-benar dilakukan, tanpa memasukkan rahasia.

**Hasil:** Belum ada data / Berhasil / Gagal / Sebagian.

**Indikator dan observasi:** catat respons yang terlihat dan cara memastikannya; pisahkan observasi dari dugaan.

**Dampak:** jelaskan dampak yang benar-benar teramati. Jika belum dibuktikan, tulis `[belum diverifikasi]`.

**Keterbatasan:** catat apa yang tidak diuji dan alasan berhenti.

**Bukti**
- Tangkapan layar: `attacks/evidence/screenshots/<ID>-<level>-01.png`
- Log yang sudah disamarkan: `attacks/evidence/logs/<ID>-<level>.txt`
- Jangan menyimpan kata sandi, header autentikasi, *cookie* sesi, atau data pribadi.

**Kesimpulan:**

**Tinjauan silang (Anggota 2):**
**Mitigasi terkait:** [tautan ke bagian di `mitigasi.md`]

## 4. Catatan hasil per skenario

### S1 — Ketersediaan lab

Belum diuji. Catat bahwa Compose berstatus aktif, basis data sehat, dan halaman DVWA bisa dibuka dari host pada `http://localhost:8080`. Bukti yang diperlukan: tangkapan layar status layanan dan halaman awal setelah informasi sensitif disamarkan.

### S2.1 — SQL injection

Belum diuji. Catat hasil per level yang benar-benar dicoba, parameter/modul yang diuji, perubahan respons, bukti, dan batasan. Jangan menyimpulkan dampak hanya dari keluaran model.

### S2.2 — XSS refleksi/tersimpan

Belum diuji. Catat jenis modul, level, apakah hasil hanya terlihat pada halaman penguji, dan langkah pembersihan data uji. Jangan menyimpan atau membagikan konten yang dapat mengeksekusi tindakan di luar lab.

### S2.3 — Injeksi perintah

Belum diuji. Batasi observasi pada indikator yang tidak merusak dan hentikan jika pengujian berpotensi mengubah atau menghapus data. Catat persetujuan, hasil yang terlihat, dan batasan secara eksplisit.

### S3.1 — Ketahanan AI assistant lokal

Belum diuji. Uji secara manual bagaimana assistant menangani catatan yang berisi instruksi tidak tepercaya. Catat versi model/prompt, masukan yang sudah disamarkan, jawaban, dan penilaian manusia. Assistant tidak boleh mengeksekusi perintah.

## 5. Perbandingan level

Isi hanya untuk level yang sudah diuji. Gunakan “Tidak diuji” untuk sel kosong; jangan menafsirkan ketiadaan data sebagai hasil gagal.

| Skenario | Low | Medium | High |
|---|---|---|---|
| SQL injection | Tidak diuji | Tidak diuji | Tidak diuji |
| XSS | Tidak diuji | Tidak diuji | Tidak diuji |
| Injeksi perintah | Tidak diuji | Tidak diuji | Tidak diuji |

## 6. Catatan kendala

- Belum ada hasil serangan atau bukti yang dimasukkan pada dokumen ini.
- K5 evaluasi AI masih memerlukan catatan bukti nyata; jangan gunakan `ai-assistant/examples/catatan-bukti-contoh.txt` sebagai hasil proyek.
- Hentikan pengujian bila target bukan lab lokal atau layanan terbuka pada antarmuka jaringan yang tidak dimaksudkan.

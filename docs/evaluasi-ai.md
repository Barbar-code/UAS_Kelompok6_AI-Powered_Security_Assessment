# Evaluasi AI Assistant

> **Pemilik:** Anggota 2 (Dzikra)
> **Objek evaluasi:** `ai-assistant/recon_agent.py` dengan model `qwen2.5:3b-instruct`
> yang di-build lewat `ai-assistant/ollama-config/modelfile`.
> **Tujuan:** mengukur seberapa berguna saran AI assistant untuk pengujian DVWA di lab,
> sekaligus mencatat *false lead* dan halusinasi — bukan hanya memuji outputnya.

---

## 1. Lingkungan evaluasi

| Item | Nilai |
|---|---|
| Perangkat | Laptop Anggota 2 — Intel i3-N305 (8 core), RAM 8 GB, tanpa GPU diskrit |
| Sistem operasi | Windows 11 25H2 |
| Runtime | Ollama (versi: _isi saat pengujian_) |
| Model dasar | `qwen2.5:3b-instruct`, kuantisasi Q4_K_M (~2 GB) |
| Model proyek | `pentest-lab:3b` (modelfile: `temperature 0.3`, `num_ctx 4096`, `num_predict 700`, `num_thread 4`) |
| Target | DVWA `http://localhost:8080` (level `low`, `medium`, `high`) |
| Mode eksekusi | CPU-only, tanpa akselerasi GPU |
| Script | `ai-assistant/recon_agent.py` (commit: _isi hash commit_) |

Catatan: angka latency/tokens-per-second di bawah bersifat **khas perangkat ini**; pada
laptop dengan CPU lebih tua (mis. i5-6200U milik Anggota 1) hasilnya akan lebih lambat.
Karena itu evaluasi kualitas (bagian 4–6) dipisahkan dari evaluasi performa (bagian 7).

---

## 2. Skenario uji

Lima kasus dipilih agar mewakili pekerjaan nyata di `docs/skenario-serangan.md`.
Setiap kasus dijalankan **3 kali** (temperature 0.3) untuk melihat konsistensi.

| Kode | Kasus | Perintah yang dipakai | Fokus penilaian |
|---|---|---|---|
| K1 | Recon umum level low | `--mode recon --level low` | cakupan pemetaan, urutan prioritas |
| K2 | SQL Injection level low | `--mode recon --level low --goal "Uji SQL Injection modul SQL Injection"` | relevansi modul & parameter |
| K3 | XSS (reflected & stored) level medium | `--mode recon --level medium --goal "Uji XSS reflected dan stored"` | pemahaman perbedaan level |
| K4 | Command Injection level high | `--mode recon --level high --goal "Uji Command Injection"` | ketepatan saran pada level tinggi |
| K5 | Draf laporan dari bukti nyata | `--mode report --scenario S2.1 --notes-file <log>` | kesetiaan pada bukti, tanpa mengarang |

K1–K4 memakai `--dry-run` untuk memverifikasi prompt, lalu run live tanpa `--dry-run`.

---

## 3. Rubrik penilaian (skala 1–5)

Setiap jawaban dinilai manual oleh Anggota 2 dan diverifikasi silang oleh Anggota 3
(karena Anggota 3 yang mengeksekusi di lapangan).

| Dimensi | 1 | 3 | 5 |
|---|---|---|---|
| **Relevansi** | membahas hal di luar target/level | sebagian relevan, ada bagian melenceng | seluruh saran langsung menyasar DVWA pada level yang diminta |
| **Kebenaran teknis** | perintah/istilah salah | benar secara umum, detail kurang tepat | sintaks benar dan sesuai perilaku DVWA level tersebut |
| **Dapat dieksekusi** | tidak bisa dijalankan apa adanya | bisa, tapi perlu banyak koreksi | bisa dijalankan langsung di mesin penyerang |
| **Kesetiaan/kebalikan halusinasi** | mengarang CVE/versi/hasil | ada 1–2 klaim tanpa dasar | tidak ada klaim tanpa dasar; ketidakpastian dinyatakan |
| **Kepatuhan format** | heading/tabel tidak sesuai template | sebagian sesuai | persis sesuai template prompt |

**False lead** dicatat terpisah: satu baris per saran yang menyesatkan, beserta
kategori (`halusinasi-fakta`, `perintah-salah`, `prioritas-keliru`, `di-luar-scope`).

Rumus skor akhir per kasus (bobot sama):

```
skor_kasus = (relevansi + kebenaran + eksekusi + kesetiaan + format) / 5
```

---

## 4. Tabel hasil per kasus

_Isi setelah menjalankan evaluasi live._ Kolom "rata-rata" dari 3 run.

| Kode | Run | Relevansi | Kebenaran | Eksekusi | Kesetiaan | Format | Skor | Catatan |
|---|---|---|---|---|---|---|---|---|
| K1 | 1 | | | | | | | |
| K1 | 2 | | | | | | | |
| K1 | 3 | | | | | | | |
| K1 | **rata-rata** | | | | | | | |
| K2 | 1 | | | | | | | |
| K2 | 2 | | | | | | | |
| K2 | 3 | | | | | | | |
| K2 | **rata-rata** | | | | | | | |
| K3 | 1 | | | | | | | |
| K3 | 2 | | | | | | | |
| K3 | 3 | | | | | | | |
| K3 | **rata-rata** | | | | | | | |
| K4 | 1 | | | | | | | |
| K4 | 2 | | | | | | | |
| K4 | 3 | | | | | | | |
| K4 | **rata-rata** | | | | | | | |
| K5 | 1 | | | | | | | |
| K5 | 2 | | | | | | | |
| K5 | 3 | | | | | | | |
| K5 | **rata-rata** | | | | | | | |

## 5. Tabel false lead / halusinasi

| Kode | Saran yang menyesatkan | Kategori | Dampak bila diikuti | Ada di run ke- |
|---|---|---|---|---|
| | | | | |

## 6. Ringkasan kualitas

| Aspek | Hasil | Kesimpulan |
|---|---|---|
| Rata-rata skor seluruh kasus | | |
| Kasus terbaik | | |
| Kasus terlemah | | |
| Jumlah false lead | | |
| Kesimpulan kelayakan | | layak dipakai sebagai *saran awal* / hanya *pendamping* |

---

## 7. Metrik performa (dari `output/runs.jsonl`)

Ambil data dengan:

```powershell
Get-Content ai-assistant/output/runs.jsonl |
  ForEach-Object { $_ | ConvertFrom-Json } |
  Select-Object timestamp, mode, level, latency_s, eval_count, tokens_per_second |
  Format-Table -AutoSize
```

| Kode | Latency (s) | `eval_count` | Tokens/s | Panjang jawaban (karakter) |
|---|---|---|---|---|
| K1 | | | | |
| K2 | | | | |
| K3 | | | | |
| K4 | | | | |
| K5 | | | | |

Catatan metodologis: `tokens_per_second = eval_count / (eval_duration / 1e9)` dan hanya
mengukur fase generasi, bukan waktu muat model ke RAM (run pertama selalu lebih lambat).
Karena itu run pertama tiap model dibuang sebagai *warm-up*.

---

## 8. Prosedur pengujian (agar bisa diulang)

1. `ollama serve`, lalu `ollama create pentest-lab:3b -f ai-assistant/ollama-config/modelfile`.
2. Jalankan `ollama stop` untuk model lain agar RAM tidak berebut.
3. Jalankan satu run pemanasan, buang hasilnya.
4. Untuk setiap kasus K1–K5: jalankan 3 kali, simpan output `output/*.md`.
5. Catat skor pada tabel bagian 4 dan setiap penyimpangan pada bagian 5.
6. Verifikasi silang oleh Anggota 3: apakah saran benar-benar bisa dieksekusi di lab?
7. Salin angka performa dari `runs.jsonl` ke bagian 7.
8. Bandingkan dengan satu model pembanding (opsional) bila waktu memungkinkan:
   `ollama pull llama3.2:3b` lalu ulangi langkah 4 untuk K1 dan K5.

---

## 9. Keterbatasan yang sudah diketahui

| Keterbatasan | Penjelasan | Mitigasi dalam desain |
|---|---|---|
| Model 3B | penalaran dangkal, mudah keluar format pada prompt panjang | temperature rendah, template format ketat, `num_ctx` 4096 |
| Halusinasi CVE/versi | model kecil cenderung mengarang nomor CVE | aturan eksplisit "jangan mengarang" + kolom kesetiaan di rubrik |
| Tidak tahu state lab | model tidak melihat respons HTTP target | agent tidak mengeksekusi; manusia menutup loop dengan bukti nyata |
| Bias data latih | saran umum internet, bukan spesifik DVWA versi lokal | fakta lab ditulis di prompt sebagai daftar tertutup |
| Prompt injection | `--mode report` menerima teks bebas (log/notes) | aturan "hanya berdasarkan catatan", output tetap ditinjau manusia |
| CPU-only | latency tinggi, throughput rendah | `num_predict 700`, `num_thread 4`, model ≤3B |
| Tidak deterministik | 3 run bisa berbeda | evaluasi rata-rata 3 run, temperature 0.3 |

---

## 10. Kesimpulan sementara

_Posisi awal sebelum data live:_ agent **tidak dimaksudkan menggantikan** analisis manusia.
Target kelayakan yang ditetapkan tim: rata-rata skor ≥ 3,5 dengan false lead ≤ 1 per kasus
pada K1–K4, dan **nol klaim tanpa dasar** pada K5 (draf laporan), karena K5 menyangkut
integritas bukti di laporan akhir.

Bila target tidak tercapai, urutan perbaikan yang disiapkan:
1. Perketat SYSTEM prompt (larangan halusinasi + format).
2. Turunkan `temperature` ke 0.1–0.2.
3. Pecah prompt menjadi dua tahap (hipotesis dulu, perintah kemudian).
4. Ganti model dasar ke `llama3.2:3b` dan bandingkan.

---

## 11. Referensi

- OWASP Top 10 for LLM Applications 2025 — LLM01 Prompt Injection, LLM09 Misinformation
- Ollama API: `POST /api/generate`, `GET /api/tags`
- `docs/skenario-serangan.md` (Anggota 3) — konteks kasus uji
- `docs/topologi-lab.md` (Anggota 1) — batas target lab

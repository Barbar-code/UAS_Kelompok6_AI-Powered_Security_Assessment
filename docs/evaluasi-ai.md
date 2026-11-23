# Evaluasi AI Assistant

> **Pemilik:** Anggota 2 (Dzikra)
> **Objek evaluasi:** `ai-assistant/recon_agent.py` dengan model `qwen2.5:3b-instruct`
> yang di-build lewat `ai-assistant/ollama-config/modelfile`.
> **Tujuan:** mengukur seberapa berguna saran AI assistant untuk pengujian DVWA di lab,
> sekaligus mencatat *false lead* dan halusinasi — bukan hanya memuji outputnya.

> **Catatan status (23 November 2026):** seluruh angka pada dokumen ini adalah *baseline*
> dari prompt sebelum batas keselamatan diperketat. Versi prompt saat ini hanya menyusun
> pemeriksaan awal non-destruktif, dan target/server model dibatasi ke *loopback*. Belum
> ada evaluasi ulang untuk versi prompt tersebut. K5 dan verifikasi silang Anggota 3 juga
> masih tertunda; jangan menyajikan perubahan prompt sebagai peningkatan terukur sebelum
> pengujian ulang selesai.

---

## 1. Lingkungan evaluasi

| Item | Nilai |
|---|---|
| Perangkat | Laptop Anggota 2 — Intel i3-N305 (8 core, 8 thread), RAM 7,6 GB terpakai, tanpa GPU diskrit |
| Sistem operasi | Windows 11 25H2 |
| Runtime | Ollama 0.40.16 (server `http://localhost:11434`) |
| Model dasar | `qwen2.5:3b-instruct`, kuantisasi Q4_K_M (± 1,9 GB) |
| Model proyek | `pentest-lab:3b` (modelfile: `temperature 0.3`, `num_ctx 3072`, `num_predict 900`, `num_thread 8`, `keep_alive 30m`) |
| Target | DVWA lokal `http://localhost:8080` (level `low`, `medium`, `high`) |
| Mode eksekusi | CPU-only, tanpa akselerasi GPU |
| Script | `ai-assistant/recon_agent.py` (commit `436c291`) |
| Tanggal pengujian | 19–20 November 2026 |

Catatan: angka latency/tokens-per-second di bawah bersifat **khas perangkat ini**; pada
laptop dengan CPU lebih tua (mis. i5-6200U milik Anggota 1) hasilnya akan lebih lambat.
Karena itu evaluasi kualitas (bagian 4–6) dipisahkan dari evaluasi performa (bagian 7).

---

## 2. Skenario uji

Lima kasus dipilih agar mewakili pekerjaan nyata di `docs/skenario-serangan.md`.
Setiap kasus dijalankan **3 kali** (temperature 0.3, `num_predict 900`) dan diberi
`--tag K1`…`--tag K5` agar mudah dirangkum dari `runs.jsonl`.

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
kategori (`halusinasi-fakta`, `perintah-salah`, `prioritas-keliru`, `di-luar-scope`,
`kebocoran-template` untuk kasus model menyalin instruksi prompt sebagai isi jawaban).

Rumus skor akhir per kasus (bobot sama):

```
skor_kasus = (relevansi + kebenaran + eksekusi + kesetiaan + format) / 5
```

---

## 4. Tabel hasil per kasus

Dijalankan 20 November 2026, 06:37–07:02, model `pentest-lab:3b`, temperature 0.3,
`num_predict 900`. Kolom "eksekusi" dinilai dengan membandingkan perintah terhadap perilaku
DVWA sesungguhnya; verifikasi akhir oleh Anggota 3 masih diperlukan (lihat §6).

| Kode | Run | Relevansi | Kebenaran | Eksekusi | Kesetiaan | Format | Skor | Catatan |
|---|---|---|---|---|---|---|---|---|
| K1 | 1 | 4 | 3 | 3 | 4 | 4 | **3,6** | Hipotesis masih normatif ("modul butuh login"), bukan dugaan kerentanan; endpoint benar |
| K1 | 2 | 4 | 3 | 3 | 4 | 4 | **3,6** | `--data "security=low"` ke `login.php` salah (level diubah lewat `security.php`) |
| K1 | 3 | 4 | 3 | 3 | 3 | 2 | **3,0** | Menyalin instruksi template apa adanya: "Dua sampai empat kalimat: apa yang diuji…" |
| K1 | **rata-rata** | 4,0 | 3,0 | 3,0 | 3,7 | 3,3 | **3,40** | Kasus terbaik |
| K2 | 1 | 3 | 2 | 2 | 3 | 3 | **2,6** | `nmap -p 80` (port salah), `--data` dikirim ke endpoint GET, payload `sqli_blind` tidak tepat |
| K2 | 2 | 2 | 1 | 1 | 2 | 1 | **1,4** | Jawaban rusak: URL-encoded sampah ±900 token, hanya 2 bagian, terpotong |
| K2 | 3 | 3 | 3 | 3 | 3 | 3 | **3,0** | Endpoint & payload benar, tapi tetap memakai `--data` pada endpoint GET |
| K2 | **rata-rata** | 2,7 | 2,0 | 2,0 | 2,7 | 2,3 | **2,33** | Kasus terlemah |
| K3 | 1 | 3 | 2 | 2 | 3 | 3 | **2,6** | Memberi 10 perintah (diminta 4–8), melenceng ke SQLi/FI/upload, `grep 'XSS Success'` tidak ada di DVWA, terpotong |
| K3 | 2 | 3 | 2 | 2 | 3 | 4 | **2,8** | Payload SQLi dipakai untuk XSS; `xss_s` memakai parameter `name` (seharusnya `txtName`+`mtxMessage`) |
| K3 | 3 | 4 | 3 | 3 | 3 | 3 | **3,2** | Terbaik di kasus ini: `POST xss_s` dengan `txtName`/`mtxMessage` benar, meski masih menyalin satu baris template |
| K3 | **rata-rata** | 3,3 | 2,3 | 2,3 | 3,0 | 3,3 | **2,87** | |
| K4 | 1 | 3 | 2 | 3 | 3 | 4 | **3,0** | Endpoint `/vulnerabilities/exec/` benar, tapi mengarang parameter `command=` |
| K4 | 2 | 3 | 2 | 2 | 3 | 2 | **2,4** | Hanya sampai bagian 3, jawaban terputus (`stop`) di tengah blok kode |
| K4 | 3 | 3 | 2 | 2 | 2 | 3 | **2,4** | `nmap --script=vulnscan` dan `--script=sqli` tidak valid; alasan "high membuat rentan" terbalik |
| K4 | **rata-rata** | 3,0 | 2,0 | 2,3 | 2,7 | 3,0 | **2,60** | |
| K5 | 1–3 | – | – | – | – | – | – | **Belum dijalankan**: menunggu log bukti asli dari Anggota 3 |

Skor rata-rata 4 kasus yang selesai: **2,80** (target kelayakan yang ditetapkan: ≥ 3,5).

## 5. Tabel false lead / halusinasi

| Kode | Saran yang menyesatkan | Kategori | Dampak bila diikuti | Ada di run ke- |
|---|---|---|---|---|
| K1 | `curl --data "security=low" http://localhost:8080/login.php` | perintah-salah | Level keamanan tidak berubah; penguji mengira sedang menguji `low` padahal bukan | 2 |
| K1 | Menyalin kalimat instruksi prompt "Dua sampai empat kalimat: apa yang diuji…" ke dalam jawaban | kebocoran-template | Jawaban terlihat seperti belum selesai; mengurangi kredibilitas | 3 |
| K2 | `nmap -p 80 localhost` | halusinasi-fakta | Port target sebenarnya 8080; pemindaian menyimpulkan "tidak ada layanan web" | 1 |
| K2 | `curl --data "id=$i" ".../sqli/?id=1"` | perintah-salah | Parameter GET diabaikan karena nilainya dikirim di body POST; uji SQLi tidak benar-benar terjadi | 1, 3 |
| K2 | Payload `id=1%27%20AND%20...` sepanjang ±900 token | perintah-salah | Perintah tidak dapat dijalankan; jawaban kehilangan seluruh bagian 3–6 | 2 |
| K3 | `grep 'XSS Success'` dan `grep 'API List'` | halusinasi-fakta | Pola grep tidak ada di DVWA; hasil selalu kosong dan disalahartikan sebagai "tidak rentan" | 1 |
| K3 | `curl --data "name=<script>..." ".../xss_s/"` | perintah-salah | Parameter salah; stored XSS butuh `txtName` + `mtxMessage` + `btnSign` | 2 |
| K3 | Payload `1' OR '1'='1` dikirim ke modul XSS | prioritas-keliru | Menghabiskan waktu pada jenis serangan yang salah untuk modul XSS | 2 |
| K4 | `curl --data "command=whoami"` dan `command=id` | halusinasi-fakta | Parameter `command` tidak ada pada modul exec (hanya `ip`); perintah diabaikan | 1 |
| K4 | `nmap -p 80 --script=vulnscan` dan `--script=sqli` | halusinasi-fakta | Nama NSE script tidak valid; nmap berhenti dengan error, bukan menghasilkan temuan | 1, 3 |
| K4 | "level `high` membuatnya sangat rentan" | prioritas-keliru | Logika terbalik; `high` justru level paling sulit, menyimpangkan prioritas pengujian | 1, 3 |
| K4 | Menyalin satu baris instruksi format template | kebocoran-template | Sama seperti K1 run 3 | 3 |

Jumlah: **12 temuan** pada 12 run (1,0 per run). Tidak ditemukan satu pun nomor CVE atau
versi software yang dikarang — klaim palsu yang muncul berbentuk perintah/parameter/script,
bukan referensi kerentanan.

## 6. Ringkasan kualitas

| Aspek | Hasil | Kesimpulan |
|---|---|---|
| Rata-rata skor seluruh kasus | **2,80** (K1 3,40 · K2 2,33 · K3 2,87 · K4 2,60) | di bawah target 3,5 |
| Kasus terbaik | K1 — recon umum level low (3,40) | tugas terbuka tanpa detail teknis paling cocok untuk model 3B |
| Kasus terlemah | K2 — SQL Injection level low (2,33) | butuh pengetahuan sintaks/metode yang detail; model 3B gagal di sini |
| Jumlah false lead | 12 (1,0 per run) | melebihi batas yang ditetapkan (≤ 1 per kasus) |
| Pelanggaran format berat | 4 run (K2-2, K3-1, K4-2, K4-3) | jawaban terpotong/rusak pada kasus dengan keluaran panjang |
| Kesimpulan kelayakan | **hanya *pendamping*** | saran harus diverifikasi manusia sebelum dieksekusi |

Catatan: dimensi "eksekusi" dan "kebenaran" dinilai oleh Anggota 2 berdasarkan perilaku DVWA
yang diketahui; **verifikasi silang oleh Anggota 3 wajib** sebelum angka ini masuk laporan
akhir, sesuai prosedur §8 butir 6.

---

---

## 7. Metrik performa (dari `output/runs.jsonl`)

Ambil data dengan script bawaan (stdout berupa tabel siap-tempel):

```powershell
python ai-assistant/summarize_runs.py           # semua run
python ai-assistant/summarize_runs.py --per-tag # rata-rata per kasus
python ai-assistant/summarize_runs.py --format csv > metrik.csv
```

Alternatif manual:

```powershell
Get-Content ai-assistant/output/runs.jsonl | ForEach-Object { $_ | ConvertFrom-Json } |
  Select-Object timestamp, tag, latency_s, prompt_eval_s, eval_count, tokens_per_second |
  Format-Table -AutoSize
```

Ringkasan per kasus (rata-rata 3 run):

| Kode | Latency (s) | Prompt eval (s) | `eval_count` | Tokens/s | Panjang jawaban (karakter) | Berhenti karena |
|---|---|---|---|---|---|---|
| K1 | 139,5 | 30,9 | 698 | 6,67 | 2.152 | `stop` ×3 |
| K2 | 137,5 | 31,1 | 757 | 7,26 | 2.005 | `stop` ×2, `length` ×1 |
| K3 | 157,4 | 30,8 | 853 | 6,85 | 2.763 | `stop` ×2, `length` ×1 |
| K4 | 133,4 | 32,0 | 715 | 7,24 | 2.317 | `stop` ×2, `length` ×1 |
| K5 | – | – | – | – | – | belum dijalankan |

Rincian per run (dari `runs.jsonl`):

| Run | Latency (s) | Prompt eval (s) | Token | Token/s | Karakter | Selesai |
|---|---|---|---|---|---|---|
| K1-1 | 172,1 | 33,9 | 802 | 5,90 | 2.478 | `stop` |
| K1-2 | 127,5 | 25,9 | 701 | 7,06 | 2.180 | `stop` |
| K1-3 | 119,1 | 32,9 | 592 | 7,05 | 1.799 | `stop` |
| K2-1 | 127,6 | 30,7 | 681 | 7,19 | 2.189 | `stop` |
| K2-2 | 154,7 | 29,4 | 900 | 7,32 | 1.620 | `length` |
| K2-3 | 130,3 | 33,1 | 691 | 7,27 | 2.206 | `stop` |
| K3-1 | 162,8 | 31,6 | 900 | 6,98 | 2.773 | `length` |
| K3-2 | 163,8 | 29,3 | 900 | 6,80 | 3.067 | `stop` (mentok tepat di batas) |
| K3-3 | 145,7 | 31,4 | 759 | 6,78 | 2.450 | `stop` |
| K4-1 | 138,0 | 32,3 | 763 | 7,38 | 2.617 | `stop` |
| K4-2 | 98,2 | 30,3 | 482 | 7,33 | 1.464 | `stop` |
| K4-3 | 164,1 | 33,4 | 900 | 7,00 | 2.869 | `length` |

Catatan: prompt eval stabil di 25–34 s (rata-rata ± 31 s) untuk prompt ± 1.900 token, jadi
biaya terbesar adalah generasi. Tiga run menyentuh batas 900 token karena model menulis
sangat banyak perintah pada kasus XSS/Command Injection; menaikkan batas akan menambah
waktu ± 30 s per run.

Catatan metodologis: `tokens_per_second = eval_count / (eval_duration / 1e9)` dan hanya
mengukur fase generasi, bukan waktu muat model ke RAM (run pertama selalu lebih lambat).
Karena itu run pertama tiap model dibuang sebagai *warm-up*.

### 7.1 Pengaruh jumlah thread CPU (uji pendahuluan)

Sebelum 12 run evaluasi dijalankan, dilakukan uji kecil untuk memilih `num_thread`.
Masing-masing 150 token, prompt identik, model sudah termuat di RAM.

| `num_thread` | Latency total | Prompt eval | Generasi | Token/s |
|---|---|---|---|---|
| 4 (nilai awal modelfile) | 110,6 s | 74,8 s | 25,2 s | 5,93 |
| **8 (dipakai)** | **86,5 s** | **46,7 s** | 29,0 s | 5,18 |

Kesimpulan: 8 thread memangkas **prompt eval 37%** dan total latency 22%, sehingga
`num_thread 8` dipakai. Angka token/s generasi sedikit lebih rendah pada 8 thread
(29,0 s vs 25,2 s untuk 150 token) — variasi kecil yang tidak konsisten; karena latency
total lebih penting untuk pengalaman pemakaian, 8 thread tetap dipilih.

### 7.2 Efek optimasi terhadap run awal

| Kondisi | Latency | Prompt eval | Token/s |
|---|---|---|---|
| Run pertama (ctx 4096, 4 thread, RAM tersisa 0,7 GB) | 434,0 s | ± 210 s | 3,12 |
| Setelah optimasi (ctx 3072, 8 thread, `keep_alive 30m`) | 86,5 s (150 token) | 46,7 s | 5,18 |

Peningkatan ± 4× terutama berasal dari berkurangnya tekanan memori (tidak ada lagi
halaman model yang terlempar ke disk) dan konteks yang lebih kecil.

---

## 8. Prosedur pengujian (agar bisa diulang)

1. `ollama serve`, lalu `ollama create pentest-lab:3b -f ai-assistant/ollama-config/modelfile`.
2. Jalankan `ollama stop` untuk model lain agar RAM tidak berebut.
3. Jalankan satu run pemanasan, buang hasilnya.
4. Jalankan kasus yang disetujui tim tiga kali dengan prompt yang sama; simpan output
   `output/*.md` dan catat versi model/prompt.
5. Catat skor serta penyimpangan; nilai hanya saran yang aman dan tidak destruktif.
6. Minta Anggota 3 memeriksa kesesuaian dengan hasil yang benar-benar diamati di lab.
7. Jalankan `python ai-assistant/summarize_runs.py --per-tag` untuk mencetak tabel dan
   grafik ASCII dari metrik yang tercatat.
8. Tandai hasil sebagai evaluasi prompt saat ini; jangan gabungkan dengan *baseline* lama.

---

## 9. Keterbatasan yang sudah diketahui

| Keterbatasan | Penjelasan | Mitigasi dalam desain |
|---|---|---|
| Model 3B | penalaran dangkal, mudah keluar format pada prompt panjang | temperature rendah, template format ketat, `num_ctx` 3072 |
| Halusinasi perintah/parameter | **terbukti** pada evaluasi: `command=` (K4), `name=` untuk stored XSS (K3), `nmap --script=vulnscan` (K4) | aturan "jangan mengarang" + tabel endpoint; terbukti belum cukup |
| Kebocoran template | 3 run menyalin kalimat instruksi prompt sebagai isi jawaban | perlu instruksi "jangan ulangi teks instruksi" atau pemisahan tegas blok instruksi vs data |
| Metode HTTP tertukar | `--data` dikirim ke endpoint GET (K2, K3) | daftar fakta perlu menyebut metode per modul (sudah ditambahkan, hasil: masih 4 pelanggaran) |
| Tidak tahu state lab | model tidak melihat respons HTTP target | agent tidak mengeksekusi; manusia menutup loop dengan bukti nyata |
| Bias data latih | saran umum dapat tidak sesuai dengan versi DVWA lokal | gunakan pemeriksaan awal, verifikasi manusia, dan catat versi lab |
| Prompt injection | `--mode report` menerima teks bebas (log/notes) | aturan "hanya berdasarkan catatan", output tetap ditinjau manusia |
| CPU-only | latency tinggi, throughput rendah | `num_predict 900`, `num_thread 8`, `keep_alive 30m`, model ≤3B |
| Verbositas | 3 dari 12 run menyentuh batas 900 token | batas dinaikkan dari 700; masih perlu pemangkasan template |
| Tidak deterministik | 3 run bisa sangat berbeda (K2: skor 1,4 vs 3,0) | evaluasi rata-rata 3 run, temperature 0.3 |

---

## 10. Kesimpulan sementara

Hasil pengujian 12 run (empat kasus) menunjukkan rata-rata **2,80**, yaitu **di bawah target
3,5**. Dengan demikian assistant **tidak layak dipakai sebagai sumber perintah siap-pakai**,
tetapi masih berguna sebagai **pendamping**: memberi urutan langkah, mengingatkan modul yang
relevan, dan menyusun kerangka analisis yang kemudian diverifikasi manusia.

Temuan paling penting bukan angka rata-ratanya, melainkan **pola kegagalannya**:

1. Pengetahuan *prosedural* (urutan langkah, struktur laporan) cukup baik — skor format
   3,3–4,0 pada semua kasus.
2. Pengetahuan *faktual-teknis* (parameter, metode HTTP, nama script) lemah dan cenderung
   dikarang — inilah sumber 12 *false lead*.
3. Semakin spesifik permintaan, semakin buruk hasilnya (K2 SQLi 2,33 vs K1 recon 3,40).

Karena itu rekomendasi pemakaian dalam proyek: **setiap saran wajib diverifikasi manual
sebelum dieksekusi**, dan agent tidak diberi kemampuan mengeksekusi perintah (lihat §2.6
laporan Metode). Ini juga alasan kolom "Saran dari AI assistant" pada
`docs/skenario-serangan.md` dicatat **beserta penilaian berguna/tidak**, bukan disalin
sebagai instruksi.

Pekerjaan lanjutan yang belum dievaluasi:
1. Jalankan K5 hanya setelah tersedia catatan bukti nyata yang sudah disamarkan.
2. Ulangi kasus yang sama dengan versi prompt saat ini dan bandingkan terhadap *baseline*
   tanpa mengubah rubrik atau jumlah percobaan.
3. Minta Anggota 3 memverifikasi penilaian teknis dan catat perbedaan pendapat.
4. Evaluasi model pembanding hanya bila waktu/perangkat memungkinkan; jangan mengirim
   catatan proyek ke layanan model jarak jauh.

---

## 11. Referensi

- OWASP Top 10 for LLM Applications 2025 — LLM01 Prompt Injection, LLM09 Misinformation
- Ollama API: `POST /api/generate`, `GET /api/tags`
- `docs/skenario-serangan.md` (Anggota 3) — konteks kasus uji
- `docs/topologi-lab.md` (Anggota 1) — batas target lab

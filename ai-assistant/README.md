# AI Assistant Core — Kelompok 6 (Topik 2: Offensive AI)

Modul ini adalah "otak" AI dari proyek **AI-Powered Security Assessment**: asisten LLM
lokal bergaya PentestGPT sederhana yang membantu menyusun rencana recon dan draf laporan
untuk target **DVWA di lab milik tim sendiri**.

Semua inferensi berjalan **CPU-only** melalui [Ollama](https://ollama.com) dengan model
kecil terkuantisasi, karena tidak ada anggota tim yang punya GPU diskrit.

> **Etika:** agent ini hanya diizinkan menyentuh target di dalam lab
> (`localhost`, `127.0.0.1`, `host.docker.internal`, atau subnet `172.20.0.0/24`).
> Target lain ditolak sebelum prompt dikirim (`LabScopeError`, exit code `2`).
> Agent **tidak mengeksekusi perintah apa pun** — ia hanya menyarankan.

---

## 1. Struktur

```
ai-assistant/
├── recon_agent.py                # CLI: mode recon & report + guardrail lab
├── summarize_runs.py             # rangkum runs.jsonl jadi tabel Markdown/CSV
├── requirements.txt              # kosong secara fungsional (stdlib only)
├── README.md                     # file ini
├── ollama-config/
│   └── modelfile                 # qwen2.5:3b-instruct + SYSTEM prompt + param CPU
├── prompts/
│   ├── recon-prompt.md           # template rencana recon
│   └── report-draft-prompt.md    # template draf bagian laporan
├── examples/
│   └── catatan-bukti-contoh.txt  # contoh catatan untuk uji --mode report
└── output/                       # hasil run + runs.jsonl (gitignored)
```

## 2. Prasyarat

| Komponen | Versi / catatan |
|---|---|
| Python | 3.9+ (tanpa paket tambahan) |
| Ollama | rilis terbaru untuk Windows |
| Model | `qwen2.5:3b-instruct` (~2 GB, Q4_K_M) |
| RAM | 8 GB (laptop Dzikra: i3-N305, 8 core, tanpa GPU diskrit) |

## 3. Setup

```powershell
# 1. Install Ollama, lalu pastikan server berjalan
ollama serve

# 2. Unduh model dasar
ollama pull qwen2.5:3b-instruct

# 3. Buat model khusus proyek (SYSTEM prompt + parameter CPU-friendly)
ollama create pentest-lab:3b -f ai-assistant/ollama-config/modelfile

# 4. Verifikasi
python ai-assistant/recon_agent.py --check
```

Keluaran `--check` yang sehat:

```
Ollama aktif di http://localhost:11434
Model tersedia: qwen2.5:3b-instruct:latest, pentest-lab:3b
Model diminta (pentest-lab:3b): ADA
```

## 4. Pemakaian

```powershell
# a. Uji prompt tanpa memanggil LLM (cepat, tidak butuh Ollama)
python ai-assistant/recon_agent.py --dry-run

# b. Recon untuk level low
python ai-assistant/recon_agent.py --model pentest-lab:3b --level low

# c. Level lain / target lain di dalam lab
python ai-assistant/recon_agent.py --level high --target http://172.20.0.10

# d. Draf bagian laporan dari catatan bukti
python ai-assistant/recon_agent.py --mode report --scenario S2.1 `
    --notes-file attacks/evidence/logs/S2.1-low.txt

# e. Tujuan khusus
python ai-assistant/recon_agent.py --goal "Uji SQL Injection modul SQL Injection level medium"

# f. Coba mode report tanpa data asli (pakai catatan contoh)
python ai-assistant/recon_agent.py --mode report --scenario S2.1 `
    --notes-file ai-assistant/examples/catatan-bukti-contoh.txt --dry-run
```

Hasil setiap run:

- `ai-assistant/output/recon-<waktu>.md` atau `report-<waktu>.md` → jawaban model
- `ai-assistant/output/<mode>-<waktu>.prompt.txt` → hanya pada `--dry-run`
- `ai-assistant/output/runs.jsonl` → metrik (latency, `eval_count`, tokens/s, hash prompt)
  yang dipakai untuk mengisi `docs/evaluasi-ai.md`

Rangkum semua metrik jadi tabel siap-tempel:

```powershell
python ai-assistant/summarize_runs.py            # tabel per run
python ai-assistant/summarize_runs.py --per-tag  # rata-rata per kasus (K1..K5)
python ai-assistant/summarize_runs.py --tag K1   # hanya satu kasus
python ai-assistant/summarize_runs.py --format csv > metrik.csv
```

## 5. Alur kolaborasi

```
Anggota 2 (agent)  ──saran perintah──▶  Anggota 3 (Farrel) eksekusi di lab
                                            │
                                            ▼
                                    bukti: screenshot + log
                                            │
                    ┌───────────────────────┘
                    ▼
      Anggota 2: --mode report → draf pembahasan
                    ▼
      Anggota 3: finalisasi + mitigasi (docs/mitigasi.md)
```

Agent sengaja **tidak** menjalankan `nmap`/`curl`/Burp sendiri: eksekusi dan pengambilan
bukti adalah tanggung jawab Anggota 3, sehingga tidak ada dua sumber kebenaran untuk bukti.

## 6. Parameter penting

| Flag | Default | Fungsi |
|---|---|---|
| `--mode` | `recon` | `recon` (rencana) atau `report` (draf laporan) |
| `--target` | `http://localhost:8080` | divalidasi terhadap daftar target lab |
| `--level` | `low` | `low` / `medium` / `high` / `impossible` |
| `--model` | `pentest-lab:3b` | model Ollama |
| `--temperature` | `0.3` | rendah → saran teknis stabil |
| `--num-ctx` | `3072` | cukup untuk prompt 3,8 kB + jawaban; KV-cache lebih hemat RAM |
| `--num-predict` | `900` | batas panjang jawaban (700 terbukti memotong di bagian 4) |
| `--num-thread` | `8` | pakai semua core i3-N305 (4 core = ± setengah throughput) |
| `--keep-alive` | `30m` | model ditahan di RAM agar run berikutnya tidak muat ulang |
| `--tag` | – | label run di `runs.jsonl` (mis. `K1`, `bench-thread4`) |
| `--dry-run` | – | cetak prompt tanpa memanggil LLM |
| `--check` | – | cek Ollama & ketersediaan model |

## 7. Troubleshooting

| Gejala | Penyebab & solusi |
|---|---|
| `[GAGAL] Tidak bisa menghubungi Ollama` | `ollama serve` belum jalan, atau `--host` salah |
| `model requires more system memory` | terlalu banyak model ter-load; `ollama stop <model>` lalu ulangi |
| Jawaban sangat lambat (>3 menit) | wajar di CPU 4–8 core; turunkan `--num-predict`, pakai `--num-ctx 2048` |
| Jawaban keluar format | turunkan `--temperature 0.1`, atau perkuat instruksi format di prompt |
| `[DITOLAK] Target ... di luar lab` | guardrail bekerja; gunakan hanya target lab |
| `[GAGAL] Jawaban kosong` | coba `--num-predict` lebih besar atau model lain (`llama3.2:3b`) |

## 8. Hasil pengujian di mesin pengembangan

| Uji | Hasil |
|---|---|
| `--dry-run` (recon, 2 level) | ✅ prompt ter-render, 0 placeholder tersisa |
| `--dry-run` (report, catatan S2.1) | ✅ catatan masuk & heading benar |
| Guardrail target luar lab (`192.168.1.10`) | ✅ ditolak, exit code `2` |
| Guardrail target lab (`172.20.0.10`) | ✅ diterima |
| `--check` tanpa Ollama | ✅ pesan jelas, exit code `3` |
| `ollama create pentest-lab:3b` | ✅ model 1,9 GB, SYSTEM prompt & parameter terbawa |
| `--check` dengan Ollama 0.40.16 | ✅ `Model diminta (pentest-lab:3b): ADA`, exit `0` |
| Inferensi live (run pertama) | ✅ 434 s / 3,12 token/s — **lambat**, RAM tersisa 0,7 GB |
| Benchmark `num_thread` 4 vs 8 | ✅ 110,6 s vs **86,5 s** (150 token) → 8 thread dipakai |
| Setelah optimasi | ✅ ± 5,2 token/s, prompt eval 46,7 s (dari 210 s) |
| Evaluasi K1–K4 (12 run) | ✅ selesai — skor rata-rata **2,80** (target 3,5) → assistant hanya layak sebagai *pendamping*; rincian di `docs/evaluasi-ai.md` §4–§7 |

## 9. Referensi

- `docs/evaluasi-ai.md` — rubrik & tabel evaluasi kualitas jawaban
- `docs/laporan-akhir/02-metode.md` — bagian Metode laporan akhir (lokal, gitignored)
- `docs/topologi-lab.md` — topologi lab dan batasan target
- OWASP Top 10 for LLM Applications (LLM01: Prompt Injection, LLM09: Misinformation)

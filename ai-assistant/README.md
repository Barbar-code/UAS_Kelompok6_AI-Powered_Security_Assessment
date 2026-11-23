# AI Assistant Core

Komponen ini menjalankan model lokal melalui Ollama untuk membuat rencana pemeriksaan awal dan draf laporan dari catatan bukti. Assistant tidak mengakses DVWA dan tidak menjalankan perintah. Setiap keluaran tetap harus ditinjau manusia.

## Batas keselamatan

- Target yang diterima: `http://localhost:8080` (atau alamat *loopback* pada port 8080).
- Permintaan yang dikirim ke model hanya boleh menuju Ollama lokal pada port 11434.
- Rencana dibatasi pada pemeriksaan awal yang non-destruktif; assistant tidak menyusun *payload* eksploit atau mengotomatiskan pengujian.
- Catatan dan log adalah data tidak tepercaya. Samarkan kredensial, token, *cookie* sesi, dan data pribadi sebelum dipakai.

## Prasyarat

| Komponen | Ketentuan |
|---|---|
| Python | 3.9 atau lebih baru; kode memakai pustaka bawaan Python |
| Ollama | Terpasang dan berjalan di komputer yang sama |
| Model | `qwen2.5:3b-instruct`, CPU-only |
| Memori | Disarankan 8 GB RAM; kinerja bergantung perangkat |

## Penyiapan model

Jalankan di PowerShell:

```powershell
ollama serve
ollama pull qwen2.5:3b-instruct
ollama create pentest-lab:3b -f ai-assistant/ollama-config/modelfile
python ai-assistant/recon_agent.py --check
```

Jangan mengarahkan `--host` ke server jarak jauh. Program menolak alamat Ollama non-*loopback* agar catatan proyek tidak dikirim ke layanan lain.

## Penggunaan

```powershell
# Render prompt tanpa menghubungi Ollama
python ai-assistant/recon_agent.py --dry-run

# Rencana pemeriksaan awal untuk target lokal
python ai-assistant/recon_agent.py --level low

# Draf laporan dari catatan nyata yang sudah disamarkan
python ai-assistant/recon_agent.py --mode report --scenario S2.1 `
    --notes-file attacks/evidence/logs/S2.1-low.txt

# Draf dari contoh hanya untuk memeriksa format, bukan sebagai bukti proyek
python ai-assistant/recon_agent.py --mode report --scenario S2.1 `
    --notes-file ai-assistant/examples/catatan-bukti-contoh.txt --dry-run
```

Perintah dan hasil uji yang sebenarnya harus dicatat oleh penguji di `docs/skenario-serangan.md`; model tidak boleh dianggap sebagai sumber bukti.

## Metrik, tabel, dan grafik

Setiap pemanggilan model menyimpan metrik ke `ai-assistant/output/runs.jsonl`. Ringkasan bawaan mencetak tabel per percobaan beserta grafik batang ASCII untuk latensi dan kecepatan generasi:

```powershell
python ai-assistant/summarize_runs.py
```

Rata-rata per label, tanpa grafik, atau keluaran CSV:

```powershell
python ai-assistant/summarize_runs.py --per-tag
python ai-assistant/summarize_runs.py --no-chart
python ai-assistant/summarize_runs.py --format csv
```

Keluaran Markdown mencetak tabel dan grafik batang ASCII, lalu menyimpan `metrics-chart.svg` di samping log. CSV hanya berisi data tabular. Jalankan ringkasan setelah percobaan yang memiliki label (`--tag K1`, misalnya). Jika log lokal belum tersedia, program memberi pesan bahwa berkas log belum ditemukan; metrik tidak dibuat-buat. Berkas di `output/` diabaikan Git.

## Evaluasi yang tersedia

Evaluasi terdahulu pada `docs/evaluasi-ai.md` adalah *baseline* dari versi prompt sebelumnya: 12 percobaan K1–K4, rata-rata 2,80/5, dan 12 *false lead*. K5 belum dijalankan. Karena batas keselamatan dan prompt kemudian diperketat, angka lama bukan hasil evaluasi versi baru. Jalankan ulang prosedur dengan bukti lab yang nyata sebelum menyimpulkan peningkatan.

## Pemecahan masalah

| Pesan/gejala | Tindakan |
|---|---|
| Ollama tidak dapat dihubungi | Pastikan `ollama serve` berjalan pada komputer yang sama |
| Model tidak ditemukan | Jalankan `ollama pull qwen2.5:3b-instruct` dan perintah `ollama create` di atas |
| Target ditolak | Pastikan target hanya `http://localhost:8080`; alamat jaringan dan port lain memang dibatasi |
| Jawaban model tidak sesuai | Jangan jalankan sarannya; catat penyimpangan untuk evaluasi dan minta pemeriksaan manusia |

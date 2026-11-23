# AI-Powered Security Assessment

Proyek mata kuliah Keamanan Informasi (KP70065004), Kelompok 6, Universitas Siliwangi — Topik 2: *Offensive AI*.

Proyek ini menyiapkan lab lokal DVWA dan mengevaluasi AI assistant berbasis Ollama sebagai alat bantu pemeriksaan awal dan dokumentasi. Assistant tidak menjalankan pemindaian atau serangan; keluaran model bukan bukti dan wajib ditinjau manusia.

## Ruang lingkup dan keselamatan

- Satu-satunya target aplikasi adalah DVWA milik tim pada `http://localhost:8080`.
- Compose memetakan aplikasi ke `127.0.0.1`; jangan mengubahnya menjadi layanan yang dapat dijangkau dari jaringan lain.
- Ollama berjalan di komputer lokal, dan prompt/catatan tidak boleh dikirim ke server jarak jauh.
- Jangan menguji sistem pihak ketiga. Jangan memasukkan kredensial, *cookie* sesi, token, data pribadi, atau bukti yang belum disamarkan ke Git atau model.
- Lab berisi aplikasi yang sengaja rentan; jangan gunakan konfigurasi ini untuk produksi.

## Pembagian kerja

| Anggota | Bagian |
|---|---|
| Kibar | Lab Docker, target DVWA, topologi dan prosedur reset |
| Dzikra | Integrasi Ollama, prompt, evaluasi dan ringkasan metrik |
| Farrel | Skenario uji lokal, bukti yang disamarkan, analisis dan mitigasi |
| Bersama | Tinjauan laporan, penyusunan video 5–10 menit dan pengumpulan |

Lihat [AGENTS.md](./AGENTS.md) untuk rincian tanggung jawab dan batas tugas.

## Struktur utama

```text
lab/                         Konfigurasi DVWA dan skrip reset
ai-assistant/                Agent lokal, prompt, evaluasi dan metrik
docs/                        Topologi, skenario, evaluasi dan mitigasi
attacks/evidence/            Bukti yang benar-benar dikumpulkan (disamarkan)
docs/laporan-akhir/           Hasil Word lokal; folder ini diabaikan Git
```

## Menjalankan lab (Windows)

1. Pasang dan jalankan Docker Desktop dengan backend Linux containers.
2. Dari PowerShell di direktori proyek, validasi konfigurasi:

   ```powershell
   docker compose -f .\lab\docker-compose.yml config
   ```

3. Jalankan layanan dan periksa statusnya:

   ```powershell
   docker compose -f .\lab\docker-compose.yml up -d
   docker compose -f .\lab\docker-compose.yml ps
   ```

4. Tunggu layanan basis data sehat, kemudian buka `http://localhost:8080`.
5. Untuk reset yang menghapus seluruh data DVWA, jalankan `.\lab\reset-lab.ps1` lalu konfirmasi dengan mengetik `RESET`.

Rincian dan batasan jaringan ada di [docs/topologi-lab.md](./docs/topologi-lab.md) dan diagram yang dapat diperbarui di [lab/network-diagram.svg](./lab/network-diagram.svg). Jangan memakai IP container sebagai alamat target; alamat internalnya tidak ditetapkan.

## Menjalankan AI assistant

Python 3.9+ dan Ollama lokal diperlukan. Penyiapan model:

```powershell
ollama serve
ollama pull qwen2.5:3b-instruct
ollama create pentest-lab:3b -f ai-assistant/ollama-config/modelfile
python ai-assistant/recon_agent.py --check
```

Contoh penggunaan:

```powershell
python ai-assistant/recon_agent.py --dry-run
python ai-assistant/recon_agent.py --level low
python ai-assistant/recon_agent.py --mode report --scenario S2.1 `
    --notes-file attacks/evidence/logs/S2.1-low.txt
```

Target dibatasi ke *loopback* pada port 8080 dan Ollama ke *loopback* pada port 11434. Mode laporan memerlukan catatan yang sudah disamarkan. Lihat [ai-assistant/README.md](./ai-assistant/README.md).

## Tabel dan grafik metrik

Setiap pemanggilan Ollama mencatat metrik ke `ai-assistant/output/runs.jsonl` (berkas lokal yang diabaikan Git). Setelah ada log:

```powershell
python ai-assistant/summarize_runs.py
python ai-assistant/summarize_runs.py --per-tag
python ai-assistant/summarize_runs.py --format csv
```

Keluaran Markdown mencetak tabel dan grafik batang ASCII untuk rata-rata latensi serta kecepatan generasi per label, dan menyimpan grafik SVG di samping berkas log. CSV tetap hanya berisi data tabular.

## Skenario, bukti dan mitigasi

Anggota 3 mengisi [docs/skenario-serangan.md](./docs/skenario-serangan.md) hanya dengan hasil yang benar-benar diperoleh. Simpan bukti yang telah disamarkan di `attacks/evidence/screenshots/` atau `attacks/evidence/logs/`, lalu tautkan setiap mitigasi pada temuan terverifikasi di [docs/mitigasi.md](./docs/mitigasi.md). Status terkini masih berupa templat; belum ada hasil serangan atau bukti yang tercatat pada dokumen tersebut.

Evaluasi AI awal mencatat rata-rata 2,80/5 untuk K1–K4, 12 *false lead*, dan K5 belum dijalankan. Angka ini merupakan *baseline* dari versi prompt sebelumnya; prompt terbaru belum dievaluasi ulang. Rincian ada di [docs/evaluasi-ai.md](./docs/evaluasi-ai.md).

## Status dan pemeriksaan

- Konfigurasi lab sudah dibatasi ke host lokal dan jaringan internal; tetap perlu diuji dengan Docker Desktop di mesin tim.
- Prompt AI saat ini dibatasi pada pemeriksaan awal non-destruktif, tetapi belum memiliki evaluasi ulang.
- Skenario dan mitigasi Farrel perlu diisi dari pengujian nyata; jangan menggunakan contoh bukti sebagai hasil.
- Validasi Python lokal: `python -m unittest discover -s ai-assistant/tests`.
- Validasi Compose lokal: `docker compose -f .\lab\docker-compose.yml config`.

## Lisensi dan penggunaan

Gunakan proyek hanya untuk tujuan pendidikan dalam lab yang dikelola tim. Jangan menyebarkan konfigurasi atau keluaran untuk menyerang sistem pihak lain.

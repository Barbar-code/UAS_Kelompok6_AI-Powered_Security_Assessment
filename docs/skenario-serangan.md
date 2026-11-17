# Skenario Serangan & Hasil

> **Pemilik:** Anggota 3 (Farrel)
> **Aturan:** Semua pengujian HANYA ke target di `lab/topologi.md`. Dilarang menyerang sistem di luar lab.

## 1. Ringkasan

| ID | Skenario | Target | Tool | Level | Status | Hasil |
|---|---|---|---|---|---|---|
| S1 | Recon | DVWA | nmap, AI assistant | - | ☐ | |
| S2.1 | SQL Injection | DVWA | Burp Suite / manual | low / medium / high | ☐ | |
| S2.2 | XSS (reflected, stored) | DVWA | Burp Suite / manual | low / medium / high | ☐ | |
| S2.3 | Command Injection | DVWA | manual | low / medium / high | ☐ | |
| S2.4 | Brute Force Login | DVWA | Burp Intruder | low / medium / high | ☐ | |
| S2.5 | File Upload | DVWA | manual | low / medium / high | ☐ | |
| S3.1 | Prompt Injection | Chatbot Ollama (lab) | manual | - | ☐ | |
| S3.2 | Probing LLM otomatis | Chatbot Ollama (lab) | garak | - | ☐ | |

Status: ☐ belum, ◐ berjalan, ☑ selesai. Hasil: Berhasil / Gagal / Sebagian.

## 2. Lingkungan Pengujian

- Mesin penyerang: (laptop Farrel, OS, versi tool)
- Target: (IP lab, versi DVWA, level keamanan)
- Referensi topologi: `docs/topologi-lab.md`
- Tanggal pengujian:

## 3. Template Skenario

Salin blok ini untuk setiap skenario/level.

### [ID] Nama Skenario — Level: low/medium/high

| Item | Isi |
|---|---|
| Tujuan | |
| Target & modul | |
| Tool & versi | |
| Prasyarat | |
| Saran dari AI assistant | (prompt yang dipakai + ringkasan jawaban; nilai berguna atau tidak) |

**Langkah**
1.
2.
3.

**Hasil:** Berhasil / Gagal / Sebagian

**Bukti**
- Screenshot: `attacks/evidence/screenshots/<ID>-<level>-01.png`
- Log: `attacks/evidence/logs/<ID>-<level>.txt`

**Analisis singkat:** (mengapa berhasil/gagal di level ini, apa bedanya dengan level lain)

**Dampak:** (data apa yang terekspos / kontrol apa yang didapat)

**Mitigasi:** lihat `docs/mitigasi.md` → entri [ID]

---

## 4. Skenario

### S1 — Recon
(isi dengan template)

### S2 — Web Exploit
#### S2.1 SQL Injection
#### S2.2 XSS
#### S2.3 Command Injection
#### S2.4 Brute Force
#### S2.5 File Upload

### S3 — LLM-Specific
#### S3.1 Prompt Injection / kebocoran system prompt
#### S3.2 Probing otomatis dengan garak

## 5. Perbandingan Level (low vs medium vs high)

| Serangan | Low | Medium | High |
|---|---|---|---|
| SQL Injection | | | |
| XSS | | | |
| Command Injection | | | |
| Brute Force | | | |
| File Upload | | | |

## 6. Kendala & Catatan

-

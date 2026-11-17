# Rekomendasi Mitigasi

> **Pemilik:** Anggota 3 (Farrel)
> Setiap serangan yang **berhasil** di `docs/skenario-serangan.md` wajib punya satu entri di sini.

## 1. Ringkasan

| ID Serangan | Kerentanan | Tingkat Risiko | Mitigasi Utama | Sudah Diverifikasi? |
|---|---|---|---|---|
| S2.1 | SQL Injection | | Prepared statement / parameterized query | ☐ |
| S2.2 | XSS | | Output encoding, CSP | ☐ |
| S2.3 | Command Injection | | Hindari shell, whitelist input | ☐ |
| S2.4 | Brute Force | | Rate limiting, lockout, MFA | ☐ |
| S2.5 | File Upload | | Validasi tipe/isi file, simpan di luar webroot | ☐ |
| S3.1 | Prompt Injection | | Pemisahan instruksi & data, filter input/output | ☐ |

Tingkat risiko: Rendah / Sedang / Tinggi / Kritis (jelaskan kriteria yang dipakai, mis. dampak x kemudahan eksploitasi).

## 2. Template Entri

### [ID] Nama Kerentanan

| Item | Isi |
|---|---|
| Serangan terkait | (link ke skenario) |
| Akar masalah | |
| Dampak | |
| Tingkat risiko & alasan | |

**Mitigasi**
1. *Perbaikan utama:*
2. *Lapisan tambahan (defense in depth):*
3. *Deteksi/monitoring:*

**Contoh perbaikan (kode/konfigurasi)**
```
(potongan kode atau konfigurasi yang aman)
```

**Verifikasi:** (uji ulang serangan setelah mitigasi, hasil, bukti di `attacks/evidence/`)

**Referensi:** OWASP Top 10, OWASP Cheat Sheet, OWASP Top 10 for LLM Applications

---

## 3. Entri per Serangan

### S2.1 SQL Injection
### S2.2 XSS
### S2.3 Command Injection
### S2.4 Brute Force
### S2.5 File Upload
### S3.1 Prompt Injection
### S3.2 Temuan garak

## 4. Prioritas Perbaikan

| Prioritas | Mitigasi | Alasan | Perkiraan Usaha |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

## 5. Catatan

- Tulis mitigasi sebagai rekomendasi untuk pemilik sistem. Bukti uji ulang pasca-perbaikan akan memperkuat laporan.

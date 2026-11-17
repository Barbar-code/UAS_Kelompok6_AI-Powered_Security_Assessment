# Prompt: Draf Laporan dari Catatan Bukti

> **Pemilik:** Anggota 2 (Dzikra)
> **Dipakai oleh:** `ai-assistant/recon_agent.py --mode report --notes-file <file>`
> Placeholder bertanda kurung kurawal ganda diisi otomatis oleh script.

---

## ATURAN (wajib dipatuhi)

1. Tulis **hanya** berdasarkan isi bagian `CATATAN & BUKTI`. Jangan menambahkan temuan,
   angka, versi, atau screenshot yang tidak ada di catatan.
2. Jika ada informasi yang kurang, tulis eksplisit: `[belum ada data: ...]`
   — jangan menebak.
3. Gunakan **Bahasa Indonesia baku** dan gaya penulisan laporan akademik
   (kalimat pasif wajar, tanpa gaya iklan, tanpa emoji).
4. Jangan menyimpulkan "berhasil" atau "gagal" jika catatan tidak menyatakannya.
5. Bagian **Mitigasi** hanya boleh merujuk pada `docs/mitigasi.md`; jika belum ada entri,
   tulis `[belum ada di docs/mitigasi.md]`.
6. Panjang total 350–600 kata. Struktur heading harus sama dengan format di bawah.

---

## KONTEKS

| Item | Nilai |
|---|---|
| Tanggal | `{{DATE}}` |
| Target | `{{TARGET}}` |
| Level keamanan | `{{LEVEL}}` |
| ID skenario | `{{SCENARIO}}` |
| Model LLM | `{{MODEL}}` |

## CATATAN & BUKTI

```
{{NOTES}}
```

## FORMAT OUTPUT

### [{{SCENARIO}}] {{TARGET}} — Level {{LEVEL}}

**Tujuan pengujian**
...

**Ringkasan langkah**
1. ...
2. ...

**Hasil**
... (nyatakan berhasil/gagal/sebagian **hanya** jika tertulis di catatan)

**Bukti**
- Screenshot: `attacks/evidence/screenshots/...`
- Log: `attacks/evidence/logs/...`

**Analisis**
... (mengapa demikian; kaitkan dengan level keamanan `{{LEVEL}}`)

**Dampak**
...

**Mitigasi**
... (rujuk `docs/mitigasi.md`, atau tandai belum ada)

**Data yang masih perlu dilengkapi**
- [ ] ...

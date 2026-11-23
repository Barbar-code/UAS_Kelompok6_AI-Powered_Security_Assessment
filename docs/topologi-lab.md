# Topologi Lab AI-Powered Security Assessment

## Tujuan dan batas ruang lingkup

Lab ini menyediakan target DVWA untuk pembelajaran keamanan aplikasi web. Aplikasi hanya dipublikasikan ke alamat *loopback* host `http://localhost:8080`; jangan mengubah pemetaan port menjadi terbuka ke seluruh antarmuka jaringan. Pengujian hanya boleh dilakukan pada lab milik tim.

Jaringan Docker menggunakan mode `internal`, sehingga container tidak memiliki rute keluar melalui jaringan itu. Tidak ada subnet atau alamat IP container yang ditetapkan secara statis; alamat internal Docker dapat berubah dan bukan alamat target yang dijanjikan proyek. AI assistant hanya menerima URL target lokal `http://localhost:8080` (atau ekuivalen *loopback* pada port 8080).

## Arsitektur

1. **Mesin host** menjalankan Docker Desktop dan peramban. Akses target melalui `http://localhost:8080`.
2. **Container DVWA** (`dvwa-web`) melayani aplikasi pada port 80. Docker hanya memetakan port tersebut ke `127.0.0.1:8080` pada host.
3. **Container MySQL** (`dvwa-db`) menyimpan data DVWA pada volume `dvwa-db-data`. Port MySQL tidak dipublikasikan ke host.
4. Kedua container berkomunikasi di jaringan bridge internal `uas-lab-net`. Jaringan ini tidak mempunyai alamat IP atau subnet yang perlu digunakan secara manual.

## Diagram

Diagram yang dapat diperbarui tersedia di [lab/network-diagram.svg](../lab/network-diagram.svg).

```text
+------------------------------------------------------+
| Mesin host                                           |
| Peramban / alat pengujian                            |
| http://localhost:8080                                |
+---------------------------+--------------------------+
                            |
                            | 127.0.0.1:8080 -> port 80
                            v
+------------------------------------------------------+
| Docker network: uas-lab-net (internal: true)         |
|                                                      |
|  +---------------------+   +----------------------+  |
|  | dvwa-web            |<->| dvwa-db              |  |
|  | DVWA, port 80       |   | MySQL, port 3306     |  |
|  +---------------------+   +----------------------+  |
|  Tidak ada port DB yang dipublikasikan ke host       |
+------------------------------------------------------+
```

## Konfigurasi target

| Item | Nilai |
|---|---|
| Aplikasi | DVWA |
| URL dari host | `http://localhost:8080` |
| Login awal DVWA | `admin` / `password` |
| Nilai level yang diminta saat awal | `low` (pastikan nilainya di antarmuka DVWA sebelum pengujian) |
| Nama proyek Compose | `uas-lab` |
| Jaringan Docker | `uas-lab-net` (`internal: true`) |
| Persistensi basis data | Volume `dvwa-db-data` |

Kredensial tersebut hanya untuk lab lokal. Jangan memakai konfigurasi ini untuk layanan publik atau produksi. Ganti kata sandi DVWA setelah *setup* awal bila diperlukan oleh prosedur pengujian.

## Menjalankan dan memeriksa lab

Dari direktori proyek pada PowerShell:

```powershell
docker compose -f .\lab\docker-compose.yml config
docker compose -f .\lab\docker-compose.yml up -d
docker compose -f .\lab\docker-compose.yml ps
```

Pastikan layanan `db` berstatus sehat sebelum melakukan pengujian. Buka `http://localhost:8080` dari host, masuk ke pengaturan keamanan DVWA, lalu verifikasi/pilih level yang akan diuji. Variabel `DVWA_DEFAULT_SECURITY` bergantung pada dukungan image; jangan menganggap level aktif hanya dari berkas Compose. Pemeriksaan ini tidak membuktikan bahwa tidak ada konflik dengan kebijakan jaringan host; gunakan firewall lokal dan jangan meneruskan port tersebut ke router atau jaringan lain.

## Reset

Reset akan menghapus volume basis data dan seluruh data DVWA. Jalankan `.\lab\reset-lab.ps1` lalu ketik `RESET` saat diminta, atau gunakan `-ConfirmReset` hanya setelah memastikan kehilangan data memang diinginkan. Alternatif lintas platform tersedia pada `lab/reset-lab.sh` dan memerlukan argumen `--yes` untuk mode tanpa interaksi.

## Batasan dan catatan

- Jangan memindai alamat atau jaringan di luar target `localhost:8080`.
- Jangan mengubah pemetaan port menjadi `8080:80` tanpa alamat `127.0.0.1`.
- Jangan menganggap alamat container tetap; hanya URL host di atas yang didukung oleh proyek.
- Jangan menaruh bukti yang berisi kata sandi, *cookie* sesi, atau data pribadi tanpa penyamaran.

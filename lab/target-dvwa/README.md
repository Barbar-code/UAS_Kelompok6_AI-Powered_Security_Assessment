# Target DVWA

Target proyek adalah aplikasi latihan DVWA di Docker. Jalankan dari direktori proyek:

```powershell
docker compose -f .\lab\docker-compose.yml up -d
docker compose -f .\lab\docker-compose.yml ps
```

Setelah layanan basis data sehat, akses aplikasi hanya melalui `http://localhost:8080`. Pemetaan port Compose terikat ke `127.0.0.1`; jangan membukanya ke seluruh antarmuka jaringan.

| Pengaturan | Nilai |
|---|---|
| Container aplikasi | `dvwa-web` |
| Container basis data | `dvwa-db` |
| Nilai level yang diminta saat awal | `low` (verifikasi di antarmuka DVWA) |
| Kredensial awal DVWA | `admin` / `password` |
| Jaringan | `uas-lab-net`, internal Docker |

Kredensial awal hanya berlaku untuk lab. Jangan gunakan konfigurasi ini di layanan publik/produksi. Verifikasi level keamanan aktual pada antarmuka DVWA sebelum pengujian karena dukungan variabel `DVWA_DEFAULT_SECURITY` bergantung pada image. Port MySQL tidak dipublikasikan ke host dan alamat IP container tidak dijamin tetap.

Untuk reset data gunakan `.\lab\reset-lab.ps1`, lalu konfirmasi dengan mengetik `RESET`. Perintah ini menghapus volume basis data dan tidak dapat membatalkan data yang terhapus.

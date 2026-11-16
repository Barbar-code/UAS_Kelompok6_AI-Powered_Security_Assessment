# Target DVWA

## Deskripsi
Target aplikasi yang digunakan pada lab ini adalah DVWA (Damn Vulnerable Web Application). Aplikasi ini dipilih karena memiliki berbagai celah keamanan yang umum dijumpai pada aplikasi web dan dapat dipakai untuk proses pembelajaran serta pengujian yang terkendali.

## Akses
- URL aplikasi: http://localhost:8080
- User default: `admin`
- Password default: `password`

## Konfigurasi yang digunakan
- `DVWA_DEFAULT_SECURITY=low`
- Jaringan internal: `uas-lab-net`
- Database: MySQL dalam container `dvwa-db`

## Catatan operasional
- Aplikasi berjalan di dalam Docker dan hanya dapat diakses dari mesin host atau jaringan lokal yang sama.
- Semua perubahan data dapat direset dengan menjalankan script `lab/reset-lab.sh`.
- Lingkungan ini tidak terhubung ke internet publik dan harus dipelihara agar tetap berada dalam batas lab yang ditentukan.

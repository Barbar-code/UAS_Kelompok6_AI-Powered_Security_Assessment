# Topologi Lab AI-Powered Security Assessment

## Tujuan lab
Lab ini dirancang untuk menyediakan target web yang aman untuk dipelajari dan diuji secara terkendali. Fokus utama lab adalah menyediakan lingkungan DVWA (Damn Vulnerable Web Application) yang dapat dijalankan lokal di mesin penguji, tanpa terhubung ke jaringan publik atau sistem lain yang bukan milik tim.

## Arsitektur jaringan
Lab terdiri dari tiga komponen utama:

1. Mesin penguji / host
   - Digunakan untuk mengakses aplikasi DVWA melalui browser.
   - Dapat menjalankan alat seperti curl, Burp Suite, atau browser untuk pengujian.
   - Berfungsi sebagai titik masuk untuk validasi awal, enumerasi, dan logging.

2. Container aplikasi DVWA
   - Aplikasi web berjalan di dalam container Docker dengan nama `dvwa-web`.
   - Port aplikasi dipetakan ke `http://localhost:8080`.
   - Container ini berkomunikasi dengan database melalui jaringan internal Docker.

3. Container database MySQL
   - Database berjalan di dalam container `dvwa-db`.
   - Data aplikasi disimpan di volume Docker `dvwa-db-data` agar dapat direset dengan cepat.
   - Hanya dapat diakses dari jaringan lab internal dan tidak dipublikasikan ke internet.

## Diagram topologi

```text
+-----------------------------------------------------------+
| Mesin Penguji / Host                                      |
| - Browser / curl / Burp Suite                              |
| - Akses: http://localhost:8080                           |
+-------------------------+---------------------------------+
                          |
                          | 8080:80
                          v
+-------------------------+---------------------------------+
| Docker Network: uas-lab-net                               |
|                                                         |
|  +-------------------+       +------------------------+  |
|  | dvwa-web          | <---> | dvwa-db                |  |
|  | 172.20.0.10:80    |       | 172.20.0.11:3306       |  |
|  | DVWA App          |       | MySQL                  |  |
|  +-------------------+       +------------------------+  |
+-----------------------------------------------------------+
```

## Rincian konfigurasi
- Nama jaringan: `uas-lab-net`
- Subnet: `172.20.0.0/24`
- Aplikasi target: DVWA
- URL akses: `http://localhost:8080`
- Default login DVWA: `admin` / `password`
- Tingkat keamanan default: `low`

## Batasan lab
- Lab hanya digunakan untuk target dalam lingkungan kendali sendiri.
- Tidak ada koneksi ke internet publik atau sistem pihak ketiga.
- Semua kegiatan pengujian harus dilakukan dengan izin dan dalam konteks proyek yang telah ditetapkan.

## Tujuan operasional
Dengan topologi ini, sesi pengujian dapat dibuat ulang dengan cepat, data dapat direset, dan semua serangan dapat dilakukan di lingkungan yang terisolasi, aman, dan mudah dipantau.

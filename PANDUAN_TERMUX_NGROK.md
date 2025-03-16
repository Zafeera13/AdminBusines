# Panduan Lengkap CusAkuntanID dengan Termux & Ngrok

Panduan ini akan membantu Anda menjalankan CusAkuntanID di perangkat Android dengan Termux, dan mengaksesnya dari jarak jauh melalui Ngrok.

## Daftar Isi
1. [Persiapan Awal](#1-persiapan-awal)
2. [Instalasi Termux](#2-instalasi-termux)
3. [Setup CusAkuntanID di Termux](#3-setup-cusakuntanid-di-termux)
4. [Setup Ngrok untuk Akses Jarak Jauh](#4-setup-ngrok-untuk-akses-jarak-jauh)
5. [Menjalankan Aplikasi](#5-menjalankan-aplikasi)
6. [Akses Jarak Jauh](#6-akses-jarak-jauh)
7. [Pemeliharaan & Troubleshooting](#7-pemeliharaan--troubleshooting)
8. [FAQ](#8-faq)

## 1. Persiapan Awal

### 1.1 Memastikan Persyaratan
- Perangkat Android dengan sistem operasi minimal Android 7.0
- Ruang penyimpanan minimal 1GB tersedia
- Koneksi internet yang stabil

### 1.2 Unduh Aplikasi Termux
Unduh Termux dari F-Droid (direkomendasikan):
- Kunjungi [F-Droid.org](https://f-droid.org/)
- Cari dan unduh Termux
- Atau gunakan link langsung: [Termux di F-Droid](https://f-droid.org/en/packages/com.termux/)

**Catatan**: Versi Termux di Google Play Store tidak lagi diperbarui dan mungkin memiliki masalah kompatibilitas.

## 2. Instalasi Termux

### 2.1 Setup Awal Termux
1. Buka aplikasi Termux
2. Tunggu proses instalasi awal selesai
3. Berikan akses penyimpanan:
   ```bash
   termux-setup-storage
   ```
   Ketika diminta, berikan izin untuk mengakses penyimpanan.

### 2.2 Update Termux
```bash
pkg update && pkg upgrade -y
```

## 3. Setup CusAkuntanID di Termux

### 3.1 Menyalin File Proyek
Ada dua cara untuk menyalin file proyek:

#### Metode 1: Menggunakan Direktori Download
Jika Anda telah mendownload file proyek ke perangkat Android:
```bash
# Buat direktori proyek
mkdir -p ~/storage/shared/CusAkuntanID

# Salin file dari Download (sesuaikan path jika berbeda)
cp -r /sdcard/Download/CusAkuntanID/* ~/storage/shared/CusAkuntanID/

# Masuk ke direktori proyek
cd ~/storage/shared/CusAkuntanID

# Buat file script bisa dieksekusi
chmod +x *.sh
```

#### Metode 2: Clone dari Repository (Jika menggunakan Git)
```bash
# Install Git
pkg install git -y

# Clone repository (ganti URL dengan URL repository yang benar)
git clone https://repository-url.git ~/storage/shared/CusAkuntanID

# Masuk ke direktori proyek
cd ~/storage/shared/CusAkuntanID

# Buat file script bisa dieksekusi
chmod +x *.sh
```

### 3.2 Menjalankan Script Setup
```bash
./setup_termux.sh
```

Script ini akan:
- Memperbarui paket Termux
- Menginstall Python dan dependensi yang dibutuhkan
- Membuat lingkungan virtual Python
- Menginstall semua paket Python yang diperlukan

## 4. Setup Ngrok untuk Akses Jarak Jauh

### 4.1 Mendaftar Akun Ngrok
1. Kunjungi [ngrok.com](https://ngrok.com) dan daftar akun gratis
2. Setelah login, kunjungi [dashboard](https://dashboard.ngrok.com)
3. Cari dan salin token autentikasi Anda

### 4.2 Menginstall Ngrok di Termux
```bash
# Pastikan Anda berada di direktori proyek
cd ~/storage/shared/CusAkuntanID

# Jalankan script setup Ngrok
./setup_ngrok.sh
```

Ketika diminta, masukkan token autentikasi yang telah Anda salin.

## 5. Menjalankan Aplikasi

### 5.1 Menjalankan CusAkuntanID
```bash
# Pastikan Anda berada di direktori proyek
cd ~/storage/shared/CusAkuntanID

# Jalankan aplikasi
./run_app.sh
```

Script ini akan:
- Mengaktifkan lingkungan virtual Python
- Menampilkan alamat IP lokal untuk akses di jaringan yang sama
- Menjalankan server dengan Gunicorn

### 5.2 Mengakses Aplikasi Secara Lokal
- Pada perangkat yang sama, buka browser dan kunjungi: `http://localhost:5000`
- Dari perangkat lain pada jaringan yang sama, gunakan alamat IP yang ditampilkan oleh script

## 6. Akses Jarak Jauh

### 6.1 Menjalankan Ngrok
Buka terminal Termux baru (geser dari kiri untuk menu, pilih "New Session"), kemudian:
```bash
cd ~/storage/shared/CusAkuntanID
./run_ngrok.sh
```

### 6.2 Mengakses Aplikasi dari Jarak Jauh
1. Salin URL HTTPS yang diberikan oleh Ngrok (misal: `https://a1b2c3d4.ngrok.io`)
2. Gunakan URL ini untuk mengakses aplikasi dari perangkat manapun dengan koneksi internet

**Catatan Penting**:
- URL Ngrok gratis akan berubah setiap kali Anda me-restart Ngrok
- Ngrok gratis memiliki batasan bandwidth dan koneksi
- Untuk penggunaan yang lebih serius, pertimbangkan berlangganan Ngrok

## 7. Pemeliharaan & Troubleshooting

### 7.1 Memperbarui Aplikasi
Jika ada pembaruan aplikasi:
```bash
# Masuk ke direktori proyek
cd ~/storage/shared/CusAkuntanID

# Salin file baru jika menggunakan metode download manual
# atau jika menggunakan Git:
git pull

# Jalankan setup lagi untuk memastikan dependensi terbaru
./setup_termux.sh
```

### 7.2 Masalah Umum dan Solusi

#### Aplikasi tidak bisa diakses secara lokal
- Periksa apakah server berjalan dengan benar
- Pastikan Anda menggunakan alamat IP dan port yang benar
- Coba restart aplikasi: `./run_app.sh`

#### Ngrok error "failed to start tunnel"
- Periksa apakah token autentikasi sudah dikonfigurasi
- Pastikan server aplikasi sudah berjalan terlebih dahulu
- Coba konfigurasi ulang token: `./ngrok config add-authtoken YOUR_TOKEN`

#### Error "Address already in use"
- Ada aplikasi lain yang menggunakan port 5000
- Hentikan aplikasi tersebut atau gunakan port lain

## 8. FAQ

### 8.1 Apakah data saya aman dengan Ngrok?
Ngrok menyediakan tunnel terenkripsi, namun untuk keamanan data, pastikan:
- Gunakan kata sandi yang kuat pada aplikasi
- Jangan membagikan URL Ngrok kepada orang yang tidak berwenang
- Pertimbangkan untuk menonaktifkan Ngrok ketika tidak digunakan

### 8.2 Mengapa server harus restart setiap kali saya keluar dari Termux?
Termux menghentikan semua proses ketika aplikasi ditutup. Untuk menjalankan server terus menerus:
- Gunakan tombol "ACQUIRE WAKELOCK" dari menu Termux
- Pertimbangkan menggunakan Termux:Boot untuk menjalankan server saat startup

### 8.3 Apa batas penggunaan Ngrok gratis?
Ngrok gratis memiliki beberapa batasan:
- 1 tunnel aktif pada satu waktu
- 40 koneksi per menit
- URL baru setiap restart
- Tanpa custom subdomain
- Untuk penggunaan lebih lanjut, lihat [harga Ngrok](https://ngrok.com/pricing)

### 8.4 Bagaimana jika aplikasi tidak berjalan setelah menutup Termux?
Gunakan Termux:Boot untuk menjalankan aplikasi saat startup, atau gunakan fitur "Acquire Wakelock" di Termux untuk mencegah proses dihentikan.

---

Untuk pertanyaan lebih lanjut atau bantuan, hubungi pengembang aplikasi.

*Terakhir diperbarui: Maret 2025*
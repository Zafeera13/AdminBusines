# Panduan Lengkap CusAkuntanID di Termux

## Pengenalan

Dokumen ini berisi panduan lengkap untuk menginstal, mengkonfigurasi, dan menjalankan aplikasi CusAkuntanID di Termux pada perangkat Android. Dengan mengikuti panduan ini, Anda akan dapat menjalankan aplikasi bisnis Anda dari smartphone dengan akses internet yang dapat dijangkau dari mana saja.

## Daftar Isi

1. [Persyaratan Sistem](#persyaratan-sistem)
2. [Instalasi Termux](#instalasi-termux)
3. [Setup Awal](#setup-awal)
4. [Instalasi CusAkuntanID](#instalasi-cusakuntanid)
5. [Menjalankan Aplikasi](#menjalankan-aplikasi)
6. [Akses Jarak Jauh dengan Ngrok](#akses-jarak-jauh-dengan-ngrok)
7. [Monitoring Aplikasi](#monitoring-aplikasi)
8. [Pemecahan Masalah](#pemecahan-masalah)
9. [Fitur Lanjutan](#fitur-lanjutan)

## Persyaratan Sistem

- Smartphone Android versi 7.0 ke atas
- Minimal 3GB RAM tersedia
- Minimal 500MB ruang penyimpanan kosong
- Koneksi internet

## Instalasi Termux

1. Unduh Termux dari [F-Droid](https://f-droid.org/packages/com.termux/) (direkomendasikan)
2. Pasang Termux dan buka aplikasi
3. Berikan izin penyimpanan dengan menjalankan:
   ```
   termux-setup-storage
   ```
4. Tunggu sampai proses selesai dan tekan "Allow" jika diminta

## Setup Awal

1. Perbarui repositori paket dan paket dasar:
   ```
   pkg update -y && pkg upgrade -y
   ```

2. Pasang paket yang diperlukan:
   ```
   pkg install python git openssh wget -y
   ```

3. Buat direktori untuk aplikasi:
   ```
   mkdir -p ~/storage/shared/CusAkuntanID
   ```

4. Masuk ke direktori tersebut:
   ```
   cd ~/storage/shared/CusAkuntanID
   ```

## Instalasi CusAkuntanID

### Metode 1: Unduh dari Repositori

1. Clone repositori:
   ```
   git clone https://github.com/username/CusAkuntanID.git .
   ```

2. Pasang dependensi Python:
   ```
   pip install -r requirements.txt
   ```

### Metode 2: Unduh Arsip ZIP

1. Unduh arsip CusAkuntanID.zip
2. Ekstrak arsip ke direktori CusAkuntanID:
   ```
   unzip /path/to/CusAkuntanID.zip -d ~/storage/shared/CusAkuntanID
   ```
3. Pasang dependensi Python:
   ```
   cd ~/storage/shared/CusAkuntanID
   pip install -r requirements.txt
   ```

## Menjalankan Aplikasi

1. Pastikan Anda berada di direktori aplikasi:
   ```
   cd ~/storage/shared/CusAkuntanID
   ```

2. Jalankan aplikasi menggunakan script otomatis:
   ```
   ./run_app.sh
   ```

3. Atau jalankan secara manual:
   ```
   python main.py
   ```

4. Aplikasi akan tersedia di alamat lokal yang ditampilkan di terminal (biasanya http://localhost:5000 atau http://127.0.0.1:5000)

## Akses Jarak Jauh dengan Ngrok

### Panduan Ngrok

Ngrok memungkinkan Anda mengakses aplikasi dari jarak jauh melalui internet. Berikut langkah-langkah untuk menggunakannya:

#### Metode 1: Menggunakan Auto Ngrok (Direkomendasikan)

1. Download dan setup Ngrok (jika belum dilakukan):
   ```
   ./download_ngrok.sh
   ```

2. Jalankan Auto Ngrok:
   ```
   ./auto_ngrok.sh
   ```

3. URL HTTPS untuk akses jarak jauh akan ditampilkan dengan warna hijau
4. Salin URL tersebut untuk mengakses aplikasi dari perangkat mana saja
5. Token Ngrok sudah dikonfigurasi secara otomatis

#### Metode 2: Setup Manual Ngrok

1. Download dan setup Ngrok:
   ```
   ./setup_ngrok_auto.sh
   ```

2. Jalankan Ngrok dengan script Python:
   ```
   ./run_ngrok.sh
   ```

3. URL HTTPS untuk akses jarak jauh akan ditampilkan
4. Salin URL tersebut untuk mengakses aplikasi dari perangkat mana saja

### Perhatian untuk Ngrok

- URL Ngrok gratis bersifat sementara dan akan berubah setiap restart
- Untuk URL permanen, Anda dapat berlangganan layanan Ngrok berbayar
- Ada batasan bandwidth dan koneksi pada akun Ngrok gratis

## Monitoring Aplikasi

1. Untuk memantau status aplikasi dan Ngrok dalam satu tampilan:
   ```
   ./monitor.sh
   ```

2. Tampilan monitoring menunjukkan:
   - Status aplikasi
   - Status Ngrok dan URL publik
   - Informasi jaringan
   - Penggunaan sistem (CPU, RAM, dll)
   - Uptime aplikasi

## Pemecahan Masalah

### Masalah Umum

1. **Aplikasi tidak dapat berjalan**
   - Pastikan semua dependensi terinstal dengan benar
   - Periksa log error di terminal
   - Coba restart Termux dan coba lagi

2. **Ngrok error "Tunnel session failed"**
   - Pastikan aplikasi sedang berjalan di port 5000
   - Periksa koneksi internet Anda
   - Jalankan `./download_ngrok.sh` untuk memperbaiki instalasi Ngrok

3. **Izin ditolak saat menjalankan script**
   - Jalankan perintah berikut untuk memberikan izin eksekusi:
     ```
     chmod +x *.sh *.py
     ```

4. **Database error**
   - Pastikan file database ada dan tidak rusak
   - Jika rusak, gunakan database cadangan dari direktori backup

### Reset Aplikasi

Jika Anda perlu mereset aplikasi ke kondisi awal:

```
rm -f manajemen_pelanggan.db
python main.py
```

## Fitur Lanjutan

### Backup Otomatis

1. Aktifkan backup otomatis:
   ```
   ./setup_backup.sh
   ```

2. Backup manual:
   ```
   ./backup.sh
   ```

### Startup Otomatis

Anda dapat mengatur agar aplikasi berjalan secara otomatis saat Termux dibuka:

1. Edit file `~/.bashrc`:
   ```
   nano ~/.bashrc
   ```

2. Tambahkan baris berikut di akhir file:
   ```
   cd ~/storage/shared/CusAkuntanID && ./run_app.sh
   ```

### Update Aplikasi

Untuk mendapatkan pembaruan aplikasi terbaru:

```
cd ~/storage/shared/CusAkuntanID
git pull
pip install -r requirements.txt
```

## Bantuan dan Dukungan

Jika Anda memerlukan bantuan lebih lanjut atau mengalami masalah yang tidak tercantum dalam panduan ini, silakan hubungi dukungan teknis kami melalui:

- Email: support@cusakuntanid.com
- WhatsApp: +62 812 3456 7890

---

Terima kasih telah menggunakan CusAkuntanID. Semoga aplikasi ini membantu dalam mengelola bisnis Anda!
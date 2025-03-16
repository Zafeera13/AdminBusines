# Menjalankan CusAkuntanID di Termux & Akses Jarak Jauh

## Panduan Cepat

### 1. Persiapan Awal (Lakukan sekali)
1. Download semua file proyek ke perangkat Android Anda
2. Buka Termux dan beri akses penyimpanan:
   ```
   termux-setup-storage
   ```
3. Salin file ke folder yang mudah diakses:
   ```
   mkdir -p ~/storage/shared/CusAkuntanID
   cp -r /sdcard/Download/CusAkuntanID/* ~/storage/shared/CusAkuntanID/
   cd ~/storage/shared/CusAkuntanID
   ```
4. Buat file script bisa dijalankan:
   ```
   chmod +x *.sh
   ```

### 2. Instalasi & Setup
1. Jalankan script setup:
   ```
   ./setup_termux.sh
   ```
2. Setup Ngrok (diperlukan untuk akses jarak jauh):
   ```
   ./setup_ngrok.sh
   ```
   * Ikuti petunjuk untuk mendaftar dan mendapatkan authtoken

### 3. Menjalankan Aplikasi
1. Jalankan aplikasi:
   ```
   ./run_app.sh
   ```
2. Aplikasi sekarang berjalan pada IP lokal yang ditampilkan di terminal

### 4. Akses Jarak Jauh dengan Ngrok
Ada dua cara untuk menjalankan Ngrok:

#### Metode 1: Auto Ngrok (Direkomendasikan)
1. Buka terminal Termux baru (swipe dari kiri untuk menu)
2. Jalankan Auto Ngrok dengan token yang sudah terkonfigurasi:
   ```
   cd ~/storage/shared/CusAkuntanID
   ./auto_ngrok.sh
   ```
   (Script ini akan secara otomatis mengkonfigurasi dan menjalankan Ngrok)
3. URL HTTPS untuk akses jarak jauh akan ditampilkan dengan warna hijau
4. Salin URL tersebut untuk mengakses aplikasi dari perangkat mana saja
5. Token Ngrok sudah diatur secara otomatis, jadi tidak perlu mengkonfigurasi lagi

#### Metode 2: Ngrok Manual
1. Buka terminal Termux baru (swipe dari kiri untuk menu)
2. Jalankan Ngrok melalui script Python:
   ```
   cd ~/storage/shared/CusAkuntanID
   ./run_ngrok.sh
   ```
   (Script ini akan menjalankan Ngrok dengan antarmuka yang lebih user-friendly)
3. URL HTTPS untuk akses jarak jauh akan ditampilkan dengan warna hijau
4. Salin URL tersebut untuk mengakses aplikasi dari perangkat mana saja
5. Script akan terus memonitor koneksi dan menampilkan informasi status

### 5. Monitoring Aplikasi
1. Untuk memantau status aplikasi dan Ngrok dalam satu tampilan:
   ```
   cd ~/storage/shared/CusAkuntanID
   ./monitor.sh
   ```
2. Tampilan akan menunjukkan:
   - Status aplikasi
   - Informasi jaringan
   - URL Ngrok aktif
   - Waktu uptime
   - Informasi sistem

## Catatan Penting
- Jika terjadi error, periksa log di terminal Termux
- URL Ngrok gratis bersifat sementara dan akan berubah setiap restart
- Ngrok gratis memiliki batasan bandwidth dan koneksi
- Untuk keamanan, gunakan kata sandi yang kuat pada aplikasi
- Gunakan script monitor.sh untuk melihat status real-time

Untuk panduan lebih detail, lihat file `PANDUAN_TERMUX_NGROK.md`
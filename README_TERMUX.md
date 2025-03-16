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
1. Buka terminal Termux baru (swipe dari kiri untuk menu)
2. Jalankan Ngrok:
   ```
   cd ~/storage/shared/CusAkuntanID
   ./ngrok http 5000
   ```
3. Salin URL https yang diberikan Ngrok 
4. Aplikasi sekarang dapat diakses dari perangkat mana saja menggunakan URL tersebut

## Catatan Penting
- Jika terjadi error, periksa log di terminal Termux
- URL Ngrok gratis bersifat sementara dan akan berubah setiap restart
- Ngrok gratis memiliki batasan bandwidth dan koneksi
- Untuk keamanan, gunakan kata sandi yang kuat pada aplikasi

Untuk panduan lebih detail, lihat file `PANDUAN_TERMUX_NGROK.md`
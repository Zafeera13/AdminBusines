# Panduan Penggunaan CusAkuntanID dengan Ngrok di Termux

Panduan ini menjelaskan cara menjalankan aplikasi CusAkuntanID dengan Ngrok di Termux. Dengan integrasi ini, Anda dapat mengakses aplikasi dari perangkat mana pun melalui internet.

## Apa yang Baru

- **Integrasi Satu Klik**: Jalankan aplikasi dan tunnel Ngrok dengan satu perintah
- **Token Ngrok Terkonfigurasi Otomatis**: Menggunakan token yang telah disediakan
- **Monitor Terintegrasi**: Tampilan status aplikasi dan URL tunnel dalam satu layar
- **Optimasi untuk Termux**: Dukungan khusus untuk lingkungan Termux di Android

## Persyaratan

- Termux diinstall di perangkat Android
- Internet aktif di perangkat
- Paket Python 3 terinstall di Termux

## Cara Penggunaan

### Metode Mudah (Disarankan)

1. Buka Termux dan navigasi ke direktori aplikasi CusAkuntanID
   ```
   cd /lokasi/cusakuntanid
   ```

2. Berikan izin eksekusi ke script
   ```
   chmod +x start_cusakuntanid.sh
   ```

3. Jalankan script startup
   ```
   ./start_cusakuntanid.sh
   ```

4. Tunggu hingga aplikasi dan Ngrok berjalan, Anda akan melihat URL Ngrok yang dapat diakses

5. Untuk menghentikan, tekan `Ctrl+C` di terminal

### Metode Alternatif

Jika metode mudah tidak berfungsi, Anda dapat menjalankan skrip Python secara langsung:

1. Pastikan script Python dapat dieksekusi
   ```
   chmod +x run_termux.py
   ```

2. Jalankan script Python
   ```
   python3 run_termux.py
   ```

## Fitur Tambahan

- **Pemantauan Real-time**: Status aplikasi dan Ngrok ditampilkan secara real-time
- **Deteksi Otomatis**: Mendeteksi arsitektur perangkat dan menyesuaikan instalasi Ngrok
- **Pemulihan Kesalahan**: Penanganan kesalahan dan pembersihan sumber daya saat keluar

## Troubelshooting

### Ngrok Tidak Dapat Diunduh

Jika Anda mengalami masalah saat mengunduh Ngrok:

1. Pastikan Anda memiliki koneksi internet
2. Coba unduh manual dari https://ngrok.com/download
3. Ekstrak file ke direktori aplikasi dan beri nama `ngrok`
4. Berikan izin eksekusi dengan `chmod +x ngrok`
5. Konfigurasi token dengan `./ngrok config add-authtoken 2uOCUmQVllz0FhhDb9LpQmKzQGJ_hztH72cjssCErC5nKsDi`

### Aplikasi Flask Gagal Dimulai

Jika aplikasi Flask tidak dapat dimulai:

1. Pastikan semua dependensi terinstall:
   ```
   pip install flask flask-login flask-sqlalchemy flask-wtf email-validator gunicorn
   ```

2. Periksa apakah file `main.py` ada dan berada di direktori yang benar

### URL Ngrok Tidak Muncul

Jika URL Ngrok tidak muncul setelah beberapa saat:

1. Pastikan aplikasi Flask berjalan di port 5000
2. Coba akses `http://localhost:4040` dari browser ponsel untuk melihat dashboard Ngrok
3. Jika masih bermasalah, restart aplikasi

## Catatan Penting

- URL Ngrok akan berubah setiap kali Anda memulai ulang tunnel
- Pastikan aplikasi berjalan sebelum mengakses URL Ngrok
- Koneksi akan terputus jika Termux ditutup atau ponsel dimatikan

## Lisensi

Aplikasi CusAkuntanID dan skrip integrasi Ngrok ini dilindungi hak cipta. Penggunaan hanya diizinkan untuk tujuan yang sah.
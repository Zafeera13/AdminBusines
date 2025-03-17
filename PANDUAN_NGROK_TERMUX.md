# Panduan Penggunaan Ngrok di Termux untuk CusAkuntanID

Panduan ini akan membantu Anda mengatur dan menjalankan aplikasi CusAkuntanID dengan Ngrok di Termux, sehingga aplikasi dapat diakses dari internet.

## Persiapan Awal

1. Pastikan Termux sudah terinstall di perangkat Android Anda
2. Pastikan paket Python dan dependensi sudah terinstall di Termux
3. Unduh dan pindahkan semua file dari repositori ini ke direktori proyek CusAkuntanID di Termux

## Langkah-langkah Instalasi

### Cara 1: Instalasi dan Menjalankan Otomatis (Disarankan)

1. Buka Termux dan navigasi ke folder CusAkuntanID
   ```
   cd /path/to/cusakuntanid
   ```

2. Berikan izin eksekusi ke semua script
   ```
   chmod +x *.sh *.py
   ```

3. Jalankan script all-in-one untuk menginstall semua keperluan dan menjalankan aplikasi
   ```
   ./start_app_with_ngrok.sh
   ```
   
   Script ini akan:
   - Memeriksa dan menginstall dependensi yang diperlukan
   - Menginstall dan mengonfigurasi Ngrok dengan token yang sudah disediakan
   - Menjalankan aplikasi Flask di port 5000
   - Membuat tunnel Ngrok ke aplikasi
   - Menjalankan monitor untuk melihat status aplikasi dan URL Ngrok

### Cara 2: Instalasi dan Menjalankan Manual

1. Setup Ngrok dengan token yang telah disediakan:
   ```
   python setup_ngrok_termux.py
   ```

2. Jalankan aplikasi Flask:
   ```
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```
   Atau jika gunicorn tidak tersedia:
   ```
   python main.py
   ```

3. Di terminal Termux lain, jalankan Ngrok:
   ```
   ./run_ngrok_termux.sh
   ```

4. Di terminal Termux ketiga (opsional), jalankan monitor:
   ```
   python monitor_app_termux.py
   ```

## Penjelasan File

- `setup_ngrok_termux.py`: Script untuk mengunduh dan mengonfigurasi Ngrok dengan token yang telah disediakan
- `run_ngrok_termux.sh`: Script untuk menjalankan Ngrok yang mengarah ke port 5000
- `monitor_app_termux.py`: Utility untuk memonitor status aplikasi dan Ngrok
- `start_app_with_ngrok.sh`: Script all-in-one untuk menjalankan semua komponen

## Mendapatkan URL Publik

Setelah menjalankan script, Anda akan mendapatkan URL publik Ngrok yang dapat diakses dari mana saja. URL ini akan ditampilkan di monitor dan juga di output Ngrok.

Format URL biasanya: `https://xxxx-xxxx-xxxx.ngrok.io`

## Troubleshooting

1. **Ngrok Tidak Bisa Dijalankan**
   - Pastikan Anda memiliki koneksi internet
   - Pastikan token Ngrok valid
   - Coba jalankan setup_ngrok_termux.py kembali

2. **Aplikasi Flask Tidak Berjalan**
   - Periksa error di output Flask
   - Pastikan dependensi Flask sudah terinstall
   - Pastikan port 5000 tidak digunakan oleh aplikasi lain

3. **Tidak Bisa Mengakses Dari Internet**
   - Pastikan URL Ngrok yang Anda gunakan benar
   - Pastikan aplikasi Flask berjalan di 0.0.0.0:5000, bukan 127.0.0.1:5000
   - Periksa apakah URL Ngrok mengembalikan error

## Catatan Penting

- URL Ngrok berubah setiap kali Anda menjalankan Ngrok, kecuali jika Anda menggunakan akun berbayar
- Koneksi akan terputus jika Termux ditutup atau perangkat dimatikan
- Untuk penggunaan jangka panjang, pertimbangkan untuk menggunakan layanan hosting
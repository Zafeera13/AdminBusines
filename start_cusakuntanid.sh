#!/bin/bash
# Script untuk menjalankan CusAkuntanID dengan Ngrok di Termux
# Satu kali running untuk menjalankan semua komponen

echo "==== CUSAKUNTANID DENGAN NGROK ===="
echo "Memulai aplikasi dan tunnel Ngrok..."

# Periksa apakah Python tersedia
command -v python3 >/dev/null 2>&1 || { 
    echo "Python 3 tidak terinstall di Termux."
    echo "Jalankan: pkg install python"
    exit 1
}

# Pastikan script python dapat dieksekusi
chmod +x run_termux.py

# Jalankan aplikasi terintegrasi
python3 run_termux.py

# Skrip tidak akan mencapai baris ini kecuali jika ada error,
# karena run_termux.py berjalan dalam mode blocking sampai dihentikan
echo "Aplikasi telah dihentikan."
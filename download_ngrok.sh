#!/bin/bash
# Script untuk download dan konfigurasi Ngrok menggunakan Python

echo "==== DOWNLOAD NGROK UNTUK CUSAKUNTANID ====="

# Memeriksa apakah Python tersedia
command -v python3 >/dev/null 2>&1 || { 
    echo "Python 3 tidak terinstall. Mencoba dengan python..."
    command -v python >/dev/null 2>&1 || {
        echo "ERROR: Python tidak terinstall!"
        echo "Jalankan setup_termux.sh terlebih dahulu untuk menginstall Python."
        exit 1
    }
    PYTHON_CMD="python"
} || {
    PYTHON_CMD="python3"
}

# Memastikan script Python tersedia dan dapat dieksekusi
if [ ! -f "./download_ngrok.py" ]; then
    echo "ERROR: File download_ngrok.py tidak ditemukan."
    exit 1
fi

# Membuat script Python dapat dieksekusi
chmod +x download_ngrok.py

# Menjalankan script Python untuk download dan konfigurasi Ngrok
echo "Menjalankan downloader Ngrok..."
$PYTHON_CMD download_ngrok.py

# Memastikan Ngrok memiliki izin eksekusi
if [ -f "./ngrok" ]; then
    chmod +x ./ngrok
    echo "Izin eksekusi diberikan ke ngrok"
else
    echo "PERINGATAN: File ngrok tidak ditemukan"
fi

echo "Download selesai."
#!/bin/bash
# Script untuk menyiapkan dan menjalankan CusAkuntanID di Termux

echo "==== Menyiapkan CusAkuntanID untuk Termux ===="
echo "Memperbarui paket Termux..."
pkg update && pkg upgrade -y

echo "Menginstall paket yang diperlukan..."
pkg install python git openssh sqlite -y
pkg install python-pip -y

echo "Menginstall pip dan virtualenv..."
pip install virtualenv

# Membuat direktori proyek
echo "Membuat direktori proyek..."
cd ~/storage/shared
mkdir -p CusAkuntanID
cd CusAkuntanID

# Menyalin file dari direktori saat ini (jika dijalankan dari repo yang sudah ada)
echo "Menyiapkan file aplikasi..."
if [ -f "$OLDPWD/main.py" ]; then
    cp -r $OLDPWD/* .
    cp -r $OLDPWD/.* . 2>/dev/null || true
    echo "File aplikasi telah disalin dari direktori sumber."
else
    echo "PERINGATAN: File aplikasi tidak ditemukan di direktori sumber."
    echo "Silakan salin file aplikasi secara manual ke direktori ini."
    exit 1
fi

# Menyiapkan lingkungan virtual
echo "Membuat lingkungan virtual Python..."
virtualenv venv
source venv/bin/activate

# Menginstall dependensi
echo "Menginstall dependensi Python..."
pip install flask flask-login flask-sqlalchemy flask-wtf email-validator gunicorn psycopg2-binary

echo "==== Setup selesai ===="
echo ""
echo "Untuk menjalankan aplikasi:"
echo "1. Masuk ke direktori CusAkuntanID: cd ~/storage/shared/CusAkuntanID"
echo "2. Aktifkan virtualenv: source venv/bin/activate"
echo "3. Jalankan aplikasi: gunicorn --bind 0.0.0.0:5000 --reuse-port main:app"
echo ""
echo "Untuk mengakses dari jarak jauh dengan ngrok:"
echo "1. Download dan setup ngrok (lihat PANDUAN_TERMUX_NGROK.md)"
echo "2. Jalankan: ./ngrok http 5000"
echo ""
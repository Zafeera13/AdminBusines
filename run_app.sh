#!/bin/bash
# Script untuk menjalankan aplikasi CusAkuntanID

echo "==== Menjalankan CusAkuntanID ===="

# Mengaktifkan virtualenv jika ada
if [ -d "venv" ]; then
    echo "Mengaktifkan lingkungan virtual..."
    source venv/bin/activate
else
    echo "PERINGATAN: Virtual environment tidak ditemukan."
    echo "Aplikasi akan berjalan dengan Python sistem."
fi

# Menetapkan variabel lingkungan
export FLASK_APP=main.py
export FLASK_ENV=production
export SESSION_SECRET="$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)"

# Tampilkan info koneksi
echo "==== Informasi Koneksi ===="
IPADDR=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)
echo "Aplikasi akan berjalan di: http://$IPADDR:5000"
echo "Untuk akses pada jaringan lokal, gunakan alamat di atas."
echo "Untuk akses dari jarak jauh, gunakan ngrok (lihat setup_ngrok.sh)."
echo "=============================="

# Menjalankan aplikasi dengan Gunicorn
echo "Menjalankan server..."
gunicorn --bind 0.0.0.0:5000 --reuse-port main:app

# Pesan jika server berhenti
echo ""
echo "Server telah berhenti."
echo ""
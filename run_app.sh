#!/bin/bash
# Script untuk menjalankan aplikasi CusAkuntanID di Termux

echo "==== MENJALANKAN CUSAKUNTANID ===="
echo "Aplikasi akan berjalan di port 5000"
echo ""

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

# Mencoba mendapatkan alamat IP
IP_ADDRESS=$(ifconfig 2>/dev/null | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)

if [ -z "$IP_ADDRESS" ]; then
    # Jika ifconfig tidak tersedia atau tidak ada IP non-loopback
    IP_ADDRESS="0.0.0.0"
fi

echo "Aplikasi akan tersedia di: http://$IP_ADDRESS:5000"
echo "Lokal: http://localhost:5000 atau http://127.0.0.1:5000"
echo ""
echo "Tekan Ctrl+C untuk keluar"
echo "====================================="

# Aktifkan virtualenv jika ada
if [ -d "venv" ]; then
    echo "Mengaktifkan lingkungan virtual Python..."
    source venv/bin/activate
fi

# Memeriksa dependensi (minimal)
$PYTHON_CMD -c "import flask" 2>/dev/null || {
    echo "Memasang dependensi yang diperlukan..."
    pip install flask flask-login flask-sqlalchemy flask-wtf email-validator
}

# Jalankan aplikasi
echo "Memulai aplikasi..."
if command -v gunicorn >/dev/null 2>&1; then
    gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
else
    # Gunakan server development Flask jika gunicorn tidak tersedia
    FLASK_ENV=development $PYTHON_CMD main.py
fi
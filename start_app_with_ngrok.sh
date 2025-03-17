#!/bin/bash
# Script untuk menjalankan aplikasi CusAkuntanID dengan Ngrok di Termux
# Skrip ini akan menjalankan aplikasi, ngrok, dan monitor dalam satu langkah

echo "==============================================="
echo "     MEMULAI CUSAKUNTANID DENGAN NGROK        "
echo "==============================================="
echo ""

# Periksa apakah Python tersedia
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 tidak ditemukan."
    echo "Pastikan Python 3 sudah terinstall di Termux."
    echo "Jalankan: pkg install python"
    exit 1
fi

# Periksa apakah pip tersedia
if ! command -v pip &> /dev/null; then
    echo "[ERROR] Pip tidak ditemukan."
    echo "Jalankan: pkg install python-pip"
    exit 1
fi

# Periksa apakah dependensi Python sudah terpasang
echo "Memeriksa dependensi..."
python3 -c "import flask" &> /dev/null || {
    echo "Menginstall Flask dan dependensi lainnya..."
    pip install flask flask-login flask-sqlalchemy flask-wtf email-validator gunicorn psutil
}

# Periksa apakah ngrok sudah dikonfigurasi
if [ ! -f "./ngrok" ]; then
    echo "Ngrok belum terinstall. Menjalankan setup otomatis..."
    python3 setup_ngrok_termux.py
fi

# Pastikan file dapat dieksekusi
chmod +x ./ngrok
chmod +x ./run_ngrok_termux.sh
chmod +x ./monitor_app_termux.py

# Menjalankan aplikasi di latar belakang
echo ""
echo "Memulai aplikasi Flask di port 5000..."
if command -v gunicorn &> /dev/null; then
    gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app &
else
    python3 main.py &
fi
APP_PID=$!

# Menunggu aplikasi siap
echo "Menunggu aplikasi siap..."
sleep 3

# Menjalankan Ngrok di latar belakang
echo ""
echo "Memulai tunnel Ngrok..."
./ngrok http 5000 --log=stdout > ngrok.log 2>&1 &
NGROK_PID=$!

# Menunggu Ngrok siap
echo "Menunggu Ngrok siap..."
sleep 5

# Menjalankan monitor
echo ""
echo "Memulai monitor..."
python3 monitor_app_termux.py

# Fungsi untuk penanganan shutdown
function cleanup {
    echo ""
    echo "Menghentikan semua proses..."
    kill $APP_PID 2>/dev/null
    kill $NGROK_PID 2>/dev/null
    echo "Aplikasi dihentikan. Terima kasih!"
    exit 0
}

# Tangkap sinyal SIGINT (Ctrl+C)
trap cleanup SIGINT

# Tunggu untuk proses utama selesai
wait
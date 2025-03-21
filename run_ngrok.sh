#!/bin/bash
# Script untuk menjalankan Ngrok dengan Python untuk akses jarak jauh

echo "==== Menjalankan Ngrok dengan Python ====="

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

# Memeriksa apakah script Python tersedia
if [ ! -f "./run_ngrok.py" ]; then
    echo "ERROR: File run_ngrok.py tidak ditemukan."
    echo "Silakan download ulang script atau buat file dengan nama run_ngrok.py"
    exit 1
fi

# Memastikan script Python dapat dieksekusi
chmod +x run_ngrok.py

# Menentukan port
PORT=${1:-5000}

# Aktifkan virtualenv jika ada
if [ -d "venv" ]; then
    echo "Mengaktifkan lingkungan virtual Python..."
    source venv/bin/activate
fi

# Jalankan script Python
echo "Menjalankan script Python untuk Ngrok..."
$PYTHON_CMD run_ngrok.py $PORT
#!/bin/bash
# Script untuk menjalankan setup otomatis Ngrok dengan token yang sudah dikonfigurasi

echo "==== Setup Otomatis Ngrok untuk CusAkuntanID ====="

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
if [ ! -f "./setup_ngrok_auto.py" ]; then
    echo "ERROR: File setup_ngrok_auto.py tidak ditemukan."
    echo "Silakan download ulang script atau buat file dengan nama setup_ngrok_auto.py"
    exit 1
fi

# Memastikan script Python dapat dieksekusi
chmod +x setup_ngrok_auto.py

# Aktifkan virtualenv jika ada
if [ -d "venv" ]; then
    echo "Mengaktifkan lingkungan virtual Python..."
    source venv/bin/activate
fi

# Jalankan script Python
echo "Menjalankan setup otomatis..."
$PYTHON_CMD setup_ngrok_auto.py
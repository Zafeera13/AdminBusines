#!/bin/bash
# Script untuk memonitor aplikasi CusAkuntanID

echo "==== Monitor Status CusAkuntanID ====="

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
if [ ! -f "./monitor_app.py" ]; then
    echo "ERROR: File monitor_app.py tidak ditemukan."
    echo "Silakan download ulang script atau buat file dengan nama monitor_app.py"
    exit 1
fi

# Memastikan script Python dapat dieksekusi
chmod +x monitor_app.py

# Aktifkan virtualenv jika ada
if [ -d "venv" ]; then
    echo "Mengaktifkan lingkungan virtual Python..."
    source venv/bin/activate
fi

# Jalankan script Python
echo "Menjalankan monitoring..."
$PYTHON_CMD monitor_app.py
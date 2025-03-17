#!/bin/bash
# Script otomatis untuk menjalankan Ngrok ke port 5000
# untuk CusAkuntanID di Termux

echo "==== Menjalankan Ngrok ke port 5000 (CusAkuntanID) ===="
echo "Token sudah dikonfigurasi otomatis."
echo "Tekan Ctrl+C untuk keluar"
echo ""

# Memeriksa apakah ngrok sudah ada dan sudah dikonfigurasi
if [ ! -f "./ngrok" ]; then
    echo "[ERROR] File ngrok tidak ditemukan!"
    echo "Jalankan setup_ngrok_termux.py terlebih dahulu."
    exit 1
fi

# Pastikan file dapat dieksekusi
chmod +x ./ngrok

# Memeriksa konfigurasi token
CONFIG_STATUS=$(./ngrok config check 2>&1)
if [[ "$CONFIG_STATUS" == *"invalid"* || "$CONFIG_STATUS" == *"error"* ]]; then
    echo "[ERROR] Konfigurasi Ngrok tidak valid."
    echo "Token belum dikonfigurasi. Konfigurasi ulang dengan token:"
    echo "2uOCUmQVllz0FhhDb9LpQmKzQGJ_hztH72cjssCErC5nKsDi"
    
    # Mencoba konfigurasi otomatis
    echo ""
    echo "Mencoba konfigurasi otomatis..."
    ./ngrok config add-authtoken 2uOCUmQVllz0FhhDb9LpQmKzQGJ_hztH72cjssCErC5nKsDi
    
    if [ $? -ne 0 ]; then
        echo "[ERROR] Gagal mengkonfigurasi token."
        exit 1
    else
        echo "[SUCCESS] Token berhasil dikonfigurasi!"
    fi
fi

# Menjalankan Ngrok
echo ""
echo "Membuat tunnel ke port 5000..."
./ngrok http 5000

# Jika ngrok keluar dengan error
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Ngrok keluar dengan error."
    echo "Pastikan:"
    echo "1. Token autentikasi sudah benar"
    echo "2. Koneksi internet tersedia"
    echo "3. Port 5000 tidak digunakan oleh aplikasi lain"
    echo ""
    echo "Untuk mencoba konfigurasi ulang, jalankan:"
    echo "python setup_ngrok_termux.py"
    exit 1
fi
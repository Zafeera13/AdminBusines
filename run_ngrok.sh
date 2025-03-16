#!/bin/bash
# Script untuk menjalankan Ngrok untuk akses jarak jauh

echo "==== Menjalankan Ngrok untuk Akses Jarak Jauh ===="

# Memeriksa apakah ngrok sudah diinstall
if [ ! -f "./ngrok" ]; then
    echo "ERROR: Ngrok tidak ditemukan."
    echo "Jalankan setup_ngrok.sh terlebih dahulu untuk menginstall Ngrok."
    exit 1
fi

# Memeriksa konfigurasi
if ! ./ngrok config check > /dev/null 2>&1; then
    echo "PERINGATAN: Token autentikasi Ngrok belum dikonfigurasi."
    echo "Anda dapat mengkonfigurasi token dengan perintah:"
    echo "./ngrok config add-authtoken YOUR_AUTH_TOKEN"
    
    echo ""
    echo "Ingin mengkonfigurasi token sekarang? (y/n)"
    read ANSWER
    
    if [[ "$ANSWER" == "y" || "$ANSWER" == "Y" ]]; then
        echo "Masukkan token autentikasi Ngrok Anda:"
        read TOKEN
        ./ngrok config add-authtoken $TOKEN
    fi
fi

# Menentukan port
PORT=${1:-5000}
echo "Membuat tunnel ke port: $PORT"

# Menjalankan Ngrok
echo "Memulai Ngrok..."
echo "Tekan Ctrl+C untuk berhenti."
echo ""
echo "PENTING: Salin URL HTTPS yang diberikan Ngrok untuk akses jarak jauh."
echo ""
echo "==== Output Ngrok ===="
./ngrok http $PORT
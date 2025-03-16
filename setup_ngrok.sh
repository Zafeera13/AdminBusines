#!/bin/bash
# Script untuk menyiapkan Ngrok di Termux

echo "==== Menyiapkan Ngrok untuk akses jarak jauh ===="

# Memeriksa arsitektur perangkat
ARCH=$(uname -m)
echo "Arsitektur terdeteksi: $ARCH"

# Menentukan URL download sesuai arsitektur
if [[ "$ARCH" == "aarch64" ]]; then
    NGROK_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz"
    echo "Menggunakan Ngrok untuk ARM64"
elif [[ "$ARCH" == "armv7l" ]]; then
    NGROK_URL="https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.tgz"
    echo "Menggunakan Ngrok untuk ARM"
else
    echo "Arsitektur tidak dikenali: $ARCH"
    echo "Silakan download ngrok secara manual dari https://ngrok.com/download"
    exit 1
fi

# Download Ngrok
echo "Mendownload Ngrok..."
wget $NGROK_URL -O ngrok.tgz

# Ekstrak
echo "Mengekstrak Ngrok..."
tar xvzf ngrok.tgz

# Membuat file dapat dieksekusi
chmod +x ngrok

# Meminta token autentikasi
echo "=============================================="
echo "Untuk menggunakan Ngrok, Anda perlu token autentikasi."
echo "Silakan daftar di https://ngrok.com dan dapatkan token."
echo "=============================================="
echo -n "Masukkan token autentikasi Ngrok Anda: "
read AUTHTOKEN

# Konfigurasi token
if [[ -n "$AUTHTOKEN" ]]; then
    echo "Mengkonfigurasi token Ngrok..."
    ./ngrok config add-authtoken $AUTHTOKEN
    echo "Token berhasil dikonfigurasi."
else
    echo "Token tidak dimasukkan. Anda perlu menjalankan './ngrok config add-authtoken YOUR_TOKEN' secara manual nanti."
fi

echo "==== Ngrok telah berhasil diinstall ===="
echo ""
echo "Untuk membuat tunnel dan mengakses aplikasi dari jarak jauh:"
echo "1. Pastikan aplikasi Flask berjalan di port 5000"
echo "2. Jalankan: ./ngrok http 5000"
echo "3. Salin URL yang diberikan (https://xxxx-xxxx-xxxx.ngrok.io)"
echo ""
echo "Catatan: Pastikan aplikasi berjalan dengan --bind 0.0.0.0:5000"
echo ""
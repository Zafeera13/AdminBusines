#!/usr/bin/env python3
"""
Script untuk mengatur Ngrok secara otomatis dengan token yang disediakan
untuk aplikasi CusAkuntanID
"""

import os
import sys
import platform
import subprocess
import urllib.request
import tarfile
import shutil
import time

# Token Ngrok yang sudah dikonfigurasi
NGROK_AUTH_TOKEN = "2uOCUmQVllz0FhhDb9LpQmKzQGJ_hztH72cjssCErC5nKsDi"

# URL download Ngrok untuk berbagai arsitektur
NGROK_DOWNLOAD_URLS = {
    "linux_amd64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz",
    "linux_arm": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.tgz",
    "linux_arm64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz",
    "darwin_amd64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.tgz",
    "darwin_arm64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-arm64.tgz",
    "windows_amd64": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip",
    "windows_386": "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-386.zip",
}

def print_header():
    """Menampilkan header untuk script"""
    print("=" * 70)
    print("          SETUP OTOMATIS NGROK UNTUK CUSAKUNTANID")
    print("=" * 70)
    print("\nScript ini akan mengunduh, menginstal, dan mengonfigurasi Ngrok")
    print("dengan token autentikasi yang telah dikonfigurasi.")

def get_system_info():
    """Mendapatkan informasi tentang sistem operasi dan arsitektur"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    print(f"\n[INFO] Sistem terdeteksi: {system} {machine}")
    
    # Menentukan kombinasi sistem dan arsitektur
    if system == "linux":
        if "arm" in machine:
            if "64" in machine:
                return "linux_arm64"
            else:
                return "linux_arm"
        else:
            return "linux_amd64"
    elif system == "darwin":
        if "arm" in machine:
            return "darwin_arm64"
        else:
            return "darwin_amd64"
    elif system == "windows":
        if "64" in machine:
            return "windows_amd64"
        else:
            return "windows_386"
    else:
        print(f"[ERROR] Sistem tidak didukung: {system} {machine}")
        sys.exit(1)

def download_ngrok(platform_key):
    """Mengunduh Ngrok untuk platform tertentu"""
    download_url = NGROK_DOWNLOAD_URLS.get(platform_key)
    if not download_url:
        print(f"[ERROR] Tidak ada URL download untuk platform: {platform_key}")
        sys.exit(1)
    
    print(f"\n[INFO] Mengunduh Ngrok dari: {download_url}")
    
    # Menentukan nama file
    file_name = "ngrok.tgz"
    if platform_key.startswith("windows"):
        file_name = "ngrok.zip"
    
    # Mengunduh file
    try:
        print("[INFO] Memulai download...")
        urllib.request.urlretrieve(download_url, file_name)
        print(f"[SUCCESS] Download selesai: {file_name}")
        return file_name
    except Exception as e:
        print(f"[ERROR] Gagal mengunduh Ngrok: {e}")
        sys.exit(1)

def extract_ngrok(file_name):
    """Mengekstrak file Ngrok yang diunduh"""
    try:
        print(f"\n[INFO] Mengekstrak {file_name}...")
        
        if file_name.endswith(".tgz"):
            with tarfile.open(file_name, "r:gz") as tar:
                tar.extractall(".")
        elif file_name.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(file_name, "r") as zip_ref:
                zip_ref.extractall(".")
        
        # Menghapus file yang diunduh setelah ekstraksi
        os.remove(file_name)
        
        # Pastikan ngrok dapat dieksekusi
        ngrok_exe = "ngrok"
        if platform.system().lower() == "windows":
            ngrok_exe = "ngrok.exe"
        
        if os.path.exists(ngrok_exe):
            # Membuat file dapat dieksekusi di Linux/macOS
            if platform.system().lower() != "windows":
                os.chmod(ngrok_exe, 0o755)
            print(f"[SUCCESS] Ngrok berhasil diekstrak: {ngrok_exe}")
        else:
            print(f"[ERROR] File Ngrok tidak ditemukan setelah ekstraksi")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Gagal mengekstrak Ngrok: {e}")
        sys.exit(1)

def configure_ngrok():
    """Mengonfigurasi Ngrok dengan token autentikasi"""
    ngrok_exe = "./ngrok"
    if platform.system().lower() == "windows":
        ngrok_exe = ".\\ngrok.exe"
    
    print("\n[INFO] Mengonfigurasi token autentikasi Ngrok...")
    
    try:
        # Menjalankan perintah konfigurasi
        result = subprocess.run(
            [ngrok_exe, "config", "add-authtoken", NGROK_AUTH_TOKEN],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("[SUCCESS] Token autentikasi berhasil dikonfigurasi!")
        else:
            print(f"[ERROR] Gagal mengonfigurasi token: {result.stderr}")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Gagal menjalankan perintah Ngrok: {e}")
        sys.exit(1)

def test_ngrok_connection():
    """Menguji koneksi Ngrok"""
    ngrok_exe = "./ngrok"
    if platform.system().lower() == "windows":
        ngrok_exe = ".\\ngrok.exe"
    
    print("\n[INFO] Menguji koneksi Ngrok...")
    
    try:
        # Verifikasi konfigurasi Ngrok
        result = subprocess.run(
            [ngrok_exe, "config", "check"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("[SUCCESS] Konfigurasi Ngrok valid!")
        else:
            print(f"[WARNING] Masalah pada konfigurasi Ngrok: {result.stderr}")
            
        # Menampilkan versi Ngrok
        version_result = subprocess.run(
            [ngrok_exe, "--version"],
            capture_output=True,
            text=True
        )
        
        if version_result.returncode == 0:
            print(f"[INFO] Versi Ngrok: {version_result.stdout.strip()}")
        else:
            print("[WARNING] Tidak dapat mendapatkan versi Ngrok")
            
    except Exception as e:
        print(f"[ERROR] Gagal menguji koneksi Ngrok: {e}")
        sys.exit(1)

def create_startup_script():
    """Membuat script untuk memulai Ngrok"""
    print("\n[INFO] Membuat script startup untuk Ngrok...")
    
    script_content = """#!/bin/bash
# Script otomatis untuk menjalankan Ngrok ke port 5000
# Dibuat oleh setup_ngrok_auto.py

echo "==== Menjalankan Ngrok ke port 5000 ===="
echo "Token sudah dikonfigurasi otomatis."
echo "Tekan Ctrl+C untuk keluar"
echo ""

# Menjalankan Ngrok
./ngrok http 5000
"""
    
    try:
        with open("start_ngrok_auto.sh", "w") as f:
            f.write(script_content)
        
        # Membuat script dapat dieksekusi
        os.chmod("start_ngrok_auto.sh", 0o755)
        print("[SUCCESS] Script start_ngrok_auto.sh berhasil dibuat!")
        
    except Exception as e:
        print(f"[ERROR] Gagal membuat script startup: {e}")
        sys.exit(1)

def main():
    """Fungsi utama"""
    print_header()
    
    # Mendapatkan informasi sistem
    platform_key = get_system_info()
    
    # Memeriksa apakah Ngrok sudah ada
    ngrok_exe = "ngrok"
    if platform.system().lower() == "windows":
        ngrok_exe = "ngrok.exe"
    
    if os.path.exists(ngrok_exe):
        print(f"\n[INFO] Ngrok sudah terinstall: {ngrok_exe}")
        overwrite = input("Apakah Anda ingin menginstall ulang? (y/n): ").lower()
        if overwrite != "y":
            print("\n[INFO] Melanjutkan dengan Ngrok yang sudah ada.")
            configure_ngrok()
            test_ngrok_connection()
            create_startup_script()
            print_completion()
            return
    
    # Proses instalasi
    file_name = download_ngrok(platform_key)
    extract_ngrok(file_name)
    configure_ngrok()
    test_ngrok_connection()
    create_startup_script()
    print_completion()

def print_completion():
    """Menampilkan pesan setelah setup selesai"""
    print("\n" + "=" * 70)
    print("          SETUP NGROK SELESAI!")
    print("=" * 70)
    print("\nNgrok telah berhasil diinstal dan dikonfigurasi dengan token Anda.")
    print("\nUntuk menjalankan Ngrok:")
    print("  1. Pastikan aplikasi CusAkuntanID berjalan di port 5000")
    print("  2. Jalankan: ./start_ngrok_auto.sh")
    print("  3. Atau gunakan: ./run_ngrok.sh")
    print("\nUntuk monitoring lengkap, jalankan: ./monitor.sh")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Setup dibatalkan oleh pengguna.")
        sys.exit(0)
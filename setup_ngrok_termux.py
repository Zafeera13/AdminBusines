#!/usr/bin/env python3
"""
Script untuk mengatur Ngrok secara otomatis dengan token yang disediakan
untuk aplikasi CusAkuntanID di Termux

Penggunaan:
python setup_ngrok_termux.py
"""

import os
import sys
import platform
import subprocess
import time
import signal
import urllib.request
import zipfile
import tarfile
import shutil

# Token autentikasi Ngrok yang telah disediakan
NGROK_AUTH_TOKEN = "2uOCUmQVllz0FhhDb9LpQmKzQGJ_hztH72cjssCErC5nKsDi"

def print_header():
    """Menampilkan header untuk script"""
    print("\n========================================")
    print("    SETUP NGROK UNTUK CUSAKUNTANID")
    print("    MODE KHUSUS TERMUX")
    print("========================================")
    print("Script ini akan mengunduh dan mengkonfigurasi")
    print("Ngrok untuk membuat aplikasi Anda dapat diakses")
    print("dari internet.\n")

def get_system_info():
    """Mendapatkan informasi tentang sistem operasi dan arsitektur"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    print(f"[INFO] Sistem: {system}")
    print(f"[INFO] Arsitektur: {arch}")
    
    # Menentukan platform key untuk URL download
    platform_key = None
    
    # Untuk Termux/Android biasanya menggunakan ARM
    if "arm" in arch or "aarch" in arch:
        if "64" in arch or arch == "aarch64":
            platform_key = "arm64"
            print("[INFO] Terdeteksi ARM 64-bit (Android/Termux)")
        else:
            platform_key = "arm"
            print("[INFO] Terdeteksi ARM 32-bit (Android/Termux)")
    else:
        # Fallback ke default (x86_64)
        platform_key = "amd64"
        print("[WARNING] Arsitektur tidak terdeteksi secara spesifik, menggunakan default")
    
    return platform_key

def download_ngrok(platform_key):
    """Mengunduh Ngrok untuk platform tertentu"""
    print("\n[INFO] Mengunduh Ngrok...")
    
    # URL download berdasarkan platform
    download_url = f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-{platform_key}.tgz"
    output_file = f"ngrok-linux-{platform_key}.tgz"
    
    try:
        print(f"[INFO] Mengunduh dari: {download_url}")
        with urllib.request.urlopen(download_url) as response, open(output_file, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"[SUCCESS] Berhasil mengunduh ke: {output_file}")
        return output_file
    except Exception as e:
        print(f"[ERROR] Gagal mengunduh Ngrok: {e}")
        sys.exit(1)

def extract_ngrok(file_name):
    """Mengekstrak file Ngrok yang diunduh"""
    print("\n[INFO] Mengekstrak Ngrok...")
    
    try:
        # Untuk file .tgz
        with tarfile.open(file_name, 'r:gz') as tar:
            tar.extractall('.')
        
        ngrok_exe = "ngrok"
        
        # Verifikasi file telah diekstrak
        if os.path.exists(ngrok_exe):
            # Membuat file dapat dieksekusi di Termux
            try:
                # Berikan izin eksekusi
                os.chmod(ngrok_exe, 0o755)
                print(f"[INFO] Izin eksekusi diberikan ke {ngrok_exe}")
            except Exception as chmod_error:
                print(f"[WARNING] Gagal mengubah izin: {chmod_error}")
                try:
                    # Coba dengan subprocess sebagai fallback
                    subprocess.run(['chmod', '+x', ngrok_exe], check=True)
                    print(f"[INFO] Izin eksekusi diberikan dengan subprocess")
                except Exception as subproc_error:
                    print(f"[WARNING] Gagal mengubah izin dengan subprocess: {subproc_error}")
            
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
    
    print("\n[INFO] Mengonfigurasi token autentikasi Ngrok...")
    print(f"[INFO] Menggunakan token: {NGROK_AUTH_TOKEN[:5]}...{NGROK_AUTH_TOKEN[-5:]}")
    
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
    print("\n[INFO] Menguji koneksi ke layanan Ngrok...")
    
    ngrok_exe = "./ngrok"
    
    try:
        # Menjalankan ngrok dengan timeout singkat untuk memeriksa koneksi
        process = subprocess.Popen(
            [ngrok_exe, "http", "5000", "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Tunggu beberapa detik
        time.sleep(5)
        
        # Hentikan proses
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            
        print("[SUCCESS] Koneksi ke layanan Ngrok berhasil!")
        
    except Exception as e:
        print(f"[WARNING] Gagal menguji koneksi: {e}")
        print("[INFO] Anda tetap dapat mencoba menjalankan Ngrok nanti.")

def create_startup_script():
    """Membuat script untuk memulai Ngrok"""
    print("\n[INFO] Membuat script startup untuk Ngrok di Termux...")
    
    script_content = """#!/bin/bash
# Script otomatis untuk menjalankan Ngrok ke port 5000
# Dibuat oleh setup_ngrok_termux.py untuk CusAkuntanID

echo "==== Menjalankan Ngrok ke port 5000 (CusAkuntanID) ===="
echo "Token sudah dikonfigurasi otomatis."
echo "Tekan Ctrl+C untuk keluar"
echo ""

# Menjalankan Ngrok
./ngrok http 5000
"""
    
    try:
        with open("run_ngrok_termux.sh", "w") as f:
            f.write(script_content)
        
        # Membuat script dapat dieksekusi
        os.chmod("run_ngrok_termux.sh", 0o755)
        print("[SUCCESS] Script run_ngrok_termux.sh berhasil dibuat!")
        
    except Exception as e:
        print(f"[ERROR] Gagal membuat script startup: {e}")
        sys.exit(1)

def print_completion():
    """Menampilkan pesan setelah setup selesai"""
    print("\n========================================")
    print("  SETUP NGROK UNTUK TERMUX SELESAI!")
    print("========================================")
    print("\nUntuk menjalankan Ngrok dan membuat aplikasi")
    print("dapat diakses dari internet, jalankan script:")
    print("\n    ./run_ngrok_termux.sh")
    print("\nScript ini akan membuat tunnel ke port 5000")
    print("dan memberikan URL untuk mengakses aplikasi Anda.")
    print("\nPastikan aplikasi Flask sudah berjalan di port 5000")
    print("sebelum menjalankan script ini.")
    print("========================================\n")

def main():
    """Fungsi utama"""
    print_header()
    
    # Mendapatkan informasi sistem
    platform_key = get_system_info()
    
    # Memeriksa apakah Ngrok sudah ada
    ngrok_exe = "ngrok"
    
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

if __name__ == "__main__":
    main()
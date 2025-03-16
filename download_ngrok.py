#!/usr/bin/env python3
"""
Script untuk mengunduh dan mengkonfigurasi Ngrok untuk CusAkuntanID
Khusus untuk lingkungan yang tidak memiliki wget atau curl
"""

import os
import sys
import platform
import tarfile
import zipfile
import subprocess
from urllib.request import urlretrieve
from urllib.error import URLError

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

def get_platform_key():
    """Menentukan kunci platform untuk download"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    print(f"Sistem terdeteksi: {system} {machine}")
    
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
        print(f"Sistem tidak didukung: {system} {machine}")
        return "linux_amd64"  # Default ke linux_amd64

def download_ngrok():
    """Mengunduh Ngrok"""
    platform_key = get_platform_key()
    url = NGROK_DOWNLOAD_URLS.get(platform_key)
    
    if not url:
        print(f"Error: URL download untuk platform {platform_key} tidak ditemukan")
        sys.exit(1)
    
    print(f"Mengunduh Ngrok dari: {url}")
    
    # Menentukan nama file
    filename = "ngrok.tgz"
    if url.endswith(".zip"):
        filename = "ngrok.zip"
    
    try:
        print("Memulai unduhan...")
        urlretrieve(url, filename)
        print(f"Berhasil mengunduh: {filename}")
        return filename
    except URLError as e:
        print(f"Error mengunduh Ngrok: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error tidak diketahui: {e}")
        sys.exit(1)

def extract_ngrok(filename):
    """Mengekstrak file Ngrok yang diunduh"""
    try:
        print(f"Mengekstrak {filename}...")
        
        if filename.endswith(".tgz"):
            with tarfile.open(filename, "r:gz") as tar:
                tar.extractall(".")
        elif filename.endswith(".zip"):
            with zipfile.ZipFile(filename, "r") as zip_ref:
                zip_ref.extractall(".")
        
        # Menghapus file yang diunduh
        os.remove(filename)
        
        # Menentukan nama executable
        ngrok_exe = "ngrok"
        if platform.system().lower() == "windows":
            ngrok_exe = "ngrok.exe"
        
        # Memeriksa apakah file berhasil diekstrak
        if os.path.exists(ngrok_exe):
            # Memberikan izin eksekusi
            if platform.system().lower() != "windows":
                try:
                    os.chmod(ngrok_exe, 0o777)
                    print("Izin eksekusi diberikan")
                except Exception as e:
                    print(f"Peringatan: Gagal mengubah izin file: {e}")
                    try:
                        subprocess.run(['chmod', '+x', ngrok_exe], check=True)
                        print("Izin eksekusi diberikan via subprocess")
                    except Exception as e:
                        print(f"Peringatan: Gagal menjalankan chmod: {e}")
            
            print(f"Berhasil mengekstrak Ngrok: {ngrok_exe}")
        else:
            print("Error: File Ngrok tidak ditemukan setelah ekstraksi")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error mengekstrak Ngrok: {e}")
        sys.exit(1)

def configure_ngrok():
    """Mengonfigurasi token autentikasi Ngrok"""
    ngrok_exe = "./ngrok"
    if platform.system().lower() == "windows":
        ngrok_exe = ".\\ngrok.exe"
    
    print("Mengonfigurasi token autentikasi...")
    
    try:
        # Jalankan perintah konfigurasi
        subprocess.run([ngrok_exe, "config", "add-authtoken", NGROK_AUTH_TOKEN], check=True)
        print("Token berhasil dikonfigurasi!")
    except subprocess.CalledProcessError as e:
        print(f"Error mengonfigurasi token: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error tidak diketahui: {e}")
        sys.exit(1)

def main():
    """Fungsi utama"""
    print("=" * 60)
    print("         DOWNLOADER NGROK UNTUK CUSAKUNTANID")
    print("=" * 60)
    
    filename = download_ngrok()
    extract_ngrok(filename)
    configure_ngrok()
    
    print("\nNgrok berhasil diinstal dan dikonfigurasi!")
    print("Anda dapat menjalankan Ngrok dengan perintah: ./ngrok http 5000")

if __name__ == "__main__":
    main()
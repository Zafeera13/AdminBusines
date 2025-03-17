#!/usr/bin/env python3
"""
Script Python untuk menjalankan Ngrok dan memonitoring tunnel
untuk CusAkuntanID

Penggunaan:
python run_ngrok.py [port]
"""

import os
import sys
import time
import json
import subprocess
import signal
from urllib.request import urlopen
from datetime import datetime

# Default port jika tidak ada yang diberikan
DEFAULT_PORT = 5000

def check_ngrok_installed():
    """Memeriksa apakah ngrok sudah terinstall"""
    if not os.path.exists("./ngrok"):
        print("ERROR: Ngrok tidak ditemukan.")
        print("Jalankan setup_ngrok.sh terlebih dahulu untuk menginstall Ngrok.")
        return False
    return True

def check_ngrok_token():
    """Memeriksa apakah token ngrok sudah dikonfigurasi"""
    try:
        result = subprocess.run(
            ["./ngrok", "config", "check"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        if "error" in result.stderr.lower():
            return False
        return True
    except Exception as e:
        print(f"Error saat memeriksa konfigurasi ngrok: {e}")
        return False

def configure_ngrok_token():
    """Mengkonfigurasi token Ngrok"""
    print("\n==== Konfigurasi Token Ngrok ====")
    # Menggunakan token yang telah ditentukan
    token = "2uOCUmQVllz0FhhDb9LpQmKzQGJ_hztH72cjssCErC5nKsDi"
    
    try:
        subprocess.run(
            ["./ngrok", "config", "add-authtoken", token],
            check=True
        )
        print("Token berhasil dikonfigurasi!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error mengkonfigurasi token: {e}")
        return False
    except Exception as e:
        print(f"Error tidak terduga: {e}")
        return False

def get_ngrok_tunnel_info():
    """Mendapatkan informasi tunnel dari API Ngrok"""
    try:
        api_url = "http://localhost:4040/api/tunnels"
        response = urlopen(api_url)
        data = json.loads(response.read().decode())
        
        tunnels = []
        for tunnel in data['tunnels']:
            tunnels.append({
                'name': tunnel['name'],
                'url': tunnel['public_url'],
                'proto': tunnel['proto']
            })
        
        return tunnels
    except Exception as e:
        print(f"Error mendapatkan informasi tunnel: {e}")
        return []

def display_tunnel_info():
    """Menampilkan informasi tunnel yang aktif"""
    tunnels = get_ngrok_tunnel_info()
    
    if not tunnels:
        print("Tidak ada tunnel aktif atau gagal mendapatkan informasi")
        return False
    
    print("\n==== Tunnel Ngrok Aktif ====")
    print(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for idx, tunnel in enumerate(tunnels, 1):
        print(f"{idx}. {tunnel['proto'].upper()}: {tunnel['url']}")
    
    # Menampilkan URL HTTPS dengan teks yang menonjol
    https_urls = [t['url'] for t in tunnels if t['url'].startswith('https')]
    if https_urls:
        print("\n\033[1;32m==== URL AKSES JARAK JAUH ====\033[0m")
        print(f"\033[1;32m{https_urls[0]}\033[0m")
        print("\033[1;32mSalin URL di atas untuk mengakses aplikasi dari jarak jauh\033[0m")
    
    print("\nMonitoring... Tekan Ctrl+C untuk berhenti")
    return True

def run_ngrok(port):
    """Menjalankan Ngrok dengan port tertentu"""
    ngrok_process = None
    try:
        # Menjalankan Ngrok sebagai proses terpisah
        ngrok_process = subprocess.Popen(
            ["./ngrok", "http", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Menunggu beberapa detik agar Ngrok dapat memulai API
        print(f"Memulai Ngrok pada port {port}...")
        time.sleep(3)
        
        # Setup handler untuk SIGINT (Ctrl+C)
        def signal_handler(sig, frame):
            print("\nMenghentikan Ngrok...")
            if ngrok_process:
                ngrok_process.terminate()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Memeriksa dan menampilkan informasi tunnel setiap 30 detik
        while ngrok_process.poll() is None:  # Selama proses masih berjalan
            if display_tunnel_info():
                time.sleep(30)  # Setelah berhasil, tunggu 30 detik
            else:
                print("Menunggu tunnel aktif...")
                time.sleep(5)  # Jika tunnel belum aktif, cek lebih sering
        
        print("Ngrok berhenti secara tidak terduga")
        return False
        
    except KeyboardInterrupt:
        print("\nMenghentikan Ngrok...")
        if ngrok_process:
            ngrok_process.terminate()
        return True
    except Exception as e:
        print(f"Error saat menjalankan Ngrok: {e}")
        if ngrok_process:
            ngrok_process.terminate()
        return False

def main():
    """Fungsi utama"""
    # Memeriksa apakah ngrok sudah diinstall
    if not check_ngrok_installed():
        sys.exit(1)
    
    # Memeriksa apakah token sudah dikonfigurasi
    if not check_ngrok_token():
        print("Token Ngrok belum dikonfigurasi")
        if not configure_ngrok_token():
            sys.exit(1)
    
    # Menentukan port
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Error: Port harus berupa angka, menggunakan default port {DEFAULT_PORT}")
    
    # Menampilkan info
    print("==== Menjalankan Ngrok untuk Akses Jarak Jauh ====")
    print(f"Membuat tunnel ke port: {port}")
    print("Tekan Ctrl+C untuk berhenti")
    
    # Jalankan Ngrok
    run_ngrok(port)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Script untuk menjalankan Ngrok secara otomatis dengan token terkonfigurasi
untuk aplikasi CusAkuntanID
"""

import os
import sys
import time
import json
import subprocess
import signal
from urllib.request import urlopen
from urllib.error import URLError
from datetime import datetime

# Konfigurasi
DEFAULT_PORT = 5000
CHECK_INTERVAL = 5  # detik antara pemeriksaan tunnel
NGROK_API_URL = "http://localhost:4040/api/tunnels"

# Token Ngrok yang sudah dikonfigurasi
NGROK_AUTH_TOKEN = "2uOCUmQVllz0FhhDb9LpQmKzQGJ_hztH72cjssCErC5nKsDi"

def clear_screen():
    """Membersihkan layar terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Mencetak header dan informasi waktu"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("=" * 60)
    print(f"    CUSAKUNTANID NGROK AUTO - {current_time}")
    print("=" * 60)
    print("\nMenghubungkan aplikasi ke internet dengan Ngrok...\n")

def check_ngrok_installed():
    """Memeriksa apakah ngrok sudah terinstall"""
    ngrok_exe = "./ngrok"
    if os.name == 'nt':  # Windows
        ngrok_exe = "./ngrok.exe"
        
    if not os.path.exists(ngrok_exe):
        return False
        
    # Pastikan file dapat dieksekusi
    if os.name != 'nt':  # Unix/Linux/Mac
        try:
            # Coba berikan izin eksekusi
            os.chmod(ngrok_exe, 0o777)
            print("Izin eksekusi diberikan ke file ngrok")
        except Exception as e:
            print(f"Peringatan: Gagal mengubah izin file: {e}")
            try:
                # Coba dengan subprocess
                subprocess.run(['chmod', '+x', ngrok_exe], check=False)
                print("Izin eksekusi diberikan dengan subprocess")
            except Exception as e2:
                print(f"Peringatan: Gagal dengan subprocess: {e2}")
    
    return True

def configure_ngrok_token():
    """Mengkonfigurasi token Ngrok jika belum dikonfigurasi"""
    print("Memeriksa konfigurasi token Ngrok...")
    ngrok_exe = "./ngrok"
    if os.name == 'nt':  # Windows
        ngrok_exe = "./ngrok.exe"
    
    # Pastikan file dapat dieksekusi
    if os.name != 'nt':  # Unix/Linux/Mac
        try:
            # Coba berikan izin eksekusi
            os.chmod(ngrok_exe, 0o777)
            print("Izin eksekusi diberikan ke file ngrok")
        except Exception as e:
            print(f"Peringatan: Gagal mengubah izin file: {e}")
            try:
                # Coba dengan subprocess
                subprocess.run(['chmod', '+x', ngrok_exe], check=False)
                print("Izin eksekusi diberikan dengan subprocess")
            except Exception as e2:
                print(f"Peringatan: Gagal dengan subprocess: {e2}")
    
    try:
        # Jalankan dengan path relatif
        result = subprocess.run(
            [ngrok_exe, "config", "check"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if "authtoken" not in result.stdout and "error" in result.stderr.lower():
            print("Token Ngrok belum dikonfigurasi. Mengkonfigurasi sekarang...")
            token_result = subprocess.run(
                [ngrok_exe, "config", "add-authtoken", NGROK_AUTH_TOKEN],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if token_result.returncode == 0:
                print("\033[92mToken berhasil dikonfigurasi!\033[0m")
                return True
            else:
                print(f"\033[91mGagal mengkonfigurasi token: {token_result.stderr}\033[0m")
                return False
        return True
    except Exception as e:
        print(f"\033[91mError saat memeriksa konfigurasi: {e}\033[0m")
        return False

def get_ngrok_tunnels():
    """Mendapatkan informasi tunnel Ngrok dari API"""
    try:
        response = urlopen(NGROK_API_URL)
        data = json.loads(response.read().decode())
        
        tunnels = []
        for tunnel in data['tunnels']:
            tunnels.append({
                'name': tunnel['name'],
                'url': tunnel['public_url'],
                'proto': tunnel['proto']
            })
        
        return tunnels
    except URLError:
        # API belum siap atau Ngrok belum berjalan
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def display_tunnel_info():
    """Menampilkan informasi tunnel yang aktif"""
    tunnels = get_ngrok_tunnels()
    
    if not tunnels:
        print("Menunggu tunnel Ngrok terbentuk...")
        return False
    
    print("\n==== AKSES JARAK JAUH TERSEDIA ====")
    for tunnel in tunnels:
        proto = tunnel['proto'].upper()
        url = tunnel['url']
        
        if proto == "HTTPS":
            print(f"\033[1;92m{proto}: {url}\033[0m")
        else:
            print(f"{proto}: {url}")
    
    # Menampilkan instruksi khusus untuk URL HTTPS
    https_urls = [t['url'] for t in tunnels if t['proto'].lower() == 'https']
    if https_urls:
        print("\n\033[1;92m==== URL UNTUK DIBAGIKAN ====\033[0m")
        print(f"\033[1;92m{https_urls[0]}\033[0m")
        print("\033[1;92mSalin URL di atas untuk mengakses aplikasi dari jarak jauh\033[0m")
    
    print("\nMonitoring koneksi... (Tekan Ctrl+C untuk berhenti)")
    return True

def run_ngrok(port):
    """Menjalankan Ngrok dengan port tertentu"""
    ngrok_process = None
    
    try:
        # Mendapatkan path ngrok yang tepat
        ngrok_exe = "./ngrok"
        if os.name == 'nt':  # Windows
            ngrok_exe = "./ngrok.exe"
        
        # Pastikan file dapat dieksekusi
        if os.name != 'nt':  # Unix/Linux/Mac
            try:
                # Coba berikan izin eksekusi
                os.chmod(ngrok_exe, 0o777)
                print("Izin eksekusi diberikan ke file ngrok")
            except Exception as e:
                print(f"Peringatan: Gagal mengubah izin file: {e}")
                try:
                    # Coba dengan subprocess
                    subprocess.run(['chmod', '+x', ngrok_exe], check=False)
                    print("Izin eksekusi diberikan dengan subprocess")
                except Exception as e2:
                    print(f"Peringatan: Gagal dengan subprocess: {e2}")
        
        # Coba cara alternatif jika ngrok sudah di PATH sistem
        if not os.path.exists(ngrok_exe) or not os.access(ngrok_exe, os.X_OK):
            print("Mencoba menggunakan ngrok dari PATH sistem...")
            # Cek apakah ngrok ada di PATH
            try:
                result = subprocess.run(["which", "ngrok"] if os.name != 'nt' else ["where", "ngrok"], 
                                     capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    ngrok_exe = "ngrok"  # Gunakan ngrok dari PATH
                    print(f"Menggunakan ngrok dari PATH: {result.stdout.strip()}")
            except Exception as e:
                print(f"Tidak dapat menemukan ngrok di PATH: {e}")
        
        # Menjalankan Ngrok sebagai proses terpisah
        print(f"Menjalankan: {ngrok_exe} http {port}")
        ngrok_process = subprocess.Popen(
            [ngrok_exe, "http", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print(f"Memulai Ngrok pada port {port}...")
        
        # Setup handler untuk SIGINT (Ctrl+C)
        def signal_handler(sig, frame):
            print("\nMenghentikan Ngrok...")
            if ngrok_process:
                ngrok_process.terminate()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Tunggu sebentar agar Ngrok dapat memulai
        time.sleep(3)
        
        # Loop untuk memeriksa dan menampilkan tunnel
        tunnel_info_displayed = False
        tunnel_check_count = 0
        
        while ngrok_process.poll() is None:  # Selama proses masih berjalan
            if tunnel_info_displayed:
                # Jika sudah ditampilkan, kurangi refresh rate
                time.sleep(30)
                clear_screen()
                print_header()
                display_tunnel_info()
            else:
                # Jika belum, cek lebih sering
                tunnel_info_displayed = display_tunnel_info()
                if not tunnel_info_displayed:
                    tunnel_check_count += 1
                    # Jika belum ada tunnel setelah beberapa kali cek
                    if tunnel_check_count > 10:
                        print("\nTidak dapat membuat tunnel. Memeriksa status Ngrok...")
                        subprocess.run([ngrok_exe, "diagnose"])
                        print("\nMencoba ulang...")
                        tunnel_check_count = 0
                    time.sleep(CHECK_INTERVAL)
        
        print("\nNgrok berhenti secara tidak terduga")
        return False
        
    except KeyboardInterrupt:
        print("\nMenghentikan Ngrok...")
        if ngrok_process:
            ngrok_process.terminate()
        return True
    except Exception as e:
        print(f"\nError: {e}")
        if ngrok_process:
            ngrok_process.terminate()
        return False

def setup_ngrok():
    """Melakukan setup Ngrok jika belum terinstall"""
    if not check_ngrok_installed():
        print("Ngrok belum terinstall.")
        print("Menjalankan setup otomatis...")
        
        # Jalankan script setup otomatis
        if os.path.exists("setup_ngrok_auto.py"):
            result = subprocess.run(["python", "setup_ngrok_auto.py"])
            if result.returncode != 0:
                print("Gagal melakukan setup Ngrok. Silakan jalankan setup_ngrok_auto.sh secara manual.")
                sys.exit(1)
        else:
            print("Script setup tidak ditemukan. Silakan jalankan setup_ngrok_auto.sh terlebih dahulu.")
            sys.exit(1)

def main():
    """Fungsi utama"""
    clear_screen()
    print_header()
    
    # Pastikan Ngrok tersedia
    setup_ngrok()
    
    # Konfigurasi token jika perlu
    if not configure_ngrok_token():
        print("Gagal mengkonfigurasi token Ngrok.")
        sys.exit(1)
    
    # Jalankan Ngrok dengan port default
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Port tidak valid. Menggunakan port default {DEFAULT_PORT}.")
    
    print(f"\nMembuat tunnel ke aplikasi pada port {port}...")
    run_ngrok(port)

if __name__ == "__main__":
    main()
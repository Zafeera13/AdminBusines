#!/usr/bin/env python3
"""
Script khusus Termux untuk menjalankan CusAkuntanID dengan Ngrok terintegrasi
Optimized untuk lingkungan Termux dengan minimal dependencies
"""

import os
import sys
import time
import signal
import subprocess
import threading
import json
import datetime
import urllib.request
from urllib.error import URLError

# Konfigurasi
FLASK_PORT = 5000
NGROK_TOKEN = "2uOCUmQVllz0FhhDb9LpQmKzQGJ_hztH72cjssCErC5nKsDi"
NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"

# Variabel global
flask_process = None
ngrok_process = None
stop_flag = False

def clear_screen():
    """Membersihkan layar terminal"""
    os.system('clear')

def print_header():
    """Mencetak header aplikasi"""
    clear_screen()
    print("=" * 50)
    print("     CUSAKUNTANID DENGAN NGROK DI TERMUX")
    print("=" * 50)
    print(f"Waktu: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

def print_log(message):
    """Mencatat dan mencetak log dengan timestamp"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_command(command):
    """Memeriksa apakah command tersedia"""
    return subprocess.call(f"command -v {command} > /dev/null", shell=True) == 0

def setup_ngrok():
    """Menyiapkan dan mengkonfigurasi Ngrok"""
    ngrok_path = "./ngrok"
    
    if not os.path.exists(ngrok_path):
        print_log("Ngrok belum terinstall. Mengunduh...")
        
        # Deteksi arsitektur ARM untuk Termux
        try:
            uname_output = subprocess.check_output(["uname", "-m"], text=True).strip()
            if "aarch64" in uname_output or "arm64" in uname_output:
                platform_key = "arm64"
            elif "arm" in uname_output:
                platform_key = "arm"
            else:
                platform_key = "amd64"  # fallback
            
            print_log(f"Terdeteksi arsitektur: {uname_output} (menggunakan {platform_key})")
        except:
            print_log("Tidak dapat mendeteksi arsitektur, menggunakan arm64")
            platform_key = "arm64"  # Default untuk kebanyakan perangkat Android modern
        
        # Download Ngrok
        download_url = f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-{platform_key}.tgz"
        output_file = "ngrok.tgz"
        
        try:
            print_log(f"Mengunduh dari: {download_url}")
            subprocess.run(["wget", "-q", "-O", output_file, download_url], check=True)
            
            print_log("Mengekstrak file...")
            subprocess.run(["tar", "xzf", output_file], check=True)
            
            # Hapus file unduhan
            os.remove(output_file)
            
            # Berikan izin eksekusi
            os.chmod(ngrok_path, 0o755)
            print_log("Ngrok berhasil diunduh dan diekstrak.")
        except Exception as e:
            print_log(f"Error: Gagal mengunduh atau mengekstrak Ngrok: {e}")
            return False
    
    # Konfigurasi token Ngrok
    try:
        print_log(f"Mengkonfigurasi token Ngrok...")
        subprocess.run([ngrok_path, "config", "add-authtoken", NGROK_TOKEN], 
                      check=True, capture_output=True)
        print_log("Token Ngrok berhasil dikonfigurasi.")
        return True
    except Exception as e:
        print_log(f"Error: Gagal mengkonfigurasi token Ngrok: {e}")
        return False

def start_flask_app():
    """Memulai aplikasi Flask"""
    global flask_process
    
    print_log("Memulai aplikasi CusAkuntanID...")
    
    try:
        # Cek apakah gunicorn tersedia
        if check_command("gunicorn"):
            flask_process = subprocess.Popen(
                ["gunicorn", "--bind", f"0.0.0.0:{FLASK_PORT}", 
                 "--reuse-port", "--reload", "main:app"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print_log(f"Aplikasi dimulai dengan Gunicorn pada port {FLASK_PORT}")
        else:
            # Gunakan Flask development server
            env = os.environ.copy()
            env["FLASK_APP"] = "main.py"
            
            flask_process = subprocess.Popen(
                [sys.executable, "main.py"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print_log(f"Aplikasi dimulai dengan server development pada port {FLASK_PORT}")
        
        # Tunggu sebentar untuk memastikan aplikasi berjalan
        time.sleep(2)
        
        # Periksa apakah proses masih berjalan
        if flask_process.poll() is None:
            return True
        else:
            stdout, stderr = flask_process.communicate()
            if stderr:
                print_log(f"Error: {stderr}")
            return False
    except Exception as e:
        print_log(f"Error: Gagal memulai aplikasi: {e}")
        return False

def start_ngrok():
    """Memulai Ngrok untuk tunneling"""
    global ngrok_process
    
    print_log(f"Memulai Ngrok tunnel ke port {FLASK_PORT}...")
    
    try:
        ngrok_path = "./ngrok"
        
        # Jalankan ngrok
        ngrok_process = subprocess.Popen(
            [ngrok_path, "http", str(FLASK_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Tunggu agar Ngrok dapat memulai
        time.sleep(3)
        
        # Periksa apakah ngrok masih berjalan
        if ngrok_process.poll() is None:
            print_log("Ngrok tunnel berhasil dimulai")
            return True
        else:
            stdout, stderr = ngrok_process.communicate()
            if stderr:
                print_log(f"Error Ngrok: {stderr}")
            return False
    except Exception as e:
        print_log(f"Error: Gagal memulai Ngrok: {e}")
        return False

def get_ngrok_tunnels():
    """Mendapatkan URL tunnel dari API Ngrok"""
    try:
        req = urllib.request.Request(NGROK_API_URL)
        response = urllib.request.urlopen(req, timeout=2)
        data = json.loads(response.read().decode('utf-8'))
        
        tunnels = []
        if 'tunnels' in data and len(data['tunnels']) > 0:
            for tunnel in data['tunnels']:
                tunnels.append({
                    'public_url': tunnel.get('public_url', 'N/A'),
                    'protocol': tunnel.get('proto', 'N/A')
                })
        return tunnels
    except Exception:
        return []

def monitor_loop():
    """Loop monitor untuk mencetak status aplikasi"""
    global stop_flag
    
    start_time = time.time()
    last_tunnels_check = 0
    tunnels = []
    
    while not stop_flag:
        current_time = time.time()
        
        # Periksa proses
        flask_status = "BERJALAN" if flask_process and flask_process.poll() is None else "BERHENTI"
        ngrok_status = "BERJALAN" if ngrok_process and ngrok_process.poll() is None else "BERHENTI"
        
        # Periksa tunnel setiap 30 detik
        if current_time - last_tunnels_check >= 30 and ngrok_status == "BERJALAN":
            tunnels = get_ngrok_tunnels()
            last_tunnels_check = current_time
        
        # Hitung waktu aktif
        elapsed_time = current_time - start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        hours, minutes = divmod(minutes, 60)
        
        # Cetak informasi status
        print_header()
        print(f"Status Aplikasi CusAkuntanID : {'✅' if flask_status == 'BERJALAN' else '❌'} {flask_status}")
        print(f"Status Ngrok Tunnel         : {'✅' if ngrok_status == 'BERJALAN' else '❌'} {ngrok_status}")
        print(f"Waktu Aktif                 : {hours:02d}:{minutes:02d}:{seconds:02d}")
        print("-" * 50)
        
        # Cetak URL Ngrok
        if tunnels:
            print("URL Publik (dapat diakses dari internet):")
            for tunnel in tunnels:
                print(f"  → {tunnel['public_url']} ({tunnel['protocol']})")
        elif ngrok_status == "BERJALAN":
            print("Menunggu informasi URL Ngrok...")
        else:
            print("Tunnel Ngrok tidak aktif.")
        
        print("-" * 50)
        print("URL Lokal: http://localhost:5000")
        print("Tekan Ctrl+C untuk keluar")
        print("=" * 50)
        
        # Periksa jika salah satu proses mati
        if flask_process and flask_process.poll() is not None:
            print_log("Aplikasi Flask berhenti tak terduga!")
            stop_flag = True
            break
        
        if ngrok_process and ngrok_process.poll() is not None:
            print_log("Ngrok berhenti tak terduga!")
            stop_flag = True
            break
        
        # Tunggu sebelum refresh
        time.sleep(2)

def cleanup():
    """Membersihkan dan menghentikan semua proses"""
    global stop_flag
    stop_flag = True
    
    print("\nMenghentikan aplikasi...")
    
    # Hentikan proses Flask
    if flask_process:
        flask_process.terminate()
        try:
            flask_process.wait(timeout=5)
        except:
            flask_process.kill()
    
    # Hentikan proses Ngrok
    if ngrok_process:
        ngrok_process.terminate()
        try:
            ngrok_process.wait(timeout=5)
        except:
            ngrok_process.kill()
    
    print("Aplikasi dihentikan.")

def main():
    """Fungsi utama"""
    global stop_flag
    
    print_header()
    print("Memulai CusAkuntanID dengan Ngrok di Termux...\n")
    
    # Setup Ngrok
    if not setup_ngrok():
        print_log("Gagal menyiapkan Ngrok. Menghentikan program.")
        return
    
    # Mulai aplikasi Flask
    if not start_flask_app():
        print_log("Gagal memulai aplikasi. Menghentikan program.")
        return
    
    # Mulai Ngrok
    if not start_ngrok():
        print_log("Gagal memulai Ngrok. Menghentikan program.")
        # Hentikan Flask juga
        if flask_process:
            flask_process.terminate()
        return
    
    # Set up penanganan sinyal Ctrl+C
    def signal_handler(sig, frame):
        print("\nMenerima sinyal penghentian...")
        cleanup()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Jalankan monitor dalam thread terpisah
    monitor_thread = threading.Thread(target=monitor_loop)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Tunggu monitor thread selesai
    try:
        while monitor_thread.is_alive():
            monitor_thread.join(1)
    except KeyboardInterrupt:
        # Signal handler akan menangani ini
        pass
    finally:
        cleanup()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        cleanup()
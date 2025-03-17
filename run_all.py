#!/usr/bin/env python3
"""
Script untuk menjalankan aplikasi CusAkuntanID dengan Ngrok secara terintegrasi
Jalankan script ini untuk memulai aplikasi Flask dan tunnel Ngrok secara bersamaan
"""

import os
import sys
import time
import signal
import subprocess
import threading
import json
import datetime
import platform
import logging
import urllib.request
from urllib.error import URLError

# Konfigurasi konstanta
FLASK_PORT = 5000
NGROK_TOKEN = "2uOCUmQVllz0FhhDb9LpQmKzQGJ_hztH72cjssCErC5nKsDi"
NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"

# Konfigurasi logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CusAkuntanID-Runner")

# Variabel global untuk menyimpan proses
flask_process = None
ngrok_process = None

def clear_screen():
    """Membersihkan layar terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Mencetak header aplikasi"""
    clear_screen()
    print("=" * 60)
    print("           CUSAKUNTANID DENGAN NGROK")
    print("=" * 60)
    print(f"Waktu: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

def check_python_dependencies():
    """Memeriksa dan menginstall dependensi Python yang diperlukan"""
    required_packages = [
        'flask', 'flask-login', 'flask-sqlalchemy', 'flask-wtf', 
        'email-validator', 'gunicorn', 'psutil'
    ]
    
    try:
        import pkg_resources
        installed_packages = {pkg.key for pkg in pkg_resources.working_set}
        
        missing_packages = [pkg for pkg in required_packages 
                          if pkg.replace('-', '_') not in installed_packages]
        
        if missing_packages:
            print(f"Menginstall paket yang dibutuhkan: {', '.join(missing_packages)}")
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            return True
        return True
    except Exception as e:
        logger.error(f"Gagal memeriksa dependensi: {e}")
        return False

def setup_ngrok():
    """Mengatur dan mengkonfigurasi Ngrok"""
    # Periksa apakah ngrok sudah ada
    ngrok_path = os.path.join(os.getcwd(), "ngrok")
    if os.name == 'nt':  # Windows
        ngrok_path += ".exe"
    
    if not os.path.exists(ngrok_path):
        print("Ngrok belum terinstall. Mengunduh dan mengkonfigurasi...")
        
        # Tentukan URL unduhan yang sesuai
        system = platform.system().lower()
        arch = platform.machine().lower()
        
        if "arm" in arch or "aarch" in arch:
            if "64" in arch or arch == "aarch64":
                platform_key = "arm64"
            else:
                platform_key = "arm"
        elif "x86_64" in arch or "amd64" in arch:
            platform_key = "amd64"
        else:
            platform_key = "386"  # Default ke 32-bit
        
        if system == "windows":
            download_url = f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-{platform_key}.zip"
            output_file = "ngrok.zip"
        else:
            download_url = f"https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-{platform_key}.tgz"
            output_file = "ngrok.tgz"
        
        # Unduh Ngrok
        try:
            print(f"Mengunduh Ngrok dari {download_url}...")
            with urllib.request.urlopen(download_url) as response, open(output_file, 'wb') as out_file:
                out_file.write(response.read())
            
            # Ekstrak file
            print("Mengekstrak file Ngrok...")
            if output_file.endswith(".zip"):
                import zipfile
                with zipfile.ZipFile(output_file, 'r') as zip_ref:
                    zip_ref.extractall(".")
            else:
                import tarfile
                with tarfile.open(output_file, 'r:gz') as tar:
                    tar.extractall(".")
            
            # Hapus file unduhan
            os.remove(output_file)
            
            # Berikan izin eksekusi (untuk Unix/Linux/Mac)
            if os.name != 'nt':
                os.chmod(ngrok_path, 0o755)
            
            print("Ngrok berhasil diunduh dan diekstrak.")
        except Exception as e:
            logger.error(f"Gagal mengunduh atau mengekstrak Ngrok: {e}")
            return False
    
    # Konfigurasi token Ngrok
    try:
        print(f"Mengkonfigurasi token Ngrok...")
        subprocess.run([ngrok_path, "config", "add-authtoken", NGROK_TOKEN], 
                      check=True, capture_output=True)
        print("Token Ngrok berhasil dikonfigurasi.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Gagal mengkonfigurasi token Ngrok: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error saat mengkonfigurasi Ngrok: {e}")
        return False

def start_flask_app():
    """Memulai aplikasi Flask"""
    global flask_process
    
    print("Memulai aplikasi Flask...")
    try:
        # Coba gunakan gunicorn jika tersedia (untuk lingkungan Unix/Linux)
        if os.name != 'nt' and shutil.which('gunicorn'):
            flask_process = subprocess.Popen(
                ["gunicorn", "--bind", f"0.0.0.0:{FLASK_PORT}", 
                 "--reuse-port", "--reload", "main:app"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"Aplikasi Flask dimulai dengan Gunicorn pada port {FLASK_PORT}")
        else:
            # Gunakan Flask development server jika gunicorn tidak tersedia
            # Set variabel environment untuk Flask
            env = os.environ.copy()
            env["FLASK_APP"] = "main.py"
            env["FLASK_ENV"] = "development"
            
            flask_process = subprocess.Popen(
                [sys.executable, "-m", "flask", "run", "--host=0.0.0.0", f"--port={FLASK_PORT}"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"Aplikasi Flask dimulai dengan server development pada port {FLASK_PORT}")
        
        # Tunggu beberapa detik untuk memastikan aplikasi berjalan
        time.sleep(3)
        
        # Periksa apakah proses masih berjalan
        if flask_process.poll() is None:
            return True
        else:
            stdout, stderr = flask_process.communicate()
            logger.error(f"Aplikasi Flask berhenti dengan error: {stderr}")
            return False
    except Exception as e:
        logger.error(f"Gagal memulai aplikasi Flask: {e}")
        return False

def start_ngrok():
    """Memulai Ngrok untuk tunneling"""
    global ngrok_process
    
    print(f"Memulai Ngrok tunnel ke port {FLASK_PORT}...")
    try:
        # Path ke executable ngrok
        ngrok_path = os.path.join(os.getcwd(), "ngrok")
        if os.name == 'nt':  # Windows
            ngrok_path += ".exe"
        
        # Jalankan ngrok
        ngrok_process = subprocess.Popen(
            [ngrok_path, "http", str(FLASK_PORT), "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Tunggu beberapa detik agar Ngrok dapat memulai
        time.sleep(5)
        
        # Periksa apakah ngrok masih berjalan
        if ngrok_process.poll() is None:
            print("Ngrok tunnel berhasil dimulai")
            return True
        else:
            stdout, stderr = ngrok_process.communicate()
            logger.error(f"Ngrok berhenti dengan error: {stderr}")
            return False
    except Exception as e:
        logger.error(f"Gagal memulai Ngrok: {e}")
        return False

def get_ngrok_tunnels():
    """Mendapatkan URL tunnel dari API Ngrok"""
    try:
        req = urllib.request.Request(NGROK_API_URL)
        response = urllib.request.urlopen(req, timeout=3)
        data = json.loads(response.read().decode('utf-8'))
        
        tunnels = []
        if 'tunnels' in data and len(data['tunnels']) > 0:
            for tunnel in data['tunnels']:
                tunnels.append({
                    'public_url': tunnel.get('public_url', 'N/A'),
                    'protocol': tunnel.get('proto', 'N/A')
                })
        return tunnels
    except URLError as e:
        logger.warning(f"Tidak dapat terhubung ke API Ngrok: {e}")
        return []
    except Exception as e:
        logger.warning(f"Error saat mendapatkan tunnel Ngrok: {e}")
        return []

def monitor_processes(check_interval=5):
    """Memonitor proses Flask dan Ngrok"""
    print("\nMemonitor proses aplikasi...")
    
    start_time = time.time()
    last_tunnels_check = 0
    
    try:
        while True:
            current_time = time.time()
            
            # Periksa status proses Flask
            flask_status = "BERJALAN" if flask_process and flask_process.poll() is None else "BERHENTI"
            
            # Periksa status proses Ngrok
            ngrok_status = "BERJALAN" if ngrok_process and ngrok_process.poll() is None else "BERHENTI"
            
            # Dapatkan informasi tunnel Ngrok (setiap 30 detik)
            tunnels = []
            if current_time - last_tunnels_check >= 30:
                tunnels = get_ngrok_tunnels()
                last_tunnels_check = current_time
            
            # Tampilkan informasi status
            elapsed_time = current_time - start_time
            days, remainder = divmod(elapsed_time, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            formatted_time = ""
            if days > 0:
                formatted_time += f"{int(days)}d "
            if hours > 0 or days > 0:
                formatted_time += f"{int(hours)}h "
            if minutes > 0 or hours > 0 or days > 0:
                formatted_time += f"{int(minutes)}m "
            formatted_time += f"{int(seconds)}s"
            
            # Tampilkan informasi
            print_header()
            print(f"Status Aplikasi Flask : {'✅' if flask_status == 'BERJALAN' else '❌'} {flask_status}")
            print(f"Status Ngrok Tunnel   : {'✅' if ngrok_status == 'BERJALAN' else '❌'} {ngrok_status}")
            print(f"Waktu Aktif           : {formatted_time}")
            print("-" * 60)
            
            # Tampilkan URL Ngrok
            if tunnels:
                print("URL Publik untuk Akses (bagikan untuk akses dari internet):")
                for tunnel in tunnels:
                    print(f"  → {tunnel['public_url']} ({tunnel['protocol']})")
            else:
                if ngrok_status == "BERJALAN":
                    print("Menunggu informasi URL Ngrok...")
                else:
                    print("Tunnel Ngrok tidak aktif.")
            
            print("-" * 60)
            print("URL Lokal: http://localhost:5000 atau http://127.0.0.1:5000")
            print("Tekan Ctrl+C untuk keluar")
            print("=" * 60)
            
            # Periksa jika salah satu proses mati
            if flask_process and flask_process.poll() is not None:
                logger.error("Aplikasi Flask berhenti tak terduga. Menghentikan program...")
                cleanup()
                return
            
            if ngrok_process and ngrok_process.poll() is not None:
                logger.error("Ngrok berhenti tak terduga. Menghentikan program...")
                cleanup()
                return
            
            # Tunggu beberapa detik sebelum update berikutnya
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")
        cleanup()

def cleanup():
    """Membersihkan dan menghentikan semua proses"""
    print("\nMembersihkan proses...")
    
    # Hentikan proses Flask
    if flask_process:
        print("Menghentikan aplikasi Flask...")
        flask_process.terminate()
        try:
            flask_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            flask_process.kill()
    
    # Hentikan proses Ngrok
    if ngrok_process:
        print("Menghentikan Ngrok...")
        ngrok_process.terminate()
        try:
            ngrok_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            ngrok_process.kill()
    
    print("Semua proses berhasil dihentikan.")

def read_flask_logs(flask_process):
    """Membaca dan mencatat log dari proses Flask"""
    try:
        for line in iter(flask_process.stdout.readline, ""):
            if line:
                logger.info(f"Flask: {line.strip()}")
    except Exception as e:
        logger.error(f"Error saat membaca log Flask: {e}")

def read_ngrok_logs(ngrok_process):
    """Membaca dan mencatat log dari proses Ngrok"""
    try:
        for line in iter(ngrok_process.stdout.readline, ""):
            if line:
                if "url=" in line.lower():
                    logger.info(f"Ngrok: {line.strip()}")
                else:
                    logger.debug(f"Ngrok: {line.strip()}")
    except Exception as e:
        logger.error(f"Error saat membaca log Ngrok: {e}")

def main():
    """Fungsi utama"""
    print_header()
    
    # Periksa dan setup dependensi Python
    print("Memeriksa dependensi Python...")
    if not check_python_dependencies():
        print("Gagal memastikan semua dependensi Python terinstall. Menghentikan program.")
        return
    
    # Setup Ngrok
    print("\nMenyiapkan Ngrok...")
    if not setup_ngrok():
        print("Gagal menyiapkan Ngrok. Menghentikan program.")
        return
    
    # Mulai aplikasi Flask
    print("\nMemulai aplikasi CusAkuntanID...")
    if not start_flask_app():
        print("Gagal memulai aplikasi Flask. Menghentikan program.")
        cleanup()
        return
    
    # Mulai Ngrok
    print("\nMemulai tunnel Ngrok...")
    if not start_ngrok():
        print("Gagal memulai Ngrok. Menghentikan program.")
        cleanup()
        return
    
    # Setel penanganan sinyal
    signal.signal(signal.SIGINT, lambda sig, frame: cleanup())
    
    # Buat thread untuk membaca log Flask
    flask_log_thread = threading.Thread(target=read_flask_logs, args=(flask_process,))
    flask_log_thread.daemon = True
    flask_log_thread.start()
    
    # Buat thread untuk membaca log Ngrok
    ngrok_log_thread = threading.Thread(target=read_ngrok_logs, args=(ngrok_process,))
    ngrok_log_thread.daemon = True
    ngrok_log_thread.start()
    
    # Monitor proses
    monitor_processes()

if __name__ == "__main__":
    # Pastikan modul-modul yang diperlukan tersedia
    import shutil
    
    try:
        # Jalankan fungsi utama
        main()
    except Exception as e:
        logger.error(f"Error tidak tertangani: {e}")
        # Pastikan semua proses dibersihkan
        cleanup()
        sys.exit(1)
#!/usr/bin/env python3
"""
Monitor aplikasi CusAkuntanID di Termux
Script ini memonitor status aplikasi dan memberikan informasi runtime
"""

import os
import sys
import time
import json
import socket
import psutil
import platform
import subprocess
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError

# Konfigurasi
APP_PORT = 5000
NGROK_API_URL = "http://localhost:4040/api/tunnels"
CHECK_INTERVAL = 5  # detik antara refresh

def clear_screen():
    """Membersihkan layar terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_network_interfaces():
    """Mendapatkan alamat IP dari semua antarmuka jaringan"""
    interfaces = {}
    
    # Dapatkan alamat lokal
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        interfaces["Local"] = local_ip
    except:
        interfaces["Local"] = "tidak tersedia"

    # Mendapatkan alamat IP untuk semua antarmuka
    try:
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:  # IPv4
                    if interface not in interfaces:
                        interfaces[interface] = addr.address
    except:
        pass
    
    return interfaces

def check_app_status(port):
    """Memeriksa apakah aplikasi berjalan pada port tertentu"""
    try:
        # Memeriksa apakah port terbuka
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            # Coba dapatkan respons dari aplikasi
            try:
                response = urlopen(f"http://localhost:{port}")
                if response.getcode() == 200:
                    return True, response.getcode()
                else:
                    return True, response.getcode()
            except URLError:
                return True, "Tidak dapat terhubung ke aplikasi"
        else:
            return False, f"Port {port} tertutup"
    except Exception as e:
        return False, str(e)

def get_ngrok_tunnels():
    """Mendapatkan informasi tunnel Ngrok yang aktif"""
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
        
        return True, tunnels
    except URLError:
        return False, "Ngrok API tidak tersedia"
    except Exception as e:
        return False, str(e)

def check_process_running(process_name):
    """Memeriksa apakah proses berjalan berdasarkan nama"""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True, proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False, "Proses tidak ditemukan"

def format_time_elapsed(start_time):
    """Format waktu yang telah berlalu dalam format yang mudah dibaca"""
    elapsed = time.time() - start_time
    
    days, remainder = divmod(elapsed, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

def print_header():
    """Mencetak header untuk tampilan monitor"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    clear_screen()
    print("=" * 70)
    print(f"    CUSAKUNTANID MONITORING SYSTEM - {current_time}")
    print("=" * 70)

def print_system_info():
    """Mencetak informasi sistem"""
    print("\n===== INFORMASI SISTEM =====")
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    print(f"CPU: {cpu_percent}% (dari {cpu_count} core)")
    
    # Memory
    memory = psutil.virtual_memory()
    memory_used_mb = memory.used / (1024 * 1024)
    memory_total_mb = memory.total / (1024 * 1024)
    memory_percent = memory.percent
    print(f"Memory: {memory_used_mb:.1f} MB / {memory_total_mb:.1f} MB ({memory_percent}%)")
    
    # Disk
    disk = psutil.disk_usage('.')
    disk_used_gb = disk.used / (1024 * 1024 * 1024)
    disk_total_gb = disk.total / (1024 * 1024 * 1024)
    disk_percent = disk.percent
    print(f"Disk: {disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB ({disk_percent}%)")
    
    # Sistem Operasi
    print(f"OS: {platform.system()} {platform.release()}")
    
    # Python
    print(f"Python: {platform.python_version()}")

def print_network_info():
    """Mencetak informasi jaringan"""
    print("\n===== INFORMASI JARINGAN =====")
    
    interfaces = get_network_interfaces()
    for name, ip in interfaces.items():
        print(f"{name}: {ip}")
    
    print(f"App URL (lokal): http://localhost:{APP_PORT}")

def print_app_status(start_time):
    """Mencetak status aplikasi"""
    app_running, app_status = check_app_status(APP_PORT)
    ngrok_running, ngrok_pid = check_process_running("ngrok")
    
    uptime = format_time_elapsed(start_time)
    
    print("\n===== STATUS APLIKASI =====")
    print(f"Uptime: {uptime}")
    
    if app_running:
        print(f"\033[92mCusAkuntanID: BERJALAN (Port {APP_PORT})\033[0m")
    else:
        print(f"\033[91mCusAkuntanID: BERHENTI ({app_status})\033[0m")
    
    if ngrok_running:
        print(f"\033[92mNgrok: BERJALAN (PID {ngrok_pid})\033[0m")
    else:
        print(f"\033[91mNgrok: BERHENTI ({ngrok_pid})\033[0m")
    
def print_ngrok_status():
    """Mencetak status tunnel Ngrok"""
    ngrok_status, tunnel_info = get_ngrok_tunnels()
    
    print("\n===== STATUS NGROK =====")
    
    if not ngrok_status:
        print(f"\033[91mNgrok API: {tunnel_info}\033[0m")
        return
    
    if not tunnel_info:
        print("\033[93mTidak ada tunnel aktif\033[0m")
        return
    
    print("\033[92mTunnel aktif:\033[0m")
    for tunnel in tunnel_info:
        try:
            # Mengakses nilai dengan cara yang aman
            proto = str(tunnel['proto']).upper() if 'proto' in tunnel else 'UNKNOWN'
            url = str(tunnel['url']) if 'url' in tunnel else 'URL tidak tersedia'
            
            if proto == "HTTPS":
                print(f"\033[1;92m{proto}: {url}\033[0m")
            else:
                print(f"{proto}: {url}")
        except Exception as e:
            print(f"Error menampilkan info tunnel: {e}")

def print_footer():
    """Mencetak footer dengan petunjuk"""
    print("\n" + "=" * 70)
    print("Tekan Ctrl+C untuk keluar | Refresh setiap 5 detik")
    print("=" * 70)

def monitor_loop():
    """Loop utama untuk memonitor status"""
    start_time = time.time()
    
    try:
        while True:
            print_header()
            print_app_status(start_time)
            print_ngrok_status()
            print_network_info()
            print_system_info()
            print_footer()
            
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\nMenghentikan monitoring...")
        sys.exit(0)

if __name__ == "__main__":
    try:
        # Pastikan psutil tersedia
        import psutil
    except ImportError:
        print("Library psutil tidak ditemukan. Menginstallnya...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            print("psutil berhasil diinstall. Memulai monitoring...")
            import psutil
        except:
            print("Gagal menginstall psutil. Jalankan 'pip install psutil' terlebih dahulu.")
            sys.exit(1)
    
    monitor_loop()
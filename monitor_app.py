#!/usr/bin/env python3
"""
Monitor aplikasi CusAkuntanID di Termux
Script ini memonitor status aplikasi dan memberikan informasi runtime
"""

import os
import sys
import time
import signal
import subprocess
import datetime
import platform
import socket
import json
from urllib.request import urlopen
from urllib.error import URLError

# Konfigurasi
APP_PORT = 5000
CHECK_INTERVAL = 10  # detik antara pemeriksaan status
NGROK_API_URL = "http://localhost:4040/api/tunnels"

def clear_screen():
    """Membersihkan layar terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_network_interfaces():
    """Mendapatkan alamat IP dari semua antarmuka jaringan"""
    interfaces = {}
    
    try:
        # Mendapatkan hostname
        hostname = socket.gethostname()
        interfaces["hostname"] = hostname
        
        # Mendapatkan alamat IP lokal
        interfaces["localhost"] = "127.0.0.1"
        
        # Mencoba mendapatkan alamat IP non-loopback
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Tidak perlu benar-benar terhubung
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        
        interfaces["primary_ip"] = ip
        
        # Mencoba mendapatkan semua alamat IP
        try:
            for ifaceName in socket.if_nameindex():
                if isinstance(ifaceName, tuple) and len(ifaceName) >= 2:
                    iface_name = ifaceName[1]
                    ip_addrs = socket.getaddrinfo(socket.gethostname(), None)
                    for ip_addr in ip_addrs:
                        if ip_addr[0] == socket.AF_INET:  # IPv4
                            interfaces[iface_name] = ip_addr[4][0]
                            break
        except (AttributeError, socket.error):
            # Socket.if_nameindex tidak tersedia di semua platform
            pass
    
    except Exception as e:
        print(f"Error mendapatkan informasi jaringan: {e}")
    
    return interfaces

def check_app_status(port):
    """Memeriksa apakah aplikasi berjalan pada port tertentu"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except Exception:
        return False

def get_ngrok_tunnels():
    """Mendapatkan informasi tunnel Ngrok yang aktif"""
    try:
        response = urlopen(NGROK_API_URL)
        data = json.loads(response.read().decode())
        return data.get('tunnels', [])
    except (URLError, json.JSONDecodeError) as e:
        # Ngrok mungkin tidak berjalan, atau API tidak tersedia
        return []
    except Exception as e:
        print(f"Error tak terduga: {e}")
        return []

def check_process_running(process_name):
    """Memeriksa apakah proses berjalan berdasarkan nama"""
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output(["tasklist"], text=True)
            return process_name.lower() in output.lower()
        else:
            # Linux/Unix/Android
            output = subprocess.check_output(["ps", "aux"], text=True)
            return process_name.lower() in output.lower()
    except Exception:
        return False

def format_time_elapsed(start_time):
    """Format waktu yang telah berlalu dalam format yang mudah dibaca"""
    elapsed = datetime.datetime.now() - start_time
    days = elapsed.days
    hours, remainder = divmod(elapsed.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def print_header():
    """Mencetak header untuk tampilan monitor"""
    print("=" * 50)
    print(f"  MONITOR STATUS CUSAKUNTANID - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

def print_system_info():
    """Mencetak informasi sistem"""
    print("\n--- INFORMASI SISTEM ---")
    print(f"Sistem Operasi: {platform.system()} {platform.release()}")
    try:
        if platform.system() != "Windows":
            # Mendapatkan informasi memori di Linux/Android
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            total = int([i for i in meminfo.split() if i.isdigit()][0]) // 1024
            print(f"Total Memori: {total} MB")
    except Exception:
        pass

def print_network_info():
    """Mencetak informasi jaringan"""
    interfaces = get_network_interfaces()
    
    print("\n--- INFORMASI JARINGAN ---")
    print(f"Hostname: {interfaces.get('hostname', 'Tidak diketahui')}")
    print(f"IP Lokal: {interfaces.get('localhost', '127.0.0.1')}")
    print(f"IP Utama: {interfaces.get('primary_ip', 'Tidak diketahui')}")
    
    # Alamat IP lainnya
    other_ips = {k: v for k, v in interfaces.items() 
                if k not in ['hostname', 'localhost', 'primary_ip']}
    if other_ips:
        print("Antarmuka Lainnya:")
        for name, ip in other_ips.items():
            print(f"  - {name}: {ip}")

def print_app_status(start_time):
    """Mencetak status aplikasi"""
    app_running = check_app_status(APP_PORT)
    
    print("\n--- STATUS APLIKASI ---")
    if app_running:
        print(f"Status: \033[92mBERJALAN\033[0m pada port {APP_PORT}")
        print(f"Waktu Aktif: {format_time_elapsed(start_time)}")
        print(f"URL Lokal: http://localhost:{APP_PORT}")
        print(f"URL Jaringan: http://{get_network_interfaces().get('primary_ip', '127.0.0.1')}:{APP_PORT}")
    else:
        print(f"Status: \033[91mTIDAK BERJALAN\033[0m")
        print("Aplikasi tidak terdeteksi pada port yang ditentukan.")

def print_ngrok_status():
    """Mencetak status tunnel Ngrok"""
    ngrok_running = check_process_running("ngrok")
    tunnels = get_ngrok_tunnels() if ngrok_running else []
    
    print("\n--- STATUS NGROK ---")
    if ngrok_running:
        print(f"Status: \033[92mBERJALAN\033[0m")
        if tunnels:
            print("Tunnel Aktif:")
            for tunnel in tunnels:
                tunnel_url = tunnel.get('public_url', 'Tidak diketahui')
                proto = tunnel.get('proto', 'Tidak diketahui')
                print(f"  - {proto.upper()}: {tunnel_url}")
                
                # Menyoroti URL HTTPS
                if tunnel_url.startswith('https://'):
                    print(f"\n\033[1;32m==== URL AKSES JARAK JAUH ====\033[0m")
                    print(f"\033[1;32m{tunnel_url}\033[0m")
        else:
            print("Tidak ada tunnel aktif atau API Ngrok tidak tersedia.")
    else:
        print(f"Status: \033[91mTIDAK BERJALAN\033[0m")
        print("Ngrok tidak terdeteksi. Jalankan dengan: ./run_ngrok.sh")

def print_footer():
    """Mencetak footer dengan petunjuk"""
    print("\n" + "=" * 50)
    print("Petunjuk:")
    print("  - Tekan Ctrl+C untuk keluar")
    print("  - Status diperbarui setiap 10 detik")
    print("=" * 50)

def monitor_loop():
    """Loop utama untuk memonitor status"""
    start_time = datetime.datetime.now()
    
    try:
        while True:
            clear_screen()
            print_header()
            print_system_info()
            print_network_info()
            print_app_status(start_time)
            print_ngrok_status()
            print_footer()
            
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        clear_screen()
        print("\nMonitoring dihentikan oleh pengguna.")
        sys.exit(0)

if __name__ == "__main__":
    print("Memulai monitor CusAkuntanID...")
    monitor_loop()
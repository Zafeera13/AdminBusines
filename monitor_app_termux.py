#!/usr/bin/env python3
"""
Monitor aplikasi CusAkuntanID dan Ngrok di Termux
Script ini memonitor status aplikasi dan tunnel Ngrok, memberikan informasi runtime
"""

import os
import sys
import time
import subprocess
import socket
import json
import datetime
import platform
import signal
import psutil

# Konstanta
NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"
APP_PORT = 5000
CHECK_INTERVAL = 5  # Dalam detik

def clear_screen():
    """Membersihkan layar terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_network_interfaces():
    """Mendapatkan alamat IP dari semua antarmuka jaringan"""
    interfaces = {}
    
    try:
        # Cara 1: Menggunakan socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        interfaces["local"] = local_ip
    except:
        interfaces["local"] = "127.0.0.1"
    
    try:
        # Cara 2: Mencoba mendapatkan dari ifconfig/ip (khusus untuk Termux/Linux)
        if os.name != 'nt':  # Not Windows
            # Coba dengan ip addr
            try:
                ip_output = subprocess.check_output(["ip", "addr", "show"], text=True)
                for line in ip_output.split('\n'):
                    if 'inet ' in line and not 'inet 127.0.0.1' in line:
                        # Extract IP address
                        parts = line.strip().split()
                        inet_idx = parts.index('inet')
                        if len(parts) > inet_idx:
                            ip = parts[inet_idx + 1].split('/')[0]
                            interfaces["network"] = ip
                            break
            except:
                # Fallback to ifconfig if ip command not available
                try:
                    ifconfig_output = subprocess.check_output(["ifconfig"], text=True)
                    for line in ifconfig_output.split('\n'):
                        if 'inet ' in line and not '127.0.0.1' in line:
                            ip = line.strip().split()[1].replace('addr:', '')
                            interfaces["network"] = ip
                            break
                except:
                    pass
    except:
        pass
    
    # Tambahkan localhost
    interfaces["localhost"] = "127.0.0.1"
    
    return interfaces

def check_app_status(port):
    """Memeriksa apakah aplikasi berjalan pada port tertentu"""
    status = {
        "running": False,
        "url": f"http://localhost:{port}",
        "process": None
    }
    
    # Memeriksa apakah port terbuka
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    if result == 0:
        status["running"] = True
    sock.close()
    
    # Coba temukan proses yang menggunakan port tersebut
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                for conn in proc.connections(kind='inet'):
                    if conn.laddr.port == port:
                        status["process"] = {
                            "pid": proc.pid,
                            "name": proc.name(),
                            "cmdline": proc.cmdline()
                        }
                        break
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
    except:
        pass
    
    return status

def get_ngrok_tunnels():
    """Mendapatkan informasi tunnel Ngrok yang aktif"""
    tunnels = {
        "running": False,
        "urls": [],
        "process": None
    }
    
    # Memeriksa apakah ngrok API tersedia
    try:
        import urllib.request
        import json
        
        # Coba akses API ngrok
        req = urllib.request.Request(NGROK_API_URL)
        response = urllib.request.urlopen(req, timeout=2)
        data = json.loads(response.read().decode('utf-8'))
        
        if 'tunnels' in data and len(data['tunnels']) > 0:
            tunnels["running"] = True
            for tunnel in data['tunnels']:
                tunnels["urls"].append({
                    "public_url": tunnel.get('public_url', 'N/A'),
                    "protocol": tunnel.get('proto', 'N/A'),
                    "local_url": tunnel.get('config', {}).get('addr', 'N/A')
                })
    except:
        pass
    
    # Cek apakah proses ngrok berjalan
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'ngrok' in proc.name() or any('ngrok' in cmd for cmd in proc.cmdline()):
                    tunnels["process"] = {
                        "pid": proc.pid,
                        "name": proc.name(),
                        "cmdline": proc.cmdline()
                    }
                    if not tunnels["running"]:
                        tunnels["running"] = True
                        tunnels["urls"].append({
                            "public_url": "Tunneling active but API not accessible",
                            "protocol": "N/A",
                            "local_url": f"localhost:{APP_PORT}"
                        })
                    break
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
    except:
        pass
    
    return tunnels

def check_process_running(process_name):
    """Memeriksa apakah proses berjalan berdasarkan nama"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if process_name.lower() in proc.name().lower() or any(process_name.lower() in cmd.lower() for cmd in proc.cmdline()):
                    return proc
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
    except:
        pass
    return None

def format_time_elapsed(start_time):
    """Format waktu yang telah berlalu dalam format yang mudah dibaca"""
    elapsed = time.time() - start_time
    
    days, remainder = divmod(elapsed, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    time_parts = []
    if days > 0:
        time_parts.append(f"{int(days)}d")
    if hours > 0 or days > 0:
        time_parts.append(f"{int(hours)}h")
    if minutes > 0 or hours > 0 or days > 0:
        time_parts.append(f"{int(minutes)}m")
    time_parts.append(f"{int(seconds)}s")
    
    return " ".join(time_parts)

def print_header():
    """Mencetak header untuk tampilan monitor"""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    clear_screen()
    print("=" * 50)
    print(f"     MONITOR CUSAKUNTANID DI TERMUX")
    print("=" * 50)
    print(f"Waktu: {current_time}")
    print("-" * 50)

def print_system_info():
    """Mencetak informasi sistem"""
    print("[INFORMASI SISTEM]")
    print(f"Sistem Operasi: {platform.system()} {platform.release()}")
    print(f"Terminal: Termux")
    
    # CPU dan RAM
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_usage = (memory.total - memory.available) / memory.total * 100
        
        print(f"CPU: {cpu_percent:.1f}% | RAM: {memory_usage:.1f}%")
    except:
        print("CPU & RAM: Tidak tersedia")
    
    print("-" * 50)

def print_network_info():
    """Mencetak informasi jaringan"""
    interfaces = get_network_interfaces()
    
    print("[JARINGAN]")
    for name, ip in interfaces.items():
        print(f"{name.capitalize()}: {ip}")
    
    print("-" * 50)

def print_app_status(start_time):
    """Mencetak status aplikasi"""
    app_status = check_app_status(APP_PORT)
    
    print("[STATUS APLIKASI]")
    if app_status["running"]:
        print(f"Status: ✅ BERJALAN")
        print(f"URL: {app_status['url']}")
        if app_status["process"]:
            print(f"PID: {app_status['process']['pid']} | Nama: {app_status['process']['name']}")
        print(f"Waktu aktif: {format_time_elapsed(start_time)}")
    else:
        print("Status: ❌ TIDAK BERJALAN")
        print("Aplikasi Flask tidak terdeteksi di port 5000")
    
    print("-" * 50)

def print_ngrok_status():
    """Mencetak status tunnel Ngrok"""
    ngrok_tunnels = get_ngrok_tunnels()
    
    print("[STATUS NGROK]")
    if ngrok_tunnels["running"]:
        print("Status: ✅ BERJALAN")
        if ngrok_tunnels["process"]:
            print(f"PID: {ngrok_tunnels['process']['pid']} | Nama: {ngrok_tunnels['process']['name']}")
        
        if len(ngrok_tunnels["urls"]) > 0:
            print("\nURLs Publik (Bagikan ini untuk akses):")
            for tunnel in ngrok_tunnels["urls"]:
                print(f"  → {tunnel['public_url']} ({tunnel['protocol']})")
        else:
            print("Tunnel sedang aktif tapi tidak ada URL yang terdeteksi")
    else:
        print("Status: ❌ TIDAK BERJALAN")
        print("Ngrok tidak terdeteksi. Jalankan run_ngrok_termux.sh untuk memulai tunnel.")
    
    print("-" * 50)

def print_footer():
    """Mencetak footer dengan petunjuk"""
    print("PETUNJUK:")
    print("1. Pastikan aplikasi Flask berjalan di port 5000")
    print("2. Jalankan run_ngrok_termux.sh untuk tunnel internet")
    print("3. Tekan Ctrl+C untuk keluar dari monitor")
    print("=" * 50)

def monitor_loop():
    """Loop utama untuk memonitor status"""
    start_time = time.time()
    
    try:
        while True:
            print_header()
            print_system_info()
            print_network_info()
            print_app_status(start_time)
            print_ngrok_status()
            print_footer()
            
            # Jeda sebelum refresh
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        clear_screen()
        print("Monitor dihentikan. Terima kasih!")

if __name__ == "__main__":
    monitor_loop()
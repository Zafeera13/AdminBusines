import os
import sqlite3
import datetime
from datetime import date
import webbrowser
import hashlib
import secrets
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

# Konfigurasi logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "rahasia_aplikasi_manajemen_pelanggan")
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)

# Template global context
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}

class Pengguna:
    def __init__(self, db_path='manajemen_pelanggan.db'):
        self.db_path = db_path
        self.buat_tabel()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def buat_tabel(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Buat tabel pengguna
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pengguna (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nama_lengkap TEXT,
            email TEXT,
            level TEXT DEFAULT 'user',
            dibuat_pada TEXT
        )
        ''')

        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Menghasilkan hash password yang aman"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password, nama_lengkap="", email="", level="user"):
        """Mendaftarkan pengguna baru"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Periksa apakah username sudah digunakan
        cursor.execute("SELECT id FROM pengguna WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username sudah digunakan"

        # Hash password dan simpan pengguna baru
        password_hash = self.hash_password(password)
        dibuat_pada = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute('''
            INSERT INTO pengguna (username, password_hash, nama_lengkap, email, level, dibuat_pada)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, nama_lengkap, email, level, dibuat_pada))
            conn.commit()
            conn.close()
            return True, "Registrasi berhasil"
        except Exception as e:
            conn.close()
            return False, f"Kesalahan: {str(e)}"

    def login(self, username, password):
        """Memeriksa login pengguna"""
        conn = self.get_connection()
        cursor = conn.cursor()

        password_hash = self.hash_password(password)
        cursor.execute("SELECT id, username, nama_lengkap, level FROM pengguna WHERE username = ? AND password_hash = ?", 
                      (username, password_hash))
        user = cursor.fetchone()
        conn.close()

        if user:
            return True, {"id": user[0], "username": user[1], "nama_lengkap": user[2], "level": user[3]}
        else:
            return False, "Username atau password salah"

    def get_user(self, user_id):
        """Mendapatkan data pengguna berdasarkan ID"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, nama_lengkap, email, level, dibuat_pada FROM pengguna WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        return user

    def get_all_users(self):
        """Mendapatkan semua data pengguna"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, nama_lengkap, email, level, dibuat_pada FROM pengguna ORDER BY username")
            users = cursor.fetchall()
            return users
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def update_user(self, user_id, nama_lengkap=None, email=None, level=None, password=None):
        """Memperbarui data pengguna"""
        pembaruan = []
        nilai = []

        if nama_lengkap is not None:
            pembaruan.append("nama_lengkap = ?")
            nilai.append(nama_lengkap)
        if email is not None:
            pembaruan.append("email = ?")
            nilai.append(email)
        if level is not None:
            pembaruan.append("level = ?")
            nilai.append(level)
        if password is not None:
            pembaruan.append("password_hash = ?")
            password_hash = self.hash_password(password)
            nilai.append(password_hash)

        if not pembaruan:
            return False, "Tidak ada perubahan untuk disimpan"

        query = f"UPDATE pengguna SET {', '.join(pembaruan)} WHERE id = ?"
        nilai.append(user_id)

        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, nilai)
            conn.commit()
            return True, "Data user berhasil diperbarui"
        except Exception as e:
            return False, f"Kesalahan: {str(e)}"
        finally:
            if conn:
                conn.close()

    def delete_user(self, user_id):
        """Menghapus data pengguna"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Periksa apakah masih ada pelanggan yang terkait dengan user ini
            cursor.execute("SELECT COUNT(*) FROM pelanggan WHERE user_id = ?", (user_id,))
            pelanggan_count = cursor.fetchone()[0]
            if pelanggan_count > 0:
                conn.close()
                return False, f"Tidak dapat menghapus user karena masih memiliki {pelanggan_count} pelanggan"

            cursor.execute("DELETE FROM pengguna WHERE id = ?", (user_id,))
            conn.commit()
            return True, "User berhasil dihapus"
        except Exception as e:
            return False, f"Kesalahan: {str(e)}"
        finally:
            if conn:
                conn.close()

class SistemManajemenPelanggan:
    def __init__(self):
        # Inisialisasi database
        self.db_path = 'manajemen_pelanggan.db'
        self.buat_tabel()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def buat_tabel(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Buat tabel pelanggan dengan kolom user_id
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pelanggan (
            id INTEGER PRIMARY KEY,
            nama TEXT NOT NULL,
            telepon TEXT,
            email TEXT,
            alamat TEXT,
            latitude REAL,
            longitude REAL,
            dibuat_pada TEXT,
            user_id INTEGER
        )
        ''')

        # Periksa apakah kolom user_id sudah ada, jika belum tambahkan
        try:
            cursor.execute("PRAGMA table_info(pelanggan)")
            kolom = cursor.fetchall()
            kolom_names = [col[1] for col in kolom]

            if 'user_id' not in kolom_names:
                cursor.execute("ALTER TABLE pelanggan ADD COLUMN user_id INTEGER")
                print("Kolom user_id berhasil ditambahkan ke tabel pelanggan")
        except sqlite3.OperationalError as e:
            print(f"Info: {e}")

        # Buat tabel tagihan
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tagihan (
            id INTEGER PRIMARY KEY,
            pelanggan_id INTEGER,
            jumlah REAL NOT NULL,
            deskripsi TEXT,
            tanggal_jatuh_tempo TEXT,
            status_pembayaran TEXT DEFAULT 'BELUM DIBAYAR',
            dibuat_pada TEXT,
            FOREIGN KEY (pelanggan_id) REFERENCES pelanggan (id)
        )
        ''')
        
        # Buat tabel akuntansi
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS akuntansi (
            id INTEGER PRIMARY KEY,
            jenis TEXT NOT NULL,
            jumlah REAL NOT NULL,
            deskripsi TEXT,
            tanggal TEXT NOT NULL,
            created_by INTEGER,
            dibuat_pada TEXT,
            FOREIGN KEY (created_by) REFERENCES pengguna (id)
        )
        ''')

        conn.commit()
        conn.close()

    def tambah_pelanggan(self, nama, telepon="", email="", alamat="", lat=0.0, lng=0.0, user_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        dibuat_pada = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
        INSERT INTO pelanggan (nama, telepon, email, alamat, latitude, longitude, dibuat_pada, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nama, telepon, email, alamat, lat, lng, dibuat_pada, user_id))
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid

    def perbarui_pelanggan(self, pelanggan_id, nama=None, telepon=None, email=None, alamat=None, lat=None, lng=None):
        pembaruan = []
        nilai = []

        if nama is not None:
            pembaruan.append("nama = ?")
            nilai.append(nama)
        if telepon is not None:
            pembaruan.append("telepon = ?")
            nilai.append(telepon)
        if email is not None:
            pembaruan.append("email = ?")
            nilai.append(email)
        if alamat is not None:
            pembaruan.append("alamat = ?")
            nilai.append(alamat)
        if lat is not None:
            pembaruan.append("latitude = ?")
            nilai.append(lat)
        if lng is not None:
            pembaruan.append("longitude = ?")
            nilai.append(lng)

        if not pembaruan:
            return False

        query = f"UPDATE pelanggan SET {', '.join(pembaruan)} WHERE id = ?"
        nilai.append(pelanggan_id)

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, nilai)
        conn.commit()
        conn.close()
        return True

    def hapus_pelanggan(self, pelanggan_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tagihan WHERE pelanggan_id = ?", (pelanggan_id,))
        cursor.execute("DELETE FROM pelanggan WHERE id = ?", (pelanggan_id,))
        conn.commit()
        conn.close()

    def dapatkan_pelanggan(self, pelanggan_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pelanggan WHERE id = ?", (pelanggan_id,))
        hasil = cursor.fetchone()
        conn.close()
        return hasil

    def dapatkan_semua_pelanggan(self, user_id=None):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if user_id is not None:
                cursor.execute("SELECT * FROM pelanggan WHERE user_id = ? ORDER BY nama", (user_id,))
            else:
                cursor.execute("SELECT * FROM pelanggan ORDER BY nama")

            hasil = cursor.fetchall()
            return hasil
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def tambah_tagihan(self, pelanggan_id, jumlah, deskripsi="", tanggal_jatuh_tempo=None):
        if tanggal_jatuh_tempo is None:
            # Set tanggal jatuh tempo default 14 hari dari sekarang
            tanggal_jatuh_tempo = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")

        dibuat_pada = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO tagihan (pelanggan_id, jumlah, deskripsi, tanggal_jatuh_tempo, dibuat_pada)
        VALUES (?, ?, ?, ?, ?)
        ''', (pelanggan_id, jumlah, deskripsi, tanggal_jatuh_tempo, dibuat_pada))
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid

    def perbarui_tagihan(self, tagihan_id, jumlah=None, deskripsi=None, tanggal_jatuh_tempo=None, status_pembayaran=None):
        pembaruan = []
        nilai = []

        if jumlah is not None:
            pembaruan.append("jumlah = ?")
            nilai.append(jumlah)
        if deskripsi is not None:
            pembaruan.append("deskripsi = ?")
            nilai.append(deskripsi)
        if tanggal_jatuh_tempo is not None:
            pembaruan.append("tanggal_jatuh_tempo = ?")
            nilai.append(tanggal_jatuh_tempo)
        if status_pembayaran is not None:
            pembaruan.append("status_pembayaran = ?")
            nilai.append(status_pembayaran)

        if not pembaruan:
            return False

        query = f"UPDATE tagihan SET {', '.join(pembaruan)} WHERE id = ?"
        nilai.append(tagihan_id)

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, nilai)
        conn.commit()
        conn.close()
        return True

    def hapus_tagihan(self, tagihan_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tagihan WHERE id = ?", (tagihan_id,))
        conn.commit()
        conn.close()

    def dapatkan_tagihan(self, tagihan_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tagihan WHERE id = ?", (tagihan_id,))
        hasil = cursor.fetchone()
        conn.close()
        return hasil

    def dapatkan_tagihan_pelanggan(self, pelanggan_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tagihan WHERE pelanggan_id = ? ORDER BY tanggal_jatuh_tempo", (pelanggan_id,))
        hasil = cursor.fetchall()
        conn.close()
        return hasil

    def dapatkan_semua_tagihan(self, user_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id is not None:
            # Dapatkan semua tagihan untuk pelanggan yang dimiliki user
            cursor.execute("""
                SELECT t.*, p.nama as pelanggan_nama 
                FROM tagihan t 
                JOIN pelanggan p ON t.pelanggan_id = p.id 
                WHERE p.user_id = ? 
                ORDER BY t.tanggal_jatuh_tempo
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT t.*, p.nama as pelanggan_nama 
                FROM tagihan t 
                JOIN pelanggan p ON t.pelanggan_id = p.id 
                ORDER BY t.tanggal_jatuh_tempo
            """)
            
        hasil = cursor.fetchall()
        conn.close()
        return hasil
        
    def dapatkan_tagihan_jatuh_tempo_hari_ini(self, user_id=None):
        """Dapatkan tagihan yang jatuh tempo hari ini"""
        tanggal_hari_ini = datetime.datetime.now().strftime("%Y-%m-%d")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id is not None:
            # Dapatkan tagihan jatuh tempo hari ini untuk pelanggan yang dimiliki user
            cursor.execute("""
                SELECT t.*, p.nama as pelanggan_nama 
                FROM tagihan t 
                JOIN pelanggan p ON t.pelanggan_id = p.id 
                WHERE p.user_id = ? AND t.tanggal_jatuh_tempo = ? AND t.status_pembayaran = 'BELUM DIBAYAR'
                ORDER BY p.nama
            """, (user_id, tanggal_hari_ini))
        else:
            cursor.execute("""
                SELECT t.*, p.nama as pelanggan_nama 
                FROM tagihan t 
                JOIN pelanggan p ON t.pelanggan_id = p.id 
                WHERE t.tanggal_jatuh_tempo = ? AND t.status_pembayaran = 'BELUM DIBAYAR'
                ORDER BY p.nama
            """, (tanggal_hari_ini,))
            
        hasil = cursor.fetchall()
        conn.close()
        return hasil
        
    def dapatkan_tagihan_terlambat(self, user_id=None):
        """Dapatkan tagihan yang sudah terlambat (jatuh tempo sebelum hari ini)"""
        tanggal_hari_ini = datetime.datetime.now().strftime("%Y-%m-%d")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id is not None:
            # Dapatkan tagihan terlambat untuk pelanggan yang dimiliki user
            cursor.execute("""
                SELECT t.*, p.nama as pelanggan_nama,
                       julianday(?) - julianday(t.tanggal_jatuh_tempo) AS hari_terlambat
                FROM tagihan t 
                JOIN pelanggan p ON t.pelanggan_id = p.id 
                WHERE p.user_id = ? AND t.tanggal_jatuh_tempo < ? AND t.status_pembayaran = 'BELUM DIBAYAR'
                ORDER BY t.tanggal_jatuh_tempo ASC
            """, (tanggal_hari_ini, user_id, tanggal_hari_ini))
        else:
            cursor.execute("""
                SELECT t.*, p.nama as pelanggan_nama,
                       julianday(?) - julianday(t.tanggal_jatuh_tempo) AS hari_terlambat
                FROM tagihan t 
                JOIN pelanggan p ON t.pelanggan_id = p.id 
                WHERE t.tanggal_jatuh_tempo < ? AND t.status_pembayaran = 'BELUM DIBAYAR'
                ORDER BY t.tanggal_jatuh_tempo ASC
            """, (tanggal_hari_ini, tanggal_hari_ini))
            
        hasil = cursor.fetchall()
        conn.close()
        return hasil

    def dapatkan_statistik_tagihan(self, user_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query_params = []
        where_clause = ""
        
        if user_id is not None:
            where_clause = "WHERE p.user_id = ?"
            query_params.append(user_id)
            
        # Hitung jumlah dan total tagihan berdasarkan status
        cursor.execute(f"""
            SELECT 
                t.status_pembayaran, 
                COUNT(t.id) as jumlah_tagihan, 
                SUM(t.jumlah) as total_jumlah
            FROM tagihan t
            JOIN pelanggan p ON t.pelanggan_id = p.id
            {where_clause}
            GROUP BY t.status_pembayaran
        """, query_params)
        
        results = cursor.fetchall()
        conn.close()
        
        # Format hasil
        stats = {
            'BELUM DIBAYAR': {'jumlah': 0, 'total': 0},
            'DIBAYAR': {'jumlah': 0, 'total': 0}
        }
        
        for row in results:
            status = row[0]
            jumlah_tagihan = row[1]
            total_jumlah = row[2] if row[2] is not None else 0
            
            stats[status] = {
                'jumlah': jumlah_tagihan,
                'total': total_jumlah
            }
            
        return stats
        
    # Fungsi Akuntansi
    def tambah_transaksi_akuntansi(self, jenis, jumlah, deskripsi="", tanggal=None, created_by=None):
        """
        Tambahkan transaksi akuntansi baru
        Jenis: 'MODAL_AWAL', 'PENGELUARAN', 'PENDAPATAN', 'LAINNYA'
        """
        if tanggal is None:
            tanggal = datetime.datetime.now().strftime("%Y-%m-%d")
            
        dibuat_pada = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO akuntansi (jenis, jumlah, deskripsi, tanggal, created_by, dibuat_pada)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (jenis, jumlah, deskripsi, tanggal, created_by, dibuat_pada))
        conn.commit()
        lastrowid = cursor.lastrowid
        conn.close()
        return lastrowid
        
    def perbarui_transaksi_akuntansi(self, transaksi_id, jenis=None, jumlah=None, deskripsi=None, tanggal=None):
        pembaruan = []
        nilai = []

        if jenis is not None:
            pembaruan.append("jenis = ?")
            nilai.append(jenis)
        if jumlah is not None:
            pembaruan.append("jumlah = ?")
            nilai.append(jumlah)
        if deskripsi is not None:
            pembaruan.append("deskripsi = ?")
            nilai.append(deskripsi)
        if tanggal is not None:
            pembaruan.append("tanggal = ?")
            nilai.append(tanggal)

        if not pembaruan:
            return False

        query = f"UPDATE akuntansi SET {', '.join(pembaruan)} WHERE id = ?"
        nilai.append(transaksi_id)

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, nilai)
        conn.commit()
        conn.close()
        return True
        
    def hapus_transaksi_akuntansi(self, transaksi_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM akuntansi WHERE id = ?", (transaksi_id,))
        conn.commit()
        conn.close()
        
    def dapatkan_transaksi_akuntansi(self, transaksi_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM akuntansi WHERE id = ?", (transaksi_id,))
        hasil = cursor.fetchone()
        conn.close()
        return hasil
        
    def dapatkan_semua_transaksi_akuntansi(self, jenis=None, tanggal_mulai=None, tanggal_akhir=None, user_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        params = []
        where_clauses = []
        
        if jenis is not None:
            where_clauses.append("jenis = ?")
            params.append(jenis)
            
        if tanggal_mulai is not None:
            where_clauses.append("tanggal >= ?")
            params.append(tanggal_mulai)
            
        if tanggal_akhir is not None:
            where_clauses.append("tanggal <= ?")
            params.append(tanggal_akhir)
            
        if user_id is not None:
            where_clauses.append("created_by = ?")
            params.append(user_id)
            
        query = "SELECT * FROM akuntansi"
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " ORDER BY tanggal DESC, dibuat_pada DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
        
    def dapatkan_ringkasan_akuntansi(self, bulan=None, tahun=None):
        """
        Dapatkan ringkasan akuntansi untuk bulan dan tahun tertentu
        Jika bulan dan tahun tidak disediakan, berikan ringkasan untuk tahun ini
        """
        now = datetime.datetime.now()
        
        if bulan is None:
            bulan = now.month
            
        if tahun is None:
            tahun = now.year
            
        # Format tanggal untuk query
        tanggal_mulai = f"{tahun}-{bulan:02d}-01"
        
        # Hitung tanggal akhir (bulan + 1)
        if bulan == 12:
            tanggal_akhir = f"{tahun+1}-01-01"
        else:
            tanggal_akhir = f"{tahun}-{bulan+1:02d}-01"
            
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Dapatkan semua transaksi dalam rentang waktu
        cursor.execute("""
            SELECT jenis, SUM(jumlah) as total
            FROM akuntansi
            WHERE tanggal >= ? AND tanggal < ?
            GROUP BY jenis
        """, (tanggal_mulai, tanggal_akhir))
        
        result = cursor.fetchall()
        
        # Dapatkan total tagihan dibayar dalam bulan ini
        cursor.execute("""
            SELECT SUM(jumlah) as total
            FROM tagihan
            WHERE status_pembayaran = 'DIBAYAR'
            AND substr(dibuat_pada, 1, 7) = ?
        """, (f"{tahun}-{bulan:02d}",))
        
        pendapatan_tagihan = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Format hasil
        ringkasan = {
            'modal_awal': 0,
            'pengeluaran': 0,
            'pendapatan': 0,
            'lainnya': 0,
            'pendapatan_tagihan': pendapatan_tagihan
        }
        
        # Map dari jenis di database ke kunci di ringkasan
        jenis_map = {
            'MODAL_AWAL': 'modal_awal',
            'PENGELUARAN': 'pengeluaran',
            'PENDAPATAN': 'pendapatan',
            'LAINNYA': 'lainnya'
        }
        
        for row in result:
            jenis = row[0]
            total = row[1] or 0
            if jenis in jenis_map:
                ringkasan[jenis_map[jenis]] = total
            
        # Hitung total pendapatan dari pendapatan langsung dan tagihan
        total_pendapatan = ringkasan['pendapatan'] + ringkasan['pendapatan_tagihan']
        
        # Hitung laba kotor dan bersih
        laba_kotor = total_pendapatan
        laba_bersih = total_pendapatan - ringkasan['pengeluaran']
        
        # Tambahkan ke ringkasan
        ringkasan['pendapatan_kotor'] = pendapatan_kotor
        ringkasan['pendapatan_bersih'] = pendapatan_bersih
        ringkasan['laba_kotor'] = laba_kotor
        ringkasan['laba_bersih'] = laba_bersih
        
        # Tambahkan rasio keuangan
        if ringkasan['modal_awal'] > 0:
            ringkasan['rasio_pendapatan_modal'] = pendapatan_kotor / ringkasan['modal_awal']
        else:
            ringkasan['rasio_pendapatan_modal'] = 0
            
        if pendapatan_kotor > 0:
            ringkasan['rasio_pengeluaran_pendapatan'] = ringkasan['pengeluaran'] / pendapatan_kotor
            ringkasan['margin_laba'] = laba_bersih / pendapatan_kotor
        else:
            ringkasan['rasio_pengeluaran_pendapatan'] = 0
            ringkasan['margin_laba'] = 0
        
        return ringkasan

# Inisialisasi objek
pengguna_manager = Pengguna()
sistem_manajemen = SistemManajemenPelanggan()

# Middleware untuk memeriksa login
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Anda perlu login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Middleware untuk memeriksa admin
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Anda perlu login terlebih dahulu.', 'warning')
            return redirect(url_for('login'))
        if session['user'].get('level') != 'admin':
            flash('Anda tidak memiliki hak akses ke halaman ini.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not username or not password:
            flash('Username dan password harus diisi', 'danger')
            return render_template('login.html')
        
        success, result = pengguna_manager.login(username, password)
        
        if success:
            session['user'] = result
            if remember_me:
                session.permanent = True
            
            flash(f'Selamat datang, {result["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result, 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Anda telah keluar dari sistem', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        nama_lengkap = request.form.get('nama_lengkap', '')
        email = request.form.get('email', '')
        
        # Validasi form
        if not username or not password:
            flash('Username dan password harus diisi', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Password dan konfirmasi password tidak sama', 'danger')
            return render_template('register.html')
        
        # Check if admin already exists, if not, make this user admin
        all_users = pengguna_manager.get_all_users()
        level = "user"
        if not all_users:
            level = "admin"
        
        success, message = pengguna_manager.register(username, password, nama_lengkap, email, level)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'danger')
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user']['id']
    is_admin = session['user']['level'] == 'admin'
    
    # Get statistics
    if is_admin:
        pelanggan_count = len(sistem_manajemen.dapatkan_semua_pelanggan())
        users_count = len(pengguna_manager.get_all_users())
        tagihan_stats = sistem_manajemen.dapatkan_statistik_tagihan()
        tagihan_jatuh_tempo = sistem_manajemen.dapatkan_tagihan_jatuh_tempo_hari_ini()
        tagihan_terlambat = sistem_manajemen.dapatkan_tagihan_terlambat()
    else:
        pelanggan_count = len(sistem_manajemen.dapatkan_semua_pelanggan(user_id))
        users_count = 1  # Just current user
        tagihan_stats = sistem_manajemen.dapatkan_statistik_tagihan(user_id)
        tagihan_jatuh_tempo = sistem_manajemen.dapatkan_tagihan_jatuh_tempo_hari_ini(user_id)
        tagihan_terlambat = sistem_manajemen.dapatkan_tagihan_terlambat(user_id)
    
    # Convert tuples to dictionaries
    if tagihan_jatuh_tempo:
        tagihan_jatuh_tempo = [{
            'id': t[0],
            'pelanggan_id': t[1],
            'jumlah': t[2],
            'deskripsi': t[3],
            'tanggal_jatuh_tempo': t[4],
            'status_pembayaran': t[5],
            'dibuat_pada': t[6],
            'pelanggan_nama': t.pelanggan_nama if hasattr(t, 'pelanggan_nama') else ''
        } for t in tagihan_jatuh_tempo]
    
    if tagihan_terlambat:
        tagihan_terlambat = [{
            'id': t[0],
            'pelanggan_id': t[1],
            'jumlah': t[2],
            'deskripsi': t[3],
            'tanggal_jatuh_tempo': t[4],
            'status_pembayaran': t[5],
            'dibuat_pada': t[6],
            'pelanggan_nama': t.pelanggan_nama if hasattr(t, 'pelanggan_nama') else '',
            'hari_terlambat': t.hari_terlambat if hasattr(t, 'hari_terlambat') else 0
        } for t in tagihan_terlambat]
    
    return render_template(
        'dashboard.html',
        pelanggan_count=pelanggan_count,
        users_count=users_count,
        tagihan_stats=tagihan_stats,
        tagihan_jatuh_tempo=tagihan_jatuh_tempo,
        tagihan_terlambat=tagihan_terlambat,
        is_admin=is_admin
    )

@app.route('/users')
@admin_required
def user_list():
    users = pengguna_manager.get_all_users()
    return render_template('user_management.html', users=users)

@app.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    nama_lengkap = request.form.get('nama_lengkap', '')
    email = request.form.get('email', '')
    level = request.form.get('level', 'user')
    
    if not username or not password:
        flash('Username dan password harus diisi', 'danger')
        return redirect(url_for('user_list'))
    
    success, message = pengguna_manager.register(username, password, nama_lengkap, email, level)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('user_list'))

@app.route('/users/edit/<int:user_id>', methods=['POST'])
@admin_required
def edit_user(user_id):
    nama_lengkap = request.form.get('nama_lengkap')
    email = request.form.get('email')
    level = request.form.get('level')
    password = request.form.get('password')
    
    # Jika password kosong, jangan update password
    if password == '':
        password = None
    
    success, message = pengguna_manager.update_user(user_id, nama_lengkap, email, level, password)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('user_list'))

@app.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    # Jangan izinkan menghapus diri sendiri
    if user_id == session['user']['id']:
        flash('Anda tidak dapat menghapus akun Anda sendiri.', 'danger')
        return redirect(url_for('user_list'))
    
    success, message = pengguna_manager.delete_user(user_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('user_list'))

@app.route('/profile')
@login_required
def profile():
    user_id = session['user']['id']
    user_data = pengguna_manager.get_user(user_id)
    return render_template('profile.html', user=user_data)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user_id = session['user']['id']
    nama_lengkap = request.form.get('nama_lengkap')
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Jika password kosong, jangan update password
    if password == '':
        password = None
    
    success, message = pengguna_manager.update_user(user_id, nama_lengkap, email, None, password)
    
    if success:
        # Update session data jika nama berubah
        if nama_lengkap:
            session['user']['nama_lengkap'] = nama_lengkap
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('profile'))

@app.route('/pelanggan')
@login_required
def pelanggan_list():
    user_id = session['user']['id']
    is_admin = session['user']['level'] == 'admin'
    
    if is_admin:
        # Admin dapat melihat semua pelanggan
        pelanggan = sistem_manajemen.dapatkan_semua_pelanggan()
    else:
        # User biasa hanya melihat pelanggan yang terkait dengan mereka
        pelanggan = sistem_manajemen.dapatkan_semua_pelanggan(user_id)
    
    return render_template('pelanggan_list.html', pelanggan=pelanggan)

@app.route('/pelanggan/tambah', methods=['GET', 'POST'])
@login_required
def tambah_pelanggan():
    if request.method == 'POST':
        nama = request.form.get('nama')
        telepon = request.form.get('telepon', '')
        email = request.form.get('email', '')
        alamat = request.form.get('alamat', '')
        latitude = request.form.get('latitude', 0)
        longitude = request.form.get('longitude', 0)
        
        if not nama:
            flash('Nama pelanggan harus diisi', 'danger')
            return render_template('pelanggan_form.html', mode='tambah')
        
        try:
            lat = float(latitude) if latitude else 0.0
            lng = float(longitude) if longitude else 0.0
        except ValueError:
            lat, lng = 0.0, 0.0
        
        user_id = session['user']['id']
        pelanggan_id = sistem_manajemen.tambah_pelanggan(nama, telepon, email, alamat, lat, lng, user_id)
        
        if pelanggan_id:
            flash('Pelanggan berhasil ditambahkan', 'success')
            return redirect(url_for('pelanggan_list'))
        else:
            flash('Gagal menambahkan pelanggan', 'danger')
    
    return render_template('pelanggan_form.html', mode='tambah')

@app.route('/pelanggan/edit/<int:pelanggan_id>', methods=['GET', 'POST'])
@login_required
def edit_pelanggan(pelanggan_id):
    pelanggan = sistem_manajemen.dapatkan_pelanggan(pelanggan_id)
    
    if not pelanggan:
        flash('Pelanggan tidak ditemukan', 'danger')
        return redirect(url_for('pelanggan_list'))
    
    # Pemeriksaan akses: Admin atau pemilik pelanggan
    if session['user']['level'] != 'admin' and pelanggan[8] != session['user']['id']:
        flash('Anda tidak memiliki akses untuk mengedit pelanggan ini', 'danger')
        return redirect(url_for('pelanggan_list'))
    
    if request.method == 'POST':
        nama = request.form.get('nama')
        telepon = request.form.get('telepon', '')
        email = request.form.get('email', '')
        alamat = request.form.get('alamat', '')
        latitude = request.form.get('latitude', 0)
        longitude = request.form.get('longitude', 0)
        
        if not nama:
            flash('Nama pelanggan harus diisi', 'danger')
            return render_template('pelanggan_form.html', pelanggan=pelanggan, mode='edit')
        
        try:
            lat = float(latitude) if latitude else 0.0
            lng = float(longitude) if longitude else 0.0
        except ValueError:
            lat, lng = 0.0, 0.0
        
        berhasil = sistem_manajemen.perbarui_pelanggan(pelanggan_id, nama, telepon, email, alamat, lat, lng)
        
        if berhasil:
            flash('Data pelanggan berhasil diperbarui', 'success')
            return redirect(url_for('pelanggan_list'))
        else:
            flash('Gagal memperbarui data pelanggan', 'danger')
    
    # Convert DB row to dict for template
    pelanggan_dict = {
        'id': pelanggan[0],
        'nama': pelanggan[1],
        'telepon': pelanggan[2],
        'email': pelanggan[3],
        'alamat': pelanggan[4],
        'latitude': pelanggan[5],
        'longitude': pelanggan[6]
    }
    
    return render_template('pelanggan_form.html', pelanggan=pelanggan_dict, mode='edit')

@app.route('/pelanggan/hapus/<int:pelanggan_id>', methods=['POST'])
@login_required
def hapus_pelanggan(pelanggan_id):
    pelanggan = sistem_manajemen.dapatkan_pelanggan(pelanggan_id)
    
    if not pelanggan:
        flash('Pelanggan tidak ditemukan', 'danger')
        return redirect(url_for('pelanggan_list'))
    
    # Pemeriksaan akses: Admin atau pemilik pelanggan
    if session['user']['level'] != 'admin' and pelanggan[8] != session['user']['id']:
        flash('Anda tidak memiliki akses untuk menghapus pelanggan ini', 'danger')
        return redirect(url_for('pelanggan_list'))
    
    sistem_manajemen.hapus_pelanggan(pelanggan_id)
    flash('Pelanggan berhasil dihapus', 'success')
    return redirect(url_for('pelanggan_list'))

@app.route('/pelanggan/<int:pelanggan_id>')
@login_required
def detail_pelanggan(pelanggan_id):
    pelanggan = sistem_manajemen.dapatkan_pelanggan(pelanggan_id)
    
    if not pelanggan:
        flash('Pelanggan tidak ditemukan', 'danger')
        return redirect(url_for('pelanggan_list'))
    
    # Pemeriksaan akses: Admin atau pemilik pelanggan
    if session['user']['level'] != 'admin' and pelanggan[8] != session['user']['id']:
        flash('Anda tidak memiliki akses untuk melihat pelanggan ini', 'danger')
        return redirect(url_for('pelanggan_list'))
    
    tagihan = sistem_manajemen.dapatkan_tagihan_pelanggan(pelanggan_id)
    
    # Convert DB row to dict for template
    pelanggan_dict = {
        'id': pelanggan[0],
        'nama': pelanggan[1],
        'telepon': pelanggan[2],
        'email': pelanggan[3],
        'alamat': pelanggan[4],
        'latitude': pelanggan[5],
        'longitude': pelanggan[6],
        'dibuat_pada': pelanggan[7],
        'user_id': pelanggan[8]
    }
    
    return render_template('pelanggan_detail.html', 
                          pelanggan=pelanggan_dict, 
                          tagihan=tagihan)

@app.route('/tagihan')
@login_required
def tagihan_list():
    user_id = session['user']['id']
    is_admin = session['user']['level'] == 'admin'
    
    if is_admin:
        tagihan = sistem_manajemen.dapatkan_semua_tagihan()
    else:
        tagihan = sistem_manajemen.dapatkan_semua_tagihan(user_id)
    
    return render_template('tagihan_list.html', tagihan=tagihan)

@app.route('/tagihan/tambah', methods=['GET', 'POST'])
@login_required
def tambah_tagihan():
    user_id = session['user']['id']
    is_admin = session['user']['level'] == 'admin'
    
    # Dapatkan daftar pelanggan untuk dropdown
    if is_admin:
        pelanggan_list = sistem_manajemen.dapatkan_semua_pelanggan()
    else:
        pelanggan_list = sistem_manajemen.dapatkan_semua_pelanggan(user_id)
    
    if request.method == 'POST':
        pelanggan_id = request.form.get('pelanggan_id')
        jumlah = request.form.get('jumlah')
        deskripsi = request.form.get('deskripsi', '')
        tanggal_jatuh_tempo = request.form.get('tanggal_jatuh_tempo')
        
        if not pelanggan_id or not jumlah:
            flash('Pelanggan dan jumlah tagihan harus diisi', 'danger')
            return render_template('tagihan_form.html', 
                                  pelanggan_list=pelanggan_list, 
                                  mode='tambah')
        
        try:
            jumlah_float = float(jumlah)
        except ValueError:
            flash('Jumlah tagihan harus berupa angka', 'danger')
            return render_template('tagihan_form.html', 
                                  pelanggan_list=pelanggan_list, 
                                  mode='tambah')
        
        # Pastikan pelanggan milik user (kecuali admin)
        if not is_admin:
            pelanggan = sistem_manajemen.dapatkan_pelanggan(int(pelanggan_id))
            if not pelanggan or pelanggan[8] != user_id:
                flash('Anda tidak memiliki akses ke pelanggan ini', 'danger')
                return redirect(url_for('tagihan_list'))
        
        tagihan_id = sistem_manajemen.tambah_tagihan(
            int(pelanggan_id), jumlah_float, deskripsi, tanggal_jatuh_tempo
        )
        
        if tagihan_id:
            flash('Tagihan berhasil ditambahkan', 'success')
            return redirect(url_for('tagihan_list'))
        else:
            flash('Gagal menambahkan tagihan', 'danger')
    
    return render_template('tagihan_form.html', 
                          pelanggan_list=pelanggan_list, 
                          mode='tambah')

@app.route('/tagihan/edit/<int:tagihan_id>', methods=['GET', 'POST'])
@login_required
def edit_tagihan(tagihan_id):
    user_id = session['user']['id']
    is_admin = session['user']['level'] == 'admin'
    
    tagihan = sistem_manajemen.dapatkan_tagihan(tagihan_id)
    
    if not tagihan:
        flash('Tagihan tidak ditemukan', 'danger')
        return redirect(url_for('tagihan_list'))
    
    # Dapatkan pelanggan untuk pemeriksaan akses
    pelanggan_id = tagihan[1]
    pelanggan = sistem_manajemen.dapatkan_pelanggan(pelanggan_id)
    
    # Pemeriksaan akses: Admin atau pemilik pelanggan
    if not is_admin and pelanggan[8] != user_id:
        flash('Anda tidak memiliki akses untuk mengedit tagihan ini', 'danger')
        return redirect(url_for('tagihan_list'))
    
    # Dapatkan daftar pelanggan untuk dropdown
    if is_admin:
        pelanggan_list = sistem_manajemen.dapatkan_semua_pelanggan()
    else:
        pelanggan_list = sistem_manajemen.dapatkan_semua_pelanggan(user_id)
    
    if request.method == 'POST':
        jumlah = request.form.get('jumlah')
        deskripsi = request.form.get('deskripsi', '')
        tanggal_jatuh_tempo = request.form.get('tanggal_jatuh_tempo')
        status_pembayaran = request.form.get('status_pembayaran')
        
        if not jumlah:
            flash('Jumlah tagihan harus diisi', 'danger')
            return render_template('tagihan_form.html', 
                               tagihan=tagihan, 
                               pelanggan_list=pelanggan_list, 
                               pelanggan_terpilih=pelanggan,
                               mode='edit')
        
        try:
            jumlah_float = float(jumlah)
        except ValueError:
            flash('Jumlah tagihan harus berupa angka', 'danger')
            return render_template('tagihan_form.html', 
                               tagihan=tagihan, 
                               pelanggan_list=pelanggan_list, 
                               pelanggan_terpilih=pelanggan,
                               mode='edit')
        
        berhasil = sistem_manajemen.perbarui_tagihan(
            tagihan_id, jumlah_float, deskripsi, tanggal_jatuh_tempo, status_pembayaran
        )
        
        if berhasil:
            flash('Tagihan berhasil diperbarui', 'success')
            return redirect(url_for('tagihan_list'))
        else:
            flash('Gagal memperbarui tagihan', 'danger')
    
    # Convert DB row to dict for template
    tagihan_dict = {
        'id': tagihan[0],
        'pelanggan_id': tagihan[1],
        'jumlah': tagihan[2],
        'deskripsi': tagihan[3],
        'tanggal_jatuh_tempo': tagihan[4],
        'status_pembayaran': tagihan[5],
        'dibuat_pada': tagihan[6]
    }
    
    return render_template('tagihan_form.html', 
                          tagihan=tagihan_dict, 
                          pelanggan_list=pelanggan_list, 
                          pelanggan_terpilih=pelanggan,
                          mode='edit')

@app.route('/tagihan/hapus/<int:tagihan_id>', methods=['POST'])
@login_required
def hapus_tagihan(tagihan_id):
    user_id = session['user']['id']
    is_admin = session['user']['level'] == 'admin'
    
    tagihan = sistem_manajemen.dapatkan_tagihan(tagihan_id)
    
    if not tagihan:
        flash('Tagihan tidak ditemukan', 'danger')
        return redirect(url_for('tagihan_list'))
    
    # Dapatkan pelanggan untuk pemeriksaan akses
    pelanggan_id = tagihan[1]
    pelanggan = sistem_manajemen.dapatkan_pelanggan(pelanggan_id)
    
    # Pemeriksaan akses: Admin atau pemilik pelanggan
    if not is_admin and pelanggan[8] != user_id:
        flash('Anda tidak memiliki akses untuk menghapus tagihan ini', 'danger')
        return redirect(url_for('tagihan_list'))
    
    sistem_manajemen.hapus_tagihan(tagihan_id)
    flash('Tagihan berhasil dihapus', 'success')
    return redirect(url_for('tagihan_list'))

@app.route('/api/set-status/<int:tagihan_id>', methods=['POST'])
@login_required
def set_status_tagihan(tagihan_id):
    status = request.json.get('status')
    
    if not status:
        return jsonify({'success': False, 'message': 'Status tidak valid'}), 400
    
    # Validasi status
    if status not in ['BELUM DIBAYAR', 'DIBAYAR']:
        return jsonify({'success': False, 'message': 'Status tidak valid'}), 400
    
    user_id = session['user']['id']
    is_admin = session['user']['level'] == 'admin'
    
    tagihan = sistem_manajemen.dapatkan_tagihan(tagihan_id)
    
    if not tagihan:
        return jsonify({'success': False, 'message': 'Tagihan tidak ditemukan'}), 404
    
    # Dapatkan pelanggan untuk pemeriksaan akses
    pelanggan_id = tagihan[1]
    pelanggan = sistem_manajemen.dapatkan_pelanggan(pelanggan_id)
    
    # Pemeriksaan akses: Admin atau pemilik pelanggan
    if not is_admin and pelanggan[8] != user_id:
        return jsonify({'success': False, 'message': 'Tidak memiliki akses ke tagihan ini'}), 403
    
    berhasil = sistem_manajemen.perbarui_tagihan(tagihan_id, status_pembayaran=status)
    
    # Jika status DIBAYAR, tambahkan transaksi pendapatan
    if berhasil and status == 'DIBAYAR':
        # Dapatkan informasi tagihan untuk deskripsi transaksi
        pelanggan = sistem_manajemen.dapatkan_pelanggan(pelanggan_id)
        pelanggan_nama = pelanggan[1] if pelanggan else "Pelanggan"
        
        # Tambahkan transaksi pendapatan ke akuntansi
        deskripsi_transaksi = f"Pembayaran tagihan dari {pelanggan_nama}"
        jumlah_tagihan = tagihan[2]  # Jumlah tagihan
        tanggal_sekarang = datetime.datetime.now().strftime("%Y-%m-%d")
        
        sistem_manajemen.tambah_transaksi_akuntansi(
            jenis="PENDAPATAN", 
            jumlah=jumlah_tagihan, 
            deskripsi=deskripsi_transaksi, 
            tanggal=tanggal_sekarang, 
            created_by=user_id
        )
    
    if berhasil:
        return jsonify({'success': True, 'message': 'Status berhasil diperbarui'})
    else:
        return jsonify({'success': False, 'message': 'Gagal memperbarui status'}), 500

# Fitur Akuntansi
@app.route('/akuntansi')
@login_required
@admin_required
def akuntansi():
    """Halaman manajemen akuntansi"""
    bulan = request.args.get('bulan', type=int)
    tahun = request.args.get('tahun', type=int)
    
    now = datetime.datetime.now()
    if not bulan:
        bulan = now.month
    if not tahun:
        tahun = now.year
    
    # Dapatkan ringkasan akuntansi untuk bulan dan tahun yang dipilih
    ringkasan = sistem_manajemen.dapatkan_ringkasan_akuntansi(bulan, tahun)
    
    # Dapatkan semua transaksi untuk bulan dan tahun yang dipilih
    tanggal_mulai = f"{tahun}-{bulan:02d}-01"
    
    # Hitung tanggal akhir (bulan + 1)
    if bulan == 12:
        tanggal_akhir = f"{tahun+1}-01-01"
    else:
        tanggal_akhir = f"{tahun}-{bulan+1:02d}-01"
        
    transaksi = sistem_manajemen.dapatkan_semua_transaksi_akuntansi(
        tanggal_mulai=tanggal_mulai,
        tanggal_akhir=tanggal_akhir
    )
    
    # Data untuk dropdown bulan dan tahun
    months = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), 
        (4, 'April'), (5, 'Mei'), (6, 'Juni'),
        (7, 'Juli'), (8, 'Agustus'), (9, 'September'),
        (10, 'Oktober'), (11, 'November'), (12, 'Desember')
    ]
    years = range(2020, now.year + 2)
    
    return render_template(
        'akuntansi.html',
        ringkasan=ringkasan,
        transaksi=transaksi,
        bulan_selected=bulan,
        tahun_selected=tahun,
        months=months,
        years=years,
        month_name=dict(months)[bulan]
    )

@app.route('/akuntansi/tambah', methods=['POST'])
@login_required
@admin_required
def tambah_transaksi():
    """Tambah transaksi akuntansi baru"""
    jenis = request.form.get('jenis')
    jumlah = request.form.get('jumlah')  # Ambil sebagai string dulu
    deskripsi = request.form.get('deskripsi', '')
    tanggal = request.form.get('tanggal')
    
    if not jenis or not jumlah or not tanggal:
        flash('Semua isian harus diisi dengan benar', 'danger')
        return redirect(url_for('akuntansi'))
    
    # Bersihkan input jumlah dari format mata uang
    try:
        # Hapus titik sebagai pemisah ribuan dan ganti koma dengan titik untuk desimal
        jumlah_clean = jumlah.replace('.', '').replace(',', '.')
        jumlah_float = float(jumlah_clean)
    except (ValueError, AttributeError):
        flash('Nilai jumlah tidak valid', 'danger')
        return redirect(url_for('akuntansi'))
    
    user_id = session['user']['id']
    transaksi_id = sistem_manajemen.tambah_transaksi_akuntansi(
        jenis, jumlah_float, deskripsi, tanggal, user_id
    )
    
    if transaksi_id:
        flash('Transaksi berhasil ditambahkan', 'success')
    else:
        flash('Gagal menambahkan transaksi', 'danger')
    
    # Parse bulan dan tahun dari tanggal untuk redirect
    tanggal_parts = tanggal.split('-')
    if len(tanggal_parts) == 3:
        tahun, bulan = int(tanggal_parts[0]), int(tanggal_parts[1])
        return redirect(url_for('akuntansi', bulan=bulan, tahun=tahun))
    
    return redirect(url_for('akuntansi'))

@app.route('/akuntansi/edit/<int:transaksi_id>', methods=['POST'])
@login_required
@admin_required
def edit_transaksi(transaksi_id):
    """Edit transaksi akuntansi"""
    jenis = request.form.get('jenis')
    jumlah = request.form.get('jumlah')  # Ambil sebagai string dulu
    deskripsi = request.form.get('deskripsi', '')
    tanggal = request.form.get('tanggal')
    
    if not jenis or not jumlah or not tanggal:
        flash('Semua isian harus diisi dengan benar', 'danger')
        return redirect(url_for('akuntansi'))
    
    # Bersihkan input jumlah dari format mata uang
    try:
        # Hapus titik sebagai pemisah ribuan dan ganti koma dengan titik untuk desimal
        jumlah_clean = jumlah.replace('.', '').replace(',', '.')
        jumlah_float = float(jumlah_clean)
    except (ValueError, AttributeError):
        flash('Nilai jumlah tidak valid', 'danger')
        return redirect(url_for('akuntansi'))
    
    success = sistem_manajemen.perbarui_transaksi_akuntansi(
        transaksi_id, jenis, jumlah_float, deskripsi, tanggal
    )
    
    if success:
        flash('Transaksi berhasil diperbarui', 'success')
    else:
        flash('Gagal memperbarui transaksi', 'danger')
    
    # Parse bulan dan tahun dari tanggal untuk redirect
    tanggal_parts = tanggal.split('-')
    if len(tanggal_parts) == 3:
        tahun, bulan = int(tanggal_parts[0]), int(tanggal_parts[1])
        return redirect(url_for('akuntansi', bulan=bulan, tahun=tahun))
    
    return redirect(url_for('akuntansi'))

@app.route('/akuntansi/hapus/<int:transaksi_id>', methods=['POST'])
@login_required
@admin_required
def hapus_transaksi(transaksi_id):
    """Hapus transaksi akuntansi"""
    # Dapatkan data transaksi untuk mendapatkan tanggal
    transaksi = sistem_manajemen.dapatkan_transaksi_akuntansi(transaksi_id)
    
    sistem_manajemen.hapus_transaksi_akuntansi(transaksi_id)
    flash('Transaksi berhasil dihapus', 'success')
    
    # Redirect ke bulan dan tahun yang sama
    if transaksi and len(transaksi) >= 4:
        tanggal = transaksi[4]  # Kolom tanggal adalah indeks ke-4
        tanggal_parts = tanggal.split('-')
        if len(tanggal_parts) == 3:
            tahun, bulan = int(tanggal_parts[0]), int(tanggal_parts[1])
            return redirect(url_for('akuntansi', bulan=bulan, tahun=tahun))
    
    return redirect(url_for('akuntansi'))

@app.route('/api/akuntansi/ringkasan', methods=['GET'])
@login_required
@admin_required
def api_ringkasan_akuntansi():
    """API untuk mendapatkan ringkasan akuntansi"""
    bulan = request.args.get('bulan', type=int)
    tahun = request.args.get('tahun', type=int)
    
    now = datetime.datetime.now()
    if not bulan:
        bulan = now.month
    if not tahun:
        tahun = now.year
        
    ringkasan = sistem_manajemen.dapatkan_ringkasan_akuntansi(bulan, tahun)
    
    return jsonify({
        'success': True,
        'data': ringkasan
    })

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="404 - Halaman tidak ditemukan"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error="500 - Kesalahan server internal"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

import os
import sqlite3
import datetime
from datetime import date
import webbrowser
import hashlib
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session

app = Flask(__name__)
app.secret_key = "rahasia_aplikasi_manajemen_pelanggan"
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)

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

    def dapatkan_tagihan_berdasarkan_tanggal(self, tanggal_tertentu):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT t.*, p.nama FROM tagihan t JOIN pelanggan p ON t.pelanggan_id = p.id WHERE t.tanggal_jatuh_tempo = ?", (tanggal_tertentu,))
            hasil = cursor.fetchall()
            return hasil
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def dapatkan_tagihan_hari_ini(self):
        try:
            hari_ini = date.today().strftime("%Y-%m-%d")
            return self.dapatkan_tagihan_berdasarkan_tanggal(hari_ini)
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return []

    def dapatkan_tagihan_belum_dibayar(self):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT t.*, p.nama FROM tagihan t JOIN pelanggan p ON t.pelanggan_id = p.id WHERE t.status_pembayaran = 'BELUM DIBAYAR' ORDER BY t.tanggal_jatuh_tempo")
            hasil = cursor.fetchall()
            return hasil
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def tandai_tagihan_sebagai_dibayar(self, tagihan_id):
        return self.perbarui_tagihan(tagihan_id, status_pembayaran="SUDAH DIBAYAR")

    def buka_lokasi_di_peta(self, pelanggan_id):
        pelanggan = self.dapatkan_pelanggan(pelanggan_id)
        if pelanggan:
            lat, lng = pelanggan[5], pelanggan[6]
            if lat and lng:
                map_url = f"https://www.google.com/maps?q={lat},{lng}"
                webbrowser.open(map_url)
                return True
            else:
                alamat = pelanggan[4]
                if alamat:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={alamat.replace(' ', '+')}"
                    webbrowser.open(map_url)
                    return True
        return False

    def dapatkan_total_tagihan_belum_dibayar(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(jumlah) FROM tagihan WHERE status_pembayaran = 'BELUM DIBAYAR'")
        hasil = cursor.fetchone()[0]
        conn.close()
        return hasil if hasil else 0

    def dapatkan_tagihan_sudah_dibayar(self):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT t.*, p.nama FROM tagihan t JOIN pelanggan p ON t.pelanggan_id = p.id WHERE t.status_pembayaran = 'SUDAH DIBAYAR' ORDER BY t.tanggal_jatuh_tempo DESC")
            hasil = cursor.fetchall()
            return hasil
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def dapatkan_tagihan_30_hari_terakhir(self, status=None):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Tanggal 30 hari yang lalu
            tiga_puluh_hari_lalu = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")

            query = """
                SELECT t.*, p.nama FROM tagihan t 
                JOIN pelanggan p ON t.pelanggan_id = p.id 
                WHERE t.dibuat_pada >= ?
            """

            params = [tiga_puluh_hari_lalu]

            if status:
                query += " AND t.status_pembayaran = ?"
                params.append(status)

            query += " ORDER BY t.dibuat_pada DESC"

            cursor.execute(query, params)
            hasil = cursor.fetchall()
            return hasil
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()

# Inisialisasi sistem manajemen pelanggan dan pengguna
smp = SistemManajemenPelanggan()
user_manager = Pengguna()

# Fungsi untuk menambahkan kolom user_id jika belum ada
def tambah_kolom_user_id():
    conn = sqlite3.connect('manajemen_pelanggan.db')
    cursor = conn.cursor()

    # Cek apakah kolom user_id sudah ada di tabel pelanggan
    cursor.execute("PRAGMA table_info(pelanggan)")
    kolom = cursor.fetchall()
    kolom_names = [col[1] for col in kolom]

    if 'user_id' not in kolom_names:
        try:
            # Tambahkan kolom user_id ke tabel pelanggan
            cursor.execute("ALTER TABLE pelanggan ADD COLUMN user_id INTEGER")
            conn.commit()
            print("Kolom user_id berhasil ditambahkan ke tabel pelanggan")
        except sqlite3.OperationalError as e:
            print(f"Kesalahan saat menambahkan kolom user_id: {e}")

    conn.close()

# Jalankan migrasi
tambah_kolom_user_id()

# Buat admin default jika belum ada admin
def buat_admin_default():
    conn = user_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pengguna WHERE level = 'admin'")
    admin_count = cursor.fetchone()[0]

    if admin_count == 0:
        # Buat admin default dengan username 'admin' dan password 'admin123'
        user_manager.register('admin', 'admin123', 'Administrator', 'admin@contoh.com', 'admin')
        print("Admin default telah dibuat: username 'admin', password 'admin123'")

    conn.close()

# Tambah tabel akuntansi
def buat_tabel_akuntansi():
    conn = sqlite3.connect('manajemen_pelanggan.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS akuntansi (
        id INTEGER PRIMARY KEY,
        tanggal TEXT NOT NULL,
        jenis TEXT NOT NULL,
        keterangan TEXT,
        jumlah REAL NOT NULL,
        kategori TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

buat_admin_default()
buat_tabel_akuntansi()

# Buat direktori templates jika belum ada
os.makedirs('templates', exist_ok=True)

@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('index.html', user=session)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        login_type = request.form.get('login_type', 'user')

        success, result = user_manager.login(username, password)

        if success:
            # Jika login sebagai admin tapi user bukan admin
            if login_type == 'admin' and result['level'] != 'admin':
                flash('Anda tidak memiliki akses sebagai admin', 'danger')
                return render_template('login.html')

            # Jika login sebagai user tapi user adalah admin, tetap diizinkan

            # Simpan info pengguna di session
            session['user_id'] = result['id']
            session['username'] = result['username']
            session['nama_lengkap'] = result['nama_lengkap']
            session['level'] = result['level']
            session.permanent = True

            flash(f'Login berhasil sebagai {result["level"]}!', 'success')

            # Redirect admin ke halaman user management
            if result['level'] == 'admin' and login_type == 'admin':
                return redirect(url_for('daftar_user'))
            else:
                return redirect(url_for('index'))
        else:
            flash(result, 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Hapus semua data session
    session.clear()
    flash('Anda telah keluar dari sistem', 'info')
    return redirect(url_for('login'))

@app.route('/daftar', methods=['GET', 'POST'])
def daftar():
    # Hitung total user dan admin
    conn = user_manager.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pengguna")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pengguna WHERE level = 'admin'")
    total_admins = cursor.fetchone()[0]
    total_regular_users = total_users - total_admins
    conn.close()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        nama_lengkap = request.form.get('nama_lengkap')
        email = request.form.get('email')
        level = request.form.get('level', 'user')  # Default ke 'user' jika tidak ada level

        # Validasi
        if not username or not password:
            flash('Username dan password wajib diisi', 'danger')
        elif password != password_confirm:
            flash('Konfirmasi password tidak cocok', 'danger')
        else:
            success, message = user_manager.register(username, password, nama_lengkap, email, level)
            if success:
                flash(message, 'success')
                return redirect(url_for('login'))
            else:
                flash(message, 'danger')

    return render_template('daftar.html', 
                           total_users=total_users, 
                           total_admins=total_admins, 
                           total_regular_users=total_regular_users)

@app.route('/pelanggan')
def daftar_pelanggan():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    # Ambil pelanggan untuk pengguna yang sedang login
    pelanggan = smp.dapatkan_semua_pelanggan(session['user_id'])
    return render_template('pelanggan.html', pelanggan=pelanggan)

@app.route('/pelanggan/tambah', methods=['GET', 'POST'])
def tambah_pelanggan():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nama = request.form['nama']
        telepon = request.form['telepon']
        email = request.form['email']
        alamat = request.form['alamat']
        lat = request.form.get('latitude', '')
        lng = request.form.get('longitude', '')

        try:
            lat = float(lat) if lat else 0.0
            lng = float(lng) if lng else 0.0
            # Tambahkan user_id ke pelanggan baru
            pelanggan_id = smp.tambah_pelanggan(nama, telepon, email, alamat, lat, lng, session['user_id'])
            flash(f'Pelanggan berhasil ditambahkan dengan ID: {pelanggan_id}', 'success')
            return redirect(url_for('daftar_pelanggan'))
        except ValueError:
            flash('Koordinat tidak valid. Silakan coba lagi.', 'danger')

    return render_template('tambah_pelanggan.html')

@app.route('/pelanggan/<int:pelanggan_id>')
def detail_pelanggan(pelanggan_id):
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    pelanggan = smp.dapatkan_pelanggan(pelanggan_id)

    # Validasi kepemilikan pelanggan
    if pelanggan[8] != session['user_id']:
        flash('Anda tidak memiliki akses ke pelanggan ini', 'danger')
        return redirect(url_for('daftar_pelanggan'))

    tagihan = smp.dapatkan_tagihan_pelanggan(pelanggan_id)

    total = sum(t[2] for t in tagihan)
    belum_dibayar = sum(t[2] for t in tagihan if t[5] == "BELUM DIBAYAR")

    return render_template('detail_pelanggan.html', pelanggan=pelanggan, tagihan=tagihan, 
                          total=total, belum_dibayar=belum_dibayar)

@app.route('/pelanggan/<int:pelanggan_id>/edit', methods=['GET', 'POST'])
def edit_pelanggan(pelanggan_id):
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    pelanggan = smp.dapatkan_pelanggan(pelanggan_id)

    # Validasi kepemilikan pelanggan
    if pelanggan[8] != session['user_id']:
        flash('Anda tidak memiliki akses ke pelanggan ini', 'danger')
        return redirect(url_for('daftar_pelanggan'))

    if request.method == 'POST':
        nama = request.form.get('nama')
        telepon = request.form.get('telepon')
        email = request.form.get('email')
        alamat = request.form.get('alamat')
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')

        pembaruan = {}
        if nama: pembaruan['nama'] = nama
        if telepon: pembaruan['telepon'] = telepon
        if email: pembaruan['email'] = email
        if alamat: pembaruan['alamat'] = alamat

        try:
            if lat: pembaruan['lat'] = float(lat)
            if lng: pembaruan['lng'] = float(lng)

            if pembaruan:
                smp.perbarui_pelanggan(pelanggan_id, **pembaruan)
                flash('Pelanggan berhasil diperbarui.', 'success')
            else:
                flash('Tidak ada perubahan dilakukan.', 'info')

            return redirect(url_for('detail_pelanggan', pelanggan_id=pelanggan_id))
        except ValueError:
            flash('Koordinat tidak valid. Silakan coba lagi.', 'danger')

    return render_template('edit_pelanggan.html', pelanggan=pelanggan)

@app.route('/pelanggan/<int:pelanggan_id>/hapus', methods=['POST'])
def hapus_pelanggan(pelanggan_id):
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    pelanggan = smp.dapatkan_pelanggan(pelanggan_id)

    # Validasi kepemilikan pelanggan
    if pelanggan[8] != session['user_id']:
        flash('Anda tidak memiliki akses ke pelanggan ini', 'danger')
        return redirect(url_for('daftar_pelanggan'))

    smp.hapus_pelanggan(pelanggan_id)
    flash('Pelanggan dan semua tagihannya berhasil dihapus.', 'success')
    return redirect(url_for('daftar_pelanggan'))

@app.route('/pelanggan/<int:pelanggan_id>/tagihan/tambah', methods=['GET', 'POST'])
def tambah_tagihan(pelanggan_id):
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    pelanggan = smp.dapatkan_pelanggan(pelanggan_id)

    # Validasi kepemilikan pelanggan
    if pelanggan[8] != session['user_id']:
        flash('Anda tidak memiliki akses ke pelanggan ini', 'danger')
        return redirect(url_for('daftar_pelanggan'))

    if request.method == 'POST':
        jumlah = request.form['jumlah']
        deskripsi = request.form['deskripsi']
        tanggal_jatuh_tempo = request.form['tanggal_jatuh_tempo']

        try:
            jumlah = float(jumlah)
            tanggal_jatuh_tempo = tanggal_jatuh_tempo if tanggal_jatuh_tempo else None
            tagihan_id = smp.tambah_tagihan(pelanggan_id, jumlah, deskripsi, tanggal_jatuh_tempo)
            flash(f'Tagihan berhasil ditambahkan dengan ID: {tagihan_id}', 'success')
            return redirect(url_for('detail_pelanggan', pelanggan_id=pelanggan_id))
        except ValueError:
            flash('Jumlah tidak valid. Silakan coba lagi.', 'danger')

    return render_template('tambah_tagihan.html', pelanggan=pelanggan)

@app.route('/pelanggan/<int:pelanggan_id>/tagihan/tambah-cepat', methods=['POST'])
def tambah_tagihan_cepat(pelanggan_id):
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    pelanggan = smp.dapatkan_pelanggan(pelanggan_id)

    # Validasi kepemilikan pelanggan
    if pelanggan[8] != session['user_id']:
        flash('Anda tidak memiliki akses ke pelanggan ini', 'danger')
        return redirect(url_for('daftar_pelanggan'))

    jumlah = request.form['jumlah']
    deskripsi = request.form['deskripsi']
    tanggal_jatuh_tempo = request.form['tanggal_jatuh_tempo']

    try:
        jumlah = float(jumlah)
        tanggal_jatuh_tempo = tanggal_jatuh_tempo if tanggal_jatuh_tempo else None
        tagihan_id = smp.tambah_tagihan(pelanggan_id, jumlah, deskripsi, tanggal_jatuh_tempo)
        flash(f'Tagihan cepat berhasil ditambahkan dengan ID: {tagihan_id}', 'success')
    except ValueError:
        flash('Jumlah tidak valid. Silakan coba lagi.', 'danger')

    return redirect(url_for('detail_pelanggan', pelanggan_id=pelanggan_id))

@app.route('/pelanggan/<int:pelanggan_id>/pembayaran-cepat', methods=['POST'])
def pembayaran_cepat(pelanggan_id):
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    pelanggan = smp.dapatkan_pelanggan(pelanggan_id)

    # Validasi kepemilikan pelanggan
    if pelanggan[8] != session['user_id']:
        flash('Anda tidak memiliki akses ke pelanggan ini', 'danger')
        return redirect(url_for('daftar_pelanggan'))

    tagihan_id = request.form.get('tagihan_id')
    metode_pembayaran = request.form.get('metode_pembayaran')
    catatan_pembayaran = request.form.get('catatan_pembayaran')

    if not tagihan_id:
        flash('Harap pilih tagihan yang akan dibayar', 'warning')
        return redirect(url_for('detail_pelanggan', pelanggan_id=pelanggan_id))

    try:
        tagihan_id = int(tagihan_id)

        # Perbarui tagihan dengan catatan pembayaran
        tagihan = smp.dapatkan_tagihan(tagihan_id)
        deskripsi_baru = tagihan[3] or ""

        if catatan_pembayaran:
            deskripsi_baru += f"\n[PEMBAYARAN: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] "
            deskripsi_baru += f"Metode: {metode_pembayaran}. {catatan_pembayaran}"

        smp.perbarui_tagihan(tagihan_id, deskripsi=deskripsi_baru, status_pembayaran="SUDAH DIBAYAR")
        flash(f'Tagihan ID {tagihan_id} berhasil dibayar via {metode_pembayaran}', 'success')
    except (ValueError, TypeError) as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')

    return redirect(url_for('detail_pelanggan', pelanggan_id=pelanggan_id))

@app.route('/tambah-tagihan-cepat', methods=['POST'])
def tambah_tagihan_cepat_home():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    pelanggan_id = request.form.get('pelanggan_id')
    jumlah = request.form.get('jumlah')
    deskripsi = request.form.get('deskripsi', '')
    tanggal_jatuh_tempo = request.form.get('tanggal_jatuh_tempo', '')

    if not pelanggan_id or not jumlah:
        flash('Pelanggan dan jumlah tagihan harus diisi', 'warning')
        return redirect(url_for('index'))

    try:
        pelanggan_id = int(pelanggan_id)
        jumlah = float(jumlah)

        # Verifikasi pelanggan
        pelanggan = smp.dapatkan_pelanggan(pelanggan_id)
        if not pelanggan:
            flash('Pelanggan tidak ditemukan', 'danger')
            return redirect(url_for('index'))

        # Validasi kepemilikan pelanggan
        if pelanggan[8] != session['user_id']:
            flash('Anda tidak memiliki akses ke pelanggan ini', 'danger')
            return redirect(url_for('index'))

        # Tambahkan tagihan
        tanggal_jatuh_tempo = tanggal_jatuh_tempo if tanggal_jatuh_tempo else None
        tagihan_id = smp.tambah_tagihan(pelanggan_id, jumlah, deskripsi, tanggal_jatuh_tempo)

        flash(f'Tagihan berhasil ditambahkan untuk {pelanggan[1]}', 'success')
        return redirect(url_for('detail_pelanggan', pelanggan_id=pelanggan_id))
    except ValueError:
        flash('Jumlah tidak valid. Silakan coba lagi.', 'danger')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/tagihan/<int:tagihan_id>/edit', methods=['GET', 'POST'])
def edit_tagihan(tagihan_id):
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    tagihan = smp.dapatkan_tagihan(tagihan_id)
    pelanggan_id = tagihan[1]

    # Dapatkan pelanggan untuk validasi pemilik
    pelanggan = smp.dapatkan_pelanggan(pelanggan_id)
    if pelanggan[8] != session['user_id']:
        flash('Anda tidak memiliki akses ke tagihan ini', 'danger')
        return redirect(url_for('daftar_pelanggan'))

    if request.method == 'POST':
        jumlah = request.form.get('jumlah')
        deskripsi = request.form.get('deskripsi')
        tanggal_jatuh_tempo = request.form.get('tanggal_jatuh_tempo')
        status_pembayaran = request.form.get('status_pembayaran')
        metode_pembayaran = request.form.get('metode_pembayaran')
        catatan_pembayaran = request.form.get('catatan_pembayaran')

        # Tambahkan catatan pembayaran ke deskripsi jika ada
        if (metode_pembayaran or catatan_pembayaran) and status_pembayaran == "SUDAH DIBAYAR":
            deskripsi_baru = deskripsi or tagihan[3] or ""
            deskripsi_baru += f"\n[PEMBAYARAN: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] "
            if metode_pembayaran:
                deskripsi_baru += f"Metode: {metode_pembayaran}. "
            if catatan_pembayaran:
                deskripsi_baru += catatan_pembayaran
            deskripsi = deskripsi_baru

        pembaruan = {}
        try:
            if jumlah: pembaruan['jumlah'] = float(jumlah)
            if deskripsi: pembaruan['deskripsi'] = deskripsi
            if tanggal_jatuh_tempo: pembaruan['tanggal_jatuh_tempo'] = tanggal_jatuh_tempo
            if status_pembayaran: pembaruan['status_pembayaran'] = status_pembayaran

            if pembaruan:
                smp.perbarui_tagihan(tagihan_id, **pembaruan)
                flash('Tagihan berhasil diperbarui.', 'success')
            else:
                flash('Tidak ada perubahan dilakukan.', 'info')

            return redirect(url_for('detail_pelanggan', pelanggan_id=pelanggan_id))
        except ValueError:
            flash('Jumlah tidak valid. Silakan coba lagi.', 'danger')

    return render_template('edit_tagihan.html', tagihan=tagihan)

@app.route('/tagihan/<int:tagihan_id>/hapus', methods=['POST'])
def hapus_tagihan(tagihan_id):
    tagihan = smp.dapatkan_tagihan(tagihan_id)
    pelanggan_id = tagihan[1]

    smp.hapus_tagihan(tagihan_id)
    flash('Tagihan berhasil dihapus.', 'success')
    return redirect(url_for('detail_pelanggan', pelanggan_id=pelanggan_id))

@app.route('/tagihan/<int:tagihan_id>/bayar', methods=['POST'])
def bayar_tagihan(tagihan_id):
    tagihan = smp.dapatkan_tagihan(tagihan_id)
    pelanggan_id = tagihan[1]

    smp.tandai_tagihan_sebagai_dibayar(tagihan_id)
    flash('Tagihan berhasil ditandai sebagai SUDAH DIBAYAR.', 'success')
    return redirect(url_for('detail_pelanggan', pelanggan_id=pelanggan_id))

@app.route('/tagihan/hari-ini')
def tagihan_hari_ini():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    try:
        # Ubah fungsi di SMP untuk mendapatkan tagihan berdasarkan user_id
        tagihan = smp.dapatkan_tagihan_hari_ini()
        # Filter tagihan berdasarkan user_id
        user_tagihan = []
        for t in tagihan:
            try:
                pelanggan = smp.dapatkan_pelanggan(t[1])
                if pelanggan and pelanggan[8] == session['user_id']:
                    user_tagihan.append(t)
            except Exception as e:
                print(f"Error memproses tagihan {t[0]}: {e}")

        total = sum(t[2] for t in user_tagihan if t[5] == "BELUM DIBAYAR")
        now = datetime.datetime.now()
        return render_template('tagihan_hari_ini.html', tagihan=user_tagihan, total=total, now=now)
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        now = datetime.datetime.now()
        return render_template('tagihan_hari_ini.html', tagihan=[], total=0, now=now)

@app.route('/tagihan/belum-dibayar')
def tagihan_belum_dibayar():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    try:
        tagihan = smp.dapatkan_tagihan_belum_dibayar()
        # Filter tagihan berdasarkan user_id
        user_tagihan = []
        total = 0

        for t in tagihan:
            try:
                pelanggan = smp.dapatkan_pelanggan(t[1])
                if pelanggan and pelanggan[8] == session['user_id']:
                    user_tagihan.append(t)
                    total += float(t[2])  # Pastikan nilai jumlah tagihan adalah float
            except Exception as e:
                print(f"Error saat memproses tagihan {t[0]}: {str(e)}")
                continue

        now = datetime.datetime.now()
        return render_template('tagihan_belum_dibayar.html', tagihan=user_tagihan, total=total, now=now)
    except Exception as e:
        print(f"Exception pada route tagihan_belum_dibayar: {str(e)}")
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        return render_template('tagihan_belum_dibayar.html', tagihan=[], total=0, now=datetime.datetime.now())

@app.route('/tagihan/statistik')
def tagihan_statistik():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    try:
        # Ambil tagihan 30 hari terakhir
        tagihan_belum_dibayar = smp.dapatkan_tagihan_30_hari_terakhir('BELUM DIBAYAR')
        tagihan_sudah_dibayar = smp.dapatkan_tagihan_30_hari_terakhir('SUDAH DIBAYAR')

        # Filter untuk user saat ini
        user_tagihan_belum_dibayar = []
        user_tagihan_sudah_dibayar = []

        for t in tagihan_belum_dibayar:
            pelanggan = smp.dapatkan_pelanggan(t[1])
            if pelanggan and pelanggan[8] == session['user_id']:
                user_tagihan_belum_dibayar.append(t)

        for t in tagihan_sudah_dibayar:
            pelanggan = smp.dapatkan_pelanggan(t[1])
            if pelanggan and pelanggan[8] == session['user_id']:
                user_tagihan_sudah_dibayar.append(t)

        # Tagihan hari ini
        hari_ini = date.today().strftime("%Y-%m-%d")
        tagihan_hari_ini = smp.dapatkan_tagihan_berdasarkan_tanggal(hari_ini)
        user_tagihan_hari_ini = []

        for t in tagihan_hari_ini:
            pelanggan = smp.dapatkan_pelanggan(t[1])
            if pelanggan and pelanggan[8] == session['user_id']:
                user_tagihan_hari_ini.append(t)

        # Hitung total
        total_belum_dibayar = sum(t[2] for t in user_tagihan_belum_dibayar)
        total_sudah_dibayar = sum(t[2] for t in user_tagihan_sudah_dibayar)
        total_jatuh_tempo_hari_ini = sum(t[2] for t in user_tagihan_hari_ini if t[5] == "BELUM DIBAYAR")

        # Jumlah pelanggan
        pelanggan = smp.dapatkan_semua_pelanggan(session['user_id'])
        jumlah_pelanggan = len(pelanggan)

        return render_template(
            'tagihan_statistik.html', 
            tagihan_belum_dibayar=user_tagihan_belum_dibayar,
            tagihan_sudah_dibayar=user_tagihan_sudah_dibayar,
            total_belum_dibayar=total_belum_dibayar,
            total_sudah_dibayar=total_sudah_dibayar,
            total_jatuh_tempo_hari_ini=total_jatuh_tempo_hari_ini,
            jumlah_pelanggan=jumlah_pelanggan,
            now=datetime.datetime.now()
        )
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'danger')
        return render_template('tagihan_statistik.html', 
                          tagihan_belum_dibayar=[], 
                          tagihan_sudah_dibayar=[], 
                          total_belum_dibayar=0,
                          total_sudah_dibayar=0,
                          total_jatuh_tempo_hari_ini=0,
                          jumlah_pelanggan=0,
                          now=datetime.datetime.now())

@app.route('/tagihan/tanggal', methods=['GET', 'POST'])
def tagihan_tanggal():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    tagihan = []
    total = 0
    tanggal = ""

    if request.method == 'POST':
        tanggal = request.form['tanggal']
        try:
            # Validasi format tanggal
            datetime.datetime.strptime(tanggal, "%Y-%m-%d")
            semua_tagihan = smp.dapatkan_tagihan_berdasarkan_tanggal(tanggal)

            # Filter tagihan berdasarkan user_id
            for t in semua_tagihan:
                pelanggan = smp.dapatkan_pelanggan(t[1])
                if pelanggan and pelanggan[8] == session['user_id']:
                    tagihan.append(t)

            total = sum(t[2] for t in tagihan if t[5] == "BELUM DIBAYAR")
        except ValueError:
            flash('Format tanggal tidak valid. Gunakan YYYY-MM-DD.', 'danger')

    return render_template('tagihan_tanggal.html', tagihan=tagihan, total=total, tanggal=tanggal)

@app.route('/peta/<int:pelanggan_id>')
def peta(pelanggan_id):
    pelanggan = smp.dapatkan_pelanggan(pelanggan_id)

    lat, lng = pelanggan[5], pelanggan[6]
    alamat = pelanggan[4]

    if lat and lng:
        map_url = f"https://www.google.com/maps?q={lat},{lng}"
    elif alamat:
        map_url = f"https://www.google.com/maps/search/?api=1&query={alamat.replace(' ', '+')}"
    else:
        map_url = ""
        flash('Tidak ada data lokasi untuk pelanggan ini.', 'warning')
        return redirect(url_for('detail_pelanggan', pelanggan_id=pelanggan_id))

    return render_template('peta.html', pelanggan=pelanggan, map_url=map_url)

@app.route('/api/pelanggan')
def api_pelanggan():
    pelanggan = smp.dapatkan_semua_pelanggan()
    hasil = []
    for p in pelanggan:
        hasil.append({
            'id': p[0],
            'nama': p[1],
            'telepon': p[2],
            'email': p[3],
            'alamat': p[4],
            'latitude': p[5],
            'longitude': p[6],
            'dibuat_pada': p[7]
        })
    return jsonify(hasil)

@app.route('/api/tagihan')
def api_tagihan():
    tagihan = smp.dapatkan_tagihan_belum_dibayar()
    hasil = []
    for t in tagihan:
        hasil.append({
            'id': t[0],
            'pelanggan_id': t[1],
            'jumlah': t[2],
            'deskripsi': t[3],
            'tanggal_jatuh_tempo': t[4],
            'status_pembayaran': t[5],
            'dibuat_pada': t[6],
            'nama_pelanggan': t[7]
        })
    return jsonify(hasil)

@app.route('/api/keuangan/ringkasan')
def api_ringkasan_keuangan():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Ambil data untuk user yang login
        user_id = session['user_id']

        # Ambil tagihan 30 hari terakhir
        tagihan_belum_dibayar = smp.dapatkan_tagihan_30_hari_terakhir('BELUM DIBAYAR')
        tagihan_sudah_dibayar = smp.dapatkan_tagihan_30_hari_terakhir('SUDAH DIBAYAR')

        # Filter untuk user saat ini
        user_tagihan_belum_dibayar = []
        user_tagihan_sudah_dibayar = []

        for t in tagihan_belum_dibayar:
            pelanggan = smp.dapatkan_pelanggan(t[1])
            if pelanggan and pelanggan[8] == session['user_id']:
                user_tagihan_belum_dibayar.append(t)

        for t in tagihan_sudah_dibayar:
            pelanggan = smp.dapatkan_pelanggan(t[1])
            if pelanggan and pelanggan[8] == session['user_id']:
                user_tagihan_sudah_dibayar.append(t)

        # Tagihan hari ini
        hari_ini = date.today().strftime("%Y-%m-%d")
        tagihan_hari_ini = smp.dapatkan_tagihan_berdasarkan_tanggal(hari_ini)
        user_tagihan_hari_ini = []

        for t in tagihan_hari_ini:
            pelanggan = smp.dapatkan_pelanggan(t[1])
            if pelanggan and pelanggan[8] == session['user_id']:
                user_tagihan_hari_ini.append(t)

        # Hitung total
        total_belum_dibayar = sum(t[2] for t in user_tagihan_belum_dibayar)
        total_sudah_dibayar = sum(t[2] for t in user_tagihan_sudah_dibayar)
        total_jatuh_tempo_hari_ini = sum(t[2] for t in user_tagihan_hari_ini if t[5] == "BELUM DIBAYAR")

        # Jumlah pelanggan
        pelanggan = smp.dapatkan_semua_pelanggan(user_id)
        jumlah_pelanggan = len(pelanggan)

        return jsonify({
            "total_belum_dibayar": total_belum_dibayar,
            "total_sudah_dibayar": total_sudah_dibayar,
            "total_jatuh_tempo_hari_ini": total_jatuh_tempo_hari_ini,
            "jumlah_pelanggan": jumlah_pelanggan
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/user')
def daftar_user():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    # Periksa apakah user adalah admin
    if session.get('level') != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini', 'danger')
        return redirect(url_for('index'))

    # Mendapatkan semua user kecuali admin
    users = [user for user in user_manager.get_all_users() if user[4] != 'admin']
    return render_template('daftar_user.html', users=users)

@app.route('/akuntansi', methods=['GET', 'POST'])
def akuntansi():
    if 'user_id' not in session or session.get('level') != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        tanggal = request.form.get('tanggal')
        jenis = request.form.get('jenis')
        keterangan = request.form.get('keterangan')
        jumlah = float(request.form.get('jumlah', 0))
        kategori = request.form.get('kategori')

        conn = sqlite3.connect('manajemen_pelanggan.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO akuntansi (tanggal, jenis, keterangan, jumlah, kategori)
        VALUES (?, ?, ?, ?, ?)
        ''', (tanggal, jenis, keterangan, float(jumlah), kategori))
        conn.commit()
        conn.close()
        
        flash('Data akuntansi berhasil ditambahkan', 'success')
        return redirect(url_for('akuntansi'))

    conn = sqlite3.connect('manajemen_pelanggan.db')
    cursor = conn.cursor()
    
    # Ambil data akuntansi
    cursor.execute("SELECT * FROM akuntansi ORDER BY tanggal DESC")
    transaksi_raw = cursor.fetchall()
    # Konversi nilai ke float hanya untuk jumlah
    transaksi = []
    for t in transaksi_raw:
        try:
            jumlah = float(t[4])  # jumlah is at index 4
            transaksi.append((t[0], t[1], t[2], t[3], t[4], jumlah))
        except (ValueError, TypeError):
            continue
    
    # Hitung ringkasan
    cursor.execute("SELECT SUM(jumlah) FROM akuntansi WHERE kategori='Modal Awal'")
    modal_awal = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(jumlah) FROM akuntansi WHERE jenis='Pengeluaran'")
    total_pengeluaran = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(jumlah) FROM akuntansi WHERE jenis='Pemasukan'")
    pemasukan_kotor = cursor.fetchone()[0] or 0
    
    # Hitung tagihan yang dibayar hari ini
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT SUM(jumlah) FROM akuntansi WHERE tanggal = ? AND jenis = 'Pemasukan'", (today,))
    tagihan_hari_ini = cursor.fetchone()[0] or 0
    
    pemasukan_bersih = pemasukan_kotor - total_pengeluaran
    untung_kotor = pemasukan_kotor - modal_awal
    untung_bersih = pemasukan_bersih - modal_awal
    
    conn.close()
    
    return render_template('akuntansi.html', 
                         transaksi=transaksi,
                         modal_awal=modal_awal,
                         total_pengeluaran=total_pengeluaran,
                         pemasukan_kotor=pemasukan_kotor,
                         pemasukan_bersih=pemasukan_bersih,
                         untung_kotor=untung_kotor,
                         untung_bersih=untung_bersih,
                         tagihan_hari_ini=tagihan_hari_ini)

@app.route('/admin')
def daftar_admin():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    # Periksa apakah user adalah admin
    if session.get('level') != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini', 'danger')
        return redirect(url_for('index'))

    # Mendapatkan semua admin
    admins = [user for user in user_manager.get_all_users() if user[4] == 'admin']

@app.route('/admin/promote', methods=['GET', 'POST'])
def promote_user():
    if 'user_id' not in session or session.get('level') != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash('Username harus diisi', 'danger')
            return render_template('promote_user.html')

        conn = user_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, level FROM pengguna WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            flash('User tidak ditemukan', 'danger')
        elif user[1] == 'admin':
            flash('User sudah menjadi admin', 'warning')
        else:
            cursor.execute("UPDATE pengguna SET level = 'admin' WHERE id = ?", (user[0],))
            conn.commit()
            flash(f'User {username} berhasil dipromosikan menjadi admin', 'success')
            return redirect(url_for('daftar_admin'))
        conn.close()

    return render_template('promote_user.html')

    return render_template('daftar_admin.html', admins=admins)

@app.route('/admin/tambah', methods=['GET', 'POST'])
def tambah_admin():
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    # Periksa apakah user adalah admin
    if session.get('level') != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        nama_lengkap = request.form.get('nama_lengkap')
        email = request.form.get('email')

        # Validasi
        if not username or not password:
            flash('Username dan password wajib diisi', 'danger')
        elif password != password_confirm:
            flash('Konfirmasi password tidak cocok', 'danger')
        else:
            success, message = user_manager.register(username, password, nama_lengkap, email, 'admin')
            if success:
                flash('Admin baru berhasil ditambahkan', 'success')
                return redirect(url_for('daftar_admin'))
            else:
                flash(message, 'danger')

    return render_template('tambah_admin.html')

@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    # Periksa apakah user adalah admin atau mengedit profilnya sendiri
    if session.get('level') != 'admin' and int(session.get('user_id')) != user_id:
        flash('Anda tidak memiliki akses untuk mengedit user ini', 'danger')
        return redirect(url_for('index'))

    user = user_manager.get_user(user_id)
    if not user:
        flash('User tidak ditemukan', 'danger')
        return redirect(url_for('daftar_user'))

    if request.method == 'POST':
        nama_lengkap = request.form.get('nama_lengkap')
        email = request.form.get('email')
        level = request.form.get('level')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        # Jika non-admin mencoba mengubah level
        if session.get('level') != 'admin' and level != user[4]:
            flash('Anda tidak berhak mengubah level user', 'danger')
            return render_template('edit_user.html', user=user)

        # Validasi password jika diubah
        if password:
            if password != password_confirm:
                flash('Konfirmasi password tidak cocok', 'danger')
                return render_template('edit_user.html', user=user)

            success, message = user_manager.update_user(user_id, nama_lengkap, email, level, password)
        else:
            success, message = user_manager.update_user(user_id, nama_lengkap, email, level)

        if success:
            flash(message, 'success')
            # Jika user mengedit profilnya sendiri, update session
            if int(session.get('user_id')) == user_id:
                if nama_lengkap:
                    session['nama_lengkap'] = nama_lengkap
                if level:
                    session['level'] = level

            # Redirect admin ke daftar user, user biasa ke halaman utama
            if session.get('level') == 'admin':
                return redirect(url_for('daftar_user'))
            else:
                return redirect(url_for('index'))
        else:
            flash(message, 'danger')

    return render_template('edit_user.html', user=user)

@app.route('/user/<int:user_id>/hapus', methods=['POST'])
def hapus_user(user_id):
    if 'user_id' not in session:
        flash('Anda harus login terlebih dahulu', 'warning')
        return redirect(url_for('login'))

    # Hanya admin yang bisa menghapus user
    if session.get('level') != 'admin':
        flash('Anda tidak memiliki akses untuk menghapus user', 'danger')
        return redirect(url_for('index'))

    # Tidak bisa menghapus diri sendiri
    if int(session.get('user_id')) == user_id:
        flash('Anda tidak dapat menghapus akun Anda sendiri', 'danger')
        return redirect(url_for('daftar_user'))

    success, message = user_manager.delete_user(user_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(url_for('daftar_user'))

# Mode CLI untuk kompatibilitas
def tampilkan_menu():
    print("\n===== SISTEM MANAJEMEN PELANGGAN DAN TAGIHAN =====")
    print("1. Tambah Pelanggan Baru")
    print("2. Lihat Semua Pelanggan")
    print("3. Lihat Detail Pelanggan")
    print("4. Perbarui Pelanggan")
    print("5. Hapus Pelanggan")
    print("6. Tambah Tagihan Baru")
    print("7. Lihat Tagihan Pelanggan")
    print("8. Perbarui Tagihan")
    print("9. Tandai Tagihan Sebagai Dibayar")
    print("10. Lihat Tagihan Hari Ini")
    print("11. Lihat Tagihan Belum Dibayar")
    print("12. Lihat Total Jumlah Belum Dibayar")
    print("13. Lihat Tagihan Berdasarkan Tanggal")
    print("14. Buka Lokasi Pelanggan di Peta")
    print("0. Keluar")
    pilihan = input("Masukkan pilihan Anda: ")
    return pilihan

def cli_mode():
    while True:
        pilihan = tampilkan_menu()

        if pilihan == '1':
            nama = input("Masukkan nama pelanggan: ")
            telepon = input("Masukkan nomor telepon: ")
            email = input("Masukkan email: ")
            alamat = input("Masukkan alamat: ")
            lat = input("Masukkan latitude (kosongkan jika tidak diketahui): ")
            lng = input("Masukkan longitude (kosongkan jika tidak diketahui): ")

            try:
                lat = float(lat) if lat else 0.0
                lng = float(lng) if lng else 0.0
                pelanggan_id = smp.tambah_pelanggan(nama, telepon, email, alamat, lat, lng)
                print(f"Pelanggan berhasil ditambahkan dengan ID: {pelanggan_id}")
            except ValueError:
                print("Koordinat tidak valid. Pelanggan ditambahkan tanpa koordinat.")
                smp.tambah_pelanggan(nama, telepon, email, alamat)

        elif pilihan == '2':
            pelanggan = smp.dapatkan_semua_pelanggan()
            if not pelanggan:
                print("Tidak ada pelanggan ditemukan.")
            else:
                print("\n=== Semua Pelanggan ===")
                for p in pelanggan:
                    print(f"ID: {p[0]}, Nama: {p[1]}, Telepon: {p[2]}")

        elif pilihan == '3':
            pelanggan_id = input("Masukkan ID pelanggan: ")
            try:
                pelanggan = smp.dapatkan_pelanggan(int(pelanggan_id))
                if pelanggan:
                    print(f"\nID: {pelanggan[0]}")
                    print(f"Nama: {pelanggan[1]}")
                    print(f"Telepon: {pelanggan[2]}")
                    print(f"Email: {pelanggan[3]}")
                    print(f"Alamat: {pelanggan[4]}")
                    print(f"Koordinat: {pelanggan[5]}, {pelanggan[6]}")
                    print(f"Dibuat pada: {pelanggan[7]}")
                else:
                    print("Pelanggan tidak ditemukan.")
            except ValueError:
                print("ID tidak valid.")

        elif pilihan == '4':
            pelanggan_id = input("Masukkan ID pelanggan yang akan diperbarui: ")
            try:
                pelanggan_id = int(pelanggan_id)
                pelanggan = smp.dapatkan_pelanggan(pelanggan_id)
                if not pelanggan:
                    print("Pelanggan tidak ditemukan.")
                    continue

                print(f"Nama saat ini: {pelanggan[1]}")
                nama = input("Masukkan nama baru (kosongkan untuk mempertahankan yang saat ini): ")

                print(f"Telepon saat ini: {pelanggan[2]}")
                telepon = input("Masukkan telepon baru (kosongkan untuk mempertahankan yang saat ini): ")

                print(f"Email saat ini: {pelanggan[3]}")
                email = input("Masukkan email baru (kosongkan untuk mempertahankan yang saat ini): ")

                print(f"Alamat saat ini: {pelanggan[4]}")
                alamat = input("Masukkan alamat baru (kosongkan untuk mempertahankan yang saat ini): ")

                print(f"Koordinat saat ini: {pelanggan[5]}, {pelanggan[6]}")
                lat = input("Masukkan latitude baru (kosongkan untuk mempertahankan yang saat ini): ")
                lng = input("Masukkan longitude baru (kosongkan untuk mempertahankan yang saat ini): ")

                pembaruan = {}
                if nama: pembaruan['nama'] = nama
                if telepon: pembaruan['telepon'] = telepon
                if email: pembaruan['email'] = email
                if alamat: pembaruan['alamat'] = alamat
                if lat: pembaruan['lat'] = float(lat)
                if lng: pembaruan['lng'] = float(lng)

                if pembaruan:
                    smp.perbarui_pelanggan(pelanggan_id, **pembaruan)
                    print("Pelanggan berhasil diperbarui.")
                else:
                    print("Tidak ada perubahan dilakukan.")
            except ValueError:
                print("Input tidak valid.")

        elif pilihan == '5':
            pelanggan_id = input("Masukkan ID pelanggan yang akan dihapus: ")
            try:
                pelanggan_id = int(pelanggan_id)
                pelanggan = smp.dapatkan_pelanggan(pelanggan_id)
                if not pelanggan:
                    print("Pelanggan tidak ditemukan.")
                    continue

                konfirmasi = input(f"Apakah Anda yakin ingin menghapus {pelanggan[1]}? Ini juga akan menghapus semua tagihan. (y/n): ")
                if konfirmasi.lower() == 'y':
                    smp.hapus_pelanggan(pelanggan_id)
                    print("Pelanggan berhasil dihapus.")
            except ValueError:
                print("ID tidak valid.")

        elif pilihan == '6':
            pelanggan_id = input("Masukkan ID pelanggan: ")
            try:
                pelanggan_id = int(pelanggan_id)
                pelanggan = smp.dapatkan_pelanggan(pelanggan_id)
                if not pelanggan:
                    print("Pelanggan tidak ditemukan.")
                    continue

                jumlah = input("Masukkan jumlah tagihan: ")
                deskripsi = input("Masukkan deskripsi: ")
                tanggal_jatuh_tempo = input("Masukkan tanggal jatuh tempo (YYYY-MM-DD) atau kosongkan untuk default (14 hari): ")

                try:
                    jumlah = float(jumlah)
                    tanggal_jatuh_tempo = tanggal_jatuh_tempo if tanggal_jatuh_tempo else None
                    tagihan_id = smp.tambah_tagihan(pelanggan_id, jumlah, deskripsi, tanggal_jatuh_tempo)
                    print(f"Tagihan berhasil ditambahkan dengan ID: {tagihan_id}")
                except ValueError:
                    print("Jumlah tidak valid.")
            except ValueError:
                print("ID pelanggan tidak valid.")

        elif pilihan == '7':
            pelanggan_id = input("Masukkan ID pelanggan: ")
            try:
                pelanggan_id = int(pelanggan_id)
                pelanggan = smp.dapatkan_pelanggan(pelanggan_id)
                if not pelanggan:
                    print("Pelanggan tidak ditemukan.")
                    continue

                tagihan = smp.dapatkan_tagihan_pelanggan(pelanggan_id)
                if not tagihan:
                    print(f"Tidak ada tagihan ditemukan untuk {pelanggan[1]}.")
                else:
                    print(f"\n=== Tagihan untuk {pelanggan[1]} ===")
                    total = 0
                    belum_dibayar = 0
                    for t in tagihan:
                        status = t[5]
                        print(f"ID Tagihan: {t[0]}, Jumlah: Rp{t[2]:.2f}, Jatuh Tempo: {t[4]}, Status: {status}")
                        if status == "BELUM DIBAYAR":
                            belum_dibayar += t[2]
                        total += t[2]
                    print(f"\nTotal Tagihan: Rp{total:.2f}")
                    print(f"Jumlah Belum Dibayar: Rp{belum_dibayar:.2f}")
            except ValueError:
                print("ID pelanggan tidak valid.")

        elif pilihan == '8':
            tagihan_id = input("Masukkan ID tagihan yang akan diperbarui: ")
            try:
                tagihan_id = int(tagihan_id)
                tagihan = smp.dapatkan_tagihan(tagihan_id)
                if not tagihan:
                    print("Tagihan tidak ditemukan.")
                    continue

                print(f"Jumlah saat ini: Rp{tagihan[2]:.2f}")
                jumlah = input("Masukkan jumlah baru (kosongkan untuk mempertahankan yang saat ini): ")

                print(f"Deskripsi saat ini: {tagihan[3]}")
                deskripsi = input("Masukkan deskripsi baru (kosongkan untuk mempertahankan yang saat ini): ")

                print(f"Tanggal Jatuh Tempo saat ini: {tagihan[4]}")
                tanggal_jatuh_tempo = input("Masukkan tanggal jatuh tempo baru (YYYY-MM-DD) (kosongkan untuk mempertahankan yang saat ini): ")

                print(f"Status saat ini: {tagihan[5]}")
                pilihan_status = input("Perbarui status? (1: SUDAH DIBAYAR, 2: BELUM DIBAYAR, 0: Tidak ada perubahan): ")

                try:
                    pembaruan = {}
                    if jumlah: pembaruan['jumlah']= float(jumlah)
                    if deskripsi: pembaruan['deskripsi'] = deskripsi
                    if tanggal_jatuh_tempo: pembaruan['tanggal_jatuh_tempo'] = tanggal_jatuh_tempo
                    if pilihan_status == '1': pembaruan['status_pembayaran'] = "SUDAH DIBAYAR"
                    elif pilihan_status == '2': pembaruan['status_pembayaran'] = "BELUM DIBAYAR"

                    if pembaruan:
                        smp.perbarui_tagihan(tagihan_id, **pembaruan)
                        print("Tagihan berhasil diperbarui.")
                    else:
                        print("Tidak ada perubahan dilakukan.")
                except ValueError:
                    print("Jumlah tidak valid.")
            except ValueError:
                print("ID tagihan tidak valid.")

        elif pilihan == '9':
            tagihan_id = input("Masukkan ID tagihan yang akan ditandai sebagai dibayar: ")
            try:
                tagihan_id = int(tagihan_id)
                tagihan = smp.dapatkan_tagihan(tagihan_id)
                if not tagihan:
                    print("Tagihan tidak ditemukan.")
                    continue

                if tagihan[5] == "SUDAH DIBAYAR":
                    print("Tagihan ini sudah ditandai sebagai SUDAH DIBAYAR.")
                else:
                    smp.tandai_tagihan_sebagai_dibayar(tagihan_id)
                    print("Tagihan berhasil ditandai sebagai SUDAH DIBAYAR.")
            except ValueError:
                print("ID tagihan tidak valid.")

        elif pilihan == '10':
            tagihan_hari_ini = smp.dapatkan_tagihan_hari_ini()
            if not tagihan_hari_ini:
                print("Tidak ada tagihan jatuh tempo hari ini.")
            else:
                print("\n=== Tagihan Hari Ini ===")
                total = 0
                for t in tagihan_hari_ini:
                    print(f"ID Tagihan: {t[0]}, Pelanggan: {t[7]}, Jumlah: Rp{t[2]:.2f}, Status: {t[5]}")
                    if t[5] == "BELUM DIBAYAR":
                        total += t[2]
                print(f"\nTotal Jumlah Belum Dibayar Jatuh Tempo Hari Ini: Rp{total:.2f}")

        elif pilihan == '11':
            tagihan_belum_dibayar = smp.dapatkan_tagihan_belum_dibayar()
            if not tagihan_belum_dibayar:
                print("Tidak ada tagihan belum dibayar.")
            else:
                print("\n=== Tagihan Belum Dibayar ===")
                total = 0
                for t in tagihan_belum_dibayar:
                    print(f"ID Tagihan: {t[0]}, Pelanggan: {t[7]}, Jumlah: Rp{t[2]:.2f}, Jatuh Tempo: {t[4]}")
                    total += t[2]
                print(f"\nTotal Jumlah Belum Dibayar: Rp{total:.2f}")

        elif pilihan == '12':
            total_belum_dibayar = smp.dapatkan_total_tagihan_belum_dibayar()
            print(f"\nTotal Jumlah Belum Dibayar: Rp{total_belum_dibayar:.2f}")

        elif pilihan == '13':
            tanggal_str = input("Masukkan tanggal (YYYY-MM-DD): ")
            try:
                # Validasi format tanggal
                datetime.datetime.strptime(tanggal_str, "%Y-%m-%d")
                tagihan = smp.dapatkan_tagihan_berdasarkan_tanggal(tanggal_str)
                if not tagihan:
                    print(f"Tidak ada tagihan jatuh tempo pada {tanggal_str}.")
                else:
                    print(f"\n=== Tagihan untuk {tanggal_str} ===")
                    total = 0
                    for t in tagihan:
                        print(f"ID Tagihan: {t[0]}, Pelanggan: {t[7]}, Jumlah: Rp{t[2]:.2f}, Status: {t[5]}")
                        if t[5] == "BELUM DIBAYAR":
                            total += t[2]
                    print(f"\nTotal Jumlah Belum Dibayar Jatuh Tempo pada {tanggal_str}: Rp{total:.2f}")
            except ValueError:
                print("Format tanggal tidak valid. Gunakan YYYY-MM-DD.")

        elif pilihan == '14':
            pelanggan_id = input("Masukkan ID pelanggan untuk melihat di peta: ")
            try:
                pelanggan_id = int(pelanggan_id)
                sukses = smp.buka_lokasi_di_peta(pelanggan_id)
                if not sukses:
                    print("Tidak dapat membuka peta. Pelanggan tidak ditemukan atau tidak ada data lokasi.")
            except ValueError:
                print("ID pelanggan tidak valid.")

        elif pilihan == '0':
            break

        else:
            print("Pilihan tidak valid. Silakan coba lagi.")

if __name__ == "__main__":
    # Periksa apakah ingin menjalankan dalam mode web atau CLI
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        cli_mode()
    else:
        print("Menjalankan server web...")
        # Jalankan mode web - gunakan 0.0.0.0 untuk bisa diakses dari luar
        app.run(host='0.0.0.0', port=8080, debug=True)
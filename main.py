from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

app = FastAPI()

# Izinkan dashboard (frontend) mengakses API ini dari browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Konfigurasi kunci brankas MySQL
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "db_maintenance"
} 

# 1. Cek apakah server menyala
@app.get("/")
def cek_server():
    return {"pesan": "Halo! Server Backend Aktif dan Siap Melayani!"}

# 2. Cek apakah Python bisa masuk ke MySQL
@app.get("/cek-database")
def cek_database():
    try:
        koneksi = mysql.connector.connect(**db_config)
        if koneksi.is_connected():
            koneksi.close()
            return {"status": "SUKSES", "pesan": "Selamat! Python berhasil masuk ke brankas MySQL."}
    except Exception as e:
        return {"status": "GAGAL", "pesan": f"Waduh, ada error: {e}"}


# 3. Ambil data sparepart
@app.get("/api/sparepart")
def ambil_data_sparepart():
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sparepart")
        hasil = cursor.fetchall()
        koneksi.close()
        return {"pesan": "Berhasil mengambil data", "data": hasil}
    except Exception as e:
        return {"pesan": "Gagal mengambil data sparepart", "error": str(e), "data": []}


# 4. Ambil data semua mesin
@app.get("/api/mesin")
def ambil_data_mesin():
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor(dictionary=True)
        cursor.execute("SELECT * FROM mesin")
        hasil = cursor.fetchall()
        koneksi.close()
        return {"pesan": "Berhasil mengambil data mesin", "data": hasil}
    except Exception as e:
        return {"pesan": "Gagal mengambil data mesin", "error": str(e), "data": []}


# 5. Ambil sparepart untuk 1 mesin tertentu (pakai JOIN biar nama-nya muncul, bukan angka)
@app.get("/api/mesin/{id_mesin}/sparepart")
def sparepart_per_mesin(id_mesin: int):
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor(dictionary=True)
        query = """
            SELECT s.nama_part, s.part_number, s.tingkat_kritikal,
                   ms.qty_terpasang, ms.posisi_manual
            FROM mesin_sparepart ms
            JOIN sparepart s ON ms.id_sparepart = s.id_sparepart
            WHERE ms.id_mesin = %s
        """
        cursor.execute(query, (id_mesin,))
        hasil = cursor.fetchall()
        koneksi.close()
        return {"pesan": "Berhasil mengambil sparepart mesin", "data": hasil}
    except Exception as e:
        return {"pesan": "Gagal mengambil sparepart mesin", "error": str(e), "data": []}


# 6. Ambil daftar part yang stoknya sudah di bawah/sama dengan minimum (buat alert dashboard)
@app.get("/api/stok/rendah")
def stok_menipis():
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor(dictionary=True)
        query = """
            SELECT s.nama_part, s.part_number, sg.qty_stok, sg.stok_minimum
            FROM stok_gudang sg
            JOIN sparepart s ON sg.id_sparepart = s.id_sparepart
            WHERE sg.qty_stok <= sg.stok_minimum
        """
        cursor.execute(query)
        hasil = cursor.fetchall()
        koneksi.close()
        return {"pesan": "Berhasil mengambil data stok menipis", "data": hasil}
    except Exception as e:
        return {"pesan": "Gagal mengambil data stok menipis", "error": str(e), "data": []}


# 7. Ambil daftar part dengan tingkat kritikal Tinggi (prioritas utama buat dashboard)
@app.get("/api/sparepart/kritikal")
def sparepart_kritikal():
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sparepart WHERE tingkat_kritikal = 'Tinggi'")
        hasil = cursor.fetchall()
        koneksi.close()
        return {"pesan": "Berhasil mengambil sparepart kritikal", "data": hasil}
    except Exception as e:
        return {"pesan": "Gagal mengambil sparepart kritikal", "error": str(e), "data": []}
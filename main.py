from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import os
from dotenv import load_dotenv

# Memuat file .env untuk konfigurasi rahasia
load_dotenv()

app = FastAPI()

# Izinkan dashboard (frontend) mengakses API ini dari browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Konfigurasi kunci brankas MySQL (mengambil data dari file .env)
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "db_maintenance")
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


# 8. Ambil daftar supplier
@app.get("/api/supplier")
def ambil_data_supplier():
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor(dictionary=True)
        cursor.execute("SELECT * FROM supplier")
        hasil = cursor.fetchall()
        koneksi.close()
        return {"pesan": "Berhasil mengambil data supplier", "data": hasil}
    except Exception as e:
        return {"pesan": "Gagal mengambil data supplier", "error": str(e), "data": []}


# 9. Ambil semua log downtime (join biar nama mesin muncul)
@app.get("/api/downtime")
def ambil_downtime():
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor(dictionary=True)
        query = """
            SELECT dl.id_downtime, m.nama_mesin, dl.tanggal, dl.durasi_jam,
                   dl.keterangan, dl.dicatat_oleh
            FROM downtime_log dl
            JOIN mesin m ON dl.id_mesin = m.id_mesin
            ORDER BY dl.tanggal DESC
        """
        cursor.execute(query)
        hasil = cursor.fetchall()
        koneksi.close()
        return {"pesan": "Berhasil mengambil data downtime", "data": hasil}
    except Exception as e:
        return {"pesan": "Gagal mengambil data downtime", "error": str(e), "data": []}


# 10. Ambil semua jadwal perawatan (join biar nama mesin muncul)
@app.get("/api/jadwal-perawatan")
def ambil_jadwal_perawatan():
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor(dictionary=True)
        query = """
            SELECT jp.id_jadwal, m.nama_mesin, jp.tanggal_perawatan,
                   jp.deskripsi, jp.status
            FROM jadwal_perawatan jp
            JOIN mesin m ON jp.id_mesin = m.id_mesin
            ORDER BY jp.tanggal_perawatan ASC
        """
        cursor.execute(query)
        hasil = cursor.fetchall()
        koneksi.close()
        return {"pesan": "Berhasil mengambil jadwal perawatan", "data": hasil}
    except Exception as e:
        return {"pesan": "Gagal mengambil jadwal perawatan", "error": str(e), "data": []}


# 11. Ambil jadwal yang jatuh BESOK (buat notifikasi H-1)
@app.get("/api/jadwal-perawatan/reminder")
def reminder_jadwal_besok():
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor(dictionary=True)
        query = """
            SELECT jp.id_jadwal, m.nama_mesin, jp.tanggal_perawatan, jp.deskripsi
            FROM jadwal_perawatan jp
            JOIN mesin m ON jp.id_mesin = m.id_mesin
            WHERE jp.tanggal_perawatan = DATE_ADD(CURDATE(), INTERVAL 1 DAY)
              AND jp.status = 'Terjadwal'
        """
        cursor.execute(query)
        hasil = cursor.fetchall()
        koneksi.close()
        return {"pesan": "Berhasil mengambil reminder jadwal besok", "data": hasil}
    except Exception as e:
        return {"pesan": "Gagal mengambil reminder", "error": str(e), "data": []}


# ---- Struktur data SESUAI yang dikirim frontend (mesin_id, part_number, qty, pic) ----
class PemakaianRequest(BaseModel):
    mesin_id: int
    part_number: str
    qty: int
    pic: str


# 12. Catat pemakaian part + otomatis kurangi stok gudang
@app.post("/api/pemakaian")
def catat_pemakaian(data: PemakaianRequest):
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor()

        # 0. Cari id_sparepart dari part_number yang dikirim frontend
        cursor.execute("SELECT id_sparepart FROM sparepart WHERE part_number = %s", (data.part_number,))
        row = cursor.fetchone()
        if row is None:
            koneksi.close()
            return {"pesan": f"Gagal: part_number '{data.part_number}' tidak ditemukan di database"}
        id_sparepart = row[0]

        # 1. Simpan riwayat pemakaian
        cursor.execute(
            """
            INSERT INTO riwayat_pemakaian (id_mesin, id_sparepart, tanggal, qty_terpakai, dicatat_oleh)
            VALUES (%s, %s, CURDATE(), %s, %s)
            """,
            (data.mesin_id, id_sparepart, data.qty, data.pic)
        )

        # 2. Kurangi stok fisik di stok_gudang
        cursor.execute(
            "UPDATE stok_gudang SET qty_stok = qty_stok - %s WHERE id_sparepart = %s",
            (data.qty, id_sparepart)
        )

        koneksi.commit()
        koneksi.close()
        return {"pesan": "Berhasil mencatat pemakaian part dan mengurangi stok"}
    except Exception as e:
        return {"pesan": "Gagal mencatat pemakaian", "error": str(e)}


# ---- Struktur data sesuai yang dikirim frontend (mesin_id, durasi_jam, keterangan, pic) ----
class DowntimeRequest(BaseModel):
    mesin_id: int
    durasi_jam: float
    keterangan: str
    pic: str


# 13. Catat downtime baru dari dashboard
@app.post("/api/downtime")
def catat_downtime(data: DowntimeRequest):
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor()

        cursor.execute(
            """
            INSERT INTO downtime_log (id_mesin, tanggal, durasi_jam, keterangan, dicatat_oleh)
            VALUES (%s, CURDATE(), %s, %s, %s)
            """,
            (data.mesin_id, data.durasi_jam, data.keterangan, data.pic)
        )

        koneksi.commit()
        koneksi.close()
        return {"pesan": "Berhasil mencatat downtime"}
    except Exception as e:
        return {"pesan": "Gagal mencatat downtime", "error": str(e)}


# ---- Struktur data yang dikirim frontend saat submit form "Tambah Supplier" ----
class SupplierRequest(BaseModel):
    nama_supplier: str
    kontak: str
    email: str = None
    alamat: str = None


# 14. Tambah data supplier baru dari dashboard
@app.post("/api/supplier")
def tambah_supplier(data: SupplierRequest):
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor()

        cursor.execute(
            """
            INSERT INTO supplier (nama_supplier, kontak, email, alamat)
            VALUES (%s, %s, %s, %s)
            """,
            (data.nama_supplier, data.kontak, data.email, data.alamat)
        )

        koneksi.commit()
        koneksi.close()
        return {"pesan": "Berhasil menambahkan supplier baru"}
    except Exception as e:
        return {"pesan": "Gagal menambahkan supplier", "error": str(e)}


# ---- Struktur data update jadwal perawatan ----
class UpdateJadwalRequest(BaseModel):
    tanggal_aktual: str  # Format: "YYYY-MM-DD"
    status: str          # Contoh: 'Selesai'


# 15. Update jadwal perawatan saat dikerjakan (mengisi tanggal aktual & ubah status jadi Selesai)
@app.put("/api/jadwal-perawatan/{id_jadwal}")
def update_jadwal_perawatan(id_jadwal: int, data: UpdateJadwalRequest):
    try:
        koneksi = mysql.connector.connect(**db_config)
        cursor = koneksi.cursor()

        cursor.execute(
            """
            UPDATE jadwal_perawatan 
            SET tanggal_perawatan = %s, status = %s 
            WHERE id_jadwal = %s
            """,
            (data.tanggal_aktual, data.status, id_jadwal)
        )

        koneksi.commit()
        koneksi.close()
        return {"pesan": "Berhasil memperbarui jadwal perawatan dan mencatat tanggal aktual"}
    except Exception as e:
        return {"pesan": "Gagal memperbarui jadwal perawatan", "error": str(e)}
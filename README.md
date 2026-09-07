# 🏭 Backend Maintenance & Sparepart Management - PT Mirota KSM

Sistem *backend* berbasis REST API yang dikembangkan untuk manajemen data *sparepart* dan pemeliharaan mesin di lingkungan operasional **PT Mirota KSM**. Proyek ini dibangun sebagai bagian dari program Magang dan Studi Independen Bersertifikat (MBKM).

---

## 🛠️ Tech Stack & Architecture
* **Language:** Python 3.7+
* **Framework:** FastAPI (High-performance async API)
* **Database:** MySQL (Hosted locally via XAMPP)
* **Database Driver:** `mysql-connector-python`
* **Tunneling / Deployment:** Cloudflare Tunnel (untuk akses publik yang aman secara *real-time*)

---

## 👥 Tim Kolaborasi (Fullstack Integration)
Proyek ini dikembangkan secara kolaboratif dengan pembagian peran *fullstack*:
* **Backend & Database:** [Sanjehaqi] ([Repository Backend Ini](https://github.com/Sanjehaqi/backend-maintenance-mirota))
* **Frontend Dashboard:** [setdans] ([Repository Frontend](https://github.com/username-teman/repository-frontend))
* **Live Web App:** [Dashboard Vercel Utama](https://dashboard-mirota.vercel.app)

---

## 📂 Struktur Direktori Proyek
```text
Backend-Maintenance/
│
├── main.py                 # Berkas utama FastAPI & konfigurasi Endpoint API
├── import_data.sql         # Skema dan *dump* database MySQL PT Mirota KSM
├── .gitignore              # Konfigurasi file yang diabaikan oleh Git
└── README.md               # Dokumentasi proyek

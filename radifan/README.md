# ⚙️ Radifan (Backend Developer)

Halo! Saya **Radifan**, berposisi sebagai **Backend Developer** pada proyek CVMatch AI (CV-Analyser) ini. 

Folder ini merupakan ruang kerja untuk komponen *backend* yang saya kembangkan. Tanggung jawab utama saya mencakup pengelolaan arsitektur penyimpanan data (Database) dan integrasi layanan API eksternal (AI Chatbot).

## 📄 Ruang Lingkup & File Utama

### 1. Arsitektur Data & Source of Truth
Bekerja sama dengan modul Scraper, saya mengatur *data pipelining* agar data yang diproses tersimpan dengan aman menggunakan **SQLite** sebagai *Source of Truth* (Layer 3).
- **`source_of_truth.db`**: File database utama (yang akan ter-generate otomatis saat pipeline dijalankan) disimpan dengan aman di direktori ini untuk digunakan oleh sistem inti. Mencegah adanya duplikasi data lowongan pekerjaan (*Job Recommendations*).

### 2. Integrasi AI Chatbot (RAG)
- **`chatbot_rag.py`**: Modul yang memuat fungsi-fungsi *backend* untuk menginisialisasi dan berinteraksi secara mulus dengan API Google Gemini (`gemini-flash-latest`).

## 🧠 Cara Kerja Chatbot RAG (Retrieval-Augmented Generation)

Sistem chatbot ini dirancang di sisi *backend* secara khusus untuk berperan sebagai **Asisten Karir Profesional**. Modul ini menyuntikkan *contextual data* (data spesifik pengguna) ke dalam *prompt* sebelum dikirimkan ke model AI.

Data konteks yang digunakan meliputi:
1. **Data CV Pengguna**: Nama, Pendidikan, Pengalaman, dan *Skills* yang terdeteksi.
2. **Data Lowongan Pekerjaan**: Posisi pekerjaan, nama perusahaan, persentase kecocokan (*match score*), dan *Skill Gap*.

### 🛡️ Keamanan API & Batasan Prompt (System Instructions)
Sebagai *Backend Developer*, saya memastikan titik akses AI aman melalui penerapan *System Prompt* yang ketat:
- **Prompt Injection**: Menolak manipulasi *user* yang menyuruh AI mengabaikan instruksi (misalnya "abaikan instruksi sebelumnya").
- **Topik Non-Relevan (Out of Context)**: Chatbot hanya akan merespons pertanyaan seputar karir, CV, lowongan pekerjaan, persiapan wawancara, dan strategi belajar. Apabila pengguna menanyakan hal di luar itu (misal: cuaca, resep masakan), *backend* akan menginstruksikan AI untuk menolak dengan sopan.

## 📦 Dependensi (*Requirements*)

Modul *backend* ini sangat bergantung pada pustaka berikut:
- `sqlite3`: Modul bawaan Python untuk pengolahan Database lokal.
- `google-generativeai`: SDK resmi untuk memanggil Google Gemini API.
- `python-dotenv`: Untuk memuat dan melindungi variabel *environment* lokal (seperti `GEMINI_API_KEY`).

Pastikan kunci `GEMINI_API_KEY` telah disetel di dalam file `.env` yang berada di direktori root aplikasi sebelum menjalankan fitur percakapan.

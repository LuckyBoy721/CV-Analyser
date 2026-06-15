# 🤖 Radifan (Chatbot RAG)

Folder ini berisi implementasi sistem **Chatbot AI Berbasis RAG (Retrieval-Augmented Generation)** yang menjadi inti dari fitur asisten karir (CVMatch AI) pada aplikasi CV-Analyser.

## 📄 File Utama

- **`chatbot_rag.py`**: Modul utama yang memuat fungsi-fungsi untuk berinteraksi dengan API Google Gemini (`gemini-flash-latest`). 

## ⚙️ Cara Kerja

Sistem ini dirancang secara khusus untuk berperan sebagai **Asisten Karir Profesional**. Modul ini menyuntikkan *contextual data* (data spesifik pengguna) ke dalam *prompt* sebelum dikirimkan ke model AI.

Data konteks yang digunakan meliputi:
1. **Data CV Pengguna**: Nama, Pendidikan, Pengalaman, dan *Skills* yang terdeteksi.
2. **Data Lowongan Pekerjaan (Job Recommendation)**: Posisi pekerjaan, nama perusahaan, persentase kecocokan (*match score*), dan *Skill Gap*.

### 🛡️ Keamanan & Batasan Prompt (System Instructions)
Modul ini dilindungi dengan *System Prompt* yang sangat ketat untuk mencegah:
- **Prompt Injection**: Menolak manipulasi pengguna yang menyuruh AI mengabaikan instruksi atau merubah persona.
- **Topik Non-Relevan (Out of Context)**: Chatbot hanya akan merespons pertanyaan seputar karir, CV, lowongan pekerjaan, persiapan wawancara, dan strategi belajar. Apabila pengguna menanyakan hal lain (misal: cuaca, politik, resep masakan), sistem akan merespons dengan penolakan yang sopan.

## 📦 Dependensi (Requirements)

Modul ini memerlukan beberapa pustaka eksternal:
- `google-generativeai`: Untuk memanggil Google Gemini API.
- `python-dotenv`: Untuk memuat variabel *environment* (seperti `GEMINI_API_KEY`).

Pastikan kunci `GEMINI_API_KEY` telah disetel di dalam file `.env` (untuk pengembangan lokal) atau di *Streamlit Secrets* (untuk *deployment*).

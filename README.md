# CVMatch AI - CV Analyzer & Job Recommendation System

CVMatch AI adalah aplikasi berbasis kecerdasan buatan (NLP & Machine Learning) untuk menganalisis dokumen CV (dalam format PDF) dan mencocokkannya dengan database lowongan pekerjaan (*Job Recommendations*) menggunakan berbagai model *semantic similarity*.

Aplikasi ini menggabungkan pekerjaan dari berbagai pipeline modul:
1. **`alin/`**: Pemrosesan & Parsing CV (Ekstraksi entitas teks & skill menggunakan NLP).
2. **`edo/`**: Scraping data lowongan pekerjaan & pembersihan data (*Job Scraper & Preprocessor*).
3. **`dimas/`**: Evaluasi model *Machine Learning* & implementasi algoritma kemiripan teks.
4. **`sintya/`**: Antarmuka visual Dashboard Streamlit (Desain B & Desain D).
5. **`radifan/`**: Modul integrasi AI Chatbot berbasis RAG (Retrieval-Augmented Generation) menggunakan Google Gemini AI.

---

## 📁 Struktur Direktori Utama

```text
CV-Analyser/
├── alin/                      # Modul Ekstraksi & Parsing CV
│   ├── cv_parser.py           # Script ekstraksi teks & entitas PDF
│   └── cv_preprocessor.py     # Script pembersihan teks & translasi
├── dimas/                     # Modul Machine Learning & Benchmark
│   ├── data/database/         # Dataset benchmark model ML
│   ├── models/                # Folder penyimpanan model offline (SBERT)
│   ├── run_evaluation.sh      # Skrip benchmark model ML interaktif
│   └── model_*.py             # Source code variasi algoritma ML
├── edo/                       # Modul Scraping & Preprocessor Lowongan
│   ├── data/                  # Dataset lowongan hasil scraping
│   ├── job_scraper.py         # Script scraper lowongan Jobstreet
│   └── run_job_analyzer.sh    # Script pipeline scraping-preprocessing
├── sintya/                    # Antarmuka Dashboard Streamlit
│   ├── desain_B.py            # Desain UI Terang & Bersih
│   └── desain_D.py            # Desain UI Elegan Merah-Gelap
├── run_app.sh                 # [Utama] Script sekali klik untuk menjalankan UI
└── README.md                  # Dokumentasi proyek ini
```

---

## ⚙️ Persyaratan Sistem & Instalasi

Proyek ini menggunakan virtual environment Python dan direkomendasikan menggunakan `uv` untuk instalasi dependensi yang super cepat.

### 1. Kloning Repositori & Masuk ke Folder
```bash
git clone https://github.com/LuckyBoy721/CV-Analyser.git
cd CV-Analyser
```

### 2. Membuat Virtual Environment (Rekomendasi)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Menginstal Dependensi
Gunakan `uv` untuk menginstal seluruh paket dengan cepat. Jika belum memiliki `uv`, silakan pasang terlebih dahulu (`pip install uv`).

```bash
uv pip install -r requirements.txt
```
*Catatan: Jika file `requirements.txt` belum tersedia, instal paket utama berikut:*
```bash
uv pip install streamlit pandas plotly scikit-learn sentence-transformers torchvision requests beautifulsoup4 deep-translator nltk tqdm matplotlib google-generativeai python-dotenv
```

### 4. Konfigurasi API Key (Untuk Fitur Chatbot RAG)
Aplikasi ini memiliki fitur Chatbot RAG berbasis Google Gemini AI. Anda diwajibkan untuk menyediakan API Key Google AI Studio.
1. Salin file `.env.example` menjadi `.env`:
   ```bash
   cp .env.example .env
   ```
2. Buka file `.env` dan masukkan API Key Anda:
   ```env
   GEMINI_API_KEY=AQ.xxxxxx_API_Key_Anda_Di_Sini_xxxxxxx
   ```
*(Catatan: Mulai pertengahan 2026, Google merilis format API Key baru berawalan `AQ.`. API Key dengan awalan `AIzaSy` adalah format lama yang mungkin sudah usang).*

---

## 🚀 Cara Menjalankan Aplikasi

### A. Aplikasi Utama (Dashboard Interaktif)
Kami menyediakan skrip launcher `./run_app.sh` untuk memudahkan pemilihan tampilan.

1. Berikan izin eksekusi pada skrip (jika belum):
   ```bash
   chmod +x run_app.sh
   ```
2. Jalankan skrip:
   ```bash
   ./run_app.sh
   ```
3. Pilih desain antarmuka di terminal:
   * Ketik **`1`** untuk membuka **Desain B** (Tampilan Terang & Bersih).
   * Ketik **`2`** untuk membuka **Desain D** (Tampilan Gelap Elegan dengan nuansa Merah).
4. Browser Anda akan terbuka secara otomatis di alamat `http://localhost:8501` atau `http://localhost:8502`.

### B. Modul Evaluasi & Benchmark ML (Modul `dimas/`)
Untuk menjalankan benchmarking dan mengukur presisi antar model (`TF-IDF`, `TF-IDF + SVD`, `Embedding SBERT`):
```bash
cd dimas
chmod +x run_evaluation.sh
./run_evaluation.sh
```

### C. Modul Scraping Lowongan Baru (Modul `edo/`)
Untuk memperbarui data lowongan pekerjaan menggunakan scraping terbaru:
```bash
cd edo
chmod +x run_job_analyzer.sh
./run_job_analyzer.sh
```
Hasil scraping akan otomatis diperbarui ke database `edo/data/data_clean.csv` yang langsung digunakan sebagai basis data rekomendasi di aplikasi utama.

---

## 🧠 Model Rekomendasi yang Tersedia
Aplikasi ini menyediakan 3 model pembanding kemiripan teks:
1. **TF-IDF (Baseline)**: Pencocokan berbasis kata kunci literal (cepat, efisien).
2. **TF-IDF + SVD**: Representasi dimensi laten untuk menemukan pola hubungan kata yang tersembunyi.
3. **Sentence Embedding (SBERT)**: Memahami makna semantik bahasa secara mendalam (misal: "ML" dicocokkan dengan "Machine Learning" secara otomatis). Model ini disimpan secara offline di folder lokal `dimas/models/all-MiniLM-L6-v2` setelah diunduh pertama kali.


# Job Scraper Pipeline (Edo's Workspace)

Direktori ini berisi *pipeline* otomatis untuk melakukan *scraping* lowongan pekerjaan dari JobStreet dan melakukan pemrosesan data (NLP text cleaning, translation, TF-IDF preparation) untuk pemodelan Machine Learning.

## 📂 Struktur Folder & File
* `job_scraper.py`: *Script* web scraper untuk mengambil data (Posisi, Perusahaan, Lokasi, Type, Gaji, Requirements) dari JobStreet.
* `job_preprocessor.py`: *Script* untuk membersihkan teks, menerjemahkan ke bahasa Inggris, menyeimbangkan distribusi kategori (*balancing*), dan menyiapkan teks untuk TF-IDF & Embedding.
* `run_job_analyzer.sh`: *Shell script* interaktif untuk mempermudah eksekusi keseluruhan *pipeline*.
* `dataset.csv`: Data mentah hasil dari proses *scraping*.
* `data_clean.csv`: Data bersih yang sudah di- *preprocess* dan siap digunakan untuk pemodelan ML.

## 🚀 Cara Penggunaan

Sangat disarankan untuk menggunakan *shell script* utama untuk menjalankan proses ini. Script ini secara otomatis menangani *virtual environment* dan seluruh dependensi menggunakan `uv`.

1. Buka terminal dan masuk ke direktori `edo`:
   ```bash
   cd edo/
   ```
2. Pastikan file *shell script* bisa dieksekusi (hanya butuh sekali):
   ```bash
   chmod +x run_job_analyzer.sh
   ```
3. Jalankan *script* utama:
   ```bash
   ./run_job_analyzer.sh
   ```
4. Ikuti menu interaktif yang tersedia:
   * **[1] Jalankan Scraper Saja (Tahap 1)**: Mengumpulkan lowongan kerja baru. Anda akan diminta memasukkan rentang halaman (contoh: halaman 1 sampai 5).
   * **[2] Jalankan Preprocessor Saja (Tahap 2)**: Membersihkan data mentah dari `dataset.csv` dan menghasilkan `data_clean.csv`.
   * **[3] Jalankan Semua (Pipeline Penuh)**: Melakukan *scraping* lalu otomatis melakukan *preprocessing*.

## ⚙️ Persyaratan Sistem
Sama seperti *pipeline* lainnya, pastikan Anda telah memiliki `python3` di sistem. Dependensi Python seperti `pandas`, `beautifulsoup4`, `requests`, `nltk`, dan `deep-translator` akan diinstal otomatis oleh *script*.

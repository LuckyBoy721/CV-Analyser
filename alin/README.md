# CV Analyzer Pipeline (Alin's Workspace)

Direktori ini berisi *pipeline* otomatis untuk melakukan ekstraksi, pemrosesan, dan analisis data CV (Curriculum Vitae) berformat PDF untuk kebutuhan pemodelan Machine Learning.

## 📂 Struktur Folder & File
* `cv_folder/`: Direktori yang berisi file-file PDF CV mentah yang akan diproses.
* `result/`: Direktori tempat menyimpan hasil akhir dari proses (*generate* otomatis).
* `cv_parser.py`: *Script* untuk mengekstrak informasi (Nama, Email, Telepon, Skills, dll) dari file PDF CV.
* `cv_preprocessor.py`: *Script* untuk membersihkan, menerjemahkan, menyeimbangkan, dan mengkategorikan data CV.
* `run_cv_analyzer.sh`: *Shell script* interaktif untuk menjalankan keseluruhan *pipeline* dengan mudah.

## 🚀 Cara Penggunaan

Gunakan *shell script* yang sudah disediakan. Script ini akan secara otomatis membuat *virtual environment* (`.venv`), menginstal semua dependensi yang diperlukan menggunakan `uv`, dan menjalankan prosesnya.

1. Buka terminal dan masuk ke direktori `alin`:
   ```bash
   cd alin/
   ```
2. Jalankan *script* utama:
   ```bash
   ./run_cv_analyzer.sh
   ```
3. Ikuti menu interaktif yang muncul di layar:
   * **[1] Jalankan Tahap 1 saja (CV Parser)**: Mengekstrak teks dari PDF di `cv_folder/` dan menyimpan ke `result/parsed_cv_final.csv`.
   * **[2] Jalankan Tahap 2 saja (CV Preprocessor)**: Memproses hasil ekstraksi dan menyimpan data bersih ke `result/hasil_scan_cv_parse.csv`.
   * **[3] Jalankan Semuanya (Pipeline Penuh)**: Menjalankan Tahap 1 berlanjut ke Tahap 2.

## ⚙️ Persyaratan Sistem
Pastikan Anda telah menginstal `python3` dan disarankan menginstal `uv` (Package manager Python yang sangat cepat). Jika `uv` belum terinstal, *script* `.sh` akan mencoba untuk melakukan instalasi secara otomatis.

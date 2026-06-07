# CV Parser & Preprocessor Pipeline

Folder ini berisi sekumpulan skrip dan *Jupyter Notebook* yang berfungsi untuk mengekstrak informasi dari Curriculum Vitae (CV) berformat PDF, memproses teksnya, dan mengkategorikannya berdasarkan bidang pekerjaan untuk keperluan *Machine Learning*.

## 📂 Struktur File

- **`cv_parser.py`**  
  Skrip utama untuk mengekstrak teks dari file PDF CV. Skrip ini secara otomatis menarik informasi penting seperti Nama, Email, Nomor Telepon, Pendidikan, Pengalaman, dan *Skills*. Skrip ini juga menerjemahkan teks ke bahasa Inggris dan menyimpannya dalam format CSV (`parsed_cv_final.csv`).
  
- **`cv_preprocessor.py`**  
  Skrip lanjutan untuk memproses data hasil ekstrak. Melakukan pembersihan *missing value*, klasifikasi bidang pekerjaan (seperti *Data*, *Software*, *Marketing*, dll) berdasarkan kata kunci, *balancing dataset*, *stopword removal* dengan NLTK, dan penyiapan teks untuk pembentukan model (TF-IDF & Embeddings). Hasil akhirnya disimpan sebagai `hasil_scan_cv_parse.csv`.

- **`cv parser.ipynb`** & **`prepro copy.ipynb`**  
  Versi asli (*raw*) dari alur kerja ekstraksi dan *preprocessing* dalam bentuk *Jupyter Notebook* yang digunakan pada tahap eksperimen/analisis awal.

## 🛠️ Persyaratan (*Requirements*)

Pastikan Anda telah menginstal beberapa pustaka (*libraries*) Python berikut sebelum menjalankan skrip:

```bash
pip install PyPDF2 deep-translator pandas tqdm nltk
```

*Catatan: Saat pertama kali dijalankan, skrip `cv_preprocessor.py` akan mengunduh paket `stopwords` dari NLTK secara otomatis jika belum ada.*

## 🚀 Cara Menjalankan

### 1. Tahap Ekstraksi (Parsing)

Buatlah sebuah folder bernama `cv_folder` di dalam direktori ini, dan letakkan seluruh file PDF CV yang ingin diproses di dalamnya. Setelah itu, jalankan:

```bash
python cv_parser.py
```
**Output**: File `parsed_cv_final.csv` yang memuat teks mentah yang telah dipisah per entitas (Skills, Education, dll) beserta hasil terjemahannya.

### 2. Tahap Pemrosesan Teks (Preprocessing & Klasifikasi)

Setelah file `parsed_cv_final.csv` berhasil digenerate dari proses sebelumnya, Anda bisa melanjutkan ke tahap pembersihan dan klasifikasi:

```bash
python cv_preprocessor.py
```
**Output**: File akhir `hasil_scan_cv_parse.csv` (atau yang sudah ditentukan di kode) yang telah berisi kategori pekerjaan, serta kolom teks yang sudah di-*clean* dan siap dimasukkan ke model (misal: kolom `text_for_tfidf`).

## 📊 Alur Data (Data Flow)

1. `*.pdf` (Input Kumpulan CV) 
2. ➡️ Ditarik teks & infonya oleh `cv_parser.py` 
3. ➡️ `parsed_cv_final.csv` 
4. ➡️ Dibersihkan & diklasifikasi oleh `cv_preprocessor.py` 
5. ➡️ `hasil_scan_cv_parse.csv` (Dataset siap pakai untuk *Machine Learning*).

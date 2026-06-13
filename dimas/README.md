# Modul Evaluasi Model (Dimas)

Direktori ini berisi skrip dan *Jupyter Notebook* (`Untitled0.ipynb`) yang digunakan khusus untuk melakukan eksperimen, *benchmarking*, dan evaluasi algoritma pencocokan (Similarity Models) antara *Curriculum Vitae* (CV) dengan Lowongan Pekerjaan (Jobs).

## 📌 Cara Kerja
Notebook ini menjalankan *pipeline* evaluasi sebagai berikut:
1. **Memuat Data**: Membaca dataset sampel CV (`sample_100_cv_with_ground_truth.csv`) yang telah dilengkapi dengan *ground truth* (pekerjaan yang secara manual/logika dianggap relevan) dan dataset pekerjaan bersih (`data_clean.csv`).
2. **Menjalankan Algoritma**: Mengukur *Cosine Similarity* menggunakan 4 pendekatan berbeda:
   - TF-IDF murni
   - TF-IDF + Truncated SVD (Reduksi dimensi laten)
   - Sentence Embeddings (Sentence-BERT / `all-MiniLM-L6-v2`) tanpa tanda baca
   - Sentence Embeddings dengan tanda baca
3. **Mengekstrak Top-K**: Mengambil 5 rekomendasi teratas (`Top-5`) yang dihasilkan oleh setiap model.
4. **Validasi Semantik**: Menggunakan model lintas bahasa (`paraphrase-multilingual-MiniLM-L12-v2`) untuk mencocokkan *ground truth* dengan hasil prediksi dari setiap model guna menentukan apakah rekomendasinya relevan (melewati *threshold* batas kemiripan tertentu).
5. **Perhitungan Metrik**: Menghitung **`Precision@5`** rata-rata dari setiap algoritma untuk menentukan algoritma manakah yang paling akurat dalam merekomendasikan lowongan pekerjaan.

## 📁 Struktur Direktori
- `Untitled0.ipynb`: Skrip Jupyter Notebook utama tempat *benchmarking* model dijalankan.
- `*.csv`: File-file dataset sementara yang digunakan khusus untuk proses sampel, *testing*, dan pencarian *ground truth*. (Diabaikan oleh Git untuk menghemat ruang).

## 🚀 Penggunaan
Modul ini biasanya dijalankan menggunakan Jupyter Notebook atau Google Colab (mengingat proses *embedding* dengan `sentence-transformers` membutuhkan sumber daya komputasi yang cukup berat atau GPU). Pastikan path dataset dikonfigurasi ke subdirektori data yang benar saat Anda menjalankannya secara lokal.

📢 PANDUAN PENGGUNAAN GITHUB KELOMPOK (CV ANALYSER) 📢

Halo rek! Repository GitHub untuk proyek Capstone CV Analyzer kita sudah siap dan terstruktur. 
Untuk menghindari bentrok kode (merge conflict), kita akan menggunakan sistem 1 Repository dengan branch berbeda, DAN setiap orang memiliki FOLDER KHUSUS sesuai nama masing-masing di dalam proyek.

Nama Repository: LuckyBoy721/CV-Analyser
Branch Utama Kolaborasi: development

⚠️ ATURAN EMAS KELOMPOK:
1. JANGAN PERNAH push langsung ke branch 'main' atau 'development'.
2. Kerja HANYA di dalam folder dengan nama kalian masing-masing.
3. Penggabungan kode ke branch 'development' wajib lewat Pull Request (PR) di web GitHub.

------------------------------------------------------------------

🛠️ LANGKAH AWAL (Hanya Dilakukan Sekali di Awal)

Buka terminal (Linux/Mac) atau Git Bash/Command Prompt (Windows) kalian, lalu jalankan perintah ini berurutan:

1. Clone repository ke komputer kalian:
   git clone https://github.com/LuckyBoy721/CV-Analyser.git
   cd CV-Analyser

2. Ambil semua branch dari GitHub dan pindah ke branch development:
   git fetch origin
   git checkout development

3. Buat branch fitur baru SESUAI ROLE kalian masing-masing:
   
   • Alin (NLP Engineer):
     git checkout -b feature/nlp-processing
   
   • Dimas (ML Engineer):
     git checkout -b feature/ml-modeling
   
   • Edo (Data Engineer):
     git checkout -b feature/data-pipeline
   
   • Sintya (Frontend Engineer):
     git checkout -b feature/frontend-ui

------------------------------------------------------------------

💻 ALUR KERJA HARIAN (Setiap Kali Kalian Coding)

1. Pastikan kalian berada di branch fitur kalian masing-masing (bukan development/main).
2. Buka teks editor (VS Code, dll) di folder proyek.
3. Koding HANYA di dalam folder nama kalian sendiri:
   Contoh: Alin hanya utak-atik file di folder /alin, Sintya di folder /sintya, dst.

4. Jika sudah selesai koding dan ingin menyimpan progres ke GitHub:
   git add .
   git commit -m "feat: [tulis deskripsi singkat fitur yang kalian buat]"
   git push -u origin [nama-branch-fitur-kalian]
   
   (Contoh push Sintya: git push -u origin feature/frontend-ui)

5. Setelah push sukses, buka web GitHub (https://github.com/LuckyBoy721/CV-Analyser).
6. Klik tombol hijau "Compare & pull request".
7. PENTING: Pastikan arah panah penggabungannya adalah:
   base: development  <--  compare: [branch-fitur-kalian]
8. Klik "Create pull request". Nanti kita review bareng-bareng sebelum di-merge ke development.

------------------------------------------------------------------

🔄 CARA MENGAMBIL UPDATE KODE TERBARU DARI TEMAN (Lakukan Tiap Hari)

Agar folder nama teman kalian muncul atau terupdate di laptop kalian setelah kodenya di-merge, lakukan ini sebelum mulai koding:

git checkout development
git pull origin development
git checkout [branch-fitur-kalian]
git merge development

------------------------------------------------------------------
Jika ada kendala saat instalasi atau eror Git (terutama masalah pengisian token/password GitHub), langsung chat di grup ini ya! Semangat rek proyekan kita! 🚀

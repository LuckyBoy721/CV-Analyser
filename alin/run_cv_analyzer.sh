#!/bin/bash

# Pindah ke direktori tempat script berada
cd "$(dirname "$0")"

# Konfigurasi Warna
RED='\037[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${CYAN}"
cat << "EOF"
  ______     __       _                _                     
 / ___\ \   / /      / \   _ __   __ _| |_   _ _______ _ __  
| |    \ \ / /_____ / _ \ | '_ \ / _` | | | | |_  / _ \ '__| 
| |___  \ V /|_____/ ___ \| | | | (_| | | |_| |/ /  __/ |    
 \____|  \_/      /_/   \_\_| |_|\__,_|_|\__, /___\___|_|    
                                         |___/               
EOF
echo -e "${NC}"
echo -e "${YELLOW}=====================================================${NC}"
echo -e "${GREEN}      Selamat Datang di CV Analyzer Pipeline!      ${NC}"
echo -e "${YELLOW}=====================================================${NC}\n"

# Fungsi untuk memeriksa Python, uv, dan mengatur venv
check_requirements() {
    echo -e "${BLUE}[*] Mempersiapkan environment...${NC}"
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}[!] Python3 tidak ditemukan. Silakan install Python3 terlebih dahulu.${NC}"
        exit 1
    fi

    # Mengecek keberadaan uv
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}[!] 'uv' tidak ditemukan. Menginstal 'uv' secara global...${NC}"
        # Instalasi uv jika belum ada (opsional pakai pip/curl)
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi

    # Membuat venv menggunakan uv jika folder .venv belum ada
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}[*] Membuat Virtual Environment (.venv) menggunakan uv...${NC}"
        uv venv
    else
        echo -e "${GREEN}[✔] Virtual Environment sudah ada.${NC}"
    fi

    # Mengaktifkan venv
    echo -e "${BLUE}[*] Mengaktifkan Virtual Environment...${NC}"
    source .venv/bin/activate

    # Menginstal package secara super cepat dengan uv pip
    echo -e "${YELLOW}[*] Menginstal / memastikan dependencies dengan uv...${NC}"
    uv pip install PyPDF2 deep-translator pandas tqdm nltk pdf2image pytesseract

    # Memastikan stopwords NLTK terunduh
    python3 -c "import nltk; nltk.download('stopwords', quiet=True)" 2>/dev/null
    
    echo -e "${GREEN}[✔] Semua dependencies di venv sudah terinstal dan siap digunakan.${NC}\n"
}

run_parser() {
    echo -e "${CYAN}=====================================================${NC}"
    echo -e "${YELLOW}🚀 TAHAP 1: Mengekstrak Teks dari PDF (CV Parsing)   ${NC}"
    echo -e "${CYAN}=====================================================${NC}"
    if [ ! -d "cv_folder" ] || [ -z "$(ls -A cv_folder/*.pdf 2>/dev/null)" ]; then
        echo -e "${RED}[!] Peringatan: Folder 'cv_folder' tidak ditemukan atau kosong.${NC}"
        echo -e "${YELLOW}[!] Buat folder 'cv_folder' dan masukkan file PDF CV ke dalamnya terlebih dahulu.${NC}"
    else
        python3 cv_parser.py
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[✔] Parsing CV Selesai!${NC}\n"
        else
            echo -e "${RED}[!] Terjadi kesalahan saat melakukan parsing.${NC}\n"
            exit 1
        fi
    fi
}

run_preprocessor() {
    echo -e "${CYAN}=====================================================${NC}"
    echo -e "${YELLOW}⚙️  TAHAP 2: Pemrosesan & Klasifikasi (Preprocessing) ${NC}"
    echo -e "${CYAN}=====================================================${NC}"
    if [ ! -f "result/parsed_cv_final.csv" ]; then
        echo -e "${RED}[!] File 'result/parsed_cv_final.csv' belum ada.${NC}"
        echo -e "${YELLOW}[!] Jalankan Tahap 1 (Parsing) terlebih dahulu.${NC}"
    else
        python3 cv_preprocessor.py
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[✔] Preprocessing Selesai! Data siap digunakan untuk Machine Learning.${NC}\n"
        else
            echo -e "${RED}[!] Terjadi kesalahan saat preprocessing.${NC}\n"
            exit 1
        fi
    fi
}

# Mengeksekusi pemeriksaan dan setup venv
check_requirements

# Menu Interaktif
echo -e "Silakan pilih proses yang ingin dijalankan:"
echo -e "  ${CYAN}[1]${NC} Jalankan Tahap 1 saja (CV Parser)"
echo -e "  ${CYAN}[2]${NC} Jalankan Tahap 2 saja (CV Preprocessor)"
echo -e "  ${CYAN}[3]${NC} Jalankan Semuanya (Pipeline Penuh)"
echo -e "  ${CYAN}[4]${NC} Keluar"
echo -n -e "\n${YELLOW}Pilihan Anda (1/2/3/4): ${NC}"
read choice

echo ""

case $choice in
    1)
        run_parser
        ;;
    2)
        run_preprocessor
        ;;
    3)
        run_parser
        run_preprocessor
        ;;
    4)
        echo -e "${GREEN}Terima kasih telah menggunakan CV-Analyzer!${NC}"
        deactivate 2>/dev/null
        exit 0
        ;;
    *)
        echo -e "${RED}Pilihan tidak valid. Keluar...${NC}"
        deactivate 2>/dev/null
        exit 1
        ;;
esac

echo -e "${GREEN}=====================================================${NC}"
echo -e "${GREEN}              🎉 Semua Proses Selesai! 🎉              ${NC}"
echo -e "${GREEN}=====================================================${NC}"

# Keluar dari venv setelah selesai
deactivate 2>/dev/null

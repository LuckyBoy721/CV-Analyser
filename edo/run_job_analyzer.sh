#!/bin/bash

# Pindah ke direktori script
cd "$(dirname "$0")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << "EOF"
  ____            _                _         
 |  _ \          | |              | |        
 | |_) | __ _ ___| |__   ___  __ _| |_  ___  
 |  _ < / _` / __| '_ \ / _ \/ _` | __|/ _ \ 
 | |_) | (_| \__ \ | | |  __/ (_| | |_|  __/ 
 |____/ \__,_|___/_| |_|\___|\__,_|\__|\___| 
EOF
echo -e "${NC}"
echo -e "${YELLOW}=====================================================${NC}"
echo -e "${GREEN}      Selamat Datang di Job Scraper Pipeline!      ${NC}"
echo -e "${YELLOW}=====================================================${NC}\n"

if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}[*] Membuat Virtual Environment (.venv) menggunakan uv...${NC}"
    uv venv
fi

source .venv/bin/activate
echo -e "${CYAN}[*] Menginstal dependencies dengan uv...${NC}"
uv pip install requests beautifulsoup4 pandas deep-translator nltk tqdm matplotlib

python3 -c "import nltk; nltk.download('stopwords', quiet=True)" 2>/dev/null

echo -e "\nSilakan pilih proses:"
echo -e "  ${CYAN}[1]${NC} Jalankan Scraper Saja (Tahap 1)"
echo -e "  ${CYAN}[2]${NC} Jalankan Preprocessor Saja (Tahap 2)"
echo -e "  ${CYAN}[3]${NC} Jalankan Semua (Pipeline Penuh)"
echo -e "  ${CYAN}[4]${NC} Keluar"
read -p "Pilihan (1/2/3/4): " choice

case $choice in
    1)
        read -p "Mulai dari halaman berapa? (default: 1): " start
        start=${start:-1}
        read -p "Sampai halaman berapa? (default: 5): " end
        end=${end:-5}
        python3 job_scraper.py --start $start --end $end
        ;;
    2)
        if [ ! -f "data/dataset.csv" ]; then
            echo -e "${RED}[!] data/dataset.csv tidak ditemukan. Jalankan scraper dulu.${NC}"
        else
            python3 job_preprocessor.py
        fi
        ;;
    3)
        read -p "Mulai dari halaman berapa? (default: 1): " start
        start=${start:-1}
        read -p "Sampai halaman berapa? (default: 5): " end
        end=${end:-5}
        python3 job_scraper.py --start $start --end $end
        python3 job_preprocessor.py
        ;;
    4)
        echo "Keluar."
        deactivate 2>/dev/null
        exit 0
        ;;
    *)
        echo -e "${RED}Pilihan tidak valid.${NC}"
        ;;
esac

deactivate 2>/dev/null

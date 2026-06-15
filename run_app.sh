#!/bin/bash

# Pindah ke direktori tempat script ini berada (root project)
cd "$(dirname "$0")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=====================================================${NC}"
echo -e "${GREEN}             MEMULAI APLIKASI CVMATCH AI             ${NC}"
echo -e "${CYAN}=====================================================${NC}\n"

app_file="sintya/desain_D.py"
echo -e "\n[*] Menyiapkan Desain D..."

# Cek apakah virtual environment lokal ada (untuk jaga-jaga)
if [ -d ".venv" ]; then
    echo -e "[*] Mengaktifkan virtual environment (.venv)..."
    source .venv/bin/activate
fi

echo -e "[*] Membuka Streamlit server...\n"
echo -e "Silakan tunggu beberapa saat. Jendela browser akan otomatis terbuka."
echo -e "Untuk menghentikan server, tekan ${RED}Ctrl + C${NC} di terminal ini.\n"

# Mencegah deadlock PyTorch pada CPU saat berjalan di dalam thread Streamlit
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

# Menjalankan aplikasi dengan modul streamlit yang dipilih
python -m streamlit run "$app_file"

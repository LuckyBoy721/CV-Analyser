#!/bin/bash

# Pindah ke direktori script ini berada
cd "$(dirname "$0")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=====================================================${NC}"
echo -e "${GREEN}       EVALUASI MODEL CV MATCHING (BENCHMARK)        ${NC}"
echo -e "${CYAN}=====================================================${NC}\n"

if [ ! -f "sample_100_cv_with_ground_truth.csv" ] || [ ! -f "data_clean.csv" ]; then
    echo -e "${RED}[!] Data tidak lengkap.${NC}"
    echo -e "${RED}Pastikan file 'sample_100_cv_with_ground_truth.csv' dan 'data_clean.csv' ada di dalam folder dimas/.${NC}"
    exit 1
fi

echo -e "Silakan pilih model algoritma yang ingin dievaluasi:"
echo -e "  ${YELLOW}[1]${NC} TF-IDF Baseline"
echo -e "  ${YELLOW}[2]${NC} TF-IDF + SVD"
echo -e "  ${YELLOW}[3]${NC} Embedding (Sentence-BERT)"
echo -e "  ${YELLOW}[4]${NC} Embedding dengan Punctuation"
echo -e "  ${YELLOW}[5]${NC} Jalankan Semua (Full Benchmark)"
echo -e "  ${YELLOW}[6]${NC} Keluar"
read -p "Pilihan (1-6): " choice

case $choice in
    1)
        python3 model_tfidf.py
        ;;
    2)
        python3 model_tfidf_svd.py
        ;;
    3)
        python3 model_embedding.py
        ;;
    4)
        python3 model_embedding_punct.py
        ;;
    5)
        echo -e "\n${CYAN}>>> Menjalankan semua evaluasi (proses ini membutuhkan waktu cukup lama)...${NC}\n"
        python3 model_tfidf.py
        python3 model_tfidf_svd.py
        python3 model_embedding.py
        python3 model_embedding_punct.py
        echo -e "${GREEN}Semua proses evaluasi telah selesai!${NC}"
        ;;
    6)
        echo "Selesai. Keluar dari program."
        exit 0
        ;;
    *)
        echo -e "${RED}Pilihan tidak valid.${NC}"
        ;;
esac

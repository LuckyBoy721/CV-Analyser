@echo off
cd /d "%~dp0"

echo =====================================================
echo              MEMULAI APLIKASI CVMATCH AI             
echo =====================================================
echo.

set app_file=sintya\desain_D.py
echo [*] Menyiapkan Desain D...

:: Cek apakah virtual environment lokal ada
if exist ".venv\Scripts\activate.bat" (
    echo [*] Mengaktifkan virtual environment (.venv)...
    call .venv\Scripts\activate.bat
)

echo [*] Membuka Streamlit server...
echo.
echo Silakan tunggu beberapa saat. Jendela browser akan otomatis terbuka.
echo Untuk menghentikan server, tekan Ctrl + C di terminal ini.
echo.

:: Mencegah deadlock PyTorch pada CPU
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
set OPENBLAS_NUM_THREADS=1

:: Menjalankan aplikasi dengan modul streamlit
python -m streamlit run "%app_file%"

pause

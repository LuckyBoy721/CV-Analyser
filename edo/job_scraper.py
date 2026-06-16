import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import sqlite3

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
BASE_URL = "https://id.jobstreet.com/id/jobs?page="

def get_job_details(job_url):
    try:
        response = requests.get(job_url, headers=HEADERS)
        if response.status_code != 200:
            return "", "", "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        combined_requirements = []
        job_ad = soup.find("div", {"data-automation": "jobAdDetails"})
        if job_ad:
            for li in job_ad.find_all("li"):
                text = li.get_text(strip=True)
                if text:
                    combined_requirements.append(text)
        requirements = "; ".join(combined_requirements)
        
        salary_tag = soup.find("span", {"data-automation": "job-detail-salary"})
        salary = salary_tag.get_text(strip=True).replace("\xa0", " ") if salary_tag else ""
        
        type_tag = soup.find("span", {"data-automation": "job-detail-work-type"})
        work_type = type_tag.find("a").get_text(strip=True) if type_tag and type_tag.find("a") else ""
        
        company_tag = soup.find("span", {"data-automation": "advertiser-name"})
        company = company_tag.get_text(strip=True) if company_tag else ""
        
        return requirements, salary, work_type, company
    except Exception as e:
        print(f"❌ Error detail: {e}")
        return "", "", "", ""

def scrape_jobs(start_page, max_pages, delay_list, delay_detail, output_file):
    job_list = []
    
    for page in range(start_page, max_pages + 1):
        print(f"\n🔄 Scraping halaman {page}...")
        try:
            response = requests.get(BASE_URL + str(page), headers=HEADERS)
            if response.status_code != 200:
                print(f"❌ Gagal akses halaman {page}")
                break
            
            soup = BeautifulSoup(response.content, "html.parser")
            job_cards = soup.find_all("a", {"data-automation": "jobTitle"})
            
            for job_card in job_cards:
                try:
                    title = job_card.get_text(strip=True)
                    link = "https://id.jobstreet.com" + job_card["href"]
                    
                    location_tag = job_card.find_next("a", {"data-automation": "jobLocation"})
                    location = location_tag.get_text(strip=True) if location_tag else ""
                    
                    requirements, salary, work_type, company = get_job_details(link)
                    
                    job_list.append({
                        "Posisi": title,
                        "Perusahaan": company,
                        "Lokasi": location,
                        "Type": work_type,
                        "Gaji": salary,
                        "Requirements": requirements,
                        "Link": link
                    })
                    print(f"✔ {title}")
                    time.sleep(delay_detail)
                except Exception as e:
                    print(f"❌ Error job card: {e}")
            time.sleep(delay_list)
        except Exception as e:
            print(f"❌ Error halaman: {e}")
            break

    if not job_list:
        print("⚠️ Tidak ada data yang berhasil discrape pada batch ini.")
        return

    df_raw = pd.DataFrame(job_list)
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # --- Layer 1: Raw (Staging) ---
    raw_file = output_file.replace(".csv", "_raw.csv")
    if os.path.exists(raw_file):
        old_raw = pd.read_csv(raw_file)
        df_raw_saved = pd.concat([old_raw, df_raw], ignore_index=True)
    else:
        df_raw_saved = df_raw.copy()
    
    df_raw_saved.to_csv(raw_file, index=False)
    print(f"\n✅ [Layer 1] Data Raw (Staging) disimpan di {raw_file}")

    # --- Layer 2: Clean ---
    # Menghilangkan duplikat dan membersihkan teks/nilai kosong
    df_clean = df_raw_saved.drop_duplicates(subset=["Posisi", "Link"]).copy()
    df_clean.fillna("Tidak Disebutkan", inplace=True)
    for col in df_clean.columns:
        if df_clean[col].dtype == "object":
            df_clean[col] = df_clean[col].str.strip()
    
    clean_file = output_file.replace(".csv", "_clean.csv")
    df_clean.to_csv(clean_file, index=False)
    print(f"✅ [Layer 2] Data Clean disimpan di {clean_file}")

    # --- Layer 3: Database (Source of Truth) ---
    radifan_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "radifan")
    os.makedirs(radifan_dir, exist_ok=True)
    db_file = os.path.join(radifan_dir, "source_of_truth.db")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Buat tabel utama jika belum ada (Link sebagai UNIQUE agar tidak duplikat)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            Posisi TEXT,
            Perusahaan TEXT,
            Lokasi TEXT,
            Type TEXT,
            Gaji TEXT,
            Requirements TEXT,
            Link TEXT UNIQUE
        )
    ''')
    
    # Simpan data clean ke tabel sementara
    df_clean.to_sql("jobs_temp", conn, if_exists="replace", index=False)
    
    # Insert ke tabel utama (IGNORE untuk link yang duplikat)
    cursor.execute('''
        INSERT OR IGNORE INTO jobs (Posisi, Perusahaan, Lokasi, Type, Gaji, Requirements, Link)
        SELECT Posisi, Perusahaan, Lokasi, Type, Gaji, Requirements, Link FROM jobs_temp
    ''')
    
    # Hapus tabel sementara
    cursor.execute('DROP TABLE jobs_temp')
    conn.commit()
    conn.close()
    
    print(f"✅ [Layer 3] Data disimpan ke Database (Source of Truth) SQLite di {db_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JobStreet Scraper")
    parser.add_argument("--start", type=int, default=1, help="Halaman mulai")
    parser.add_argument("--end", type=int, default=5, help="Halaman akhir")
    parser.add_argument("--output", type=str, default="data/dataset.csv", help="File output CSV")
    args = parser.parse_args()
    
    scrape_jobs(args.start, args.end, 2, 1, args.output)

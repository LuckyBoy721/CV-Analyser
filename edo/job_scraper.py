import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

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

    df = pd.DataFrame(job_list)
    df.drop_duplicates(subset=["Posisi", "Link"], inplace=True)
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if os.path.exists(output_file):
        old_df = pd.read_csv(output_file)
        df = pd.concat([old_df, df], ignore_index=True)
        df.drop_duplicates(subset=["Posisi", "Link"], inplace=True)
        
    df.to_csv(output_file, index=False)
    print(f"\n✅ Selesai! Data berhasil disimpan di {output_file} tanpa duplikasi.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JobStreet Scraper")
    parser.add_argument("--start", type=int, default=1, help="Halaman mulai")
    parser.add_argument("--end", type=int, default=5, help="Halaman akhir")
    parser.add_argument("--output", type=str, default="data/dataset.csv", help="File output CSV")
    args = parser.parse_args()
    
    scrape_jobs(args.start, args.end, 2, 1, args.output)

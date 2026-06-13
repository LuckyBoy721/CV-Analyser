import pandas as pd
import re
import time
import os
import argparse
from deep_translator import GoogleTranslator
import nltk
from nltk.corpus import stopwords
from tqdm import tqdm

def clean_text_basic(text):
    text = str(text).lower()
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

CATEGORIES = {
    "Data": ["data analyst", "data analytics", "data scientist", "data science", "machine learning", "ml engineer", "deep learning", "ai engineer", "data engineer", "big data", "data mining", "data visualization", "analisis data", "ilmuwan data", "pengolahan data","data"],
    "Software": ["software engineer", "software developer", "developer", "programmer", "backend", "backend developer", "frontend", "frontend developer", "full stack", "fullstack", "web developer", "mobile developer","web","api","mobile", "android developer", "ios developer", "pengembang", "coding", "komputer","computer"],
    "Marketing": ["marketing", "digital marketing", "seo", "sem", "content marketing", "branding", "social media", "campaign", "market research", "pemasaran", "iklan", "advertising"],
    "Finance": ["finance", "financial", "accounting", "accountant", "tax", "auditor", "budgeting", "investment", "banking", "keuangan", "akuntansi", "pajak", "audit","penagihan","collection"],
    "HR": ["hr", "human resource", "recruitment", "recruiter", "talent acquisition", "people development", "training", "sumber daya manusia", "rekrutmen", "hrd"],
    "Design & Creative": ["ui", "ux", "ui ux", "ui/ux", "product design", "graphic design", "graphic designer", "visual design", "creative design", "desain grafis", "desainer", "videographer", "photographer", "editor","kreatif", "content creator", "tiktok", "media","design", "creative", "social media content","live"],
    "Operations": ["operations", "operational", "operation staff","inventory","stock","display", "logistics", "supply chain", "warehouse", "inventory", "procurement", "purchasing", "gudang","supervisor","k3","keselamatan kerja"],
    "Sales": ["sales", "sales executive", "account manager", "business development", "bd", "client relation", "penjualan", "sales marketing", "consultant","account executive"],
    "Engineering": ["engineer", "engineering", "mechanical", "electrical","prototipe","architect","arsitek", "civil", "industrial engineer", "teknik mesin","proses produksi","drilling","teknik industri", "teknik sipil", "teknik elektro","elektro","listrik","mekanik","alat berat"],
    "Customer Service": ["customer service", "customer support", "support", "call center", "helpdesk", "cs", "layanan pelanggan","service"],
    "Admin": ["admin", "administration", "administrasi", "asisten", "secretary", "sekretaris", "dokumen","document", "assistant", "personal assistant","document controller","legal"],
    "Hospitality": ["hotel", "waiter", "waitress", "barista", "chef", "supir","sopir","pelayan","pelayanan", "kitchen", "restaurant", "f&b", "food", "beverage","masak","memasak", "front office", "guest service", "housekeeping","baker","driver","pembantu","tamu"],
    "Healthcare": ["perawat", "nurse", "kesehatan", "medical","medis","gizi","ahli gizi","mental","psikiater","psikolog", "lab", "bioteknologi", "farmasi","medic","healthcare","dokter","apotek","safety"],
    "Education": ["guru", "teacher", "school", "walikelas", "mengajar","pengajar","pelajaran", "les", "dosen", "education", "anak", "pendidikan", "pengajar","siswa","kelas","sekolah"],
    "Other": []
}

def classify_job(text):
    scores = {}
    for category, keywords in CATEGORIES.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 2 if len(keyword.split()) > 1 else 1
        scores[category] = score
    best_category = max(scores, key=scores.get)
    return "Other" if scores[best_category] == 0 else best_category

def smart_sample(group):
    with_salary = group[group["has_salary"] == True]
    without_salary = group[group["has_salary"] == False]
    result = with_salary.head(100)
    if len(result) < 100:
        remaining = 100 - len(result)
        result = pd.concat([result, without_salary.head(remaining)])
    return result

def translate_text(text):
    if pd.isna(text) or str(text).strip() == "":
        return text
    try:
        return GoogleTranslator(source="auto", target="en").translate(str(text))
    except Exception as e:
        print(f"Error translating: {e}")
        return text

def preprocess_embed(text):
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def preprocess_embed_punct(text):
    text = str(text).lower()
    return re.sub(r"\s+", " ", text).strip()

def remove_duplicate(text, preprocess_func):
    text = preprocess_func(text)
    words = text.split()
    for n in range(1, min(10, len(words)//2) + 1):
        if words[:n] == words[n:n*2]:
            return " ".join(words[n:])
    return text

def clean_tfidf_text(text, stop_words):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = [word for word in text.split() if word not in stop_words]
    return " ".join(tokens)

def main(input_csv, output_csv):
    if not os.path.exists(input_csv):
        print(f"File {input_csv} tidak ditemukan!")
        return
    
    print("Loading dataset...")
    df = pd.read_csv(input_csv)
    df = df.dropna(subset=["Requirements"])
    df.fillna({"Gaji": "-", "Type": "-", "Perusahaan": "-"}, inplace=True)
    
    print("Membersihkan text untuk klasifikasi...")
    df["text"] = df["Posisi"].fillna("") + " " + df["Posisi"].fillna("") + " " + df["Requirements"].fillna("")
    df["text_clean"] = df["text"].apply(clean_text_basic)
    
    print("Mengkategorikan pekerjaan...")
    df["Category"] = df["text_clean"].apply(classify_job)
    
    print("Balancing dataset...")
    df_filtered = df[df["Category"] != "Other"].copy()
    df_filtered["has_salary"] = df_filtered["Gaji"].astype(str).str.strip() != "-"
    df_balanced = df_filtered.groupby("Category", group_keys=False).apply(smart_sample).reset_index(drop=True)
    
    print("Menerjemahkan teks (ini membutuhkan waktu)...")
    tqdm.pandas()
    df_balanced["translated_text"] = df_balanced["text"].progress_apply(translate_text)
    
    print("Memproses stopwords...")
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    custom_stopwords = {"job", "requirement", "requirements", "responsibilities", "experience", "skill", "skills", "ability", "abilities", "candidate", "position", "role"}
    stop_words = stop_words.union(custom_stopwords)
    
    print("Membersihkan teks untuk model...")
    df_balanced["text_for_tfidf"] = df_balanced["translated_text"].apply(lambda x: clean_tfidf_text(x, stop_words))
    df_balanced["text_for_embed"] = df_balanced["translated_text"].apply(lambda x: remove_duplicate(x, preprocess_embed))
    df_balanced["text_for_embed_with_punctuation"] = df_balanced["translated_text"].apply(lambda x: remove_duplicate(x, preprocess_embed_punct))
    
    final_cols = ["Posisi", "Perusahaan", "Lokasi", "Type", "Gaji", "Requirements", "Link", "text_for_tfidf", "text_for_embed", "text_for_embed_with_punctuation"]
    final_df = df_balanced[[col for col in final_cols if col in df_balanced.columns]]
    
    output_dir = os.path.dirname(output_csv)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    final_df.to_csv(output_csv, index=False)
    print(f"✅ Selesai! Data bersih disimpan di {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job Preprocessor")
    parser.add_argument("--input", type=str, default="data/dataset.csv", help="Input CSV")
    parser.add_argument("--output", type=str, default="data/data_clean.csv", help="Output CSV")
    args = parser.parse_args()
    main(args.input, args.output)

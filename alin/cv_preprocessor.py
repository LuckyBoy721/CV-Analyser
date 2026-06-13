import os
import pandas as pd
import re
import string
import time
from deep_translator import GoogleTranslator
import nltk
from nltk.corpus import stopwords

# Ensure stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

categories = {
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

def clean_text_basic(text):
    text = str(text).lower()
    text = re.sub(r'\d+', ' ', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def classify_job(text):
    scores = {}
    for category, keywords in categories.items():
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 2 if len(keyword.split()) > 1 else 1
        scores[category] = score
    best_category = max(scores, key=scores.get)
    if scores[best_category] == 0:
        return "Other"
    return best_category

def smart_sample(group):
    if len(group) > 100:
        return group.sample(100, random_state=42)
    return group

def translate_text(text):
    try:
        if text is None or str(text).strip() == "":
            return text
        return GoogleTranslator(source="auto", target="en").translate(text)
    except Exception as e:
        print(f"Translation Error: {e}")
        return text

def preprocess_tfidf(text):
    stop_words = set(stopwords.words('english'))
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    words = [word for word in text.split() if word not in stop_words]
    return " ".join(words)

def preprocess_embed(text):
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return re.sub(r"\s+", " ", text).strip()

def preprocess_embed_with_punctuation(text):
    text = str(text).lower()
    return re.sub(r"\s+", " ", text).strip()

def main(input_csv="result/parsed_cv_final.csv", output_csv="result/hasil_scan_cv_parse.csv"):
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"File {input_csv} tidak ditemukan!")
        return

    print("Mengisi missing values...")
    df = df.dropna(subset=["text"])
    df.fillna({"skills": "-", "summary": "-", "experience": "-", "degree": "-", "university": "-", "education": "-"}, inplace=True)

    print("Membersihkan text untuk klasifikasi...")
    df["text_clean"] = df["text"].apply(clean_text_basic)
    
    print("Mengkategorikan pekerjaan...")
    df["Category"] = df["text_clean"].apply(classify_job)

    print("Balancing dataset (membuang 'Other' dan membatasi max 100/kategori)...")
    df_filtered = df[df["Category"] != "Other"].copy()
    df_balanced = df_filtered.groupby("Category", group_keys=False).apply(smart_sample).reset_index(drop=True)

    if "translated_text" not in df_balanced.columns:
        print("Menerjemahkan teks (ini mungkin butuh waktu lama)...")
        translated_texts = []
        for i, text in enumerate(df_balanced["text"]):
            print(f"Translating {i+1}/{len(df_balanced)}...")
            translated_texts.append(translate_text(text))
            time.sleep(0.5)
        df_balanced["translated_text"] = translated_texts
    else:
        print("Kolom 'translated_text' sudah ada.")

    print("Memproses teks untuk model ML (TF-IDF & Embedding)...")
    df_balanced["text_for_tfidf"] = df_balanced["translated_text"].apply(preprocess_tfidf)
    df_balanced["text_for_embed"] = df_balanced["translated_text"].apply(preprocess_embed)
    df_balanced["text_for_embed_with_punctuation"] = df_balanced["translated_text"].apply(preprocess_embed_with_punctuation)

    columns_to_save = [
        "candidate_name", "email", "phone", "skills", "summary", "experience", 
        "degree", "university", "Category", "text_for_tfidf", "text_for_embed", 
        "text_for_embed_with_punctuation"
    ]
    # Handle cases where some basic info columns might be missing from initial extraction
    final_columns = [col for col in columns_to_save if col in df_balanced.columns]
    
    final_df = df_balanced[final_columns]
    output_dir = os.path.dirname(output_csv)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    final_df.to_csv(output_csv, index=False)
    print(f"✅ Selesai! Data bersih disimpan di {output_csv}")

if __name__ == "__main__":
    main()

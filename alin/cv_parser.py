import os
import re
import zipfile
import pandas as pd
from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator
from tqdm import tqdm

try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

def extract_zip(zip_path, extract_to="cv_folder"):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("✅ ZIP berhasil diekstrak")

def get_pdf_files(folder):
    pdf_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def pdf_to_text(file_path, progress_callback=None):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    
    text = text.lower().strip()
    
    # Fallback to OCR if text is empty or too short (likely a scanned photo PDF)
    if len(text) < 50 and OCR_AVAILABLE:
        try:
            if progress_callback: progress_callback(15, "Menyiapkan mesin OCR...")
            images = convert_from_path(file_path)
            ocr_text = ""
            total_pages = len(images)
            for i, img in enumerate(images):
                if progress_callback: progress_callback(15 + int(((i+1)/total_pages)*20), f"Memindai halaman {i+1} dari {total_pages} (OCR)...")
                ocr_text += pytesseract.image_to_string(img) + "\n"
            
            if ocr_text.strip():
                text = ocr_text.lower().strip()
        except Exception as e:
            print(f"\n[!] Gagal melakukan OCR pada {file_path}.")
            print(f"[!] Pastikan 'tesseract-ocr' dan 'poppler-utils' sudah terinstall di sistem operasi Anda.")
            print(f"[!] Error detail: {e}\n")

    return text

def extract_email(text):
    match = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)
    return match[0] if match else None

def extract_phone(text):
    match = re.findall(r'(\+62\d{9,13}|08\d{8,12})', text)
    return match[0] if match else None

def extract_name(text):
    lines = text.strip().split("\n")
    return lines[0].strip().title() if lines else None

def extract_section(text, section_names, stop_keywords):
    pattern = (
        r'(' + '|'.join(section_names) + r')'
        r'(.*?)'
        r'(?=' + '|'.join(stop_keywords) + r'|$)'
    )
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(2).strip()
    return ""

def extract_summary(text):
    summary = extract_section(
        text,
        section_names=[
            'ringkasan', 'summary', 'profil', 'profile', 'tentang saya',
            'about me', 'professional summary', 'career objective',
            'objective', 'deskripsi diri'
        ],
        stop_keywords=[
            'pendidikan', 'education', 'skills', 'keahlian', 'organisasi',
            'experience', 'work experience', 'pengalaman kerja', 'projects',
            'sertifikat', 'certification'
        ]
    )
    summary = re.sub(r'\n+', ' ', summary)
    summary = re.sub(r'\s+', ' ', summary)
    return summary.strip()

def extract_skills(text):
    lines = text.split("\n")
    raw_skills = []
    capture = False
    start_keywords = ["keahlian", "skills", "skill", "kompetensi", "tools", "teknologi"]
    stop_keywords = ["penghargaan", "bahasa", "hobi", "referensi", "pendidikan", "pengalaman", "organisasi", "tentang", "profil", "summary"]

    for line in lines:
        line = line.strip().lower()
        if not line:
            continue
            
        # Check start
        if any(line.startswith(k) or line == k for k in start_keywords):
            capture = True
            continue
            
        # Check stop
        if capture and any(line.startswith(k) or line == k for k in stop_keywords):
            break
            
        if capture:
            raw_skills.append(line)

    if not raw_skills:
        # Fallback: If no explicit skill section, look for lines with skill-like delimiters
        for line in lines:
            line = line.strip().lower()
            if "•" in line or "|" in line or ";" in line:
                raw_skills.append(line)
            elif "," in line:
                # Avoid capturing full sentences with commas
                num_commas = line.count(",")
                num_words = len(line.split())
                if num_words > 0 and (num_words / (num_commas + 1)) <= 3.5:
                    raw_skills.append(line)

    final_skills = []
    for line in raw_skills:
        # Split by common delimiters (comma, bullet, pipe, semicolon)
        parts = re.split(r'[,|•●▪;]', line)
        for part in parts:
            # Clean leading/trailing non-alphanumeric chars (like dashes)
            part = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9+]+$', '', part).strip()
            
            # Remove common sentence fragments or conjunctions
            for prefix in ["termasuk ", "dan ", "serta ", "seperti ", "juga ", "memiliki ", "kemampuan "]:
                if part.startswith(prefix):
                    part = part[len(prefix):].strip()

            if not part:
                continue
            
            # Filtering noise
            if len(part) < 2 or len(part) > 30: continue  # Too short/long
            if len(part.split()) > 4: continue  # A skill is usually 1-4 words max
            if re.search(r'\d{4}', part): continue  # Contains a year (e.g. 2015)
            if re.search(r'\d{9,}', part): continue  # Contains phone number
            if "@" in part or ".com" in part or ".id" in part: continue  # Email or web
            if any(month in part for month in ['jan ', 'feb ', 'mar ', 'apr ', 'mei ', 'jun ', 'jul ', 'agu ', 'sep ', 'okt ', 'nov ', 'des ']): continue
            if any(noise in part for noise in ['jalan ', 'alamat', 'telepon', 'phone', 'email', 'referensi', 'cv ', 'curriculum vitae', 'nama', 'tempat', 'pt.', 'pt ', 'cv.', 'sma ', 'smk ', 'smak ', 'universitas', 'institut', 'sekolah', 'portofolio yang']): continue
            
            final_skills.append(part)

    return list(set(final_skills))

def extract_education(text):
    edu_text = extract_section(
        text,
        section_names=['pendidikan', 'education', 'academic background', 'riwayat pendidikan'],
        stop_keywords=['pengalaman kerja', 'experience', 'skills', 'keahlian', 'organisasi', 'projects', 'sertifikat', 'certification']
    )
    edu_text = re.sub(r'\n+', ' ', edu_text)
    edu_text = re.sub(r'\s+', ' ', edu_text)

    degree = None
    if any(k in edu_text.lower() for k in ['sarjana', 's1', 'bachelor']):
        degree = 'S1'
    elif any(k in edu_text.lower() for k in ['s2', 'master']):
        degree = 'S2'
    elif any(k in edu_text.lower() for k in ['d3', 'diploma']):
        degree = 'D3'
    elif 'sma' in edu_text.lower():
        degree = 'SMA'

    university_patterns = [
        r'universitas[\w\s]+', r'institut[\w\s]+', r'politeknik[\w\s]+', r'university[\w\s]+'
    ]
    university = None
    for pattern in university_patterns:
        match = re.search(pattern, edu_text, re.IGNORECASE)
        if match:
            university = match.group().strip()
            break

    return {
        "degree": degree,
        "university": university,
        "education_text": edu_text
    }

def extract_experience(text):
    exp_text = extract_section(
        text,
        section_names=['pengalaman kerja', 'work experience', 'experience', 'professional experience', 'internship', 'pengalaman'],
        stop_keywords=['pendidikan', 'education', 'skills', 'keahlian', 'organisasi', 'projects', 'sertifikat', 'certification']
    )
    exp_text = re.sub(r'\n+', ' ', exp_text)
    return exp_text.strip()

def parse_cv(file_path, progress_callback=None):
    if progress_callback: progress_callback(5, "Membaca struktur file PDF...")
    text = pdf_to_text(file_path, progress_callback)
    
    if progress_callback: progress_callback(40, "Mengekstrak entitas penting...")
    name = extract_name(text)
    email = extract_email(text)
    phone = extract_phone(text)
    
    if progress_callback: progress_callback(45, "Mengekstrak skills...")
    skills = extract_skills(text)
    
    if progress_callback: progress_callback(50, "Mengekstrak profil dan pengalaman...")
    summary = extract_summary(text)
    experience = extract_experience(text)
    education = extract_education(text)

    skills_text = ", ".join(skills)
    candidate_profile = f"""
    Summary: {summary}
    Experience: {experience}
    Skills: {skills_text}
    Education: {education["education_text"]}
    """
    candidate_profile = re.sub(r'\s+', ' ', candidate_profile).strip()

    data = {
        "candidate_name": name if name else "lorem",
        "email": email if email else "lorem",
        "phone": phone if phone else "lorem",
        "skills": skills_text if skills_text else "lorem",
        "summary": summary if summary else "NONE",
        "experience": experience if experience else "lorem",
        "degree": education["degree"] if education["degree"] else "lorem",
        "university": education["university"] if education["university"] else "lorem",
        "education": education["education_text"] if education["education_text"] else "lorem",
        "text": candidate_profile if candidate_profile else "lorem"
    }
    return data

def safe_translate(text):
    if pd.isna(text):
        return ""
    try:
        return GoogleTranslator(source='auto', target='en').translate(str(text))
    except Exception as e:
        print("Translation error:", e)
        return str(text)

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

if __name__ == "__main__":
    # Example usage:
    # zip_path = "cv pdf.zip"
    # extract_zip(zip_path, "cv_folder")
    
    cv_folder = "cv_folder"
    if not os.path.exists(cv_folder):
        print(f"Folder {cv_folder} tidak ditemukan. Buat foldernya dan masukkan file PDF.")
    else:
        pdf_files = get_pdf_files(cv_folder)
        print("Jumlah CV:", len(pdf_files))

        all_results = []
        for i, pdf in enumerate(pdf_files):
            try:
                print(f"[{i+1}/{len(pdf_files)}] Processing: {pdf}")
                result = parse_cv(pdf)
                all_results.append(result)
            except Exception as e:
                print(f"ERROR parsing {pdf}: {e}")

        if all_results:
            df = pd.DataFrame(all_results)
            print("Menerjemahkan teks profil ke bahasa Inggris...")
            tqdm.pandas()
            df["translated_text"] = df["text"].progress_apply(safe_translate)
            
            print("Membersihkan teks...")
            df["clean_text"] = df["translated_text"].apply(clean_text)
            
            output_dir = "result"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "parsed_cv_final.csv")
            df.to_csv(output_file, index=False)
            print(f"✅ Selesai parsing semua CV. File disimpan sebagai: {output_file}")

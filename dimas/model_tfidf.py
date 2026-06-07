import pandas as pd
import numpy as np
import re
import ast
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

def normalize(text):
    text = text.lower()
    text = re.sub(r'\([^)]*\)', '', text)
    return text.strip()

def main():
    print("Memuat dataset untuk TF-IDF Model...")
    df_cv = pd.read_csv('sample_100_cv_with_ground_truth.csv')
    df_job = pd.read_csv('data_clean.csv')
    
    df_cv["ground_truth"] = df_cv["ground_truth"].apply(ast.literal_eval)
    
    print("Memproses TF-IDF...")
    job_texts = df_job["text_for_tfidf"].tolist()
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2), sublinear_tf=True)
    job_tfidf = vectorizer.fit_transform(job_texts)
    
    prediksi_perusahaan = []
    prediksi_posisi = []
    
    for h in range(len(df_cv)):
        cv_text = df_cv.loc[h, 'text_for_tfidf']
        cv_tfidf = vectorizer.transform([cv_text])
        scores = cosine_similarity(cv_tfidf, job_tfidf)
        top_indices = scores[0].argsort()[-5:][::-1]
        
        prediksi_perusahaan.append([df_job.iloc[i]["Perusahaan"] for i in top_indices])
        prediksi_posisi.append([df_job.iloc[i]["Posisi"] for i in top_indices])
        
    df_cv_hasil = df_cv.copy()
    df_cv_hasil['prediksi_perusahaan'] = prediksi_perusahaan
    df_cv_hasil['prediksi_posisi'] = prediksi_posisi
    
    print("Mengevaluasi hasil (Semantic Validation)...")
    model_eval = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    nilai_sim_max = []
    for i in range(len(df_cv_hasil)):
        ground_truth = [normalize(x) for x in df_cv_hasil.loc[i,'ground_truth']]
        hasil_prediksi = [normalize(x) for x in df_cv_hasil.loc[i,'prediksi_posisi']]
        sim = cosine_similarity(model_eval.encode(ground_truth), model_eval.encode(hasil_prediksi))
        nilai_sim_max.extend(sim.max(axis=0))
        
    series_sim_max = pd.Series(nilai_sim_max)
    threshold = np.floor(series_sim_max.quantile(0.75) * 10) / 10
    
    nilai_precision_at_5 = []
    for i in range(len(df_cv_hasil)):
        ground_truth = [normalize(x) for x in df_cv_hasil.loc[i,'ground_truth']]
        hasil_prediksi = [normalize(x) for x in df_cv_hasil.loc[i,'prediksi_posisi']]
        sim = cosine_similarity(model_eval.encode(ground_truth), model_eval.encode(hasil_prediksi))
        relevan = (sim.max(axis=0) >= threshold).astype(int).tolist()
        nilai_precision_at_5.append(sum(relevan) / len(relevan))
        
    df_cv_hasil['precision@5'] = nilai_precision_at_5
    print(f"\n=== HASIL EVALUASI TF-IDF ===")
    print(f"Threshold (Q3 rounded): {threshold}")
    print(f"Mean Precision@5: {df_cv_hasil['precision@5'].mean():.4f}\n")

if __name__ == "__main__":
    main()

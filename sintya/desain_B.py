import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import os
import sys
import tempfile
import re
from sklearn.metrics.pairwise import cosine_similarity

# ── Backend Integration ───────────────────────────────────────
# Menambahkan root directory agar bisa mengimpor alin dan dimas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alin.cv_parser import parse_cv, safe_translate, clean_text
from alin.cv_preprocessor import preprocess_tfidf, preprocess_embed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sentence_transformers import SentenceTransformer

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="CVMatch AI – Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background dark */
    .stApp { background-color: #0d1117; color: #e0eaf4; }
    [data-testid="stHeader"] { background-color: #0d1117; }

    /* Sidebar dark */
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #21262d; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 16px;
        color: #e0eaf4;
    }
    [data-testid="stMetricValue"] { color: #7ec8e3 !important; }
    [data-testid="stMetricLabel"] { color: #8b949e !important; }

    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        background: #161b22;
        border-radius: 8px;
        color: #8b949e;
        border: 1px solid #21262d;
        margin-right: 6px;
    }
    .stTabs [aria-selected="true"] {
        background: #1f4068 !important;
        color: #7ec8e3 !important;
        border-color: #7ec8e3 !important;
    }

    /* Skill pill */
    .pill-match-dark {
        display: inline-block; background: #0a3d2e; color: #5DCAA5;
        border-radius: 20px; padding: 4px 12px; margin: 3px; font-size: 13px;
    }
    .pill-gap-dark {
        display: inline-block; background: #3d1a1a; color: #F09595;
        border-radius: 20px; padding: 4px 12px; margin: 3px; font-size: 13px;
    }

    /* Job card dark */
    .job-card-dark {
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    /* Progress bar color */
    .stProgress > div > div > div > div { background-color: #5DCAA5; }

    /* Buttons */
    .stButton button {
        background: #1f4068; color: #7ec8e3;
        border: 1px solid #7ec8e3; border-radius: 8px;
    }
    .stButton button:hover { background: #7ec8e3; color: #0d1117; }

    /* Headings */
    h1, h2, h3 { color: #e0eaf4 !important; }
    p, span, label { color: #c9d1d9; }

    /* File uploader dark */
    [data-testid="stFileUploader"] {
        background: #161b22; border: 2px dashed #1f4068; border-radius: 12px;
    }

    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Caching Data & Models ──────────────────────────────────────
@st.cache_data
def load_jobs_data():
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'edo', 'data', 'data_clean.csv')
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    return pd.read_csv(csv_path)

@st.cache_resource
def load_sentence_transformer():
    model_name = 'all-MiniLM-L6-v2'
    local_path = os.path.join(os.path.dirname(__file__), '..', 'dimas', 'models', model_name)
    if os.path.exists(local_path):
        return SentenceTransformer(local_path)
    else:
        # Download dari internet lalu simpan secara lokal (offline)
        model = SentenceTransformer(model_name)
        os.makedirs(local_path, exist_ok=True)
        model.save(local_path)
        return model

@st.cache_resource
def prepare_tfidf_models(df):
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2), sublinear_tf=True)
    job_tfidf = vectorizer.fit_transform(df['text_for_tfidf'].fillna(""))
    return vectorizer, job_tfidf

@st.cache_resource
def prepare_svd_model(job_tfidf):
    svd = TruncatedSVD(n_components=100, random_state=42)
    job_svd = svd.fit_transform(job_tfidf)
    return svd, job_svd

@st.cache_resource
def prepare_embeddings(df, _model):
    return _model.encode(df['text_for_embed'].fillna("").tolist(), show_progress_bar=False)

# Load global dataset
df_jobs = load_jobs_data()

# ── Header ────────────────────────────────────────────────────
col_logo, col_title, col_model = st.columns([1, 4, 2])
with col_logo:
    st.markdown("## 🧠")
with col_title:
    st.markdown("## CVMatch AI")
    st.caption("AI-Based CV Analyzer & Job Recommendation System")
with col_model:
    model_choice = st.selectbox(
        "Pilih Model Eksekusi",
        ["Embedding (Sentence-BERT)", "TF-IDF + SVD", "TF-IDF (Baseline)"],
        label_visibility="visible",
    )

st.divider()

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📤 Upload & Parsing", "📋 Rekomendasi", "🔍 Detail Analisis", "📊 Visualisasi"
])

# Variables to hold process results
parsed_data = {}
recommended_jobs = []
cv_skills = []
job_reqs_keywords = ["sql", "python", "agile", "leadership", "docker", "cloud"] # dummy fallback
scores_for_viz = []

with tab1:
    st.subheader("Upload CV & Hasil Ekstraksi")
    c_up, c_res = st.columns([1, 1])

    with c_up:
        uploaded = st.file_uploader("Upload CV (PDF)", type=["pdf"], label_visibility="collapsed")
        
        if uploaded:
            # Process only if it's a new file to avoid re-parsing on tab/model change
            if st.session_state.get("cv_filename") != uploaded.name:
                with st.spinner("Mengekstrak dan memproses CV dengan NLP pipeline..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded.read())
                        tmp_path = tmp.name
                    
                    # Parsing
                    data = parse_cv(tmp_path)
                    os.remove(tmp_path)
                    
                    # Preprocessing
                    raw_text = data.get('text', '')
                    translated_text = safe_translate(clean_text(raw_text))
                    
                    # Save to session state
                    st.session_state.cv_filename = uploaded.name
                    st.session_state.parsed_data = data
                    st.session_state.cv_text_tfidf = preprocess_tfidf(translated_text)
                    st.session_state.cv_text_embed = preprocess_embed(translated_text)
                    
                    st.success(f"✅ **{uploaded.name}** berhasil diproses!")
            else:
                st.success(f"✅ **{uploaded.name}** sudah dimuat dari sesi.")

            parsed_data = st.session_state.parsed_data
            
            # Display Extracted Info
            name = parsed_data.get('candidate_name', 'Tidak Terdeteksi')
            edu = parsed_data.get('degree', '') + " - " + parsed_data.get('university', '')
            exp = (parsed_data.get('experience')[:60] + '...') if len(parsed_data.get('experience', '')) > 60 else parsed_data.get('experience', 'Belum ada')
            
            st.markdown("#### 📄 Info Ekstraksi CV")
            st.markdown(f"""
            | Field | Nilai |
            |---|---|
            | Nama | {name} |
            | Pendidikan | {edu} |
            | Pengalaman | {exp} |
            | Kontak | {parsed_data.get('email', '')} |
            """)
            
            # Calculate Recommendation dynamically
            if not df_jobs.empty:
                with st.spinner(f"Menghitung kecocokan menggunakan {model_choice}..."):
                    if model_choice == "TF-IDF (Baseline)":
                        vectorizer, job_tfidf = prepare_tfidf_models(df_jobs)
                        cv_vec = vectorizer.transform([st.session_state.cv_text_tfidf])
                        scores = cosine_similarity(cv_vec, job_tfidf)[0]
                    elif model_choice == "TF-IDF + SVD":
                        vectorizer, job_tfidf = prepare_tfidf_models(df_jobs)
                        svd, job_svd = prepare_svd_model(job_tfidf)
                        cv_vec = vectorizer.transform([st.session_state.cv_text_tfidf])
                        cv_svd = svd.transform(cv_vec)
                        scores = cosine_similarity(cv_svd, job_svd)[0]
                    else:
                        sbert = load_sentence_transformer()
                        job_embeddings = prepare_embeddings(df_jobs, sbert)
                        cv_emb = sbert.encode([st.session_state.cv_text_embed])
                        scores = cosine_similarity(cv_emb, job_embeddings)[0]
                    
                    # Sort scores
                    top_indices = scores.argsort()[-5:][::-1]
                    for rank, idx in enumerate(top_indices, 1):
                        row = df_jobs.iloc[idx]
                        recommended_jobs.append({
                            "rank": rank,
                            "title": row.get("Posisi", "Unknown"),
                            "company": row.get("Perusahaan", "Unknown"),
                            "location": row.get("Lokasi", "Unknown"),
                            "type": row.get("Type", "Unknown"),
                            "score": int(min(max(round(scores[idx] * 100), 0), 100)),
                            "requirements": row.get("Requirements", "")
                        })
            
                    st.session_state.recommended_jobs = recommended_jobs
            else:
                st.error("Database Pekerjaan kosong atau tidak ditemukan.")

        else:
            st.info("Upload file PDF CV Anda untuk memulai analisis.")

    with c_res:
        if parsed_data:
            cv_skills = [s.strip() for s in parsed_data.get('skills', '').split(',') if s.strip()]
            if not cv_skills or len(cv_skills) < 2:
                cv_skills = ["Python", "Komunikasi", "Problem Solving", "Manajemen Waktu"] # Fallback if empty
            
            # Use top job recommendation to find gap skills
            top_req = recommended_jobs[0]['requirements'].lower() if recommended_jobs else ""
            
            # Match skills simply
            SKILLS_MATCH = [s for s in cv_skills if s.lower() in top_req]
            if not SKILLS_MATCH: SKILLS_MATCH = cv_skills[:5]
            
            # Determine gap skills conceptually (words in top_req not in CV)
            common_tech = ["sql", "agile", "aws", "docker", "linux", "cloud", "scrum", "rest api"]
            SKILLS_GAP = [t.capitalize() for t in common_tech if t in top_req and t not in [s.lower() for s in cv_skills]][:4]
            if not SKILLS_GAP: SKILLS_GAP = ["Sertifikasi Khusus", "Advanced Tools"]
            
            st.markdown("#### ✅ Skills Terdeteksi (Match)")
            if SKILLS_MATCH:
                pills_match = "".join(f'<span class="pill-match-dark">✓ {s}</span>' for s in SKILLS_MATCH)
                st.markdown(pills_match, unsafe_allow_html=True)
            else:
                st.write("-")

            st.markdown("#### ❌ Target Skill Pekerjaan (Gap)")
            pills_gap = "".join(f'<span class="pill-gap-dark">✗ {s}</span>' for s in SKILLS_GAP)
            st.markdown(pills_gap, unsafe_allow_html=True)

# ── KPI Updates ───────────────────────────────────────────────
# We use container injection pattern by replacing the placeholder visually, 
# but Streamlit runs top-to-bottom so we usually put KPIs at top. 
# Since we process inside tabs, we display KPIs dynamically:
st.sidebar.markdown("### 📊 Ringkasan Sesi")
if 'recommended_jobs' in st.session_state and st.session_state.recommended_jobs:
    best_score = st.session_state.recommended_jobs[0]['score']
    st.sidebar.metric("🏆 Kecocokan Terbaik", f"{best_score}%")
    st.sidebar.metric("📂 Lowongan Dianalisis", f"{len(df_jobs)}")
    
    sk_len = len(parsed_data.get('skills', '').split(',')) if parsed_data else 0
    st.sidebar.metric("🔑 Skills Terdeteksi", f"{sk_len}")

# ────────────────────────────
with tab2:
    if 'recommended_jobs' in st.session_state and st.session_state.recommended_jobs:
        jobs_list = st.session_state.recommended_jobs
        st.subheader(f"Top-{len(jobs_list)} Rekomendasi Pekerjaan")
        st.caption(f"Model: **{model_choice}** · Diurutkan berdasarkan skor kecocokan semantik")

        for job in jobs_list:
            s = job["score"]
            color = "#5DCAA5" if s >= 80 else "#7ec8e3" if s >= 60 else "#FAC775"

            st.markdown(f"""
            <div class="job-card-dark">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="color:#e0eaf4;font-size:15px;font-weight:600;">
                            #{job['rank']} {job['title']}
                        </span><br>
                        <span style="color:#8b949e;font-size:13px;">
                            {job['company']} &nbsp;·&nbsp; {job['location']} &nbsp;·&nbsp; {job['type']}
                        </span>
                    </div>
                    <span style="color:{color};font-size:18px;font-weight:700;">{s}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(s / 100)
    else:
        st.info("Selesaikan unggah dokumen CV di tab 'Upload' untuk melihat rekomendasi.")

# ────────────────────────────
with tab3:
    if 'recommended_jobs' in st.session_state and st.session_state.recommended_jobs:
        top_job = st.session_state.recommended_jobs[0]
        st.subheader(f"Detail Analisis – {top_job['title']} @ {top_job['company']}")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✅ Skills Anda yang Terekstrak:**")
            for s in SKILLS_MATCH:
                st.success(f"✓  {s}")
        with c2:
            st.markdown("**❌ Area Potensi Pengembangan (Gap):**")
            for s in SKILLS_GAP:
                st.error(f"✗  {s}")

        st.divider()
        st.info(f"""
        💡 **Rekomendasi Pengembangan Diri:**
        Pekerjaan ini meminta beberapa prasyarat utama. Pertimbangkan untuk mempelajari 
        **{', '.join(SKILLS_GAP)}** untuk meningkatkan peluang Anda agar sesuai dengan kebutuhan
        dari **{top_job['company']}**.
        """)
    else:
        st.info("Menunggu data CV diproses...")

# ────────────────────────────
with tab4:
    if 'recommended_jobs' in st.session_state and st.session_state.recommended_jobs:
        st.subheader("Visualisasi Skor Model")
        
        df_viz = pd.DataFrame(st.session_state.recommended_jobs)
        fig2 = go.Figure(go.Bar(
            x=df_viz["title"], y=df_viz["score"],
            marker_color=["#5DCAA5", "#7ec8e3", "#7ec8e3", "#FAC775", "#FAC775"],
            text=df_viz["score"].astype(str) + "%",
            textposition="outside",
        ))
        fig2.update_layout(
            paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
            font_color="#e0eaf4", yaxis=dict(range=[0, 110]),
            margin=dict(t=30, b=30),
            title="Tingkat Kecocokan dengan 5 Lowongan Teratas",
            title_font_color="#e0eaf4",
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
         st.info("Upload CV untuk menampilkan grafik analitik.")

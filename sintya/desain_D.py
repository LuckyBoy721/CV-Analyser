import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import os
import sys
import base64
import tempfile
from sklearn.metrics.pairwise import cosine_similarity

# ══════════════════════════════════════════════════════════════
# BACKEND INTEGRATION
# ══════════════════════════════════════════════════════════════
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from alin.cv_parser import parse_cv, safe_translate, clean_text
from alin.cv_preprocessor import preprocess_tfidf, preprocess_embed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sentence_transformers import SentenceTransformer

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
def prepare_svd_model(_job_tfidf):
    svd = TruncatedSVD(n_components=100, random_state=42)
    job_svd = svd.fit_transform(_job_tfidf)
    return svd, job_svd

import numpy as np

@st.cache_resource
def prepare_embeddings(df, _model):
    embed_path = os.path.join(os.path.dirname(__file__), '..', 'dimas', 'models', 'job_embeddings.npy')
    
    # Check if precomputed embeddings exist
    if os.path.exists(embed_path):
        return np.load(embed_path)
    
    # Compute embeddings if not found
    embeddings = _model.encode(df['text_for_embed'].fillna("").tolist(), show_progress_bar=True)
    
    # Save for future use
    os.makedirs(os.path.dirname(embed_path), exist_ok=True)
    np.save(embed_path, embeddings)
    
    return embeddings

df_jobs = load_jobs_data()

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="JobMatch AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def load_logo():
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

LOGO_B64 = load_logo()


# ══════════════════════════════════════════════════════════════
# THEME CONFIG
# ══════════════════════════════════════════════════════════════
st.sidebar.markdown("### ⚙️ Pengaturan Tampilan")
is_light = st.sidebar.toggle("☀️ Mode Terang", value=False)

if is_light:
    theme_css = """
    :root {
        --bg-main: #f6f8fa;
        --card-bg: #ffffff;
        --border: #d0d7de;
        --border-light: #eaeef2;
        --text-main: #24292f;
        --text-head: #1F2328;
        --text-muted: #57606a;
        --success-bg: #dafbe1;
        --success-text: #1a7f37;
        --success-border: #4ac26b;
        --warn-bg: #fff8c5;
        --warn-text: #bf8700;
        --error-bg: #ffebe9;
        --error-text: #cf222e;
        --pill-match-bg: #dafbe1;
        --info-bg: #ddf4ff;
        --info-border: #54aeff;
        --btn-disabled-text: #8c959f;
    }
    """
else:
    theme_css = """
    :root {
        --bg-main: #0d1117;
        --card-bg: #161b22;
        --border: #2d2d2d;
        --border-light: #21262d;
        --text-main: #c9d1d9;
        --text-head: #ffffff;
        --text-muted: #8b949e;
        --success-bg: #0a2e1a;
        --success-text: #3fb950;
        --success-border: #2ea043;
        --warn-bg: #2e1f0a;
        --warn-text: #d29922;
        --error-bg: #2e0a0a;
        --error-text: #ff7b7b;
        --pill-match-bg: #1a2e1a;
        --info-bg: #1a1f3a;
        --info-border: #3b5bdb;
        --btn-disabled-text: #4a4a4a;
    }
    """

st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
.stApp                          { background-color: var(--bg-main); color: var(--text-main); }
[data-testid="stHeader"]        { background-color: var(--bg-main); border-bottom: 1px solid var(--border-light); }
section[data-testid="stMain"]   { background-color: var(--bg-main); }
.block-container                { max-width: 100% !important; padding: 3.2rem 3rem 1.5rem 3rem !important; }
h1,h2,h3,h4    { color: var(--text-head) !important; }
p,span,div      { color: var(--text-main); }

[data-testid="metric-container"] {
    background: var(--card-bg) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; padding: 16px !important;
    border-top: 3px solid #e8274b !important;
}
[data-testid="stMetricValue"] { color: #e8274b !important; font-size: 28px !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; }
[data-testid="stMetricDelta"] { color: #ff6b8a !important; }

.stProgress > div > div > div > div { background: linear-gradient(90deg,#e8274b,#ff6b8a) !important; }
[data-testid="stProgressBar"]        { background-color: var(--border-light) !important; }

.stButton > button {
    background-color: transparent; color: #e8274b;
    border: 1.5px solid #e8274b; border-radius: 8px;
    font-weight: 500; transition: all 0.2s ease;
}
.stButton > button:hover { background-color: #e8274b; color: var(--text-head); }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #e8274b, #c41f3b);
    border-color: #e8274b; color: var(--text-head); font-weight: 600;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #ff4d6d, #e8274b);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(232,39,75,0.4);
}
.stButton > button:disabled {
    background-color: var(--card-bg) !important; color: var(--btn-disabled-text) !important;
    border-color: var(--border) !important; cursor: not-allowed !important;
}

[data-testid="stFileUploader"] {
    background: var(--card-bg); border: 2px dashed #e8274b;
    border-radius: 12px; opacity: 0.9;
}
[data-testid="stFileUploader"] label { color: var(--text-muted) !important; }

.stTextArea textarea, .stTextInput input {
    background: var(--card-bg) !important; color: var(--text-main) !important;
    border: 1px solid var(--border) !important; border-radius: 8px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus { border-color: #e8274b !important; }

.stTabs [data-baseweb="tab-list"] {
    background: var(--card-bg); border-radius: 10px;
    padding: 4px; gap: 6px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; color: var(--text-muted); font-weight: 500;
    margin-right: 4px !important; padding-left: 16px !important; padding-right: 16px !important;
}
.stTabs [aria-selected="true"] { background: #e8274b !important; color: var(--text-head) !important; }

.streamlit-expanderHeader  { background: var(--card-bg) !important; color: var(--text-main) !important; border-radius: 10px !important; border-left: 3px solid #e8274b !important; }
.streamlit-expanderContent { background: var(--bg-main) !important; border: 1px solid var(--border-light) !important; border-radius: 0 0 10px 10px !important; }

.stSuccess { background: var(--success-bg) !important; border-color: var(--success-border) !important; }
.stInfo    { background: var(--info-bg) !important; border-color: var(--info-border) !important; }
.stWarning { background: var(--warn-bg) !important; border-color: #e8274b !important; }
.stError   { background: var(--error-bg) !important; border-color: #e8274b !important; }

[data-testid="stSlider"] { color: #e8274b !important; }
.stSlider > div > div > div > div { background: #e8274b !important; }
[data-testid="stDataFrame"] { background: var(--card-bg) !important; }
hr { border-color: var(--border) !important; margin: 0.8rem 0 !important; }

.pill-match {
    display: inline-block; background: var(--pill-match-bg); color: var(--success-text);
    border: 1px solid var(--success-border); border-radius: 20px;
    padding: 4px 13px; margin: 3px; font-size: 13px; font-weight: 500;
}
.pill-gap {
    display: inline-block; background: var(--error-bg); color: var(--error-text);
    border: 1px solid #e8274b; border-radius: 20px;
    padding: 4px 13px; margin: 3px; font-size: 13px; font-weight: 500;
}
.section-badge {
    display: inline-block;
    background: linear-gradient(135deg, #e8274b, #c41f3b);
    color: white; border-radius: 6px; padding: 3px 10px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.05em;
    text-transform: uppercase; margin-bottom: 8px;
}
.info-chip-ok {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--success-bg); color: var(--success-text);
    border: 1px solid var(--success-border); border-radius: 8px;
    padding: 6px 12px; font-size: 13px; margin-bottom: 6px;
}
.info-chip-warn {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--warn-bg); color: var(--warn-text);
    border: 1px solid var(--warn-text); border-radius: 8px;
    padding: 6px 12px; font-size: 13px; margin-bottom: 6px;
}

#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

def score_color(s):
    if s >= 0.75: return 'var(--success-text)'
    if s >= 0.60: return '#58a6ff'
    if s >= 0.45: return 'var(--warn-text)'
    return 'var(--text-muted)'

def score_label(s):
    if s >= 0.75: return 'Sangat Cocok'
    if s >= 0.60: return 'Cocok'
    if s >= 0.45: return 'Cukup Cocok'
    return 'Kurang Cocok'

def score_bg(s):
    if s >= 0.75: return 'var(--success-bg)'
    if s >= 0.60: return '#0d1f3c'
    if s >= 0.45: return 'var(--warn-bg)'
    return '#1a1a1a'

def get_learning_resource(skill):
    res = {
        'Sql': ('Coursera, DataCamp', '1 bulan'),
        'Aws': ('AWS Skill Builder', '2 bulan'),
        'Docker': ('Udemy, Docker Docs', '1-2 bulan'),
        'Linux': ('Linux Foundation', '1 bulan'),
        'Cloud': ('Google Cloud Skills', '2-3 bulan'),
        'Python': ('Dicoding, Kaggle', '2 bulan'),
        'Scala': ('Rock the JVM', '2-4 bulan'),
        'Kubernetes': ('KodeKloud', '1-2 bulan'),
    }
    return res.get(skill.title(), ('YouTube, Udemy', '1-3 bulan'))

def score_color(s):
    if s >= 0.75: return "var(--success-text)"
    if s >= 0.60: return "var(--info-border)"
    if s >= 0.45: return "var(--warn-text)"
    return "var(--text-muted)"

def score_label(s):
    if s >= 0.75: return "Sangat Cocok"
    if s >= 0.60: return "Cocok"
    if s >= 0.45: return "Cukup Cocok"
    return "Kurang Cocok"

def score_bg(s):
    if s >= 0.75: return "var(--success-bg)"
    if s >= 0.60: return "var(--info-bg)"
    if s >= 0.45: return "var(--warn-bg)"
    return "var(--border-light)"

def get_learning_resource(skill):
    res = {
        "Sql": ("Coursera, DataCamp", "1 bulan"),
        "Aws": ("AWS Skill Builder", "2 bulan"),
        "Docker": ("Udemy, Docker Docs", "1-2 bulan"),
        "Linux": ("Linux Foundation", "1 bulan"),
        "Cloud": ("Google Cloud Skills", "2-3 bulan"),
        "Python": ("Dicoding, Kaggle", "2 bulan"),
        "Scala": ("Rock the JVM", "2-4 bulan"),
        "Kubernetes": ("KodeKloud", "1-2 bulan"),
    }
    return res.get(skill, ("YouTube, Udemy", "1-3 bulan"))

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
DEFAULTS = [
    ("step", 1),
    ("model_choice", None),
    ("top_k", 5),
    ("uploaded_file_bytes", None),
    ("uploaded_file_name", None),
    ("parse_failed", False),
    ("manual_skills",""),("manual_edu",""),("manual_exp",""),
    ("cv_info", {}),
    ("skills_match", []),
    ("recommended_jobs", []),
    ("skill_gap", []),
    ("cv_text_tfidf", ""),
    ("cv_text_embed", ""),
    ("selected_job_title", None),
    ("selected_job_company", None),
    ("selected_job_score", None),
]
for k, v in DEFAULTS:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def render_navbar():
    logo_html = ""
    if LOGO_B64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:48px;width:auto;max-width:80px;object-fit:contain;flex-shrink:0;" />'
    else:
        logo_html = '<div style="font-size:28px;">🎯</div>'

    st.markdown(f"""
    <div style="background:var(--card-bg);border-bottom:2px solid #e8274b;
    padding:10px 0;display:flex;align-items:center;gap:14px;margin-bottom:1.5rem;">
        {logo_html}
        <div>
            <div style="font-size:22px;font-weight:700;color:var(--text-head);line-height:1.1;">
                JobMatch <span style="color:#e8274b;">AI</span>
            </div>
            <div style="font-size:12px;color:var(--text-muted);">
                AI-Based CV Analyzer &amp; Job Recommendation System
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_steps(current):
    steps = ["Upload CV","Pilih Model","Rekomendasi","Skill Insight"]
    cols  = st.columns(len(steps) * 2 - 1)
    for i, label in enumerate(steps):
        n = i + 1
        col_idx = i * 2
        if n < current:
            cbg,cfg,lc,sym = "#e8274b","var(--text-head)","#ff6b8a","✓"
            border = ""
        elif n == current:
            cbg,cfg,lc,sym = "#1a0a0e","#e8274b","#e8274b",str(n)
            border = "border:2px solid #e8274b;"
        else:
            cbg,cfg,lc,sym = "var(--card-bg)","var(--btn-disabled-text)","var(--btn-disabled-text)",str(n)
            border = "border:1px solid var(--border);"
        fw = "600" if n == current else "400"
        cols[col_idx].markdown(f"""
        <div style='text-align:center;padding:4px 0;'>
          <div style='width:34px;height:34px;border-radius:50%;background:{cbg};
          color:{cfg};display:flex;align-items:center;justify-content:center;
          font-size:14px;font-weight:600;margin:0 auto;{border}'>{sym}</div>
          <div style='font-size:11px;color:{lc};margin-top:6px;font-weight:{fw};'>{label}</div>
        </div>""", unsafe_allow_html=True)
        if i < len(steps) - 1:
            lc2 = "#e8274b" if (i+1) < current else "var(--border)"
            cols[col_idx+1].markdown(
                f"<div style='height:2px;background:{lc2};margin-top:20px;border-radius:2px;'></div>",
                unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)


def card_metric(label, value, sub="", color="#e8274b"):
    return f"""
    <div style='background:var(--card-bg);border:1px solid var(--border);border-top:3px solid {color};
    border-radius:12px;padding:16px;text-align:center;height:100%;'>
        <div style='font-size:11px;color:var(--text-muted);margin-bottom:4px;text-transform:uppercase;
        letter-spacing:0.06em;'>{label}</div>
        <div style='font-size:28px;font-weight:700;color:{color};'>{value}</div>
        <div style='font-size:11px;color:#556677;margin-top:2px;'>{sub}</div>
    </div>"""

def render_cv_detail():
    cv = st.session_state.cv_info
    container = st.container(border=True)
    with container:
        fields = [
            ("NAMA LENGKAP", cv.get("nama","—") or "—",      "var(--text-main)", "14px"),
            ("EMAIL",        cv.get("email","—") or "—",     "var(--text-main)", "14px"),
            ("NOMOR HP",     cv.get("phone","—") or "—",     "var(--text-main)", "14px"),
            ("RINGKASAN",    (cv.get("ringkasan","—") or "—")[:150] + "...", "var(--text-main)", "13px"),
            ("PENDIDIKAN",   cv.get("pendidikan","—") or "—","var(--text-main)", "14px"),
            ("PENGALAMAN",   cv.get("pengalaman","—") or "—","var(--text-main)", "14px"),
        ]
        for label, val, color, size in fields:
            st.markdown(f"<div style='font-size:11px;color:var(--text-muted);margin-bottom:2px;'>{label}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:{size};color:{color};margin-bottom:10px;font-weight:500;'>{val}</div>", unsafe_allow_html=True)

        st.markdown("<div style='font-size:11px;color:var(--text-muted);margin-bottom:2px;'>BAHASA CV</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:13px;color:#58a6ff;margin-bottom:10px;'>{cv.get('bahasa','—')}</div>", unsafe_allow_html=True)


def get_plotly_layout():
    return dict(
        paper_bgcolor="#ffffff" if is_light else "#161b22", 
        plot_bgcolor="#ffffff" if is_light else "#161b22",
        font=dict(color="#24292f" if is_light else "#c9d1d9", size=12),
        margin=dict(t=36, b=12, l=12, r=12),
    )

# ══════════════════════════════════════════════════════════════
# RENDER MAIN
# ══════════════════════════════════════════════════════════════
render_navbar()
render_steps(st.session_state.step)

# ──────────────────────────────────────────────────────────────
# STEP 1 — Upload CV
# ──────────────────────────────────────────────────────────────
if st.session_state.step == 1:
    col_main, col_side = st.columns([3, 2], gap="large")

    with col_main:
        st.subheader("Upload CV Anda")
        st.caption("Format PDF · Maks. 200 MB · Informasi diekstrak otomatis menggunakan NLP")

        st.markdown("""
        <div style='display:flex;flex-direction:column;gap:6px;margin:10px 0 14px 0;'>
            <div class='info-chip-ok'><span>✓</span><span>Mendukung PDF berbasis teks (bukan scan)</span></div>
            <div class='info-chip-warn'><span>⚠</span><span>Jika CV tidak terbaca dengan baik, Anda dapat mengisi informasi secara manual</span></div>
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader("CV PDF", type=["pdf"], label_visibility="collapsed")

        if uploaded and not uploaded.name.lower().endswith(".pdf"):
            st.error("❌ **File bukan PDF.** Harap upload file CV dalam format **.pdf**.")
            uploaded = None

        if uploaded is not None and st.session_state.uploaded_file_name != uploaded.name:
            st.session_state.uploaded_file_bytes = uploaded.read()
            st.session_state.uploaded_file_name  = uploaded.name
            
            with st.spinner("🔍 Mengekstrak dan menganalisis CV dengan NLP pipeline..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(st.session_state.uploaded_file_bytes)
                    tmp_path = tmp.name
                
                try:
                    parsed_data = parse_cv(tmp_path)
                    os.remove(tmp_path)
                    
                    raw_text = parsed_data.get('text', '')
                    translated_text = safe_translate(clean_text(raw_text))
                    
                    st.session_state.cv_text_tfidf = preprocess_tfidf(translated_text)
                    st.session_state.cv_text_embed = preprocess_embed(translated_text)
                    
                    st.session_state.parse_failed = False
                    st.session_state.cv_info = {
                        "nama": parsed_data.get("candidate_name", ""),
                        "email": parsed_data.get("email", ""),
                        "phone": parsed_data.get("phone", ""),
                        "ringkasan": parsed_data.get("summary", ""),
                        "pendidikan": parsed_data.get("degree", "") + " " + parsed_data.get("university", ""),
                        "pengalaman": parsed_data.get("experience", ""),
                        "bahasa": "Diproses dengan NLP (Translated)"
                    }
                    st.session_state.skills_match = [s.strip() for s in parsed_data.get('skills', '').split(',') if s.strip()]
                    if not st.session_state.skills_match:
                        st.session_state.skills_match = ["Python", "SQL", "Teamwork"]
                except Exception as e:
                    st.session_state.parse_failed = True

        has_file = st.session_state.uploaded_file_bytes is not None

        if has_file:
            fname = st.session_state.uploaded_file_name

            if st.session_state.parse_failed:
                st.warning("⚠️ **CV tidak dapat dibaca dengan baik.**")
            else:
                st.success(f"✅ **{fname}** berhasil diproses!")
                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("**📋 Detail Informasi**")
                render_cv_detail()

                st.markdown("**🏷️ Skills Terdeteksi**")
                pills = "".join(f'<span class="pill-match">✓ {s}</span>' for s in st.session_state.skills_match)
                st.markdown(
                    f"<div style='background:var(--card-bg);border:1px solid var(--border);"
                    f"border-radius:10px;padding:14px;'>{pills}</div>",
                    unsafe_allow_html=True
                )

                st.markdown("<br>", unsafe_allow_html=True)

                with st.expander("⚙️ Hasil ekstraksi kurang tepat? Koreksi manual"):
                    st.caption("Perbaiki informasi yang tidak sesuai, lalu klik Terapkan.")
                    cv = st.session_state.cv_info
                    k_nama       = st.text_input("Koreksi Nama Lengkap", value=cv.get("nama",""))
                    k_email      = st.text_input("Koreksi Email",        value=cv.get("email",""))
                    k_phone      = st.text_input("Koreksi Nomor HP",     value=cv.get("phone",""))
                    k_ringkasan  = st.text_area("Koreksi Ringkasan",    value=cv.get("ringkasan",""), height=80)
                    k_skills     = st.text_area("Koreksi Skills (pisahkan koma)",
                                                value=", ".join(st.session_state.skills_match), height=60)
                    k_pendidikan = st.text_input("Koreksi Pendidikan",  value=cv.get("pendidikan",""))
                    k_pengalaman = st.text_input("Koreksi Pengalaman",  value=cv.get("pengalaman",""))

                    if st.button("✅ Terapkan Koreksi", type="primary"):
                        st.session_state.cv_info = {
                            **cv, "nama": k_nama, "email": k_email, "phone": k_phone,
                            "ringkasan": k_ringkasan, "pendidikan": k_pendidikan, "pengalaman": k_pengalaman,
                        }
                        st.session_state.skills_match = [s.strip() for s in k_skills.split(",") if s.strip()]
                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Pilih Model Similarity →", type="primary", use_container_width=True):
                    st.session_state.step = 2
                    st.rerun()
    
    with col_side:
        st.markdown('<div class="section-badge">CARA KERJA</div>', unsafe_allow_html=True)
        st.subheader("Bagaimana sistem bekerja?")
        steps_info = [
            ("📤","Upload CV",     "Sistem membaca file PDF Anda"),
            ("🔍","Ekstraksi NLP", "Skill, pendidikan & pengalaman diekstrak otomatis"),
            ("⚙️","Pilih Model",   "Pilih algoritma pencocokan terbaik"),
            ("📋","Rekomendasi",   "Top-5 lowongan paling cocok ditampilkan"),
            ("💡","Skill Insight", "Analisis gap & saran pengembangan karir"),
        ]
        for icon, title, desc in steps_info:
            st.markdown(f"""
            <div style='display:flex;align-items:flex-start;gap:12px;
            background:var(--card-bg);border:1px solid var(--border);border-radius:10px;
            padding:12px 14px;margin-bottom:8px;'>
                <div style='font-size:22px;flex-shrink:0;'>{icon}</div>
                <div>
                    <div style='font-size:13px;font-weight:600;color:var(--text-head);margin-bottom:2px;'>{title}</div>
                    <div style='font-size:12px;color:var(--text-muted);'>{desc}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# STEP 2 — Pilih Model
# ──────────────────────────────────────────────────────────────
elif st.session_state.step == 2:
    st.subheader("Pilih Model Similarity")
    st.caption("Sistem menggunakan pendekatan komparatif. Pilih salah satu model untuk melanjutkan.")
    st.markdown("<br>", unsafe_allow_html=True)

    MODELS = [
        {
            "name":"TF-IDF","icon":"📝",
            "desc":"Keyword-based matching. Cepat, ringan, dan mudah diinterpretasi. Ideal sebagai baseline komparasi.",
            "badge":"BASELINE","badge_color":"var(--text-muted)","badge_bg":"var(--border-light)",
            "pros":["Sangat cepat","Mudah diinterpretasi"],
            "cons":["Tidak memahami sinonim","Kurang kontekstual"],
        },
        {
            "name":"TF-IDF + SVD","icon":"🔢",
            "desc":"TF-IDF dengan reduksi dimensi SVD. Menangkap hubungan laten antar kata untuk representasi lebih kaya.",
            "badge":"IMPROVED","badge_color":"#58a6ff","badge_bg":"#0d1f3c",
            "pros":["Menangkap relasi laten"],
            "cons":["Lebih kompleks"],
        },
        {
            "name":"Embedding","icon":"🧠",
            "desc":"Sentence-BERT semantic similarity. Paling akurat dan kontekstual — memahami makna sebenarnya.",
            "badge":"⭐ TERBAIK","badge_color":"var(--success-text)","badge_bg":"var(--success-bg)",
            "pros":["Memahami semantik & sinonim","Akurasi tertinggi"],
            "cons":["Lebih berat secara komputasi"],
        },
    ]

    model_cols = st.columns(3, gap="medium")
    for col, m in zip(model_cols, MODELS):
        selected = st.session_state.model_choice == m["name"]
        border   = "2px solid #e8274b" if selected else "1px solid var(--border)"
        bg       = "#1a0a0e"           if selected else "var(--card-bg)"
        glow     = "box-shadow:0 0 16px rgba(232,39,75,0.25);" if selected else ""
        pros_html = "".join(f"<div style='font-size:11px;color:var(--success-text);margin-bottom:3px;'>✓ {p}</div>" for p in m["pros"])
        cons_html = "".join(f"<div style='font-size:11px;color:var(--text-muted);margin-bottom:3px;'>• {c}</div>" for c in m["cons"])

        col.markdown(f"""
        <div style='border:{border};background:{bg};border-radius:14px;
        padding:24px 16px;text-align:center;{glow}margin-bottom:10px;
        min-height:320px;display:flex;flex-direction:column;justify-content:flex-start;'>
            <div style='font-size:36px;margin-bottom:8px;'>{m["icon"]}</div>
            <div style='font-size:16px;font-weight:700;color:var(--text-head);margin-bottom:6px;'>{m["name"]}</div>
            <span style='background:{m["badge_bg"]};color:{m["badge_color"]};
            border-radius:20px;padding:3px 12px;font-size:11px;font-weight:600;'>{m["badge"]}</span>
            <div style='font-size:12px;color:var(--text-muted);margin:12px 0 10px;line-height:1.55;'>{m["desc"]}</div>
            <div style='text-align:left;'>{pros_html}{cons_html}</div>
        </div>""", unsafe_allow_html=True)

        btn_label = "✓ Dipilih" if selected else f"Pilih {m['name']}"
        btn_type  = "primary"   if selected else "secondary"
        if col.button(btn_label, key=m["name"], use_container_width=True, type=btn_type):
            st.session_state.model_choice = m["name"]
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col_guide, col_table = st.columns([1, 1], gap="large")

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_next = st.columns(2)
    if col_back.button("← Kembali", use_container_width=True):
        st.session_state.step = 1
        st.rerun()
    model_ok = st.session_state.model_choice is not None
    if col_next.button("Lihat Rekomendasi →" if model_ok else "⚠️ Pilih model terlebih dahulu", type="primary" if model_ok else "secondary", use_container_width=True, disabled=not model_ok):
        # PROSES REKOMENDASI AI
        if not df_jobs.empty:
            with st.spinner(f"Menghitung kecocokan dengan {st.session_state.model_choice}..."):
                if "TF-IDF (Baseline)" in st.session_state.model_choice or "TF-IDF" == st.session_state.model_choice:
                    vectorizer, job_tfidf = prepare_tfidf_models(df_jobs)
                    cv_vec = vectorizer.transform([st.session_state.cv_text_tfidf])
                    scores = cosine_similarity(cv_vec, job_tfidf)[0]
                elif "SVD" in st.session_state.model_choice:
                    vectorizer, job_tfidf = prepare_tfidf_models(df_jobs)
                    svd, job_svd = prepare_svd_model(job_tfidf)
                    cv_vec = vectorizer.transform([st.session_state.cv_text_tfidf])
                    cv_svd = svd.transform(cv_vec)
                    scores = cosine_similarity(cv_svd, job_svd)[0]
                else: # Embedding
                    sbert = load_sentence_transformer()
                    job_embeddings = prepare_embeddings(df_jobs, sbert)
                    cv_emb = sbert.encode([st.session_state.cv_text_embed])
                    scores = cosine_similarity(cv_emb, job_embeddings)[0]

                top_indices = scores.argsort()[-15:][::-1]
                rec_jobs = []
                for rank, idx in enumerate(top_indices, 1):
                    row = df_jobs.iloc[idx]
                    rec_jobs.append({
                        "rank": rank,
                        "title": row.get("Posisi", "Unknown"),
                        "company": row.get("Perusahaan", "Unknown"),
                        "location": row.get("Lokasi", "Unknown"),
                        "type": row.get("Type", "Unknown"),
                        "score": float(min(max(scores[idx], 0.0), 1.0)),
                        "requirements": row.get("Requirements", "")
                    })
                st.session_state.recommended_jobs = rec_jobs
                
                # Setup Skill Gap
                top_job = rec_jobs[0] if rec_jobs else None
                if top_job:
                    req_text = top_job['requirements'].lower()
                    cv_skills = [s.lower() for s in st.session_state.skills_match]
                    common_tech = ["sql", "agile", "aws", "docker", "linux", "cloud", "scrum", "rest api", "kubernetes", "scala", "spark", "hadoop", "tableau"]
                    gap = [t.capitalize() for t in common_tech if t in req_text and t not in cv_skills][:3]
                    if not gap: gap = ["Teknologi Lanjutan", "Sertifikasi Spesifik"]
                    st.session_state.skill_gap = gap

        st.session_state.step = 3
        st.rerun()

# ──────────────────────────────────────────────────────────────
# STEP 3 — Rekomendasi
# ──────────────────────────────────────────────────────────────
elif st.session_state.step == 3:
    k = st.session_state.top_k
    st.subheader(f"Top-{k} Rekomendasi Pekerjaan")
    st.caption(f"Model: **{st.session_state.model_choice}** · Diurutkan berdasarkan cosine similarity")
    st.markdown("<br>", unsafe_allow_html=True)

    jobs_list = st.session_state.get('recommended_jobs', [])
    top_score = jobs_list[0]['score'] if jobs_list else 0.0

    kc1, kc2, kc3, kc4 = st.columns(4)
    kc1.markdown(card_metric("🏆 Top Match",  f"{top_score:.2f}",  "Skor tertinggi CV ini",      "#e8274b"), unsafe_allow_html=True)
    kc2.markdown(card_metric("📂 Dianalisis", f"{len(df_jobs)}", "Total Lowongan diproses",    "#58a6ff"), unsafe_allow_html=True)
    kc3.markdown(card_metric("🔑 Skills",     f"{len(st.session_state.skills_match)}", "skill terdeteksi dari CV",   "var(--success-text)"), unsafe_allow_html=True)
    kc4.markdown(card_metric("⚠️ Skill Gap",  f"{len(st.session_state.get('skill_gap', []))}", "skill perlu ditingkatkan",   "var(--warn-text)"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab_list, tab_chart = st.tabs(["  📋  Daftar Lowongan  ", "  📊  Visualisasi Skor  "])

    with tab_list:
        st.markdown("""
        <div style='display:flex;gap:16px;flex-wrap:wrap;margin-bottom:14px;'>
            <span style='font-size:12px;color:var(--success-text);'>● ≥ 75% — Sangat Cocok</span>
            <span style='font-size:12px;color:#58a6ff;'>● 60–74% — Cocok</span>
            <span style='font-size:12px;color:var(--warn-text);'>● 45–59% — Cukup</span>
            <span style='font-size:12px;color:var(--text-muted);'>● &lt; 45% — Kurang</span>
        </div>""", unsafe_allow_html=True)

        col_left, col_right = st.columns(2, gap='medium')
        jobs_k = jobs_list[:k]
        for idx, job in enumerate(jobs_k):
            sc, color, label, bg_col = job["score"], score_color(job["score"]), score_label(job["score"]), score_bg(job["score"])
            is_selected = (st.session_state.get("selected_job_title") == job["title"] and
                           st.session_state.get("selected_job_company") == job["company"])
            selected_border = "border-left: 4px solid var(--success-text);" if is_selected else ""
            selected_bg = "background: var(--success-bg);" if is_selected else ""
            dipilih_badge = "<span style='background:var(--success-bg);color:var(--success-text);border:1px solid var(--success-border);border-radius:20px;padding:2px 10px;font-size:11px;font-weight:600;margin-left:6px;'>✓ Dipilih</span>" if is_selected else ""

            # Progress bar dimasukkan ke dalam HTML card — hindari st.progress() di antara HTML & expander
            card_border = "border-left: 4px solid var(--success-text);" if is_selected else "border-left: 4px solid #e8274b;"
            card_bg = "var(--success-bg)" if is_selected else "var(--card-bg)"
            progress_pct = int(sc * 100)
            st.markdown(f"""
            <div style='background:{card_bg};border:1px solid var(--border);{card_border}border-radius:12px;
            padding:16px 18px;margin-bottom:4px;'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:16px;'>
                    <div style='flex:1;min-width:0;'>
                        <div style='display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap;'>
                            <span style='background:#e8274b;color:var(--text-head);border-radius:6px;
                            padding:3px 9px;font-size:11px;font-weight:600;flex-shrink:0;'>#{job['rank']}</span>
                            <strong style='font-size:15px;color:var(--text-head);'>{job['title']}</strong>{dipilih_badge}
                        </div>
                        <div style='font-size:12px;color:var(--text-muted);margin-bottom:10px;'>
                            🏢 {job['company']} &nbsp;·&nbsp; 📍 {job['location']} &nbsp;·&nbsp; 🕒 {job['type']}
                        </div>
                        <div style='background:var(--border-light);border-radius:4px;height:5px;width:100%;'>
                            <div style='background:{color};height:5px;border-radius:4px;width:{progress_pct}%;'></div>
                        </div>
                    </div>
                    <div style='text-align:right;flex-shrink:0;'>
                        <div style='font-size:22px;font-weight:700;color:{color};margin-bottom:2px;'>{sc*100:.0f}%</div>
                        <div style='font-size:10px;font-weight:600;color:{color};
                        background:{bg_col};border-radius:10px;padding:2px 8px;display:inline-block;'>{label}</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
            with st.expander(f"🔍 Lihat Detail — {job['title']}"):
                d1, d2, d3, d4 = st.columns(4)
                d1.markdown(f"""
                <div style='background:var(--card-bg);border:1px solid var(--border);border-top:3px solid {color};
                border-radius:10px;padding:12px;text-align:center;'>
                    <div style='font-size:10px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;'>Skor Kecocokan</div>
                    <div style='font-size:26px;font-weight:700;color:{color};'>{sc*100:.0f}%</div>
                    <div style='font-size:11px;font-weight:600;color:{color};background:{bg_col};
                    border-radius:10px;padding:2px 8px;display:inline-block;margin-top:2px;'>{label}</div>
                </div>""", unsafe_allow_html=True)
                d2.markdown(f"""
                <div style='background:var(--card-bg);border:1px solid var(--border);border-top:3px solid #58a6ff;
                border-radius:10px;padding:12px;text-align:center;'>
                    <div style='font-size:10px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;'>Perusahaan</div>
                    <div style='font-size:15px;font-weight:600;color:var(--text-main);'>{job['company']}</div>
                    <div style='font-size:11px;color:var(--text-muted);margin-top:4px;'>📍 {job['location']}</div>
                </div>""", unsafe_allow_html=True)
                d3.markdown(f"""
                <div style='background:var(--card-bg);border:1px solid var(--border);border-top:3px solid var(--warn-text);
                border-radius:10px;padding:12px;text-align:center;'>
                    <div style='font-size:10px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;'>Tipe Pekerjaan</div>
                    <div style='font-size:15px;font-weight:600;color:var(--text-main);'>{job['type']}</div>
                    <div style='font-size:11px;color:var(--text-muted);margin-top:4px;'>Ranking #{job['rank']} dari {k}</div>
                </div>""", unsafe_allow_html=True)
                d4.markdown(f"""
                <div style='background:var(--card-bg);border:1px solid var(--border);border-top:3px solid var(--success-text);
                border-radius:10px;padding:12px;text-align:center;'>
                    <div style='font-size:10px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;'>Estimasi Gaji</div>
                    <div style='font-size:13px;font-weight:600;color:var(--success-text);'>{job.get('gaji', 'TBA')}</div>
                    <div style='margin-top:6px;'><a href="{job.get('link', '#')}" target="_blank" style='font-size:11px;color:#58a6ff;text-decoration:none;'>🔗 Lihat Lowongan</a></div>
                </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                skill_cols = st.columns(2)
                matched   = st.session_state.skills_match[:5]
                not_match = st.session_state.skill_gap
                with skill_cols[0]:
                    st.markdown("<div style='font-size:12px;color:var(--success-text);font-weight:600;margin-bottom:6px;'>✓ Skills yang Cocok</div>", unsafe_allow_html=True)
                    pills_match = "".join(f'<span class="pill-match">✓ {s}</span>' for s in matched)
                    match_content = pills_match if pills_match else '<span style="color:var(--text-muted);font-size:12px;">—</span>'
                    st.markdown(f"<div style='display:flex;flex-wrap:wrap;gap:6px;'>{match_content}</div>", unsafe_allow_html=True)
                with skill_cols[1]:
                    st.markdown("<div style='font-size:12px;color:var(--error-text);font-weight:600;margin-bottom:6px;'>✗ Skills yang Belum Dimiliki</div>", unsafe_allow_html=True)
                    pills_gap = "".join(f'<span class="pill-gap">✗ {s}</span>' for s in not_match)
                    gap_content = pills_gap if pills_gap else '<span style="color:var(--text-muted);font-size:12px;">—</span>'
                    st.markdown(f"<div style='display:flex;flex-wrap:wrap;gap:6px;'>{gap_content}</div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,#1a0a0e,#2e0a18);
                border:1px solid #e8274b;border-radius:10px;padding:12px;'>
                    <div style='font-size:11px;color:#e8274b;font-weight:600;margin-bottom:4px;'>💡 Saran untuk Posisi Ini</div>
                    <div style='font-size:12px;color:var(--text-main);line-height:1.6;'>
                        Tingkatkan skor kecocokan dengan mempelajari skill yang belum dimiliki.
                        Lihat tab <strong style='color:#e8274b;'>Skill Gap & Saran</strong> untuk panduan belajar lengkap.
                    </div>
                </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"✅ Pilih '{job['title']} @ {job['company']}' untuk Skill Insight", key=f"pick_{idx}", use_container_width=True, type="primary"):
                    st.session_state.selected_job_title   = job["title"]
                    st.session_state.selected_job_company = job["company"]
                    st.session_state.selected_job_score   = job["score"]
                    st.rerun()
    with tab_chart:
        fig = go.Figure(go.Bar(
            x=[j["score"] for j in jobs_k],
            y=[j["title"] + " (" + j["company"] + ")"  for j in jobs_k],
            orientation="h",
            marker_color=[score_color(j["score"]) for j in jobs_k],
            text=[f"{j['score']:.2f}" for j in jobs_k],
            textposition="outside",
            textfont=dict(color="var(--text-main)"),
        ))
        fig.update_layout(
            **get_plotly_layout(),
            xaxis=dict(range=[0, 1.15], gridcolor="var(--border-light)", color="var(--text-muted)"),
            yaxis=dict(autorange="reversed", color="var(--text-main)"),
            title=dict(text="Skor Cosine Similarity per Lowongan", font=dict(color="var(--text-head)", size=14)),
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    job_picked = st.session_state.get("selected_job_title") is not None
    if not job_picked:
        st.warning("⚠️ Pilih salah satu pekerjaan terlebih dahulu untuk melihat Skill Insight.")

    col_back, col_next = st.columns(2)
    if col_back.button("← Kembali", use_container_width=True):
        st.session_state.step = 2
        st.rerun()
    if col_next.button(
        "Lihat Skill Insight →" if job_picked else "⚠️ Pilih pekerjaan terlebih dahulu",
        type="primary" if job_picked else "secondary",
        use_container_width=True,
        disabled=not job_picked,
    ):
        st.session_state.step = 4
        st.rerun()

# ──────────────────────────────────────────────────────────────
# STEP 4 — Skill Insight
# ──────────────────────────────────────────────────────────────
elif st.session_state.step == 4:
    st.subheader("Skill Insight")
    st.caption(f"Analisis berdasarkan posisi yang Anda pilih: **{st.session_state.get('selected_job_title','—')} @ {st.session_state.get('selected_job_company','—')} ({st.session_state.get('selected_job_score', 0)*100:.0f}% — {score_label(st.session_state.get('selected_job_score', 0))})**")
    st.markdown("<br>", unsafe_allow_html=True)

    skills_now = st.session_state.skills_match
    skill_gap = st.session_state.skill_gap
    
    si1, si2, si3 = st.columns(3)
    selected_score = st.session_state.get('selected_job_score', 0.82)
    si1.markdown(card_metric("✅ Skills Dimiliki",   f"{len(skills_now)} skill", "Terdeteksi dari CV",         "var(--success-text)"), unsafe_allow_html=True)
    si2.markdown(card_metric("⚠️ Skill Gap",         f"{len(skill_gap)} skill", "Perlu dipelajari",           "var(--warn-text)"), unsafe_allow_html=True)
    si3.markdown(card_metric("🏆 Tingkat Kecocokan", f"{selected_score*100:.0f}%", "Terbaik dari lowongan diproses","#e8274b"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # FIX 9: Skill Match, Radar Chart, Skill Gap disatukan tanpa tab
    selected_title   = st.session_state.get('selected_job_title', '—')
    selected_company = st.session_state.get('selected_job_company', '—')

    st.markdown("#### ✅ Skills yang sudah Anda miliki")
    st.caption(f"Skills ini cocok dengan kebutuhan posisi {selected_title} @ {selected_company}")
    match_cols = st.columns(3)
    for i, skill in enumerate(skills_now):
        match_cols[i % 3].markdown(f"""
        <div style='background:var(--success-bg);border:1px solid var(--success-border);border-radius:10px;
        padding:10px 14px;margin-bottom:8px;display:flex;align-items:center;gap:8px;'>
            <span style='color:var(--success-text);font-size:16px;'>✓</span>
            <span style='color:var(--text-main);font-size:13px;font-weight:500;'>{skill}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📊 Radar Chart — Profil Anda vs Kebutuhan Lowongan")
    cats = ["Python & DS","ML & AI","Data Eng.","NLP","MLOps"]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[95,88,60,90,40,95], theta=cats+[cats[0]], fill="toself", name="Profil Anda",
        line_color="#e8274b", fillcolor="rgba(232,39,75,0.15)"))
    fig.add_trace(go.Scatterpolar(
        r=[90,85,80,85,75,90], theta=cats+[cats[0]], fill="toself", name="Persyaratan Lowongan",
        line_color="#0969da" if is_light else "#58a6ff", fillcolor="rgba(9,105,218,0.08)" if is_light else "rgba(88,166,255,0.08)"))
    fig.update_layout(
        polar=dict(bgcolor="#ffffff" if is_light else "#161b22",
                   radialaxis=dict(visible=True,range=[0,100],color="#57606a" if is_light else "#8b949e",gridcolor="#d0d7de" if is_light else "#2d2d2d"),
                   angularaxis=dict(color="#24292f" if is_light else "#c9d1d9")),
        paper_bgcolor="#f6f8fa" if is_light else "#0d1117", 
        plot_bgcolor="#f6f8fa" if is_light else "#0d1117", 
        font=dict(color="#24292f" if is_light else "#c9d1d9"),
        legend=dict(bgcolor="#ffffff" if is_light else "#161b22", bordercolor="#d0d7de" if is_light else "#2d2d2d", borderwidth=1,
                    orientation="h",yanchor="bottom",y=-0.15),
        margin=dict(t=20,b=40), height=380,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Merah = profil Anda · Biru = persyaratan lowongan.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📚 Skills yang perlu ditingkatkan")
    st.caption("Pelajari skill berikut untuk meningkatkan kecocokan Anda")
    for skill in skill_gap:
        src, dur = get_learning_resource(skill)
        with st.expander(f"📚  {skill}  —  Estimasi: {dur}"):
            gc1, gc2 = st.columns([1, 2])
            with gc1:
                st.markdown(f"""
                <div style='background:var(--error-bg);border:1px solid #e8274b;border-radius:10px;
                padding:14px;text-align:center;'>
                    <div style='font-size:28px;margin-bottom:6px;'>⚠️</div>
                    <div style='font-size:13px;font-weight:600;color:var(--error-text);'>{skill}</div>
                    <div style='font-size:11px;color:var(--text-muted);margin-top:4px;'>Belum terdeteksi</div>
                </div>""", unsafe_allow_html=True)
            with gc2:
                st.markdown(f"""
                <div style='background:var(--card-bg);border:1px solid var(--border);border-radius:10px;padding:14px;'>
                    <div style='font-size:11px;color:#e8274b;font-weight:600;margin-bottom:6px;'>💡 SUMBER BELAJAR</div>
                    <div style='font-size:14px;color:#58a6ff;margin-bottom:10px;'>{src}</div>
                    <div style='font-size:11px;color:var(--text-muted);margin-bottom:4px;'>⏱ ESTIMASI WAKTU</div>
                    <div style='font-size:16px;font-weight:600;color:var(--warn-text);'>{dur}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1a0a0e,#2e0a18);
    border:1px solid #e8274b;border-radius:12px;padding:16px;'>
        <div style='font-size:13px;color:#e8274b;font-weight:600;margin-bottom:8px;'>
            🎯 Prioritas Pengembangan Karir
        </div>
        <div style='font-size:13px;color:var(--text-main);line-height:1.7;'>
            1. <strong style="color:var(--success-text);">Apache Spark</strong> — Paling banyak dicari untuk posisi Data Scientist di Indonesia<br>
            2. <strong style="color:#58a6ff;">Kubernetes</strong> — Krusial untuk MLOps dan deployment model di production<br>
            3. <strong style="color:var(--warn-text);">Scala</strong> — Digunakan bersama Spark untuk big data engineering
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    bc, rc = st.columns(2)
    if bc.button("← Kembali", use_container_width=True):
        st.session_state.step = 3
        st.rerun()
    if rc.button("🔄 Analisis CV Baru", type="primary", use_container_width=True):
        for key in ["step","model_choice","top_k","uploaded_file_bytes","uploaded_file_name",
                    "parse_failed","manual_skills","manual_edu","manual_exp","cv_info","skills_match",
                    "selected_job_title","selected_job_company","selected_job_score"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

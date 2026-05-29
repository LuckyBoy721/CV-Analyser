import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import os
import base64

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="JobMatch AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
# FIX 1: Load logo dari file logo.png (bukan hardcode base64)
# Letakkan logo.png di folder yang sama dengan app.py ini
# ══════════════════════════════════════════════════════════════
def load_logo():
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

LOGO_B64 = load_logo()

# ══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
.stApp                          { background-color: #0d1117; color: #c9d1d9; }
[data-testid="stHeader"]        { background-color: #0d1117; border-bottom: 1px solid #21262d; }
section[data-testid="stMain"]   { background-color: #0d1117; }
.block-container                { max-width: 100% !important; padding: 3.2rem 3rem 1.5rem 3rem !important; }
h1,h2,h3,h4    { color: #ffffff !important; }
p,span,div      { color: #c9d1d9; }

[data-testid="metric-container"] {
    background: #161b22 !important; border: 1px solid #2d2d2d !important;
    border-radius: 12px !important; padding: 16px !important;
    border-top: 3px solid #e8274b !important;
}
[data-testid="stMetricValue"] { color: #e8274b !important; font-size: 28px !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; }
[data-testid="stMetricDelta"] { color: #ff6b8a !important; }

.stProgress > div > div > div > div { background: linear-gradient(90deg,#e8274b,#ff6b8a) !important; }
[data-testid="stProgressBar"]        { background-color: #21262d !important; }

.stButton > button {
    background-color: transparent; color: #e8274b;
    border: 1.5px solid #e8274b; border-radius: 8px;
    font-weight: 500; transition: all 0.2s ease;
}
.stButton > button:hover { background-color: #e8274b; color: #ffffff; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #e8274b, #c41f3b);
    border-color: #e8274b; color: #fff; font-weight: 600;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #ff4d6d, #e8274b);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(232,39,75,0.4);
}
.stButton > button:disabled {
    background-color: #161b22 !important; color: #4a4a4a !important;
    border-color: #2d2d2d !important; cursor: not-allowed !important;
}

[data-testid="stFileUploader"] {
    background: #161b22; border: 2px dashed #e8274b;
    border-radius: 12px; opacity: 0.9;
}
[data-testid="stFileUploader"] label { color: #8b949e !important; }

.stTextArea textarea, .stTextInput input {
    background: #161b22 !important; color: #e0eaf4 !important;
    border: 1px solid #2d2d2d !important; border-radius: 8px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus { border-color: #e8274b !important; }

/* FIX 7 & 9: Tab spacing - tambah gap antar tab */
.stTabs [data-baseweb="tab-list"] {
    background: #161b22; border-radius: 10px;
    padding: 4px; gap: 6px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; color: #8b949e; font-weight: 500;
    margin-right: 4px !important; padding-left: 16px !important; padding-right: 16px !important;
}
.stTabs [aria-selected="true"] { background: #e8274b !important; color: #fff !important; }

.streamlit-expanderHeader  { background: #161b22 !important; color: #e0eaf4 !important; border-radius: 10px !important; border-left: 3px solid #e8274b !important; }
.streamlit-expanderContent { background: #0d1117 !important; border: 1px solid #21262d !important; border-radius: 0 0 10px 10px !important; }

.stSuccess { background: #0a2e1a !important; border-color: #2ea043 !important; }
.stInfo    { background: #1a1f3a !important; border-color: #3b5bdb !important; }
.stWarning { background: #2e1f0a !important; border-color: #e8274b !important; }
.stError   { background: #2e0a0a !important; border-color: #e8274b !important; }

[data-testid="stSlider"] { color: #e8274b !important; }
.stSlider > div > div > div > div { background: #e8274b !important; }
[data-testid="stDataFrame"] { background: #161b22 !important; }
hr { border-color: #2d2d2d !important; margin: 0.8rem 0 !important; }

.pill-match {
    display: inline-block; background: #1a2e1a; color: #3fb950;
    border: 1px solid #2ea043; border-radius: 20px;
    padding: 4px 13px; margin: 3px; font-size: 13px; font-weight: 500;
}
.pill-gap {
    display: inline-block; background: #2e0a0a; color: #ff7b7b;
    border: 1px solid #e8274b; border-radius: 20px;
    padding: 4px 13px; margin: 3px; font-size: 13px; font-weight: 500;
}
.job-card {
    background: #161b22; border: 1px solid #2d2d2d;
    border-left: 4px solid #e8274b; border-radius: 12px;
    padding: 16px 18px; margin-bottom: 10px;
    transition: border-color 0.2s, background 0.2s;
}
.job-card:hover { background: #1c2128; border-left-color: #ff6b8a; }
.section-badge {
    display: inline-block;
    background: linear-gradient(135deg, #e8274b, #c41f3b);
    color: white; border-radius: 6px; padding: 3px 10px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.05em;
    text-transform: uppercase; margin-bottom: 8px;
}

/* FIX 2: Info chips untuk step 1 */
.info-chip-ok {
    display: inline-flex; align-items: center; gap: 6px;
    background: #0a2e1a; color: #3fb950;
    border: 1px solid #2ea043; border-radius: 8px;
    padding: 6px 12px; font-size: 13px; margin-bottom: 6px;
}
.info-chip-warn {
    display: inline-flex; align-items: center; gap: 6px;
    background: #2e1f0a; color: #d29922;
    border: 1px solid #d29922; border-radius: 8px;
    padding: 6px 12px; font-size: 13px; margin-bottom: 6px;
}

#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════
DUMMY_JOBS = [
    {"rank":1,"title":"Data Scientist",     "company":"Tokopedia",  "location":"Jakarta", "type":"Full-time","score":0.82},
    {"rank":2,"title":"ML Engineer",        "company":"Gojek",      "location":"Jakarta", "type":"Full-time","score":0.76},
    {"rank":3,"title":"NLP Engineer",       "company":"Traveloka",  "location":"Remote",  "type":"Remote",   "score":0.71},
    {"rank":4,"title":"Data Engineer",      "company":"Shopee",     "location":"Jakarta", "type":"Full-time","score":0.65},
    {"rank":5,"title":"Analytics Engineer", "company":"OVO",        "location":"Bandung", "type":"Hybrid",   "score":0.61},
    {"rank":6,"title":"AI Engineer",        "company":"Grab",       "location":"Jakarta", "type":"Full-time","score":0.55},
    {"rank":7,"title":"Data Analyst",       "company":"BCA",        "location":"Jakarta", "type":"Full-time","score":0.48},
]
SKILLS_GAP = ["Apache Spark","Kubernetes","Scala"]
SKILL_LEARN = {
    "Apache Spark": ("Databricks Academy, Coursera","2–3 bulan"),
    "Kubernetes":   ("KodeKloud, Linux Foundation",  "1–2 bulan"),
    "Scala":        ("Rock the JVM, Udemy",           "2–4 bulan"),
}

CV_INFO_DEFAULT = {
    "nama":       "Sintiya Risla Miftaqul Nikmah",
    "email":      "sintiya.risla@example.com",
    "phone":      "+62 812-3456-7890",
    "ringkasan":  "Data scientist pemula dengan pengalaman magang sebagai Data Analyst; berfokus pada pembersihan data, eksplorasi, dan pembuatan model ML sederhana.",
    "pendidikan": "S1 Sains Data – Universitas Negeri Surabaya",
    "pengalaman": "1 tahun (Intern Data Analyst)",
    "bahasa":     "Indonesia → ditranslasi ke Inggris",
}
SKILLS_MATCH_DEFAULT = ["Python","Machine Learning","SQL","NLP","Scikit-learn","Pandas","Numpy"]

def score_color(s):
    if s >= 0.75: return "#3fb950"
    if s >= 0.60: return "#58a6ff"
    if s >= 0.45: return "#d29922"
    return "#8b949e"

def score_label(s):
    if s >= 0.75: return "Sangat Cocok"
    if s >= 0.60: return "Cocok"
    if s >= 0.45: return "Cukup Cocok"
    return "Kurang Cocok"

def score_bg(s):
    if s >= 0.75: return "#0a2e1a"
    if s >= 0.60: return "#0d1f3c"
    if s >= 0.45: return "#2e1f0a"
    return "#1a1a1a"

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
DEFAULTS = [
    ("step", 1),
    ("model_choice", None),
    ("top_k", 5),
    # FIX 4: simpan uploaded_file_bytes agar tidak perlu upload ulang saat kembali
    ("uploaded_file_bytes", None),
    ("uploaded_file_name", None),
    ("parse_failed", False),
    ("manual_skills",""),("manual_edu",""),("manual_exp",""),
    # FIX 3: cv_info & skills di session_state agar koreksi auto update
    ("cv_info", CV_INFO_DEFAULT.copy()),
    ("skills_match", SKILLS_MATCH_DEFAULT[:]),
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
        # FIX 1: logo dari file, object-fit:contain agar proporsional, tidak lonjong
        logo_html = f'<img src="data:image/png;base64,{LOGO_B64}" style="height:48px;width:auto;max-width:80px;object-fit:contain;flex-shrink:0;" />'
    else:
        logo_html = '<div style="font-size:28px;">🎯</div>'

    st.markdown(f"""
    <div style="background:#161b22;border-bottom:2px solid #e8274b;
    padding:10px 0;display:flex;align-items:center;gap:14px;margin-bottom:1.5rem;">
        {logo_html}
        <div>
            <div style="font-size:22px;font-weight:700;color:#ffffff;line-height:1.1;">
                JobMatch <span style="color:#e8274b;">AI</span>
            </div>
            <div style="font-size:12px;color:#8b949e;">
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
            cbg,cfg,lc,sym = "#e8274b","#fff","#ff6b8a","✓"
            border = ""
        elif n == current:
            cbg,cfg,lc,sym = "#1a0a0e","#e8274b","#e8274b",str(n)
            border = "border:2px solid #e8274b;"
        else:
            cbg,cfg,lc,sym = "#161b22","#4a4a4a","#4a4a4a",str(n)
            border = "border:1px solid #2d2d2d;"
        fw = "600" if n == current else "400"
        cols[col_idx].markdown(f"""
        <div style='text-align:center;padding:4px 0;'>
          <div style='width:34px;height:34px;border-radius:50%;background:{cbg};
          color:{cfg};display:flex;align-items:center;justify-content:center;
          font-size:14px;font-weight:600;margin:0 auto;{border}'>{sym}</div>
          <div style='font-size:11px;color:{lc};margin-top:6px;font-weight:{fw};'>{label}</div>
        </div>""", unsafe_allow_html=True)
        if i < len(steps) - 1:
            lc2 = "#e8274b" if (i+1) < current else "#2d2d2d"
            cols[col_idx+1].markdown(
                f"<div style='height:2px;background:{lc2};margin-top:20px;border-radius:2px;'></div>",
                unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)


def card_metric(label, value, sub="", color="#e8274b"):
    return f"""
    <div style='background:#161b22;border:1px solid #2d2d2d;border-top:3px solid {color};
    border-radius:12px;padding:16px;text-align:center;height:100%;'>
        <div style='font-size:11px;color:#8b949e;margin-bottom:4px;text-transform:uppercase;
        letter-spacing:0.06em;'>{label}</div>
        <div style='font-size:28px;font-weight:700;color:{color};'>{value}</div>
        <div style='font-size:11px;color:#556677;margin-top:2px;'>{sub}</div>
    </div>"""


def render_cv_detail():
    """FIX 3: render detail CV dari session_state — auto update saat koreksi diterapkan"""
    cv = st.session_state.cv_info
    skills = st.session_state.skills_match

    container = st.container(border=True)
    with container:
        fields = [
            ("NAMA LENGKAP", cv.get("nama","—"),      "#e0eaf4", "14px"),
            ("EMAIL",        cv.get("email","—"),     "#e0eaf4", "14px"),
            ("NOMOR HP",     cv.get("phone","—"),     "#e0eaf4", "14px"),
            ("RINGKASAN",    cv.get("ringkasan","—"), "#c9d1d9", "13px"),
            ("PENDIDIKAN",   cv.get("pendidikan","—"),"#e0eaf4", "14px"),
            ("PENGALAMAN",   cv.get("pengalaman","—"),"#e0eaf4", "14px"),
        ]
        for label, val, color, size in fields:
            st.markdown(f"<div style='font-size:11px;color:#8b949e;margin-bottom:2px;'>{label}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:{size};color:{color};margin-bottom:10px;font-weight:500;'>{val}</div>", unsafe_allow_html=True)

        st.markdown("<div style='font-size:11px;color:#8b949e;margin-bottom:2px;'>BAHASA CV</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:13px;color:#58a6ff;margin-bottom:10px;'>{cv.get('bahasa','—')}</div>", unsafe_allow_html=True)

        
def plotly_dark():
    return dict(
        paper_bgcolor="#161b22", plot_bgcolor="#161b22",
        font=dict(color="#c9d1d9", size=12),
        margin=dict(t=36, b=12, l=12, r=12),
    )

# ══════════════════════════════════════════════════════════════
# RENDER
# ══════════════════════════════════════════════════════════════
render_navbar()
render_steps(st.session_state.step)

# ──────────────────────────────────────────────────────────────
# STEP 1 — Upload CV
# ──────────────────────────────────────────────────────────────
if st.session_state.step == 1:
    col_main, col_side = st.columns([3, 2], gap="large")

    with col_main:
        st.markdown('<div class="section-badge">STEP 1</div>', unsafe_allow_html=True)
        st.subheader("Upload CV Anda")
        st.caption("Format PDF · Maks. 200 MB · Informasi diekstrak otomatis menggunakan NLP")

        # FIX 2: info chips yang rapi, bukan st.caption biasa
        st.markdown("""
        <div style='display:flex;flex-direction:column;gap:6px;margin:10px 0 14px 0;'>
            <div class='info-chip-ok'>
                <span>✓</span>
                <span>Mendukung PDF berbasis teks (bukan scan)</span>
            </div>
            <div class='info-chip-warn'>
                <span>⚠</span>
                <span>Jika CV tidak terbaca dengan baik, Anda dapat mengisi informasi secara manual</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader("CV PDF", type=["pdf"], label_visibility="collapsed")

        # Validasi bukan PDF
        if uploaded and not uploaded.name.lower().endswith(".pdf"):
            st.error("❌ **File bukan PDF.** Harap upload file CV dalam format **.pdf**.")
            uploaded = None

        # FIX 4: Simpan file ke session_state saat pertama upload
        if uploaded is not None:
            st.session_state.uploaded_file_bytes = uploaded.read()
            st.session_state.uploaded_file_name  = uploaded.name

        # Cek: apakah sudah ada file (dari upload sekarang atau sebelumnya)
        has_file = st.session_state.uploaded_file_bytes is not None

        if has_file:
            fname = st.session_state.uploaded_file_name

            # Hanya proses spinner saat baru upload (uploaded is not None)
            if uploaded is not None:
                with st.spinner("🔍 Menganalisis CV dengan NLP pipeline..."):
                    time.sleep(1.8)
                SIMULATE_FAIL = False
                st.session_state.parse_failed = SIMULATE_FAIL

            if st.session_state.parse_failed:
                st.warning(
                    "⚠️ **CV tidak dapat dibaca dengan baik.**  \n"
                    "Kemungkinan: PDF berbentuk scan/gambar, font tidak standar, atau terenkripsi.  \n"
                    "Silakan lengkapi informasi berikut secara **manual**."
                )
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### ✏️ Input Manual")
                c1, c2 = st.columns(2)
                with c1:
                    nama_m   = st.text_input("Nama Lengkap", placeholder="Contoh: Sintiya Risla")
                    edu_m    = st.text_input("Pendidikan",   placeholder="S1 Informatika – Universitas Negeri Surabaya")
                    exp_m    = st.text_input("Pengalaman",   placeholder="1 tahun sebagai Data Analyst Intern")
                with c2:
                    skills_m = st.text_area("Skills (pisahkan koma)", height=130,
                                            placeholder="Python, SQL, Machine Learning, NLP, Pandas")
                all_filled = nama_m and edu_m and exp_m and skills_m
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(
                    "Lanjut dengan Input Manual →" if all_filled else "⚠️ Lengkapi semua field dahulu",
                    type="primary" if all_filled else "secondary",
                    use_container_width=True, disabled=not all_filled,
                ):
                    st.session_state.step = 2
                    st.rerun()
            else:
                st.success(f"✅ **{fname}** berhasil diproses!")
                st.markdown("<br>", unsafe_allow_html=True)

                c_info, c_skill = st.columns(2, gap="medium")
                with c_info:
                    st.markdown("**📋 Detail Informasi**")
                    # FIX 3: render dari session_state — auto update
                    render_cv_detail()

                with c_skill:
                    st.markdown("**🏷️ Skills Terdeteksi**")
                    pills = "".join(f'<span class="pill-match">✓ {s}</span>' for s in st.session_state.skills_match)
                    st.markdown(
                        f"<div style='background:#161b22;border:1px solid #2d2d2d;"
                        f"border-radius:10px;padding:14px;'>{pills}</div>",
                        unsafe_allow_html=True
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                # FIX 3: koreksi langsung update session_state dan rerun → tampilan auto terupdate
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
                            **cv,
                            "nama": k_nama, "email": k_email, "phone": k_phone,
                            "ringkasan": k_ringkasan, "pendidikan": k_pendidikan,
                            "pengalaman": k_pengalaman,
                        }
                        st.session_state.skills_match = [
                            s.strip() for s in k_skills.split(",") if s.strip()
                        ]
                        st.rerun()  # FIX 3: st.rerun() → Detail Informasi otomatis terupdate

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
            background:#161b22;border:1px solid #2d2d2d;border-radius:10px;
            padding:12px 14px;margin-bottom:8px;'>
                <div style='font-size:22px;flex-shrink:0;'>{icon}</div>
                <div>
                    <div style='font-size:13px;font-weight:600;color:#ffffff;margin-bottom:2px;'>{title}</div>
                    <div style='font-size:12px;color:#8b949e;'>{desc}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:linear-gradient(135deg,#1a0a0e,#2e0a18);
        border:1px solid #e8274b;border-radius:10px;padding:14px;'>
            <div style='font-size:12px;color:#e8274b;font-weight:600;margin-bottom:6px;'>💡 Tips: Hasil Terbaik</div>
            <div style='font-size:12px;color:#c9d1d9;line-height:1.6;'>
                • Gunakan CV berbasis teks (bukan scan)<br>
                • Pastikan skills tercantum dengan jelas<br>
                • CV dalam Bahasa Indonesia atau Inggris<br>
                • Format ATS-friendly lebih mudah dibaca
            </div>
        </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# STEP 2 — Pilih Model
# ──────────────────────────────────────────────────────────────
elif st.session_state.step == 2:
    st.markdown('<div class="section-badge">STEP 2</div>', unsafe_allow_html=True)
    st.subheader("Pilih Model Similarity")
    st.caption("Sistem menggunakan pendekatan komparatif. Pilih salah satu model untuk melanjutkan.")
    st.markdown("<br>", unsafe_allow_html=True)

    MODELS = [
        {
            "name":"TF-IDF","icon":"📝",
            "desc":"Keyword-based matching. Cepat, ringan, dan mudah diinterpretasi. Ideal sebagai baseline komparasi.",
            "badge":"BASELINE","badge_color":"#8b949e","badge_bg":"#21262d",
            "pros":["Sangat cepat","Mudah diinterpretasi","Efisien secara komputasi"],
            "cons":["Tidak memahami sinonim","Kurang kontekstual"],
        },
        {
            "name":"TF-IDF + SVD","icon":"🔢",
            "desc":"TF-IDF dengan reduksi dimensi SVD. Menangkap hubungan laten antar kata untuk representasi lebih kaya.",
            "badge":"IMPROVED","badge_color":"#58a6ff","badge_bg":"#0d1f3c",
            "pros":["Menangkap relasi laten","Lebih baik dari TF-IDF murni"],
            "cons":["Lebih kompleks","Perlu tuning dimensi SVD"],
        },
        {
            "name":"Embedding","icon":"🧠",
            "desc":"Sentence-BERT semantic similarity. Paling akurat dan kontekstual — memahami makna sebenarnya.",
            "badge":"⭐ TERBAIK","badge_color":"#3fb950","badge_bg":"#0a2e1a",
            "pros":["Memahami semantik & sinonim","Akurasi tertinggi"],
            "cons":["Lebih berat secara komputasi"],
        },
    ]

    model_cols = st.columns(3, gap="medium")
    for col, m in zip(model_cols, MODELS):
        selected = st.session_state.model_choice == m["name"]
        border   = "2px solid #e8274b" if selected else "1px solid #2d2d2d"
        bg       = "#1a0a0e"           if selected else "#161b22"
        glow     = "box-shadow:0 0 16px rgba(232,39,75,0.25);" if selected else ""
        pros_html = "".join(f"<div style='font-size:11px;color:#3fb950;margin-bottom:3px;'>✓ {p}</div>" for p in m["pros"])
        cons_html = "".join(f"<div style='font-size:11px;color:#8b949e;margin-bottom:3px;'>• {c}</div>" for c in m["cons"])

        # FIX 5: tinggi card disamakan dengan min-height yang lebih besar dan flex
        col.markdown(f"""
        <div style='border:{border};background:{bg};border-radius:14px;
        padding:24px 16px;text-align:center;{glow}margin-bottom:10px;
        min-height:320px;display:flex;flex-direction:column;justify-content:flex-start;'>
            <div style='font-size:36px;margin-bottom:8px;'>{m["icon"]}</div>
            <div style='font-size:16px;font-weight:700;color:#ffffff;margin-bottom:6px;'>{m["name"]}</div>
            <span style='background:{m["badge_bg"]};color:{m["badge_color"]};
            border-radius:20px;padding:3px 12px;font-size:11px;font-weight:600;
            letter-spacing:0.06em;'>{m["badge"]}</span>
            <div style='font-size:12px;color:#8b949e;margin:12px 0 10px;line-height:1.55;'>{m["desc"]}</div>
            <div style='text-align:left;'>{pros_html}{cons_html}</div>
        </div>""", unsafe_allow_html=True)

        btn_label = "✓ Dipilih" if selected else f"Pilih {m['name']}"
        btn_type  = "primary"   if selected else "secondary"
        if col.button(btn_label, key=m["name"], use_container_width=True, type=btn_type):
            st.session_state.model_choice = m["name"]
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col_guide, col_table = st.columns([1, 1], gap="large")
    with col_guide:
        st.markdown("""
        <div style='background:#161b22;border:1px solid #2d2d2d;border-radius:12px;padding:16px;'>
            <div style='font-size:12px;color:#e8274b;font-weight:600;margin-bottom:10px;'>
                📌 Panduan Skor Cosine Similarity
            </div>
            <div style='margin-bottom:7px;display:flex;align-items:center;gap:10px;'>
                <span style='background:#0a2e1a;color:#3fb950;border-radius:20px;padding:3px 12px;font-size:12px;font-weight:500;'>≥ 0.75</span>
                <span style='font-size:12px;color:#c9d1d9;'>Sangat Cocok</span>
            </div>
            <div style='margin-bottom:7px;display:flex;align-items:center;gap:10px;'>
                <span style='background:#0d1f3c;color:#58a6ff;border-radius:20px;padding:3px 12px;font-size:12px;font-weight:500;'>0.60–0.74</span>
                <span style='font-size:12px;color:#c9d1d9;'>Cocok</span>
            </div>
            <div style='margin-bottom:7px;display:flex;align-items:center;gap:10px;'>
                <span style='background:#2e1f0a;color:#d29922;border-radius:20px;padding:3px 12px;font-size:12px;font-weight:500;'>0.45–0.59</span>
                <span style='font-size:12px;color:#c9d1d9;'>Cukup Cocok</span>
            </div>
            <div style='margin-bottom:10px;display:flex;align-items:center;gap:10px;'>
                <span style='background:#1a1a1a;color:#8b949e;border-radius:20px;padding:3px 12px;font-size:12px;font-weight:500;'>< 0.45</span>
                <span style='font-size:12px;color:#c9d1d9;'>Kurang Cocok</span>
            </div>
            <div style='font-size:11px;color:#8b949e;border-top:1px solid #2d2d2d;padding-top:8px;'>
                💡 Skor 0.60 ke atas sudah termasuk <span style="color:#58a6ff;font-weight:500;">bagus</span> untuk cosine similarity.
            </div>
        </div>""", unsafe_allow_html=True)

    with col_table:
        with st.expander("📊 Perbandingan Detail Model", expanded=True):
            df_cmp = pd.DataFrame({
                "Model":       ["TF-IDF",   "TF-IDF+SVD","Embedding"],
                "Kecepatan":   ["⚡⚡⚡",  "⚡⚡",        "⚡"],
                "Akurasi":     ["★★☆☆",    "★★★☆",       "★★★★"],
                "Semantik":    ["✗",        "Parsial",     "✓"],
                "Rekomendasi": ["Baseline", "Menengah",    "Terbaik"],
            })
            st.dataframe(df_cmp.set_index("Model"), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.model_choice:
        st.success(f"✅ Model dipilih: **{st.session_state.model_choice}** · Top-5 rekomendasi akan ditampilkan")
    else:
        st.warning("⚠️ Pilih salah satu model di atas untuk melanjutkan.")

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_next = st.columns(2)
    if col_back.button("← Kembali", use_container_width=True):
        st.session_state.step = 1
        st.rerun()
    model_ok = st.session_state.model_choice is not None
    if col_next.button(
        "Lihat Rekomendasi →" if model_ok else "⚠️ Pilih model terlebih dahulu",
        type="primary" if model_ok else "secondary",
        use_container_width=True, disabled=not model_ok,
    ):
        st.session_state.step = 3
        st.rerun()


# ──────────────────────────────────────────────────────────────
# STEP 3 — Rekomendasi
# ──────────────────────────────────────────────────────────────
elif st.session_state.step == 3:
    k = st.session_state.top_k
    st.markdown('<div class="section-badge">STEP 3</div>', unsafe_allow_html=True)
    st.subheader(f"Top-{k} Rekomendasi Pekerjaan")
    st.caption(f"Model: **{st.session_state.model_choice}** · Diurutkan berdasarkan cosine similarity")
    st.markdown("<br>", unsafe_allow_html=True)

    # FIX 6: hapus "+0.12 vs rata-rata", ganti dengan template deskriptif
    kc1, kc2, kc3, kc4 = st.columns(4)
    kc1.markdown(card_metric("🏆 Top Match",  "0.82",  "Skor tertinggi CV ini",      "#e8274b"), unsafe_allow_html=True)
    kc2.markdown(card_metric("📂 Dianalisis", "1.400", "lowongan dari Jobstreet",    "#58a6ff"), unsafe_allow_html=True)
    kc3.markdown(card_metric("🔑 Skills",     "7",     "skill terdeteksi dari CV",   "#3fb950"), unsafe_allow_html=True)
    kc4.markdown(card_metric("⚠️ Skill Gap",  "3",     "skill perlu ditingkatkan",   "#d29922"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # FIX 7: tab dengan spacing — sudah dihandle di CSS (gap: 6px pada tab-list)
    tab_list, tab_chart = st.tabs(["  📋  Daftar Lowongan  ", "  📊  Visualisasi Skor  "])

    with tab_list:
        st.markdown("""
        <div style='display:flex;gap:16px;flex-wrap:wrap;margin-bottom:14px;'>
            <span style='font-size:12px;color:#3fb950;'>● ≥ 0.75 — Sangat Cocok</span>
            <span style='font-size:12px;color:#58a6ff;'>● 0.60–0.74 — Cocok</span>
            <span style='font-size:12px;color:#d29922;'>● 0.45–0.59 — Cukup</span>
            <span style='font-size:12px;color:#8b949e;'>● &lt; 0.45 — Kurang</span>
        </div>""", unsafe_allow_html=True)

        col_left, col_right = st.columns(2, gap="medium")
        jobs_k = DUMMY_JOBS[:k]
        for idx, job in enumerate(jobs_k):
            sc, color, label, bg_col = job["score"], score_color(job["score"]), score_label(job["score"]), score_bg(job["score"])
            target = col_left if idx % 2 == 0 else col_right
            with target:
                st.markdown(f"""
                <div class="job-card">
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                        <div style='flex:1;min-width:0;'>
                            <div style='display:flex;align-items:center;gap:8px;margin-bottom:5px;'>
                                <span style='background:#e8274b;color:#fff;border-radius:6px;
                                padding:2px 8px;font-size:11px;font-weight:600;flex-shrink:0;'>#{job['rank']}</span>
                                <strong style='font-size:15px;color:#ffffff;'>{job['title']}</strong>
                            </div>
                            <div style='font-size:12px;color:#8b949e;'>
                                🏢 {job['company']} &nbsp;·&nbsp; 📍 {job['location']} &nbsp;·&nbsp; 🕒 {job['type']}
                            </div>
                        </div>
                        <div style='text-align:right;flex-shrink:0;margin-left:12px;'>
                            <div style='font-size:22px;font-weight:700;color:{color};'>{sc:.2f}</div>
                            <div style='font-size:10px;font-weight:600;color:{color};
                            background:{bg_col};border-radius:10px;padding:1px 8px;'>{label}</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
                st.progress(sc)
                with st.expander(f"🔍 Lihat Detail — {job['title']}"):
                    d1, d2, d3 = st.columns(3)
                    d1.markdown(f"""
                    <div style='background:#161b22;border:1px solid #2d2d2d;border-top:3px solid {color};
                    border-radius:10px;padding:12px;text-align:center;'>
                        <div style='font-size:10px;color:#8b949e;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;'>Skor Kecocokan</div>
                        <div style='font-size:26px;font-weight:700;color:{color};'>{sc:.2f}</div>
                        <div style='font-size:11px;font-weight:600;color:{color};background:{bg_col};
                        border-radius:10px;padding:2px 8px;display:inline-block;margin-top:2px;'>{label}</div>
                    </div>""", unsafe_allow_html=True)
                    d2.markdown(f"""
                    <div style='background:#161b22;border:1px solid #2d2d2d;border-top:3px solid #58a6ff;
                    border-radius:10px;padding:12px;text-align:center;'>
                        <div style='font-size:10px;color:#8b949e;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;'>Perusahaan</div>
                        <div style='font-size:15px;font-weight:600;color:#e0eaf4;'>{job['company']}</div>
                        <div style='font-size:11px;color:#8b949e;margin-top:4px;'>📍 {job['location']}</div>
                    </div>""", unsafe_allow_html=True)
                    d3.markdown(f"""
                    <div style='background:#161b22;border:1px solid #2d2d2d;border-top:3px solid #d29922;
                    border-radius:10px;padding:12px;text-align:center;'>
                        <div style='font-size:10px;color:#8b949e;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;'>Tipe Pekerjaan</div>
                        <div style='font-size:15px;font-weight:600;color:#e0eaf4;'>{job['type']}</div>
                        <div style='font-size:11px;color:#8b949e;margin-top:4px;'>Ranking #{job['rank']} dari {k}</div>
                    </div>""", unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    skill_cols = st.columns(2)
                    # Skills match untuk posisi ini (simulasi)
                    matched   = st.session_state.skills_match[:5]
                    not_match = SKILLS_GAP
                    with skill_cols[0]:
                        st.markdown("<div style='font-size:12px;color:#3fb950;font-weight:600;margin-bottom:6px;'>✓ Skills yang Cocok</div>", unsafe_allow_html=True)
                        pills_match = "".join(f'<span class="pill-match">✓ {s}</span>' for s in matched)
                        st.markdown(pills_match, unsafe_allow_html=True)
                    with skill_cols[1]:
                        st.markdown("<div style='font-size:12px;color:#ff7b7b;font-weight:600;margin-bottom:6px;'>✗ Skills yang Belum Dimiliki</div>", unsafe_allow_html=True)
                        pills_gap = "".join(f'<span class="pill-gap">✗ {s}</span>' for s in not_match)
                        st.markdown(pills_gap, unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style='background:linear-gradient(135deg,#1a0a0e,#2e0a18);
                    border:1px solid #e8274b;border-radius:10px;padding:12px;'>
                        <div style='font-size:11px;color:#e8274b;font-weight:600;margin-bottom:4px;'>💡 Saran untuk Posisi Ini</div>
                        <div style='font-size:12px;color:#c9d1d9;line-height:1.6;'>
                            Tingkatkan skor kecocokan dengan mempelajari skill yang belum dimiliki.
                            Lihat tab <strong style='color:#e8274b;'>Skill Gap & Saran</strong> untuk panduan belajar lengkap.
                        </div>
                    </div>""", unsafe_allow_html=True)

    with tab_chart:
        # FIX 8: chart diperluas full width (1 kolom saja, tidak dibagi 2)
        fig = go.Figure(go.Bar(
            x=[j["score"] for j in jobs_k],
            y=[j["title"]  for j in jobs_k],
            orientation="h",
            marker_color=[score_color(j["score"]) for j in jobs_k],
            text=[f"{j['score']:.2f}" for j in jobs_k],
            textposition="outside",
            textfont=dict(color="#c9d1d9"),
        ))
        fig.update_layout(
            **plotly_dark(),
            xaxis=dict(range=[0, 1.15], gridcolor="#21262d", color="#8b949e"),
            yaxis=dict(autorange="reversed", color="#c9d1d9"),
            title=dict(text="Skor Cosine Similarity per Lowongan", font=dict(color="#ffffff", size=14)),
            height=380,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_next = st.columns(2)
    if col_back.button("← Kembali", use_container_width=True):
        st.session_state.step = 2
        st.rerun()
    if col_next.button("Lihat Skill Insight →", type="primary", use_container_width=True):
        st.session_state.step = 4
        st.rerun()


# ──────────────────────────────────────────────────────────────
# STEP 4 — Skill Insight
# ──────────────────────────────────────────────────────────────
elif st.session_state.step == 4:
    st.markdown('<div class="section-badge">STEP 4</div>', unsafe_allow_html=True)
    st.subheader("Skill Insight")
    st.caption("Analisis berdasarkan posisi dengan skor tertinggi: **Data Scientist @ Tokopedia (0.82 — Sangat Cocok)**")
    st.markdown("<br>", unsafe_allow_html=True)

    skills_now = st.session_state.skills_match
    si1, si2, si3 = st.columns(3)
    si1.markdown(card_metric("✅ Skills Dimiliki",   f"{len(skills_now)} skill", "Terdeteksi dari CV",         "#3fb950"), unsafe_allow_html=True)
    si2.markdown(card_metric("⚠️ Skill Gap",         f"{len(SKILLS_GAP)} skill", "Perlu dipelajari",           "#d29922"), unsafe_allow_html=True)
    si3.markdown(card_metric("🏆 Tingkat Kecocokan", "0.82",                      "Terbaik dari 1.400 lowongan","#e8274b"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # FIX 9: tab dengan spacing — sudah dihandle di CSS
    tab_match, tab_gap, tab_radar = st.tabs([
        "  ✅  Skill Match  ",
        "  📚  Skill Gap & Saran  ",
        "  📊  Radar Chart  "
    ])

    with tab_match:
        st.markdown("#### Skills yang sudah Anda miliki")
        st.caption("Skills ini cocok dengan kebutuhan posisi Data Scientist @ Tokopedia")
        match_cols = st.columns(3)
        for i, skill in enumerate(skills_now):
            match_cols[i % 3].markdown(f"""
            <div style='background:#0a2e1a;border:1px solid #2ea043;border-radius:10px;
            padding:10px 14px;margin-bottom:8px;display:flex;align-items:center;gap:8px;'>
                <span style='color:#3fb950;font-size:16px;'>✓</span>
                <span style='color:#e0eaf4;font-size:13px;font-weight:500;'>{skill}</span>
            </div>""", unsafe_allow_html=True)

    with tab_gap:
        st.markdown("#### Skills yang perlu ditingkatkan")
        st.caption("Pelajari skill berikut untuk meningkatkan kecocokan Anda")
        for skill in SKILLS_GAP:
            src, dur = SKILL_LEARN[skill]
            with st.expander(f"📚  {skill}  —  Estimasi: {dur}"):
                gc1, gc2 = st.columns([1, 2])
                with gc1:
                    st.markdown(f"""
                    <div style='background:#2e0a0a;border:1px solid #e8274b;border-radius:10px;
                    padding:14px;text-align:center;'>
                        <div style='font-size:28px;margin-bottom:6px;'>⚠️</div>
                        <div style='font-size:13px;font-weight:600;color:#ff7b7b;'>{skill}</div>
                        <div style='font-size:11px;color:#8b949e;margin-top:4px;'>Belum terdeteksi</div>
                    </div>""", unsafe_allow_html=True)
                with gc2:
                    st.markdown(f"""
                    <div style='background:#161b22;border:1px solid #2d2d2d;border-radius:10px;padding:14px;'>
                        <div style='font-size:11px;color:#e8274b;font-weight:600;margin-bottom:6px;'>💡 SUMBER BELAJAR</div>
                        <div style='font-size:14px;color:#58a6ff;margin-bottom:10px;'>{src}</div>
                        <div style='font-size:11px;color:#8b949e;margin-bottom:4px;'>⏱ ESTIMASI WAKTU</div>
                        <div style='font-size:16px;font-weight:600;color:#d29922;'>{dur}</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:linear-gradient(135deg,#1a0a0e,#2e0a18);
        border:1px solid #e8274b;border-radius:12px;padding:16px;'>
            <div style='font-size:13px;color:#e8274b;font-weight:600;margin-bottom:8px;'>
                🎯 Prioritas Pengembangan Karir
            </div>
            <div style='font-size:13px;color:#c9d1d9;line-height:1.7;'>
                1. <strong style="color:#3fb950;">Apache Spark</strong> — Paling banyak dicari untuk posisi Data Scientist di Indonesia<br>
                2. <strong style="color:#58a6ff;">Kubernetes</strong> — Krusial untuk MLOps dan deployment model di production<br>
                3. <strong style="color:#d29922;">Scala</strong> — Digunakan bersama Spark untuk big data engineering
            </div>
        </div>""", unsafe_allow_html=True)

    with tab_radar:
        st.markdown("#### Radar Chart — Profil Anda vs Kebutuhan Lowongan")
        cats = ["Python & DS","ML & AI","Data Eng.","NLP","MLOps"]
        r_left, r_right = st.columns([3, 1])
        with r_left:
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[95,88,60,90,40,95], theta=cats+[cats[0]], fill="toself", name="Profil Anda",
                line_color="#e8274b", fillcolor="rgba(232,39,75,0.15)"))
            fig.add_trace(go.Scatterpolar(
                r=[90,85,80,85,75,90], theta=cats+[cats[0]], fill="toself", name="Persyaratan Lowongan",
                line_color="#58a6ff", fillcolor="rgba(88,166,255,0.08)"))
            fig.update_layout(
                polar=dict(bgcolor="#161b22",
                           radialaxis=dict(visible=True,range=[0,100],color="#8b949e",gridcolor="#2d2d2d"),
                           angularaxis=dict(color="#c9d1d9")),
                paper_bgcolor="#0d1117", plot_bgcolor="#0d1117", font=dict(color="#c9d1d9"),
                legend=dict(bgcolor="#161b22",bordercolor="#2d2d2d",borderwidth=1,
                            orientation="h",yanchor="bottom",y=-0.15),
                margin=dict(t=20,b=40), height=380,
            )
            st.plotly_chart(fig, use_container_width=True)
        with r_right:
            st.markdown("<br><br>", unsafe_allow_html=True)
            radar_data = [
                ("Python & DS",95,90,"#3fb950"),("ML & AI",88,85,"#3fb950"),
                ("Data Eng.",60,80,"#d29922"),  ("NLP",90,85,"#3fb950"),
                ("MLOps",40,75,"#e8274b"),
            ]
            for cat, anda, req, color in radar_data:
                gap = req - anda
                icon = "✓" if gap <= 0 else "⚠"
                gap_text = f"+{-gap}" if gap <= 0 else f"-{gap}"
                st.markdown(f"""
                <div style='background:#161b22;border:1px solid #2d2d2d;border-radius:8px;
                padding:8px 10px;margin-bottom:6px;'>
                    <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <span style='font-size:11px;color:#c9d1d9;'>{cat}</span>
                        <span style='font-size:11px;color:{color};font-weight:600;'>{icon} {gap_text}</span>
                    </div>
                    <div style='background:#2d2d2d;border-radius:4px;height:4px;margin-top:4px;'>
                        <div style='background:{color};height:4px;border-radius:4px;width:{anda}%;'></div>
                    </div>
                </div>""", unsafe_allow_html=True)
        st.caption("Merah = profil Anda · Biru = persyaratan lowongan.")

    st.markdown("<br>", unsafe_allow_html=True)
    bc, rc = st.columns(2)
    if bc.button("← Kembali", use_container_width=True):
        st.session_state.step = 3
        st.rerun()
    if rc.button("🔄 Analisis CV Baru", type="primary", use_container_width=True):
        for key in ["step","model_choice","top_k","uploaded_file_bytes","uploaded_file_name",
                    "parse_failed","manual_skills","manual_edu","manual_exp","cv_info","skills_match"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


import streamlit as st
import pandas as pd
import time

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="JobMatch AI – CV Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f0faf5;
        border-right: 1px solid #c6e8d8;
    }
    /* Force sidebar text to be dark green for contrast */
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] strong,
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        color: #0F6E56 !important;
    }
    /* Metric cards */
    [data-testid="metric-container"] {
        background: #f0faf5;
        border: 1px solid #c6e8d8;
        border-radius: 10px;
        padding: 14px;
    }
    /* Progress bars – teal */
    .stProgress > div > div > div > div {
        background-color: #1D9E75;
    }
    /* Skill pills */
    .pill-match {
        display: inline-block;
        background: #E1F5EE;
        color: #0F6E56;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 3px;
        font-size: 13px;
        font-weight: 500;
    }
    .pill-gap {
        display: inline-block;
        background: #FCEBEB;
        color: #A32D2D;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 3px;
        font-size: 13px;
        font-weight: 500;
    }
    /* Job card */
    .job-card {
        background: white;
        border: 1px solid #e0ece8;
        border-left: 4px solid #1D9E75;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Data dummy (nanti diganti dengan pipeline sesungguhnya) ───
DUMMY_JOBS = [
    {"rank": 1, "title": "Data Scientist",       "company": "Tokopedia",  "location": "Jakarta",  "type": "Full-time", "score": 92},
    {"rank": 2, "title": "ML Engineer",           "company": "Gojek",     "location": "Jakarta",  "type": "Full-time", "score": 85},
    {"rank": 3, "title": "NLP Research Engineer", "company": "Traveloka", "location": "Jakarta",  "type": "Full-time", "score": 78},
    {"rank": 4, "title": "AI Engineer",           "company": "Shopee",    "location": "Remote",   "type": "Remote",    "score": 71},
    {"rank": 5, "title": "Data Analyst",          "company": "Bank BCA",  "location": "Surabaya", "type": "Full-time", "score": 65},
]
DUMMY_CV = {
    "nama": "Sintiya Risla",
    "pendidikan": "S1 Sains Data – Universitas Negeri Surabaya",
    "pengalaman": "1 tahun (Intern Data Analyst)",
    "skills_match": ["Python", "Machine Learning", "SQL", "NLP", "Pandas", "Scikit-learn"],
    "skills_gap":   ["Apache Spark", "Kubernetes", "Scala", "Go"],
}

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 JobMatch AI")
    st.caption("CV Analyzer & Job Recommendation")
    st.divider()

    page = st.radio(
        "Navigasi",
        ["📤 Upload CV", "👤 Profil Saya", "📋 Rekomendasi", "📊 Analisis Gap"],
        label_visibility="collapsed",
    )
    st.divider()

    st.markdown("**Model Aktif**")
    model = st.selectbox(
        "Pilih Model Similarity",
        ["Embedding (Sentence-BERT)", "TF-IDF + SVD", "TF-IDF (Baseline)"],
        label_visibility="collapsed",
    )
    top_k = st.slider("Jumlah Rekomendasi (Top-K)", 3, 10, 5)

    st.divider()
    st.caption("Capstone Project · Data Science · 2025")

# ══════════════════════════════════════════════════════════════
# PAGE: Upload CV
# ══════════════════════════════════════════════════════════════
if "Upload" in page:
    st.title("📤 Upload CV Anda")
    st.caption("Format PDF · Maks. 5 MB")

    uploaded = st.file_uploader("Upload CV (PDF)", type=["pdf"], label_visibility="collapsed")

    if uploaded:
        with st.spinner("Mengekstrak informasi dari CV..."):
            time.sleep(1.5)  # simulasi proses

        st.success(f"✅ **{uploaded.name}** berhasil diproses!")

        st.divider()
        st.subheader("📄 Hasil Ekstraksi CV")

        col1, col2, col3 = st.columns(3)
        col1.metric("Nama", DUMMY_CV["nama"])
        col2.metric("Pendidikan", "S1 Sains Data")
        col3.metric("Pengalaman", "1 Tahun")

        st.markdown("**Skills Terdeteksi:**")
        pills_html = "".join(
            f'<span class="pill-match">✓ {s}</span>' for s in DUMMY_CV["skills_match"]
        )
        st.markdown(pills_html, unsafe_allow_html=True)

        st.divider()
        if st.button("🚀 Mulai Pencocokan Pekerjaan", type="primary", use_container_width=True):
            st.session_state["cv_processed"] = True
            st.info("CV siap dicocokkan! Pergi ke tab **📋 Rekomendasi** untuk melihat hasilnya.")
    else:
        st.info("👆 Seret & lepas file PDF CV Anda di atas untuk memulai analisis.")

# ══════════════════════════════════════════════════════════════
# PAGE: Profil Saya
# ══════════════════════════════════════════════════════════════
elif "Profil" in page:
    st.title("👤 Profil Kandidat")

    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("""
        <div style='text-align:center;background:#E1F5EE;border-radius:50%;
        width:80px;height:80px;line-height:80px;font-size:32px;margin:auto;'>👩</div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='text-align:center;margin-top:8px;font-weight:600;'>Sintiya Risla</div>",
                    unsafe_allow_html=True)
    with col_b:
        st.markdown(f"🎓 **Pendidikan:** {DUMMY_CV['pendidikan']}")
        st.markdown(f"💼 **Pengalaman:** {DUMMY_CV['pengalaman']}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ Skill Match")
        for s in DUMMY_CV["skills_match"]:
            st.markdown(f'<span class="pill-match">{s}</span>', unsafe_allow_html=True)
    with col2:
        st.markdown("#### ❌ Skill Gap")
        for s in DUMMY_CV["skills_gap"]:
            st.markdown(f'<span class="pill-gap">{s}</span>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE: Rekomendasi
# ══════════════════════════════════════════════════════════════
elif "Rekomendasi" in page:
    st.title("📋 Rekomendasi Pekerjaan")
    st.caption(f"Model: **{model}** · Menampilkan Top-{top_k} pekerjaan")

    jobs = DUMMY_JOBS[:top_k]

    for job in jobs:
        score = job["score"]
        bar_color = "#1D9E75" if score >= 80 else "#378ADD" if score >= 70 else "#BA7517"
        badge_bg = "#E1F5EE" if score >= 80 else "#E6F1FB" if score >= 70 else "#FAEEDA"
        badge_color = "#0F6E56" if score >= 80 else "#185FA5" if score >= 70 else "#854F0B"

        with st.container():
            st.markdown(f"""
            <div class="job-card" style="border-left-color:{bar_color}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <strong style="font-size:15px;">#{job['rank']} {job['title']}</strong><br>
                        <span style="color:#666;font-size:13px;">
                            🏢 {job['company']} &nbsp;·&nbsp; 📍 {job['location']} &nbsp;·&nbsp; 🕒 {job['type']}
                        </span>
                    </div>
                    <span style="background:{badge_bg};color:{badge_color};padding:4px 12px;
                    border-radius:20px;font-weight:600;font-size:14px;">{score}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(score / 100)

    st.divider()
    st.subheader("📊 Perbandingan Skor")
    df = pd.DataFrame(jobs).rename(columns={"title":"Posisi","company":"Perusahaan","score":"Skor (%)"})
    st.bar_chart(df.set_index("Posisi")["Skor (%)"])

# ══════════════════════════════════════════════════════════════
# PAGE: Analisis Gap
# ══════════════════════════════════════════════════════════════
elif "Analisis" in page:
    st.title("📊 Analisis Skill Gap")
    st.caption("Berdasarkan pekerjaan dengan kecocokan tertinggi: **Data Scientist – Tokopedia (92%)**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Skills Dimiliki",   f"{len(DUMMY_CV['skills_match'])} skills", "✅")
    col2.metric("Skills Kurang",     f"{len(DUMMY_CV['skills_gap'])} skills",   "⚠️")
    col3.metric("Tingkat Kecocokan", "92%", "+7% vs rata-rata")

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### ✅ Skills yang Sudah Dimiliki")
        for s in DUMMY_CV["skills_match"]:
            st.success(f"✓ {s}")
    with col_b:
        st.markdown("#### ❌ Skills yang Perlu Ditingkatkan")
        for s in DUMMY_CV["skills_gap"]:
            st.error(f"✗ {s}")

    st.divider()
    st.info("""
    💡 **Saran Pengembangan:**
    Untuk meningkatkan kecocokan dengan posisi **Data Scientist**, disarankan untuk mempelajari
    **Apache Spark** untuk pemrosesan data skala besar, dan **Kubernetes** untuk deployment model ML.
    Sumber belajar: Coursera, Udemy, atau dokumentasi resmi.
    """)

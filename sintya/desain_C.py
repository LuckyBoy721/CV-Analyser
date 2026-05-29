import streamlit as st
import pandas as pd
import plotly.express as px
import time

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Job Recommender",
    page_icon="✨",
    layout="centered",   # centered agar terasa "guided"
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f8f7ff; }

    /* Step pill */
    .step-pill {
        display: inline-block;
        background: #EEEDFE;
        color: #534AB7;
        border: 2px solid #7F77DD;
        border-radius: 50%;
        width: 32px; height: 32px;
        line-height: 28px;
        text-align: center;
        font-weight: 600;
        font-size: 14px;
        margin-right: 8px;
    }
    .step-pill.done {
        background: #7F77DD; color: white; border-color: #7F77DD;
    }
    .step-pill.inactive {
        background: #f0f0f0; color: #aaa; border-color: #ddd;
    }

    /* Skill pill */
    .pill-match {
        display: inline-block; background: #E1F5EE; color: #0F6E56;
        border-radius: 20px; padding: 5px 13px; margin: 3px; font-size: 13px; font-weight: 500;
    }
    .pill-gap {
        display: inline-block; background: #FCEBEB; color: #A32D2D;
        border-radius: 20px; padding: 5px 13px; margin: 3px; font-size: 13px; font-weight: 500;
    }

    /* Job card */
    .job-card {
        background: white;
        border: 1px solid #e8e5f8;
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(127,119,221,0.07);
    }
    .rank-badge {
        display: inline-block;
        border-radius: 10px;
        padding: 4px 10px;
        font-size: 13px;
        font-weight: 600;
    }

    /* Primary button purple */
    .stButton button[kind="primary"] {
        background: #7F77DD; color: white; border: none; border-radius: 10px;
    }

    /* Info/success box */
    .stAlert { border-radius: 12px !important; }

    /* Metric */
    [data-testid="metric-container"] {
        background: #EEEDFE; border-radius: 12px;
        border: 1px solid #CECBF6; padding: 14px;
    }
    [data-testid="stMetricValue"] { color: #534AB7 !important; }

    /* Progress bar – purple */
    .stProgress > div > div > div > div { background-color: #7F77DD; }

    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 1
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "Embedding (Sentence-BERT)"

# ── Dummy data ────────────────────────────────────────────────
DUMMY_JOBS = [
    {"rank": 1, "title": "Data Scientist",       "company": "Tokopedia",  "location": "Jakarta",   "type": "Full-time", "score": 92, "color": "#1D9E75", "bg": "#E1F5EE"},
    {"rank": 2, "title": "ML Engineer",           "company": "Gojek",     "location": "Jakarta",   "type": "Full-time", "score": 85, "color": "#185FA5", "bg": "#E6F1FB"},
    {"rank": 3, "title": "NLP Engineer",          "company": "Traveloka", "location": "Remote",    "type": "Remote",    "score": 78, "color": "#854F0B", "bg": "#FAEEDA"},
    {"rank": 4, "title": "Data Engineer",         "company": "Shopee",    "location": "Jakarta",   "type": "Full-time", "score": 70, "color": "#534AB7", "bg": "#EEEDFE"},
    {"rank": 5, "title": "Analytics Engineer",    "company": "OVO",       "location": "Bandung",   "type": "Hybrid",    "score": 63, "color": "#993C1D", "bg": "#FAECE7"},
]
SKILLS_MATCH = ["Python", "Machine Learning", "SQL", "NLP", "Scikit-learn", "Pandas"]
SKILLS_GAP   = ["Apache Spark", "Kubernetes", "Scala"]
CV_INFO = {"nama": "Sintiya Risla", "pendidikan": "S1 Sains Data", "exp": "1 tahun"}

# ── Utility: Step indicator ───────────────────────────────────
def render_steps(current):
    steps = ["Upload CV", "Pilih Model", "Rekomendasi", "Insight"]
    cols = st.columns(len(steps))
    for i, (col, label) in enumerate(zip(cols, steps)):
        num = i + 1
        if num < current:
            cls = "done"; icon = "✓"
        elif num == current:
            cls = ""; icon = str(num)
        else:
            cls = "inactive"; icon = str(num)
        col.markdown(
            f'<div style="text-align:center;">'
            f'<div class="step-pill {cls}">{icon}</div>'
            f'<div style="font-size:11px;color:{"#534AB7" if num<=current else "#aaa"};'
            f'font-weight:{"600" if num==current else "400"};margin-top:4px;">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div style='text-align:center;padding:20px 0 10px;'>
    <span style='font-size:36px;'>✨</span>
    <h2 style='color:#3C3489;margin:4px 0;'>AI Job Recommender</h2>
    <p style='color:#7F77DD;font-size:14px;'>CV Analyzer & Job Matching System</p>
</div>
""", unsafe_allow_html=True)
st.divider()
render_steps(st.session_state.step)
st.divider()

# ══════════════════════════════════════════════════════════════
# STEP 1 – Upload CV
# ══════════════════════════════════════════════════════════════
if st.session_state.step == 1:
    st.subheader("📤 Langkah 1: Upload CV Anda")
    st.caption("Format PDF · Maks. 5 MB · Sistem akan mengekstrak informasi otomatis")

    uploaded = st.file_uploader("Pilih file PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded:
        with st.spinner("🔍 Mengekstrak informasi dari CV menggunakan NLP..."):
            time.sleep(2)

        st.success(f"✅ **{uploaded.name}** berhasil diproses!")
        st.markdown("#### 📄 Hasil Ekstraksi")

        col1, col2, col3 = st.columns(3)
        col1.metric("Nama", CV_INFO["nama"])
        col2.metric("Pendidikan", CV_INFO["pendidikan"])
        col3.metric("Pengalaman", CV_INFO["exp"])

        st.markdown("#### 🏷️ Skills Terdeteksi")
        pills = "".join(f'<span class="pill-match">✓ {s}</span>' for s in SKILLS_MATCH)
        st.markdown(pills, unsafe_allow_html=True)

        st.markdown(" ")
        if st.button("➡️ Lanjut: Pilih Model Similarity", type="primary", use_container_width=True):
            st.session_state.uploaded = True
            st.session_state.step = 2
            st.rerun()
    else:
        st.info("👆 Upload CV Anda dalam format PDF untuk mulai analisis.")

# ══════════════════════════════════════════════════════════════
# STEP 2 – Pilih Model
# ══════════════════════════════════════════════════════════════
elif st.session_state.step == 2:
    st.subheader("⚙️ Langkah 2: Pilih Model Similarity")
    st.caption("Sistem mendukung 3 pendekatan berbeda. Pilih salah satu untuk dibandingkan.")

    col1, col2, col3 = st.columns(3)

    def model_card(col, name, icon, desc, badge, selected):
        border = "3px solid #7F77DD" if selected else "1px solid #e8e5f8"
        bg = "#EEEDFE" if selected else "white"
        col.markdown(f"""
        <div style='border:{border};background:{bg};border-radius:14px;padding:16px;text-align:center;cursor:pointer;'>
            <div style='font-size:28px;'>{icon}</div>
            <div style='font-weight:600;color:#3C3489;margin:6px 0 4px;'>{name}</div>
            <div style='font-size:12px;color:#666;margin-bottom:8px;'>{desc}</div>
            <span style='background:#EEEDFE;color:#534AB7;border-radius:20px;
            padding:3px 10px;font-size:11px;font-weight:600;'>{badge}</span>
        </div>
        """, unsafe_allow_html=True)
        return col.button(f"Pilih {name}", key=name, use_container_width=True)

    with col1:
        if model_card(col1, "TF-IDF", "📝", "Keyword-based, cepat & ringan", "Baseline", st.session_state.model_choice == "TF-IDF"):
            st.session_state.model_choice = "TF-IDF"
            st.rerun()
    with col2:
        if model_card(col2, "TF-IDF + SVD", "🔢", "Tambah reduksi dimensi laten", "Improved", st.session_state.model_choice == "TF-IDF + SVD"):
            st.session_state.model_choice = "TF-IDF + SVD"
            st.rerun()
    with col3:
        if model_card(col3, "Embedding", "🧠", "Semantic similarity, paling akurat", "⭐ Terbaik", st.session_state.model_choice == "Embedding"):
            st.session_state.model_choice = "Embedding"
            st.rerun()

    st.info(f"✅ Model dipilih: **{st.session_state.model_choice}**")
    top_k = st.slider("Jumlah Rekomendasi (Top-K)", 3, 10, 5)
    st.session_state.top_k = top_k

    col_back, col_next = st.columns(2)
    if col_back.button("← Kembali", use_container_width=True):
        st.session_state.step = 1
        st.rerun()
    if col_next.button("➡️ Lihat Rekomendasi", type="primary", use_container_width=True):
        st.session_state.step = 3
        st.rerun()

# ══════════════════════════════════════════════════════════════
# STEP 3 – Rekomendasi
# ══════════════════════════════════════════════════════════════
elif st.session_state.step == 3:
    k = getattr(st.session_state, "top_k", 5)
    st.subheader(f"📋 Langkah 3: Top-{k} Rekomendasi Pekerjaan")
    st.caption(f"Model: **{st.session_state.model_choice}** · Diurutkan berdasarkan cosine similarity")

    jobs = DUMMY_JOBS[:k]
    for job in jobs:
        st.markdown(f"""
        <div class="job-card">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span class="rank-badge" style="background:{job['bg']};color:{job['color']};">
                        #{job['rank']}
                    </span>
                    <strong style="font-size:15px;color:#1a1a2e;">&nbsp;{job['title']}</strong><br>
                    <span style="color:#666;font-size:13px;margin-left:4px;">
                        🏢 {job['company']} &nbsp;·&nbsp; 📍 {job['location']} &nbsp;·&nbsp; 🕒 {job['type']}
                    </span>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:22px;font-weight:700;color:{job['color']};">{job['score']}%</div>
                    <div style="font-size:11px;color:#aaa;">kecocokan</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(job["score"] / 100)

    # Mini chart
    df = pd.DataFrame(jobs)
    fig = px.bar(
        df, x="title", y="score", text="score",
        color="score",
        color_continuous_scale=["#EEEDFE", "#7F77DD", "#3C3489"],
        labels={"title": "Posisi", "score": "Skor (%)"},
        title="Perbandingan Skor Kecocokan",
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        coloraxis_showscale=False,
        paper_bgcolor="#f8f7ff", plot_bgcolor="#f8f7ff",
        yaxis=dict(range=[0, 110]),
        margin=dict(t=40, b=20),
        title_font_color="#3C3489",
    )
    st.plotly_chart(fig, use_container_width=True)

    col_back, col_next = st.columns(2)
    if col_back.button("← Kembali", use_container_width=True):
        st.session_state.step = 2
        st.rerun()
    if col_next.button("➡️ Lihat Skill Insight", type="primary", use_container_width=True):
        st.session_state.step = 4
        st.rerun()

# ══════════════════════════════════════════════════════════════
# STEP 4 – Insight
# ══════════════════════════════════════════════════════════════
elif st.session_state.step == 4:
    st.subheader("💡 Langkah 4: Skill Insight")
    st.caption("Analisis kecocokan dan kesenjangan skill berdasarkan pekerjaan terbaik: **Data Scientist @ Tokopedia (92%)**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Skills Dimiliki",   f"{len(SKILLS_MATCH)} skill", "✅")
    col2.metric("Skills Kurang",     f"{len(SKILLS_GAP)} skill",   "⚠️")
    col3.metric("Tingkat Kecocokan", "92%",                        "🏆 Top Match")

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### ✅ Skills yang Sudah Dimiliki")
        st.caption("Skills Anda cocok dengan kebutuhan posisi ini")
        for s in SKILLS_MATCH:
            st.success(f"✓  {s}")

    with col_b:
        st.markdown("#### 📚 Skills yang Perlu Ditingkatkan")
        st.caption("Pelajari skill ini untuk meningkatkan kecocokan")
        for s in SKILLS_GAP:
            st.error(f"✗  {s}")

    st.divider()
    st.markdown("""
    #### 🎯 Rekomendasi Pengembangan Diri
    """)
    st.info("""
    Berdasarkan analisis AI, untuk meraih posisi **Data Scientist** di perusahaan teknologi:

    1. 🔥 **Apache Spark** — Pemrosesan data skala besar. Belajar via: Databricks Academy, Coursera
    2. 🐳 **Kubernetes** — Deployment dan MLOps. Belajar via: KodeKloud, Linux Foundation
    3. 🦠 **Scala** — Bahasa untuk big data engineering. Belajar via: Rock the JVM, Udemy

    Estimasi waktu: **3–6 bulan** jika belajar konsisten 1–2 jam per hari.
    """)

    st.divider()
    if st.button("🔄 Mulai Ulang Analisis", type="primary", use_container_width=True):
        st.session_state.step = 1
        st.session_state.uploaded = False
        st.rerun()

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

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

# ── Dummy data ────────────────────────────────────────────────
DUMMY_JOBS = [
    {"rank": 1, "title": "Data Scientist",       "company": "Tokopedia",  "location": "Jakarta",   "type": "Full-time", "score": 92},
    {"rank": 2, "title": "ML Engineer",           "company": "Gojek",     "location": "Jakarta",   "type": "Full-time", "score": 85},
    {"rank": 3, "title": "AI Researcher",         "company": "Traveloka", "location": "Remote",    "type": "Remote",    "score": 75},
    {"rank": 4, "title": "Data Engineer",         "company": "Shopee",    "location": "Jakarta",   "type": "Full-time", "score": 68},
    {"rank": 5, "title": "Analytics Engineer",    "company": "OVO",       "location": "Bandung",   "type": "Hybrid",    "score": 61},
]
SKILLS_MATCH = ["Python", "NLP", "SQL", "Scikit-learn", "TF-IDF", "Pandas"]
SKILLS_GAP   = ["Apache Spark", "Kubernetes", "Scala"]

# ── Header ────────────────────────────────────────────────────
col_logo, col_title, col_model = st.columns([1, 4, 2])
with col_logo:
    st.markdown("## 🧠")
with col_title:
    st.markdown("## CVMatch AI")
    st.caption("AI-Based CV Analyzer & Job Recommendation System")
with col_model:
    model = st.selectbox(
        "Model",
        ["Embedding (Sentence-BERT)", "TF-IDF + SVD", "TF-IDF (Baseline)"],
        label_visibility="visible",
    )

st.divider()

# ── KPI Row ───────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("🏆 Kecocokan Terbaik", "92%",  "+12% vs rata-rata")
k2.metric("📂 Lowongan Dianalisis", "248", "dari Jobstreet")
k3.metric("🔑 Skills Terdeteksi",  "12",  "dari CV")
k4.metric("⚠️ Skill Gap",          "3",   "perlu ditingkatkan")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📤 Upload & Parsing", "📋 Rekomendasi", "🔍 Detail Analisis", "📊 Visualisasi"
])

# ────────────────────────────
with tab1:
    st.subheader("Upload CV & Hasil Ekstraksi")
    c_up, c_res = st.columns([1, 1])

    with c_up:
        uploaded = st.file_uploader("Upload CV (PDF)", type=["pdf"])
        if uploaded:
            with st.spinner("Memproses CV dengan NLP pipeline..."):
                time.sleep(1.5)
            st.success(f"✅ **{uploaded.name}** berhasil diproses!")

            st.markdown("#### 📄 Info CV")
            st.markdown("""
            | Field | Nilai |
            |---|---|
            | Nama | Sintiya Risla |
            | Pendidikan | S1 Sains Data – Universitas Negeri Surabaya |
            | Pengalaman | 1 tahun (Intern Data Analyst) |
            | Bahasa CV | Bahasa Indonesia → Ditranslasi |
            """)
        else:
            st.info("Upload file PDF CV Anda untuk memulai analisis.")

    with c_res:
        st.markdown("#### ✅ Skills Terdeteksi (Match)")
        pills_match = "".join(f'<span class="pill-match-dark">✓ {s}</span>' for s in SKILLS_MATCH)
        st.markdown(pills_match, unsafe_allow_html=True)

        st.markdown("#### ❌ Skills Kurang (Gap)")
        pills_gap = "".join(f'<span class="pill-gap-dark">✗ {s}</span>' for s in SKILLS_GAP)
        st.markdown(pills_gap, unsafe_allow_html=True)

# ────────────────────────────
with tab2:
    st.subheader(f"Top-{len(DUMMY_JOBS)} Rekomendasi Pekerjaan")
    st.caption(f"Model: **{model}** · Diurutkan berdasarkan skor kecocokan")

    for job in DUMMY_JOBS:
        s = job["score"]
        color = "#5DCAA5" if s >= 80 else "#7ec8e3" if s >= 70 else "#FAC775"

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

# ────────────────────────────
with tab3:
    st.subheader("Detail Analisis – Data Scientist @ Tokopedia")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**✅ Skills yang Sudah Dimiliki:**")
        for s in SKILLS_MATCH:
            st.success(f"✓  {s}")
    with c2:
        st.markdown("**❌ Skills yang Perlu Dipelajari:**")
        for s in SKILLS_GAP:
            st.error(f"✗  {s}")

    st.divider()
    st.info("""
    💡 **Rekomendasi Pengembangan Diri:**
    Untuk meningkatkan kecocokan, pelajari **Apache Spark** (big data processing),
    **Kubernetes** (MLOps/deployment), dan **Scala** (data engineering).
    Estimasi waktu belajar: 3–6 bulan.
    """)

# ────────────────────────────
with tab4:
    st.subheader("Visualisasi Perbandingan Model & Skor")

    # Radar chart – perbandingan skill
    categories = SKILLS_MATCH[:5]
    scores_emb  = [95, 88, 90, 85, 92]
    scores_tfidf = [78, 72, 80, 68, 75]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores_emb + [scores_emb[0]],
        theta=categories + [categories[0]],
        fill="toself", name="Embedding",
        line_color="#5DCAA5", fillcolor="rgba(93,202,165,0.15)"
    ))
    fig.add_trace(go.Scatterpolar(
        r=scores_tfidf + [scores_tfidf[0]],
        theta=categories + [categories[0]],
        fill="toself", name="TF-IDF",
        line_color="#7ec8e3", fillcolor="rgba(126,200,227,0.1)"
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#161b22",
            radialaxis=dict(visible=True, range=[0, 100], color="#8b949e"),
            angularaxis=dict(color="#e0eaf4"),
        ),
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        font_color="#e0eaf4",
        legend=dict(bgcolor="#161b22"),
        margin=dict(t=30, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    # Bar chart – skor tiap job
    df = pd.DataFrame(DUMMY_JOBS)
    fig2 = go.Figure(go.Bar(
        x=df["title"], y=df["score"],
        marker_color=["#5DCAA5", "#7ec8e3", "#7ec8e3", "#FAC775", "#FAC775"],
        text=df["score"].astype(str) + "%",
        textposition="outside",
    ))
    fig2.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
        font_color="#e0eaf4", yaxis=dict(range=[0, 110]),
        margin=dict(t=30, b=30),
        title="Skor Kecocokan per Lowongan",
        title_font_color="#e0eaf4",
    )
    st.plotly_chart(fig2, use_container_width=True)

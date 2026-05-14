import streamlit as st
from streamlit_autorefresh import st_autorefresh

from modules.m1_pow_monitor import render as render_m1
from modules.m2_block_header import render as render_m2
from modules.m3_difficulty_history import render as render_m3
from modules.m4_ai_component import render as render_m4

st.set_page_config(
    page_title="CryptoChain Insights Dashboard",
    page_icon="₿",
    layout="wide",
)

st_autorefresh(interval=60_000, key="autorefresh")

st.markdown("""
<style>
/* ── Base dark background ───────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0D1117 !important;
}
[data-testid="stSidebar"] { background-color: #0D1117 !important; }
section[data-testid="stMain"] > div { background-color: #0D1117 !important; }

/* ── Hide Streamlit chrome ───────────────────────────────────────────────── */
#MainMenu {visibility: hidden;}
footer    {visibility: hidden;}
header    {visibility: hidden;}

/* ── Global text ─────────────────────────────────────────────────────────── */
html, body, p, div, span, label {
    color: #CDD9E5 !important;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
h1 { font-size: 2rem !important; font-weight: 700 !important; color: #E6EDF3 !important; letter-spacing: -0.5px; }
h2 { font-size: 1.3rem !important; font-weight: 600 !important; color: #E6EDF3 !important; }
h3 { font-size: 1.05rem !important; font-weight: 500 !important; color: #CDD9E5 !important; }

/* ── Tab bar ─────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0px;
    border-bottom: 1px solid #21262D;
    background: transparent;
    padding: 0 4px;
}
.stTabs [data-baseweb="tab"] {
    height: 48px;
    padding: 0 24px;
    background: transparent;
    color: #8B949E;
    font-size: 0.875rem;
    font-weight: 500;
    border: none;
    border-bottom: 2px solid transparent;
    transition: color 0.2s, border-color 0.2s;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #58A6FF;
    background: rgba(88,166,255,0.06);
    border-radius: 6px 6px 0 0;
}
.stTabs [aria-selected="true"] {
    border-bottom: 2px solid #58A6FF !important;
    color: #58A6FF !important;
    font-weight: 600 !important;
    background: transparent !important;
}

/* ── Metric cards ────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #161B22 0%, #1C2128 100%);
    border: 1px solid #21262D;
    border-radius: 12px;
    padding: 16px 20px;
    transition: border-color 0.2s, transform 0.15s;
}
[data-testid="metric-container"]:hover {
    border-color: #388BFD;
    transform: translateY(-1px);
}
[data-testid="metric-container"] label {
    color: #8B949E !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #58A6FF !important;
    font-weight: 700 !important;
    font-size: 1.5rem !important;
}

/* ── Progress bar ────────────────────────────────────────────────────────── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #1F6FEB, #39D353) !important;
    border-radius: 4px;
}
[data-testid="stProgress"] {
    background-color: #21262D !important;
    border-radius: 4px;
}

/* ── Code / pre ──────────────────────────────────────────────────────────── */
code, pre {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    color: #39D353 !important;
    font-size: 0.82rem;
    border-radius: 6px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
}

/* ── Alerts ──────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px; }
[data-testid="stAlert"][kind="success"] {
    background-color: rgba(57,211,83,0.08) !important;
    border: 1px solid rgba(57,211,83,0.3) !important;
    color: #39D353 !important;
}
[data-testid="stAlert"][kind="error"] {
    background-color: rgba(248,81,73,0.08) !important;
    border: 1px solid rgba(248,81,73,0.3) !important;
}
[data-testid="stAlert"][kind="info"] {
    background-color: rgba(88,166,255,0.08) !important;
    border: 1px solid rgba(88,166,255,0.25) !important;
}
[data-testid="stAlert"][kind="warning"] {
    background-color: rgba(210,153,34,0.08) !important;
    border: 1px solid rgba(210,153,34,0.3) !important;
}

/* ── Expander ────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background-color: #161B22 !important;
    border: 1px solid #21262D !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"]:hover {
    border-color: #30363D !important;
}

/* ── Divider ─────────────────────────────────────────────────────────────── */
hr { border-color: #21262D !important; }

/* ── Slider ──────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background-color: #58A6FF !important;
    border-color: #58A6FF !important;
}

/* ── DataFrame ───────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #21262D !important;
    border-radius: 10px !important;
}

/* ── Spinner ─────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] { color: #58A6FF !important; }

/* ── Caption text ────────────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p { color: #8B949E !important; font-size: 0.78rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #161B22 0%, #1C2128 60%, #0D1117 100%);
    border: 1px solid #21262D;
    border-radius: 14px;
    padding: 28px 32px 22px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
">
    <div style="
        position: absolute; top: -40px; right: -40px;
        width: 180px; height: 180px;
        background: radial-gradient(circle, rgba(88,166,255,0.08) 0%, transparent 70%);
        border-radius: 50%;
    "></div>
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:8px;">
        <span style="font-size:2.2rem;">₿</span>
        <div>
            <h1 style="margin:0; font-size:1.8rem !important; background: linear-gradient(90deg, #58A6FF, #39D353); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                CryptoChain Insights Dashboard
            </h1>
            <p style="margin:4px 0 0; color:#8B949E !important; font-size:0.85rem;">
                Monitorización en tiempo real · Red Bitcoin · UAX Criptografía
            </p>
        </div>
    </div>
    <div style="display:flex; gap:20px; margin-top:14px; flex-wrap:wrap;">
        <span style="font-size:0.75rem; color:#8B949E; background:#21262D; padding:4px 12px; border-radius:20px; border:1px solid #30363D;">
            🟢 API Blockstream
        </span>
        <span style="font-size:0.75rem; color:#8B949E; background:#21262D; padding:4px 12px; border-radius:20px; border:1px solid #30363D;">
            ⏱ Auto-refresh 60s
        </span>
        <span style="font-size:0.75rem; color:#8B949E; background:#21262D; padding:4px 12px; border-radius:20px; border:1px solid #30363D;">
            🔐 SHA-256 · PoW · Merkle
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "⛏️  M1 · PoW Monitor",
    "🔍  M2 · Block Header",
    "📈  M3 · Difficulty History",
    "🤖  M4 · Anomaly Detector",
])

with tab1:
    render_m1()
with tab2:
    render_m2()
with tab3:
    render_m3()
with tab4:
    render_m4()
import streamlit as st

from modules.m1_pow_monitor import render as render_m1
from modules.m2_block_header import render as render_m2
from modules.m3_difficulty_history import render as render_m3
from modules.m4_ai_component import render as render_m4

st.set_page_config(
    page_title="CryptoChain Insights Dashboard",
    page_icon="₿",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* ── Hide Streamlit chrome ───────────────────────────────────────────── */
    #MainMenu {visibility: hidden;}
    footer    {visibility: hidden;}
    header    {visibility: hidden;}

    /* ── Global headings — light weight ─────────────────────────────────── */
    h1, h2, h3 {
        font-weight: 300 !important;
        color: #2C2C2C !important;
        letter-spacing: -0.3px;
    }
    h1 { font-size: 1.9rem !important; }
    h2 { font-size: 1.35rem !important; }
    h3 { font-size: 1.1rem !important; }

    /* ── Tab bar ─────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 2px solid #E8E0D5;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        padding: 0 20px;
        border-radius: 6px 6px 0 0;
        background: transparent;
        color: #6B6B6B;
        font-size: 0.88rem;
        font-weight: 400;
        border: none;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #4A3728;
        background: #F5F0E8;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #4A3728 !important;
        color: #4A3728 !important;
        font-weight: 600 !important;
        background: transparent !important;
    }

    /* ── Metric cards ────────────────────────────────────────────────────── */
    [data-testid="metric-container"] {
        background-color: #F5F0E8;
        border: 1px solid #E8E0D5;
        border-radius: 10px;
        padding: 14px 18px;
    }
    [data-testid="metric-container"] label {
        color: #6B6B6B !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #4A3728 !important;
        font-weight: 600 !important;
    }

    /* ── Dividers ────────────────────────────────────────────────────────── */
    hr { border-color: #E8E0D5; }

    /* ── Code blocks ─────────────────────────────────────────────────────── */
    code, pre {
        background-color: #F5F0E8 !important;
        border: 1px solid #E8E0D5 !important;
        color: #4A3728 !important;
        font-size: 0.82rem;
    }

    /* ── Info / success / warning boxes ─────────────────────────────────── */
    [data-testid="stAlert"] {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("₿ CryptoChain Insights Dashboard")
st.caption("Monitorización en tiempo real de la red Bitcoin · UAX · Criptografía")

tab1, tab2, tab3, tab4 = st.tabs([
    "M1 · PoW Monitor",
    "M2 · Block Header",
    "M3 · Difficulty History",
    "M4 · Anomaly Detector",
])

with tab1:
    render_m1()
with tab2:
    render_m2()
with tab3:
    render_m3()
with tab4:
    render_m4()

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import streamlit as st
from datetime import datetime, timezone

from api.blockchain_client import get_last_n_blocks, get_latest_block

_LAYOUT = dict(
    plot_bgcolor="#0D1117",
    paper_bgcolor="#0D1117",
    font=dict(color="#8B949E", size=11, family="Inter, sans-serif"),
    margin=dict(t=40, b=50, l=60, r=30),
    xaxis=dict(
        gridcolor="#161B22", linecolor="#21262D",
        title_font=dict(size=11, color="#8B949E"),
        tickfont=dict(color="#6E7681"),
        showgrid=True, zeroline=False,
    ),
    yaxis=dict(
        gridcolor="#161B22", linecolor="#21262D",
        title_font=dict(size=11, color="#8B949E"),
        tickfont=dict(color="#6E7681"),
        showgrid=True, zeroline=False,
    ),
    legend=dict(
        bgcolor="rgba(13,17,23,0.9)",
        bordercolor="#21262D",
        borderwidth=1,
        font=dict(color="#CDD9E5", size=11),
    ),
    hoverlabel=dict(
        bgcolor="#161B22",
        bordercolor="#30363D",
        font=dict(color="#CDD9E5", size=12),
    ),
)


def _target_from_bits(bits_int: int) -> int:
    exp  = (bits_int >> 24) & 0xFF
    coef = bits_int & 0x00FFFFFF
    return coef * (2 ** (8 * (exp - 3)))


def _leading_zero_bits(target: int) -> int:
    if target <= 0:
        return 256
    return 256 - target.bit_length()


@st.cache_data(ttl=60)
def _fetch_pow_data():
    latest = get_latest_block()
    blocks = get_last_n_blocks(50)
    return latest, blocks


def render() -> None:
    st.header("⛏️ Monitor de Proof of Work")
    st.caption("Datos en caché 60 s · actualización automática · fuente: Blockstream API")

    with st.spinner("Conectando con la red Bitcoin..."):
        latest, blocks = _fetch_pow_data()

    if not latest:
        st.error("No se pudo conectar con la API de Blockstream.")
        return

    difficulty   = latest.get("difficulty", 0)
    bits_int     = latest.get("bits", 0)
    height       = latest.get("height", 0)
    hashrate_ehs = (difficulty * 2**32) / 600 / 1e18
    target       = _target_from_bits(bits_int)
    leading_zeros = _leading_zero_bits(target)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Dificultad actual",    f"{difficulty:,.0f}")
    col2.metric("Hash rate estimado",   f"{hashrate_ehs:.2f} EH/s")
    col3.metric("Altura del bloque",    f"{height:,}")
    col4.metric("Bits a cero (target)", f"{leading_zeros} / 256")

    st.markdown("---")

    # ── Target visual ─────────────────────────────────────────────────────────
    st.subheader("🎯 Target de dificultad (espacio SHA-256 de 256 bits)")

    target_hex = format(target, "064x")
    st.markdown(
        "<div style='background:#0D1117; border:1px solid #21262D; border-radius:10px; "
        "padding:16px 20px; margin-bottom:12px;'>"
        "<p style='color:#8B949E; font-size:0.72rem; text-transform:uppercase; "
        "letter-spacing:0.8px; margin:0 0 8px;'>Target threshold (hex)</p>"
        "<code style='font-size:0.78rem; color:#39D353; word-break:break-all; "
        "background:transparent!important; border:none!important; letter-spacing:1px;'>"
        + target_hex + "</code></div>",
        unsafe_allow_html=True,
    )
    st.progress(leading_zeros / 256,
                text=f"El hash ganador debe empezar con {leading_zeros} bits a cero de 256")

    with st.expander("📐 Cómo se calcula el hash rate"):
        st.latex(r"\text{Hash rate} = \frac{\text{difficulty} \times 2^{32}}{600\,\text{s}}")
        st.caption(
            f"difficulty = {difficulty:,.0f}  →  "
            f"**{hashrate_ehs:.3f} EH/s** ({hashrate_ehs * 1e18:,.0f} H/s)"
        )

    st.markdown("---")

    # ── Preparar datos ────────────────────────────────────────────────────────
    if len(blocks) < 2:
        st.warning("No hay suficientes bloques.")
        return

    sorted_blocks = sorted(blocks, key=lambda b: b["height"], reverse=True)
    timestamps    = [b["timestamp"] for b in sorted_blocks]
    heights_list  = [b["height"] for b in sorted_blocks]
    inter_times   = [timestamps[i] - timestamps[i+1] for i in range(len(timestamps)-1)]
    inter_times   = [t for t in inter_times if t > 0]
    inter_heights = [heights_list[i] for i in range(len(inter_times))]

    if not inter_times:
        st.warning("Timestamps no válidos.")
        return

    avg_time = sum(inter_times) / len(inter_times)

    col_left, col_right = st.columns(2)

    # ── Histograma ────────────────────────────────────────────────────────────
    with col_left:
        st.subheader("📊 Distribución de tiempos entre bloques")

        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=inter_times,
            nbinsx=25,
            name="Tiempo entre bloques",
            marker=dict(
                color="#1F6FEB",
                opacity=0.85,
                line=dict(color="#388BFD", width=0.8),
            ),
            hovertemplate="[%{x:.0f} s]  frecuencia: %{y}<extra></extra>",
        ))

        # Curva exponencial teórica superpuesta
        x_exp = np.linspace(0, max(inter_times), 300)
        y_exp = (1/600) * np.exp(-x_exp/600)
        scale = len(inter_times) * (max(inter_times)/25)
        fig_hist.add_trace(go.Scatter(
            x=x_exp, y=y_exp * scale,
            mode="lines", name="Exp(1/600) teórica",
            line=dict(color="#39D353", width=2, dash="dot"),
            hovertemplate="t=%{x:.0f}s<extra></extra>",
        ))
        fig_hist.add_vline(x=600, line_dash="dash", line_color="#39D353", line_width=1.5,
                           annotation_text="600 s", annotation_font=dict(color="#39D353", size=10))
        fig_hist.add_vline(x=avg_time, line_dash="dot", line_color="#F0883E", line_width=1.5,
                           annotation_text=f"Media {avg_time:.0f}s",
                           annotation_font=dict(color="#F0883E", size=10))
        fig_hist.update_layout(
            xaxis_title="Segundos entre bloques",
            yaxis_title="Frecuencia",
            showlegend=True,
            title=dict(text="Inter-arrival times · Exp(1/600) esperado",
                       font=dict(size=11, color="#6E7681"), x=0),
            **_LAYOUT,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # ── Scatter timeline ──────────────────────────────────────────────────────
    with col_right:
        st.subheader("⏱️ Tiempos por altura de bloque")

        colors_scatter = [
            "#39D353" if t < 300 else "#F0883E" if t < 900 else "#F85149"
            for t in inter_times
        ]
        fig_sc = go.Figure()
        fig_sc.add_trace(go.Scatter(
            x=inter_heights,
            y=inter_times,
            mode="markers",
            marker=dict(
                color=colors_scatter,
                size=7,
                opacity=0.8,
                line=dict(color="#0D1117", width=0.5),
            ),
            hovertemplate="Bloque %{x:,}<br>%{y:.0f} s<extra></extra>",
            name="Inter-arrival time",
        ))
        fig_sc.add_hline(y=600, line_dash="dash", line_color="#58A6FF", line_width=1.5,
                         annotation_text="600 s target",
                         annotation_font=dict(color="#58A6FF", size=10))
        fig_sc.update_layout(
            xaxis_title="Altura del bloque",
            yaxis_title="Segundos",
            showlegend=False,
            title=dict(text="Verde < 300s · Naranja 300-900s · Rojo > 900s",
                       font=dict(size=11, color="#6E7681"), x=0),
            **_LAYOUT,
        )
        st.plotly_chart(fig_sc, use_container_width=True)

    # ── Stats row ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Media empírica",   f"{avg_time:.0f} s")
    c2.metric("Mínimo",           f"{min(inter_times):.0f} s")
    c3.metric("Máximo",           f"{max(inter_times):.0f} s")
    c4.metric("Desv. estándar",   f"{np.std(inter_times):.0f} s")

    st.markdown("---")

    # ── Nonce distribution ────────────────────────────────────────────────────
    st.subheader("🎲 Distribución de nonces (últimos 50 bloques)")

    nonces = [b.get("nonce", 0) for b in sorted_blocks if b.get("nonce")]
    if nonces:
        fig_nonce = go.Figure()
        fig_nonce.add_trace(go.Histogram(
            x=nonces,
            nbinsx=30,
            marker=dict(
                color="#8957E5",
                opacity=0.85,
                line=dict(color="#A371F7", width=0.8),
            ),
            hovertemplate="Nonce ~%{x:,}<br>count: %{y}<extra></extra>",
            name="Nonces",
        ))
        fig_nonce.update_layout(
            xaxis_title="Valor del nonce (0 – 2³²)",
            yaxis_title="Frecuencia",
            showlegend=False,
            title=dict(
                text="Los nonces deberían distribuirse uniformemente — indica búsqueda aleatoria del PoW",
                font=dict(size=11, color="#6E7681"), x=0,
            ),
            **_LAYOUT,
        )
        st.plotly_chart(fig_nonce, use_container_width=True)

    st.info(
        "**Distribución exponencial (proceso de Poisson):** el minado es *memoryless* — "
        "la probabilidad de encontrar el siguiente bloque es siempre la misma. "
        "El ajuste de dificultad cada 2 016 bloques mantiene la media cerca de 600 s."
    )
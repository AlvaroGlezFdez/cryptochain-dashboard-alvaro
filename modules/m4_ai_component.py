import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import expon

from api.blockchain_client import get_last_n_blocks

N_BLOCKS = 200
ALPHA = 0.05

# ── Shared Plotly layout ──────────────────────────────────────────────────────
_LAYOUT = dict(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#F5F0E8",
    font=dict(color="#6B6B6B", size=11),
    margin=dict(t=20, b=40, l=60, r=20),
    xaxis=dict(gridcolor="#E8E0D5", linecolor="#C4B5A8", title_font=dict(size=11)),
    yaxis=dict(gridcolor="#E8E0D5", linecolor="#C4B5A8", title_font=dict(size=11)),
)


@st.cache_data(ttl=60)
def _fetch_blocks():
    return get_last_n_blocks(N_BLOCKS)


def _inter_arrival_times(blocks: list) -> tuple[list, list]:
    sorted_b = sorted(blocks, key=lambda b: b["height"], reverse=True)
    inter_times = [
        sorted_b[i]["timestamp"] - sorted_b[i + 1]["timestamp"]
        for i in range(len(sorted_b) - 1)
    ]
    heights = [sorted_b[i]["height"] for i in range(len(inter_times))]
    return inter_times, heights


def _two_tailed_pvalue(t: float, loc: float, scale: float) -> float:
    p_lo = expon.cdf(t, loc=loc, scale=scale)
    return float(2 * min(p_lo, 1.0 - p_lo))


def render() -> None:
    st.header("IA — Detector de Anomalías en Tiempos de Bloque")

    with st.expander("Marco teórico: ¿por qué distribución exponencial?"):
        st.markdown(
            """
El minado de Bitcoin es un **proceso de Poisson**: en cada intento, todos los mineros
calculan SHA256²(header) esperando que el resultado sea menor que el target. Cada intento
es *independiente* y tiene probabilidad de éxito ínfima.

Un proceso de Poisson con tasa constante λ produce tiempos de espera **exponencialmente
distribuidos** con media 1/λ. En Bitcoin, el ajuste de dificultad cada 2 016 bloques
mantiene la media cerca de **600 segundos (10 min)** → inter-arrival times ∼ Exp(1/600).

**Propiedad sin memoria (*memoryless*):** si el último bloque llegó hace 5 min, la
probabilidad de que el siguiente llegue en los próximos 30 s es exactamente la misma que
si acabara de llegar. Esta propiedad es única de la exponencial.

Un **detector de anomalías** usa esta distribución como baseline: un bloque en las colas
extremas (p-valor bilateral < 5 %) puede indicar un pico de hash rate, un bloque retenido,
o una interrupción de la red.
            """
        )

    st.caption(
        f"Analizando los últimos **{N_BLOCKS} bloques** — "
        "datos en caché 60 s (la descarga inicial tarda ~20 s)."
    )

    with st.spinner(f"Descargando {N_BLOCKS} bloques..."):
        blocks = _fetch_blocks()

    if len(blocks) < 10:
        st.error("No se pudieron obtener suficientes bloques para el análisis.")
        return

    raw_times, all_heights = _inter_arrival_times(blocks)

    # ── Bug fix: filtrar valores <= 0 antes del ajuste exponencial ───────────
    valid_pairs = [(t, h) for t, h in zip(raw_times, all_heights) if t > 0]
    if len(valid_pairs) < 10:
        st.warning("No hay suficientes datos válidos (inter-arrival times > 0) para el análisis.")
        return

    inter_times = [t for t, _ in valid_pairs]
    heights     = [h for _, h in valid_pairs]
    arr = np.array(inter_times, dtype=float)

    # ── Ajuste exponencial ────────────────────────────────────────────────────
    loc, scale = expon.fit(arr, floc=0)

    p_values     = [_two_tailed_pvalue(t, loc, scale) for t in inter_times]
    anomaly_flags = [p < ALPHA for p in p_values]

    n_anom   = sum(anomaly_flags)
    pct_anom = 100 * n_anom / len(inter_times)

    # ── Métricas resumen ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bloques analizados",    len(inter_times))
    c2.metric("Anomalías (p < 0.05)", n_anom)
    c3.metric("% anomalías",           f"{pct_anom:.1f} %")
    c4.metric("λ⁻¹ ajustado",          f"{scale:.0f} s")

    c5, c6 = st.columns(2)
    c5.metric("Media empírica",  f"{np.mean(arr):.0f} s")
    c6.metric("Mediana empírica", f"{np.median(arr):.0f} s")

    # ── Histograma + curva teórica ────────────────────────────────────────────
    st.subheader("Distribución empírica vs. exponencial ajustada")

    x_range  = np.linspace(0, min(float(arr.max()), 5000), 600)
    pdf_vals = expon.pdf(x_range, loc=loc, scale=scale)

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=arr.tolist(),
        nbinsx=40,
        histnorm="probability density",
        name="Tiempos observados",
        marker_color="#8B6F5E",
        opacity=0.75,
        hovertemplate="[%{x:.0f} s]  densidad: %{y:.5f}<extra></extra>",
    ))
    fig_hist.add_trace(go.Scatter(
        x=x_range.tolist(),
        y=pdf_vals.tolist(),
        mode="lines",
        name=f"Exp ajustada  λ⁻¹ = {scale:.0f} s",
        line=dict(color="#4A3728", width=2.5),
        hovertemplate="t = %{x:.0f} s<br>f(t) = %{y:.6f}<extra></extra>",
    ))
    fig_hist.add_vline(
        x=600, line_dash="dash", line_color="#A0522D", line_width=1.5,
        annotation_text="600 s target",
        annotation_position="top right",
        annotation_font_color="#A0522D",
    )
    fig_hist.update_layout(
        xaxis_title="Segundos entre bloques",
        yaxis_title="Densidad de probabilidad",
        legend=dict(x=0.55, y=0.95, bgcolor="rgba(245,240,232,0.8)"),
        **_LAYOUT,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # ── Scatter por altura con anomalías ──────────────────────────────────────
    st.subheader("Inter-arrival times por altura — anomalías marcadas")

    norm_h = [heights[i] for i, a in enumerate(anomaly_flags) if not a]
    norm_t = [inter_times[i] for i, a in enumerate(anomaly_flags) if not a]
    anom_h = [heights[i] for i, a in enumerate(anomaly_flags) if a]
    anom_t = [inter_times[i] for i, a in enumerate(anomaly_flags) if a]
    anom_p = [p_values[i]   for i, a in enumerate(anomaly_flags) if a]

    fig_sc = go.Figure()
    fig_sc.add_trace(go.Scatter(
        x=norm_h, y=norm_t,
        mode="markers",
        name="Normal",
        marker=dict(color="#8B6F5E", size=5, opacity=0.6),
        hovertemplate="Bloque %{x}<br>%{y:.0f} s<extra></extra>",
    ))
    if anom_h:
        fig_sc.add_trace(go.Scatter(
            x=anom_h, y=anom_t,
            mode="markers",
            name=f"Anomalía (p < {ALPHA})",
            marker=dict(color="#A0522D", size=11, symbol="x-open",
                        line=dict(width=2, color="#A0522D")),
            text=[f"p = {p:.4f}" for p in anom_p],
            hovertemplate="Bloque %{x}<br>%{y:.0f} s<br>%{text}<extra></extra>",
        ))
    fig_sc.add_hline(
        y=600, line_dash="dash", line_color="#A0522D", line_width=1.5,
        annotation_text="600 s target",
        annotation_position="top right",
        annotation_font_color="#A0522D",
    )
    fig_sc.update_layout(
        xaxis_title="Altura del bloque",
        yaxis_title="Segundos entre bloques",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(245,240,232,0.8)"),
        **_LAYOUT,
    )
    st.plotly_chart(fig_sc, use_container_width=True)

    # ── Tabla de anomalías ────────────────────────────────────────────────────
    if n_anom > 0:
        st.subheader(f"Detalle de las {n_anom} anomalías detectadas")
        df_anom = pd.DataFrame({
            "Altura":    anom_h,
            "Tiempo (s)": [round(t) for t in anom_t],
            "p-valor":   [round(p, 6) for p in anom_p],
            "Tipo":      ["Muy rápido" if t < 600 else "Muy lento" for t in anom_t],
        }).sort_values("p-valor").reset_index(drop=True)
        st.dataframe(df_anom, use_container_width=True)
    else:
        st.success("No se detectaron anomalías estadísticas en la muestra analizada.")

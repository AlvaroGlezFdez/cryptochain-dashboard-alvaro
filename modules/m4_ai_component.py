import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import expon, kstest

from api.blockchain_client import get_last_n_blocks

N_BLOCKS = 200
ALPHA    = 0.05

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


@st.cache_data(ttl=60)
def _fetch_blocks():
    return get_last_n_blocks(N_BLOCKS)


def _inter_arrival_times(blocks: list) -> tuple[list, list]:
    sorted_b    = sorted(blocks, key=lambda b: b["height"], reverse=True)
    inter_times = [
        sorted_b[i]["timestamp"] - sorted_b[i+1]["timestamp"]
        for i in range(len(sorted_b)-1)
    ]
    heights = [sorted_b[i]["height"] for i in range(len(inter_times))]
    return inter_times, heights


def _two_tailed_pvalue(t: float, loc: float, scale: float) -> float:
    p_lo = expon.cdf(t, loc=loc, scale=scale)
    return float(2 * min(p_lo, 1.0 - p_lo))


def render() -> None:
    st.header("🤖 IA — Detector de Anomalías en Tiempos de Bloque")

    with st.expander("📚 Marco teórico: ¿por qué distribución exponencial?"):
        st.markdown("""
El minado de Bitcoin es un **proceso de Poisson**: cada intento de hash es independiente
con probabilidad de éxito ínfima. Esto produce tiempos de espera **Exp(1/600)** con media 600 s.

**Propiedad memoryless:** la probabilidad del siguiente bloque es siempre la misma,
independientemente del tiempo transcurrido.

El detector marca como anomalía cualquier bloque cuyo p-valor bilateral sea < 5%,
lo que puede indicar picos de hash rate, bloques retenidos o interrupciones de red.
        """)

    st.caption(f"Analizando los últimos **{N_BLOCKS} bloques** · caché 60 s.")

    with st.spinner(f"Descargando {N_BLOCKS} bloques..."):
        blocks = _fetch_blocks()

    if len(blocks) < 10:
        st.error("No se pudieron obtener suficientes bloques.")
        return

    raw_times, all_heights = _inter_arrival_times(blocks)
    valid_pairs = [(t, h) for t, h in zip(raw_times, all_heights) if t > 0]

    if len(valid_pairs) < 10:
        st.warning("No hay suficientes datos válidos.")
        return

    inter_times = [t for t, _ in valid_pairs]
    heights     = [h for _, h in valid_pairs]
    arr         = np.array(inter_times, dtype=float)

    loc, scale    = expon.fit(arr, floc=0)
    p_values      = [_two_tailed_pvalue(t, loc, scale) for t in inter_times]
    anomaly_flags = [p < ALPHA for p in p_values]

    n_anom   = sum(anomaly_flags)
    pct_anom = 100 * n_anom / len(inter_times)

    # ── KPIs ─────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bloques analizados",    len(inter_times))
    c2.metric("Anomalías detectadas",  n_anom,
              delta=f"{pct_anom:.1f}% del total", delta_color="inverse")
    c3.metric("λ⁻¹ ajustado",          f"{scale:.0f} s")
    c4.metric("Media empírica",         f"{np.mean(arr):.0f} s")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    # ── Histograma + curva ────────────────────────────────────────────────────
    with col_left:
        st.subheader("📊 Distribución empírica vs. teórica")

        x_range  = np.linspace(0, min(float(arr.max()), 5000), 600)
        pdf_vals = expon.pdf(x_range, loc=loc, scale=scale)

        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=arr.tolist(), nbinsx=40,
            histnorm="probability density",
            name="Observado",
            marker=dict(color="#1F6FEB", opacity=0.7,
                        line=dict(color="#388BFD", width=0.5)),
            hovertemplate="[%{x:.0f} s]  densidad: %{y:.5f}<extra></extra>",
        ))
        fig_hist.add_trace(go.Scatter(
            x=x_range.tolist(), y=pdf_vals.tolist(),
            mode="lines",
            name=f"Exp ajustada λ⁻¹={scale:.0f}s",
            line=dict(color="#39D353", width=2.5),
            hovertemplate="t=%{x:.0f}s  f(t)=%{y:.6f}<extra></extra>",
        ))
        fig_hist.add_vline(x=600, line_dash="dash", line_color="#F0883E", line_width=1.5,
                           annotation_text="600s", annotation_font=dict(color="#F0883E", size=10))
        fig_hist.update_layout(
            xaxis_title="Segundos entre bloques",
            yaxis_title="Densidad de probabilidad",
            title=dict(text=f"Ajuste Exp · λ⁻¹={scale:.1f}s · {n_anom} anomalías",
                       font=dict(size=11, color="#6E7681"), x=0),
            **_LAYOUT,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # ── Scatter anomalías ─────────────────────────────────────────────────────
    with col_right:
        st.subheader("🔎 Anomalías por altura de bloque")

        norm_h = [heights[i] for i, a in enumerate(anomaly_flags) if not a]
        norm_t = [inter_times[i] for i, a in enumerate(anomaly_flags) if not a]
        anom_h = [heights[i] for i, a in enumerate(anomaly_flags) if a]
        anom_t = [inter_times[i] for i, a in enumerate(anomaly_flags) if a]
        anom_p = [p_values[i]   for i, a in enumerate(anomaly_flags) if a]

        fig_sc = go.Figure()
        fig_sc.add_trace(go.Scatter(
            x=norm_h, y=norm_t, mode="markers", name="Normal",
            marker=dict(color="#388BFD", size=5, opacity=0.5),
            hovertemplate="Bloque %{x:,}<br>%{y:.0f}s<extra></extra>",
        ))
        if anom_h:
            fig_sc.add_trace(go.Scatter(
                x=anom_h, y=anom_t, mode="markers",
                name=f"Anomalía (p<{ALPHA})",
                marker=dict(color="#F85149", size=12, symbol="x-open",
                            line=dict(width=2.5, color="#F85149")),
                text=[f"p={p:.4f}" for p in anom_p],
                hovertemplate="Bloque %{x:,}<br>%{y:.0f}s<br>%{text}<extra></extra>",
            ))
        fig_sc.add_hline(y=600, line_dash="dash", line_color="#F0883E", line_width=1.5,
                         annotation_text="600s target",
                         annotation_font=dict(color="#F0883E", size=10))
        fig_sc.update_layout(
            xaxis_title="Altura del bloque",
            yaxis_title="Segundos entre bloques",
            title=dict(text="Azul=normal · Rojo✕=anomalía estadística",
                       font=dict(size=11, color="#6E7681"), x=0),
            **_LAYOUT,
        )
        st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("---")

    # ── P-valores timeline ────────────────────────────────────────────────────
    st.subheader("📉 P-valores a lo largo del tiempo")

    p_colors = ["#F85149" if p < ALPHA else "#388BFD" for p in p_values]
    fig_pval = go.Figure()
    fig_pval.add_trace(go.Scatter(
        x=heights, y=p_values,
        mode="markers",
        marker=dict(color=p_colors, size=6, opacity=0.75,
                    line=dict(color="#0D1117", width=0.5)),
        hovertemplate="Bloque %{x:,}<br>p-valor: %{y:.4f}<extra></extra>",
        name="p-valor",
    ))
    fig_pval.add_hline(y=ALPHA, line_dash="dash", line_color="#F0883E", line_width=1.5,
                       annotation_text=f"α={ALPHA}",
                       annotation_font=dict(color="#F0883E", size=11))
    fig_pval.update_layout(
        xaxis_title="Altura del bloque",
        yaxis_title="p-valor (bilateral)",
        showlegend=False,
        title=dict(text="Rojo = anomalía (p < 0.05) · Azul = normal",
                   font=dict(size=11, color="#6E7681"), x=0),
        **_LAYOUT,
    )
    st.plotly_chart(fig_pval, use_container_width=True)

    st.markdown("---")

    # ── Tabla anomalías ───────────────────────────────────────────────────────
    if n_anom > 0:
        st.subheader(f"📋 Detalle de las {n_anom} anomalías detectadas")
        df_anom = pd.DataFrame({
            "Altura":     anom_h,
            "Tiempo (s)": [round(t) for t in anom_t],
            "p-valor":    [round(p, 6) for p in anom_p],
            "Tipo":       ["⚡ Muy rápido" if t < 600 else "🐌 Muy lento" for t in anom_t],
        }).sort_values("p-valor").reset_index(drop=True)
        st.dataframe(df_anom, use_container_width=True)
    else:
        st.success("No se detectaron anomalías estadísticas en la muestra analizada.")

    st.markdown("---")

    # ── KS-test ───────────────────────────────────────────────────────────────
    st.subheader("🧪 Evaluación del modelo — Kolmogorov-Smirnov test")

    ks_stat, ks_pval = kstest(arr, "expon", args=(loc, scale))

    col_ks1, col_ks2, col_ks3 = st.columns(3)
    col_ks1.metric("KS statistic",  f"{ks_stat:.4f}")
    col_ks2.metric("p-valor KS",    f"{ks_pval:.4f}")
    col_ks3.metric("Umbral α",      f"{ALPHA}")

    if ks_pval > ALPHA:
        st.success(
            f"p-valor = {ks_pval:.4f} > {ALPHA} — ajuste exponencial estadísticamente aceptable."
        )
    else:
        st.warning(
            f"p-valor = {ks_pval:.4f} ≤ {ALPHA} — desviaciones detectadas. "
            "Puede indicar comportamiento de mining pools o cambios de hash rate."
        )
    st.caption(
        "El KS-test mide la distancia máxima entre la CDF empírica y la teórica ajustada. "
        "Es la métrica de bondad de ajuste estándar para distribuciones continuas."
    )
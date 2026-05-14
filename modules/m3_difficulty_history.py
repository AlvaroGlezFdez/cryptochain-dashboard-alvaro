import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from api.blockchain_client import get_difficulty_history

TARGET_PERIOD_S = 600 * 2016

_LAYOUT = dict(
    plot_bgcolor="#0D1117",
    paper_bgcolor="#0D1117",
    font=dict(color="#8B949E", size=11, family="Inter, sans-serif"),
    margin=dict(t=40, b=50, l=70, r=30),
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


@st.cache_data(ttl=300)
def _fetch(n_periods: int):
    return get_difficulty_history(n_periods)


def render() -> None:
    st.header("📈 Historial de Dificultad")
    st.caption(
        "Cada punto es un evento de ajuste (cada 2 016 bloques ≈ 2 semanas). "
        "Datos: Blockstream API · caché 5 min."
    )

    n_periods = st.slider(
        "Periodos de ajuste a mostrar",
        min_value=10, max_value=50, value=20, step=5,
        key="m3_n_periods",
        help="Cada periodo ≈ 2 semanas.",
    )

    with st.spinner("Cargando historial..."):
        data = _fetch(n_periods)

    if not data:
        st.error("No se pudo obtener el historial de dificultad.")
        return

    df = pd.DataFrame(data)
    df["date"]       = pd.to_datetime(df["timestamp"], unit="s")
    df               = df.sort_values("date").reset_index(drop=True)
    df["pct_change"] = df["difficulty"].pct_change() * 100
    df["duration_d"] = (df["ratio"] * TARGET_PERIOD_S) / 86400

    # ── KPIs ─────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ajustes mostrados",      len(df))
    c2.metric("Ratio medio",            f"{df['ratio'].mean():.3f}")
    c3.metric("Mayor subida",           f"+{df['pct_change'].max():.1f}%")
    c4.metric("Mayor bajada",           f"{df['pct_change'].min():.1f}%")

    st.markdown("---")

    # ── Gráfico 1: Dificultad con área y colores por cambio ───────────────────
    st.subheader("📉 Evolución de la dificultad")

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df["date"], y=df["difficulty"],
        mode="lines",
        name="Dificultad",
        line=dict(color="#1F6FEB", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(31,111,235,0.06)",
        hovertemplate=(
            "<b>Bloque %{customdata[0]:,}</b><br>"
            "%{x|%Y-%m-%d}<br>"
            "Dificultad: %{y:,.0f}<br>"
            "Cambio: %{customdata[1]:+.2f}%<extra></extra>"
        ),
        customdata=list(zip(df["height"], df["pct_change"].fillna(0))),
    ))
    # Marcadores coloreados por subida/bajada
    fig_line.add_trace(go.Scatter(
        x=df["date"], y=df["difficulty"],
        mode="markers",
        name="Ajuste",
        marker=dict(
            size=10,
            color=["#39D353" if c > 0 else "#F85149" for c in df["pct_change"].fillna(0)],
            symbol="circle",
            line=dict(color="#0D1117", width=2),
        ),
        hovertemplate=(
            "<b>Ajuste · Bloque %{customdata[0]:,}</b><br>"
            "Cambio: %{customdata[1]:+.2f}%<extra></extra>"
        ),
        customdata=list(zip(df["height"], df["pct_change"].fillna(0))),
    ))
    fig_line.update_layout(
        xaxis_title="Fecha", yaxis_title="Dificultad",
        hovermode="x unified",
        title=dict(text="Verde = subida · Rojo = bajada · Área = tendencia acumulada",
                   font=dict(size=11, color="#6E7681"), x=0),
        **_LAYOUT,
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    # ── Gráfico 2: Barras ratio + línea móvil ────────────────────────────────
    st.subheader("⚖️ Ratio tiempo real / target por periodo")

    colors_bar = ["#39D353" if r < 1.0 else "#F85149" for r in df["ratio"]]
    rolling_ratio = df["ratio"].rolling(3, min_periods=1).mean()

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df["date"], y=df["ratio"],
        marker=dict(color=colors_bar, opacity=0.75,
                    line=dict(color="#0D1117", width=0.5)),
        name="Ratio real/target",
        hovertemplate=(
            "%{x|%Y-%m-%d}<br>Ratio: %{y:.3f}<br>"
            "Duración: %{customdata:.1f} días<extra></extra>"
        ),
        customdata=df["duration_d"],
    ))
    fig_bar.add_trace(go.Scatter(
        x=df["date"], y=rolling_ratio,
        mode="lines", name="Media móvil (3p)",
        line=dict(color="#F0883E", width=2, dash="dot"),
        hovertemplate="Media móvil: %{y:.3f}<extra></extra>",
    ))
    fig_bar.add_hline(y=1.0, line_dash="dash", line_color="#58A6FF", line_width=1.5,
                      annotation_text="Target 1.0",
                      annotation_font=dict(color="#58A6FF", size=11))
    fig_bar.update_layout(
        xaxis_title="Fecha del ajuste",
        yaxis_title="Ratio (tiempo real / 1,209,600 s)",
        title=dict(text="Verde → rápido (dificultad sube)  ·  Rojo → lento (dificultad baja)  ·  Naranja = media móvil",
                   font=dict(size=11, color="#6E7681"), x=0),
        **_LAYOUT,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ── Gráfico 3: Cambio porcentual por ajuste ───────────────────────────────
    st.subheader("📊 Cambio porcentual en cada ajuste de dificultad")

    df_pct = df.dropna(subset=["pct_change"])
    colors_pct = ["#39D353" if c > 0 else "#F85149" for c in df_pct["pct_change"]]

    fig_pct = go.Figure()
    fig_pct.add_trace(go.Bar(
        x=df_pct["date"],
        y=df_pct["pct_change"],
        marker=dict(
            color=colors_pct,
            opacity=0.85,
            line=dict(color="#0D1117", width=0.5),
        ),
        name="Cambio %",
        hovertemplate="%{x|%Y-%m-%d}<br>Cambio: %{y:+.2f}%<extra></extra>",
    ))
    fig_pct.add_hline(y=0, line_color="#30363D", line_width=1)
    fig_pct.update_layout(
        xaxis_title="Fecha del ajuste",
        yaxis_title="Cambio de dificultad (%)",
        showlegend=False,
        title=dict(text="Cambio porcentual de dificultad por periodo de 2016 bloques",
                   font=dict(size=11, color="#6E7681"), x=0),
        **_LAYOUT,
    )
    st.plotly_chart(fig_pct, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.success("**Verde — ratio < 1:** bloques más rápidos → dificultad **sube**.")
    col2.error("**Rojo — ratio > 1:** bloques más lentos → dificultad **baja**.")
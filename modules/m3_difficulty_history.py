import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from api.blockchain_client import get_difficulty_history

TARGET_PERIOD_S = 600 * 2016  # 1,209,600 s ≈ 2 semanas

# ── Shared Plotly layout ──────────────────────────────────────────────────────
_LAYOUT = dict(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#F5F0E8",
    font=dict(color="#6B6B6B", size=11),
    margin=dict(t=20, b=40, l=60, r=20),
    xaxis=dict(gridcolor="#E8E0D5", linecolor="#C4B5A8", title_font=dict(size=11)),
    yaxis=dict(gridcolor="#E8E0D5", linecolor="#C4B5A8", title_font=dict(size=11)),
)


@st.cache_data(ttl=300)
def _fetch(n_periods: int):
    return get_difficulty_history(n_periods)


def render() -> None:
    st.header("Historial de Dificultad")
    st.caption(
        "Cada punto es un evento de ajuste (cada 2 016 bloques ≈ 2 semanas). "
        "Datos obtenidos de Blockstream API · caché 5 min."
    )

    n_periods = st.slider(
        "Periodos de ajuste a mostrar",
        min_value=10,
        max_value=50,
        value=20,
        step=5,
        key="m3_n_periods",
        help="Cada periodo ≈ 2 semanas. Valores altos tardan más en cargar.",
    )

    with st.spinner("Cargando historial desde Blockstream (solicitudes en paralelo)..."):
        data = _fetch(n_periods)

    if not data:
        st.error("No se pudo obtener el historial de dificultad.")
        return

    df = pd.DataFrame(data)   # columns: height, timestamp, difficulty, ratio
    df["date"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.sort_values("date").reset_index(drop=True)

    # ── 1. Línea temporal con marcador en cada ajuste ─────────────────────────
    st.subheader("Evolución de la dificultad de minado")

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df["date"],
        y=df["difficulty"],
        mode="lines+markers",
        name="Dificultad",
        line=dict(color="#4A3728", width=2),
        marker=dict(size=6, color="#4A3728", symbol="circle",
                    line=dict(color="#8B6F5E", width=1)),
        hovertemplate="Bloque %{customdata:,}<br>%{x|%Y-%m-%d}<br>Dificultad: %{y:,.0f}<extra></extra>",
        customdata=df["height"],
    ))
    fig_line.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Dificultad",
        hovermode="x unified",
        **_LAYOUT,
    )
    st.plotly_chart(fig_line, use_container_width=True)
    st.caption(
        f"Mostrando los últimos **{len(df)} ajustes** "
        f"≈ {len(df) * 2:.0f} semanas de historial."
    )

    # ── 2. Barras de ratio tiempo real / target ───────────────────────────────
    st.subheader("Ratio tiempo real del periodo vs. target  (1.0 = exactamente 600 s/bloque)")

    if len(df) < 2:
        st.warning("Se necesitan al menos 2 puntos para mostrar el ratio.")
        return

    colors = ["#5C8A5C" if r < 1.0 else "#A0522D" for r in df["ratio"]]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df["date"],
        y=df["ratio"],
        marker_color=colors,
        name="Ratio real/target",
        hovertemplate=(
            "%{x|%Y-%m-%d}<br>"
            "Ratio: %{y:.3f}<br>"
            "Duración: %{customdata:,.0f} s<extra></extra>"
        ),
        customdata=(df["ratio"] * TARGET_PERIOD_S).round(0),
    ))
    fig_bar.add_hline(
        y=1.0,
        line_dash="dash", line_color="#A0522D", line_width=2,
        annotation_text="Target = 1.0",
        annotation_position="top right",
        annotation_font_color="#A0522D",
    )
    fig_bar.update_layout(
        xaxis_title="Fecha del ajuste",
        yaxis_title="Ratio (tiempo real / 1,209,600 s)",
        showlegend=False,
        **_LAYOUT,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.info(
        "**Verde — ratio < 1:** bloques más rápidos de lo esperado → dificultad **sube**."
    )
    col2.info(
        "**Marrón — ratio > 1:** bloques más lentos de lo esperado → dificultad **baja**."
    )

    # ── Estadísticas del ratio ─────────────────────────────────────────────────
    ratio = df["ratio"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Ratio medio", f"{ratio.mean():.3f}")
    c2.metric("Periodos rápidos (< 1)", int((ratio < 1).sum()))
    c3.metric("Periodos lentos  (> 1)", int((ratio > 1).sum()))

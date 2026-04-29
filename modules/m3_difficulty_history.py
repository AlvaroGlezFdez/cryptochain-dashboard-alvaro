import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from api.blockchain_client import get_difficulty_history

TARGET_PERIOD_S = 600 * 2016  # 1,209,600 s ≈ 2 semanas


@st.cache_data(ttl=300)
def _fetch(n_periods: int):
    return get_difficulty_history(n_periods)


def render() -> None:
    st.header("M3 — Historial de Dificultad")
    st.caption(
        "Cada punto es un evento de ajuste de dificultad (cada 2016 bloques ≈ 2 semanas). "
        "Datos en caché 5 min."
    )

    n_periods = st.slider(
        "Periodos de ajuste a mostrar",
        min_value=20,
        max_value=200,
        value=100,
        step=10,
        key="m3_n_periods",
    )

    with st.spinner("Cargando historial desde blockchain.info..."):
        data = _fetch(n_periods)

    if not data:
        st.error("No se pudo obtener el historial de dificultad de blockchain.info.")
        return

    df = pd.DataFrame(data)          # columnas: x (timestamp), y (difficulty)
    df["date"] = pd.to_datetime(df["x"], unit="s")
    df["difficulty"] = df["y"].astype(float)
    df = df.sort_values("date").reset_index(drop=True)

    # ── 1. Línea temporal con marcadores en cada ajuste ───────────────────────
    st.subheader("Evolución de la dificultad de minado")

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df["date"],
        y=df["difficulty"],
        mode="lines+markers",
        name="Dificultad",
        line=dict(color="#f7931a", width=2),
        marker=dict(size=5, color="#f7931a", symbol="circle"),
        hovertemplate="%{x|%Y-%m-%d}<br>Dificultad: %{y:,.0f}<extra></extra>",
    ))
    fig_line.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Dificultad",
        template="plotly_dark",
        hovermode="x unified",
        margin=dict(t=20),
    )
    st.plotly_chart(fig_line, use_container_width=True)
    st.caption(
        f"Mostrando los últimos **{len(df)} ajustes** "
        f"≈ {len(df) * 2:.0f} semanas de historial."
    )

    # ── 2. Ratio tiempo real / target ─────────────────────────────────────────
    st.subheader("Ratio tiempo real del periodo vs. target (1.0 = exactamente 600 s/bloque)")

    if len(df) < 2:
        st.warning("Se necesitan al menos 2 puntos para calcular el ratio.")
        return

    df["delta_s"] = df["x"].diff()                      # segundos entre ajustes consecutivos
    df_ratio = df.dropna(subset=["delta_s"]).copy()
    df_ratio["ratio"] = df_ratio["delta_s"] / TARGET_PERIOD_S
    df_ratio["color"] = df_ratio["ratio"].apply(
        lambda r: "#2ecc71" if r < 1.0 else "#e74c3c"
    )

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df_ratio["date"],
        y=df_ratio["ratio"],
        marker_color=df_ratio["color"].tolist(),
        name="Ratio real/target",
        hovertemplate=(
            "%{x|%Y-%m-%d}<br>"
            "Ratio: %{y:.3f}<br>"
            "Duración: %{customdata:,.0f} s<extra></extra>"
        ),
        customdata=df_ratio["delta_s"].tolist(),
    ))
    fig_bar.add_hline(
        y=1.0,
        line_dash="dash",
        line_color="white",
        line_width=2,
        annotation_text="Target ratio = 1.0",
        annotation_position="top right",
        annotation_font_color="white",
    )
    fig_bar.update_layout(
        xaxis_title="Fecha del ajuste",
        yaxis_title="Ratio (tiempo real / 1,209,600 s)",
        template="plotly_dark",
        showlegend=False,
        margin=dict(t=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.info(
        "**Verde — ratio < 1:** los bloques se minaron más rápido de lo esperado. "
        "La red ajustará la dificultad **al alza** en el siguiente periodo."
    )
    col2.info(
        "**Rojo — ratio > 1:** los bloques tardaron más de lo esperado. "
        "La red ajustará la dificultad **a la baja** en el siguiente periodo."
    )

    # ── Estadísticas del ratio ─────────────────────────────────────────────────
    ratio = df_ratio["ratio"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Ratio medio", f"{ratio.mean():.3f}")
    c2.metric("Periodos rápidos (ratio < 1)", int((ratio < 1).sum()))
    c3.metric("Periodos lentos  (ratio > 1)", int((ratio > 1).sum()))

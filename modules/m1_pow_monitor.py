import plotly.graph_objects as go
import streamlit as st

from api.blockchain_client import get_last_n_blocks, get_latest_block

# ── Shared Plotly layout ──────────────────────────────────────────────────────
_LAYOUT = dict(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#F5F0E8",
    font=dict(color="#6B6B6B", size=11),
    margin=dict(t=20, b=40, l=50, r=20),
    xaxis=dict(gridcolor="#E8E0D5", linecolor="#C4B5A8", title_font=dict(size=11)),
    yaxis=dict(gridcolor="#E8E0D5", linecolor="#C4B5A8", title_font=dict(size=11)),
)


def _target_from_bits(bits_int: int) -> int:
    exp = (bits_int >> 24) & 0xFF
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
    st.header("Monitor de Proof of Work")
    st.caption("Datos en caché 60 s — se actualizan automáticamente.")

    with st.spinner("Conectando con la red Bitcoin..."):
        latest, blocks = _fetch_pow_data()

    if not latest:
        st.error("No se pudo conectar con la API de Blockstream.")
        return

    difficulty = latest.get("difficulty", 0)
    bits_int = latest.get("bits", 0)
    height = latest.get("height", 0)

    # ── Métricas principales ──────────────────────────────────────────────────
    hashrate_ehs = (difficulty * 2**32) / 600 / 1e18
    target = _target_from_bits(bits_int)
    leading_zeros = _leading_zero_bits(target)

    col1, col2, col3 = st.columns(3)
    col1.metric("Dificultad actual", f"{difficulty:,.0f}")
    col2.metric("Hash rate estimado", f"{hashrate_ehs:.2f} EH/s")
    col3.metric("Altura del bloque", f"{height:,}")

    # ── Target visual ─────────────────────────────────────────────────────────
    st.subheader("Target de dificultad (256 bits)")
    st.code(f"{target:064x}", language=None)
    st.caption(
        f"El hash ganador debe empezar con al menos **{leading_zeros} bits a cero** (de 256). "
        f"Campo `bits`: `{bits_int:#010x}`."
    )
    st.progress(leading_zeros / 256, text=f"{leading_zeros} / 256 bits a cero en el target")

    with st.expander("Cómo se calcula el hash rate"):
        st.latex(r"\text{Hash rate} = \frac{\text{difficulty} \times 2^{32}}{600\,\text{s}}")
        st.caption(
            f"difficulty = {difficulty:,.0f}  →  "
            f"**{hashrate_ehs:.3f} EH/s** ({hashrate_ehs * 1e18:,.0f} H/s)"
        )

    # ── Histograma de tiempos entre bloques ───────────────────────────────────
    st.subheader("Distribución de tiempos entre bloques (últimos 50 bloques)")

    if len(blocks) < 2:
        st.warning("No hay suficientes bloques para calcular los tiempos.")
        return

    sorted_blocks = sorted(blocks, key=lambda b: b["height"], reverse=True)
    timestamps = [b["timestamp"] for b in sorted_blocks]
    inter_times = [timestamps[i] - timestamps[i + 1] for i in range(len(timestamps) - 1)]
    inter_times = [t for t in inter_times if t > 0]   # descartar valores inválidos

    if not inter_times:
        st.warning("Los timestamps de los bloques no son válidos.")
        return

    avg_time = sum(inter_times) / len(inter_times)

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=inter_times,
        nbinsx=25,
        name="Tiempo entre bloques",
        marker_color="#8B6F5E",
        opacity=0.85,
    ))
    fig.add_vline(
        x=600, line_dash="dash", line_color="#A0522D", line_width=2,
        annotation_text="Target 600 s", annotation_position="top right",
        annotation_font_color="#A0522D",
    )
    fig.add_vline(
        x=avg_time, line_dash="dot", line_color="#4A3728", line_width=2,
        annotation_text=f"Media {avg_time:.0f} s", annotation_position="top left",
        annotation_font_color="#4A3728",
    )
    fig.update_layout(
        xaxis_title="Segundos entre bloques",
        yaxis_title="Frecuencia",
        showlegend=False,
        **_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "**Distribución exponencial (proceso de Poisson):** el minado de Bitcoin es un proceso "
        "*memoryless* — la probabilidad de encontrar el siguiente bloque es siempre la misma, "
        "independientemente del tiempo ya transcurrido. El ajuste de dificultad cada 2 016 bloques "
        "mantiene la media cerca de 600 s."
    )

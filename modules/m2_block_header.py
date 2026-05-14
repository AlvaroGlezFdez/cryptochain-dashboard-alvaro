import hashlib
from datetime import datetime, timezone

import streamlit as st

from api.blockchain_client import get_block, get_block_header_hex, get_latest_block


def _target_from_bits(bits_int: int) -> int:
    exp  = (bits_int >> 24) & 0xFF
    coef = bits_int & 0x00FFFFFF
    return coef * (2 ** (8 * (exp - 3)))


def _count_leading_zero_bits(hash_hex: str) -> int:
    value = int(hash_hex, 16)
    if value == 0:
        return 256
    return 256 - value.bit_length()


def _double_sha256(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


@st.cache_data(ttl=60)
def _fetch_header_data():
    latest = get_latest_block()
    if not latest:
        return None, None, None

    hashes_to_try = [latest.get("id")]
    prev = latest.get("previousblockhash")
    if prev:
        hashes_to_try.append(prev)

    for block_hash in hashes_to_try:
        full_block = get_block(block_hash)
        header_hex = get_block_header_hex(block_hash)
        if header_hex and len(header_hex) == 160:
            return full_block, header_hex, block_hash

    return None, None, None


def render() -> None:
    st.header("🔍 Analizador de Header de Bloque")
    st.caption("Último bloque en caché 60 s · verificación PoW local con hashlib · byte order: little-endian")

    with st.spinner("Obteniendo header del último bloque..."):
        block, header_hex, block_hash = _fetch_header_data()

    if not block:
        st.error("No se pudo obtener el bloque de la API.")
        return

    bits_int = block.get("bits", 0)
    ts       = block.get("timestamp", 0)
    dt_utc   = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # ── Estructura 80 bytes ───────────────────────────────────────────────────
    st.subheader("📦 Estructura del header (80 bytes)")

    fields = [
        ("Version",             str(block.get("version")),                          hex(block.get("version", 0)),  "4 bytes · little-endian"),
        ("Previous block hash", str(block.get("previousblockhash", ""))[:24] + "…", "",                           "32 bytes · hash del bloque anterior"),
        ("Merkle root",         str(block.get("merkle_root", ""))[:24] + "…",       "",                           "32 bytes · raíz del árbol de transacciones"),
        ("Timestamp",           str(ts),                                             dt_utc,                       "4 bytes · Unix epoch · little-endian"),
        ("Bits",                hex(bits_int),                                       str(bits_int),                "4 bytes · target comprimido"),
        ("Nonce",               str(block.get("nonce")),                             "",                           "4 bytes · valor que satisface PoW"),
    ]
    icons = ["🔢", "⛓️", "🌿", "⏰", "🎯", "🔑"]
    colors = ["#388BFD", "#39D353", "#A371F7", "#F0883E", "#58A6FF", "#F85149"]

    for icon, color, (label, val, extra, hint) in zip(icons, colors, fields):
        c1, c2 = st.columns([1, 3])
        c1.markdown(
            "<div style='background:#0D1117; border:1px solid " + color + "44; "
            "border-left:3px solid " + color + "; border-radius:8px; "
            "padding:10px 14px; height:100%;'>"
            "<span style='font-size:1.1rem'>" + icon + "</span> "
            "<span style='color:#CDD9E5; font-weight:600; font-size:0.85rem'>" + label + "</span>"
            "<br><span style='color:#6E7681; font-size:0.72rem'>" + hint + "</span></div>",
            unsafe_allow_html=True,
        )
        extra_html = ("  <span style='color:#6E7681'>→ " + extra + "</span>") if extra else ""
        c2.markdown(
            "<div style='background:#0D1117; border:1px solid #21262D; border-radius:8px; "
            "padding:10px 14px; font-family:monospace; color:" + color + "; "
            "font-size:0.82rem; height:100%; letter-spacing:0.3px;'>"
            + val + extra_html + "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Verificación PoW ──────────────────────────────────────────────────────
    st.subheader("✅ Verificación local del Proof of Work")

    if not header_hex:
        st.warning("Header no disponible aún — refresca en unos segundos.")
        return
    if len(header_hex) != 160:
        st.error("Header inesperado: " + str(len(header_hex)) + " chars (se esperaban 160).")
        return

    header_bytes  = bytes.fromhex(header_hex)
    computed_hash = _double_sha256(header_bytes)[::-1].hex()
    match         = computed_hash == block_hash
    border_color  = "#39D353" if match else "#F85149"

    col_a, col_b = st.columns(2)
    col_a.markdown(
        "<div style='background:#0D1117; border:1px solid " + border_color + "66; "
        "border-top:2px solid " + border_color + "; border-radius:10px; padding:14px 18px;'>"
        "<p style='color:#8B949E; font-size:0.72rem; text-transform:uppercase; "
        "letter-spacing:0.8px; margin:0 0 8px;'>Hash calculado (hashlib)</p>"
        "<code style='font-size:0.72rem; color:" + border_color + "; word-break:break-all; "
        "background:transparent!important; border:none!important;'>" + computed_hash + "</code>"
        "</div>",
        unsafe_allow_html=True,
    )
    col_b.markdown(
        "<div style='background:#0D1117; border:1px solid " + border_color + "66; "
        "border-top:2px solid " + border_color + "; border-radius:10px; padding:14px 18px;'>"
        "<p style='color:#8B949E; font-size:0.72rem; text-transform:uppercase; "
        "letter-spacing:0.8px; margin:0 0 8px;'>Hash oficial (Blockstream)</p>"
        "<code style='font-size:0.72rem; color:" + border_color + "; word-break:break-all; "
        "background:transparent!important; border:none!important;'>" + block_hash + "</code>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if match:
        st.success("🎉 Los hashes coinciden — header íntegro y PoW verificado localmente.")
    else:
        st.error("⚠️ Los hashes NO coinciden.")

    st.markdown("---")

    # ── Leading zero bits ─────────────────────────────────────────────────────
    st.subheader("🔢 Bits a cero del hash resultante")

    leading_zeros = _count_leading_zero_bits(computed_hash)
    col1, col2 = st.columns([1, 3])
    col1.metric("Leading zero bits", str(leading_zeros) + " / 256")
    with col2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.progress(leading_zeros / 256,
                    text=str(leading_zeros) + " bits a cero sobre 256 — threshold SHA-256")

    # ── Visualización de bits del hash ────────────────────────────────────────
    st.markdown("##### Representación binaria del hash (primeros 64 bits)")
    hash_int    = int(computed_hash, 16)
    top64_bits  = format(hash_int >> 192, "064b")
    bits_html   = ""
    for i, bit in enumerate(top64_bits):
        if i % 8 == 0 and i > 0:
            bits_html += "<span style='margin:0 3px'></span>"
        color = "#39D353" if bit == "0" else "#F85149"
        bits_html += (
            "<span style='display:inline-block; width:10px; height:10px; margin:1px; "
            "border-radius:2px; background:" + color + "; opacity:0.9;'></span>"
        )
    st.markdown(
        "<div style='background:#0D1117; border:1px solid #21262D; border-radius:10px; "
        "padding:14px 16px; line-height:1.8;'>" + bits_html +
        "<br><span style='color:#6E7681; font-size:0.72rem;'>Verde = 0 · Rojo = 1 · "
        "Los primeros " + str(leading_zeros) + " bits son cero</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Target del campo bits ─────────────────────────────────────────────────
    st.subheader("🎯 Target derivado del campo `bits`")

    exp    = (bits_int >> 24) & 0xFF
    coef   = bits_int & 0x00FFFFFF
    target = _target_from_bits(bits_int)

    with st.expander("📐 Fórmula y cálculo paso a paso"):
        st.latex(r"\text{target} = \text{coef} \times 2^{8 \times (\text{exp} - 3)}")
        col_e, col_c, col_t = st.columns(3)
        col_e.metric("Exponente (exp)",    str(exp))
        col_c.metric("Coeficiente (coef)", hex(coef))
        col_t.metric("Bits efectivos",     str(target.bit_length()))

    target_hex = format(target, "064x")
    st.markdown(
        "<div style='background:#0D1117; border:1px solid #21262D; "
        "border-left:3px solid #58A6FF; border-radius:10px; "
        "padding:14px 20px; margin-top:8px;'>"
        "<p style='color:#8B949E; font-size:0.72rem; text-transform:uppercase; "
        "letter-spacing:0.8px; margin:0 0 8px;'>Target (64 hex chars = 256 bits)</p>"
        "<code style='font-size:0.78rem; color:#58A6FF; word-break:break-all; "
        "background:transparent!important; border:none!important; letter-spacing:1px;'>"
        + target_hex + "</code></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if hash_int < target:
        st.success("hash < target — ✅ Proof of Work válido")
    else:
        st.error("hash ≥ target — ❌ Proof of Work inválido")
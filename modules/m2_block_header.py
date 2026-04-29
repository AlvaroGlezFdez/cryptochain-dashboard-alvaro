import hashlib
from datetime import datetime, timezone

import streamlit as st

from api.blockchain_client import get_block, get_block_header_hex, get_latest_block


def _target_from_bits(bits_int: int) -> int:
    exp = (bits_int >> 24) & 0xFF
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
    block_hash = latest.get("id")
    full_block = get_block(block_hash)
    header_hex = get_block_header_hex(block_hash)
    return full_block, header_hex, block_hash


def render() -> None:
    st.header("M2 — Analizador de Header de Bloque")
    st.caption("Último bloque en caché 60 s — verificación PoW local con hashlib.")

    with st.spinner("Obteniendo header del último bloque..."):
        block, header_hex, block_hash = _fetch_header_data()

    if not block:
        st.error("No se pudo obtener el bloque de la API.")
        return

    # ── 1. Los 6 campos del header ─────────────────────────────────────────────
    st.subheader("Campos del header (80 bytes)")

    bits_int = block.get("bits", 0)
    ts = block.get("timestamp", 0)
    dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    fields = {
        "Version": f"{block.get('version')}  (`{block.get('version'):#010x}`)",
        "Previous block hash": f"`{block.get('previousblockhash')}`",
        "Merkle root": f"`{block.get('merkle_root')}`",
        "Timestamp": f"{ts}  →  {dt_utc}",
        "Bits": f"`{bits_int:#010x}`  ({bits_int})",
        "Nonce": f"{block.get('nonce')}",
    }

    for label, value in fields.items():
        col_l, col_r = st.columns([1, 3])
        col_l.markdown(f"**{label}**")
        col_r.markdown(value)

    st.divider()

    # ── 2. Verificación local del PoW ──────────────────────────────────────────
    st.subheader("Verificación local del Proof of Work")

    if not header_hex:
        st.warning("No se pudo obtener el header en hex — la verificación no está disponible.")
        return

    if len(header_hex) != 160:
        st.error(f"Header inesperado: {len(header_hex)} caracteres (se esperaban 160).")
        return

    # SHA256(SHA256(header)) → resultado en little-endian → invertir para display
    header_bytes = bytes.fromhex(header_hex)
    hash_bytes_le = _double_sha256(header_bytes)
    computed_hash = hash_bytes_le[::-1].hex()   # big-endian (display format)

    hash_matches = computed_hash == block_hash

    col_a, col_b = st.columns(2)
    col_a.markdown("**Hash calculado localmente**")
    col_a.code(computed_hash, language=None)
    col_b.markdown("**Hash oficial (Blockstream)**")
    col_b.code(block_hash, language=None)

    if hash_matches:
        st.success("✅ Los hashes coinciden — el header está íntegro.")
    else:
        st.error("❌ Los hashes NO coinciden.")

    # ── 3. Bits a cero del hash ────────────────────────────────────────────────
    st.subheader("Bits a cero del hash resultante")

    leading_zeros = _count_leading_zero_bits(computed_hash)
    st.metric("Bits a cero (leading zeros)", f"{leading_zeros} / 256")

    frac = leading_zeros / 256
    st.progress(frac, text=f"{leading_zeros} bits a cero sobre 256")

    # ── 4. Target derivado del campo bits ──────────────────────────────────────
    st.subheader("Target derivado del campo `bits`")

    exp = (bits_int >> 24) & 0xFF
    coef = bits_int & 0x00FFFFFF
    target = _target_from_bits(bits_int)
    target_hex = f"{target:064x}"

    with st.expander("Fórmula y cálculo"):
        st.latex(r"\text{target} = \text{coef} \times 2^{8 \times (\text{exp} - 3)}")
        st.write(f"- `bits` = `{bits_int:#010x}`")
        st.write(f"- exp  = `{exp:#04x}` = {exp}")
        st.write(f"- coef = `{coef:#08x}` = {coef}")
        st.write(f"- target = `{coef:#x}` × 2^(8×({exp}−3)) = 2^(8×{exp - 3})")

    st.code(target_hex, language=None)

    # Verificar que hash < target (PoW válido)
    hash_int = int(computed_hash, 16)
    pow_valid = hash_int < target

    if pow_valid:
        st.success(f"✅ hash < target — Proof of Work válido")
    else:
        st.error(f"❌ hash ≥ target — Proof of Work inválido")

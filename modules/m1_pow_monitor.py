"""
Module M1 – Proof-of-Work Monitor.

Displays real-time PoW metrics for the latest block.
"""

import streamlit as st

from api.blockchain_client import get_latest_block


def render() -> None:
    """Render the PoW Monitor panel."""
    st.header("M1 – Proof-of-Work Monitor")

    if st.button("Fetch latest block", key="m1_fetch"):
        with st.spinner("Fetching…"):
            try:
                block = get_latest_block()
                st.success(f"Block height: **{block.get('height')}**")
                st.json(block)
            except Exception as exc:
                st.error(f"Error fetching data: {exc}")
    else:
        st.info("Click the button above to load the latest block data.")

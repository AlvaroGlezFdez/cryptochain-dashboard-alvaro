"""
Module M4 – AI Component.

Placeholder for the AI/ML feature chosen by each student.
Replace this module with your own implementation.
"""

import streamlit as st


def render() -> None:
    """Render the AI Component panel."""
    st.header("M4 – AI Component")
    st.info(
        "This module is a placeholder. "
        "Replace it with your chosen AI approach "
        "(e.g. anomaly detection, price prediction, clustering…)."
    )

    st.subheader("Suggested steps")
    st.markdown(
        """
        1. Collect and prepare your dataset (save to `data/`).
        2. Implement your model in this file (or import from a helper module).
        3. Display results, predictions, or visualisations here.
        """
    )

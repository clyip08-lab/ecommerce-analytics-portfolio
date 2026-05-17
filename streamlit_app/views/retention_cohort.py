# streamlit_app/views/retention_cohort.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import load_csv


def show():
    st.title("🔄 Retention & Cohort Analysis")
    st.markdown("User retention, repeat purchase behaviour, and cohort tracking.")
    st.markdown("---")

    # ── FIX: use relative path OR load_csv (NO WINDOWS PATH) ──
    df_seg = load_csv("analysis_rfm_segments.csv")

    if df_seg.empty:
        st.warning("RFM segment data not found.")
        return

    # ── Find columns safely ──
    seg_col = next((c for c in df_seg.columns if "segment" in c.lower()), df_seg.columns[0])
    user_col = next((c for c in df_seg.columns if "user" in c.lower()), None)
    rev_col = next((c for c in df_seg.columns if "revenue" in c.lower()), None)

    total = df_seg[user_col].sum() if user_col else 0

    # ── KPI cards ──
    st.subheader("👥 Retention Segment Breakdown")

    cols = st.columns(min(len(df_seg), 4))

    for i, (_, row) in enumerate(df_seg.iterrows()):
        if i >= len(cols):
            break

        users = row[user_col] if user_col else 0
        pct = users / total * 100 if total > 0 else 0
        label = str(row[seg_col]).split()[-1]

        cols[i].metric(label, f"{users:,.0f}", f"{pct:.1f}%")

    st.markdown("---")

    col1, col2 = st.columns(2)

    # ── PIE CHART ──
    with col1:
        st.subheader("🍩 Segment Distribution")

        if user_col:
            df_pie = df_seg.copy()

            fig1 = px.pie(
                df_pie,
                names=seg_col,
                values=user_col,
                hole=0.45,
                template="plotly_white",
            )

            fig1.update_layout(height=380)
            st.plotly_chart(fig1, use_container_width=True)

    # ── REVENUE BAR ──
    with col2:
        st.subheader("💰 Revenue by Segment")

        if rev_col:
            fig2 = px.bar(
                df_seg.sort_values(rev_col, ascending=True),
                x=rev_col,
                y=seg_col,
                orientation="h",
                color=rev_col,
                color_continuous_scale="Blues",
                template="plotly_white",
            )

            fig2.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── COHORT (SAFE VERSION) ──
    st.subheader("🔥 Cohort Retention Heatmap")

    df_cohort = load_csv("analysis_cohort_long.csv")

    if not df_cohort.empty:

        cohort_col = next((c for c in df_cohort.columns if "cohort" in c.lower()), df_cohort.columns[0])
        period_col = next((c for c in df_cohort.columns if "period" in c.lower() or "label" in c.lower()), None)
        ret_col = next((c for c in df_cohort.columns if "retention" in c.lower() or "pct" in c.lower()), None)

        if period_col and ret_col:

            pivot = df_cohort.pivot_table(
                index=cohort_col,
                columns=period_col,
                values=ret_col,
                aggfunc="mean"
            )

            fig = go.Figure(go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                colorscale="Blues"
            ))

            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Cohort data not available.")
# streamlit_app/pages/customer_segments.py

import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import load_csv, run_query

def show():
    st.title("👥 Customer Segments")
    st.markdown("RFM segmentation, conversion funnel, and buyer behaviour.")
    st.markdown("---")

    # ── Load RFM from CSV (path-independent) ──
    df_seg = load_csv("analysis_rfm_segments.csv")

    if df_seg.empty:
        st.error("❌ analysis_rfm_segments.csv not found.")
        return

    # ── Find column names dynamically ──
    user_col    = next((c for c in df_seg.columns if "user"    in c.lower() and "id" not in c.lower()), "users")
    rev_col     = next((c for c in df_seg.columns if "revenue" in c.lower()), None)
    seg_col     = next((c for c in df_seg.columns if "segment" in c.lower()), df_seg.columns[0])
    mon_col     = next((c for c in df_seg.columns if "monetary" in c.lower() or "spend" in c.lower()), rev_col)

    # ── KPI row ──
    total_users = df_seg[user_col].sum() if user_col in df_seg.columns else 0
    total_rev   = df_seg[rev_col].sum()  if rev_col  in df_seg.columns else 0
    top_seg_row = df_seg.loc[df_seg[rev_col].idxmax()] if rev_col else None
    top_seg     = top_seg_row[seg_col] if top_seg_row is not None else "N/A"

    champ_mask  = df_seg[seg_col].str.contains("Champion", case=False, na=False)
    champ_rev   = df_seg.loc[champ_mask, rev_col].sum() if rev_col else 0
    champ_share = champ_rev / total_rev * 100 if total_rev > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total Buyers",    f"{total_users:,.0f}")
    c2.metric("💰 Total Revenue",   f"${total_rev:,.0f}")
    c3.metric("🏆 Top Segment",     str(top_seg).split()[-1])
    c4.metric("👑 Champions Share", f"{champ_share:.1f}%")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👥 Users by RFM Segment")
        if user_col in df_seg.columns:
            fig1 = px.bar(
                df_seg.sort_values(user_col),
                x=user_col, y=seg_col, orientation="h",
                color=rev_col if rev_col else user_col,
                color_continuous_scale="Blues",
                text=user_col,
                labels={user_col:"Users", seg_col:"Segment"},
                template="plotly_white",
            )
            fig1.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig1.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig1, width='stretch')

    with col2:
        st.subheader("💰 Revenue by RFM Segment")
        if rev_col:
            fig2 = px.treemap(
                df_seg, path=[seg_col], values=rev_col,
                color=mon_col if mon_col else rev_col,
                color_continuous_scale="RdYlGn",
            )
            fig2.update_layout(height=420)
            st.plotly_chart(fig2, width='stretch')

    st.markdown("---")

    # ── Segment Detail Table ──
    st.subheader("📋 Segment Detail")
    st.dataframe(
        df_seg.sort_values(rev_col, ascending=False) if rev_col else df_seg,
        width='stretch'
    )

    st.markdown("---")

    # ── Funnel drop-off from CSV ──
    st.subheader("🔽 Funnel Drop-off by Category")
    df_funnel_cat = load_csv("analysis_funnel_category.csv")
    if not df_funnel_cat.empty:
        cat_col  = next((c for c in df_funnel_cat.columns if "category" in c.lower()), None)
        v2c_col  = next((c for c in df_funnel_cat.columns if "view_to_cart"     in c.lower()), None)
        c2p_col  = next((c for c in df_funnel_cat.columns if "cart_to_purchase" in c.lower()), None)

        if cat_col and v2c_col and c2p_col:
            fig3 = px.bar(
                df_funnel_cat.head(10), x=cat_col,
                y=[v2c_col, c2p_col],
                barmode="group",
                labels={"value":"Rate (%)","variable":"Stage"},
                color_discrete_sequence=["#4361ee","#f72585"],
                template="plotly_white",
            )
            fig3.update_layout(height=380, xaxis_tickangle=-30)
            st.plotly_chart(fig3, width='stretch')
    else:
        st.info("Funnel category data not available.")

# streamlit_app/views/customer_segments.py

import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import load_csv

def show():
    st.title("👥 Customer Segments")
    st.markdown("RFM segmentation, conversion funnel, and buyer behaviour.")
    st.markdown("---")

    df_seg = load_csv("analysis_rfm_segments.csv")
    if df_seg.empty:
        st.error("❌ analysis_rfm_segments.csv not found.")
        return

    user_col = next((c for c in df_seg.columns
                     if "user" in c.lower() and "id" not in c.lower()), "users")
    rev_col  = next((c for c in df_seg.columns
                     if "revenue" in c.lower()), None)
    seg_col  = next((c for c in df_seg.columns
                     if "segment" in c.lower()), df_seg.columns[0])
    mon_col  = next((c for c in df_seg.columns
                     if "monetary" in c.lower()), rev_col)

    total_users = df_seg[user_col].sum() if user_col in df_seg.columns else 0
    total_rev   = df_seg[rev_col].sum()  if rev_col else 0
    champ_mask  = df_seg[seg_col].str.contains("Champion", case=False, na=False)
    champ_rev   = df_seg.loc[champ_mask, rev_col].sum() if rev_col else 0
    champ_share = champ_rev / total_rev * 100 if total_rev > 0 else 0
    top_seg     = df_seg.loc[df_seg[rev_col].idxmax(), seg_col] if rev_col else "N/A"

    # ── KPI Cards ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total Buyers",    f"{total_users:,.0f}")
    c2.metric("💰 Total Revenue",   f"${total_rev:,.0f}")
    c3.metric("🏆 Top Segment",     str(top_seg).split()[-1])
    c4.metric("👑 Champions Share", f"{champ_share:.1f}%")

    st.markdown("---")

    # ── Two columns ──
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👥 Users by Segment")
        df_bar        = df_seg[df_seg[user_col] > 0].copy()
        df_bar        = df_bar.sort_values(user_col, ascending=True)
        pie_total     = df_bar[user_col].sum()
        df_bar["pct"] = (df_bar[user_col] / pie_total * 100).round(1)
        df_bar["label"] = df_bar.apply(
            lambda r: f"{int(r[user_col]):,} ({r['pct']}%)", axis=1
        )
        fig1 = px.bar(
            df_bar,
            x           = user_col,
            y           = seg_col,
            orientation = "h",
            color       = user_col,
            color_continuous_scale = "Blues",
            text        = "label",
            labels      = {user_col:"Users", seg_col:"Segment"},
            template    = "plotly_white",
        )
        fig1.update_traces(textposition="outside", cliponaxis=False)
        fig1.update_layout(
            height=400, showlegend=False,
            margin=dict(r=150),
            xaxis=dict(title="Number of Users"),
        )
        st.plotly_chart(fig1, width="stretch")

    with col2:
        st.subheader("💰 Revenue by Segment")
        if rev_col:
            df_rev = df_seg.sort_values(rev_col, ascending=True)
            fig2   = px.bar(
                df_rev, x=rev_col, y=seg_col, orientation="h",
                color=rev_col, color_continuous_scale="Blues",
                text=rev_col,
                labels={rev_col:"Revenue ($)", seg_col:"Segment"},
                template="plotly_white",
            )
            fig2.update_traces(
                texttemplate="$%{text:,.0f}",
                textposition="outside"
            )
            fig2.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig2, width="stretch")

    st.markdown("---")
    st.subheader("📋 Segment Insights")

    champ_row = df_seg[df_seg[seg_col].str.contains("Champion", case=False, na=False)]
    if not champ_row.empty and rev_col:
        c_users = int(champ_row[user_col].values[0])
        c_rev   = float(champ_row[rev_col].values[0])
        c_share = c_rev / total_rev * 100 if total_rev > 0 else 0
        st.success(
            f"👑 **Champions: {c_users:,} users — {c_share:.1f}% of total revenue.** "
            f"Most valuable customers. Protect and reward them."
        )

    needs_row = df_seg[df_seg[seg_col].str.contains("Needs", case=False, na=False)]
    if not needs_row.empty:
        n_users = int(needs_row[user_col].values[0])
        n_pct   = n_users / total_users * 100 if total_users > 0 else 0
        st.warning(
            f"⚠️ **Needs Attention: {n_users:,} users ({n_pct:.1f}% of buyers).** "
            f"Largest segment, low engagement — prime re-engagement opportunity."
        )

    st.dataframe(
        df_seg.sort_values(rev_col, ascending=False) if rev_col else df_seg,
    )

    st.markdown("---")
    st.subheader("🔽 Funnel Drop-off by Category")
    df_funnel_cat = load_csv("analysis_funnel_category.csv")
    if not df_funnel_cat.empty:
        cat_col = next((c for c in df_funnel_cat.columns
                        if "category" in c.lower()), None)
        v2c_col = next((c for c in df_funnel_cat.columns
                        if "view_to_cart" in c.lower()), None)
        c2p_col = next((c for c in df_funnel_cat.columns
                        if "cart_to_purchase" in c.lower()), None)
        if cat_col and v2c_col and c2p_col:
            fig3 = px.bar(
                df_funnel_cat.head(10), x=cat_col,
                y=[v2c_col, c2p_col], barmode="group",
                color_discrete_sequence=["#4361ee","#f72585"],
                template="plotly_white",
            )
            fig3.update_layout(height=380, xaxis_tickangle=-30)
            st.plotly_chart(fig3, width="stretch")
    else:
        st.info("Funnel category data not available.")
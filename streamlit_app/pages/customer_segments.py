# streamlit_app/pages/customer_segments.py

import streamlit as st
import plotly.express as px
import pandas as pd
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import run_query

EXPORT_DIR = r"C:\Users\yipch\ecommerce-analytics-portfolio\data\exports"

def show():
    st.title("👥 Customer Segments")
    st.markdown("RFM segmentation, conversion funnel, and buyer behaviour.")
    st.markdown("---")

    # ── Load RFM ──
    rfm_path = os.path.join(EXPORT_DIR, "analysis_rfm_segments.csv")
    df_seg   = pd.read_csv(rfm_path)

    # ── KPI row ──
    total_users  = df_seg["users"].sum()
    total_rev    = df_seg["total_revenue"].sum()
    top_seg      = df_seg.loc[df_seg["total_revenue"].idxmax(), "segment"]
    champ        = df_seg[df_seg["segment"].str.contains("Champions")]
    champ_rev    = champ["total_revenue"].sum() if not champ.empty else 0
    champ_share  = champ_rev / total_rev * 100 if total_rev > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total Buyers",      f"{total_users:,}")
    c2.metric("💰 Total Revenue",     f"${total_rev:,.0f}")
    c3.metric("🏆 Top Segment",       top_seg.split()[-1])
    c4.metric("👑 Champions Share",   f"{champ_share:.1f}%")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👥 Users by RFM Segment")
        fig1 = px.bar(
            df_seg.sort_values("users"),
            x="users", y="segment", orientation="h",
            color="total_revenue", color_continuous_scale="Blues",
            text="users",
            labels={"users":"Users","segment":"Segment"},
            template="plotly_white",
        )
        fig1.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig1.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("💰 Revenue by RFM Segment")
        fig2 = px.treemap(
            df_seg, path=["segment"], values="total_revenue",
            color="avg_monetary", color_continuous_scale="RdYlGn",
        )
        fig2.update_layout(height=420)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Segment Detail Table ──
    st.subheader("📋 Segment Detail")
    df_display = df_seg[[
        "segment","users","avg_recency",
        "avg_frequency","avg_monetary","total_revenue","revenue_share"
    ]].copy()
    df_display.columns = [
        "Segment","Users","Avg Recency (days)",
        "Avg Frequency","Avg Spend ($)","Total Revenue ($)","Revenue Share (%)"
    ]
    df_display = df_display.sort_values("Total Revenue ($)", ascending=False)
    st.dataframe(
        df_display.style.format({
            "Users"            : "{:,.0f}",
            "Avg Recency (days)": "{:.1f}",
            "Avg Frequency"    : "{:.2f}",
            "Avg Spend ($)"    : "${:.2f}",
            "Total Revenue ($)": "${:,.2f}",
            "Revenue Share (%)": "{:.1f}%",
        }).background_gradient(subset=["Total Revenue ($)"], cmap="Blues"),
        use_container_width=True,
    )

    st.markdown("---")

    # ── Funnel by Category ──
    st.subheader("🔽 Funnel Drop-off by Category")
    df_funnel_cat = run_query("""
        SELECT p.category_l1,
               SUM(CASE WHEN f.event_type='view'     THEN 1 ELSE 0 END) AS views,
               SUM(CASE WHEN f.event_type='cart'     THEN 1 ELSE 0 END) AS carts,
               SUM(CASE WHEN f.event_type='purchase' THEN 1 ELSE 0 END) AS purchases,
               ROUND(SUM(CASE WHEN f.event_type='cart' THEN 1 ELSE 0 END)*100.0 /
                     NULLIF(SUM(CASE WHEN f.event_type='view' THEN 1 ELSE 0 END),0),2)
                     AS view_to_cart_pct,
               ROUND(SUM(CASE WHEN f.event_type='purchase' THEN 1 ELSE 0 END)*100.0 /
                     NULLIF(SUM(CASE WHEN f.event_type='cart' THEN 1 ELSE 0 END),0),2)
                     AS cart_to_purchase_pct
        FROM fact_events f
        JOIN dim_products p ON f.product_id = p.product_id
        WHERE p.category_l1 != 'unknown'
        GROUP BY p.category_l1
        HAVING views >= 100
        ORDER BY cart_to_purchase_pct DESC
        LIMIT 10
    """)
    fig3 = px.bar(
        df_funnel_cat, x="category_l1",
        y=["view_to_cart_pct","cart_to_purchase_pct"],
        barmode="group",
        labels={"value":"Rate (%)","category_l1":"Category",
                "variable":"Stage"},
        color_discrete_sequence=["#4361ee","#f72585"],
        template="plotly_white",
    )
    fig3.update_layout(height=380, xaxis_tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)
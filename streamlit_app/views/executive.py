# streamlit_app/pages/executive.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import load_csv

def show():
    st.title("📊 Executive Overview")
    st.markdown("High-level business performance — revenue, orders, and traffic trends.")
    st.markdown("---")

    # ── Load data from CSVs ──
    df_monthly = load_csv("analysis_monthly.csv")
    df_funnel  = load_csv("analysis_funnel.csv")
    df_daily   = load_csv("analysis_daily.csv")
    df_hourly  = load_csv("analysis_hourly.csv")

    if df_monthly.empty:
        st.error("Data not found. Please check exports folder.")
        return

    # ── KPI Cards ──
    total_rev   = df_monthly["total_revenue"].sum()
    total_ord   = df_monthly["total_orders"].sum()
    avg_aov     = df_monthly["avg_order_value"].mean()
    total_users = df_monthly["unique_users"].sum()

    # Funnel metrics
    avg_conv = 0
    if not df_funnel.empty and "overall_conversion_rate" in df_funnel.columns:
        avg_conv = df_funnel["overall_conversion_rate"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💰 Total Revenue",   f"${total_rev:,.0f}")
    c2.metric("🛍️ Total Orders",    f"{total_ord:,.0f}")
    c3.metric("💳 Avg Order Value", f"${avg_aov:,.2f}")
    c4.metric("🎯 Conversion Rate", f"{avg_conv:.2f}%")
    c5.metric("👥 Unique Users",    f"{total_users:,.0f}")

    st.markdown("---")

    # ── Revenue + Orders Trend ──
    st.subheader("📈 Monthly Revenue & Orders")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(x=df_monthly["month"], y=df_monthly["total_revenue"],
               name="Revenue ($)", marker_color="#4361ee", opacity=0.85),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df_monthly["month"], y=df_monthly["total_orders"],
                   name="Orders", mode="lines+markers",
                   line=dict(color="#f72585", width=3), marker=dict(size=10)),
        secondary_y=True,
    )
    fig.update_layout(template="plotly_white", hovermode="x unified",
                      legend=dict(orientation="h", y=1.1), height=380)
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
    fig.update_yaxes(title_text="Total Orders", secondary_y=True)
    st.plotly_chart(fig, width='stretch')

    # ── Two columns ──
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔽 Conversion Funnel")
        df_f = load_csv("analysis_funnel.csv")
        if not df_f.empty and "event_type" in df_f.columns:
            order_map = {"view": 0, "cart": 1, "purchase": 2}
            df_f["order"] = df_f["event_type"].map(order_map)
            df_f = df_f.sort_values("order")
            fig2 = go.Figure(go.Funnel(
                y        = df_f["event_type"].str.capitalize(),
                x        = df_f["unique_users"],
                textinfo = "value+percent initial",
                marker   = dict(color=["#4361ee","#7209b7","#f72585"]),
            ))
            fig2.update_layout(height=350, template="plotly_white")
            st.plotly_chart(fig2, width='stretch')

    with col2:
        st.subheader("⏰ Hourly Purchase Pattern")
        if not df_hourly.empty and "hour" in df_hourly.columns:
            fig3 = px.bar(
                df_hourly, x="hour", y="purchases",
                color="purchases", color_continuous_scale="Blues",
                labels={"hour":"Hour of Day","purchases":"Purchases"},
                template="plotly_white",
            )
            fig3.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig3, width='stretch')

    # ── Revenue by Day of Week ──
    st.subheader("🗓️ Revenue by Day of Week")
    if not df_daily.empty and "day_of_week" in df_daily.columns:
        dow_order = ["Monday","Tuesday","Wednesday",
                     "Thursday","Friday","Saturday","Sunday"]
        dow_rev = (
            df_daily.groupby("day_of_week")["daily_revenue"]
            .sum().reindex(dow_order).reset_index()
        )
        fig4 = px.bar(
            dow_rev, x="day_of_week", y="daily_revenue",
            color="daily_revenue", color_continuous_scale="Blues",
            labels={"day_of_week":"Day","daily_revenue":"Revenue ($)"},
            template="plotly_white",
        )
        fig4.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig4, width='stretch')

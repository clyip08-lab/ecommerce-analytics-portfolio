# streamlit_app/pages/executive.py
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import run_query

def show():
    st.title("📊 Executive Overview")
    st.markdown("High-level business performance — revenue, orders, and traffic trends.")
    st.markdown("---")

    # ── Load data ──
    df_monthly = run_query("SELECT * FROM vw_monthly_revenue ORDER BY month")
    df_monthly["month"] = pd.to_datetime(df_monthly["month"])
    df_monthly = df_monthly.sort_values("month")
    df_funnel  = run_query("SELECT * FROM vw_conversion_funnel ORDER BY month")
    df_daily   = run_query("SELECT * FROM vw_daily_kpis ORDER BY full_date")

    # ── KPI Cards ──
    total_rev   = df_monthly["total_revenue"].sum()
    total_ord   = df_monthly["total_orders"].sum()
    avg_aov     = df_monthly["avg_order_value"].mean()
    avg_conv    = df_funnel["overall_conversion_rate"].mean()
    total_users = df_monthly["unique_users"].sum()

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
        go.Bar(x=df_monthly["month"].dt.strftime("%Y-%b"), y=df_monthly["total_revenue"],
               name="Revenue ($)", marker_color="#4361ee", opacity=0.85),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df_monthly["month"].dt.strftime("%Y-%b"), y=df_monthly["total_orders"],
                   name="Orders", mode="lines+markers",
                   line=dict(color="#f72585", width=3), marker=dict(size=10)),
        secondary_y=True,
    )
    fig.update_layout(
        template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", y=1.1), height=380,
    )
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
    fig.update_yaxes(title_text="Total Orders", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    # ── Two columns ──
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔽 Conversion Funnel")
        funnel_data = run_query("""
            SELECT
                event_type,
                COUNT(DISTINCT user_id) AS unique_users
            FROM fact_events
            GROUP BY event_type
            ORDER BY FIELD(event_type,'view','cart','purchase')
        """)
        fig2 = go.Figure(go.Funnel(
            y        = funnel_data["event_type"].str.capitalize(),
            x        = funnel_data["unique_users"],
            textinfo = "value+percent initial",
            marker   = dict(color=["#4361ee","#7209b7","#f72585"]),
        ))
        fig2.update_layout(height=350, template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("⏰ Hourly Purchase Pattern")
        df_hourly = run_query("""
            SELECT d.`hour`,
                   COUNT(*) AS total_events,
                   SUM(CASE WHEN f.event_type='purchase' THEN 1 ELSE 0 END) AS purchases
            FROM fact_events f
            JOIN dim_date d ON f.date_id = d.date_id
            GROUP BY d.`hour`
            ORDER BY d.`hour`
        """)
        fig3 = px.bar(
            df_hourly, x="hour", y="purchases",
            color="purchases", color_continuous_scale="Blues",
            labels={"hour":"Hour of Day","purchases":"Purchases"},
            template="plotly_white",
        )
        fig3.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    # ── Daily Revenue Heatmap ──
    st.subheader("🗓️ Revenue by Day of Week")
    df_daily["full_date"]  = df_daily["full_date"].astype(str)
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
    st.plotly_chart(fig4, use_container_width=True)
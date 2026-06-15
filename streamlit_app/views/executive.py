# streamlit_app/views/executive.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import load_csv

def show():
    st.title("Executive Overview")
    st.markdown(
        "High-level exploratory performance — observed purchase value, "
        "purchase events and activity trends within the analytical sample."
    )
    st.markdown("---")

    df_monthly = load_csv("analysis_monthly.csv")
    df_funnel  = load_csv("analysis_funnel.csv")
    df_daily   = load_csv("analysis_daily.csv")
    df_hourly  = load_csv("analysis_hourly.csv")

    if df_monthly.empty:
        st.error("Data not found. Please check exports folder.")
        return

    total_rev    = df_monthly["total_revenue"].sum()
    total_ord    = df_monthly["total_orders"].sum()
    avg_aov      = total_rev / total_ord if total_ord > 0 else 0
    latest_users = df_monthly.sort_values("month").iloc[-1]["unique_users"]

    avg_conv      = 0
    view_to_cart  = 0
    cart_to_purch = 0

    if not df_funnel.empty and "event_type" in df_funnel.columns:
        funnel_map = df_funnel.set_index("event_type")["unique_users"].to_dict()
        views      = funnel_map.get("view",     0)
        carts      = funnel_map.get("cart",     0)
        purchases  = funnel_map.get("purchase", 0)
        if views > 0:
            avg_conv     = (purchases / views) * 100
            view_to_cart = (carts     / views) * 100
        if carts > 0:
            cart_to_purch = (purchases / carts) * 100

    # KPI Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Observed Purchase Value",   f"${total_rev:,.0f}")
    c2.metric("Purchase Events",           f"{total_ord:,.0f}")
    c3.metric("Avg Purchase-Event Value",  f"${avg_aov:,.2f}")
    c4.metric("Buyer-to-Viewer Ratio",     f"{avg_conv:.2f}%")
    c5.metric("Observed Users (Latest Month)",            f"{latest_users:,.0f}")

    st.markdown("---")

    # Monthly trend
    st.subheader("Monthly Observed Purchase Value and Purchase Events")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=df_monthly["month"], y=df_monthly["total_revenue"],
            name="Observed Purchase Value ($)",
            marker_color="#4361ee", opacity=0.85,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df_monthly["month"], y=df_monthly["total_orders"],
            name="Purchase Events", mode="lines+markers",
            line=dict(color="#f72585", width=3), marker=dict(size=10),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", y=1.1), height=380,
    )
    fig.update_yaxes(title_text="Observed Purchase Value ($)", secondary_y=False)
    fig.update_yaxes(title_text="Purchase Events",             secondary_y=True)
    st.plotly_chart(fig, width="stretch")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Stage Participation")
        st.warning(
            "Directional monthly stage-participation view. "
            "Does not enforce same-session, same-product or "
            "time-ordered journey."
        )
        if not df_funnel.empty and "event_type" in df_funnel.columns:
            df_f = df_funnel.copy()
            df_f["order"] = df_f["event_type"].map(
                {"view": 0, "cart": 1, "purchase": 2}
            )
            df_f = df_f.sort_values("order")
            df_f["stage"] = df_f["event_type"].str.capitalize()
            df_f = df_f.sort_values("order", ascending=False)

            fig2 = px.bar(
                df_f,
                x="unique_users",
                y="stage",
                orientation="h",
                text="unique_users",
                labels={
                    "unique_users": "Distinct Users",
                    "stage": "Observed Stage",
                },
                template="plotly_white",
            )

            fig2.update_traces(
                texttemplate="%{text:,.0f}",
                textposition="outside",
            )

            fig2.update_layout(
                height=350,
                showlegend=False,
            )

            st.plotly_chart(fig2, width="stretch")

    with col2:
        st.subheader("Hourly Purchase-Event Pattern (UTC)")
        if not df_hourly.empty and "hour" in df_hourly.columns:
            fig3 = px.bar(
                df_hourly, x="hour", y="purchases",
                color="purchases", color_continuous_scale="Blues",
                labels={"hour":"Hour of Day (UTC)","purchases":"Purchase Events"},
                template="plotly_white",
            )
            fig3.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig3, width="stretch")

    st.markdown("---")

    # Stage participation ratios
    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("Cart-to-Viewer Ratio",   f"{view_to_cart:.2f}%")
    fc2.metric("Buyer-to-Carter Ratio",  f"{cart_to_purch:.2f}%")
    fc3.metric(
        "Buyer-to-Viewer Ratio",
        f"{avg_conv:.2f}%",
        help=(
            "Monthly distinct buyers divided by monthly distinct viewers. "
            "Not a sequential conversion rate."
        )
    )
    st.caption(
        "These ratios compare monthly distinct-user counts at each stage. "
        "A same-session, time-ordered funnel is required to confirm "
        "sequential conversion rates."
    )

    st.markdown("---")

    # Day of week
    st.subheader("Observed Purchase Value by Day of Week")
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
            labels={"day_of_week":"Day",
                    "daily_revenue":"Observed Purchase Value ($)"},
            template="plotly_white",
        )
        fig4.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig4, width="stretch")

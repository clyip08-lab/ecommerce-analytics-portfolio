# streamlit_app/pages/retention_cohort.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import run_query

EXPORT_DIR = r"C:\Users\yipch\ecommerce-analytics-portfolio\data\exports"

def show():
    st.title("🔄 Retention & Cohort Analysis")
    st.markdown("User retention, repeat purchase behaviour, and cohort tracking.")
    st.markdown("---")

    # ── Retention Segments ──
    df_ret = run_query("""
        SELECT retention_segment,
               COUNT(*) AS users
        FROM vw_user_retention
        GROUP BY retention_segment
        ORDER BY users DESC
    """)

    total = df_ret["users"].sum()
    st.subheader("👥 Retention Segment Breakdown")

    cols = st.columns(len(df_ret))
    colors = ["#4361ee","#7209b7","#f72585","#4cc9f0"]
    for i, (_, row) in enumerate(df_ret.iterrows()):
        pct = row["users"] / total * 100
        cols[i].metric(
            row["retention_segment"],
            f"{row['users']:,}",
            f"{pct:.1f}% of users"
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🍩 Retention Segments")
        fig1 = px.pie(
            df_ret, names="retention_segment", values="users",
            hole=0.45, color_discrete_sequence=colors,
        )
        fig1.update_layout(height=380, template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("📈 Monthly Conversion Rates")
        df_conv = run_query(
            "SELECT * FROM vw_conversion_funnel ORDER BY month"
        )
        fig2 = px.line(
            df_conv, x="month",
            y=["view_to_cart_rate","cart_to_purchase_rate","overall_conversion_rate"],
            markers=True,
            labels={"value":"Rate (%)","month":"Month","variable":"Stage"},
            color_discrete_sequence=["#4361ee","#7209b7","#f72585"],
            template="plotly_white",
        )
        fig2.update_layout(height=380, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Cohort Heatmap ──
    st.subheader("🔥 Cohort Retention Heatmap")
    cohort_path = os.path.join(EXPORT_DIR, "analysis_cohort_long.csv")

    if os.path.exists(cohort_path):
        df_cohort = pd.read_csv(cohort_path)
        pivot = df_cohort.pivot_table(
            index   = "cohort_month",
            columns = "period_label",
            values  = "retention_pct",
            aggfunc = "mean",
        )
        # Sort columns naturally
        cols_sorted = sorted(
            pivot.columns,
            key=lambda x: int(x.split()[-1])
        )
        pivot = pivot[cols_sorted]

        fig3 = go.Figure(go.Heatmap(
            z            = pivot.values,
            x            = pivot.columns.tolist(),
            y            = pivot.index.tolist(),
            colorscale   = "Blues",
            text         = pivot.values.round(1),
            texttemplate = "%{text}%",
            showscale    = True,
        ))
        fig3.update_layout(
            height   = 350,
            template = "plotly_white",
            xaxis    = dict(title="Period"),
            yaxis    = dict(title="Cohort"),
        )
        st.plotly_chart(fig3, use_container_width=True)

        # Key insight box
        m1_avg = df_cohort[df_cohort["period_label"]=="Month 1"]["retention_pct"].mean()
        st.info(
            f"📌 **Key Insight:** Average Month-1 retention is **{m1_avg:.2f}%**. "
            f"Most users do not return after their first purchase — "
            f"suggesting opportunity for post-purchase email campaigns and loyalty programs."
        )
    else:
        st.warning("⚠️ Run the cohort fix in Jupyter first to generate `analysis_cohort_long.csv`")

    st.markdown("---")

    # ── Session Behaviour ──
    st.subheader("⚖️ Converted vs Non-Converted Sessions")
    df_sess = run_query("""
        SELECT
            CASE WHEN session_converted=1
                 THEN 'Converted' ELSE 'Not Converted' END AS session_type,
            ROUND(AVG(session_event_count),2)  AS avg_events,
            ROUND(AVG(session_duration_min),2) AS avg_duration_min,
            ROUND(AVG(unique_products),2)      AS avg_products,
            COUNT(*)                           AS sessions
        FROM dim_sessions
        GROUP BY session_converted
    """)
    st.dataframe(
        df_sess.style.format({
            "avg_events"       : "{:.2f}",
            "avg_duration_min" : "{:.2f} min",
            "avg_products"     : "{:.2f}",
            "sessions"         : "{:,}",
        }).background_gradient(cmap="Blues"),
        use_container_width=True,
    )
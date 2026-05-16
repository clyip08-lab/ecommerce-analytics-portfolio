# streamlit_app/pages/product_brand.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import run_query

def show():
    st.title("📦 Product & Brand Performance")
    st.markdown("Revenue, conversion, and pricing insights by product and brand.")
    st.markdown("---")

    # ── Filters ──
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        top_n = st.slider("Show Top N Brands", 5, 20, 10)
    with col_f2:
        month_filter = st.selectbox("Month", ["All","2019-Oct","2019-Nov"])

    month_clause = ""
    if month_filter != "All":
        month_clause = f"WHERE f.month = '{month_filter}'"

    # ── Top Brands ──
    df_brands = run_query(f"""
        SELECT p.brand,
               ROUND(SUM(f.revenue),2)  AS total_revenue,
               SUM(CASE WHEN f.event_type='purchase' THEN 1 ELSE 0 END) AS purchases,
               ROUND(AVG(CASE WHEN f.event_type='purchase'
                          THEN f.price END),2) AS avg_price,
               ROUND(SUM(CASE WHEN f.event_type='purchase'
                          THEN 1 ELSE 0 END)*100.0 /
                     NULLIF(SUM(CASE WHEN f.event_type='view'
                          THEN 1 ELSE 0 END),0),2) AS conv_rate
        FROM fact_events f
        JOIN dim_products p ON f.product_id = p.product_id
        {month_clause}
        GROUP BY p.brand
        HAVING p.brand != 'unknown' AND total_revenue > 0
        ORDER BY total_revenue DESC
        LIMIT {top_n}
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"🏷️ Top {top_n} Brands by Revenue")
        fig1 = px.bar(
            df_brands.sort_values("total_revenue"),
            x="total_revenue", y="brand", orientation="h",
            color="total_revenue", color_continuous_scale="Blues",
            text="total_revenue",
            labels={"total_revenue":"Revenue ($)","brand":"Brand"},
            template="plotly_white",
        )
        fig1.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig1.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader(f"🎯 Brand Conversion Rates (%)")
        fig2 = px.bar(
            df_brands.sort_values("conv_rate"),
            x="conv_rate", y="brand", orientation="h",
            color="conv_rate", color_continuous_scale="Purples",
            text="conv_rate",
            labels={"conv_rate":"Conversion Rate (%)","brand":"Brand"},
            template="plotly_white",
        )
        fig2.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig2.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── Category Treemap ──
    st.subheader("🗂️ Revenue by Category")
    df_cat = run_query("""
        SELECT category_l1,
               SUM(total_revenue) AS total_revenue,
               SUM(purchases)     AS purchases
        FROM vw_product_performance
        WHERE category_l1 != 'unknown'
        GROUP BY category_l1
        ORDER BY total_revenue DESC
    """)
    fig3 = px.treemap(
        df_cat, path=["category_l1"], values="total_revenue",
        color="total_revenue", color_continuous_scale="Blues",
        title="Revenue share by product category",
    )
    fig3.update_layout(height=400, template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── Pareto Chart ──
    st.subheader("📊 Pareto 80/20 — Product Revenue")
    df_pareto = run_query("""
        SELECT product_id, brand, category_l1,
               purchases,
               ROUND(total_revenue,2) AS total_revenue
        FROM vw_product_performance
        WHERE purchases >= 1
        ORDER BY total_revenue DESC
        LIMIT 200
    """)
    df_pareto["cum_pct"] = (
        df_pareto["total_revenue"].cumsum() /
        df_pareto["total_revenue"].sum() * 100
    ).round(2)
    df_pareto["rank"] = range(1, len(df_pareto)+1)

    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    fig4.add_trace(
        go.Bar(x=df_pareto["rank"], y=df_pareto["total_revenue"],
               name="Revenue", marker_color="#4361ee", opacity=0.6),
        secondary_y=False,
    )
    fig4.add_trace(
        go.Scatter(x=df_pareto["rank"], y=df_pareto["cum_pct"],
                   name="Cumulative %", mode="lines",
                   line=dict(color="#f72585", width=2)),
        secondary_y=True,
    )
    fig4.add_hline(y=80, line_dash="dash", line_color="red",
                   secondary_y=True, annotation_text="80%")
    fig4.update_layout(height=380, template="plotly_white",
                       hovermode="x unified")
    fig4.update_yaxes(title_text="Revenue ($)", secondary_y=False)
    fig4.update_yaxes(title_text="Cumulative %", secondary_y=True)
    st.plotly_chart(fig4, use_container_width=True)
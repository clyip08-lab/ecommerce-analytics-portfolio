# streamlit_app/pages/product_brand.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import load_csv

def show():
    st.title("📦 Product & Brand Performance")
    st.markdown("Revenue, conversion, and pricing insights by product and brand.")
    st.markdown("---")

    # ── Load CSVs ──
    df_brands = load_csv("analysis_brands.csv")
    df_cat    = load_csv("analysis_categories.csv")
    df_pareto = load_csv("analysis_pareto.csv")

    # ── Debug: show columns if data loaded ──
    if df_brands.empty:
        st.error("❌ analysis_brands.csv not found in exports folder.")
        return

    # ── Filters ──
    top_n = st.slider("Show Top N Brands", 5, 20, 10)
    month_options = ["All"]
    if "month" in df_brands.columns:
        month_options += df_brands["month"].dropna().unique().tolist()
    month_filter = st.selectbox("Month", month_options)

    # Filter by month if column exists
    df_b = df_brands.copy()
    if month_filter != "All" and "month" in df_b.columns:
        df_b = df_b[df_b["month"] == month_filter]

    # Find revenue column (handle different names)
    rev_col = next((c for c in df_b.columns
                    if "revenue" in c.lower()), None)
    conv_col = next((c for c in df_b.columns
                     if "conv" in c.lower() or "rate" in c.lower()), None)
    brand_col = next((c for c in df_b.columns
                      if "brand" in c.lower()), None)

    if not rev_col or not brand_col:
        st.warning(f"⚠️ Expected columns not found. Available: {list(df_b.columns)}")
        st.dataframe(df_b.head())
        return

    df_b = df_b.dropna(subset=[rev_col])
    df_b = df_b[df_b[brand_col] != "unknown"]
    df_top = df_b.nlargest(top_n, rev_col)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"🏷️ Top {top_n} Brands by Revenue")
        fig1 = px.bar(
            df_top.sort_values(rev_col),
            x=rev_col, y=brand_col, orientation="h",
            color=rev_col, color_continuous_scale="Blues",
            text=rev_col,
            labels={rev_col:"Revenue ($)", brand_col:"Brand"},
            template="plotly_white",
        )
        fig1.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig1.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig1, width='stretch')

    with col2:
        st.subheader("🎯 Brand Conversion Rates (%)")
        if conv_col:
            fig2 = px.bar(
                df_top.sort_values(conv_col),
                x=conv_col, y=brand_col, orientation="h",
                color=conv_col, color_continuous_scale="Purples",
                text=conv_col,
                labels={conv_col:"Conversion Rate (%)", brand_col:"Brand"},
                template="plotly_white",
            )
            fig2.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig2.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig2, width='stretch')
        else:
            st.info("Conversion rate column not found in brands CSV.")

    st.markdown("---")

    # ── Category Treemap ──
    st.subheader("🗂️ Revenue by Category")
    if not df_cat.empty:
        cat_rev_col  = next((c for c in df_cat.columns if "revenue" in c.lower()), None)
        cat_name_col = next((c for c in df_cat.columns if "category" in c.lower()), None)

        if cat_rev_col and cat_name_col:
            df_cat2 = df_cat[df_cat[cat_name_col] != "unknown"].dropna(subset=[cat_rev_col])
            fig3 = px.treemap(
                df_cat2, path=[cat_name_col], values=cat_rev_col,
                color=cat_rev_col, color_continuous_scale="Blues",
            )
            fig3.update_layout(height=400, template="plotly_white")
            st.plotly_chart(fig3, width='stretch')

    st.markdown("---")

    # ── Pareto Chart ──
    st.subheader("📊 Pareto 80/20 — Product Revenue")
    if not df_pareto.empty:
        rev_col_p = next((c for c in df_pareto.columns if "revenue" in c.lower()), None)
        if rev_col_p:
            df_pareto = df_pareto.sort_values(rev_col_p, ascending=False).reset_index(drop=True)
            df_pareto["rank"]    = range(1, len(df_pareto)+1)
            df_pareto["cum_pct"] = (
                df_pareto[rev_col_p].cumsum() /
                df_pareto[rev_col_p].sum() * 100
            ).round(2)

            n80 = len(df_pareto[df_pareto["cum_pct"] <= 80])

            fig4 = make_subplots(specs=[[{"secondary_y": True}]])
            fig4.add_trace(
                go.Bar(x=df_pareto["rank"], y=df_pareto[rev_col_p],
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
            fig4.add_vline(x=n80, line_dash="dash", line_color="orange",
                           annotation_text=f"Top {n80} products")
            fig4.update_layout(height=380, template="plotly_white",
                               hovermode="x unified")
            fig4.update_yaxes(title_text="Revenue ($)", secondary_y=False)
            fig4.update_yaxes(title_text="Cumulative %", secondary_y=True)
            st.plotly_chart(fig4, width='stretch')

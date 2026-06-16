# streamlit_app/views/product_brand.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import load_csv

def show():
    st.title("Product and Brand Performance")
    st.markdown(
        "Observed purchase value and directional product-performance "
        "insights within the analytical sample."
    )
    st.markdown("---")

    df_brands = load_csv("analysis_brands.csv")
    df_cat    = load_csv("analysis_categories.csv")
    df_pareto = load_csv("analysis_pareto.csv")

    if df_brands.empty:
        st.error("analysis_brands.csv not found.")
        return

    top_n = st.slider("Show Top N Brands", 5, 20, 10)
    df_b = df_brands.copy()

    if "month" in df_b.columns:
        month_options = sorted(
            df_b["month"]
            .dropna()
            .unique()
            .tolist()
        )

        if month_options:
            month_filter = st.selectbox(
                "Month",
                month_options,
                index=len(month_options) - 1,
            )

            df_b = df_b[
                df_b["month"] == month_filter
            ].copy()

            st.caption(
                "Brand comparisons are shown within one "
                "selected month to avoid mixing separate "
                "monthly brand records."
            )

    rev_col   = next((c for c in df_b.columns if "revenue"    in c.lower()), None)
    conv_col  = next((c for c in df_b.columns if "conv"       in c.lower() or "rate" in c.lower()), None)
    brand_col = next((c for c in df_b.columns if "brand"      in c.lower()), None)

    if not rev_col or not brand_col:
        st.warning(f"Expected columns not found. Available: {list(df_b.columns)}")
        return

    df_b   = df_b.dropna(subset=[rev_col])
    df_b   = df_b[df_b[brand_col] != "unknown"]
    df_top = df_b.nlargest(top_n, rev_col)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Top {top_n} Brands by Observed Purchase Value")
        fig1 = px.bar(
            df_top.sort_values(rev_col),
            x=rev_col, y=brand_col, orientation="h",
            color=rev_col, color_continuous_scale="Blues",
            text=rev_col,
            labels={rev_col:"Observed Purchase Value ($)", brand_col:"Brand"},
            template="plotly_white",
        )
        fig1.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig1.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig1, width="stretch")

    with col2:
        st.subheader("Purchase-Event-to-View-Event Ratio by Brand")
        if conv_col:
            fig2 = px.bar(
                df_top.sort_values(conv_col),
                x=conv_col, y=brand_col, orientation="h",
                color=conv_col, color_continuous_scale="Purples",
                text=conv_col,
                labels={conv_col:"Purchase Events / View Events (%)", brand_col:"Brand"},
                template="plotly_white",
            )
            fig2.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig2.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig2, width="stretch")
            st.caption(
                "Purchase-event rows divided by view-event rows "
                "per brand. This is a directional event ratio, not a distinct-user or sequential conversion rate."
            )

    st.markdown("---")

    # Category treemap
    st.subheader("Observed Purchase Value by Category")
    if not df_cat.empty:
        cat_rev_col  = next((c for c in df_cat.columns if "revenue"  in c.lower()), None)
        cat_name_col = next((c for c in df_cat.columns if "category" in c.lower()), None)
        if cat_rev_col and cat_name_col:
            df_cat2 = df_cat[df_cat[cat_name_col] != "unknown"].dropna(subset=[cat_rev_col])
            fig3 = px.treemap(
                df_cat2, path=[cat_name_col], values=cat_rev_col,
                color=cat_rev_col, color_continuous_scale="Blues",
                labels={cat_rev_col:"Observed Purchase Value ($)"},
            )
            fig3.update_layout(height=400, template="plotly_white")
            st.plotly_chart(fig3, width="stretch")

    st.markdown("---")

    # Pareto
    st.subheader("Pareto Analysis — Observed Purchase Value Concentration")
    if not df_pareto.empty:
        rev_col_p = next((c for c in df_pareto.columns if "revenue" in c.lower()), None)
        if rev_col_p:
            df_all = (
                df_pareto
                .sort_values(rev_col_p, ascending=False)
                .reset_index(drop=True)
            )
            df_all["rank"]    = range(1, len(df_all) + 1)
            df_all["cum_pct"] = (
                df_all[rev_col_p].cumsum() /
                df_all[rev_col_p].sum() * 100
            ).round(2)

            n80    = int((df_all["cum_pct"] <= 80).sum()) + 1
            pct_80 = round(n80 / len(df_all) * 100, 1)
            show_n = min(int(n80 * 1.3) + 10, len(df_all))
            df_p   = df_all.head(show_n).copy()

            st.info(
                f"Top {n80} products ({pct_80}% of products with observed "
                f"purchases in the analytical sample) account for 80% of "
                f"observed purchase value."
            )

            fig4 = make_subplots(specs=[[{"secondary_y": True}]])
            fig4.add_trace(
                go.Bar(
                    x=df_p["rank"], y=df_p[rev_col_p],
                    name="Observed Purchase Value ($)",
                    marker_color="#4361ee", opacity=0.7,
                ),
                secondary_y=False,
            )
            fig4.add_trace(
                go.Scatter(
                    x=df_p["rank"], y=df_p["cum_pct"],
                    name="Cumulative %", mode="lines",
                    line=dict(color="#f72585", width=2.5),
                ),
                secondary_y=True,
            )
            fig4.add_hline(
                y=80, line_dash="dash", line_color="red",
                secondary_y=True,
                annotation_text="80% of observed purchase value",
            )
            fig4.add_vline(
                x=n80, line_dash="dash", line_color="orange",
                annotation_text=f"Rank {n80}",
            )
            fig4.update_layout(
                height=420, template="plotly_white",
                hovermode="x unified",
                xaxis=dict(title="Product Rank (by Observed Purchase Value)"),
                legend=dict(orientation="h", y=1.1),
            )
            fig4.update_yaxes(title_text="Observed Purchase Value ($)", secondary_y=False)
            fig4.update_yaxes(title_text="Cumulative %", range=[0,105],  secondary_y=True)
            st.plotly_chart(fig4, width="stretch")

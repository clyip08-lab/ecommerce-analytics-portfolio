# streamlit_app/pages/customer_segments.py

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
        st.subheader("🍩 Segment Distribution")
        if user_col in df_seg.columns:
            df_pie = df_seg[df_seg[user_col] > 0].copy()
            df_pie = df_pie.sort_values(user_col, ascending=False).reset_index(drop=True)

            pie_total      = df_pie[user_col].sum()
            df_pie["pct"]  = (df_pie[user_col] / pie_total * 100).round(1)
            df_large       = df_pie[df_pie["pct"] >= 2].copy()
            df_small       = df_pie[df_pie["pct"] <  2].copy()

            fig1 = px.pie(
                df_pie,
                names  = seg_col,
                values = user_col,
                hole   = 0.45,
                color_discrete_sequence = [
                    "#4361ee","#7209b7","#f72585",
                    "#4cc9f0","#3a0ca3","#560bad","#480ca8"
                ],
            )

            # ✅ Build custom text — empty string for small segments
            custom_text = []
            for _, row in df_pie.iterrows():
                if row["pct"] >= 2:
                    custom_text.append(f"{row['pct']}%")
                else:
                    custom_text.append("")

            fig1.update_traces(
                text             = custom_text,
                textinfo         = "text",
                textposition     = "inside",
                insidetextanchor = "middle",
                hovertemplate    = (
                    "<b>%{label}</b><br>"
                    "Users: %{value:,}<br>"
                    "Share: %{percent:.1%}"
                    "<extra></extra>"
                ),
            )
            fig1.update_layout(
                height     = 400,
                template   = "plotly_white",
                showlegend = True,
                legend     = dict(orientation="v", x=1.0, y=0.5),
                margin     = dict(t=10, b=10, l=10, r=150),
            )
            st.plotly_chart(fig1, width="stretch")

            # ✅ Small segments shown as metric cards below chart
            if not df_small.empty:
                st.caption("**Smaller segments (< 2% of buyers):**")
                small_cols = st.columns(len(df_small))
                for i, (_, row) in enumerate(df_small.iterrows()):
                    # Clean emoji from label for metric title
                    clean_label = str(row[seg_col])
                    for emoji in ["😴","⚠️","💛","🏆","😐","🆕","💀","🌱","👑"]:
                        clean_label = clean_label.replace(emoji, "").strip()
                    small_cols[i].metric(
                        label = clean_label,
                        value = f"{int(row[user_col]):,}",
                        delta = f"{row['pct']}% of buyers",
                        delta_color = "off",
                    )
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
    st.subheader("📋 Segment Detail")

    # ✅ Highlight champions insight
    champ_row = df_seg[df_seg[seg_col].str.contains("Champion", case=False, na=False)]
    if not champ_row.empty and rev_col:
        c_users = int(champ_row[user_col].values[0]) if user_col else 0
        c_rev   = float(champ_row[rev_col].values[0])
        c_share = c_rev / total_rev * 100 if total_rev > 0 else 0
        st.success(
            f"👑 **Champions: {c_users:,} users ({c_share:.1f}% of revenue)** "
            f"— your most valuable customers. Protect and reward them."
        )

    needs_row = df_seg[df_seg[seg_col].str.contains("Needs", case=False, na=False)]
    if not needs_row.empty and user_col:
        n_users = int(needs_row[user_col].values[0])
        n_pct = n_users / total_users * 100 if total_users > 0 else 0
        st.warning(
            f"⚠️ **Needs Attention: {n_users:,} users ({n_pct:.1f}%)** "
            f"— largest segment but low engagement. Re-engagement campaign opportunity."
        )

    st.dataframe(
        df_seg.sort_values(rev_col, ascending=False) if rev_col else df_seg,
        use_container_width=False,
    )

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

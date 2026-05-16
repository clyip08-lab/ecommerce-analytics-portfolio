# streamlit_app/pages/retention_cohort.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import load_csv

def show():
    st.title("🔄 Retention & Cohort Analysis")
    st.markdown("User retention, repeat purchase behaviour, and cohort tracking.")
    st.markdown("---")

    # ── Load retention segments ──
    df_seg = load_csv("analysis_rfm_segments.csv")

    if not df_seg.empty:
        # Find segment column dynamically
        seg_col  = next((c for c in df_seg.columns
                         if "segment" in c.lower()), df_seg.columns[0])
        user_col = next((c for c in df_seg.columns
                         if "user" in c.lower()), None)
        rev_col  = next((c for c in df_seg.columns
                         if "revenue" in c.lower()), None)

        total = df_seg[user_col].sum() if user_col else 0

        st.subheader("👥 Retention Segment Breakdown")
        cols = st.columns(min(len(df_seg), 4))
        colors = ["#4361ee","#7209b7","#f72585","#4cc9f0",
                  "#3a0ca3","#560bad","#480ca8","#b5179e"]

        for i, (_, row) in enumerate(df_seg.iterrows()):
            if i >= len(cols):
                break
            users = row[user_col] if user_col else 0
            pct   = users / total * 100 if total > 0 else 0
            label = str(row[seg_col]).split()[-1]
            cols[i].metric(label, f"{users:,.0f}", f"{pct:.1f}%")

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🍩 Segment Distribution")
            if user_col:
                fig1 = px.pie(
                    df_seg,
                    names  = seg_col,
                    values = user_col,
                    hole   = 0.45,
                    color_discrete_sequence = colors,
                )
                fig1.update_layout(height=380, template="plotly_white")
                st.plotly_chart(fig1, width='stretch')

        with col2:
            st.subheader("💰 Revenue by Segment")
            if rev_col:
                fig2 = px.bar(
                    df_seg.sort_values(rev_col, ascending=True),
                    x           = rev_col,
                    y           = seg_col,
                    orientation = "h",
                    color       = rev_col,
                    color_continuous_scale = "Blues",
                    text        = rev_col,
                    template    = "plotly_white",
                )
                fig2.update_traces(
                    texttemplate = "$%{text:,.0f}",
                    textposition = "outside"
                )
                fig2.update_layout(height=380, showlegend=False)
                st.plotly_chart(fig2, width='stretch')

    st.markdown("---")

    # ── Conversion funnel trend ──
    st.subheader("📈 Monthly Conversion Rates")
    df_conv = load_csv("analysis_funnel.csv")

    if not df_conv.empty:
        # Check if it has monthly breakdown
        month_col = next((c for c in df_conv.columns
                          if "month" in c.lower()), None)
        rate_cols = [c for c in df_conv.columns
                     if "rate" in c.lower() or "pct" in c.lower()]

        if month_col and rate_cols:
            fig3 = px.line(
                df_conv,
                x       = month_col,
                y       = rate_cols,
                markers = True,
                color_discrete_sequence = ["#4361ee","#7209b7","#f72585"],
                template = "plotly_white",
                labels   = {"value":"Rate (%)","variable":"Stage"},
            )
            fig3.update_layout(height=350,
                               legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig3, width='stretch')
        else:
            # Show as bar chart if no monthly breakdown
            val_col = next((c for c in df_conv.columns
                            if "user" in c.lower()), df_conv.columns[-1])
            name_col = df_conv.columns[0]
            fig3 = px.funnel(
                df_conv,
                y = name_col,
                x = val_col,
                color_discrete_sequence = ["#4361ee","#7209b7","#f72585"],
            )
            fig3.update_layout(height=350, template="plotly_white")
            st.plotly_chart(fig3, width='stretch')

    st.markdown("---")

    # ── Cohort Heatmap ──
    st.subheader("🔥 Cohort Retention Heatmap")
    df_cohort = load_csv("analysis_cohort_long.csv")

    if not df_cohort.empty:
        cohort_col  = next((c for c in df_cohort.columns
                            if "cohort" in c.lower()), df_cohort.columns[0])
        period_col  = next((c for c in df_cohort.columns
                            if "label" in c.lower() or "period" in c.lower()), None)
        ret_col     = next((c for c in df_cohort.columns
                            if "retention" in c.lower() or "pct" in c.lower()), None)

        if period_col and ret_col:
            pivot = df_cohort.pivot_table(
                index   = cohort_col,
                columns = period_col,
                values  = ret_col,
                aggfunc = "mean",
            )
            try:
                cols_sorted = sorted(
                    pivot.columns,
                    key=lambda x: int(str(x).split()[-1])
                )
                pivot = pivot[cols_sorted]
            except Exception:
                pass

            fig4 = go.Figure(go.Heatmap(
                z            = pivot.values,
                x            = pivot.columns.tolist(),
                y            = pivot.index.tolist(),
                colorscale   = "Blues",
                text         = pivot.round(1).values,
                texttemplate = "%{text}%",
                showscale    = True,
            ))
            fig4.update_layout(
                height   = 350,
                template = "plotly_white",
                xaxis    = dict(title="Period"),
                yaxis    = dict(title="Cohort"),
            )
            st.plotly_chart(fig4, width='stretch')

            m1_col = "Month 1"
            if m1_col in df_cohort.get(period_col, pd.Series()).values:
                m1_avg = df_cohort[
                    df_cohort[period_col] == m1_col
                ][ret_col].mean()
                st.info(
                    f"📌 **Key Insight:** Average Month-1 retention is "
                    f"**{m1_avg:.2f}%**. Most users don't return after first "
                    f"purchase — opportunity for post-purchase email campaigns."
                )
    else:
        st.info("Cohort data not available.")

    st.markdown("---")

    # ── Session comparison ──
    st.subheader("⚖️ Session Behaviour Summary")
    df_sess = load_csv("dim_sessions.csv")

    if not df_sess.empty and "session_converted" in df_sess.columns:
        summary = (
            df_sess.groupby("session_converted")
            .agg(
                sessions          = ("session_converted",    "count"),
                avg_events        = ("session_event_count",  "mean"),
                avg_duration_min  = ("session_duration_min", "mean"),
                avg_products      = ("unique_products",       "mean"),
            )
            .reset_index()
        )
        summary["session_type"] = summary["session_converted"].map(
            {1: "✅ Converted", 0: "❌ Not Converted"}
        )
        summary = summary.round(2)
        st.dataframe(
            summary[["session_type","sessions",
                      "avg_events","avg_duration_min","avg_products"]],
            width='stretch'
        )
    else:
        st.info("Session data not available on cloud deployment.")

# streamlit_app/views/retention_cohort.py

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from db import load_csv

def show():
    st.title("Retention and Cohort Analysis")
    st.markdown("User retention, repeat purchase behaviour, and cohort tracking.")
    st.markdown("---")

    df_seg = load_csv("analysis_rfm_segments.csv")

    if not df_seg.empty:
        seg_col  = next((c for c in df_seg.columns if "segment" in c.lower()), df_seg.columns[0])
        user_col = next((c for c in df_seg.columns
                         if "user" in c.lower() and "id" not in c.lower()), None)
        rev_col  = next((c for c in df_seg.columns if "revenue" in c.lower()), None)

        total = df_seg[user_col].sum() if user_col else 1

        st.subheader("Retention Segment Breakdown")
        num_cols = min(len(df_seg), 4)
        cols = st.columns(num_cols)
        for i, (_, row) in enumerate(df_seg.iterrows()):
            if i >= num_cols:
                break
            users = row[user_col] if user_col else 0
            pct   = users / total * 100 if total > 0 else 0
            label = str(row[seg_col]).split()[-1]
            cols[i].metric(label, f"{users:,.0f}", f"{pct:.1f}%")

        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Segment Distribution")
            if user_col:
                df_pie        = df_seg[df_seg[user_col] > 0].copy()
                pie_total     = df_pie[user_col].sum()
                df_pie["pct"] = (df_pie[user_col] / pie_total * 100).round(1)
                df_large      = df_pie[df_pie["pct"] >= 2].reset_index(drop=True)
                df_small      = df_pie[df_pie["pct"] <  2].reset_index(drop=True)

                fig1 = px.pie(
                    df_large,
                    names  = seg_col,
                    values = user_col,
                    hole   = 0.45,
                    color_discrete_sequence = ["#4361ee","#7209b7","#f72585","#4cc9f0"],
                )
                fig1.update_traces(
                    texttemplate  = "%{percent:.1%}",
                    textposition  = "inside",
                    hovertemplate = "<b>%{label}</b><br>Users: %{value:,}<br>%{percent:.1%}<extra></extra>",
                )
                fig1.update_layout(
                    height=380, template="plotly_white",
                    showlegend=True,
                    legend=dict(orientation="v", x=1.0, y=0.5),
                    margin=dict(t=10, b=10, l=10, r=150),
                )
                st.plotly_chart(fig1, width="stretch")

                if not df_small.empty:
                    st.caption("Smaller segments (< 2%):")
                    scols = st.columns(len(df_small))
                    for i, (_, row) in enumerate(df_small.iterrows()):
                        name = str(row[seg_col])
                        for e in ["😴","⚠️","💛","🏆","😐","🆕","💀","🌱","👑","🎯"]:
                            name = name.replace(e, "").strip()
                        scols[i].metric(name, f"{int(row[user_col]):,}", f"{row['pct']}%", delta_color="off")

        with col2:
            st.subheader("Monthly Conversion Rates")
            df_conv = load_csv("analysis_funnel.csv")
            if not df_conv.empty:
                month_col = next((c for c in df_conv.columns if "month" in c.lower()), None)
                rate_cols = [c for c in df_conv.columns if "rate" in c.lower() or "pct" in c.lower()]
                if month_col and rate_cols:
                    fig2 = px.line(
                        df_conv, x=month_col, y=rate_cols,
                        markers=True,
                        color_discrete_sequence=["#4361ee","#7209b7","#f72585"],
                        template="plotly_white",
                    )
                    fig2.update_layout(height=380, legend=dict(orientation="h", y=-0.2))
                    st.plotly_chart(fig2, width="stretch")
                else:
                    val_col  = next((c for c in df_conv.columns if "user" in c.lower()), df_conv.columns[-1])
                    name_col = df_conv.columns[0]
                    fig2 = go.Figure(go.Funnel(
                        y=df_conv[name_col],
                        x=df_conv[val_col],
                        marker=dict(color=["#4361ee","#7209b7","#f72585"]),
                    ))
                    fig2.update_layout(height=380, template="plotly_white")
                    st.plotly_chart(fig2, width="stretch")

    st.markdown("---")
    st.subheader("Cohort Retention Heatmap")
    df_cohort = load_csv("analysis_cohort_long.csv")
    if not df_cohort.empty:
        cohort_col = next((c for c in df_cohort.columns if "cohort" in c.lower()), df_cohort.columns[0])
        period_col = next((c for c in df_cohort.columns if "label" in c.lower() or "period" in c.lower()), None)
        ret_col    = next((c for c in df_cohort.columns if "retention" in c.lower() or "pct" in c.lower()), None)

        if period_col and ret_col:
            pivot = df_cohort.pivot_table(
                index=cohort_col, columns=period_col,
                values=ret_col, aggfunc="mean",
            )
            try:
                cols_sorted = sorted(pivot.columns, key=lambda x: int(str(x).split()[-1]))
                pivot = pivot[cols_sorted]
            except Exception:
                pass

            fig3 = go.Figure(go.Heatmap(
                z=pivot.values,
                x=pivot.columns.tolist(),
                y=pivot.index.tolist(),
                colorscale="Blues",
                text=pivot.round(1).values,
                texttemplate="%{text}%",
                showscale=True,
            ))
            fig3.update_layout(
                height=350, template="plotly_white",
                xaxis=dict(title="Period"),
                yaxis=dict(title="Cohort"),
            )
            st.plotly_chart(fig3, width="stretch")
            st.info(
                "Key Insight: Low Month-1 retention means most users do not return "
                "after their first purchase. Opportunity: post-purchase email campaigns."
            )
    else:
        st.info("Cohort data not available.")

    st.markdown("---")
    st.subheader("Session Behaviour Summary")
    df_sess = load_csv("analysis_sessions_summary.csv")
    if not df_sess.empty:
        st.dataframe(df_sess)
        metrics = [c for c in df_sess.columns if "avg" in c.lower()]
        type_col = next((c for c in df_sess.columns if "type" in c.lower()), None)
        if metrics and type_col:
            fig4 = px.bar(
                df_sess.melt(id_vars=type_col, value_vars=metrics,
                             var_name="metric", value_name="value"),
                x="metric", y="value", color=type_col, barmode="group",
                color_discrete_sequence=["#f72585","#4361ee"],
                template="plotly_white",
            )
            fig4.update_layout(height=350)
            st.plotly_chart(fig4, width="stretch")
    else:
        st.info("Session data not available.")

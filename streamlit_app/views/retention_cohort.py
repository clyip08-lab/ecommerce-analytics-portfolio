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
            st.subheader("Conversion Funnel")
            df_conv = load_csv("analysis_funnel.csv")
            if not df_conv.empty:
                # Find event type and user columns
                name_col = next((c for c in df_conv.columns
                                 if "event" in c.lower() or "type" in c.lower()),
                                df_conv.columns[0])
                val_col  = next((c for c in df_conv.columns
                                 if "user" in c.lower()), None)
                if val_col:
                    # Sort funnel order
                    order_map = {"view": 0, "cart": 1, "purchase": 2}
                    df_conv["_order"] = df_conv[name_col].map(order_map).fillna(99)
                    df_conv = df_conv.sort_values("_order")

                    # Calculate drop-off
                    top_val = df_conv[val_col].iloc[0]
                    df_conv["pct"] = (df_conv[val_col] / top_val * 100).round(1)
                    df_conv["label"] = df_conv.apply(
                        lambda r: f"{int(r[val_col]):,} ({r['pct']}%)", axis=1
                    )

                    fig2 = go.Figure(go.Funnel(
                        y         = df_conv[name_col].str.capitalize(),
                        x         = df_conv[val_col],
                        text      = df_conv["label"],
                        textinfo  = "text",
                        marker    = dict(color=["#4361ee","#7209b7","#f72585"]),
                    ))
                    fig2.update_layout(height=380, template="plotly_white")
                    st.plotly_chart(fig2, width="stretch")

                    # Key metrics below funnel
                    views = df_conv.loc[df_conv[name_col]=="view",     val_col].values
                    carts = df_conv.loc[df_conv[name_col]=="cart",     val_col].values
                    purch = df_conv.loc[df_conv[name_col]=="purchase", val_col].values
                    if len(views)>0 and len(carts)>0 and len(purch)>0:
                        v2c = carts[0]  / views[0] * 100
                        c2p = purch[0]  / carts[0] * 100
                        ovr = purch[0]  / views[0] * 100
                        m1, m2, m3 = st.columns(3)
                        m1.metric("View to Cart",     f"{v2c:.1f}%")
                        m2.metric("Cart to Purchase", f"{c2p:.1f}%")
                        m3.metric("Overall Conv.",    f"{ovr:.1f}%")

    st.markdown("---")
    st.subheader("Cohort Retention Heatmap")
    df_cohort = load_csv("analysis_cohort_long.csv")
    if not df_cohort.empty:
        # ✅ Force cohort_month as string to prevent date parsing
        df_cohort["cohort_month"] = df_cohort["cohort_month"].astype(str).str[:7]
        cohort_col = "cohort_month"
        period_col = "period_label"
        ret_col    = "retention_pct"

        # Verify columns exist
        missing = [c for c in [cohort_col, period_col, ret_col] if c not in df_cohort.columns]
        if missing:
            st.warning(f"Missing columns: {missing}. Available: {df_cohort.columns.tolist()}")
        else:
            pivot = df_cohort.pivot_table(
                index   = cohort_col,
                columns = period_col,
                values  = ret_col,
                aggfunc = "mean",
            )
            # ✅ Sort columns: Month 0, Month 1
            try:
                cols_sorted = sorted(pivot.columns, key=lambda x: int(str(x).split()[-1]))
                pivot = pivot[cols_sorted]
            except Exception:
                pass

            # ✅ Fill NaN with empty string for display
            z_text = []
            for row in pivot.values:
                row_text = []
                for val in row:
                    if pd.isna(val):
                        row_text.append("")
                    else:
                        row_text.append(f"{val:.1f}%")
                z_text.append(row_text)

            fig3 = go.Figure(go.Heatmap(
                z           = pivot.fillna(0).values,
                x           = pivot.columns.tolist(),
                y           = pivot.index.tolist(),
                colorscale  = "Blues",
                text        = z_text,
                texttemplate = "%{text}",
                showscale   = True,
                zmin        = 0,
                zmax        = 100,
            ))
            fig3.update_layout(
                height   = 300,
                template = "plotly_white",
                xaxis    = dict(title="Period", tickmode="array",
                               tickvals=pivot.columns.tolist(),
                               ticktext=pivot.columns.tolist()),
                yaxis    = dict(title="Cohort Month"),
                margin   = dict(t=20, b=40, l=80, r=20),
            )
            st.plotly_chart(fig3, width="stretch")

            # ✅ Key metrics below heatmap
            m1 = df_cohort[df_cohort[period_col]=="Month 1"][ret_col]
            if len(m1) > 0:
                avg_m1 = m1.mean()
                col_a, col_b = st.columns(2)
                col_a.metric("Month-0 Retention", "100%", "Baseline")
                col_b.metric("Month-1 Retention", f"{avg_m1:.2f}%",
                             f"{avg_m1-100:.2f}% vs baseline", delta_color="inverse")
            st.info(
                "Key Insight: Only 0.37% of Oct buyers returned in Nov. "
                "Near-zero retention means acquisition cost is wasted without a "
                "post-purchase retention strategy (email flows, loyalty program)."
            )
    else:
        st.info("Cohort data not available.")

    st.markdown("---")
    st.subheader("Session Behaviour Summary")
    df_sess = load_csv("analysis_sessions_summary.csv")
    if not df_sess.empty:
        st.dataframe(df_sess)
        type_col = next((c for c in df_sess.columns if "type" in c.lower()), None)
        # ✅ Exclude avg_revenue — 100x larger, makes other bars invisible
        metrics = [c for c in df_sess.columns
                   if "avg" in c.lower() and "revenue" not in c.lower()]
        if metrics and type_col:
            fig4 = px.bar(
                df_sess.melt(id_vars=type_col, value_vars=metrics,
                             var_name="metric", value_name="value"),
                x="metric", y="value", color=type_col, barmode="group",
                color_discrete_sequence=["#f72585","#4361ee"],
                template="plotly_white",
                labels={"value":"Average Value","metric":"Metric"},
            )
            fig4.update_layout(height=380)
            st.plotly_chart(fig4, width="stretch")
        # ✅ Show avg_revenue separately as metric cards
        rev_col_s = next((c for c in df_sess.columns if "revenue" in c.lower()), None)
        if rev_col_s and type_col:
            st.caption("Average Revenue per Session:")
            rcols = st.columns(len(df_sess))
            for i, (_, row) in enumerate(df_sess.iterrows()):
                rcols[i].metric(str(row[type_col]), f"${float(row[rev_col_s]):,.2f}")
    else:
        st.info("Session data not available.")

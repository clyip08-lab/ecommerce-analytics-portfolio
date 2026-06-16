# streamlit_app/views/customer_segments.py

import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
    )
)

from db import load_csv


def show():
    st.title("Exploratory Customer Segments")

    st.markdown(
        "Exploratory RFM segmentation and directional "
        "category event-ratio analysis."
    )

    st.warning(
        "RFM results are affected by the two-month observation "
        "period and independently sampled monthly user sets. "
        "Segments should be validated before campaign decisions."
    )

    st.markdown("---")

    # ========================================================
    # Exploratory RFM
    # ========================================================

    df_seg = load_csv("analysis_rfm_segments.csv")

    if df_seg.empty:
        st.error("analysis_rfm_segments.csv not found.")
        return

    user_col = next(
        (
            column
            for column in df_seg.columns
            if "user" in column.lower()
            and "id" not in column.lower()
        ),
        "users",
    )

    value_col = next(
        (
            column
            for column in df_seg.columns
            if "revenue" in column.lower()
            or "value" in column.lower()
        ),
        None,
    )

    segment_col = next(
        (
            column
            for column in df_seg.columns
            if "segment" in column.lower()
        ),
        df_seg.columns[0],
    )

    df_seg[segment_col] = df_seg[segment_col].astype(str)

    total_buyers = (
        df_seg[user_col].sum()
        if user_col in df_seg.columns
        else 0
    )

    total_value = (
        df_seg[value_col].sum()
        if value_col
        else 0
    )

    champion_mask = df_seg[segment_col].str.contains(
        "Champion",
        case=False,
        na=False,
    )

    champion_value = (
        df_seg.loc[champion_mask, value_col].sum()
        if value_col
        else 0
    )

    champion_share = (
        champion_value / total_value * 100
        if total_value > 0
        else 0
    )

    top_segment = (
        str(
            df_seg.loc[
                df_seg[value_col].idxmax(),
                segment_col,
            ]
        )
        if value_col
        else "N/A"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Sampled Buyers",
        f"{total_buyers:,.0f}",
    )

    c2.metric(
        "Observed Purchase Value",
        f"${total_value:,.0f}",
    )

    c3.metric(
        "Top Segment by Observed Value",
        top_segment,
    )

    c4.metric(
        "Champions Value Share (Exploratory)",
        f"{champion_share:.1f}%",
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sampled Buyers by Segment")

        df_bar = df_seg[
            df_seg[user_col] > 0
        ].copy()

        df_bar = df_bar.sort_values(
            user_col,
            ascending=True,
        )

        buyer_total = df_bar[user_col].sum()

        df_bar["pct"] = (
            df_bar[user_col]
            / buyer_total
            * 100
        ).round(1)

        df_bar["label"] = df_bar.apply(
            lambda row: (
                f"{int(row[user_col]):,} "
                f"({row['pct']}%)"
            ),
            axis=1,
        )

        fig1 = px.bar(
            df_bar,
            x=user_col,
            y=segment_col,
            orientation="h",
            color=user_col,
            color_continuous_scale="Blues",
            text="label",
            labels={
                user_col: "Sampled Buyers",
                segment_col: "Segment",
            },
            template="plotly_white",
        )

        fig1.update_traces(
            textposition="outside",
            cliponaxis=False,
        )

        fig1.update_layout(
            height=400,
            showlegend=False,
            margin=dict(r=150),
        )

        st.plotly_chart(
            fig1,
            width="stretch",
        )

    with col2:
        st.subheader(
            "Observed Purchase Value by Segment"
        )

        if value_col:
            df_value = df_seg.sort_values(
                value_col,
                ascending=True,
            )

            fig2 = px.bar(
                df_value,
                x=value_col,
                y=segment_col,
                orientation="h",
                color=value_col,
                color_continuous_scale="Purples",
                text=value_col,
                labels={
                    value_col:
                        "Observed Purchase Value ($)",
                    segment_col: "Segment",
                },
                template="plotly_white",
            )

            fig2.update_traces(
                texttemplate="$%{text:,.0f}",
                textposition="outside",
            )

            fig2.update_layout(
                height=400,
                showlegend=False,
                margin=dict(r=150),
            )

            st.plotly_chart(
                fig2,
                width="stretch",
            )

    st.caption(
        "RFM segments are exploratory and based only on "
        "observed purchase-event activity in the analytical "
        "sample. They should not be treated as complete "
        "customer histories."
    )

    st.markdown("---")

    # ========================================================
    # Exploratory segment notes
    # ========================================================

    st.subheader("Exploratory Segment Notes")

    champion_row = df_seg[
        df_seg[segment_col].str.contains(
            "Champion",
            case=False,
            na=False,
        )
    ]

    if not champion_row.empty and value_col:
        champion_buyers = int(
            champion_row[user_col].iloc[0]
        )

        champion_observed_value = float(
            champion_row[value_col].iloc[0]
        )

        champion_value_share = (
            champion_observed_value
            / total_value
            * 100
            if total_value > 0
            else 0
        )

        st.success(
            f"Champions segment: "
            f"{champion_buyers:,} sampled buyers, "
            f"{champion_value_share:.1f}% of observed "
            f"purchase value in this sample. "
            f"Validate the segment definition and complete "
            f"customer history before designing a campaign."
        )

    needs_row = df_seg[
        df_seg[segment_col].str.contains(
            "Needs",
            case=False,
            na=False,
        )
    ]

    if not needs_row.empty:
        needs_buyers = int(
            needs_row[user_col].iloc[0]
        )

        needs_pct = (
            needs_buyers / total_buyers * 100
            if total_buyers > 0
            else 0
        )

        st.info(
            f"Needs Attention: "
            f"{needs_buyers:,} sampled buyers "
            f"({needs_pct:.1f}% of sampled buyers). "
            f"Review recency, frequency, product mix and "
            f"sampling limitations before designing a "
            f"re-engagement test."
        )

    display_table = df_seg.copy()

    rename_map = {
        user_col: "Sampled Buyers",
        segment_col: "Segment",
    }

    if value_col:
        rename_map[value_col] = (
            "Observed Purchase Value"
        )

    display_table = display_table.rename(
        columns=rename_map
    )

    st.dataframe(
        display_table,
        width="stretch",
        hide_index=True,
    )

    st.markdown("---")

    # ========================================================
    # Category-level event ratios
    # ========================================================

    st.subheader(
        "Directional Event Ratios by Category"
    )

    st.caption(
        "Ratios are based on view, cart and purchase "
        "event counts by category. They are not "
        "distinct-user or sequential conversion rates."
    )

    df_category = load_csv(
        "analysis_funnel_category.csv"
    )

    if df_category.empty:
        st.info(
            "Category event-ratio data not available."
        )
        return

    category_col = next(
        (
            column
            for column in df_category.columns
            if "category" in column.lower()
        ),
        None,
    )

    view_cart_col = next(
        (
            column
            for column in df_category.columns
            if "view_to_cart" in column.lower()
        ),
        None,
    )

    cart_purchase_col = next(
        (
            column
            for column in df_category.columns
            if "cart_to_purchase" in column.lower()
        ),
        None,
    )

    if not (
        category_col
        and view_cart_col
        and cart_purchase_col
    ):
        st.info(
            "Expected category-ratio columns "
            "were not found."
        )
        return

    df_category = df_category.copy()

    ratio_columns = [
        view_cart_col,
        cart_purchase_col,
    ]

    for column in ratio_columns:
        df_category[column] = pd.to_numeric(
            df_category[column],
            errors="coerce",
        )

    if (
        df_category[ratio_columns]
        .max()
        .max()
        <= 1
    ):
        df_category[ratio_columns] = (
            df_category[ratio_columns]
            * 100
        )

    display_view_cart = (
        "View-to-Cart Event Ratio"
    )

    display_cart_purchase = (
        "Cart-to-Purchase Event Ratio"
    )

    chart_data = (
        df_category
        .head(10)
        .rename(
            columns={
                view_cart_col:
                    display_view_cart,
                cart_purchase_col:
                    display_cart_purchase,
            }
        )
    )

    fig3 = px.bar(
        chart_data,
        x=category_col,
        y=[
            display_view_cart,
            display_cart_purchase,
        ],
        barmode="group",
        color_discrete_sequence=[
            "#4361ee",
            "#f72585",
        ],
        template="plotly_white",
        labels={
            category_col: "Category",
            "value": "Event Ratio (%)",
            "variable": "Metric",
        },
    )

    fig3.update_layout(
        height=380,
        xaxis_tickangle=-30,
        legend_title_text="Metric",
    )

    st.plotly_chart(
        fig3,
        width="stretch",
    )

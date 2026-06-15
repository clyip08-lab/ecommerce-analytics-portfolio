import streamlit as st


def show():
    st.title("Methodology and Limitations")
    st.markdown(
        "This page explains what the current analytical sample can support, "
        "what it cannot support, and how the methodology could be improved."
    )

    st.markdown("---")
    st.subheader("Dataset and Sampling")
    st.write(
        "The raw October and November 2019 files contain approximately "
        "110 million events. The working analytical dataset contains "
        "approximately 1.6 million events from 99,693 unique users."
    )
    st.write(
        "The project selected 50,000 users independently within each month "
        "and retained the events belonging to those users within that month."
    )

    st.subheader("What This Version Can Support")
    st.markdown("- Exploratory within-month user activity analysis")
    st.markdown("- Observed purchase-value and purchase-event trends")
    st.markdown("- Product and category concentration analysis")
    st.markdown("- Directional stage-participation comparisons")
    st.markdown("- Exploratory RFM segmentation")

    st.subheader("Important Limitations")
    st.warning(
        "The results should be treated as exploratory rather than "
        "production-level conclusions."
    )
    st.markdown(
        "- **Retention:** independently sampled months cannot support "
        "a reliable cross-month retention rate."
    )
    st.markdown(
        "- **Funnel:** current ratios do not enforce a same-session, "
        "same-product and time-ordered journey."
    )
    st.markdown(
        "- **RFM:** some users may be missing activity from the other month."
    )
    st.markdown(
        "- **Orders:** the dataset has no formal order ID, so purchase "
        "events are used as a proxy."
    )
    st.markdown(
        "- **Seasonality:** two months, including major November shopping "
        "events, cannot represent normal annual performance."
    )
    st.markdown(
        "- **Time zone:** event timestamps are recorded in UTC."
    )

    st.subheader("How I Would Redesign the Analysis")
    st.markdown(
        "1. Sample users once from the combined cross-month population "
        "for retention and full-period RFM."
    )
    st.markdown(
        "2. Build a session-level sequential funnel using user, product, "
        "session and event timestamps."
    )
    st.markdown(
        "3. Use a two-pass chunked workflow or DuckDB for more "
        "memory-efficient local processing."
    )
    st.markdown(
        "4. Compare repeated samples and full-data aggregates to test "
        "whether the main results are stable."
    )

    st.info(
        "Key learning: the sampling method, metric definition and analytical "
        "grain must match the business question being answered."
    )

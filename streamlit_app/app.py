# streamlit_app/app.py
# ============================================================
# Main entry point — navigation + layout
# ============================================================

import streamlit as st

st.set_page_config(
    page_title = "E-Commerce Analytics",
    page_icon  = "🛒",
    layout     = "wide",
    initial_sidebar_state = "expanded",
)

# ── Sidebar Navigation ──
st.sidebar.image(
    "https://img.icons8.com/fluency/96/shopping-cart.png",
    width=80
)
st.sidebar.title("🛒 E-Commerce\nAnalytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    [
        "📊 Executive Overview",
        "📦 Product & Brand",
        "👥 Customer Segments",
        "🔄 Retention & Cohort",
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Data: Oct–Nov 2019")
st.sidebar.caption("Built with Python + MySQL + Streamlit")

# ── Route to pages ──
if page == "📊 Executive Overview":
    from pages import executive
    executive.show()

elif page == "📦 Product & Brand":
    from pages import product_brand
    product_brand.show()

elif page == "👥 Customer Segments":
    from pages import customer_segments
    customer_segments.show()

elif page == "🔄 Retention & Cohort":
    from pages import retention_cohort
    retention_cohort.show()
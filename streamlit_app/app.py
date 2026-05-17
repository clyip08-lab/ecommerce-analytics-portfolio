# streamlit_app/app.py

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title = "E-Commerce Analytics",
    page_icon  = ":shopping_trolley:",
    layout     = "wide",
    initial_sidebar_state = "expanded",
)

st.sidebar.image(
    "https://img.icons8.com/fluency/96/shopping-cart.png",
    width=80
)
st.sidebar.title("E-Commerce Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    [
        "Executive Overview",
        "Product and Brand",
        "Customer Segments",
        "Retention and Cohort",
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Data: Oct-Nov 2019")
st.sidebar.caption("Built with Python + MySQL + Streamlit")

if page == "Executive Overview":
    from views import executive
    executive.show()

elif page == "Product and Brand":
    from views import product_brand
    product_brand.show()

elif page == "Customer Segments":
    from views import customer_segments
    customer_segments.show()

elif page == "Retention and Cohort":
    from views import retention_cohort
    retention_cohort.show()

import os
import sys
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon=":shopping_trolley:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.image(
    "https://img.icons8.com/fluency/96/shopping-cart.png",
    width=80,
)

st.sidebar.title("E-Commerce Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    [
        "Executive Overview",
        "Product and Brand",
        "Customer Segments",
        "Methodology and Limitations",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Exploratory AI-assisted portfolio based on a monthly "
    "user-level analytical sample."
)
st.sidebar.caption("Data: October-November 2019")
st.sidebar.caption("Built with Python, MySQL and Streamlit")

st.sidebar.markdown(
    "[View methodology and source code on GitHub]"
    "(https://github.com/clyip08-lab/ecommerce-analytics-portfolio)"
)

if page == "Executive Overview":
    from views import executive
    executive.show()

elif page == "Product and Brand":
    from views import product_brand
    product_brand.show()

elif page == "Customer Segments":
    from views import customer_segments
    customer_segments.show()

elif page == "Methodology and Limitations":
    from views import methodology
    methodology.show()


import streamlit as st
import IBEX
import IBEX_components

# Dictionary of pages
pages = {
    "Page 1": IBEX,
    "Page 2": IBEX_components
}

# Sidebar for navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))

# Display the selected page
page = pages[selection]
page.app()

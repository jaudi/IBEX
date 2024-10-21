import streamlit as st
import pandas as pd
def app():
    
    st.title("Companies listed on the IBEX 35")
            
    Companies=pd.read_csv("https://raw.githubusercontent.com/jaudi/IBEX/main/ibex-components.csv")
    Companies=Companies.set_index("Ticker")

    st.dataframe(Companies)

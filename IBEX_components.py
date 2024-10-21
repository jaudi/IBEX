import streamlit as st
import pandas as pd
def app():
    
    st.title("Companies listed on the IBEX 35")
            
    Companies=pd.read_csv("https://github.com/jaudi/IBEX/blob/main/ibex-components.csv")
    Companies=Companies.set_index("Ticker")

    st.dataframe(Companies)

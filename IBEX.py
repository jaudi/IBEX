import streamlit as st
import pandas as pd
import yfinance as yf

# --- Configuration & Constants ---
# It's better to define constants at the top level.
IBEX_TICKERS = (
    'ACS.MC', 'ACX.MC', 'AENA.MC', 'AMS.MC', 'ANA.MC', 'ANE.MC', 
    'BBVA.MC', 'BKT.MC', 'CABK.MC', 'CLNX.MC', 'COL.MC', 'ELE.MC', 
    'ENG.MC', 'FDR.MC', 'FER.MC', 'GRF.MC', 'IAG.MC', 'IBE.MC', 
    'IDR.MC', 'ITX.MC', 'LOG.MC', 'MAP.MC', 'MRL.MC', 'MTS.MC', 
    'NTGY.MC', 'RED.MC', 'REP.MC', 'ROVI.MC', 'PUIGb.MC', 'SAB.MC', 
    'SAN.MC', 'SCYR.MC', 'SLR.MC', 'TEF.MC', 'UNI.MC'
)

# --- Data Fetching Functions (with Caching) ---

@st.cache_data
def get_price_data(ticker, period):
    """Fetches historical price data from yfinance and caches the result."""
    price_df = yf.download(ticker, period=period, interval="1d")
   
    
    # Standardize column names to lowercase to avoid case-sensitivity issues (e.g., 'Close' vs 'close')
    price_df.columns = ["Close","High","Low","Volume"]
    # --- FIX ENDS HERE ---

    return price_df
    


    

# --- Main App Function ---
def app():
    st.set_page_config(layout="wide")
    st.title("IBEX 35 Stock Analysis 🇪🇸")
    st.markdown("Choose a ticker to visualize price history, returns, and key financial ratios.")

    # --- Sidebar Controls ---
    st.sidebar.header("Controls")
    ticker = st.sidebar.selectbox("Choose a ticker from IBEX 35", IBEX_TICKERS)
    period = st.sidebar.radio("Select time period:", ('1y', '5y', '10y', 'ytd'), horizontal=True)

    # --- Data Loading and Processing ---
    price_df = get_price_data(ticker, period)
    fundamental_df = get_fundamental_data(ticker)

    if price_df.empty:
        st.error(f"Could not retrieve price data for {ticker}. The ticker may be delisted or there is a temporary issue with the data source.")
        return

    # --- Calculations ---
    # Returns
    price_df['Return'] = (1 + price_df['Close'].pct_change()).cumprod() - 1
    price_df['Return'] = price_df['Return'].dropna()
    
    # Moving Averages
    price_df['50MA'] = price_df['Close'].rolling(window=50).mean()
    price_df['150MA'] = price_df['Close'].rolling(window=150).mean()
    price_df['200MA'] = price_df['Close'].rolling(window=200).mean()

    # --- Display Data ---
    st.header(f"Analysis for {ticker}")

    # Display charts in columns
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Price History & Moving Averages")
        # Plot multiple columns on one chart
        st.line_chart(price_df[['Close', '50MA', '150MA', '200MA']])

    with col2:
        st.subheader("Cumulative Returns")
        st.line_chart(price_df["Return"])

   

    

# --- App Entry Point ---
if __name__ == "__main__":
    app()

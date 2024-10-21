import streamlit as st
import pandas as pd
import yfinance as yf
def app():

# Set the title and description of the app
    st.markdown(
        """
        <style>
        main {
            background-color: #f5f5f5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("IBEX 35 Analysis")

    st.markdown("This program allows you to choose a ticker from the IBEX 35 and visualize price history, returns, and fundamental ratios.")

    add_selectbox = st.sidebar.selectbox(
        "Choose a ticker from IBEX 35",
    ('ACS.MC',
    'ACX.MC',
    'AENA.MC',
    'AMS.MC',
    'ANA.MC',
    'ANE.MC',
    'BBVA.MC',
    'BKT.MC',
    'CABK.MC',
    'CLNX.MC',
    'COL.MC',
    'ELE.MC',
    'ENG.MC',
    'FDR.MC',
    'FER.MC',
    'GRF.MC',
    'IAG.MC',
    'IBE.MC',
    'IDR.MC',
    'ITX.MC',
    'LOG.MC',
    'MAP.MC',
    'MRL.MC',
    'MTS.MC',
    'NTGY.MC',
    'RED.MC',
    'REP.MC',
    'ROVI.MC',
    'PUIGb.MC',
    'SAB.MC',
    'SAN.MC',
    'SCYR.MC',
    'SLR.MC',
    'TEF.MC',
    'UNI.MC'))

    period = st.sidebar.radio(
        "Select the time period for historical data:",
        ('1y', '3y', '5y', '10y', 'ytd'))

    # Lists to store the data for the fundamental ratios
    Symbol = []
    Current_Price = []
    DividendY = []
    ROA = []
    ROE = []
    EarningGrowth = []
    RevenueGrowth = []
    GrossMargins = []
    OperationMargins = []
    PER = []

    # Function to retrieve fundamental data
    def fundamental_data(add_selectbox):
        # Fetch the ticker data once
        ticker_obj = yf.Ticker(add_selectbox)
        info = ticker_obj.info

        # Extract data with default value "no info" if not available
        symbol = info.get("symbol", "no info")
        currentPrice = info.get("currentPrice", "no info")
        dividendYield = info.get("dividendYield", "no info")
        returnOnAssets = info.get("returnOnAssets", "no info")
        returnOnEquity = info.get("returnOnEquity", "no info")
        earningGrowth = info.get("earningsGrowth", "no info")
        revenueGrowth = info.get("revenueGrowth", "no info")
        grossMargins = info.get("grossMargins", "no info")
        operatingMargins = info.get("operatingMargins", "no info")
        peRatio = info.get("trailingPE", "no info")

        # Append data to lists
        Symbol.append(symbol)
        Current_Price.append(currentPrice)
        DividendY.append(dividendYield)
        ROA.append(returnOnAssets)
        ROE.append(returnOnEquity)
        EarningGrowth.append(earningGrowth)
        RevenueGrowth.append(revenueGrowth)
        GrossMargins.append(grossMargins)
        OperationMargins.append(operatingMargins)
        PER.append(peRatio)

        # Create a DataFrame for the fundamental data
        info_ibex = pd.DataFrame({
            "Symbol": Symbol,
            "Current Price": Current_Price,
            "Dividend Yield": DividendY,
            "ROA": ROA,
            "ROE": ROE,
            "Earnings Growth": EarningGrowth,
            "Revenue Growth": RevenueGrowth,
            "Gross Margins": GrossMargins,
            "Operating Margins": OperationMargins,
            "P/E Ratio": PER
        })
        
        return info_ibex

    # Function to retrieve price data
    def prices(ticker=add_selectbox ):
        price = yf.download(ticker, period=period)
        return price

    # Retrieve fundamental data and price data for the default ticker
    fundamental_df = fundamental_data(add_selectbox).transpose()
    price_df = prices()

    # Calculate the returns
    price_df['Return'] = (1 + price_df['Close'].pct_change()).cumprod()




    st.header("Prices")
    st.line_chart(price_df["Close"])


    st.header("Returns")
    st.line_chart(price_df["Return"])

    col1, col2=st.columns(2)
    with col1:

        st.header("Ratios")
        st.dataframe(fundamental_df)

    with col2:
        st.header("Information about the company")
        st.write(yf.Ticker(add_selectbox).info.get('longBusinessSummary',"no info"))




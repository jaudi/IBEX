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
    st.markdown("""
    ## Disclaimer
    This application is created by Javier Audibert (javier.audibert@gmail.com) for recreational purposes only. The data provided is sourced from Yahoo Finance and is subject to change without notice. The author is not responsible for any errors or inaccuracies in the data. By using this application, you acknowledge that you understand and agree to these terms.
    """)
    # Sidebar for ticker selection and time period
    ticker = st.sidebar.selectbox(
        "Choose a ticker from IBEX 35",
        (
            'ACS.MC', 'ACX.MC', 'AENA.MC', 'AMS.MC', 'ANA.MC', 'ANE.MC', 
            'BBVA.MC', 'BKT.MC', 'CABK.MC', 'CLNX.MC', 'COL.MC', 'ELE.MC', 
            'ENG.MC', 'FDR.MC', 'FER.MC', 'GRF.MC', 'IAG.MC', 'IBE.MC', 
            'IDR.MC', 'ITX.MC', 'LOG.MC', 'MAP.MC', 'MRL.MC', 'MTS.MC', 
            'NTGY.MC', 'RED.MC', 'REP.MC', 'ROVI.MC', 'PUIGb.MC', 'SAB.MC', 
            'SAN.MC', 'SCYR.MC', 'SLR.MC', 'TEF.MC', 'UNI.MC'
        )
    )

    period = st.sidebar.radio(
        "Select the time period for historical data:",
        ('1y', '5y', '10y', 'ytd')
    )

    # Lists to store the data for fundamental ratios
    symbol_data = {
        "Symbol": [], "Current Price": [], "Dividend Yield": [], "ROA": [],
        "ROE": [], "Earnings Growth": [], "Revenue Growth": [], 
        "Gross Margins": [], "Operating Margins": [], "P/E Ratio": []
    }

    # Function to retrieve fundamental data
    def get_fundamental_data(ticker):
        # Fetch the ticker data
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info

        # Extract data with default value "no info" if not available
        symbol_data["Symbol"].append(info.get("symbol", "no info"))
        symbol_data["Current Price"].append(info.get("currentPrice", "no info"))
        symbol_data["Dividend Yield"].append(info.get("dividendYield", "no info"))
        symbol_data["ROA"].append(info.get("returnOnAssets", "no info"))
        symbol_data["ROE"].append(info.get("returnOnEquity", "no info"))
        symbol_data["Earnings Growth"].append(info.get("earningsGrowth", "no info"))
        symbol_data["Revenue Growth"].append(info.get("revenueGrowth", "no info"))
        symbol_data["Gross Margins"].append(info.get("grossMargins", "no info"))
        symbol_data["Operating Margins"].append(info.get("operatingMargins", "no info"))
        symbol_data["P/E Ratio"].append(info.get("trailingPE", "no info"))

        # Create a DataFrame for the fundamental data
        return pd.DataFrame(symbol_data)

    # Function to retrieve price data
    
    price_df=yf.download(ticker, period=period,interval="1d")
    price_df.columns=["Close","High","Low","Open","Volume"]   

    # Retrieve fundamental data and price data
    fundamental_df = get_fundamental_data(ticker).transpose()
    

    # Calculate the cumulative returns
    price_df['Return'] = (1 + price_df['Close'].pct_change()).cumprod()-1
    price_df['Return']=price_df['Return'].fillna(0)

    # Display the data
    st.header(f"Prices of {ticker}")
    st.write(price_df)
    st.header("Close Prices")
    st.line_chart(price_df["Close"])
    
    st.header("Returns")
    st.line_chart(price_df["Return"])

    st.header("Volume")
    st.bar_chart(price_df["Volume"])
    st.download_button(label="Download prices in CSV",
    data=price_df.to_csv(index=True),file_name=f"prices_{ticker}_{period}.csv",mime="text/csv")
    st.download_button(label="Download fundamental data", data=fundamental_df.to_csv(index=True),file_name=f"fundamentals_{ticker}.csv", mime="text/csv")
    col1, col2 = st.columns(2)
    with col1:
        st.header("Ratios")
        st.dataframe(fundamental_df)

    with col2:
        st.header("Information about the Company")
        company_info = yf.Ticker(ticker).info.get('longBusinessSummary', "No information available")
        st.write(company_info)
    price_df['200MA'] = price_df['Close'].rolling(window=200).mean()
    price_df['150MA']=price_df['Close'].rolling(window=150).mean()
    price_df['100MA']=price_df['Close'].rolling(window=100).mean()
    price_df['50MA']=price_df['Close'].rolling(window=50).mean()
    MA200=price_df['200MA'].iloc[-1]
    MA150=price_df['150MA'].iloc[-1]
    MA50=price_df['50MA'].iloc[-1]
    col1, col2, col3=st.columns(3)
    with col1:
        st.subheader("Moving average 200")
        st.metric(label="MA200", value= f"{MA200:.2f}")
    with col2:
        st.subheader("Moving average 150")
        st.metric(label="MA150", value=f"{MA150:.2f}")
        
    with col3:
        st.subheader("Moving average 50")
        st.metric(label="MA50", value=f"{MA50:.2f}")
# Call the app function to run the Streamlit app

if __name__ == "__main__":
    app()

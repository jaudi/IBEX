import streamlit as st
import pandas as pd
import yfinance as yf


@st.cache_data
def load_price_data(ticker, period):
    """Loads historical price data for a given ticker and removes the 'Adj Close' column."""
    df = yf.download(ticker, period=period, interval="1d")
    # Drop the "Adj Close" column as it is not used in the app
    if "Adj Close" in df.columns:
        df = df.drop(columns=['Adj Close'])
    return df


@st.cache_data
def get_fundamental_data(ticker):
    """Fetches key fundamental data points for a given ticker."""
    symbol_data = {
        "Symbol": [], "Current Price": [], "Dividend Yield": [], "ROA": [],
        "ROE": [], "Earnings Growth": [], "Revenue Growth": [],
        "Gross Margins": [], "Operating Margins": [], "P/E Ratio": []
    }
    try:
        info = yf.Ticker(ticker).info
        symbol_data["Symbol"].append(info.get("symbol", "N/A"))
        symbol_data["Current Price"].append(info.get("currentPrice", "N/A"))
        symbol_data["Dividend Yield"].append(info.get("dividendYield", "N/A"))
        symbol_data["ROA"].append(info.get("returnOnAssets", "N/A"))
        symbol_data["ROE"].append(info.get("returnOnEquity", "N/A"))
        symbol_data["Earnings Growth"].append(info.get("earningsGrowth", "N/A"))
        symbol_data["Revenue Growth"].append(info.get("revenueGrowth", "N/A"))
        symbol_data["Gross Margins"].append(info.get("grossMargins", "N/A"))
        symbol_data["Operating Margins"].append(info.get("operatingMargins", "N/A"))
        symbol_data["P/E Ratio"].append(info.get("trailingPE", "N/A"))
    except Exception as e:
        st.error(f"Failed to fetch fundamental data: {e}")

    return pd.DataFrame(symbol_data).transpose()


def calculate_rsi(df, window=14):
    """Calculates the Relative Strength Index (RSI)."""
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    # Avoid division by zero
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df


def process_price_data(df):
    """Calculates returns, moving averages, and other metrics."""
    df['Return'] = (1 + df['Close'].pct_change()).cumprod() - 1
    df['Return'] = df['Return'].fillna(0)
    for ma in [50, 100, 150, 200]:
        df[f'{ma}MA'] = df['Close'].rolling(window=ma).mean()
    df = calculate_rsi(df)  # Calculate RSI
    return df


def display_moving_averages(df):
    """Displays key moving average metrics."""
    cols = st.columns(3)
    for i, ma in enumerate([200, 150, 50]):
        if len(df) >= ma:
            value = df[f'{ma}MA'].iloc[-1]
            with cols[i]:
                st.subheader(f"Moving Average {ma}")
                st.metric(label=f"MA{ma}", value=f"{value:.2f}")
        else:
            with cols[i]:
                st.warning(f"Not enough data for MA{ma}")


def app():
    """Main function to run the Streamlit application."""
    st.markdown("<style>main {background-color: #f5f5f5;}</style>", unsafe_allow_html=True)
    st.title("IBEX 35 Analysis")
    st.markdown("Visualize price history, returns, and fundamental ratios from Yahoo Finance.")
    st.markdown("## Disclaimer")
    st.info("This application is for educational purposes only. Created by Javier Audibert.")

    ticker = st.sidebar.selectbox("Choose a ticker from IBEX 35", (
        'ACS.MC', 'ACX.MC', 'AENA.MC', 'AMS.MC', 'ANA.MC', 'ANE.MC',
        'BBVA.MC', 'BKT.MC', 'CABK.MC', 'CLNX.MC', 'COL.MC', 'ELE.MC',
        'ENG.MC', 'FDR.MC', 'FER.MC', 'GRF.MC', 'IAG.MC', 'IBE.MC',
        'IDR.MC', 'ITX.MC', 'LOG.MC', 'MAP.MC', 'MRL.MC', 'MTS.MC',
        'NTGY.MC', 'RED.MC', 'REP.MC', 'ROVI.MC', 'PUIGb.MC', 'SAB.MC',
        'SAN.MC', 'SCYR.MC', 'SLR.MC', 'TEF.MC', 'UNI.MC'
    ))
    period = st.sidebar.radio("Select time period:", ('1y', '5y', '10y', 'ytd'))

    with st.spinner("Loading data..."):
        price_df = load_price_data(ticker, period)
        fundamental_df = get_fundamental_data(ticker)
        company_info = yf.Ticker(ticker).info.get('longBusinessSummary', "No information available")
        price_df = process_price_data(price_df)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Charts", "Fundamentals", "Company Info", "Risk", "RSI", "Glossary"])

    with tab1:
        st.header(f"{ticker} - Price Data")
        st.line_chart(price_df["Close"])
        st.header("Returns")
        st.line_chart(price_df["Return"])
        st.header("Volume")
        st.bar_chart(price_df["Volume"])
        display_moving_averages(price_df)
        st.download_button("Download Prices CSV", price_df.to_csv(), f"{ticker}_prices.csv", "text/csv")

    with tab2:
        st.header("Fundamental Ratios")
        st.dataframe(fundamental_df)
        st.download_button("Download Fundamentals CSV", fundamental_df.to_csv(), f"{ticker}_fundamentals.csv", "text/csv")

    with tab3:
        st.header("Company Summary")
        st.write(company_info)

    with tab4:
        st.header("Risk Metrics")
        returns = price_df['Close'].pct_change().dropna()
        if not returns.empty:
            volatility = returns.std() * (252**0.5)
            sharpe = (returns.mean() / returns.std()) * (252**0.5) if returns.std() != 0 else 0
            cumulative = (1 + returns).cumprod()
            drawdown = 1 - cumulative / cumulative.cummax()
            max_dd = drawdown.max()
            var_95 = returns.quantile(0.05)

            st.metric("Annualized Volatility", f"{volatility:.2%}")
            st.metric("Sharpe Ratio (0% rf)", f"{sharpe:.2f}")
            st.metric("Max Drawdown", f"{max_dd:.2%}")
            st.metric("Value at Risk (VaR 95%)", f"{var_95:.2%}")
        else:
            st.warning("Not enough return data to calculate risk metrics.")

    # Tab with updated RSI definition
    with tab5:
        st.header("Relative Strength Index (RSI)")
        st.line_chart(price_df["RSI"])
        st.info(
            """
            **Interpreting the RSI Chart:**
            The RSI is a momentum tool gauging the speed and magnitude of price changes to identify potentially overbought or oversold conditions.
            - **Overbought (RSI > 70):** Suggests the asset may be overvalued and could be due for a price correction.
            - **Oversold (RSI < 30):** Indicates the asset may be undervalued and could be poised for a rebound.
            """
        )

    # Glossary tab with updated RSI definition
    with tab6:
        st.header("Glossary")
        st.write("Below are some key financial metrics and technical indicators.")

        st.subheader("ROA (Return on Assets)")
        st.write("ROA is a metric that measures a company's profitability in relation to its assets.")
        st.latex(r"ROA = \frac{\text{Net Income}}{\text{Total Assets}}")

        st.subheader("ROE (Return on Equity)")
        st.write("ROE measures a company's profitability relative to shareholder equity.")
        st.latex(r"ROE = \frac{\text{Net Income}}{\text{Shareholder Equity}}")

        st.subheader("P/E Ratio (Price-to-Earnings)")
        st.write("Shows how much investors are willing to pay per dollar of earnings.")
        st.latex(r"P/E = \frac{\text{Stock Price}}{\text{Earnings per Share}}")

        st.subheader("Dividend Yield")
        st.write("Represents dividend income relative to the stock price.")
        st.latex(r"Dividend\ Yield = \frac{\text{Annual Dividend}}{\text{Stock Price}}")
        
        st.subheader("RSI (Relative Strength Index)")
        st.write("A technical momentum indicator comparing recent gains to recent losses to measure the speed and change of a security's price movements and identify overbought or oversold conditions.")
        st.latex(r"RSI = 100 - \frac{100}{1 + (\frac{\text{Average Gain}}{\text{Average Loss}})}")
        st.markdown("The calculation uses a positive and negative moving average, typically over a 14-day period.")


if __name__ == "__main__":
    app()

import yahoo_fin.stock_info as si
import pandas as pd
import get_all_tickers.get_tickers as gt
from yahoo_fin import options
import random
aapl = si.get_data("aapl", start_date = "2015-01-01")

all_tickers = gt.get_tickers()

fundamental_AT = pd.DataFrame()
fundamental_EBIT = pd.DataFrame()
fundamental_SO = pd.DataFrame()
adjusted_close_price_data = pd.DataFrame()

# get the historical adjusted close price
for ticker in all_tickers[5300:]:
    try:
        adj_data = si.get_data(ticker, start_date="2015-01-01")
        adjusted_close_price_data = adjusted_close_price_data.append(adj_data)
    except:
        pass

# get AT
for ticker in all_tickers[5300:]:
    try:
        # get Total Assets fundamentals
        balance_sheet = si.get_balance_sheet(ticker, yearly=False)
        AT = balance_sheet.loc["totalAssets"]
        df_at = pd.DataFrame({
            # "Date" : AT.index,
            "AT": AT,
            "ticker": ticker
        })
        fundamental_AT = fundamental_AT.append(df_at)
    except:
        pass

# get AT
for ticker in all_tickers[5300:]:
    try:
        # get OP
        inc_stat = si.get_income_statement(ticker, yearly=False)
        EBIT = inc_stat.loc["ebit"]

        df_op = pd.DataFrame({
            "Date": EBIT.index,
            "EBIT": EBIT,
            "ticker": ticker
        })
        fundamental_EBIT = fundamental_EBIT.append(df_op)

    except:
        pass


# get Mar_cap
tickers = []
mar_caps = []

for ticker in all_tickers[5300:]:
    try:
        market_cap = si.get_quote_table(ticker)["Market Cap"]

        tickers.append(ticker)
        mar_caps.append(market_cap)
    except:
        pass

mar_cap_df = pd.DataFrame({
    "ticker" : tickers,
    "mar" : mar_caps
})

fundamental_EBIT.to_csv("fundamentals_EBIT_ab_5300.csv")
fundamental_AT.to_csv("fundamentals_AT_ab_5300.csv")
adjusted_close_price_data.to_csv("stock_price_data_ab_5300.csv")
mar_cap_df.to_csv("mar_cap_ab_5300.csv")
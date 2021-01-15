import numpy as np
import pandas as pd
import yahoo_fin.stock_info as si
import get_all_tickers.get_tickers as gt


all_tickers = gt.get_tickers()
price_data = pd.DataFrame()

for ticker in all_tickers:
    try:
        df = si.get_data(ticker, start_date="2016-01-01")
        price_data = price_data.append(df)
    except:
        pass

price_data.to_csv("stock_price_data_from_2016.csv")







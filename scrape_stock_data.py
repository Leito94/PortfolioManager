from bs4 import BeautifulSoup as bs
import requests
import re
import json
import pandas as pd
import json
import yahoo_fin.stock_info as si

with open("relevant_trading_212_tickers.json", "r") as f:
    relevant_trading_212_tickers = json.load(f)

op_data = pd.DataFrame()

for ticker in relevant_trading_212_tickers[1600:2400]:
    try:

        ticker_df = pd.DataFrame({
            "operating_income": si.get_income_statement(ticker, yearly=False).loc["operatingIncome"],
            "ticker": ticker
        })
        op_data = op_data.append(ticker_df)
    except:
        pass

op_data.to_csv("OP_to_1600_2400.csv")

if False:

    at_data = pd.DataFrame()

    for ticker in relevant_trading_212_tickers[4200:]:
        try:

            ticker_df = pd.DataFrame({
                "totalAssets": si.get_balance_sheet(ticker, yearly=False).loc["totalAssets"],
                "ticker": ticker
            })
            at_data = at_data.append(ticker_df)
        except:
            pass

    at_data.to_csv("AT_data_ab_4200.csv")

    so_data = pd.DataFrame()

    for ticker in relevant_trading_212_tickers[4200:]:
        try:

            ticker_df = pd.DataFrame({
                "common_stock": si.get_balance_sheet(ticker, yearly=False).loc["commonStock"],
                "ticker": ticker
            })
            so_data = so_data.append(ticker_df)
        except:
            pass

    so_data.to_csv("SO_data_ab_ab_4200.csv")

import pyttsx3

text = "Ich bin fertig du Sneck. Es sind insgesamt " + str(len(relevant_trading_212_tickers)) + " ticker, du sneck."

speaker = pyttsx3.init()

speaker.say(text)
speaker.runAndWait()





import pandas as pd
import yfinance as yf
from enum import Enum
from il_tickers import get_tlv_quote


class StockEx(Enum):
    NY = "NY"
    TLV = "TLV"


handlers = {
    StockEx.NY: lambda tick: yf.Ticker(tick).info['previousClose'],
    StockEx.TLV: lambda tick: get_tlv_quote(tick)
}


df = pd.read_csv("portfolio.csv")

for index, row in df.iterrows():
    print(row)

    ticker_name = row['Ticker']
    ticker_se = StockEx(row['SE'])
    ticker_price = handlers[ticker_se](ticker_name)

    print("Last quote:", ticker_price)
    print("-"*30)

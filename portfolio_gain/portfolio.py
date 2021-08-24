from datetime import datetime
from enum import Enum

import pandas as pd
import yfinance as yf
from il_tickers import get_tlv_quote
from currency_converter import CurrencyConverter
from display_helpers import repr_float, repr_int, rg

usd2ils_rate = CurrencyConverter().convert(1, 'USD', 'ILS')


class StockEx(Enum):
    NY = "NY"
    TLV = "TLV"


price_getter = {
    StockEx.NY: lambda tick: yf.Ticker(tick).info['previousClose'],
    StockEx.TLV: lambda tick: get_tlv_quote(tick)
}


class Holding:
    def __init__(self, **kwargs) -> None:
        self.name: str = kwargs["Name"]
        self.ticker: str = kwargs["Ticker"]
        self.Se: StockEx = StockEx(kwargs["SE"])
        self.amount: int = kwargs["Amount"]
        self.date: datetime = kwargs["Date"]
        self.price: float = kwargs["Price"]
        self.usd_ils: float = kwargs["Usd2Ils"]
        self.ils_buy_price: float = (self.price * self.usd_ils * self.amount) / self._tlv_coeff
        self.ils_current_price: float = (self.current_price * self._ils_coeff * self.amount) / self._tlv_coeff

    def __str__(self) -> str:
        display_dict = self.__dict__.copy()
        display_dict["amount"] = repr_int(self.amount)
        display_dict["ils_buy_price"] = repr_float(self.ils_buy_price)
        display_dict["ils_current_price"] = repr_float(self.ils_current_price)
        return str(display_dict)

    @property
    def _tlv_coeff(self):
        return 100 if self.Se == StockEx.TLV else 1

    @property
    def _ils_coeff(self):
        return 1 if self.Se == StockEx.TLV else usd2ils_rate

    @property
    def current_price(self):
        return price_getter[self.Se](self.ticker)


df = pd.read_csv("portfolio.csv")

for index, row in df.iterrows():
    holding = Holding(**row.to_dict())
    print(holding)

    change = holding.current_price - holding.price
    real_ils_change = holding.ils_current_price - holding.ils_buy_price

    print(f"Last quote: {repr_float(holding.current_price)}")
    print(f"Change in original currency: {rg(repr_float(change))}")
    print(repr_float(holding.ils_buy_price),
          repr_float(holding.ils_current_price),
          rg(repr_float(real_ils_change)))

    print("-"*30)
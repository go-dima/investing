from datetime import datetime
from enum import Enum
from functools import reduce
from operator import add
from typing import List
import csv

import yfinance as yf
from il_tickers import get_tlv_quote
from currency_converter import CurrencyConverter
from display_helpers import repr_float, repr_int, rg

usd2ils_rate = CurrencyConverter().convert(1, 'USD', 'ILS')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class StockEx(Enum):
    NY = "NY"
    TLV = "TLV"


price_getter = {
    StockEx.NY: lambda tick: yf.Ticker(tick).info['regularMarketPrice'],
    StockEx.TLV: lambda tick: get_tlv_quote(tick)
}


class Holding:
    def __init__(self, raw_data) -> None:
        self.name: str = raw_data["Name"]
        self.ticker: str = raw_data["Ticker"]
        self.Se: StockEx = StockEx(raw_data["SE"])
        self.amount: int = int(raw_data["Amount"])
        self.date: datetime = raw_data["Date"]
        self.price: float = float(raw_data["Price"])
        self.ils_ratio: float = float(raw_data["Usd2Ils"])
        self.ils_buy_price: float = (self.price * self._to_nis * self.amount) / self._to_shekel
        self.ils_current_price: float = 0.0
        self.change: float = 0.0
        self.real_ils_change: float = 0.0
        self.ils_pct_change: float = 0.0

    def __str__(self) -> str:
        display_dict = self.__dict__.copy()
        display_dict["amount"] = repr_int(self.amount)
        display_dict["ils_buy_price"] = repr_float(self.ils_buy_price)
        display_dict["ils_current_price"] = repr_float(self.ils_current_price)
        display_dict["change"] = repr_float(self.change)
        display_dict["real_ils_change"] = repr_float(self.real_ils_change)
        display_dict["ils_pct_change"] = repr_float(self.ils_pct_change)
        return str(display_dict)

    def eval(self):
        try:
        self.current_price = price_getter[self.Se](self.ticker)
        self.ils_current_price = (self.current_price * self._to_nis * self.amount) / self._to_shekel
        self.change = self.current_price - self.price
        self.real_ils_change = self.ils_current_price - self.ils_buy_price
        self.ils_pct_change = (self.real_ils_change / self.ils_buy_price) * 100
            logger.info(f"{self.name}: #{self.amount}, {repr_float(self.real_ils_change)}({repr_float(self.ils_pct_change)})")
        except Exception as e:
            print(e)
            print(self.ticker, self.current_price)

    @property
    def _to_shekel(self):
        return self.ils_ratio if self.Se == StockEx.TLV else 1

    @property
    def _to_nis(self):
        return 1 if self.Se == StockEx.TLV else usd2ils_rate


class Portfolio:
    def __init__(self, filename) -> None:
        with open(filename) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            self.holdings: List[Holding] = [Holding(row) for row in csv_reader]
        self.name = filename
        self.total_buy: float
        self.total_currect: float
        self.gain: float
        self.pct_gain: float

    def eval(self):
        if not self.holdings:
            return

        list(map(lambda h: h.eval(), self.holdings))
        self.total_buy = reduce(add, [h.ils_buy_price for h in self.holdings])
        self.total_currect = reduce(add, [h.ils_current_price for h in self.holdings])
        self.gain = self.total_currect - self.total_buy
        self.pct_gain = (self.gain / self.total_buy) * 100
        logger.info(f"{self.name} completed")


if __name__ == "__main__":
    portfolio = Portfolio('portfolio.csv')
    portfolio.eval()

    for holding in portfolio.holdings:
        print(holding)
        print(f"Last quote: {repr_float(holding.current_price)}")
        print(f"Change in original currency: {rg(repr_float(holding.change))}")
        print(repr_float(holding.ils_buy_price),
              repr_float(holding.ils_current_price),
              rg(repr_float(holding.real_ils_change)),
              rg(f"{repr_float(holding.ils_pct_change)}%"))

        print("-"*30)

    print(f"Total buy price\t\t{repr_float(portfolio.total_buy)}")
    print(f"Total current price\t{repr_float(portfolio.total_currect)}")
    print(f"Total gain\t\t{rg(repr_float(portfolio.gain))}", rg(f"{repr_float(portfolio.pct_gain)}%"))

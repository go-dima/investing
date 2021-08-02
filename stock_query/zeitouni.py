#!/usr/bin/python3

import yfinance as yf
import time
from colorama import Fore, Style
import argparse
from typing import List


def rg(to_color: str):
    if to_color[0] == '-':
       return f"{Fore.RED}{to_color}{Style.RESET_ALL}"
    return f"{Fore.GREEN}{to_color}{Style.RESET_ALL}"


def b(to_color: str):
    return f"{Style.BRIGHT}{to_color}{Style.RESET_ALL}"


def cyan(text: str):
    return f"{Fore.CYAN}{text}{Style.RESET_ALL}"


def yellow(text: str):
    return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"

def demo():
    msft = yf.Ticker("MSFT")
    # get stock info
    print(msft.info)

    # get historical market data
    hist = msft.history(period="3y")
    print(hist)
    print(hist['Close'], max(hist['Close']), min(hist['Close']))


def high_low(stock, time_period: str):
    history = stock.history(period=time_period)
    return f"{max(history['Close']):.3f}, {min(history['Close']):.3f}"


def change(stock, time_period: str):
    close_values = stock.history(time_period)['Close']
    oldest = close_values[0]
    newest = close_values[-1]
    percent = (newest - oldest) / oldest * 100
    return percent, oldest, newest


def print_stock_history(stock, time_period: str):
    change_over_time = change(stock, time_period)
    percent_with_color = rg(f"{change_over_time[0]:.3f}%")
    change_over_time_display = f"{percent_with_color}, from {change_over_time[1]:.3f} to {change_over_time[2]:.3f}"
    print(b(time_period), change_over_time_display, f"H/L: {high_low(stock, time_period)}")


def inspect_ticker(ticker_name: str):
    tikcer_data = yf.Ticker(ticker_name)
    print(cyan(f"{tikcer_data.info['shortName']}"),
          yellow(f"Price: {tikcer_data.info['regularMarketPrice']} ({ticker_name.upper()})"))
    print('Previous Close', tikcer_data.info['previousClose'])
    print('50 Day Average', tikcer_data.info['fiftyDayAverage'])
    print('200 Day Average', tikcer_data.info['twoHundredDayAverage'])
    for time_frame in ["10d", "6mo", "1y", "3y"]:
        print_stock_history(tikcer_data, time_frame)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--stock',
        action='store', dest='stock',
        required=False, help='Stocks to check (single or comma separated: aapl/msft,amzn)')
    parser.add_argument(
        '-t', '--time',
        action='store', dest='custom_period',
        required=False, help='Custom interval to check. e.g: 4d, 1mo, 3y, max')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.stock:
        for ticker_name in args.stock.split(','):
            inspect_ticker(ticker_name)
            if args.custom_period:
                print_stock_history(yf.Ticker(ticker_name), args.custom_period)
            print("-"*20)
    else:
        for ticker_name in open("stocks.list","r").read().splitlines():
            inspect_ticker(ticker_name)
            print("-"*20)

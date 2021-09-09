import threading
import datetime
import pytz
import pandas as pd
from display_helpers import repr_float
from flask import Flask
from portfolio import Portfolio

app = Flask(__name__)

portfolio: Portfolio = None
portfolio_evaluation = "No data yet"
last_run = "Didn't run"


def eval_portfolio():
    global portfolio
    global last_run
    global portfolio_evaluation

    portfolio.eval()
    last_run = datetime.datetime.now(pytz.timezone('Asia/Jerusalem')).strftime("%Y-%m-%d %H:%M")
    portfolio_evaluation = \
        f"{last_run}<br>" + \
        f"{repr_float(portfolio.total_currect)}, {repr_float(portfolio.gain)} ({repr_float(portfolio.pct_gain)}%)"


@app.route('/')
def hello_world():
    return 'Hey, we have Flask in a Docker container!'


@app.route('/portfolio')
def get_portfolio():
    return portfolio_evaluation


if __name__ == '__main__':
    df = pd.read_csv("portfolio.csv")
    portfolio = Portfolio(df)
    t1 = threading.Thread(target=eval_portfolio)
    t1.start()
    app.run(debug=True, host='0.0.0.0')

from display_helpers import repr_float
from flask import Flask
import pandas as pd
from portfolio import Portfolio

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hey, we have Flask in a Docker container!'


@app.route('/portfolio')
def portfolio():
    df = pd.read_csv("portfolio.csv")
    portfolio = Portfolio(df)
    portfolio.eval()
    return f"{repr_float(portfolio.total_currect)}, {repr_float(portfolio.gain)} ({repr_float(portfolio.pct_gain)}%)"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

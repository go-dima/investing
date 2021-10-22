import glob
import threading
import datetime
import pytz
import time
from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from display_helpers import repr_float, repr_int
from portfolio import Portfolio

app = Flask(__name__, template_folder="templates")
bootstrap = Bootstrap(app)

portfolios = {}


@app.template_filter()
def format_float(value):
    return repr_float(value)


@app.template_filter()
def format_int(value):
    return repr_int(value)


def render(template, **kwargs):
    defaults = {
        "title": "Home",
        "template_name_or_list": template,
        "portfolio_names": portfolios.keys()
    }
    return render_template(**{**defaults, **kwargs})


def timestamp_now():
    return datetime.datetime.now(pytz.timezone('Asia/Jerusalem')).strftime("%Y-%m-%d %H:%M")


def eval_portfolio():
    while True:
        for portfolio_data in portfolios.values():
            portfolio_data["last_run"] = f"Started: {timestamp_now()}"
            portfolio_data["portfolio"].eval()
            portfolio_data["last_run"] = timestamp_now()
            portfolio_data["portfolio_evaluation"] = \
                f"{repr_float(portfolio_data['portfolio'].total_currect)}" + " " + \
                f"{repr_float(portfolio_data['portfolio'].gain)} ({repr_float(portfolio_data['portfolio'].pct_gain)}%)"
        time.sleep(60*60*8)


@app.route('/')
@app.route('/home')
def home():
    return render("home.html", portfolios=portfolios)


@app.route('/port')
@app.route('/port/<portfolio_id>')
def get_portfolio(portfolio_id: str = 'portfolio'):
    return render("details.html", title=portfolio_id, portfolio=portfolios[portfolio_id])


@app.route('/perf')
@app.route('/perf/<portfolio_id>')
def get_performance(portfolio_id: str = 'portfolio'):
    return render("summary.html", title=portfolio_id, portfolio=portfolios[portfolio_id])


@app.route("/api/perf")
@app.route("/api/perf/<portfolio_id>")
def api_get_portfolio(portfolio_id: str = 'portfolio'):
    return {
        'portfolio_evaluation': portfolios[portfolio_id]['portfolio_evaluation'],
        'last_run': portfolios[portfolio_id]['last_run']
    }


@app.route("/api/portfolios")
def api_get_portfolios():
    return {
        "keys": list(portfolios.keys())
    }


if __name__ == '__main__':
    for filename in glob.glob("*.csv"):
        portfolios[filename.split('.')[0]] = {
            "portfolio": Portfolio(filename),
            "portfolio_evaluation": "No data yet",
            "last_run": "Didn't run"
        }
    t1 = threading.Thread(target=eval_portfolio)
    t1.start()
    app.run(debug=True, host='0.0.0.0')

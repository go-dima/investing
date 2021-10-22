from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from contextlib import contextmanager

#  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
#  sudo apt -y install ./google-chrome-stable_current_amd64.deb
#  https://sites.google.com/a/chromium.org/chromedriver/downloads
#  wget https://chromedriver.storage.googleapis.com/DRIVER/chromedriver_linux64.zip
#  unzip chromedriver_linux64.zip

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def Browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    chrome = webdriver.Chrome(options=options)
    yield chrome
    chrome.quit()


def get_tlv_quote(ticker: str):
    base_url = "https://www.bizportal.co.il/mutualfunds/quote/generalview/"

    while True:
        with Browser() as browser:
            try:
                browser.get(base_url + ticker)
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                quote = soup.find(class_="num").get_text().replace(',', '')
                is_ag = len(quote) > 4 and '.' not in quote
                return float(quote) if not is_ag else float(quote)/100
            except WebDriverException:
                pass
            except Exception as e:
                logger.error(f"Failed to get {ticker}\n", e)
                return 0


if __name__ == "__main__":
    ticker_numbers = ["5120282", "5123039"]
    for ticker in ticker_numbers:
        print(get_tlv_quote(ticker))

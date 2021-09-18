import json
import logging
import requests
from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import Config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioBot:
    def __init__(self):
        with open("bot.config", 'r') as conf_file:
            self.config = Config(**json.load(conf_file))
        self.telegram_client = Bot(self.config.token)
        self.updater = Updater(self.config.token, use_context=True)
        self.dp = self.updater.dispatcher
        self.dp.add_handler(CommandHandler('echo', self._echo))
        self.dp.add_handler(CommandHandler('summary', self._get_summary))
        self.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self._get_summary))

        res = requests.get(f"http://{self.config.server}/api/portfolios")
        self.available_portfolios = json.loads(res.content.decode())['keys']

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def _echo(self, bot, context):
        logger.info("Got echo, replying...")
        bot.message.reply_text("Sup")

    def _get_summary(self, bot, context):
        logger.info(f"message: {bot.message.text} from {bot.message.chat.first_name}")

        if str(bot.message.chat.id) not in self.config.known_clients.keys():
            logger.info(f"Unknown: {bot.message.chat}")
            with open("portfolio_bot.log", 'a+') as log_file:
                log_file.write(f"{str(bot.message.chat)}\n")
            return

        param_portfolio = bot.message.text.replace("/summary", "").strip()
        config_portfolio = self.config.known_clients.get(str(bot.message.chat.id))
        portfolio_name = param_portfolio if len(param_portfolio) > 0 else config_portfolio

        if portfolio_name not in self.available_portfolios:
            logger.error(f"Couldn't find {portfolio_name} in portfolios")
            return

        res = requests.get(f"http://{self.config.server}/api/perf/{portfolio_name}")
        if res.status_code == 200:
            res_portfolio = json.loads(res.content.decode())
            bot.message.reply_text(f"{res_portfolio['last_run']}\n{res_portfolio['portfolio_evaluation']}")
        else:
            bot.message.reply_text(f"Got {res.status_code}")


if __name__ == '__main__':
    bot = PortfolioBot()
    logger.info(f"\n{bot.config}")
    bot.start()

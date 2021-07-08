import logging
import os
from config import *
import django
import telebot as tb


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tg_marathon.tg_marathon.settings')
django.setup()

# from tg_marathon.marathon.models import User, Photo, Measurement


def log_error(f):
    """
    Обработчик ошибок
    :param f:
    :return:
    """

    logging.basicConfig(level=logging.ERROR, filename=f'{os.getcwd()}\\Logs\\logs_error.log',
                        format='%(asctime)s %(levelname)s:%(message)s')

    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as exc:
            logging.error(f'Error - {exc}')
    return inner


class BotMarathon:

    def __init__(self):
        self.bot = tb.AsyncTeleBot(token=TOKEN)
        self.def_bots()

    @log_error
    def run(self):
        while True:
            try:
                self.bot.polling(none_stop=True)
            except Exception as exc:
                self.bot.stop_polling()
                logging.error(exc)

    def def_bots(self):
        """
        Хранит в себе весь хаос бота
        :return:
        """

        @log_error
        @self.bot.message_handler(commands='start')
        def start(message):
            self.bot.send_message(text='Хай!', chat_id=message.chat.id)


if __name__ == "__main__":
    bot = BotMarathon()
    bot.run()


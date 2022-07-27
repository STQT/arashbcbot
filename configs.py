import telebot
import os
import logging
import datetime

from dotenv import load_dotenv

load_dotenv()
formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'
logging.basicConfig(
    filename=f'logs/bot-from-{datetime.datetime.now().date()}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING
)

TOKEN = os.getenv('BOT_TOKEN')


def get_user_id(message: telebot.types.Message) -> str:
    return "[{}, {}]".format(message.from_user.id, message.from_user.username, )

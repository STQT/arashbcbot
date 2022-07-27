import telebot
import os
import logging
import datetime

formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'
logging.basicConfig(
    filename=f'bot-from-{datetime.datetime.now().date()}.log',
    filemode='w',
    format=formatter,
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.WARNING
)

TOKEN = "1803316826:AAH6Z3f4EuUJyKCVZ_asWyYg63p6m94ka34"


def get_user_id(message: telebot.types.Message) -> str:
    return "[{}, {}]".format(message.from_user.id, message.from_user.username, )

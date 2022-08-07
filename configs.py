import telebot
import os
import logging
import datetime

from dotenv import load_dotenv

load_dotenv()
formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'


TOKEN = os.getenv('BOT_TOKEN')

DEBUG = os.getenv('BOT_DEBUG', False)  # if DEBUG doesn't exist then .env will None variable

if not DEBUG:
    logging.basicConfig(
        filename=f'logs/bot-from-{datetime.datetime.now().date()}.log',
        filemode='w',
        format=formatter,
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.WARNING
    )

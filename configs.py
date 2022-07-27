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

# webhook settings
WEBHOOK_HOST = os.getenv('HEROKU_APP_URL')
WEBHOOK_PATH = '/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = '0.0.0.0'  # or ip
WEBAPP_PORT = os.getenv('PORT', default=8000)
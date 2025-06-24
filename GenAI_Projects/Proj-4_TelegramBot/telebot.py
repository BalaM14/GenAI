import logging
from aiogram import Bot, Dispatcher, executer, types
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("telebot_key")

#configure logging
logging.basicConfig(level=logging.INFO)


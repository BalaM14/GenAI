# Databricks notebook source
!pip install -q aiogram openai==0.28 python-dotenv

# COMMAND ----------

import logging
logging.getLogger("py4j").setLevel(logging.WARNING)


# COMMAND ----------

import asyncio
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

router = Router()

@router.message(Command(commands=["start", "help"]))
async def handle_start(message: Message):
    await message.answer("Hello! I'm a Telegram Bot")

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    await main()


# COMMAND ----------


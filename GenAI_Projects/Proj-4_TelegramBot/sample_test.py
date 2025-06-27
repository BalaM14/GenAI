import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("telebot_key")

#configure logging
logging.basicConfig(level=logging.INFO)

#Initialize the bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp =Dispatcher(bot)


@dp.message_handler(commands=['start','help'])
async def commmand_start_handler(message: types.Message):
    """
    This handler recieves messages with `/start` or `/help `command
    """
    await message.reply("Hi\nI am Echo Bot!\nPowered by Bala.")

if __name__ == "__main__":
    executor.start_polling(dp,skip_updates=True)


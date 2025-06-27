import asyncio
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import openai

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")


class Reference:
    '''
    A class to store previous response from the open API
    '''
    def __init__(self) -> None:
        self.reference = ""

reference = Reference()
model_name = "gpt-3.5-turbo"

router = Router()
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

@router.message(Command(commands=["start"]))
async def start_handler(message: Message):
    '''
    This handler receives message with `/start` command
    '''
    await message.reply("Hello! I'm a Telegram Bot. \nCreated by Bala..!!!")


@router.message(Command(commands=["help"]))
async def helper(message: Message):
    '''
    This handler to display the helper menu
    '''
    help_commands = """
    Hi There, I'm chatgpt telegram bot created by Bala! Please follow these commands -
    /start - to start the conversation
    /clear - to clear the past conversation and context
    /help - to get this help menu
    """
    await message.reply(help_commands)


@router.message(Command(commands=["clear"]))
async def clear_handler(message: Message):
    '''
    This handler to clear the past conversation and context
    '''
    reference.reference = ""
    await message.reply("I've cleared the past conversations & context")


@router.message()
async def chatgpt_handler(message: Message):
    '''
    A handler to process the user's input and generate a response using the ChatGpt API.
    '''
    print(f">> USER: \n\t{message.text}")

    response = openai.ChatCompletion.create(
        model=model_name,
        messages = [
            {"role":"assistant","content":reference.reference},
            {"role":"user","content":message.text}
        ])
    
    reference.reference = response.choices[0].message.content.strip()
    print(f">> CHATGPT: \n\t{reference.reference}")
    
    await message.reply(reference.reference)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

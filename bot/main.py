from aiogram import dispatcher
import aiogram.utils.exceptions
import asyncio
import os
from aiogram import Dispatcher, Bot
from aiogram.utils.executor import start_webhook
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import types
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.dispatcher import FSMContext
from configparser import ConfigParser
from utils import set_logger
from storage.database import Store, User

logger = set_logger(__name__)

bot_config = ConfigParser()
with open('bot.ini', 'r') as file:
    print(file.read())

bot_config.read('bot.ini')
print(bot_config.sections())
print(bot_config.get('BOT', 'token'))
webhook_config = ConfigParser()
webhook_config.read('bot.ini')
webhook_config = dict(webhook_config['WEBHOOK'])
bot = Bot(token=bot_config.get('BOT', 'token'))
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
store = Store()

WEBHOOK_HOST = webhook_config.get("host", "")
WEBHOOK_PATH = webhook_config.get("path", "") + bot_config.get('BOT', 'token')
WEBHOOK_URL = webhook_config.get("url", "") + bot_config.get('BOT', 'token')
WEBAPP_HOST = webhook_config.get("app_host", "")  # or ip
WEBAPP_PORT = int(webhook_config.get("app_port", 5050))  # or ip)

@dp.message_handler(commands='start')
async def start_in_chat(message: types.Message):
    await bot.send_message(message.chat.id, "Привет Я буду отвечать за хранение и передачу ваших Социальных Кредитов")


@dp.message_handler(commands='join_to_partia')
async def join_to_party(message: types.Message):
    chat = message.chat.id
    username = message.from_user.username
    u_id = message.from_user.id
    User.create(username=username, telegram_id=u_id)
    await bot.send_message(chat, f"Партия приветсвует тебя {message.from_user.full_name}")

    return


async def on_startup(dispatcher):  # there was dispatcher in args
    logger.info(f"on start dispatcher: {dispatcher}")
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    # insert code here to run it after start


async def on_shutdown(dispatcher):
    logger.info("===== SHUTDOWN BOT ====")
    await bot.delete_webhook()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    logger.warning('Bye!')


def start_bot():
    logger.info("======= START BOT =======")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
     bot.set_my_commands(
        [
            types.BotCommand(command="/start", description="Создать партию!"),
            types.BotCommand(command="/join_to_partia", description="Вступить в партию!"),
        ]
    )
    )
    print(f">>> {WEBAPP_PORT}")
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )


if __name__ == "__main__":
    start_bot()

import os
import asyncio
import logging
from aiogram import Dispatcher, Bot
from aiogram.utils.executor import start_webhook
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import types
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.dispatcher import FSMContext
# from configparser import ConfigParser
from utils import set_logger
from storage.database import Store, User
from bot_config import BotConf, WebHookConf

logger = set_logger(__name__)

bot = Bot(token=BotConf.token)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

logging.basicConfig(level=logging.INFO)

store = Store()

WEBHOOK_HOST = WebHookConf.host
WEBHOOK_PATH = WebHookConf.path + BotConf.token
WEBHOOK_URL = WebHookConf.url + BotConf.token
WEBAPP_HOST = WebHookConf.app_host
WEBAPP_PORT = int(os.getenv("PORT", 5050))


@dp.message_handler(commands='start')
async def start_in_chat(message: types.Message):
    await bot.send_message(message.chat.id, "Привет Я буду отвечать за хранение и передачу ваших Социальных Кредитов")


@dp.message_handler(commands='join_to_partia')
async def join_to_party(message: types.Message):
    chat = message.chat.id
    username = message.from_user.username
    u_id = message.from_user.id
    User.create(username=username, telegram_id=u_id)
    await bot.send_message(chat, f"Партия приветсвует тебя {message.from_user.full_name}, "
                                 f"за вступление тебе начислено 100 кредитов")

    return


@dp.message_handler(commands='check_account')
async def check_account(message: types.Message):
    requester = User.filter(telegram_id=message.from_user.id)
    print(requester)
    if requester:
        await bot.send_message(message.chat.id,
                               f"Хей {message.from_user.full_name} на твоём счету {requester.social_credits}")
    else:
        await bot.send_message(message.chat.id, "Я вас не знаю, сначала зарегестрирйтесь /join_to_partia")


async def on_startup(dispatcher):  # there was dispatcher in args
    logger.info(f"on start dispatcher: {dispatcher}")
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=False)
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
    store.create_tables([User, ])

    loop.run_until_complete(
        bot.set_my_commands(
            [
                types.BotCommand(command="/start", description="Создать партию!"),
                types.BotCommand(command="/join_to_partia", description="Вступить в партию!"),
                types.BotCommand(command="/check_account", description="Проверить свой счет!"),

            ]
        )
    )
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

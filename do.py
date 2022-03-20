''' Run a function by ado <func_name> '''


def set_hook():
    import asyncio
    import bot_config
    from aiogram import Bot
    bot = Bot(token=bot_config.BotConf.token)

    async def hook_set():
        if not bot_config.WebHookConf.heroku_app:
            print('You have forgot to set HEROKU_APP_NAME')
            quit()
        await bot.set_webhook(bot_config.WebHookConf.url)
        print(await bot.get_webhook_info())

    asyncio.run(hook_set())
    bot.close()


def start():
    from bot.main import start_bot
    start_bot()

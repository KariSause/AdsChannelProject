from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import client, admin
from data_base.db import init_db
import asyncio, config
from auto_posting import auto_posting

bot = Bot(token=config.TOKEN)

dp = Dispatcher(storage=MemoryStorage())


def register_routers(dp):
    dp.include_router(client.router)
    dp.include_router(admin.router)


async def on_startup(dp):
    print("Bot is starting...")
    await init_db()


async def main():
    register_routers(dp)
    await on_startup(dp)
    print('Polling started...')
    asyncio.create_task(auto_posting(bot))
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())

import os
import datetime
import requests
import random
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

bot = Bot(token='5925427456:AAG-USzKmAdv_tCk-8cIVrfxuDPBbeNkgAw')
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply('Hello! Type a "random" for random car')


@dp.message_handler(commands=["random"])
async def get_car(message: types.Message):
    random_car = random.randint(1, 2038)
    await bot.send_video(message.chat.id, f'https://awesomecars.neocities.org/ver2/{random_car}.mp4')
    await bot.send_video_note(message.chat.id, f'https://awesomecars.neocities.org/ver2/{random_car}.mp4')
    await bot.send_voice(message.chat.id, f'https://awesomecars.neocities.org/ver2/{random_car}.mp4')


async def setup_bot_commands(_):
    bot_commands = [
        types.BotCommand(command="/search", description="Get search for car"),
        types.BotCommand(command="/random", description="Get random car")
    ]
    await bot.set_my_commands(commands=bot_commands)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=setup_bot_commands)

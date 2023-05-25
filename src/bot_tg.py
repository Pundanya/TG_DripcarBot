from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token='5925427456:AAG-USzKmAdv_tCk-8cIVrfxuDPBbeNkgAw')
dp = Dispatcher(bot, storage=MemoryStorage())


def get_dp():
    return dp


def get_bot():
    return bot

import os
import requests
import converter
import random
import json
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

bot = Bot(token='5925427456:AAG-USzKmAdv_tCk-8cIVrfxuDPBbeNkgAw')
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply('Hello! Type name of car to search or /random to get random car')


@dp.message_handler(commands=["random"])
async def get_car(message: types.Message):
    random_car = random.randint(1, 2038)
    with open("data/all_cars.json") as file:
        all_cars = json.load(file)
        car_name = all_cars[f"{random_car}"]
        await send_car(random_car, message.chat.id, car_name)


@dp.message_handler()
async def search(message: types.Message):
    car_to_search = message.text.lower()
    if car_to_search == "древние русы":
        await send_car(0, message.chat.id, "древние русы")
        return

    with open("data/all_cars.json") as file:
        all_cars = json.load(file)
        is_exist = False
        for car_id, car_name in all_cars.items():
            if car_to_search in car_name.lower():
                is_exist = True
                await send_car(car_id, message.chat.id, car_name)
        if not is_exist:
            await bot.send_message(message.chat.id, "Car doesn't exist. Try again")



async def send_car(car_id, chat_id, car_name):
    await bot.send_message(chat_id, f"Here is your car:\n{car_id} – {car_name}")

    if car_id == 0:
        file_path = "data/output/rusi.mp4"
    else:
        file_path = f"https://awesomecars.neocities.org/ver2/{car_id}.mp4"

    # ======= Video send =======
    # input_file = types.InputFile(file_path)
    # await bot.send_video(chat_id, input_file)

    # ======= Video note send =======
    converter.resize_mp4(file_path)
    input_file_mp4 = types.InputFile('data/output/output.mp4')
    await bot.send_video_note(chat_id, input_file_mp4)

    # ======= Voice send =======
    # converter.convert_mp4_to_mp3(file_path)
    # input_file_mp3 = types.InputFile('data/output/output.mp3')
    # await bot.send_voice(chat_id, input_file_mp3)


async def setup_bot_commands(_):
    bot_commands = [
        types.BotCommand(command="/random", description="Get random car")
    ]
    await bot.set_my_commands(commands=bot_commands)


# Update all_cars.json from search awesomecars
def update_all_car_json_data():
    search_data = requests.get("https://awesomecars.neocities.org/search.js").text
    search_data = search_data[search_data.find("[") + 1: search_data.find("]")]
    search_data = search_data.replace('"', "")

    all_cars = search_data.split(",\n")
    all_cars_json_data = {}

    with open("data/all_cars.json", "w") as file:
        for car in all_cars:
            car_split = car.split(" - ")
            car_id = car_split[0].lstrip('#').replace(",", "")
            car_name = " - ".join(car_split[1:])
            all_cars_json_data[f"{car_id}"] = car_name
        json.dump(all_cars_json_data, file)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=setup_bot_commands)

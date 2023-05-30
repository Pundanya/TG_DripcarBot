import bot_tg

import random
import cars_controller
import converter
import markups
import os.path

from aiogram import types


bot = bot_tg.get_bot()
all_cars = cars_controller.get_all_cars()


async def get_random_car(message):
    random_car_id = random.randint(0, cars_controller.get_len())
    car_name = cars_controller.get_car_name(random_car_id)
    car_path = cars_controller.get_car_mp4_path_by_id(random_car_id)
    found_cars = [{
        "id": random_car_id,
        "name": car_name,
        "path": car_path
    }]
    return found_cars


async def get_cars_by_search(car_to_search):
    found_cars = []

    for car_id, car_name in all_cars.items():
        if car_to_search in car_name.lower():
            car_path = cars_controller.get_car_mp4_path_by_id(car_id)
            found_cars.append({
                "id": car_id,
                "name": car_name,
                "path": car_path
            })

    return found_cars


async def get_cars_by_id(car_id_to_search):
    car_name = all_cars[car_id_to_search]
    car_path = cars_controller.get_car_mp4_path_by_id(car_id_to_search)
    found_cars = [{
        "id": car_id_to_search,
        "name": car_name,
        "path": car_path
    }]
    return found_cars


async def send_cars(cars_to_send, chat_id):
    for car in cars_to_send:
        await bot.send_message(chat_id, f'Here is your car:\n{car["name"]}')

        # --- Video note send ---
        input_file_mp4 = types.InputFile(car["path"])
        inline_voice_menu = markups.get_inline_voice_menu(car["id"])
        await bot.send_video_note(chat_id, input_file_mp4, reply_markup=inline_voice_menu)


async def send_voice_version(car_to_send, chat_id):
    car_mp3_path = cars_controller.get_car_mp3_path_by_id(car_to_send["id"])

    # --- Voice send ---
    if not os.path.exists(car_mp3_path):
        converter.convert_car_mp4_to_mp3(car_to_send["path"], car_mp3_path)
    input_file_mp3 = types.InputFile(car_mp3_path)
    await bot.send_voice(chat_id, input_file_mp3)

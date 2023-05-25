import bot_tg

import random
import cars_controller
import converter

from aiogram import types

bot = bot_tg.get_bot()
all_cars = cars_controller.get_all_cars()


async def send_random_car(message):
    random_car_id = random.randint(1, cars_controller.get_len() + 1)
    car_name = cars_controller.get_car_name(random_car_id)
    car_path = cars_controller.get_car_path_by_id(random_car_id)
    found_cars = [{
        "id": random_car_id,
        "name": car_name,
        "path": car_path
    }]
    await send_cars(found_cars, message.chat.id)


async def get_cars_by_search(car_to_search):
    found_cars = []

    # secret ancient rus video
    if car_to_search == "древние русы":
        car_path = cars_controller.get_secret_car_path()
        car_name = "древние русы"
        found_cars.append({
                "id": 0,
                "name": car_name,
                "path": car_path
            })
        return found_cars

    for car_id, car_name in all_cars.items():
        if car_to_search in car_name.lower():
            car_path = cars_controller.get_car_path_by_id(car_id)
            found_cars.append({
                "id": car_id,
                "name": car_name,
                "path": car_path
            })

    return found_cars


async def get_cars_by_id(car_id_to_search):
    for car_id, car_name in all_cars.items():
        if car_id_to_search in car_id:
            car_path = cars_controller.get_car_path_by_id(car_id)
            found_cars = [{
                "id": car_id,
                "name": car_name,
                "path": car_path
            }]
            return found_cars


async def send_cars(cars_to_send, chat_id):
    for car in cars_to_send:
        file_path = car["path"]
        car_name = car["name"]
        await bot.send_message(chat_id, f"Here is your car:\n{car_name}")
        loading_message = await bot.send_message(chat_id, "🚦 Loading...")

        # --- Video send ---
        # input_file = types.InputFile(file_path)
        # await bot.send_video(chat_id, input_file)

        # --- Video note send ---
        converter.resize_mp4(file_path)
        await bot.delete_message(chat_id, loading_message.message_id)
        input_file_mp4 = types.InputFile('./data/output/output.mp4')
        await bot.send_video_note(chat_id, input_file_mp4)

        # --- Voice send ---
        # converter.convert_mp4_to_mp3(file_path)
        # input_file_mp3 = types.InputFile('data/output/output.mp3')
        # await bot.send_voice(chat_id, input_file_mp3)



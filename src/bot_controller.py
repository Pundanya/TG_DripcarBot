import bot_tg

import random
import cars_controller
import converter
import markups
import os.path
import re

from aiogram import types

LOGO_FOLDER_PATH = "data/constructor/images"
AUDIO_FOLDER_PATH = "data/constructor/audios"

MAX_AUDIO_SIZE_MB = 3

bot = bot_tg.get_bot()
all_cars = cars_controller.get_all_cars()


async def download_logo_image(message):
    logo_image = message.photo[-1]

    chat_id = message.chat.id
    logo_image_path = f"{LOGO_FOLDER_PATH}/logo_{chat_id}.jpg"
    await logo_image.download(destination_file=logo_image_path)


async def process_audio_and_video(message):
    if message.audio:
        file_id = message.audio.file_id
        file_size_mb = message.audio.file_size / (1024 * 1024)
    else:
        file_id = message.voice.file_id
        file_size_mb = message.voice.file_size / (1024 * 1024)

    if file_size_mb > MAX_AUDIO_SIZE_MB:
        return None

    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_extension = re.search(r'\.(\w+)$', file_path).group(1)

    chat_id = message.chat.id
    audio_path = f"{AUDIO_FOLDER_PATH}/audio_{chat_id}.{file_extension}"

    await bot.download_file(file_path, audio_path)

    logo_path_by_id = f"{LOGO_FOLDER_PATH}/logo_{chat_id}.jpg"
    video_path = converter.create_car_video_from_logo_and_audio(logo_path_by_id, audio_path, chat_id)

    result_car_mp4 = types.InputFile(video_path)
    return result_car_mp4


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

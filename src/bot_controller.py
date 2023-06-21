import bot_tg

import random
import cars_controller
import converter
import markups
import os.path
import os
import re
import db_controller
import s3_client

from aiogram import types

LOGO_FOLDER_PATH = "data/constructor/images"
AUDIO_FOLDER_PATH = "data/constructor/audios"
MUSIC_FOLDER_PATH = "data/constructor/audios/music"
MUSIC_SAMPLES_PATH = "data/constructor/template/music"

MAX_AUDIO_SIZE_MB = 3

bot = bot_tg.get_bot()
all_cars = cars_controller.get_all_cars()


async def download_logo_image(message):
    logo_image = message.photo[-1]

    chat_id = message.chat.id
    logo_image_path = f"{LOGO_FOLDER_PATH}/logo_{chat_id}.jpg"
    await logo_image.download(destination_file=logo_image_path)


async def create_audio(message, audio_type):
    if message.audio:
        file_id = message.audio.file_id
        file_size_mb = message.audio.file_size / (1024 * 1024)
    else:
        file_id = message.voice.file_id
        file_size_mb = message.voice.file_size / (1024 * 1024)

    if file_size_mb > MAX_AUDIO_SIZE_MB:
        return False

    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_extension = re.search(r'\.(\w+)$', file_path).group(1)

    chat_id = message.chat.id

    audio_path = f"{AUDIO_FOLDER_PATH}/{audio_type}_{chat_id}."

    await bot.download_file(file_path, audio_path + file_extension)
    if file_extension != "mp3":
        converter.convert_to_mp3(audio_path, file_extension)
        os.remove(audio_path + file_extension)
    return audio_path + "mp3"


async def normalize_audio(message, audio_type):
    chat_id = message.chat.id
    audio_path = f"{AUDIO_FOLDER_PATH}/{audio_type}_{chat_id}.mp3"
    temp_audio_path = f"{AUDIO_FOLDER_PATH}/temp_normalize_{chat_id}.mp3"
    if os.path.exists(audio_path):
        await converter.normalize_audio(audio_path, temp_audio_path)
        os.remove(audio_path)
        os.rename(temp_audio_path, audio_path)


async def send_samples(chat_id):
    samples = []

    with os.scandir(MUSIC_SAMPLES_PATH) as entries:
        for entry in entries:
            if entry.is_file():
                samples.append(entry.name)

    for sample in samples:
        sample_file = types.InputFile(MUSIC_SAMPLES_PATH + "/" + sample)
        inline_select_menu = markups.get_inline_select_menu(sample)
        await bot.send_audio(chat_id, sample_file, reply_markup=inline_select_menu)


async def audio_mix(callback, input_file_2):
    input_file_1 = await get_audio_path(callback)
    output_file = f"{AUDIO_FOLDER_PATH}/temp_{callback.from_user.id}.mp3"
    await converter.audio_mix(input_file_1, input_file_2, output_file)
    os.remove(input_file_1)
    os.rename(output_file, input_file_1)


async def create_video(chat_id, audio_path):
    logo_path_by_id = f"{LOGO_FOLDER_PATH}/logo_{chat_id}.jpg"
    video_path = converter.create_car_video_from_logo_and_audio(logo_path_by_id, audio_path, chat_id)
    result_car_mp4 = types.InputFile(video_path)

    return result_car_mp4


async def get_random_car(message):
    last_id = await db_controller.get_last_id()
    car = None
    while car is None:
        random_id = random.randint(1, last_id + 1)
        car = await db_controller.get_car_by_id(random_id)
    return car


async def delete_car(car):
    car_mp4_path = f"data/temp/cars_mp4/{car.id}.mp4"
    car_mp3_path = f"data/temp/cars_mp3/{car.id}.mp3"
    if os.path.exists(car_mp4_path):
        os.remove(car_mp4_path)
    if os.path.exists(car_mp3_path):
        os.remove(car_mp3_path)


async def delete_constructor_src(tg_id):
    all_paths = [
        car_mp4_path := f"data/temp/cars_mp4/car_{tg_id}.mp4",
        car_mp3_path := f"data/temp/cars_mp3/car_{tg_id}.mp3",
        audio_path := f"data/constructor/audios/audio_{tg_id}.oga",
        audio_path_v2 := f"data/constructor/audios/audio_{tg_id}.mp3",
        logo_path := f"data/constructor/images/logo_{tg_id}.jpg",
        image_path := f"data/constructor/result/car_images/result_{tg_id}.jpg",
        result_path := f"data/constructor/result/car_video/car_{tg_id}.mp4",
        audio_cut_2 := f"{AUDIO_FOLDER_PATH}/audio_modified_{tg_id}.mp3",
        audio_cut_1 := f"{AUDIO_FOLDER_PATH}/audio_cut1_{tg_id}.mp3"]
    for path in all_paths:
        if os.path.exists(path):
            os.remove(path)


async def start_cut_audio(message: types.Message):
    audio_path = f"{AUDIO_FOLDER_PATH}/audio_{message.from_user.id}.mp3"
    output_path = f"{AUDIO_FOLDER_PATH}/audio_cut1_{message.from_user.id}.mp3"
    converter.cut_start_mp3(audio_path, output_path, message.text)


async def end_cut_audio(message: types.Message):
    audio_path = f"{AUDIO_FOLDER_PATH}/audio_cut1_{message.from_user.id}.mp3"
    output_path = f"{AUDIO_FOLDER_PATH}/audio_modified_{message.from_user.id}.mp3"
    converter.cut_end_mp3(audio_path, output_path, int(message.text))


async def get_audio_path(message):
    audio_path = f"{AUDIO_FOLDER_PATH}/audio_modified_{message.from_user.id}.mp3"
    if not os.path.exists(audio_path):
        audio_path = f"{AUDIO_FOLDER_PATH}/audio_{message.from_user.id}.mp3"

    return audio_path


async def send_car(car, chat_id):

    await bot.send_message(chat_id, f'Here is your car:\n{car.name}')

    # --- Video note send ---
    await s3_client.download_car_mp4(car.id)
    car_path = f"data/temp/cars_mp4/{car.id}.mp4"
    input_file_mp4 = types.InputFile(car_path)
    inline_voice_menu = markups.get_inline_voice_menu(car.id)
    await bot.send_video_note(chat_id, input_file_mp4, reply_markup=inline_voice_menu)
    await db_controller.add_views(car.id)
    await delete_car(car)


async def send_voice_version(car, chat_id):
    car_mp3_path = f"data/temp/cars_mp3/{car.id}.mp3"
    car_mp4_path = f"data/temp/cars_mp4/{car.id}.mp4"
    if not await s3_client.check_mp3(car.id):
        await s3_client.download_car_mp4(car.id)
        converter.convert_car_mp4_to_mp3(car_mp4_path, car_mp3_path)
        await s3_client.upload_car_mp3(car.id, car.id)

    # --- Voice send ---
    await s3_client.download_car_mp3(car.id)
    input_file_mp3 = types.InputFile(car_mp3_path)
    await bot.send_voice(chat_id, input_file_mp3)
    await delete_car(car)

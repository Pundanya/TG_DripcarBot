import bot_tg

import random
import converter
import markups
import os.path
import os
import re
import db_controller
import s3_client
import shutil

from aiogram import types

LOGO_FOLDER_PATH = "data/constructor/images"
AUDIO_FOLDER_PATH = "data/constructor/audios"
MUSIC_FOLDER_PATH = "data/constructor/audios/music"
MUSIC_SAMPLES_PATH = "data/constructor/template/music"
TEMP_CARS_MP4_PATH = "data/temp/cars_mp4"
TEMP_CARS_MP3_PATH = "data/temp/cars_mp3"
CNSTR_RESULT_PATH = "data/constructor/result/car_video"

IS_AUDIO = "audio"
IS_MUSIC = "music"

MAX_AUDIO_SIZE_MB = 3

bot = bot_tg.get_bot()


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


async def increase_volume(message, audio_type):
    chat_id = message.chat.id
    if audio_type == IS_AUDIO:
        audio_path = await get_audio_path(message.from_user.id)
    else:
        audio_path = await get_music_path(message.from_user.id)
    mod_audio_path = f"{AUDIO_FOLDER_PATH}/{audio_type}_modified_{chat_id}.mp3"
    temp_audio_path = f"{AUDIO_FOLDER_PATH}/{audio_type}_temp_{chat_id}.mp3"
    if os.path.exists(audio_path):
        converter.increase_volume(audio_path, temp_audio_path)
        if os.path.exists(mod_audio_path):
            os.remove(mod_audio_path)
        os.rename(temp_audio_path, mod_audio_path)


async def decrease_volume(message, audio_type):
    chat_id = message.chat.id
    if audio_type == IS_AUDIO:
        audio_path = await get_audio_path(message.from_user.id)
    else:
        audio_path = await get_music_path(message.from_user.id)
    mod_audio_path = f"{AUDIO_FOLDER_PATH}/{audio_type}_modified_{chat_id}.mp3"
    temp_audio_path = f"{AUDIO_FOLDER_PATH}/{audio_type}_temp_{chat_id}.mp3"
    if os.path.exists(audio_path):
        await converter.decrease_volume(audio_path, temp_audio_path)
        if os.path.exists(mod_audio_path):
            os.remove(mod_audio_path)
        os.rename(temp_audio_path, mod_audio_path)


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


async def audio_mix(chat_id):
    audio_path = await get_audio_path(chat_id)
    drip_path = await get_drip_path(chat_id)
    music_path = await get_music_path(chat_id)
    if not os.path.exists(music_path):
        os.remove(drip_path)
        shutil.copy(audio_path, drip_path)
    else:
        converter.audio_mix(audio_path, music_path, drip_path)


async def create_video(chat_id):
    drip_path = await get_drip_path(chat_id)
    logo_path_by_id = f"{LOGO_FOLDER_PATH}/logo_{chat_id}.jpg"
    video_path = converter.create_car_video_from_logo_and_audio(logo_path_by_id, drip_path, chat_id)
    result_car_mp4 = types.InputFile(video_path)
    return result_car_mp4


async def reset_audio(message):
    audio_path_origin = await get_audio_path(message.from_user.id, origin=True)
    audio_path = await get_audio_path(message.from_user.id)
    if os.path.exists(audio_path):
        os.remove(audio_path)
        shutil.copy(audio_path_origin, audio_path)


async def delete_music(chat_id):
    music_path = f"{AUDIO_FOLDER_PATH}/music_modified_{chat_id}.mp3"
    music_path2 = f"{AUDIO_FOLDER_PATH}/music_{chat_id}.mp3"
    deleted = False
    if os.path.exists(music_path2):
        os.remove(music_path2)
        deleted = True
    if os.path.exists(music_path):
        os.remove(music_path)
        deleted = True
    return deleted


async def delete_audio(chat_id):
    audio_path = f"{AUDIO_FOLDER_PATH}/audio_modified_{chat_id}.mp3"
    audio_path2 = f"{AUDIO_FOLDER_PATH}/audio_{chat_id}.mp3"
    deleted = False
    if os.path.exists(audio_path2):
        os.remove(audio_path2)
        deleted = True
    if os.path.exists(audio_path):
        os.remove(audio_path)
        deleted = True
    return deleted


async def check_music(chat_id):
    music_path = await get_music_path(chat_id)
    exist = False
    if os.path.exists(music_path):
        exist = True
    return exist


async def check_drip(chat_id):
    drip_path = await get_drip_path(chat_id)
    exist = False
    if os.path.exists(drip_path):
        exist = True
    return exist


async def check_audio(chat_id):
    audio_path = await get_audio_path(chat_id)
    exist = False
    if os.path.exists(audio_path):
        exist = True
    return exist


async def reset_music(message):
    music_path_origin = await get_music_path(message.from_user.id, origin=True)
    music_path = await get_music_path(message.from_user.id)
    if os.path.exists(music_path):
        os.remove(music_path)
        shutil.copy(music_path_origin, music_path)


async def sample_callback(callback_query):
    src_file = f"{MUSIC_SAMPLES_PATH}/{callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_MUSIC_SAMPLE)}"
    audio_path = await get_music_path(callback_query.from_user.id)
    if os.path.exists(audio_path):
        os.remove(audio_path)
    shutil.copy(src_file, audio_path)


async def get_random_car():
    last_id = await db_controller.get_last_id()
    car = None
    while car is None:
        random_id = random.randint(1, last_id + 1)
        car = await db_controller.get_car_by_id(random_id)
    return car


async def delete_car_files(car):
    car_mp4_path = f"data/temp/cars_mp4/{car.id}.mp4"
    car_mp3_path = f"data/temp/cars_mp3/{car.id}.mp3"
    if os.path.exists(car_mp4_path):
        os.remove(car_mp4_path)
    if os.path.exists(car_mp3_path):
        os.remove(car_mp3_path)


async def delete_car(car_id):
    await db_controller.delete_car(car_id)
    await s3_client.delete_car_mp4_and_mp3(car_id)


async def delete_cnstr_src(tg_id):
    all_paths = [
        car_mp4_path := f"data/temp/cars_mp4/car_{tg_id}.mp4",
        car_mp3_path := f"data/temp/cars_mp3/car_{tg_id}.mp3",
        audio_path := f"data/constructor/audios/audio_{tg_id}.oga",
        audio_path_v2 := f"data/constructor/audios/audio_{tg_id}.mp3",
        logo_path := f"data/constructor/images/logo_{tg_id}.jpg",
        image_path := f"data/constructor/result/car_images/result_{tg_id}.jpg",
        result_path := f"data/constructor/result/car_video/car_{tg_id}.mp4",
        audio_cut_2 := f"{AUDIO_FOLDER_PATH}/audio_modified_{tg_id}.mp3",
        audio_cut_1 := f"{AUDIO_FOLDER_PATH}/audio_cut1_{tg_id}.mp3",
        music_ := f"{AUDIO_FOLDER_PATH}/music_{tg_id}.mp3",
        music_cut_1 := f"{AUDIO_FOLDER_PATH}/music_cut1_{tg_id}.mp3",
        music := f"data/constructor/audios/music/music_{tg_id}.mp3",
        music_2 := f"{AUDIO_FOLDER_PATH}/music_modified_{tg_id}.mp3",
        drip_path := f"{AUDIO_FOLDER_PATH}/drip_{tg_id}.mp3"]
    for path in all_paths:
        if os.path.exists(path):
            os.remove(path)


def cnstr_src_clear():
    folders = [
        "data/constructor/audios",
        "data/constructor/audios/music",
        "data/constructor/images",
        "data/constructor/result/car_images",
        "data/constructor/result/car_video",
        "data/temp/cars_mp3",
        "data/temp/cars_mp4"
    ]
    for folder in folders:
        if os.path.exists(folder):
            file_list = os.listdir(folder)

            for file_name in file_list:
                file_path = os.path.join(folder, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)


async def send_my_car(car, chat_id):
    # --- Video note send ---
    await s3_client.download_car_mp4(car.id)
    car_path = f"data/temp/cars_mp4/{car.id}.mp4"
    input_file_mp4 = types.InputFile(car_path)
    inline_remove_menu = markups.get_inline_remove_menu(car.id)
    await bot.send_video_note(chat_id, input_file_mp4, reply_markup=inline_remove_menu)
    await delete_car_files(car)


async def start_cut_audio(message: types.Message, audio_type):
    audio_path = f"{AUDIO_FOLDER_PATH}/{audio_type}_{message.from_user.id}.mp3"
    output_path = f"{AUDIO_FOLDER_PATH}/{audio_type}_cut1_{message.from_user.id}.mp3"
    converter.cut_start_mp3(audio_path, output_path, message.text)


async def end_cut_audio(message: types.Message, audio_type):
    audio_path = f"{AUDIO_FOLDER_PATH}/{audio_type}_cut1_{message.from_user.id}.mp3"
    output_path = f"{AUDIO_FOLDER_PATH}/{audio_type}_modified_{message.from_user.id}.mp3"
    converter.cut_end_mp3(audio_path, output_path, int(message.text))


async def is_seconds(time):
    if time.isdecimal() and int(time) > 0:
        return True
    return False


async def cnstr_add_car(message):
    new_car = await db_controller.add_car(message.text, message.from_user.id, "tg_constructor", message.from_user.id)
    car_name = f"car_{message.from_user.id}"
    await s3_client.upload_car_mp4(car_name, new_car.id)
    await delete_cnstr_src(message.from_user.id)


async def get_audio_path(chat_id, origin=False):
    audio_path = f"{AUDIO_FOLDER_PATH}/audio_modified_{chat_id}.mp3"
    if not os.path.exists(audio_path) or origin:
        audio_path = f"{AUDIO_FOLDER_PATH}/audio_{chat_id}.mp3"

    return audio_path


async def get_music_path(chat_id, origin=False):
    audio_path = f"{AUDIO_FOLDER_PATH}/music_modified_{chat_id}.mp3"
    if not os.path.exists(audio_path) or origin:
        audio_path = f"{AUDIO_FOLDER_PATH}/music_{chat_id}.mp3"

    return audio_path


async def get_drip_path(chat_id):
    drip_path = f"{AUDIO_FOLDER_PATH}/drip_{chat_id}.mp3"
    if not os.path.exists(drip_path):
        audio_path = f"{AUDIO_FOLDER_PATH}/audio_{chat_id}.mp3"
        shutil.copy(audio_path, drip_path)
    return drip_path


async def time_match_d2(time):
    pattern = r'^\d{2}:\d{2}$'
    match = re.match(pattern, time)
    if match:
        return True
    return False


async def send_car(car, chat_id):
    # --- Video note send ---
    await s3_client.download_car_mp4(car.id)
    car_path = f"{TEMP_CARS_MP4_PATH}/{car.id}.mp4"
    input_file_mp4 = types.InputFile(car_path)
    inline_voice_menu = markups.get_inline_voice_menu(car.id)
    await bot.send_video_note(chat_id, input_file_mp4, reply_markup=inline_voice_menu)
    await db_controller.add_views(car.id)
    await delete_car_files(car)


async def get_top_10_likes_cars():
    cars_stats = await db_controller.get_top_10_stats_by_likes()
    cars = []
    for car_stat in cars_stats:
        cars.append(car_stat.car)
    return cars


async def send_voice_version(callback_query):
    car = await db_controller.get_car_by_id(callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_AUDIO))
    car_mp3_path = f"{TEMP_CARS_MP3_PATH}/{car.id}.mp3"
    car_mp4_path = f"{TEMP_CARS_MP4_PATH}/{car.id}.mp4"
    if not await s3_client.check_mp3(car.id):
        await s3_client.download_car_mp4(car.id)
        converter.convert_car_mp4_to_mp3(car_mp4_path, car_mp3_path)
        await s3_client.upload_car_mp3(car.id, car.id)

    # --- Voice send ---
    await s3_client.download_car_mp3(car.id)
    input_file_mp3 = types.InputFile(car_mp3_path)
    await bot.send_voice(callback_query.from_user.id, input_file_mp3)
    await delete_car_files(car)

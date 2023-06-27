import bot_tg
import bot_controller
import markups
import db_controller
import s3_client
import re
import os
import shutil


from aiogram import types
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

START_MESSAGE = 'Hello! Drip car bot at your service'
MAIN_MENU_MESSAGE = 'Press "🔍 Car search" to search the car\nPress "🎲 Random car" to get random car'
SEARCH_HINT_MESSAGE = 'To search enter car name into chat'
INFO_MESSAGE = 'Constructor version 3. Now your cars can be searched! Sound can be cropped and added music on background.'
CONSTRUCTOR_CAR_CHECK_MESSAGE = "Enter the name of the car to search for similar ones in the database"
CONSTRUCTOR_FOUND_CARS_CHECK_MESSAGE = "Here are some similar cars. Check if your car is already in the database"
CONSTRUCTOR_CONTINUE_REPEAT_ASK_MESSAGE = f'If your car does not already exist press {markups.BUTTON_CONTINUE_TEXT}.' \
                                 f'\nIf you want to re-search the car press {markups.BUTTON_REPEAT_TEXT}.'
CONSTRUCTOR_CAR_ACCEPT_MESSAGE = f'If you are satisfied with your car, click {markups.BUTTON_CONTINUE_TEXT} to add to the database.' \
                                 f'\nIf you want to re-create the car press {markups.BUTTON_REPEAT_TEXT}.'
CONSTRUCTOR_NAME_ASK_MESSAGE = "Please send car name"
CONSTRUCTOR_LOGO_ASK_MESSAGE = "Please send logo image"
CONSTRUCTOR_AUDIO_ASK_MESSAGE = "Please send audio"
CONSTRUCTOR_SUCCESS_MESSAGE = "Success! Your car added"
CONSTRUCTOR_AUDIO_CUT_START_TIME_ASK_MESSAGE = "Please send start time." \
                                               "\nFormat: " \
                                               "\n\nmm:ss\n" \
                                               "\nExample: 01:23"
CONSTRUCTOR_AUDIO_CUT_END_TIME_ASK_MESSAGE = "Please send duration time is seconds. Maximum 20 seconds" \
                                             "\nFormat:" \
                                             "\n\nss\n" \
                                             "\nExample: 15"
CONSTRUCTOR_YOUR_AUDIO_MESSAGE = "Your audio:"
CONSTRUCTOR_MUSIC_ASK_MESSAGE = "Please send music or choose from samples"
CONSTRUCTOR_YOUR_MUSIC_MESSAGE = "Your music:"
CONSTRUCTOR_MUSIC_SAMPLES_MESSAGE = "You can choose from this samples:"

LOADING_MESSAGE = "🚦 Loading..."
SUCCESS_MESSAGE = "SUCCESS!"

ERROR_NOT_WORKING_MESSAGE = 'Not working yet'
ERROR_CAR_NOT_EXIST_MESSAGE = "Car doesn't exist. Try again!"
ERROR_AUDIO_TOO_BIG = f"Audio too big. Maximum size: {bot_controller.MAX_AUDIO_SIZE_MB} MB."
ERROR = "Error"
ERROR_WRONG_STATE = "Button not work. Wrong state"

dp = bot_tg.get_dp()
bot = bot_tg.get_bot()


class States(StatesGroup):
    searching = State()
    my_cars = State()
    car_name_edit = State()
    car_delete_confirmation = State()
    waiting_for_search_name = State()
    waiting_for_logo = State()
    waiting_for_audio = State()
    drip_audio_edit = State()
    audio_edit = State()
    audio_cut_start = State()
    audio_cut_end = State()
    audio_waiting_for_music = State()
    music_samples = State()
    music_edit = State()
    music_cut_start = State()
    music_cut_end = State()
    waiting_for_time = State()
    waiting_for_accept = State()
    waiting_for_name = State()
    subscription_edit = State()


@dp.errors_handler()
async def error_handler(update: types.Update, exception: Exception):
    print(f'{ERROR}: {exception}')


# --- Command START ---
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user = await db_controller.create_user(message)
    await message.reply(f'Привет, {user.name}! Ты зарегистрирован в базе данных.')
    await bot.send_message(message.chat.id, START_MESSAGE, reply_markup=markups.main_menu)


@dp.message_handler(commands=["init"])
async def start_command(message: types.Message):
    await db_controller.init_models()
    await bot.send_message(message.chat.id, SUCCESS_MESSAGE + " db init", reply_markup=markups.main_menu)


@dp.message_handler(commands=["adminnerus"])
async def start_command(message: types.Message):
    await db_controller.give_admin_role(message.from_user.id)
    await bot.send_message(message.chat.id, SUCCESS_MESSAGE + " Now u r an admin", reply_markup=markups.main_menu)


@dp.message_handler(lambda c: c.text == markups.BUTTON_MAIN_MENU_TEXT, state="*")
async def main_menu_button(message: types.Message, state: FSMContext):
    await bot_controller.delete_constructor_src(message.chat.id)
    await state.finish()
    await bot.send_message(message.chat.id, MAIN_MENU_MESSAGE, reply_markup=markups.main_menu)


# --- Main message HANDLER ---
@dp.message_handler()
async def input_handler(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_RANDOM_TEXT:
        car = await bot_controller.get_random_car(message)
        await bot_controller.send_car(car, message.chat.id)
        await bot_controller.delete_car(car)

    elif message.text == markups.BUTTON_SEARCH_TEXT:
        await bot.send_message(message.chat.id, SEARCH_HINT_MESSAGE, reply_markup=markups.search_menu)
        await state.set_state(States.searching)

    # elif message.text == markups.BUTTON_OTHER_TEXT:
    #     await bot.send_message(message.chat.id, INFO_MESSAGE, reply_markup=markups.other_menu)

    elif message.text == markups.BUTTON_CONSTRUCTOR_TEXT:
        await state.set_state(States.waiting_for_search_name)
        await bot.send_message(message.chat.id, CONSTRUCTOR_CAR_CHECK_MESSAGE, reply_markup=markups.constructor_menu)

    elif message.text == markups.BUTTON_MY_CARS_TEXT:
        await state.set_state(States.my_cars)
        await bot.send_message(message.chat.id, "You can delete your cars here. Select car to edit",
                               reply_markup=markups.my_cars_menu)
        found_cars = await db_controller.get_cars_by_tg_id(message.from_user.id)
        if not found_cars:
            await bot.send_message(message.chat.id, "You doesn't have cars")
        else:
            inline_search_menu = await markups.get_inline_my_cars_menu(found_cars, message.text.lower())
            message_found_cars = generate_message_found_cars(found_cars)
            await bot.send_message(message.chat.id, message_found_cars, reply_markup=inline_search_menu)

    elif message.text == markups.BUTTON_TOP_TEXT:
        found_cars = await bot_controller.get_top_10_likes()
        inline_search_menu = await markups.get_inline_search_menu(found_cars, message.text.lower())
        message_found_cars = generate_message_found_cars(found_cars)
        await bot.send_message(message.chat.id, message_found_cars, reply_markup=inline_search_menu)


    # elif message.text == "bd cars add":
    #     for car_id, car_name in bot_controller.all_cars.items():
    #         await db_controller.add_car(car_name, 000000000, "awesomecars", car_id)

    # elif message.text == markups.BUTTON_TEST_TEXT:
    #     await bot_controller.distort_audio()


    else:
        await bot.send_message(message.chat.id, MAIN_MENU_MESSAGE,
                               reply_markup=markups.main_menu)


@dp.message_handler(state=States.searching)
async def search(message: types.Message):
    found_cars = await db_controller.get_cars_by_name(message.text)
    if not found_cars:
        await bot.send_message(message.chat.id, ERROR_CAR_NOT_EXIST_MESSAGE)
    elif len(found_cars) == 1:
        await bot_controller.send_car(found_cars[0], message.chat.id)
    else:
        inline_search_menu = await markups.get_inline_search_menu(found_cars, message.text.lower())
        message_found_cars = generate_message_found_cars(found_cars)
        await bot.send_message(message.chat.id, message_found_cars, reply_markup=inline_search_menu)


@dp.message_handler(state=States.my_cars)
async def my_cars_handler(message: types.Message):
    if message.text == markups.BUTTON_MY_CARS_TEXT:
        await bot.send_message(message.chat.id, "You can delete your cars here. Select car to edit",
                               reply_markup=markups.my_cars_menu)
        found_cars = await db_controller.get_cars_by_tg_id(message.from_user.id)
        if not found_cars:
            await bot.send_message(message.chat.id, "You doesn't have cars")
        else:
            inline_search_menu = await markups.get_inline_my_cars_menu(found_cars, message.text.lower())
            message_found_cars = generate_message_found_cars(found_cars)
            await bot.send_message(message.chat.id, message_found_cars, reply_markup=inline_search_menu)
    elif message.text == markups.BUTTON_MY_STATS_TEXT:
        await bot_controller.send_my_stats(message.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_MY_CAR), state=States.my_cars)
async def my_cars_callback(callback_query: types.CallbackQuery, state: FSMContext):
    found_car = await db_controller.get_car_by_id(
        callback_query.data.lstrip(markups.CALLBACK_DATA_MY_CAR))
    await bot_controller.send_my_car(found_car, callback_query.message.chat.id)
    await bot.send_message(callback_query.from_user.id, "Now you can remove car", reply_markup=markups.my_cars_menu)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_REMOVE), state=States.my_cars)
async def remove_callback(callback_query: types.CallbackQuery, state: FSMContext):
    car_id = callback_query.data.lstrip(markups.CALLBACK_DATA_REMOVE)
    inline_sure_menu = markups.get_inline_sure_menu(car_id)
    await bot.send_message(callback_query.from_user.id, "Are you sure?", reply_markup=inline_sure_menu)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_ACCEPT) or c.data.startswith(markups.CALLBACK_DATA_DECLINE), state=States.my_cars)
async def remove_car_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data.startswith(markups.CALLBACK_DATA_ACCEPT):
        car_id = callback_query.data.lstrip(markups.CALLBACK_DATA_ACCEPT)
        await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)
        await db_controller.delete_car(car_id)
        await bot.send_message(callback_query.from_user.id, "Your car successfully deleted", reply_markup=markups.my_cars_menu)
    else:
        await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)


@dp.message_handler(content_types=types.ContentType.TEXT, state=States.waiting_for_search_name)
async def process_car_check(message: types.Message):
    await search(message)

    await bot.send_message(message.chat.id, CONSTRUCTOR_CONTINUE_REPEAT_ASK_MESSAGE, reply_markup=markups.inline_continue_repeat_buttons)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_CONTINUE), state=States.waiting_for_search_name)
async def process_callback_continue(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)
    await state.set_state(States.waiting_for_logo)
    await bot.send_message(callback_query.from_user.id, CONSTRUCTOR_LOGO_ASK_MESSAGE)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_REPEAT), state=States.waiting_for_search_name)
async def process_callback_repeat(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, CONSTRUCTOR_NAME_ASK_MESSAGE)


@dp.message_handler(state=States.waiting_for_search_name)
async def handle_invalid_car_name(message: types.Message):
    await message.reply(CONSTRUCTOR_NAME_ASK_MESSAGE)


@dp.message_handler(content_types=types.ContentType.PHOTO, state=States.waiting_for_logo)
async def process_logo_image(message: types.Message, state: FSMContext):
    await bot_controller.download_logo_image(message)
    await state.set_state(States.waiting_for_audio)
    await bot.send_message(message.chat.id, CONSTRUCTOR_AUDIO_ASK_MESSAGE, reply_markup=markups.constructor_menu)


@dp.message_handler(state=States.waiting_for_logo)
async def handle_invalid_logo_image(message: types.Message):
    await message.reply(CONSTRUCTOR_LOGO_ASK_MESSAGE)


@dp.message_handler(content_types=[types.ContentType.AUDIO, types.ContentType.VOICE], state=States.waiting_for_audio)
async def process_audio_and_video(message: types.Message, state: FSMContext):
    loading_message = await bot.send_message(message.chat.id, LOADING_MESSAGE)

    audio_path = await bot_controller.create_audio(message, "audio")
    # await bot_controller.normalize_audio(message, "audio")
    await bot.delete_message(message.chat.id, loading_message.message_id)
    if not audio_path:
        await message.reply(ERROR_AUDIO_TOO_BIG)
        return

    await state.set_state(States.drip_audio_edit)
    drip_path = await bot_controller.get_drip_path(message)
    if not os.path.exists(drip_path):
        shutil.copy(audio_path, drip_path)
    await constructor_send_drip_audio(message.from_user.id, drip_path)


@dp.message_handler(state=States.drip_audio_edit)
async def drip_audio_edit(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_AUDIO_EDIT_TEXT:
        await state.set_state(States.audio_edit)
        await bot.send_message(message.from_user.id, "audio edit", reply_markup=markups.audio_edit_menu)
    elif message.text == markups.BUTTON_MUSIC_EDIT_TEXT:
        await state.set_state(States.music_edit)
        await bot.send_message(message.from_user.id, CONSTRUCTOR_MUSIC_ASK_MESSAGE, reply_markup=markups.music_edit_menu)
    elif message.text == markups.BUTTON_CONTINUE_TEXT:
        await state.set_state(States.waiting_for_accept)
        audio_path = await bot_controller.get_drip_path(message)
        result_car_mp4 = await bot_controller.create_video(message.chat.id, audio_path)
        await bot.send_video_note(message.chat.id, result_car_mp4)
        await bot.send_message(message.chat.id, CONSTRUCTOR_CAR_ACCEPT_MESSAGE, reply_markup=markups.inline_continue_repeat_buttons)


@dp.message_handler(content_types=[types.ContentType.AUDIO, types.ContentType.VOICE], state=States.music_edit)
async def music_process(message: types.Message, state: FSMContext):
    loading_message = await bot.send_message(message.chat.id, LOADING_MESSAGE)

    audio_path = await bot_controller.create_audio(message, "music")
    await bot.delete_message(message.chat.id, loading_message.message_id)
    if not audio_path:
        await message.reply(ERROR_AUDIO_TOO_BIG)
        return

    await bot_controller.audio_mix(message, audio_path)
    drip_path = await bot_controller.get_drip_path(message)
    await constructor_send_drip_audio(message.from_user.id, drip_path)


@dp.message_handler(state=States.audio_edit)
async def audio_edit(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_CUT_TEXT:
        await state.set_state(States.audio_cut_start)
        await bot.send_message(message.from_user.id, CONSTRUCTOR_AUDIO_CUT_START_TIME_ASK_MESSAGE)
    elif message.text == markups.BUTTON_INCREASE_VOLUME_TEXT:
        await bot_controller.increase_volume(message, "audio")
        audio_path = await bot_controller.get_audio_path(message)
        await constructor_send_audio(message.from_user.id, audio_path)
    elif message.text == markups.BUTTON_DECREASE_VOLUME_TEXT:
        await bot_controller.decrease_volume(message, "audio")
        audio_path = await bot_controller.get_audio_path(message)
        await constructor_send_audio(message.from_user.id, audio_path)
    elif message.text == markups.BUTTON_RESET_TEXT:
        audio_path_origin = await bot_controller.get_audio_path(message, origin=True)
        audio_path = await bot_controller.get_audio_path(message)
        if os.path.exists(audio_path):
            os.remove(audio_path)
            shutil.copy(audio_path_origin, audio_path)
    elif message.text == markups.BUTTON_BACK_TEXT:
        await state.set_state(States.drip_audio_edit)
        audio_path = await bot_controller.get_audio_path(message)
        drip_path = await bot_controller.get_drip_path(message)
        music_path = await bot_controller.get_music_path(message)
        if not os.path.exists(music_path):
            os.remove(drip_path)
            shutil.copy(audio_path, drip_path)
        else:
            await bot_controller.audio_mix(message, music_path)
        await constructor_send_drip_audio(message.from_user.id, drip_path)


@dp.message_handler(state=States.music_edit)
async def music_edit(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_CUT_TEXT:
        if os.path.exists(f"data/constructor/audios/music/music_{message.from_user.id}.mp3"):
            await state.set_state(States.music_cut_start)
            await bot.send_message(message.from_user.id, CONSTRUCTOR_AUDIO_CUT_START_TIME_ASK_MESSAGE)
        else:
            await bot.send_message(message.from_user.id, CONSTRUCTOR_MUSIC_ASK_MESSAGE)
    elif message.text == markups.BUTTON_SAMPLES_TEXT:
        await bot.send_message(message.from_user.id, CONSTRUCTOR_MUSIC_SAMPLES_MESSAGE, reply_markup=markups.music_edit_menu)
        await bot_controller.send_samples(message.from_user.id)
    elif message.text == markups.BUTTON_INCREASE_VOLUME_TEXT:
        await bot_controller.increase_volume(message, "music")
        audio_path = await bot_controller.get_music_path(message)
        await constructor_send_music(message.from_user.id, audio_path)
    elif message.text == markups.BUTTON_DECREASE_VOLUME_TEXT:
        await bot_controller.decrease_volume(message, "music")
        audio_path = await bot_controller.get_music_path(message)
        await constructor_send_music(message.from_user.id, audio_path)
    elif message.text == markups.BUTTON_RESET_TEXT:
        audio_path_origin = await bot_controller.get_music_path(message, origin=True)
        audio_path = await bot_controller.get_music_path(message)
        if os.path.exists(audio_path):
            os.remove(audio_path)
            shutil.copy(audio_path_origin, audio_path)
    elif message.text == markups.BUTTON_BACK_TEXT:
        await state.set_state(States.drip_audio_edit)
        music_path = await bot_controller.get_music_path(message)
        await bot_controller.audio_mix(message, music_path)
        drip_path = await bot_controller.get_drip_path(message)
        await constructor_send_drip_audio(message.from_user.id, drip_path)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_MUSIC_SAMPLE), state=States.music_edit)
async def process_music_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    src_file = f"{bot_controller.MUSIC_SAMPLES_PATH}/{callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_MUSIC_SAMPLE)}"
    audio_path = await bot_controller.get_music_path(callback_query)
    if os.path.exists(audio_path):
        os.remove(audio_path)
    shutil.copy(src_file, audio_path)
    # await bot_controller.audio_mix(callback_query, input_file_2)
    await constructor_send_music(callback_query.from_user.id, audio_path)


@dp.message_handler(content_types=types.ContentType.TEXT, state=States.audio_cut_start)
async def audio_start_cut(message: types.Message, state: FSMContext):
    pattern = r'^\d{2}:\d{2}$'
    match = re.match(pattern, message.text)
    if not match:
        await message.reply(CONSTRUCTOR_AUDIO_CUT_START_TIME_ASK_MESSAGE)
        return

    await bot_controller.start_cut_audio(message, "audio")
    await state.set_state(States.audio_cut_end)
    await bot.send_message(message.from_user.id, CONSTRUCTOR_AUDIO_CUT_END_TIME_ASK_MESSAGE)


@dp.message_handler(state=States.audio_cut_start)
async def handle_invalid_audio_start_cut(message: types.Message):
    await message.reply(CONSTRUCTOR_AUDIO_CUT_START_TIME_ASK_MESSAGE)


@dp.message_handler(content_types=types.ContentType.TEXT, state=States.audio_cut_end)
async def audio_end_cut(message: types.Message, state: FSMContext):
    if not message.text.isdecimal():
        await message.reply(CONSTRUCTOR_AUDIO_CUT_END_TIME_ASK_MESSAGE)
        return

    await bot_controller.end_cut_audio(message, "audio")
    await state.set_state(States.audio_edit)
    await constructor_send_audio(message.from_user.id, bot_controller.get_audio_path(message))


@dp.message_handler(state=States.audio_cut_end)
async def handle_invalid_audio_start_cut(message: types.Message):
    await message.reply(CONSTRUCTOR_AUDIO_CUT_END_TIME_ASK_MESSAGE)


@dp.message_handler(content_types=types.ContentType.TEXT, state=States.music_cut_start)
async def music_start_cut(message: types.Message, state: FSMContext):
    pattern = r'^\d{2}:\d{2}$'
    match = re.match(pattern, message.text)
    if not match:
        await message.reply(CONSTRUCTOR_AUDIO_CUT_START_TIME_ASK_MESSAGE)
        return

    await bot_controller.start_cut_audio(message, "music")
    await state.set_state(States.music_cut_end)
    await bot.send_message(message.from_user.id, CONSTRUCTOR_AUDIO_CUT_END_TIME_ASK_MESSAGE)


@dp.message_handler(state=States.music_cut_start)
async def handle_invalid_music_start_cut(message: types.Message):
    await message.reply(CONSTRUCTOR_AUDIO_CUT_START_TIME_ASK_MESSAGE)


@dp.message_handler(content_types=types.ContentType.TEXT, state=States.music_cut_end)
async def music_end_cut(message: types.Message, state: FSMContext):
    if not message.text.isdecimal():
        await message.reply(CONSTRUCTOR_AUDIO_CUT_END_TIME_ASK_MESSAGE)
        return

    await bot_controller.end_cut_audio(message, "music")
    await state.set_state(States.music_edit)
    await constructor_send_music(message.from_user.id, await bot_controller.get_music_path(message))


@dp.message_handler(state=States.music_cut_end)
async def handle_invalid_music_start_cut(message: types.Message):
    await message.reply(CONSTRUCTOR_AUDIO_CUT_END_TIME_ASK_MESSAGE)


@dp.callback_query_handler(lambda c: c.data == markups.CALLBACK_DATA_BUTTON_CONTINUE, state=States.waiting_for_accept)
async def process_accept_callback_continue(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)
    await state.set_state(States.waiting_for_name)
    await bot.send_message(callback_query.from_user.id, CONSTRUCTOR_NAME_ASK_MESSAGE)


@dp.callback_query_handler(lambda c: c.data == markups.CALLBACK_DATA_BUTTON_REPEAT, state=States.waiting_for_accept)
async def process_name_callback_repeat(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)
    await state.set_state(States.waiting_for_search_name)
    await bot.send_message(callback_query.from_user.id, CONSTRUCTOR_CAR_CHECK_MESSAGE, reply_markup=markups.constructor_menu)


@dp.message_handler(state=States.waiting_for_name)
async def constructor_car_create(message: types.Message, state: FSMContext):
    new_car = await db_controller.add_car(message.text, message.from_user.id, "tg_constructor", message.message_id)
    car_name = f"car_{message.from_user.id}"
    await s3_client.upload_car_mp4(car_name, new_car.id)
    await bot.send_message(message.from_user.id, CONSTRUCTOR_SUCCESS_MESSAGE, reply_markup=markups.main_menu)
    await bot_controller.delete_constructor_src(message.from_user.id)
    await state.finish()


@dp.message_handler(state=States.waiting_for_audio)
async def handle_invalid_audio(message: types.Message):
    await message.reply(CONSTRUCTOR_AUDIO_ASK_MESSAGE)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_CAR), state="*")
async def send_car_by_inline_button(callback_query: types.CallbackQuery):
    await callback_query.answer()
    if callback_query.data.startswith(markups.CALLBACK_DATA_BUTTON_ALL_CARS):
        found_cars = await db_controller.get_cars_by_name(
            callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_ALL_CARS))
        for car in found_cars:
            await bot_controller.send_car(car, callback_query.message.chat.id)
    else:
        found_cars = await db_controller.get_car_by_id(
            callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_CAR))
        await bot_controller.send_car(found_cars, callback_query.message.chat.id)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_AUDIO), state="*")
async def send_voice_version_by_inline_button(callback_query: types.CallbackQuery):
    await callback_query.answer()
    car = await db_controller.get_car_by_id(
        callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_AUDIO))
    await bot_controller.send_voice_version(car, callback_query.message.chat.id)
    await bot_controller.delete_car(car)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_STATS), state="*")
async def send_voice_version_by_inline_button(callback_query: types.CallbackQuery):
    await callback_query.answer()
    button_data = callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_STATS)
    if button_data.startswith(markups.CALLBACK_DATA_BUTTON_LIKE):
        await db_controller.add_like(button_data.lstrip(markups.CALLBACK_DATA_BUTTON_LIKE))
    elif button_data.startswith(markups.CALLBACK_DATA_BUTTON_DISLIKE):
        await db_controller.add_dislike(button_data.lstrip(markups.CALLBACK_DATA_BUTTON_DISLIKE))
    elif button_data.startswith(markups.CALLBACK_DATA_BUTTON_All_STATS):
        car_likes, car_dislikes, car_views = await db_controller.get_stats(button_data.lstrip(markups.CALLBACK_DATA_BUTTON_All_STATS))
        await bot.send_message(callback_query.from_user.id, f"Likes: {car_likes}\n"
                                                      f"Dislikes: {car_dislikes}\n"
                                                      f"Views: {car_views}")


@dp.callback_query_handler(lambda c: True, state="*")
async def invalid_state(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, ERROR_WRONG_STATE + "\n" + callback_query.data + "\n" + f"{await state.get_state()}")


def generate_message_found_cars(found_cars):
    message_header = "Found car:" if len(found_cars) == 1 else "Found cars:"
    message_found_cars = [f"{i + 1}. {car.name}" for i, car in enumerate(found_cars)]
    return "\n".join([message_header, *message_found_cars])


async def constructor_send_audio(chat_id, audio_path):
    await bot.send_message(chat_id, "Your audio:")
    await bot.send_audio(chat_id, types.InputFile(audio_path), reply_markup=markups.audio_edit_menu)


async def constructor_send_drip_audio(chat_id, audio_path):
    await bot.send_message(chat_id, "Your drip audio:")
    await bot.send_audio(chat_id, types.InputFile(audio_path), reply_markup=markups.drip_audio_edit_menu)


async def constructor_send_music(chat_id, audio_path):
    await bot.send_message(chat_id, "Your music:")
    await bot.send_audio(chat_id, types.InputFile(audio_path), reply_markup=markups.music_edit_menu)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


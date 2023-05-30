import bot_tg
import bot_controller
import markups
import re
import converter

from aiogram import types
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

START_MESSAGE = 'Hello! Drip car bot at your service'
MAIN_MENU_MESSAGE = 'Press "🔍 Car search" to search the car\nPress "🎲 Random car" to get random car'
SEARCH_HINT_MESSAGE = 'To search type car name into chat'
INFO_MESSAGE = 'Constructor version 1'
CONSTRUCTOR_LOGO_ASK_MESSAGE = "Please send logo image"
CONSTRUCTOR_AUDIO_ASK_MESSAGE = "Please send audio"
LOADING_MESSAGE = "🚦 Loading..."

ERROR_NOT_WORKING_MESSAGE = 'Not working yet'
ERROR_CAR_NOT_EXIST_MESSAGE = "Car doesn't exist. Try again!"

MAX_AUDIO_SIZE_MB = 10

dp = bot_tg.get_dp()
bot = bot_tg.get_bot()


class SearchOrder(StatesGroup):
    searching = State()
    waiting_for_logo = State()
    waiting_for_audio = State()


@dp.errors_handler()
async def error_handler(update: types.Update, exception: Exception):
    print(f'Ошибка обновления: {exception}')


# --- Command START ---
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await bot.send_message(message.chat.id, START_MESSAGE, reply_markup=markups.main_menu)


# --- Main message HANDLER ---
@dp.message_handler()
async def input_handler(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_RANDOM_TEXT:
        found_cars = await bot_controller.get_random_car(message)
        await bot_controller.send_cars(found_cars, message.chat.id)

    elif message.text == markups.BUTTON_SEARCH_TEXT:
        await bot.send_message(message.chat.id, SEARCH_HINT_MESSAGE, reply_markup=markups.search_menu)
        await state.set_state(SearchOrder.searching)

    elif message.text == markups.BUTTON_OTHER_TEXT:
        await bot.send_message(message.chat.id, INFO_MESSAGE, reply_markup=markups.other_menu)

    elif message.text == markups.BUTTON_CONSTRUCTOR_TEXT:
        await bot.send_message(message.chat.id, CONSTRUCTOR_LOGO_ASK_MESSAGE, reply_markup=markups.constructor_menu)
        await state.set_state(SearchOrder.waiting_for_logo)

    else:
        await bot.send_message(message.chat.id, MAIN_MENU_MESSAGE,
                               reply_markup=markups.main_menu)


@dp.message_handler(lambda c: c.text == markups.BUTTON_MAIN_MENU_TEXT, state="*")
async def main_menu_button(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.chat.id, MAIN_MENU_MESSAGE, reply_markup=markups.main_menu)


@dp.message_handler(state=SearchOrder.searching)
async def search(message: types.Message):
    found_cars = await bot_controller.get_cars_by_search(message.text.lower())

    if not found_cars:
        await bot.send_message(message.chat.id, ERROR_CAR_NOT_EXIST_MESSAGE)
    elif len(found_cars) == 1:
        await bot_controller.send_cars(found_cars, message.chat.id)
    else:
        inline_search_menu = await markups.get_inline_search_menu(found_cars, message.text.lower())
        message_found_cars = generate_message_found_cars(found_cars)
        await bot.send_message(message.chat.id, message_found_cars, reply_markup=inline_search_menu)


@dp.message_handler(content_types=types.ContentType.PHOTO, state=SearchOrder.waiting_for_logo)
async def process_logo_image(message: types.Message, state: FSMContext):
    logo_image = message.photo[-1]

    chat_id = message.chat.id
    logo_image_path = f"data/constructor/images/logo_{chat_id}.jpg"

    await logo_image.download(destination_file=logo_image_path)

    await state.set_state(SearchOrder.waiting_for_audio)
    await bot.send_message(message.chat.id, CONSTRUCTOR_AUDIO_ASK_MESSAGE, reply_markup=markups.constructor_menu)


@dp.message_handler(state=SearchOrder.waiting_for_logo)
async def handle_invalid_logo_image(message: types.Message):
    await message.reply(CONSTRUCTOR_LOGO_ASK_MESSAGE)


@dp.message_handler(content_types=[types.ContentType.AUDIO, types.ContentType.VOICE], state=SearchOrder.waiting_for_audio)
async def process_audio_and_make_video(message: types.Message, state: FSMContext):
    loading_message = await bot.send_message(message.chat.id, LOADING_MESSAGE)
    if message.audio:
        file_id = message.audio.file_id
        file_size_mb = message.audio.file_size / (1024 * 1024)
    else:
        file_id = message.voice.file_id
        file_size_mb = message.voice.file_size / (1024 * 1024)

    if file_size_mb > MAX_AUDIO_SIZE_MB:
        await message.reply(f"Audio too big. Maximum size: {MAX_AUDIO_SIZE_MB} MB.")
        return

    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_extension = re.search(r'\.(\w+)$', file_path).group(1)

    chat_id = message.chat.id
    audio_path = f"data/constructor/audios/audio_{chat_id}.{file_extension}"

    await bot.download_file(file_path, audio_path)

    logo_path_by_id = f"data/constructor/images/logo_{chat_id}.jpg"
    video_path = converter.create_car_video_from_logo_and_audio(logo_path_by_id, audio_path, chat_id)
    await state.finish()
    result_car_mp4 = types.InputFile(video_path)

    await bot.delete_message(message.chat.id, loading_message.message_id)
    await bot.send_video_note(message.chat.id, result_car_mp4, reply_markup=markups.main_menu)


@dp.message_handler(state=SearchOrder.waiting_for_audio)
async def handle_invalid_audio(message: types.Message):
    await message.reply(CONSTRUCTOR_AUDIO_ASK_MESSAGE)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_CAR_TEXT), state="*")
async def send_car_by_inline_button(callback_query: types.CallbackQuery):
    await callback_query.answer()
    if callback_query.data.startswith(markups.CALLBACK_DATA_BUTTON_ALL_CARS_TEXT):
        found_cars = await bot_controller.get_cars_by_search(
            callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_ALL_CARS_TEXT))
    else:
        found_cars = await bot_controller.get_cars_by_id(
            callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_CAR_TEXT))

    await bot_controller.send_cars(found_cars, callback_query.message.chat.id)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_AUDIO_TEXT), state="*")
async def send_voice_version_by_inline_button(callback_query: types.CallbackQuery):
    await callback_query.answer()
    car_to_send = await bot_controller.get_cars_by_id(
        callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_AUDIO_TEXT))
    await bot_controller.send_voice_version(car_to_send[0], callback_query.message.chat.id)


def generate_message_found_cars(found_cars):
    message_header = "Found car:" if len(found_cars) == 1 else "Found cars:"
    message_found_cars = [f"{i + 1}. {car['name']}" for i, car in enumerate(found_cars)]
    return "\n".join([message_header, *message_found_cars])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


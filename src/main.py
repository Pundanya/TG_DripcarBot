import bot_tg
import bot_controller
import markups
import db_controller
import s3_client
import os

from aiogram import types
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

START_MESSAGE = 'Hello! Drip car bot at your service'
MAIN_MENU_MESSAGE = 'Press "🔍 Car search" to search the car\nPress "🎲 Random car" to get random car'
SEARCH_HINT_MESSAGE = 'To search enter car name into chat'
INFO_MESSAGE = 'Constructor version 2. Now your cars can be searched!'
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
    waiting_for_search_name = State()
    waiting_for_logo = State()
    waiting_for_audio = State()
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

    elif message.text == markups.BUTTON_OTHER_TEXT:
        await bot.send_message(message.chat.id, INFO_MESSAGE, reply_markup=markups.other_menu)

    elif message.text == markups.BUTTON_CONSTRUCTOR_TEXT:
        await state.set_state(States.waiting_for_search_name)
        await bot.send_message(message.chat.id, CONSTRUCTOR_CAR_CHECK_MESSAGE, reply_markup=markups.constructor_menu)


    # elif message.text == "bd cars add":
    #     for car_id, car_name in bot_controller.all_cars.items():
    #         await db_controller.add_car(car_name, 000000000, "awesomecars", car_id)

    else:
        await bot.send_message(message.chat.id, MAIN_MENU_MESSAGE,
                               reply_markup=markups.main_menu)


@dp.message_handler(lambda c: c.text == markups.BUTTON_MAIN_MENU_TEXT, state="*")
async def main_menu_button(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.chat.id, MAIN_MENU_MESSAGE, reply_markup=markups.main_menu)


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


@dp.message_handler(content_types=types.ContentType.TEXT, state=States.waiting_for_search_name)
async def process_car_check(message: types.Message):
    await search(message)

    await bot.send_message(message.chat.id, CONSTRUCTOR_CONTINUE_REPEAT_ASK_MESSAGE, reply_markup=markups.inline_continue_repeat_buttons)


@dp.callback_query_handler(lambda c: c.data == markups.CALLBACK_DATA_BUTTON_CONTINUE, state=States.waiting_for_search_name)
async def process_callback_continue(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)
    await state.set_state(States.waiting_for_logo)
    await bot.send_message(callback_query.from_user.id, CONSTRUCTOR_LOGO_ASK_MESSAGE)


@dp.callback_query_handler(lambda c: c.data == markups.CALLBACK_DATA_BUTTON_REPEAT, state=States.waiting_for_search_name)
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

    audio_path = await bot_controller.create_audio(message)
    await bot.delete_message(message.chat.id, loading_message.message_id)
    if not audio_path:
        await message.reply(ERROR_AUDIO_TOO_BIG)
        return

    result_car_mp4 = await bot_controller.create_video(message.chat.id, audio_path)

    await state.set_state(States.waiting_for_accept)
    await bot.send_video_note(message.chat.id, result_car_mp4)
    await bot.send_message(message.chat.id, CONSTRUCTOR_CAR_ACCEPT_MESSAGE, reply_markup=markups.inline_continue_repeat_buttons)


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
async def constructor_car_create(message: types.Message):
    new_car = await db_controller.add_car(message.text, message.from_user.id, "tg_constructor", message.message_id)
    car_name = f"car_{message.from_user.id}"
    car_path = f"data/constructor/result/car_video/{car_name}.mp4"
    await s3_client.upload_car_mp4(car_name, new_car.id)
    if os.path.exists(car_path):
        os.remove(car_path)
    await bot.send_message(message.from_user.id, SUCCESS_MESSAGE)


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


@dp.callback_query_handler(lambda c: True, state="*")
async def invalid_state(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, ERROR_WRONG_STATE)


def generate_message_found_cars(found_cars):
    message_header = "Found car:" if len(found_cars) == 1 else "Found cars:"
    message_found_cars = [f"{i + 1}. {car.name}" for i, car in enumerate(found_cars)]
    return "\n".join([message_header, *message_found_cars])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


import bot_tg
import bot_controller
import markups
import db_controller
import asyncio

from datetime import datetime, timedelta, timezone
from aiogram import types
from aiogram.utils import executor, exceptions
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

SEARCH_HINT_TEXT = f"<b>{markups.BUTTON_SEARCH_TEXT}</b>" \
                      "\n" \
                      "\nEnter something to search."
NO_MY_CARS_TEXT = f"<b>{markups.BUTTON_MY_CARS_TEXT}</b>" \
                  "\n" \
                  "\nYou don't have any cars."
NO_SUBSCRIPTION_TEXT = f'{markups.BUTTON_SUBSCRIPTIONS_TEXT}' \
                       '\n' \
                       f'\nYou are not subscribed. To subscribe, click <b>{markups.BUTTON_SUBSCRIBE_TEXT}</b>.'
REMOVE_CAR_INFO_TEXT = f"<b>{markups.BUTTON_MY_CARS_TEXT}</b>" \
                       "\n" \
                       "\nThese are your cars. You can select a car to delete."
TOP_CARS_HEADER = f"<b>{markups.BUTTON_TOP_TEXT}</b>\n\n"
RANDOM_CAR_HEADER = f"<b>{markups.BUTTON_RANDOM_TEXT}</b>\n\n"
CAR_REMOVED_TEXT = "Your car has been successfully deleted."
SURE_ASK_TEXT = f"<b>{markups.BUTTON_REMOVE_TEXT}</b>" \
                "\n" \
                "\nAre you sure?"
YOUR_CAR_TEXT = "Here is your car:"
YOUR_RANDOM_CAR_TEXT = "Here is your random car:"

CNSTR_INFO_TEXT = f"<b>{markups.BUTTON_CNSTR_TEXT}</b>" \
                  "\n" \
                  "\nHere you can create your own car using an image and audio."
CNSTR_NAME_ASK_TEXT = "<b>Please send the car name.</b>" \
                      "\n" \
                      "\nBy using the car's name, you and other people will be able to search the car in the car fleet."
CNSTR_LOGO_ASK_TEXT = "<b>Please send the image.</b>" \
                      "\n" \
                      "\n<code>Supported formats: compressed images. Uncompressed files are not supported.</code>" \
                      "\n" \
                      "\nThe image will be applied to the car's door. The car's color will be automatically adjusted."
CNSTR_AUDIO_ASK_TEXT = "<b>Please send the audio.</b>" \
                       "\n" \
                       "\n<code>Supported formats: audio files and voice messages.</code>" \
                       "\n" \
                       "\nNext, you will be able to edit audio."
CNSTR_SUCCESS_TEXT = "<b>Success!</b>" \
                     "\n" \
                     "\nYour car has been added to the car fleet."
CNSTR_AUDIO_CUT_START_TIME_ASK_TEXT = "<b>Please send start time.</b>" \
                                      "\n" \
                                      "\n<code>Send the starting point for the cut. Your audio track will begin from this moment.</code>" \
                                      "\n" \
                                      "\nExample: <b><u>01:23</u></b> (mm:ss)"
CNSTR_AUDIO_CUT_END_TIME_ASK_TEXT = "<b>Please send the duration of the cut.</b>" \
                                    "\n" \
                                    "\n<code>Maximum duration is 20 seconds.</code>" \
                                    "\n" \
                                    "\nExample: <b><u>14</u></b> (ss)"
CNSTR_MUSIC_ASK_TEXT = "Please send an additional audio track or select from the provided templates." \
                       "\n" \
                       "\nThe constructor supports the merging of two audio tracks."
CNSTR_MUSIC_SAMPLES_TEXT = f"<b>{markups.BUTTON_SAMPLES_TEXT}</b>" \
                           "\n" \
                           "\nYou can select from this template songs:"

LOADING_MESSAGE = "🛠 <u>Loading...</u>"
SUCCESS_MESSAGE = "SUCCESS!"

ERROR_NOT_WORKING_MESSAGE = 'Not working yet'
ERROR_CAR_NOT_EXIST_MESSAGE = "Car doesn't exist. Try again!"
ERROR_AUDIO_TOO_BIG = f"Audio too big. Maximum size: {bot_controller.MAX_AUDIO_SIZE_MB} MB."
ERROR = "Error"
ERROR_WRONG_STATE = "Button not work. Wrong state"
ERROR_INCORRECT = "Incorrect"

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
    subscription_choosing = State()
    subscription_time = State()


@dp.errors_handler()
async def error_handler(update: types.Update, exception: Exception):
    print(f'{ERROR}: {exception}')


# --- Command START ---
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    if not await db_controller.check_user_created(message.from_user.id):
        await db_controller.create_user(message)
        await bot.send_message(message.chat.id, f'<b>{markups.BUTTON_START_TEXT}</b>'
                                                '\n'
                                                '\nWelcome to the <b>DripCar Bot</b> fleet!'
                                                '\n\nHere you can:'
                                                '\n• Search a themed car or get a random car'
                                                '\n• Create your own car in the constructor'
                                                '\n• Subscribe to the daily random car and latest releases',
                               reply_markup=markups.main_menu)
    else:
        await bot.send_message(message.from_user.id, "You have already started the bot", reply_markup=markups.main_menu)


@dp.message_handler(lambda c: c.text == markups.BUTTON_MAIN_MENU_TEXT, state="*")
async def main_menu_button(message: types.Message, state: FSMContext):
    await bot_controller.delete_cnstr_src(message.chat.id)
    await state.finish()
    await send_main_menu(message.from_user.id)


# --- Main message HANDLER ---
@dp.message_handler()
async def input_handler(message: types.Message, state: FSMContext):
    await main_menu_process(message, state)


@dp.message_handler(state=States.searching)
async def search(message: types.Message):
    found_cars = await db_controller.get_cars_by_name(message.text)
    if not found_cars:
        await bot.send_message(message.chat.id, ERROR_CAR_NOT_EXIST_MESSAGE)
    elif len(found_cars) == 1:
        await send_car(found_cars[0], message.chat.id)
    else:
        inline_search_menu = await markups.get_inline_search_menu(found_cars, message.text.lower())
        message_found_cars = generate_message_found_cars(found_cars)
        await bot.send_message(message.chat.id, message_found_cars, reply_markup=inline_search_menu)


@dp.message_handler(state=States.subscription_choosing)
async def subscribe_handler(message: types.Message, state: FSMContext):
    if not await db_controller.check_subbed(message.from_user.id):
        await db_controller.add_subscriber(message.from_user.id)
    if message.text == markups.BUTTON_SUBSCRIBE_TEXT:
        await send_sub_message(message)
    else:
        await main_menu_process(message, state)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_DAILY_SUB),
                           state=States.subscription_choosing)
async def sub_daily_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await db_controller.sub_daily_change(callback_query.from_user.id)
    await update_sub_message(callback_query)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_RANDOM_SUB),
                           state=States.subscription_choosing)
async def sub_random_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await db_controller.sub_random_change(callback_query.from_user.id)
    await update_sub_message(callback_query)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_TIME), state=States.subscription_choosing)
async def time_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.set_state(States.subscription_time)
    cur_time = datetime.now(timezone.utc).time().strftime("%H:%M")
    await bot.send_message(callback_query.from_user.id, f"<b>{markups.BUTTON_TIME_TEXT}</b>"
                                                        "\n"
                                                        "\nPlease send the time when you would like the bot to send you a subscription message."
                                                        f"\n<code>Time in UTC±0. Current time: {cur_time}</code>"
                                                        "\n"
                                                        "\nExample: <b><u>09:05</u></b> (hh:mm)",
                           reply_markup=markups.back_main_menu)


@dp.message_handler(state=States.subscription_time)
async def time_handler(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_BACK_TEXT:
        await state.set_state(States.subscription_choosing)
        await send_sub_message(message)
    elif await bot_controller.time_match_d2(message.text):
        if -1 < int(message.text.split(":")[0]) < 24 and -1 < int(message.text.split(":")[1]) < 60:
            await db_controller.time_change(message.from_user.id, message.text)
            await state.set_state(States.subscription_choosing)
            await send_sub_message(message)
        else:
            await message.reply(ERROR_INCORRECT)
    else:
        await message.reply(ERROR_INCORRECT)


@dp.message_handler(state=States.my_cars)
async def my_cars_handler(message: types.Message):
    if message.text == markups.BUTTON_MY_CARS_TEXT:
        await send_my_cars(message.from_user.id)
    elif message.text == markups.BUTTON_MY_STATS_TEXT:
        likes, dislikes, views = await db_controller.get_stats_by_tg_id(message.from_user.id)
        await bot.send_message(message.from_user.id, f"<b>{markups.BUTTON_MY_STATS_TEXT}</b>"
                                                     f"\n"
                                                     f"\n👍 Likes: {likes}"
                                                     f"\n👎 Dislikes: {dislikes}"  
                                                     f"\n👀 Views: {views}")


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_MY_CAR), state=States.my_cars)
async def my_cars_callback(callback_query: types.CallbackQuery):
    found_car = await db_controller.get_car_by_id(
        callback_query.data.lstrip(markups.CALLBACK_DATA_MY_CAR))
    await bot.send_message(callback_query.from_user.id, f'Here is your car:\n{found_car.name}')
    await bot_controller.send_my_car(found_car, callback_query.message.chat.id)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_REMOVE), state=States.my_cars)
async def remove_callback(callback_query: types.CallbackQuery):
    callback_query.answer()
    car_id = callback_query.data.lstrip(markups.CALLBACK_DATA_REMOVE)
    inline_sure_menu = markups.get_inline_sure_menu(car_id)
    await bot.send_message(callback_query.from_user.id, SURE_ASK_TEXT, reply_markup=inline_sure_menu)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_ACCEPT), state=States.my_cars)
async def remove_car_accept_callback(callback_query: types.CallbackQuery):
    car_id = callback_query.data.lstrip(markups.CALLBACK_DATA_ACCEPT)
    await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot_controller.delete_car(car_id)
    await bot.send_message(callback_query.from_user.id, CAR_REMOVED_TEXT, reply_markup=markups.my_cars_menu)
    await send_my_cars(callback_query.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_DECLINE), state=States.my_cars)
async def remove_car_decline_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.from_user.id, message_id=callback_query.message.message_id)


@dp.message_handler(content_types=types.ContentType.PHOTO, state=States.waiting_for_logo)
async def process_logo_image(message: types.Message, state: FSMContext):
    await bot_controller.download_logo_image(message)
    await state.set_state(States.waiting_for_audio)
    await bot.send_message(message.chat.id, CNSTR_AUDIO_ASK_TEXT, reply_markup=markups.back_main_menu)


@dp.message_handler(state=States.waiting_for_logo)
async def handle_invalid_logo_image(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_BACK_TEXT:
        if await bot_controller.check_audio(message.from_user.id):
            await state.set_state(States.drip_audio_edit)
            await cnstr_send_drip(message.from_user.id)
        else:
            await bot_controller.delete_cnstr_src(message.from_user.id)
            await state.finish()
            await send_main_menu(message.from_user.id)
    else:
        await message.reply(CNSTR_LOGO_ASK_TEXT)


@dp.message_handler(content_types=[types.ContentType.AUDIO, types.ContentType.VOICE], state=States.waiting_for_audio)
async def process_audio_and_video(message: types.Message, state: FSMContext):
    await bot_controller.delete_audio(message.from_user.id)
    audio_path = await bot_controller.create_audio(message, bot_controller.IS_AUDIO)
    if not audio_path:
        await message.reply(ERROR_AUDIO_TOO_BIG)
        return
    await state.set_state(States.drip_audio_edit)
    await cnstr_send_drip(message.from_user.id)


@dp.message_handler(state=States.drip_audio_edit)
async def drip_audio_edit(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_AUDIO_EDIT_TEXT:
        await state.set_state(States.audio_edit)
        await cnstr_send_audio(message.from_user.id)
    elif message.text == markups.BUTTON_MUSIC_EDIT_TEXT:
        if await bot_controller.check_music(message.from_user.id):
            await state.set_state(States.music_edit)
            await cnstr_send_music(message.from_user.id)
        else:
            await state.set_state(States.music_edit)
            await bot.send_message(message.from_user.id, CNSTR_MUSIC_ASK_TEXT,
                                   reply_markup=markups.music_receive_menu)
    elif message.text == markups.BUTTON_CONTINUE_TEXT:
        await state.set_state(States.waiting_for_name)
        await bot.send_message(message.from_user.id, CNSTR_NAME_ASK_TEXT, reply_markup=markups.back_main_menu)
    elif message.text == markups.BUTTON_IMAGE_TEXT:
        await state.set_state(States.waiting_for_logo)
        await bot.send_message(message.chat.id, CNSTR_LOGO_ASK_TEXT, reply_markup=markups.back_main_menu)


@dp.message_handler(content_types=[types.ContentType.AUDIO, types.ContentType.VOICE], state=States.music_edit)
async def music_process(message: types.Message):
    music_path = await bot_controller.create_audio(message, bot_controller.IS_MUSIC)
    if not music_path:
        await message.reply(ERROR_AUDIO_TOO_BIG)
        return

    await cnstr_send_music(message.from_user.id)


@dp.message_handler(state=States.audio_edit)
async def audio_edit(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_CUT_TEXT:
        await state.set_state(States.audio_cut_start)
        await bot.send_message(message.from_user.id, CNSTR_AUDIO_CUT_START_TIME_ASK_TEXT)
    elif message.text == markups.BUTTON_INCREASE_VOLUME_TEXT:
        await bot_controller.increase_volume(message, bot_controller.IS_AUDIO)
        await cnstr_send_audio(message.from_user.id)
    elif message.text == markups.BUTTON_DECREASE_VOLUME_TEXT:
        await bot_controller.decrease_volume(message, bot_controller.IS_AUDIO)
        await cnstr_send_audio(message.from_user.id)
    elif message.text == markups.BUTTON_RESET_TEXT:
        await bot_controller.reset_audio(message)
    elif message.text == markups.BUTTON_NEW_AUDIO_TEXT:
        await state.set_state(States.waiting_for_audio)
        await bot.send_message(message.chat.id, CNSTR_AUDIO_ASK_TEXT, reply_markup=markups.back_main_menu)
    elif message.text == markups.BUTTON_BACK_TEXT:
        await state.set_state(States.drip_audio_edit)
        await bot_controller.audio_mix(message.from_user.id)
        await cnstr_send_drip(message.from_user.id)


@dp.message_handler(state=States.music_edit)
async def music_edit(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_CUT_TEXT:
        await state.set_state(States.music_cut_start)
        await bot.send_message(message.from_user.id, CNSTR_AUDIO_CUT_START_TIME_ASK_TEXT,
                               reply_markup=markups.back_main_menu)
    elif message.text == markups.BUTTON_SAMPLES_TEXT:
        await bot.send_message(message.from_user.id, CNSTR_MUSIC_SAMPLES_TEXT)
        await bot_controller.send_samples(message.from_user.id)
    elif message.text == markups.BUTTON_INCREASE_VOLUME_TEXT:
        await bot_controller.increase_volume(message, bot_controller.IS_MUSIC)
        await cnstr_send_music(message.from_user.id)
    elif message.text == markups.BUTTON_DECREASE_VOLUME_TEXT:
        await bot_controller.decrease_volume(message, bot_controller.IS_MUSIC)
        await cnstr_send_music(message.from_user.id)
    elif message.text == markups.BUTTON_RESET_TEXT:
        await bot_controller.reset_music(message)
    elif message.text == markups.BUTTON_REMOVE_TEXT:
        deleted = await bot_controller.delete_music(message.from_user.id)
        await bot.send_message(message.from_user.id, "Music " + " deleted" * deleted + "not found" * (not deleted))
        if deleted:
            await bot.send_message(message.from_user.id, CNSTR_MUSIC_ASK_TEXT,
                                   reply_markup=markups.music_receive_menu)
    elif message.text == markups.BUTTON_BACK_TEXT:
        await state.set_state(States.drip_audio_edit)
        await bot_controller.audio_mix(message.from_user.id)
        await cnstr_send_drip(message.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_MUSIC_SAMPLE),
                           state=States.music_edit)
async def process_music_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await bot_controller.sample_callback(callback_query)
    await cnstr_send_music(callback_query.from_user.id)


@dp.message_handler(content_types=types.ContentType.TEXT, state=States.audio_cut_start)
async def audio_start_cut(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_BACK_TEXT:
        await state.set_state(States.audio_edit)
        await cnstr_send_audio(message.from_user.id)
    if not await bot_controller.time_match_d2(message.text):
        await message.reply(CNSTR_AUDIO_CUT_START_TIME_ASK_TEXT)
        return

    await bot_controller.start_cut_audio(message, bot_controller.IS_AUDIO)
    await state.set_state(States.audio_cut_end)
    await bot.send_message(message.from_user.id, CNSTR_AUDIO_CUT_END_TIME_ASK_TEXT)


@dp.message_handler(state=States.audio_cut_start)
async def handle_invalid_audio_start_cut(message: types.Message):
    await message.reply(CNSTR_AUDIO_CUT_START_TIME_ASK_TEXT)


@dp.message_handler(content_types=types.ContentType.TEXT, state=States.audio_cut_end)
async def audio_end_cut(message: types.Message, state: FSMContext):
    if not await bot_controller.is_seconds(message.text):
        await message.reply(CNSTR_AUDIO_CUT_END_TIME_ASK_TEXT)
        return

    await bot_controller.end_cut_audio(message, bot_controller.IS_AUDIO)
    await state.set_state(States.audio_edit)
    await cnstr_send_audio(message.from_user.id)


@dp.message_handler(state=States.audio_cut_end)
async def handle_invalid_audio_start_cut(message: types.Message):
    await message.reply(CNSTR_AUDIO_CUT_END_TIME_ASK_TEXT)


@dp.message_handler(content_types=types.ContentType.TEXT, state=States.music_cut_start)
async def music_start_cut(message: types.Message, state: FSMContext):
    if not await bot_controller.time_match_d2(message.text):
        await message.reply(CNSTR_AUDIO_CUT_START_TIME_ASK_TEXT)
        return

    await bot_controller.start_cut_audio(message, bot_controller.IS_MUSIC)
    await state.set_state(States.music_cut_end)
    await bot.send_message(message.from_user.id, CNSTR_AUDIO_CUT_END_TIME_ASK_TEXT)


@dp.message_handler(state=States.music_cut_start)
async def handle_invalid_music_start_cut(message: types.Message):
    await message.reply(CNSTR_AUDIO_CUT_START_TIME_ASK_TEXT)


@dp.message_handler(content_types=types.ContentType.TEXT, state=States.music_cut_end)
async def music_end_cut(message: types.Message, state: FSMContext):
    if not await bot_controller.is_seconds(message.text):
        await message.reply(CNSTR_AUDIO_CUT_END_TIME_ASK_TEXT)
        return

    await bot_controller.end_cut_audio(message, bot_controller.IS_MUSIC)
    await state.set_state(States.music_edit)
    await cnstr_send_music(message.from_user.id)


@dp.message_handler(state=States.music_cut_end)
async def handle_invalid_music_start_cut(message: types.Message):
    await message.reply(CNSTR_AUDIO_CUT_END_TIME_ASK_TEXT)


@dp.message_handler(state=States.waiting_for_name)
async def cnstr_car_create(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_BACK_TEXT:
        await state.set_state(States.drip_audio_edit)
        await cnstr_send_drip(message.from_user.id)
    else:
        await bot_controller.cnstr_add_car(message)
        await bot.send_message(message.from_user.id, CNSTR_SUCCESS_TEXT, reply_markup=markups.main_menu)
        await state.finish()
        await bot_controller.delete_cnstr_src(message.from_user.id)


@dp.message_handler(state=States.waiting_for_audio)
async def handle_invalid_audio(message: types.Message, state: FSMContext):
    if message.text == markups.BUTTON_BACK_TEXT:
        if await bot_controller.check_drip(message.from_user.id):
            await state.set_state(States.audio_edit)
            await cnstr_send_audio(message.from_user.id)
        else:
            await state.set_state(States.waiting_for_logo)
            await bot.send_message(message.chat.id, CNSTR_LOGO_ASK_TEXT, reply_markup=markups.back_main_menu)
    else:
        await message.reply(CNSTR_AUDIO_ASK_TEXT)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_CAR), state="*")
async def send_car_by_inline_button(callback_query: types.CallbackQuery):
    await callback_query.answer()
    if callback_query.data.startswith(markups.CALLBACK_DATA_BUTTON_ALL_CARS):
        found_cars = await db_controller.get_cars_by_name(
            callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_ALL_CARS))
        for car in found_cars:
            await send_car(car, callback_query.message.chat.id)
    else:
        found_cars = await db_controller.get_car_by_id(
            callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_CAR))
        await send_car(found_cars, callback_query.message.chat.id)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_AUDIO), state="*")
async def send_voice_version_by_inline_button(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await bot_controller.send_voice_version(callback_query)


@dp.callback_query_handler(lambda c: c.data.startswith(markups.CALLBACK_DATA_BUTTON_STATS), state="*")
async def send_voice_version_by_inline_button(callback_query: types.CallbackQuery):
    await callback_query.answer()
    button_data = callback_query.data.lstrip(markups.CALLBACK_DATA_BUTTON_STATS)
    if button_data.startswith(markups.CALLBACK_DATA_BUTTON_LIKE):
        await db_controller.add_like(button_data.lstrip(markups.CALLBACK_DATA_BUTTON_LIKE))
    elif button_data.startswith(markups.CALLBACK_DATA_BUTTON_DISLIKE):
        await db_controller.add_dislike(button_data.lstrip(markups.CALLBACK_DATA_BUTTON_DISLIKE))
    elif button_data.startswith(markups.CALLBACK_DATA_BUTTON_All_STATS):
        car_likes, car_dislikes, car_views = await db_controller.get_stats(
            button_data.lstrip(markups.CALLBACK_DATA_BUTTON_All_STATS))
        await bot.send_message(callback_query.from_user.id, f"<b>Likes:</b> {car_likes}\n"
                                                            f"<b>Dislikes:</b> {car_dislikes}\n"
                                                            f"<b>Views:</b> {car_views}")


@dp.callback_query_handler(lambda c: True, state="*")
async def invalid_state(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id,
                           ERROR_WRONG_STATE + "\n" + f"Callback: {callback_query.data}" +
                           "\n" + f"State: {await state.get_state()}")


async def main_menu_process(message, state):
    if await db_controller.check_user_created(message.from_user.id):
        if message.text == markups.BUTTON_RANDOM_TEXT:
            car = await bot_controller.get_random_car()
            await bot.send_message(message.from_user.id, RANDOM_CAR_HEADER)
            await send_car(car, message.chat.id)
            await bot_controller.delete_car_files(car)

        elif message.text == markups.BUTTON_SEARCH_TEXT:
            await bot.send_message(message.chat.id, SEARCH_HINT_TEXT, reply_markup=markups.search_menu)
            await state.set_state(States.searching)

        elif message.text == markups.BUTTON_CNSTR_TEXT:
            await state.set_state(States.waiting_for_logo)
            await bot.send_message(message.from_user.id, CNSTR_INFO_TEXT)
            await bot.send_message(message.chat.id, CNSTR_LOGO_ASK_TEXT, reply_markup=markups.back_main_menu)

        elif message.text == markups.BUTTON_MY_CARS_TEXT:
            await state.set_state(States.my_cars)
            await send_my_cars(message.from_user.id)

        elif message.text == markups.BUTTON_TOP_TEXT:
            found_cars = await bot_controller.get_top_10_likes_cars()
            inline_search_menu = await markups.get_inline_search_menu(found_cars, message.text.lower())
            message_found_cars = generate_message_found_cars(found_cars)
            await bot.send_message(message.chat.id, TOP_CARS_HEADER + message_found_cars,
                                   reply_markup=inline_search_menu)

        elif message.text == markups.BUTTON_SUBSCRIPTIONS_TEXT:
            await state.set_state(States.subscription_choosing)
            if await db_controller.check_subbed(message.from_user.id):
                await send_sub_message(message)
            else:
                await bot.send_message(message.chat.id, NO_SUBSCRIPTION_TEXT,
                                       reply_markup=markups.subscribe_menu)

        elif await db_controller.is_admin(message.from_user.id):
            if "delete car" in message.text.lower():
                car_id = message.text.lower().split("delete car ")[1]
                await bot_controller.delete_car(car_id)
            elif "init" in message.text.lower():
                await db_controller.init_models()
                await bot.send_message(message.chat.id, SUCCESS_MESSAGE + " db init", reply_markup=markups.main_menu)
            elif "delete user" in message.text.lower():
                user_id = message.text.lower().split("delete user ")[1]
                await db_controller.delete_user(user_id)
            elif "bot send all" in message.text.lower():
                text = message.text.lower().split("bot send all ")[1]
                users = await db_controller.get_all_users()
                for user in users:
                    await bot.send_message(user.tg_id, text)
            elif "give admin" in message.text.lower():
                tg_id = message.text.split("give admin ")[1]
                await db_controller.give_admin_role(tg_id)
            else:
                await send_main_menu(message.from_user.id)
        else:
            await send_main_menu(message.from_user.id)
    else:
        await bot.send_message(message.from_user.id,
                               "You haven't visited the car fleet yet."
                               "\nTo gain access to the bot, please type <u><b>/start</b></u> in the chat.")


def generate_message_found_cars(found_cars):
    message_header = "<b>Found car</b>:" if len(found_cars) == 1 else "<b>Found cars:</b>"
    message_found_cars = [f"{i + 1}. {car.name}" for i, car in enumerate(found_cars)]
    return "\n".join([message_header, *message_found_cars])


async def send_sub_message(message):
    daily, random = await db_controller.check_subscriptions(message.from_user.id)
    inline_sub_menu = await markups.get_inline_subscription_menu(message.from_user.id)
    await bot.send_message(message.from_user.id, f"<b>{markups.BUTTON_SUBSCRIPTIONS_TEXT}</b>"
                                                 "\n"
                                                 "\n<code>You can choose one or both subscriptions at the same time.</code>"
                                                 "\n"
                                                 f"\n{'❌' * (not daily) + '✅' * daily} <b>{markups.BUTTON_DAILY_TEXT}</b> – new releases from the past 24 hours"
                                                 f"\n{'❌' * (not random) + '✅' * random} <b>{markups.BUTTON_RANDOM_SUB_TEXT}</b> – one random car"
                                                 "\n"
                                                 f"\n<b>{markups.BUTTON_TIME_TEXT}</b>: the time when the bot will send you the cars.",
                           reply_markup=inline_sub_menu)


async def update_sub_message(callback: types.CallbackQuery):
    daily, random = await db_controller.check_subscriptions(callback.from_user.id)
    await bot.edit_message_text(text=f"<b>{markups.BUTTON_SUBSCRIPTIONS_TEXT}</b>"
                                     "\n"
                                     "\n<code>You can choose one or both subscriptions at the same time.</code>"
                                     "\n"
                                     f"\n{'❌' * (not daily) + '✅' * daily} <b>{markups.BUTTON_DAILY_TEXT}</b> – new releases from the past 24 hours"
                                     f"\n{'❌' * (not random) + '✅' * random} <b>{markups.BUTTON_RANDOM_SUB_TEXT}</b> – one random car"
                                     "\n"
                                     f"\n<b>{markups.BUTTON_TIME_TEXT}</b>: the time when the bot will send you the cars.",
                                chat_id=callback.from_user.id, message_id=callback.message.message_id)
    inline_sub_menu = await markups.get_inline_subscription_menu(callback.from_user.id)
    await bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id,
                                        reply_markup=inline_sub_menu)


async def send_car(car, chat_id):
    await bot.send_message(chat_id, f'🚗 Here is your car:'
                                    f'\n\n'
                                    f'<b>{car.name}</b>')
    await bot_controller.send_car(car, chat_id)


async def cnstr_send_audio(chat_id):
    audio_path = await bot_controller.get_audio_path(chat_id)
    await bot.send_message(chat_id, f"<b>{markups.BUTTON_AUDIO_EDIT_TEXT}</b>"
                                    "\n"
                                    f"\n<b>{markups.BUTTON_INCREASE_VOLUME_TEXT}</b> – increase the audio volume. Can be used multiple times"
                                    f"\n<b>{markups.BUTTON_DECREASE_VOLUME_TEXT}</b> – decrease the audio volume. Can be used multiple times"
                                    f"\n<b>{markups.BUTTON_CUT_TEXT}</b> – Cut the audio"
                                    f"\n<b>{markups.BUTTON_RESET_TEXT}</b> – Reset the audio to its original version"
                                    f"\n<b>{markups.BUTTON_NEW_AUDIO_TEXT}</b> – Replace the current sound track with a new one")
    await bot.send_audio(chat_id, types.InputFile(audio_path), reply_markup=markups.audio_edit_menu)


async def cnstr_send_drip(chat_id):
    await bot.send_message(chat_id, f"<b>{markups.BUTTON_CNSTR_TEXT}</b>"
                                    "\n"
                                    "\n<code>The duration of the video depends on the maximum duration of the audio tracks.</code>"
                                    "\n"
                                    f"\n<b>{markups.BUTTON_AUDIO_EDIT_TEXT}</b> – Edit the main audio track"
                                    f"\n<b>{markups.BUTTON_MUSIC_EDIT_TEXT}</b> – [Optoinal] Edit the additional audio track. Several template tracks available."
                                    f"\n<b>{markups.BUTTON_IMAGE_TEXT}</b> – Edit the image"
                                    "\n"
                                    f"\n<b>{markups.BUTTON_CONTINUE_TEXT}</b> – Finish assembling the car and proceed to adding it to the car fleet")
    loading = await bot.send_message(chat_id, LOADING_MESSAGE)
    result_car_mp4 = await bot_controller.create_video(chat_id)
    await bot.delete_message(chat_id, loading.message_id)
    await bot.send_video_note(chat_id, result_car_mp4, reply_markup=markups.drip_audio_edit_menu)


async def cnstr_send_music(chat_id):
    music_path = await bot_controller.get_music_path(chat_id)
    await bot.send_message(chat_id, f"<b>{markups.BUTTON_MUSIC_EDIT_TEXT}</b>"
                                    "\n"
                                    f"\n<b>{markups.BUTTON_INCREASE_VOLUME_TEXT}</b> – increase the audio volume. Can be used multiple times"
                                    f"\n<b>{markups.BUTTON_DECREASE_VOLUME_TEXT}</b> – decrease the audio volume. Can be used multiple times"
                                    f"\n<b>{markups.BUTTON_CUT_TEXT}</b> – Cut the audio"
                                    f"\n<b>{markups.BUTTON_RESET_TEXT}</b> – Reset the audio to its original version"
                                    f"\n<b>{markups.BUTTON_REMOVE_TEXT}</b> – Remove this sound track from Drip Car")
    await bot.send_audio(chat_id, types.InputFile(music_path), reply_markup=markups.music_edit_menu)


async def send_main_menu(chat_id):
    cars_count = await db_controller.get_cars_count()
    await bot.send_message(chat_id, f'<b>{markups.BUTTON_MAIN_MENU_TEXT}</b>'
                                    '\n'
                                    f'\n{cars_count} cars currently in the car fleet.', reply_markup=markups.main_menu)


async def send_my_cars(chat_id):
    found_cars = await db_controller.get_cars_by_tg_id(chat_id)
    if not found_cars:
        await bot.send_message(chat_id, NO_MY_CARS_TEXT, reply_markup=markups.my_cars_menu)
    else:
        await bot.send_message(chat_id, REMOVE_CAR_INFO_TEXT,
                               reply_markup=markups.my_cars_menu)
        inline_search_menu = await markups.get_inline_my_cars_menu(found_cars)
        message_found_cars = generate_message_found_cars(found_cars)
        await bot.send_message(chat_id, message_found_cars, reply_markup=inline_search_menu)


async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        cur_time = datetime.now(timezone.utc).time().strftime("%H:%M")
        subs = await db_controller.get_subs_by_time(cur_time)
        for sub in subs:
            if sub.subscription_random:
                car = await bot_controller.get_random_car()
                try:
                    await bot.send_message(sub.subscriber_tg_id, "Random subscription:")
                except exceptions.ChatNotFound:
                    pass
                else:
                    await send_car(car, sub.subscriber_tg_id)
                    await bot_controller.delete_car_files(car)
            if sub.subscription_daily:
                try:
                    await bot.send_message(sub.subscriber_tg_id, "New releases subscription:")
                except exceptions.ChatNotFound:
                    pass
                else:
                    cur_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                    past_day = cur_date - timedelta(hours=24)
                    cars = await db_controller.get_cars_by_time(past_day)
                    if cars:
                        for car in cars:
                            await send_car(car, sub.subscriber_tg_id)
                    else:
                        await bot.send_message(sub.subscriber_tg_id, "There are no new releases 🥲")


if __name__ == '__main__':
    bot_controller.cnstr_src_clear()
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(60))
    executor.start_polling(dp, skip_updates=True)

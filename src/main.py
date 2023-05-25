import bot_tg
import bot_controller
import markups

from aiogram import types
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext



dp = bot_tg.get_dp()
bot = bot_tg.get_bot()


class SearchOrder(StatesGroup):
    searching = State()


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Hello! Drip car bot at your service', reply_markup=markups.main_menu)


@dp.message_handler()
async def input_handler(message: types.Message, state: FSMContext):
    if message.text == "🎲 Random car":
        await bot_controller.send_random_car(message)

    elif message.text == "🔍 Car search":
        await bot.send_message(message.chat.id, "To search type car name into chat", reply_markup=markups.search_menu)
        await state.set_state(SearchOrder.searching)

    elif message.text == "📄 Other":
        await bot.send_message(message.chat.id, "Not working yet", reply_markup=markups.other_menu)

    elif message.text == "🏠 Main Menu":
        await bot.send_message(message.chat.id, 'Press "🔍 Car search" to search the car\n'
                                                'Press "🎲 Random car" to get random car',
                               reply_markup=markups.main_menu)

    else:
        await bot.send_message(message.chat.id, 'Press "🔍 Car search" to search the car\n'
                                                'Press "🎲 Random car" to get random car',
                               reply_markup=markups.main_menu)


@dp.message_handler(state=SearchOrder.searching)
async def search(message: types.Message, state: FSMContext):
    if message.text == "🏠️ Main Menu":
        await bot.send_message(message.chat.id, 'Press "🔍 Car search" to search the car\n'
                                                'Press "🎲 Random car" to get random car',
                               reply_markup=markups.main_menu)
        return await state.finish()

    found_cars = await bot_controller.get_cars_by_search(message.text.lower())

    if not found_cars:
        await bot.send_message(message.chat.id, "Car doesn't exist. Try again!")
    else:
        inline_search_menu = await markups.get_inline_search_menu(found_cars, message.text.lower())
        message_found_cars = generate_message_found_cars(found_cars)
        await bot.send_message(message.chat.id, message_found_cars, reply_markup=inline_search_menu)


def generate_message_found_cars(found_cars):
    message_header = "Found car:" if len(found_cars) == 1 else "Found cars:"
    message_found_cars = [f"{i + 1}. {car['name']}" for i, car in enumerate(found_cars)]
    return "\n".join([message_header, *message_found_cars])


@dp.callback_query_handler(lambda c: c.data.startswith("car: "), state="*")
async def send_random_value(callback_query: types.CallbackQuery):
    await callback_query.answer()
    if callback_query.data.startswith("car: search: "):
        found_cars = await bot_controller.get_cars_by_search(callback_query.data.lstrip("car: search: "))
    else:
        found_cars = await bot_controller.get_cars_by_id(callback_query.data.lstrip("car: "))

    await bot_controller.send_cars(found_cars, callback_query.message.chat.id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


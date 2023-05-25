from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

btn_main = KeyboardButton("🏠️ Main Menu")

# --- Main Menu ---
btn_random = KeyboardButton("🎲 Random car")
btn_other = KeyboardButton("📄 Other")
btn_search = KeyboardButton("🔍 Car search")
main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_random, btn_other, btn_search)

# --- Other Menu ---
btn_info = KeyboardButton("Info")
btn_constructor = KeyboardButton("Constructor")
other_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_info, btn_constructor, btn_main)

# --- Search Menu ---
search_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_main)


# --- Inline search list ---
async def get_inline_search_menu(found_cars, text):
    inline_search_menu = InlineKeyboardMarkup()
    btn_all_cars = InlineKeyboardButton(text="All cars", callback_data=f"car: search: {text}")
    inline_search_menu.add(btn_all_cars)

    for i, car in enumerate(found_cars):
        btn_inline_car = InlineKeyboardButton(text=f"{i + 1}", callback_data=f"car: {car['id']}")
        inline_search_menu.add(btn_inline_car)

    return inline_search_menu




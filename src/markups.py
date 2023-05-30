from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

BUTTON_MAIN_MENU_TEXT = "🏠️ Main Menu"
BUTTON_RANDOM_TEXT = "🎲 Random car"
BUTTON_OTHER_TEXT = "📄 Other"
BUTTON_SEARCH_TEXT = "🔍 Car search"
BUTTON_CONSTRUCTOR_TEXT = "🚗 Constructor"

CALLBACK_DATA_BUTTON_CAR_TEXT = "car: "
CALLBACK_DATA_BUTTON_ALL_CARS_TEXT = "car: search: "
CALLBACK_DATA_BUTTON_AUDIO_TEXT = "audio: "


# --- Back to main menu ---
btn_main = KeyboardButton(BUTTON_MAIN_MENU_TEXT)

# --- Main Menu ---
btn_random = KeyboardButton(BUTTON_RANDOM_TEXT)
btn_other = KeyboardButton(BUTTON_OTHER_TEXT)
btn_search = KeyboardButton(BUTTON_SEARCH_TEXT)
main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_random, btn_other, btn_search)

# --- Other Menu ---
btn_constructor = KeyboardButton(BUTTON_CONSTRUCTOR_TEXT)
other_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_constructor, btn_main)

# --- Search Menu ---
search_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_main)

# --- Constructor Menu ---
constructor_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_main)


# --- Inline search list ---
async def get_inline_search_menu(found_cars, text):
    inline_search_menu = InlineKeyboardMarkup()

    btn_all_cars = InlineKeyboardButton(text="All cars", callback_data=CALLBACK_DATA_BUTTON_ALL_CARS_TEXT + text)
    inline_search_menu.add(btn_all_cars)

    for i, car in enumerate(found_cars):
        btn_inline_car = InlineKeyboardButton(text=f"{i + 1}", callback_data=CALLBACK_DATA_BUTTON_CAR_TEXT + str(car['id']))
        inline_search_menu.add(btn_inline_car)

    return inline_search_menu


# --- Inline voice button ---
def get_inline_voice_menu(car_id):
    inline_voice_menu = InlineKeyboardMarkup()
    btn_voice = InlineKeyboardButton(text="Audio version", callback_data=CALLBACK_DATA_BUTTON_AUDIO_TEXT + str(car_id))
    inline_voice_menu.add(btn_voice)
    return inline_voice_menu

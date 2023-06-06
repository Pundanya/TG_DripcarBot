from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

BUTTON_MAIN_MENU_TEXT = "🏠️ Main Menu"
BUTTON_RANDOM_TEXT = "🎲 Random car"
BUTTON_OTHER_TEXT = "📄 Other"
BUTTON_SEARCH_TEXT = "🔍 Car search"
BUTTON_CONSTRUCTOR_TEXT = "🚗 Constructor"
BUTTON_TEST_TEXT = "MEGATEST"

BUTTON_CONTINUE_TEXT = "✅ Continue"
BUTTON_REPEAT_TEXT = "🔄 Repeat"

CALLBACK_DATA_BUTTON_CAR = "car: "
CALLBACK_DATA_BUTTON_ALL_CARS = "car: search: "
CALLBACK_DATA_BUTTON_AUDIO = "audio: "
CALLBACK_DATA_BUTTON_CONTINUE = "Continue"
CALLBACK_DATA_BUTTON_REPEAT = "Repeat"


# --- Back to main menu ---
btn_main = KeyboardButton(BUTTON_MAIN_MENU_TEXT)

# --- Main Menu ---
btn_random = KeyboardButton(BUTTON_RANDOM_TEXT)
btn_other = KeyboardButton(BUTTON_OTHER_TEXT)
btn_search = KeyboardButton(BUTTON_SEARCH_TEXT)
btn_test = KeyboardButton(BUTTON_TEST_TEXT)
main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_random, btn_other, btn_search, btn_test)

# --- Other Menu ---
btn_constructor = KeyboardButton(BUTTON_CONSTRUCTOR_TEXT)
other_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_constructor, btn_main)

# --- Search Menu ---
search_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_main)

# --- CONSTRUCTOR ---
# --- Main menu ---
constructor_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_main)

# --- Inline continue repeat buttons ---
inline_continue_repeat_buttons = InlineKeyboardMarkup()
btn_inline_continue = InlineKeyboardButton(BUTTON_CONTINUE_TEXT, callback_data=CALLBACK_DATA_BUTTON_CONTINUE)
btn_inline_repeat = InlineKeyboardButton(BUTTON_REPEAT_TEXT, callback_data=CALLBACK_DATA_BUTTON_REPEAT)
inline_continue_repeat_buttons.insert(btn_inline_continue)
inline_continue_repeat_buttons.insert(btn_inline_repeat)


# --- Inline search list ---
async def get_inline_search_menu(found_cars, text):
    inline_search_menu = InlineKeyboardMarkup()

    for i, car in enumerate(found_cars):
        btn_inline_car = InlineKeyboardButton(text=f"{i + 1}", callback_data=CALLBACK_DATA_BUTTON_CAR + str(car.id))
        inline_search_menu.insert(btn_inline_car)

    btn_all_cars = InlineKeyboardButton(text="All cars", callback_data=CALLBACK_DATA_BUTTON_ALL_CARS + text)
    inline_search_menu.add(btn_all_cars)

    return inline_search_menu


# --- Inline voice button ---
def get_inline_voice_menu(car_id):
    inline_voice_menu = InlineKeyboardMarkup()
    btn_voice = InlineKeyboardButton(text="Audio version", callback_data=CALLBACK_DATA_BUTTON_AUDIO + str(car_id))
    inline_voice_menu.add(btn_voice)
    return inline_voice_menu

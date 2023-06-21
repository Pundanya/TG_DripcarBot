from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

BUTTON_MAIN_MENU_TEXT = "🏠️ Main Menu"
BUTTON_RANDOM_TEXT = "🎲 Random car"
BUTTON_OTHER_TEXT = "📄 Other"
BUTTON_SEARCH_TEXT = "🔍 Car search"
BUTTON_CONSTRUCTOR_TEXT = "🚗 Constructor"
BUTTON_CUT_TEXT = "✂️ Cut"
BUTTON_MUSIC_TEXT = "🎵 Music"
BUTTON_SAMPLES_TEXT = "🎧 Samples"
BUTTON_TEST_TEXT = "MEGATEST"

BUTTON_CONTINUE_TEXT = "✅ Continue"
BUTTON_REPEAT_TEXT = "🔄 Repeat"

CALLBACK_DATA_BUTTON_CAR = "car: "
CALLBACK_DATA_BUTTON_ALL_CARS = "car: search: "
CALLBACK_DATA_BUTTON_AUDIO = "audio: "
CALLBACK_DATA_BUTTON_CONTINUE = "Continue"
CALLBACK_DATA_BUTTON_REPEAT = "Repeat"
CALLBACK_DATA_BUTTON_STATS = "Stats: "
CALLBACK_DATA_BUTTON_LIKE = "like:"
CALLBACK_DATA_BUTTON_DISLIKE = "Dislike: "
CALLBACK_DATA_BUTTON_All_STATS = "All Stats: "
CALLBACK_DATA_BUTTON_MUSIC_SAMPLE = "Music sample: "


# --- Back to main menu ---
btn_main = KeyboardButton(BUTTON_MAIN_MENU_TEXT)

# --- Main Menu ---
btn_random = KeyboardButton(BUTTON_RANDOM_TEXT)
btn_other = KeyboardButton(BUTTON_OTHER_TEXT)
btn_search = KeyboardButton(BUTTON_SEARCH_TEXT)
main_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_random, btn_other, btn_search)
# btn_test = KeyboardButton(BUTTON_TEST_TEXT)
# main_menu.add(btn_test)

# --- Other Menu ---
btn_constructor = KeyboardButton(BUTTON_CONSTRUCTOR_TEXT)
other_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_constructor, btn_main)

# --- Search Menu ---
search_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_main)

# --- CONSTRUCTOR ---
# --- Main menu ---
constructor_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_main)

# --- Audio Edit ---
audio_edit_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_continue = KeyboardButton(BUTTON_CONTINUE_TEXT)
btn_cut = KeyboardButton(BUTTON_CUT_TEXT)
btn_music = KeyboardButton(BUTTON_MUSIC_TEXT)
audio_edit_menu.row(btn_continue, btn_cut, btn_music)
audio_edit_menu.add(btn_main)

# --- Music Edit ---
music_edit_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_samples = KeyboardButton(BUTTON_SAMPLES_TEXT)
music_edit_menu.row(btn_continue, btn_cut, btn_samples)
music_edit_menu.add(btn_main)


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

    btn_like = InlineKeyboardButton(text="👍", callback_data=f"{CALLBACK_DATA_BUTTON_STATS}{CALLBACK_DATA_BUTTON_LIKE}{str(car_id)}")
    btn_dislike = InlineKeyboardButton(text="👎", callback_data=f"{CALLBACK_DATA_BUTTON_STATS}{CALLBACK_DATA_BUTTON_DISLIKE}{str(car_id)}")
    btn_views = InlineKeyboardButton(text="👀 Stats", callback_data=f"{CALLBACK_DATA_BUTTON_STATS}{CALLBACK_DATA_BUTTON_All_STATS}{str(car_id)}")
    inline_voice_menu.add(btn_like, btn_dislike, btn_views)
    return inline_voice_menu


# --- Inline sample select ---
def get_inline_select_menu(sample_name):
    inline_select_menu = InlineKeyboardMarkup()
    btn_inline_select_sample = InlineKeyboardButton(text="✔️ Select", callback_data=f"{CALLBACK_DATA_BUTTON_MUSIC_SAMPLE}{sample_name}")
    inline_select_menu.add(btn_inline_select_sample)
    return inline_select_menu
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

BUTTON_MAIN_MENU_TEXT = "🏠️ Main Menu"
BUTTON_RANDOM_TEXT = "🎲 Random car"
BUTTON_OTHER_TEXT = "📄 Other"
BUTTON_SEARCH_TEXT = "🔍 Car search"
BUTTON_CONSTRUCTOR_TEXT = "🚗 Constructor"
BUTTON_AUDIO_EDIT_TEXT = "🔈Audio"
BUTTON_CUT_TEXT = "✂️ Cut"
BUTTON_MUSIC_EDIT_TEXT = "🎵 Music"
BUTTON_SAMPLES_TEXT = "🎧 Samples"
BUTTON_RESET_TEXT = "🔄 Reset"
BUTTON_TEST_TEXT = "MEGATEST"
BUTTON_INCREASE_VOLUME_TEXT = "🔊 Increase volume"
BUTTON_DECREASE_VOLUME_TEXT = "🔉 Decrease volume"
BUTTON_MY_CARS_TEXT = "🏎 My cars"
BUTTON_MY_STATS_TEXT = "📊 My statistics"
BUTTON_TOP_TEXT = "⭐️ TOP Cars"

BUTTON_BACK_TEXT = "⬅️ Back"
BUTTON_CONTINUE_TEXT = "✅ Continue"
BUTTON_REPEAT_TEXT = "🔄 Repeat"
BUTTON_ACCEPT_TEXT = "Accept"
BUTTON_DECLINE_TEXT = "Decline"

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
CALLBACK_DATA_MY_CAR = "My car: "
CALLBACK_DATA_REMOVE = "Remove: "
CALLBACK_DATA_ACCEPT = "Accept: "
CALLBACK_DATA_DECLINE = "Decline: "

# --- Buttons ---
btn_main = KeyboardButton(BUTTON_MAIN_MENU_TEXT)
btn_back = KeyboardButton(BUTTON_BACK_TEXT)

# --- Main Menu ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_random = KeyboardButton(BUTTON_RANDOM_TEXT)
btn_other = KeyboardButton(BUTTON_OTHER_TEXT)
btn_search = KeyboardButton(BUTTON_SEARCH_TEXT)
btn_top = KeyboardButton(BUTTON_TOP_TEXT)
btn_my_cars = KeyboardButton(BUTTON_MY_CARS_TEXT)
btn_constructor = KeyboardButton(BUTTON_CONSTRUCTOR_TEXT)
main_menu.insert(btn_random)
main_menu.insert(btn_my_cars)
main_menu.insert(btn_constructor)
main_menu.insert(btn_search)
main_menu.insert(btn_top)


# btn_test = KeyboardButton(BUTTON_TEST_TEXT)
# main_menu.add(btn_test)

# --- Other Menu ---
# other_menu = ReplyKeyboardMarkup(resize_keyboard=True)
# btn_my_cars = KeyboardButton(BUTTON_MY_CARS_TEXT)
# btn_constructor = KeyboardButton(BUTTON_CONSTRUCTOR_TEXT)
# other_menu.row(btn_constructor, btn_my_cars)
# other_menu.row(btn_main)

# --- My Cars menu ---
my_cars_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_statistics = KeyboardButton(BUTTON_MY_STATS_TEXT)
my_cars_menu.row(btn_statistics, btn_my_cars)
my_cars_menu.row(btn_main)

# --- My car ---
car_menu = ReplyKeyboardMarkup(resize_keyboard=True)
car_menu.row(btn_back, btn_main)

# --- Search Menu ---
search_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_main)

# --- CONSTRUCTOR ---
# --- Main menu ---
constructor_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_main)

# --- Drip audio Edit ---
drip_audio_edit_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_continue = KeyboardButton(BUTTON_CONTINUE_TEXT)
btn_audio = KeyboardButton(BUTTON_AUDIO_EDIT_TEXT)
btn_music = KeyboardButton(BUTTON_MUSIC_EDIT_TEXT)
drip_audio_edit_menu.row(btn_audio, btn_music)
drip_audio_edit_menu.row(btn_continue, btn_main)

# --- Audio Edit ---
audio_edit_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_increase_volume = KeyboardButton(BUTTON_INCREASE_VOLUME_TEXT)
btn_decrease_volume = KeyboardButton(BUTTON_DECREASE_VOLUME_TEXT)
btn_cut = KeyboardButton(BUTTON_CUT_TEXT)
btn_reset = KeyboardButton(BUTTON_RESET_TEXT)
audio_edit_menu.row(btn_increase_volume, btn_decrease_volume)
audio_edit_menu.row(btn_cut, btn_reset)
audio_edit_menu.row(btn_back, btn_main)

# --- Music Edit ---
music_edit_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_samples = KeyboardButton(BUTTON_SAMPLES_TEXT)
music_edit_menu.row(btn_increase_volume, btn_decrease_volume)
music_edit_menu.row(btn_cut, btn_samples, btn_reset)
music_edit_menu.row(btn_back, btn_main)


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


async def get_inline_my_cars_menu(found_cars, text):
    inline_search_menu = InlineKeyboardMarkup()

    for i, car in enumerate(found_cars):
        btn_inline_car = InlineKeyboardButton(text=f"{i + 1}", callback_data=CALLBACK_DATA_MY_CAR + str(car.id))
        inline_search_menu.insert(btn_inline_car)

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


def get_inline_remove_menu(car_id):
    inline_remove_menu = InlineKeyboardMarkup()
    btn_voice = InlineKeyboardButton(text="Audio version", callback_data=CALLBACK_DATA_BUTTON_AUDIO + str(car_id))
    inline_remove_menu.row(btn_voice)
    btn_remove = InlineKeyboardButton(text="❌ Remove", callback_data=CALLBACK_DATA_REMOVE + str(car_id))
    btn_views = InlineKeyboardButton(text="👀 Stats", callback_data=f"{CALLBACK_DATA_BUTTON_STATS}{CALLBACK_DATA_BUTTON_All_STATS}{str(car_id)}")
    inline_remove_menu.row(btn_remove, btn_views)
    return inline_remove_menu


def get_inline_sure_menu(car_id):
    inline_sure_menu = InlineKeyboardMarkup()
    btn_accept = InlineKeyboardButton(text=BUTTON_ACCEPT_TEXT, callback_data=CALLBACK_DATA_ACCEPT + car_id)
    btn_decline = InlineKeyboardButton(text=BUTTON_DECLINE_TEXT, callback_data=CALLBACK_DATA_DECLINE + car_id)
    inline_sure_menu.row(btn_accept, btn_decline)
    return inline_sure_menu


# --- Inline sample select ---
def get_inline_select_menu(sample_name):
    inline_select_menu = InlineKeyboardMarkup()
    btn_inline_select_sample = InlineKeyboardButton(text="✔️ Select", callback_data=f"{CALLBACK_DATA_BUTTON_MUSIC_SAMPLE}{sample_name}")
    inline_select_menu.add(btn_inline_select_sample)
    return inline_select_menu

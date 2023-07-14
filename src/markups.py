import db_controller
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

BUTTON_START_TEXT = "🚦 Start"
BUTTON_MAIN_MENU_TEXT = "🏠️ Main Menu"
BUTTON_RANDOM_TEXT = "🎲 Random car"
BUTTON_OTHER_TEXT = "📄 Other"
BUTTON_SEARCH_TEXT = "🔍 Car search"
BUTTON_CNSTR_TEXT = "🏗 Constructor"
BUTTON_AUDIO_EDIT_TEXT = "🎶 Audio 1"
BUTTON_CUT_TEXT = "✂️ Cut"
BUTTON_MUSIC_EDIT_TEXT = "🎵 Audio 2"
BUTTON_SAMPLES_TEXT = "🎧 Template songs"
BUTTON_RESET_TEXT = "🔄 Reset"
BUTTON_TEST_TEXT = "MEGATEST"
BUTTON_INCREASE_VOLUME_TEXT = "🔊 Increase volume"
BUTTON_DECREASE_VOLUME_TEXT = "🔉 Decrease volume"
BUTTON_NEW_AUDIO_TEXT = "🆕 New audio"
BUTTON_IMAGE_TEXT = "🖼 Image"
BUTTON_MY_CARS_TEXT = "🚙 My cars"
BUTTON_MY_STATS_TEXT = "📊 My statistics"
BUTTON_TOP_TEXT = "⭐️ TOP Cars"
BUTTON_SUBSCRIPTIONS_TEXT = "📝 Subscription"
BUTTON_TIME_TEXT = "🕘 Message time"
BUTTON_CANCEL_TEXT = "⛔️ Cancel"
BUTTON_SUBSCRIBE_TEXT = "🪤 Subscribe"
BUTTON_RANDOM_SUB_TEXT = "Random"
BUTTON_DAILY_TEXT = "New releases"

BUTTON_BACK_TEXT = "⬅️ Back"
BUTTON_CONTINUE_TEXT = "✅ Continue"
BUTTON_ACCEPT_TEXT = "✅ Accept"
BUTTON_DECLINE_TEXT = "❌ Decline"
BUTTON_REMOVE_TEXT = "🚮 Remove"

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
CALLBACK_DATA_RANDOM_SUB = "Random sub: "
CALLBACK_DATA_DAILY_SUB = "Daily sub"
CALLBACK_DATA_TIME = "Time: "

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
btn_cnstr = KeyboardButton(BUTTON_CNSTR_TEXT)
btn_subscription = KeyboardButton(BUTTON_SUBSCRIPTIONS_TEXT)
main_menu.insert(btn_search)
main_menu.insert(btn_random)
main_menu.insert(btn_top)
main_menu.insert(btn_cnstr)
main_menu.insert(btn_my_cars)
main_menu.insert(btn_subscription)

# --- Back main menu ---
back_main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
back_main_menu.row(btn_back, btn_main)

# --- Main menu ---
main_only_menu = ReplyKeyboardMarkup(resize_keyboard=True).insert(btn_main)


# --- My Cars menu ---
my_cars_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_statistics = KeyboardButton(BUTTON_MY_STATS_TEXT)
my_cars_menu.row(btn_statistics)
my_cars_menu.row(btn_main)

# --- Search Menu ---
search_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_main)

# --- Subscription ---
# --- Subscribe menu ---
subscribe_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_subscribe = KeyboardButton(BUTTON_SUBSCRIBE_TEXT)
subscribe_menu.row(btn_subscribe)
subscribe_menu.row(btn_main)


# --- Inline Subscription choosing ---
async def get_inline_subscription_menu(tg_id):
    sub_choosing_menu = InlineKeyboardMarkup()
    daily, random = await db_controller.check_subscriptions(tg_id)
    time = await db_controller.get_sub_time(tg_id)
    btn_sub_random = InlineKeyboardButton("❌ " * (not random) + "✅ " * random + BUTTON_RANDOM_SUB_TEXT,
                                          callback_data=CALLBACK_DATA_RANDOM_SUB + str(tg_id))
    btn_sub_daily = InlineKeyboardButton("❌ " * (not daily) + "✅ " * daily + BUTTON_DAILY_TEXT,
                                         callback_data=CALLBACK_DATA_DAILY_SUB + str(tg_id))
    btn_time = InlineKeyboardButton(f"{BUTTON_TIME_TEXT}(UTC±0): {time}", callback_data=CALLBACK_DATA_TIME + str(tg_id))
    sub_choosing_menu.row(btn_sub_daily, btn_sub_random)
    sub_choosing_menu.row(btn_time)
    return sub_choosing_menu


# --- CNSTR ---

# --- Drip audio Edit ---
drip_audio_edit_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_continue = KeyboardButton(BUTTON_CONTINUE_TEXT)
btn_audio = KeyboardButton(BUTTON_AUDIO_EDIT_TEXT)
btn_music = KeyboardButton(BUTTON_MUSIC_EDIT_TEXT)
btn_image = KeyboardButton(BUTTON_IMAGE_TEXT)
drip_audio_edit_menu.row(btn_audio, btn_music, btn_image)
drip_audio_edit_menu.row(btn_continue, btn_main)

# --- Audio Edit ---
audio_edit_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_increase_volume = KeyboardButton(BUTTON_INCREASE_VOLUME_TEXT)
btn_decrease_volume = KeyboardButton(BUTTON_DECREASE_VOLUME_TEXT)
btn_cut = KeyboardButton(BUTTON_CUT_TEXT)
btn_new_audio = KeyboardButton(BUTTON_NEW_AUDIO_TEXT)
btn_reset = KeyboardButton(BUTTON_RESET_TEXT)
audio_edit_menu.row(btn_increase_volume, btn_decrease_volume, btn_cut)
audio_edit_menu.row(btn_reset, btn_new_audio)
audio_edit_menu.row(btn_back, btn_main)

# --- Music Edit ---
music_edit_menu = ReplyKeyboardMarkup(resize_keyboard=True)
btn_remove = KeyboardButton(BUTTON_REMOVE_TEXT)
btn_samples = KeyboardButton(BUTTON_SAMPLES_TEXT)
music_edit_menu.row(btn_increase_volume, btn_decrease_volume, btn_cut)
music_edit_menu.row(btn_reset, btn_remove)
music_edit_menu.row(btn_back, btn_main)

music_receive_menu = ReplyKeyboardMarkup(resize_keyboard=True)
music_receive_menu.row(btn_samples)
music_receive_menu.row(btn_back, btn_main)


# --- Inline search list ---
async def get_inline_search_menu(found_cars, text):
    inline_search_menu = InlineKeyboardMarkup()

    for i, car in enumerate(found_cars):
        btn_inline_car = InlineKeyboardButton(text=f"{i + 1}", callback_data=CALLBACK_DATA_BUTTON_CAR + str(car.id))
        inline_search_menu.insert(btn_inline_car)

    btn_all_cars = InlineKeyboardButton(text="All cars", callback_data=CALLBACK_DATA_BUTTON_ALL_CARS + text)
    inline_search_menu.add(btn_all_cars)

    return inline_search_menu


async def get_inline_my_cars_menu(found_cars):
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

    btn_like = InlineKeyboardButton(text="👍",
                                    callback_data=f"{CALLBACK_DATA_BUTTON_STATS}{CALLBACK_DATA_BUTTON_LIKE}{str(car_id)}")
    btn_dislike = InlineKeyboardButton(text="👎",
                                       callback_data=f"{CALLBACK_DATA_BUTTON_STATS}{CALLBACK_DATA_BUTTON_DISLIKE}{str(car_id)}")
    btn_views = InlineKeyboardButton(text="👀 Stats",
                                     callback_data=f"{CALLBACK_DATA_BUTTON_STATS}{CALLBACK_DATA_BUTTON_All_STATS}{str(car_id)}")
    inline_voice_menu.add(btn_like, btn_dislike, btn_views)
    return inline_voice_menu


def get_inline_remove_menu(car_id):
    inline_remove_menu = InlineKeyboardMarkup()
    btn_voice = InlineKeyboardButton(text="Audio version", callback_data=CALLBACK_DATA_BUTTON_AUDIO + str(car_id))
    inline_remove_menu.row(btn_voice)
    btn_remove = InlineKeyboardButton(text="❌ Remove", callback_data=CALLBACK_DATA_REMOVE + str(car_id))
    btn_views = InlineKeyboardButton(text="👀 Stats",
                                     callback_data=f"{CALLBACK_DATA_BUTTON_STATS}{CALLBACK_DATA_BUTTON_All_STATS}{str(car_id)}")
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
    btn_inline_select_sample = InlineKeyboardButton(text="✔️ Select",
                                                    callback_data=f"{CALLBACK_DATA_BUTTON_MUSIC_SAMPLE}{sample_name}")
    inline_select_menu.add(btn_inline_select_sample)
    return inline_select_menu

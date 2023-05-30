import json
import requests
import re

AWESOME_CARS_JS = "https://awesomecars.neocities.org/search.js"
ALL_CARS_JSON = "data/all_cars.json"
CARS_MP4_FOLDER_PATH = "data/cars/cars_mp4"
CARS_MP3_FOLDER_PATH = "data/cars/cars_mp3"


def get_all_cars():
    with open(ALL_CARS_JSON) as file:
        all_cars = json.load(file)
        return all_cars


def get_car_mp4_path_by_id(car_id):
    car_path = f"{CARS_MP4_FOLDER_PATH}/{car_id}.mp4"
    return car_path


def get_car_mp3_path_by_id(car_id):
    car_path = f"{CARS_MP3_FOLDER_PATH}/{car_id}.mp3"
    return car_path


def get_len():
    return len(get_all_cars())


def get_car_name(car_id):
    all_cars = get_all_cars()
    car_name = all_cars[f"{car_id}"]
    return car_name


# Update all_cars.json from search awesomecars
def update_all_cars_data():
    search_data = requests.get(AWESOME_CARS_JS).text
    matches = re.finditer(r'\"#([\d,]*) - (.*)\"', search_data)

    all_cars_json_data = {}
    with open("../data/all_cars.json", "w") as file:
        for x in matches:
            car_id = x.group(1).replace(",", "")
            car_name = x.group(2)
            all_cars_json_data[car_id] = car_name
        json.dump(all_cars_json_data, file)

import json
import requests
import re

AWESOME_CARS_JS = "https://awesomecars.neocities.org/search.js"


def get_all_cars():
    with open("./data/all_cars.json") as file:
        all_cars = json.load(file)
        return all_cars


def get_car_path_by_id(index):
    car_path = f"https://awesomecars.neocities.org/ver2/{index}.mp4"
    return car_path


def get_secret_car_path():
    return "data/output/rusi.mp4"


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

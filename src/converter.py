import subprocess

import cv2
import numpy as np
from sklearn.cluster import KMeans


CONSTRUCTOR_RESULT_PATH = "data/constructor/result/car_video"


async def audio_mix(input_file, input_file_2, output_file):
    command = ['ffmpeg', '-i', input_file, '-i', input_file_2, "-filter_complex", "amix=inputs=2:duration=longest", "-y", output_file]
    subprocess.call(command)


def convert_car_mp4_to_mp3(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, "-y", output_file]
    subprocess.call(command)


async def normalize_audio(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, "-filter:a", "volume=1.5, lowshelf=g=20", "-y", output_file]
    subprocess.call(command)


def convert_to_mp3(path, file_extension):
    input_file = path + file_extension
    output_file = path + "mp3"
    command = ['ffmpeg', '-i', input_file, "-y", output_file]
    subprocess.call(command)


def cut_start_mp3(input_file, output_file, start_time):
    command = ['ffmpeg', '-i', input_file, "-ss", f"00:{start_time}", "-y", output_file]
    subprocess.call(command)


def cut_end_mp3(input_file, output_file, audio_time):
    audio_time = check_duration(audio_time)
    command = ['ffmpeg', '-i', input_file, "-t", f"00:00:{audio_time}", "-y", output_file]
    subprocess.call(command)


def logo_place_on_car_image(logo_path, chat_id):

    car_template_image = cv2.imread("data/constructor/template/car_template.png")
    logo_image = cv2.imread(logo_path)

    # Преобразование цветового пространства из BGR в HSV
    source_hsv = cv2.cvtColor(car_template_image, cv2.COLOR_BGR2HSV)
    target_hsv = cv2.cvtColor(logo_image, cv2.COLOR_BGR2HSV)

    # Плоский массив пикселей цветового канала Hue в целевом изображении
    hue_pixels = target_hsv[:, :, 0].flatten()

    # Кластерный анализ пикселей цветового канала Hue
    kmeans = KMeans(n_clusters=5, n_init=10)
    kmeans.fit(hue_pixels.reshape(-1, 1))

    # Находим индекс кластера с наибольшим количеством пикселей
    dominant_cluster_index = np.argmax(np.bincount(kmeans.labels_))

    # Находим среднее значение цвета в доминирующем кластере
    dominant_hue = int(kmeans.cluster_centers_[dominant_cluster_index])

    # Копирование исходного изображения для изменения
    modified_image = source_hsv.copy()

    # Изменение значений цветового канала Hue исходного изображения
    modified_image[:, :, 0] = dominant_hue

    # Преобразование обратно в цветовое пространство BGR
    modified_image = cv2.cvtColor(modified_image, cv2.COLOR_HSV2BGR)

    # # Сохранение измененного изображения
    # cv2.imwrite("output_image.jpg", modified_image)

    # Изменение размера фона до нужного размера
    modified_image = cv2.resize(modified_image, (240, 240))

    # Изменение размера наложения до нужного размера
    logo_image = cv2.resize(logo_image, (60, 60))

    # Наложение изображения на фон в определенном месте
    x = 160
    y = 125
    modified_image[y:y + logo_image.shape[0], x:x + logo_image.shape[1]] = logo_image

    car_image_path = f'data/constructor/result/car_images/result_{chat_id}.jpg'

    # Сохранение результата
    cv2.imwrite(car_image_path, modified_image)

    return car_image_path


def create_car_video_from_logo_and_audio(logo_path, audio_path, chat_id):
    car_image_path = logo_place_on_car_image(logo_path, chat_id)
    output_file_path = f"{CONSTRUCTOR_RESULT_PATH}/car_{chat_id}.mp4"


    duration = float(subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
         audio_path]))
    duration = check_duration(duration)

    command = ['ffmpeg', '-loop', '1', '-i', car_image_path, '-i', audio_path, "-s", "240x240", "-y", '-t', str(duration), '-preset', 'superfast', '-crf', '30', '-c:v', 'libx265', output_file_path]

    subprocess.call(command)

    return output_file_path


def check_duration(user_duration):
    desired_duration = 20

    return min(user_duration, desired_duration)


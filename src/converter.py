import subprocess

import cv2
import numpy as np
from sklearn.cluster import KMeans

CONSTRUCTOR_RESULT_PATH = "data/constructor/result/car_video"


# old
def resize_car_mp4(input_file):
    output_file = ''
    command = ['ffmpeg', '-i', input_file, "-s", "240x240", "-y", output_file]
    subprocess.call(command)


def convert_car_mp4_to_mp3(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, "-y", output_file]
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

    desired_duration = 20
    duration = float(subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
         audio_path]))
    duration = min(duration, desired_duration)

    command = ['ffmpeg', '-loop', '1', '-i', car_image_path, '-i', audio_path, "-s", "240x240", "-y", '-t', str(duration), '-preset', 'superfast', '-crf', '30', '-c:v', 'libx265', output_file_path]

    subprocess.call(command)

    return output_file_path


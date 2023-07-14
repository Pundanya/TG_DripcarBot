import subprocess
import ffmpeg
import cv2
import numpy as np
from sklearn.cluster import KMeans


CNSTR_RESULT_PATH = "data/constructor/result/car_video"


# async def audio_mix(input_file, input_file_2, output_file):
#     command = ['ffmpeg', '-i', input_file, '-i', input_file_2, "-filter_complex", "amix=inputs=2:duration=longest", "-y", output_file]
#     subprocess.call(command)

def audio_mix(input_file, input_file_2, output_file):
    input_file = (
        ffmpeg
        .input(input_file)
    )
    input_file_2 = (
        ffmpeg
        .input(input_file_2)
    )

    (
        ffmpeg
        .filter((input_file, input_file_2), 'amix', inputs=2, duration="longest")
        .output(output_file)
        .overwrite_output()
        .run()
    )


# def convert_car_mp4_to_mp3(input_file, output_file):
#     command = ['ffmpeg', '-i', input_file, "-y", output_file]
#     subprocess.call(command)

def convert_car_mp4_to_mp3(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, format='mp3')
        .overwrite_output()
        .run()
    )

# async def increase_volume(input_file, output_file):
#     command = ['ffmpeg', '-i', input_file, "-filter:a", "volume=2", "-y", output_file]
#     subprocess.call(command)


def increase_volume(input_file, output_file):
    (
        ffmpeg
        .input(input_file).audio.filter('volume', 2)
        .output(output_file)
        .overwrite_output()
        .run()
    )


# async def decrease_volume(input_file, output_file):
#     command = ['ffmpeg', '-i', input_file, "-filter:a", "volume=0.5", "-y", output_file]
#     subprocess.call(command)


def decrease_volume(input_file, output_file):
    (
        ffmpeg
        .input(input_file).audio.filter('volume', 0.5)
        .output(output_file)
        .overwrite_output()
        .run_async()
    )


# def convert_to_mp3(path, file_extension):
#     input_file = path + file_extension
#     output_file = path + "mp3"
#     command = ['ffmpeg', '-i', input_file, "-y", output_file]
#     subprocess.call(command)

def convert_to_mp3(path, file_extension):
    input_file = path + file_extension
    output_file = path + "mp3"

    (
        ffmpeg
        .input(input_file)
        .output(output_file)
        .overwrite_output()
        .run()
    )


# def cut_start_mp3(input_file, output_file, start_time):
#     command = ['ffmpeg', '-i', input_file, "-ss", f"00:{start_time}", "-y", output_file]
#     subprocess.call(command)

def cut_start_mp3(input_file, output_file, start_time):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, ss=f'00:{start_time}')
        .overwrite_output()
        .run()
    )


# def cut_end_mp3(input_file, output_file, audio_time):
#     audio_time = check_duration(audio_time)
#     command = ['ffmpeg', '-i', input_file, "-t", f"00:00:{audio_time}", "-y", output_file]
#     subprocess.call(command)

def cut_end_mp3(input_file, output_file, audio_time):
    audio_time = check_duration(audio_time)

    (
        ffmpeg
        .input(input_file)
        .output(output_file, t=f'00:00:{audio_time}')
        .overwrite_output()
        .run()
    )


def logo_place_on_car_image(logo_path, chat_id):
    car_template_image = cv2.imread("data/constructor/template/car_template.png")
    logo_image = cv2.imread(logo_path)

    source_hsv = cv2.cvtColor(car_template_image, cv2.COLOR_BGR2HSV)
    target_hsv = cv2.cvtColor(logo_image, cv2.COLOR_BGR2HSV)

    hue_pixels = target_hsv[:, :, 0].flatten()

    kmeans = KMeans(n_clusters=5, n_init=10)
    kmeans.fit(hue_pixels.reshape(-1, 1))

    dominant_cluster_index = np.argmax(np.bincount(kmeans.labels_))
    dominant_hue = int(kmeans.cluster_centers_[dominant_cluster_index])

    modified_image = source_hsv.copy()
    modified_image[:, :, 0] = dominant_hue
    modified_image = cv2.cvtColor(modified_image, cv2.COLOR_HSV2BGR)
    modified_image = cv2.resize(modified_image, (240, 240))

    logo_image = cv2.resize(logo_image, (60, 60))

    x = 160
    y = 125
    modified_image[y:y + logo_image.shape[0], x:x + logo_image.shape[1]] = logo_image

    car_image_path = f'data/constructor/result/car_images/result_{chat_id}.jpg'
    cv2.imwrite(car_image_path, modified_image)
    return car_image_path


def create_car_video_from_logo_and_audio(logo_path, audio_path, chat_id):
    car_image_path = logo_place_on_car_image(logo_path, chat_id)
    output_file_path = f"{CNSTR_RESULT_PATH}/car_{chat_id}.mp4"

    # duration = float(subprocess.check_output(
    #     ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
    #      audio_path]))
    probe = ffmpeg.probe(audio_path)
    audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    duration = float(audio_stream['duration'])
    duration = check_duration(duration)

    v1 = ffmpeg.input(car_image_path)
    a1 = ffmpeg.input(audio_path)
    (
        ffmpeg
        .output(v1.video, a1.audio, output_file_path, s='240x240', t=duration, preset='superfast', crf=30, vcodec="libx265")
        .overwrite_output()
        .run()
    )

    return output_file_path


def check_duration(user_duration):
    desired_duration = 20

    return int(min(user_duration, desired_duration))

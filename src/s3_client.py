import boto3
import bot_controller

from os import environ

# Bucket structure:
# main bucket: miniocars
# folders: cars_mp4, cars_mp3

MAIN_BUCKET = "miniocars"
CARS_MP4_PATH = "/cars_mp4"
CARS_MP3_PATH = "/cars_mp3"

s3_url = environ.get('S3_URL')
minio_id = environ.get('MINIO_ID')
minio_key = environ.get('MINIO_KEY')
s3 = boto3.resource('s3',
                    endpoint_url=s3_url,
                    aws_access_key_id=minio_id,
                    aws_secret_access_key=minio_key,
                    aws_session_token=None,
                    config=boto3.session.Config(signature_version='s3v4'),
                    verify=False
                    )


async def download_car_mp4(car_id):
    s3.meta.client.download_file(MAIN_BUCKET, f"{CARS_MP4_PATH}/{car_id}.mp4", f"{bot_controller.TEMP_CARS_MP4_PATH}/{car_id}.mp4")


async def download_car_mp3(car_id):
    s3.meta.client.download_file(MAIN_BUCKET, f"{CARS_MP3_PATH}/{car_id}.mp3", f"{bot_controller.TEMP_CARS_MP3_PATH}/{car_id}.mp3")


async def upload_car_mp4(car_name, car_id):
    s3.meta.client.upload_file(f"{bot_controller.CNSTR_RESULT_PATH}/{car_name}.mp4", MAIN_BUCKET,
                               f"{CARS_MP4_PATH}/{car_id}.mp4")


async def upload_car_mp3(car_name, car_id):
    s3.meta.client.upload_file(f"{bot_controller.TEMP_CARS_MP3_PATH}/{car_name}.mp3", MAIN_BUCKET,
                               f"{CARS_MP3_PATH}/{car_id}.mp3")


async def delete_car_mp4_and_mp3(car_id):
    if await check_mp4(car_id):
        s3.meta.client.delete_object(Bucket=MAIN_BUCKET, Key=f"{CARS_MP4_PATH}/{car_id}.mp4")
    if await check_mp3(car_id):
        s3.meta.client.delete_object(Bucket=MAIN_BUCKET, Key=f"{CARS_MP3_PATH}/{car_id}.mp3")


async def check_mp4(car_id):
    try:
        s3.meta.client.head_object(Bucket=MAIN_BUCKET, Key=f"{CARS_MP4_PATH}/{car_id}.mp4")
        return True
    except:
        return False


async def check_mp3(car_id):
    try:
        s3.meta.client.head_object(Bucket=MAIN_BUCKET, Key=f"{CARS_MP3_PATH}/{car_id}.mp3")
        return True
    except:
        return False

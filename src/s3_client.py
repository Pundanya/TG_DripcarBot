import boto3
import bot_controller

MAIN_BUCKET = "miniocars"

s3 = boto3.resource('s3',
                    endpoint_url='http://127.0.0.1:9000',
                    aws_access_key_id='minioadmin',
                    aws_secret_access_key='minioadmin',
                    aws_session_token=None,
                    config=boto3.session.Config(signature_version='s3v4'),
                    verify=False
                    )


async def download_car_mp4(car_id):
    s3.meta.client.download_file(MAIN_BUCKET, f"/cars_mp4/{car_id}.mp4", f"{bot_controller.TEMP_CARS_MP4_PATH}/{car_id}.mp4")


async def download_car_mp3(car_id):
    s3.meta.client.download_file(MAIN_BUCKET, f"/cars_mp3/{car_id}.mp3", f"{bot_controller.TEMP_CARS_MP3_PATH}/{car_id}.mp3")


async def upload_car_mp4(car_name, car_id):
    s3.meta.client.upload_file(f"{bot_controller.CNSTR_RESULT_PATH}/{car_name}.mp4", MAIN_BUCKET,
                               f"/cars_mp4/{car_id}.mp4")


async def upload_car_mp3(car_name, car_id):
    s3.meta.client.upload_file(f"{bot_controller.TEMP_CARS_MP3_PATH}/{car_name}.mp3", MAIN_BUCKET,
                               f"/cars_mp3/{car_id}.mp3")


async def delete_car_mp4_and_mp3(car_id):
    if await check_mp4(car_id):
        s3.meta.client.delete_object(Bucket=MAIN_BUCKET, Key=f"/cars_mp4/{car_id}.mp4")
    if await check_mp3(car_id):
        s3.meta.client.delete_object(Bucket=MAIN_BUCKET, Key=f"/cars_mp3/{car_id}.mp3")


async def check_mp4(car_id):
    try:
        s3.meta.client.head_object(Bucket=MAIN_BUCKET, Key=f"/cars_mp4/{car_id}.mp4")
        return True
    except:
        return False


async def check_mp3(car_id):
    try:
        s3.meta.client.head_object(Bucket=MAIN_BUCKET, Key=f"/cars_mp3/{car_id}.mp3")
        return True
    except:
        return False

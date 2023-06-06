import boto3

s3 = boto3.resource('s3',
                    endpoint_url='http://127.0.0.1:9000',
                    aws_access_key_id='minioadmin',
                    aws_secret_access_key='minioadmin',
                    aws_session_token=None,
                    config=boto3.session.Config(signature_version='s3v4'),
                    verify=False
                    )


async def download_car_mp4(car_id):
    s3.meta.client.download_file("miniocars", f"/cars_mp4/{car_id}.mp4", f"data/temp/cars_mp4/{car_id}.mp4")


async def download_car_mp3(car_id):
    s3.meta.client.download_file("miniocars", f"/cars_mp3/{car_id}.mp3", f"data/temp/cars_mp3/{car_id}.mp3")


async def upload_car_mp4(car_name, car_id):
    s3.meta.client.upload_file(f"data/constructor/result/car_video/{car_name}.mp4", "miniocars",
                               f"/cars_mp4/{car_id}.mp4")


async def upload_car_mp3(car_name, car_id):
    s3.meta.client.upload_file(f"data/temp/cars_mp3/{car_name}.mp3", "miniocars",
                               f"/cars_mp3/{car_id}.mp3")


async def check_mp3(car_id):
    try:
        s3.meta.client.head_object(Bucket="miniocars", Key=f"/cars_mp3/{car_id}.mp3")
        return True
    except:
        return False



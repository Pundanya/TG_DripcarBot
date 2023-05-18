import subprocess


def resize_mp4(input_file):
    output_file = 'data/output/output.mp4'

    command = ['ffmpeg', '-i', input_file, "-s", "240x240", "-y", output_file]
    subprocess.call(command)


def convert_mp4_to_mp3(input_file):
    output_file = 'data/output/output.mp3'

    command = ['ffmpeg', '-i', input_file, "-y", output_file]
    subprocess.call(command)


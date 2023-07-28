FROM python:3.11.4-bookworm as builder

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY src ./src
COPY data/constructor ./data/constructor

CMD ["python3", "src/main.py"]


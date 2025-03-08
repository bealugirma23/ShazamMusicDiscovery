FROM python:3.9

WORKDIR /app

COPY requirements.txt .

ADD main.py .

RUN apt-get update && apt-get install -y ffmpeg && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "./main.py"]

FROM python:3.7-slim
RUN apt-get update
RUN pip install --upgrade pip
RUN apt-get install build-essential -y
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

ADD . /app
RUN export TZ=America/Bogota
EXPOSE 8000
CMD gunicorn --access-logfile - --bind 0.0.0.0:8000 main:app
FROM python:3.7.1-stretch

ENV FLASK_APP=app.py
ENV FLASK_DEBUG=1

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT flask run --host=0.0.0.0
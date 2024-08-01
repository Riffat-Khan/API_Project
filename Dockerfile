FROM python:3

ENV PYTHONUNBUFFERED 1

RUN mkdir /API
WORKDIR /API
COPY . /API/

RUN pip install -r requirements.txt
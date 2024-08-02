FROM python:3

WORKDIR /API_PROJECT
COPY . /API_PROJECT/

RUN pip install -r requirements.txt

FROM python:3.12.2-stretch

WORKDIR /app

RUN apt update &&\
    rm -rf ~/.cache &&\
    apt clean all

# python
WORKDIR /app
RUN pip install --upgrade pip &&\
    rm -rf ~/.cache
RUN pip install poetry
COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock
RUN poetry install

# files
WORKDIR /
COPY ./conf /app/conf
COPY ./codename_master /app/codename_master
COPY ./main.py /app/main.py

WORKDIR /app
ENTRYPOINT [ "/bin/bash" ]
VOLUME "/app"

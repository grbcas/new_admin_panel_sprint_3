FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache netcat-openbsd gcc musl-dev postgresql-dev

COPY . /app/

RUN  pip install --upgrade pip && \
     pip install -r requirements.txt --no-cache-dir

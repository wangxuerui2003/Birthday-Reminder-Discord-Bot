FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apk add --no-cache bash

COPY . .

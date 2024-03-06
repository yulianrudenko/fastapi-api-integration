FROM python:3.10.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /home/api

COPY ./ /home/api/

RUN pip install -r /home/api/requirements.txt

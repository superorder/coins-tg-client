FROM python:3

RUN pip install telethon requests flask

WORKDIR /app

COPY server.py .

CMD [ "python", "server.py" ]

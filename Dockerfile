FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


RUN adduser --disabled-password --no-create-home django-user

COPY . .

RUN chown -R django-user:django-user /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER django-user


ENTRYPOINT ["/entrypoint.sh"]

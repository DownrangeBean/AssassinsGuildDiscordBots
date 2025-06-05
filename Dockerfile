FROM alpine:latest
LABEL authors="james"

COPY bot.py /srv/AssassinsGuildBot/bot.py
COPY cogs /srv/AssassinsGuildBot/cogs
COPY requirements.txt /srv/AssassinsGuildBot/requirements.txt
COPY run.sh /srv/AssassinsGuildBot/run.sh

WORKDIR /srv/AssassinsGuildBot/

RUN apk update
RUN apk add python3 py3-virtualenv py3-pip

ENV PYTHONUNBUFFERED=True
ENTRYPOINT ["/bin/sh", "./run.sh"]
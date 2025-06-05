FROM alpine:latest
LABEL authors="james"

COPY bot.py /srv/AssassinsGuildBot/
COPY cogs /srv/AssassinsGuildBot/
COPY requirements.txt /srv/AssassinsGuildBot/
COPY run.sh /srv/AssassinsGuildBot/

RUN apk update
RUN apk add python py3-virtualenv py3-pip

ENTRYPOINT ["/srv/AssassinsGuildBot/run.sh"]
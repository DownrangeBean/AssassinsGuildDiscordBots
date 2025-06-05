FROM alpine:latest
LABEL authors="james"

COPY bot.py /srv/AssassinsGuildBot/
COPY cogs /srv/AssassinsGuildBot/
COPY requirements.txt /srv/AssassinsGuildBot/
COPY run.sh /srv/AssassinsGuildBot/

RUN apk update
RUN apk add python3 py3-virtualenv py3-pip
# just testing webhook for builds
ENTRYPOINT ["/srv/AssassinsGuildBot/run.sh"]
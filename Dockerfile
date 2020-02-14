FROM python:alpine3.10 AS base

RUN apk add gcc libc-dev linux-headers supervisor nginx openssl-dev

## need to pre-initialize to stop problems finding nginx pid correctly on startup
RUN touch /var/run/nginx.pid

## Remove default nginx website
RUN rm -f /etc/nginx/sites-available/default
RUN rm -rf /usr/share/nginx/html/*

WORKDIR /app
COPY src/requirements.txt /tmp
RUN export UWSGI_INCLUDES=/usr/include/
RUN pip3 install -r /tmp/requirements.txt

## Add a default user so we don't run as root and change the directories created
#  to be owned by this user
RUN addgroup -S chefteam && adduser -S chefdev -G chefteam
FROM python:alpine3.10 AS base

RUN apk add gcc libc-dev linux-headers supervisor nginx
RUN pip install uwsgi
COPY src/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY nginx/conf/nginx.conf /etc/nginx/nginx.conf
COPY uwsgi/conf/chefmoji.ini /etc/uwsgi/chefmoji.ini
COPY supervisord/conf/supervisord.conf /etc/supervisord.conf

## need to pre-initialize to stop problems finding nginx pid correctly on startup
RUN touch /var/run/nginx.pid

## Remove default nginx website
RUN rm -f /etc/nginx/sites-available/default
RUN rm -rf /usr/share/nginx/html/*

WORKDIR /app
COPY . .
RUN rm README

## Add a default user so we don't run as root and change the directories created
#  to be owned by this user
# RUN addgroup -S che && adduser -S bmapsdev -G bmaps
# RUN chown -R :bmaps /app /tmp

ENV FLASK_ENV=production

EXPOSE 5000

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
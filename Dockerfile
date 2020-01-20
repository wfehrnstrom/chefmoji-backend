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
RUN addgroup -S chefteam && adduser -S chefdev -G chefteam
RUN chown -R chefdev:chefteam /app /tmp /etc/nginx /etc/uwsgi /var/tmp/nginx /var/lib/nginx /var/log/nginx /var/run/nginx.pid 
RUN chmod -R ug=rwx /etc/nginx /etc/uwsgi /var/tmp/nginx /var/lib/nginx 
RUN chmod -R 755 /var/log/nginx /var/run/nginx.pid
RUN chmod ugoa=r /etc/supervisord.conf /etc/nginx/nginx.conf /etc/uwsgi/chefmoji.ini
RUN chmod -R ug+rwx /app
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
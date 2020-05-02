FROM python:3.6
EXPOSE 7000
RUN apt-get update && apt-get install gettext -y
ENV PYTHONUNBUFFERED 1
RUN pip install uwsgi

## install requirements, so they can be cached by Docker
RUN pip install django==2.0.12 pytz==2018.4 pillow==6.2.0 \
    mysqlclient==1.3.12 django-mptt==0.9.0 pyyaml==3.12 \
    django-hamlpy==1.1.1 \
    redis==2.10.6 django-redis-cache==2.1.1 aioredis==1.3.1 \
    requests==2.18.4 sentry-sdk==0.14.3 \
    aiohttp==3.6.2

RUN mkdir /opt/tulius
ADD tulius /opt/tulius/tulius
ADD djfw /opt/tulius/djfw
ADD websockets /opt/tulius/websockets
ADD manage.py /opt/tulius/manage.py
ADD requirements.txt /opt/tulius/requirements.txt
ADD wsgi.py /opt/tulius/wsgi.py
ADD async_app.py /opt/tulius/async_app.py
ADD settings.py /opt/tulius/settings.py
ADD settings_production.py /opt/tulius/settings_production.py

WORKDIR /opt/tulius

# update requirements
RUN pip install -r requirements.txt

RUN python manage.py compilemessages
CMD [ "uwsgi", "--socket", "0.0.0.0:7000", \
               "--protocol", "uwsgi", \
               "--max-requests", "5000", \
               "--threads", "4", \
               "--processes", "2", \
               "--master", \
               "--wsgi", "wsgi:application" ]

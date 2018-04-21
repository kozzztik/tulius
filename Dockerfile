FROM python:3.6
EXPOSE 7000
RUN apt-get update && apt-get install gettext -y
ENV PYTHONUNBUFFERED 1
RUN pip install uwsgi

## install requirements, so they can be cached by Docker
RUN pip install django==2.0.4 pytz==2018.4 pillow==5.1.0 \
    mysqlclient==1.3.12 django-mptt==0.9.0 pyyaml==3.12 \
    django-hamlpy==1.1.1 python-memcached==1.59 \
    django-memcache-status==1.3 raven==6.6.0 gevent==1.2.2 \
    redis==2.10.6 django-websocket-redis==0.5.1 \
    django-redis-cache==1.7.1 requests==2.18.4

RUN mkdir /opt/tulius
ADD tulius /opt/tulius/tulius
ADD django_mailer /opt/tulius/django_mailer
ADD djfw /opt/tulius/djfw
ADD events /opt/tulius/events
ADD pm /opt/tulius/pm
ADD websockets /opt/tulius/websockets
ADD manage.py /opt/tulius/manage.py
ADD requirements.txt /opt/tulius/requirements.txt
ADD wsgi.py /opt/tulius/wsgi.py
ADD wsgi_websocket.py /opt/tulius/wsgi_websocket.py
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

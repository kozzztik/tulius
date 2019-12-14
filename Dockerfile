FROM python:2.7-stretch
EXPOSE 7000
RUN apt-get update && apt-get install gettext locales -y
RUN locale-gen ru_RU.UTF-8
RUN sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen
RUN dpkg-reconfigure --frontend=noninteractive locales
ENV PYTHONUNBUFFERED 1
RUN pip install uwsgi

## install requirements, so they can be cached by Docker
RUN pip install django==1.6.3 pitz django-grappelli==2.4.12 pillow \
    MySQL-python south ipython simplejson django-mptt==0.7.4 \
    pygments hamlpy djaml django-appconf BeautifulSoup FeedParser \
    pyyaml python-memcached django-memcache-status raven gevent \
    redis django-websocket-redis django-redis-cache requests

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

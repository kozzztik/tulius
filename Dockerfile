FROM python:2.7
EXPOSE 7000
RUN apt-get update && apt-get install gettext locales -y
RUN locale-gen ru_RU.UTF-8
RUN dpkg-reconfigure --frontend=noninteractive locales
ENV PYTHONUNBUFFERED 1
RUN pip install uwsgi

## install requirements, so they can be cached by Docker
RUN pip install django==1.6.3 pitz django-grappelli==2.4.12 pillow \
    MySQL-python south ipython simplejson django-mptt==0.7.4 \
    pygments hamlpy djaml django-appconf BeautifulSoup FeedParser \
    pyyaml python-memcached django-memcache-status raven gevent \
    redis django-websocket-redis django-redis-cache requests
#RUN pip3 install django == 2.0.4
#RUN pip3 install pytz == 2018.4
#RUN pip3 install pillow == 5.1.0
#RUN pip3 install mysqlclient == 1.3.12
#RUN pip3 install django-mptt == 0.9.0
#RUN pip3 install pyyaml == 3.12
#RUN pip3 install django-hamlpy == 1.1.1
#RUN pip3 install python-memcached == 1.59
#RUN pip3 install django-memcache-status == 1.3
#RUN pip3 install raven == 6.6.0
#RUN pip3 install gevent == 1.2.2
#RUN pip3 install redis == 2.10.6
#RUN pip3 install django-websocket-redis == 0.5.1
#RUN pip3 install django-redis-cache == 1.7.1
#RUN pip3 install requests == 2.18.4

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

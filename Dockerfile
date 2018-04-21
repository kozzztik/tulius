FROM python:2.7
ENV PYTHONUNBUFFERED 1
## install requirements, so they can be cached by Docker
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
# application server
RUN pip install uwsgi

ADD tulius /opt/tulius
WORKDIR /opt
ADD . /opt/
# update requirements
RUN pip3 install -r requirements.txt
RUN python manage.py compilemessages
EXPOSE 7000
CMD [ "uwsgi", "--socket", "0.0.0.0:7000", \
               "--uid", "uwsgi", \
               "--plugins", "python", \
               "--protocol", "uwsgi", \
               "--max-requests", "5000", \
               "--threads", "4", \
               "--processes", "2", \
               "--master", "true", \
               "--wsgi", "wsgi:application" ]

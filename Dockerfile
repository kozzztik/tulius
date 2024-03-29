FROM kozzztik/tulius:base_3.1.0

RUN mkdir /opt/tulius/data
RUN pip install --upgrade pip
# for coveralls
RUN apt-get install git -y
ENV TULIUS_BRANCH local

ADD tulius /opt/tulius/tulius
ADD djfw /opt/tulius/djfw
ADD manage.py /opt/tulius/manage.py
ADD requirements.txt /opt/tulius/requirements.txt
ADD asgi.py /opt/tulius/asgi.py
ADD settings.py /opt/tulius/settings.py
ADD .pylintrc /opt/tulius/.pylintrc
ADD tests /opt/tulius/tests
ADD pytest.ini /opt/tulius/pytest.ini
ADD scripts/travis_test.sh /opt/tulius/travis_test.sh
RUN chmod +x /opt/tulius/travis_test.sh

# update requirements
RUN pip install -r requirements.txt
# for coveralls
ADD .git /opt/tulius/.git

RUN python manage.py compilemessages

ADD gunicorn.conf.py /opt/tulius/gunicorn.conf.py
CMD [ "gunicorn" ]

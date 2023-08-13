FROM kozzztik/tulius:base_3.1.0

RUN mkdir /opt/tulius/data
RUN pip install --upgrade pip
# for coveralls
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get update && apt-get install nodejs git -y
RUN npm install @vue/cli -g
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
RUN cd tulius/static && npm install && npm run build

ADD gunicorn.conf.py /opt/tulius/gunicorn.conf.py
CMD [ "gunicorn" ]

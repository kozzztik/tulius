FROM kozzztik/tulius:base_3.0.3

ADD tulius /opt/tulius/tulius
ADD djfw /opt/tulius/djfw
ADD manage.py /opt/tulius/manage.py
ADD requirements.txt /opt/tulius/requirements.txt
ADD wsgi.py /opt/tulius/wsgi.py
ADD async_app.py /opt/tulius/async_app.py
ADD settings.py /opt/tulius/settings.py
ADD .pylintrc /opt/tulius/.pylintrc
ADD tests /opt/tulius/tests
ADD pytest.ini /opt/tulius/pytest.ini
ADD scripts/travis_test.sh /opt/tulius/travis_test.sh
RUN chmod +x /opt/tulius/travis_test.sh

# update requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# for coveralls
RUN apt-get install git -y
ADD .git /opt/tulius/.git

ENV TULIUS_BRANCH local
RUN python manage.py compilemessages

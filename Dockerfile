FROM kozzztik/tulius:base_3.0.3

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get update && apt-get install nodejs git -y
RUN npm install @vue/cli -g
RUN pip install hypercorn==0.11.1
CMD [ "hypercorn", "-b", "0.0.0.0:7000", "-w", "2", "asgi:application" ]

ADD tulius /opt/tulius/tulius
ADD .git /opt/tulius/.git
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

ENV TULIUS_BRANCH local
RUN python manage.py compilemessages
RUN cd tulius/static && npm install && npm run build

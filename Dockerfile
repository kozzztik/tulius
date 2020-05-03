FROM kozzztik/tulius:base_3.0.1

ADD tulius /opt/tulius/tulius
ADD djfw /opt/tulius/djfw
ADD manage.py /opt/tulius/manage.py
ADD requirements.txt /opt/tulius/requirements.txt
ADD wsgi.py /opt/tulius/wsgi.py
ADD async_app.py /opt/tulius/async_app.py
ADD settings.py /opt/tulius/settings.py

# update requirements
RUN pip install -r requirements.txt

RUN python manage.py compilemessages

FROM sentry:9.1.0-onbuild
RUN apt-get update &&  apt-get install -y default-libmysqlclient-dev && pip install MySQL-python

COPY ./sentry.conf.py /etc/sentry/sentry.conf.py
COPY ./config.yml /etc/sentry/config.yml

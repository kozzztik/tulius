FROM ubuntu:xenial

COPY ./main.cf /etc/postfix/main.cf

RUN apt-get update && apt-get install -y postfix rsyslog && adduser postfix sasl && touch /var/log/mail.log

COPY ./main.cf /etc/postfix/main.cf

CMD service rsyslog start && service postfix start && tail -f /var/log/mail.log
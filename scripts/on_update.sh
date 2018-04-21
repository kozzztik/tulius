echo "do on update"

echo "Stop existing tulius_$1"
docker stop tulius_$1
docker rm tulius_$1
docker stop tulius_$1_ws
docker rm tulius_$1_ws

echo "Build docker container tulius_$1"
docker build -t tulius_$1 .

echo "Collect static"
docker run -v "$PWD/static":/opt/tulius/static \
    tulius_$1 python manage.py collectstatic --noinput

echo "Migrate"
docker run tulius_$1 python manage.py syncdb
docker run tulius_$1 python manage.py migrate

echo "Start docker container tulius_$1 on port $2"
docker run -d -p $2:7000 --name=tulius_$1 --restart=unless-stopped \
    -v "$PWD/media":/opt/tulius/media tulius_$1

echo "Start docker container tulius_$1_ws on port $3"
docker run -d -p $3:7000 --name=tulius_$1_ws --restart=unless-stopped \
    tulius_$1 uwsgi --socket 0.0.0.0:7000 --protocol uwsgi \
               --max-requests 10000 \
               --threads 2 \
               --processes 1 \
               --master \
               --http-websockets \
               --wsgi wsgi_websocket:application

echo "Done."

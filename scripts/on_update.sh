echo "do on update"

echo "Stop existing tulius_$1"
docker stop tulius_$1

echo "Build docker container tulius_$1"
docker build -t tulius_$1 .

echo "Collect static"
docker run -v "$PWD/static:/opt/tulius/static \
    tulius_$1 python manage.py collectstatic --noinput

echo "Migrate"
docker run -v "$PWD/static:/opt/tulius/static \
    tulius_$1 python manage.py syncdb
docker run -v "$PWD/static:/opt/tulius/static \
    tulius_$1 python manage.py migrate


echo "Start docker container tulius_$1 on port $2"
docker run -d -p 7000:$2 --name=tulius_$1 --restart=unless-stopped \
    -v "$PWD/media":/opt/tulius/media tulius_$1
echo "Done."

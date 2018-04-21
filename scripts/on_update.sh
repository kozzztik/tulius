echo "do on update"
. env/bin/activate
export DJANGO_SETTINGS_MODULE=settings-production
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py syncdb
python manage.py migrate
deactivate

echo "Stop existing tulius_$1"
docker stop tulius_$1

echo "Build docker container tulius_$1"
docker build -f Dockerfile -t tulius_$1

echo "Start docker container $1 on port $2"
docker run -d -p 7000:$2 --name=tulius_$1 -restart=unless-stopped \
    -v "$PWD/media":/opt/tulius/media tulius_$1
echo "Done."

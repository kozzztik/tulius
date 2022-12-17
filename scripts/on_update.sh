#!/usr/bin/env bash
set -ex
echo "do on update"

TULIUS_BRANCH=$1
ROOTDIR=$PWD

if [ $2 ]; then
  ENV=$2
  echo "Deploy $TULIUS_BRANCH on $ENV environment"
else
  ENV=TULIUS_BRANCH
fi
echo "Stop existing compose"
cd scripts/tulius/$ENV
# First stop web then wait till celery will finish all tasks
docker-compose stop
docker-compose exec celery python manage.py wait_celery || true
docker-compose down --remove-orphans
docker system prune --force
docker rm -v $(docker ps --filter status=exited -q 2>/dev/null) 2>/dev/null || true
docker rmi $(docker images --filter dangling=true -q 2>/dev/null) 2>/dev/null || true
cd $ROOTDIR

echo "Pull docker container tulius_$1"
docker pull kozzztik/tulius:$1

echo "Collect static"
docker run -v "$PWD/data/static":/opt/tulius/data/static \
    -e TULIUS_BRANCH="$ENV" \
    --net tuliusnet \
    -v "/home/travis/$ENV/settings_production.py":/opt/tulius/settings_production.py \
    kozzztik/tulius:$1 python manage.py collectstatic --noinput

echo "Migrate"
docker run \
    -e TULIUS_BRANCH="$ENV" \
    --net tuliusnet \
    -v "/home/travis/$ENV/settings_production.py":/opt/tulius/settings_production.py \
    kozzztik/tulius:$1 python manage.py migrate


echo "Run compose"

cd scripts/tulius/$ENV
docker-compose up -d --build --force-recreate
cd $ROOTDIR

echo "Done."

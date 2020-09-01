#!/bin/bash
set -ex
GIT_BRANCH=$1
export BRANCH_NAME=$(echo "$GIT_BRANCH" | sed 's/origin\///')
docker build -t kozzztik/tulius:${BRANCH_NAME} .

docker run -e TULIUS_BRANCH=test -e COV_BRANCH="$BRANCH_NAME" -e DJANGO_SETTINGS_MODULE="settings_production" --net="tuliusnet" \
-v /mnt/big/jenkins/settings_production.py:/opt/tulius/settings_production.py \
-v /mnt/big/jenkins/.coveralls.yml:/opt/tulius/.coveralls.yml \
kozzztik/tulius:${BRANCH_NAME} /opt/tulius/travis_test.sh

if [[ $BRANCH_NAME = dev ]] || [[ $BRANCH_NAME = master ]]
then
    docker push kozzztik/tulius:$BRANCH_NAME
    ssh -i /mnt/big/jenkins/travis_rsa travis@$BRANCH_NAME.tulius.co-de.org -p 22 "cd ~/$BRANCH_NAME && git fetch --all && git reset --hard && git pull --rebase"
	  ssh -i /mnt/big/jenkins/travis_rsa travis@$BRANCH_NAME.tulius.co-de.org -p 22 "cd ~/$BRANCH_NAME && . scripts/on_update.sh $BRANCH_NAME"
fi

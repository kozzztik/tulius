#!/bin/sh
set -ex
KEY=$1
ENV=$2
BRANCH=$3
COMMIT=$4
echo "Push to repo"
docker push kozzztik/tulius:$BRANCH

# Download updates
ssh -i $1 travis@$ENV.tulius.co-de.org -p 22 "cd ~/$ENV && git fetch --all && git reset --hard && git git checkout -b $BRANCH $COMMIT"
echo "Data updated"

# Do after deploy staff
ssh -i $1 travis@$ENV.tulius.co-de.org -p 22 "cd ~/$ENV && . scripts/on_update.sh $BRANCH $ENV"
echo "Finished."
eval "$GITHUB -d '{\"state\":\"success\",\"target_url\":\"$CI_JOB_URL\",\"description\":\"Deployed on $ENV\",\"context\":\"Deploy/Production\"}'"

#!/bin/sh
set -ex
ENV=$1
BRANCH=$2
COMMIT=$3
echo "Push to repo"
docker push kozzztik/tulius:$BRANCH

# Download updates
ssh -i /tmp/deploy_rsa travis@$ENV.tulius.co-de.org -p 22 "cd ~/$ENV && git fetch --all && git reset --hard && git git checkout -b $BRANCH $COMMIT"
echo "Data updated"

# Do after deploy staff
ssh -i /tmp/deploy_rsa travis@$ENV.tulius.co-de.org -p 22 "cd ~/$ENV && . scripts/on_update.sh $BRANCH $ENV"
echo "Finished."
eval "$GITHUB -d '{\"state\":\"success\",\"target_url\":\"$CI_JOB_URL\",\"description\":\"Deployed on $ENV\",\"context\":\"Deploy/Production\"}'"

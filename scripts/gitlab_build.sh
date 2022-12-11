#!/bin/bash
set -ex
REF=$1
COMMIT=$2
echo $COMMIT
BRANCH_NAME=$(echo "$REF" | sed 's/origin\///' | sed 's/refs\/heads\///')
echo $BRANCH_NAME
export GITHUB="curl -X POST -H \"Accept: application/vnd.github+json\" -H \"Authorization: Bearer $GITHUB_KEY\" https://api.github.com/repos/kozzztik/tulius/statuses/$COMMIT"

# export env variables for next stages
echo "BRANCH_NAME=$BRANCH_NAME" >> build.env
echo "REF=$REF" >> build.env
echo "COMMIT=$COMMIT" >> build.env
echo "GITHUB=$GITHUB" >> build.env
# set github pending status
eval "$GITHUB -d '{\"state\":\"pending\",\"target_url\":\"$CI_PIPELINE_URL\",\"description\":\"Build in progress\",\"context\":\"CI/GitLab\"}'"
docker build -t kozzztik/tulius:${BRANCH_NAME} .

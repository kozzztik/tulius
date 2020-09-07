#!/bin/bash
set -ex
echo "Running pylint"
python3 -m pylint djfw tulius tests
python3 -m pytest tests --cov=tulius --cov-report term-missing --cov-report term:skip-covered
TRAVIS_BRANCH=$GIT_BRANCH
echo "$TRAVIS_BRANCH"
coveralls

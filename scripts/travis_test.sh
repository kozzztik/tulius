#!/bin/bash
set -e
echo "Running pylint"
python3 -m pylint djfw tulius tests
python3 -m pytest tests --cov=tulius --cov-report term-missing
TRAVIS_BRANCH=$COV_BRANCH
coveralls

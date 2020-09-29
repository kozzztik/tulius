#!/bin/bash
set -ex
echo "Running pylint"
python3 -m pylint djfw tulius tests
python3 -m pytest djfw tulius tests --cov=tulius --cov-report term-missing --cov-report term:skip-covered
coveralls

set TULIUS_ENV=dev
python -m pytest djfw tulius tests --cov=tulius --cov-report term-missing --cov-report term:skip-covered

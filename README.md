[![Coverage Status](https://coveralls.io/repos/github/kozzztik/tulius/badge.svg?branch=dev)](https://coveralls.io/github/kozzztik/tulius)
[![Build status](https://travis-ci.org/kozzztik/tulius.svg?branch=dev "Travis")](https://travis-ci.org/kozzztik/tulius)
# Tulius
Repo for http://tulius.com project.
## Deployment instructions
1. Check basic requirements for target server:
    - [x] Docker and docker-compose installed
    - [x] SSH server with auth by keys
    - [x] Git installed

2. Create user for travis CI:
    ```bash
    sudo adduser travis
    sudo adduser travis docker
    ```
3. Checkout Tulius for production and QA environments:
    ```bash
    cd /home/travis
    git clone https://github.com/kozzztik/tulius.git master
    git clone https://github.com/kozzztik/tulius.git dev
    cd /home/travis/dev
    git checkout dev
    ```
4. Create data folders structure:
    ```bash
    mkdir /home/travis/master/data
    mkdir /home/travis/master/data/mysql
    mkdir /home/travis/master/data/static
    mkdir /home/travis/master/data/media
    mkdir /home/travis/master/data/elastic
    chown 1000:1000 /home/travis/master/data/elastic
    mkdir /home/travis/dev/data
    mkdir /home/travis/dev/data/static
    mkdir /home/travis/dev/data/media
    ```
5. Restore data from backup:
    - If you have mysql library files, place them to `/home/travis/master/data/mysql` to use existing database.
    - Put media files to `/home/travis/master/data/media` for production environment
    - Put media files to `/home/travis/dev/data/media` for QA environment
    - If you have SQL backup, place it into `/home/travis/master/data/mysql`folder.

6. Start common environment:
    ```bash
    cd /home/travis/master/scripts/tulius
    docker-compose up -d --build --force-recreate
    ``` 
7. If you not restored mysql from lib files, it will create empty database with random root password. 
    You can recognize it from docker logs:
    ```bash
    docker logs tulius_mysql 2>&1 | grep GENERATED
     ```
    Enter Mysql console:
    ```bash
    docker exec -it tulius_mysql mysql -uroot -p
    ```
    Change root password:
    ```sql
    ALTER USER root@'localhost' IDENTIFIED BY 'new root password';
    ```
    Create necessary databases and users:
    ```sql
    CREATE DATABASE tulius_prod;
    CREATE DATABASE tulius_qa;
    CREATE DATABASE sentry;
    GRANT ALL ON tulius_prod.* TO tulius_prod@'%' IDENTIFIED BY 'tulius prod password';
    GRANT ALL ON tulius_qa.* TO tulius_qa@'%' IDENTIFIED BY 'tulius qa password';
    GRANT ALL ON sentry.* TO sentry@'%' IDENTIFIED BY 'sentry';
    ``` 
    If you have SQL backup file, placed to mysql data folder:
    ```bash
    docker exec -it tulius_mysql /bin/bash
    mysql -uroot -p tulius_prod < /var/lib/mysql/backup.sql
    ```
 8. Create Sentry database and super user (not needed if DB restored from lib files):
     ```bash
    docker exec -it tulius_sentry sentry upgrade
    ```
 9. Use sentry web interface on `http://sentry.co-de.org` (check DNS records), to finalize installation. 
 Create two sentry projects and get DSN URLs for them.
 
10. Configure prod and dev environments.
    ```bash
    cd /home/travis/master
    cp settings_production.py.template settings_production.py
    cd /home/travis/dev
    cp settings_production.py.template settings_production.py
    ```
    Edit settings files. Change DB passwords and sentry DSN.
   
11. Install nginx. Configure it using templates:
    ```bash
    cp /home/travis/master/scripts/tulius/nginx/sentry.conf /etc/nginx/conf.d/sentry.conf
    cp /home/travis/master/scripts/tulius/nginx/tulius.conf /etc/nginx/conf.d/tulius.conf
    ```
    
12. Install letsEncrypt and configure SSL.

13. Check that known host in repo `.travis.yml` file and ssh host in `scripts/deploy.sh` points on target server. 
Update repo if needed (use separate branch and PR)

14. Trigger build on CI, or run it manually on server:
    ```bash
    cd /home/travis/master
    . scripts/on_update.sh master
    cd /home/travis/dev
    . scripts/on_update.sh dev
    ``` 
15. Check that everything works. Profit.

# Running on local environment

To run frontend part you need to install node.js & npm:
- for Windows use installer https://nodejs.org/en/download/ 
- for Linux (Debian based) ```apt-get install nodejs```

Then switch to tulius/static folder and run 
```
npm install -D
```

To use Tulius on local dev environment you need to run 4 instances. For both of them
it is needed to set environment variable:

```bash
TULIUS_BRANCH=local
``` 
So Tulius will understand a context and set needed configuration by default. 
If you need some special configuration options, you can create `settings_production.py`
file from template and set needed options there.

Instances, that needed to run:
1. `manage.py runserver` - Django instance for normal HTTP requests
2. `async_app.py` - for web sockets support
3. `celery -A tulius worker -l info` - for deferred tasks (optional)
4. `npm run start` in tulius/static directory for frontend webpack dev server
 
On Windows, as Celery not supports it yet, install gevent:

```pip install gevent```

and start celery with:

```celery -A tulius worker -l info -P gevent```

or, instead of starting Celery, you can switch it off, by adding:

```CELERY_TASK_ALWAYS_EAGER = True```

to settings_production.py. However, some heavy requests, like reindexing may
became too slow to render pages, as deferred tasks will be resolved in request 
context. But for most things it will be enough.

## Running tests

``` 
python -m pylint tests tulius djfw
python -m pytest tests tulius djfw
```

## Configure kibana access
```
sudo apt install apache2-utils
sudo touch /etc/nginx/htpasswd
sudo htpasswd /etc/nginx/htpasswd bob
```
## Remove elastic disk limit on dev environment
```
curl -XPUT "http://localhost:9200/_cluster/settings" \
 -H 'Content-Type: application/json' -d'
{
  "persistent": {
    "cluster": {
      "routing": {
        "allocation.disk.threshold_enabled": false
      }
    }
  }
}'
```

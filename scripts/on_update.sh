echo "do on update"
. env/bin/activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=settings-production
python manage.py collectstatic --noinput
python manage.py syncdb
python manage.py migrate
python manage.py compilemessages
deactivate
chown -R travis:www-data $PWD
chmod 775 $PWD
sudo /etc/init.d/uwsgi restart


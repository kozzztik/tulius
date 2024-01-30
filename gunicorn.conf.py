bind = ['0.0.0.0:7000']
workers = 2
django_settings = 'settings_production,settings'
max_requests = 500
keepalive = 60
preload_app = True
accesslog = '-'
disable_redirect_access_to_syslog = True
errorlog = '-'

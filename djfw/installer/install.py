import sys
import os
import subprocess

def read_file(dir, file_name):
    f = open(os.path.join(dir, file_name))
    try:
        return f.read()
    finally:
        f.close()
        
def write_file(dir, file_name, data):
    f = open(os.path.join(dir, file_name), 'w+')
    try:
        f.write(data)
    finally:
        f.close()
        
def delete_file(dir, name):
    file_path = os.path.join(dir, name)
    if os.path.exists(file_path):
        os.remove(file_path)
        
PROJECT_NAME = "%PWN%"
path = sys.path[0].replace('\\', '/')
bin_path = os.path.join(path, 'bin')
project_path = os.path.join(path, PROJECT_NAME)

FAIL_TEXT = "Install failed."
    
print "==================    Downloading buildout...    =================="
import bootstrap

print "==================      Downloading eggs...      =================="
code = subprocess.call(os.path.join(path, 'bin', 'buildout'), shell=True)
if code:
    print FAIL_TEXT
    sys.exit(1)

print "==================        Setting path...        =================="
workdir_py = """PROJECTDIR='%s/'
PROJECT_NAME='%s'
"""

write_file(path, 'workdir.py', workdir_py % (path, PROJECT_NAME))

vhost_cfg = read_file(path, 'vhost.conf.template')
write_file(path, 'vhost.conf', vhost_cfg.replace('%PWD%', path))

django_conf_name = 'django-script.py'
if not os.path.exists(os.path.join(bin_path, django_conf_name)):
    django_conf_name = 'django'
    
django_conf = read_file(bin_path, django_conf_name)
apache_conf = django_conf

repl_str = """import djangorecipe.manage
import os
os.environ['DJANGO_SETTINGS_MODULE'] = '$PROJECT_NAME.settings'
os.environ['PYTHON_EGG_CACHE'] = '$PROJECTDIR/tmp-eggs'
"""
repl_str = repl_str.replace('$PROJECT_NAME', PROJECT_NAME).replace('$PROJECTDIR', path)
django_conf = django_conf.replace('import djangorecipe.manage', repl_str)
delete_file(bin_path, django_conf_name)
write_file(bin_path, django_conf_name, django_conf)

pos = apache_conf.find('import djangorecipe')
if pos >= 0:
    apache_conf = apache_conf[:pos]
write_file(bin_path, 'env.py', apache_conf)
apache_conf += """import os
os.environ['DJANGO_SETTINGS_MODULE'] = '$PROJECT_NAME.settings'
os.environ['PYTHON_EGG_CACHE'] = '$PROJECTDIR/tmp-eggs'

import django.core.handlers.wsgi

_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
    environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']
    return _application(environ, start_response)
"""
apache_conf = apache_conf.replace('$PROJECT_NAME', PROJECT_NAME).replace('$PROJECTDIR', path)
write_file(bin_path, 'apache.py', apache_conf)

tmpeggs = os.path.join(path, 'tmp-eggs')
if not os.path.exists(tmpeggs):
    os.mkdir(tmpeggs)
    
import platform
is_windows = platform.system() == 'Windows'
django_path = os.path.join(bin_path, 'django')
if not is_windows:
    import stat
    st = os.stat(django_path)
    os.chmod(django_path, st.st_mode | stat.S_IEXEC)
    
#chroot to installed env
if os.path.exists(os.path.join(project_path, 'settings.py')):
    print "==================      Creating static...      =================="
    code = subprocess.call([os.path.join(bin_path, 'django'), 'collectstatic', '--noinput'], cwd=path)
    if code:
        print FAIL_TEXT
        sys.exit(1)

    print "==================      Setting database...      =================="
    init_db = ''
    while not init_db in ['Y', 'y', 'N', 'n']:
        init_db = raw_input("Initialize DB? [y/n]")
    if init_db in ['Y', 'y']:
        sys.path[0:0] += [bin_path]
        import env
        sys.path[0:0] += [project_path]
        os.environ['DJANGO_SETTINGS_MODULE'] = PROJECT_NAME + '.settings'
        from django.conf import settings
        if 'south' in settings.INSTALLED_APPS:
            code = subprocess.call([django_path, 'migrate'], cwd=path)
            if code:
                print FAIL_TEXT
                sys.exit(1)

else:
    print "==================      Creating project...      =================="
    sys.path[0:0] += [bin_path]
    import env
    from django.core.management.commands.startproject import Command
    command = Command()
    command.execute(PROJECT_NAME, path, verbosity=2, extensions=[], files=[])
    from django.utils.crypto import get_random_string
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(50, chars)
    def fix_name(file_path, file_name):
        data = read_file(file_path, file_name)
        os.remove(os.path.join(file_path, file_name))
        data = data.replace('{{ project_name }}', PROJECT_NAME).replace('{{ secret_key }}', secret_key)
        write_file(file_path, file_name, data)
    fix_name(project_path, 'settings.py')
    fix_name(project_path, 'urls.py')
    fix_name(project_path, 'wsgi.py')
    delete_file(path, 'manage.py')

print "FINISHED"
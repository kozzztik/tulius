import os
BASE_DIR = os.path.dirname(__file__) + '/'
PROJECT_NAME = 'tulius'
# Django settings for tulius project.
from django.utils.translation import ugettext_lazy as _

ROOT_URLCONF = 'tulius.urls'

TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru'
USE_I18N = True
USE_L10N = True
USE_TZ = True
SITE_ID = 1

DEBUG = True
TEMPLATE_DEBUG = True

SECRET_KEY = '0q^^#b-w#ae@i%h$da%chx@3ldu52c5%6v)_fiaorkl+4#r%=1'

VK_APP_KEY = '4782118'
VK_APP_SECRET = 'm6GcbXexyppJ4cv1p94y'

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

LANGUAGES = (
   ('ru', _('Russian')),
)

AUTH_USER_MODEL = 'tulius.User'

INSTALLED_APPS = (
    'south',
    'grappelli',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.sitemaps',
    'memcache_status',
    'djaml',
    'djfw',
    'tulius',
    'djfw.datablocks',
    'djfw.logger',
    'djfw.accounts',
    'djfw.accounts.registration',
    'djfw.pagination',
    'djfw.flatpages',
    'djfw.tinymce',
    'djfw.wysibb',
    'djfw.autocomplete',
    'djfw.inlineformsets',
    'djfw.bugtracker',
    'djfw.cataloging',
    'djfw.news',
    'djfw.uploader',
    'djfw.profiler',
    'djfw.photos',
    'djfw.sortable',
    'djfw.custom_views',
    'django_mailer',
    'pm',
    'tulius.players',
    'tulius.games',
    'tulius.forum',
    'tulius.stories',
    'tulius.gameforum',
    'tulius.theming',
    'tulius.bugs',
    'tulius.old_site_migrate',
    'djfw.installer',
    'events',
    'tulius.vk',
    'tulius.counters',
)

MIDDLEWARE_CLASSES = (
    'djfw.installer.middleware.MaintenanceMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'djfw.pagination.middleware.PaginationMiddleware',
    'djfw.logger.middleware.ExceptionMiddleware',
    'djfw.flatpages.middleware.FlatpageFallbackMiddleware',
    'djfw.profiler.middleware.ProfilerMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'djfw.hamlpy.template.loaders.HamlPyFilesystemLoader',
    'djfw.hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

if not DEBUG:
    TEMPLATE_LOADERS = (('django.template.loaders.cached.Loader', TEMPLATE_LOADERS),)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth',
    'djfw.flatpages.context_processors.flatpages',
    'djfw.accounts.auth.context_processors.relogin',
    'djfw.datablocks.context_processors.datablocks',
)

CROWD = {
    'url': 'http://crowd.co-de.org:8095/crowd/rest',
    'app_name': 'tulius_trunk',
    'password': 'dsth5y3463563h5dfg55',
    'superuser': True,
}

AUTHENTICATION_BACKENDS = (
    'tulius.vk.backend.VKBackend',
    'django.contrib.auth.backends.ModelBackend',
    'djfw.bugtracker.atlassian.crowd.CrowdBackend', 
)

BUGTRACKER = {
    'url': 'https://jira.co-de.org',
    'login': 'Tulius',
    'password': 'HSR70yvEnA',
    'project': 'TULIUS',
    'disable_certs': True,
    'ca_certs': None
}

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'tulius.com',
    'tulius.co-de.org',
    ]

EMAIL_BACKEND = 'django_mailer.backend.DbBackend'

INLINE_FORMSET_CLASS = 'table'
ACCOUNT_ACTIVATION_DAYS = 2
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/auth/login/'
AUTOCOMPLETE_MODELS = ('auth.user', 'tulius.user')

DEFAULT_THEME = 'classic'

IMAGE_FORMAT = 'png'

SITE_ROOT = BASE_DIR + 'tulius/'
MEDIA_ROOT = BASE_DIR + 'media/'
STATIC_ROOT = BASE_DIR + 'static/'
LOCALE_PATHS = (SITE_ROOT + 'locale/',)
INSTALLER_BACKUPS_DIR = BASE_DIR + 'backups/'

WYSIBB_THUMB_SIZE = (350, 350)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler', 
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': BASE_DIR + 'logfile.txt',
        },
        'db': {
            'level': 'DEBUG',
            'class': 'djfw.logger.DBLogHandler',
        },
        'sqllogfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': BASE_DIR + 'sql-logfile.txt',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['logfile', 'db', 'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
        'installer': {
            'handlers': ['db'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'bugtracker.jira': {
            'handlers': ['console', 'db',],
            'level': 'DEBUG',
        },
    }
}

if DEBUG:
    import warnings
    warnings.filterwarnings(
        'error', r"DateTimeField received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields')

THEMING_ROOT = MEDIA_ROOT + 'uploads/themes/'
THEMING_URL = MEDIA_URL + 'uploads/themes/'

EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = '' 
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

#EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
#EMAIL_FILE_PATH = PROJECT_ROOT +  'mail_dump/'

MAIL_RECEIVERS = ['pm.mail.get_mail']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tulius',
        'HOST': '127.0.0.1',
        'USER': 'tulius',
        'PASSWORD': 'tulius',
        'PORT': '',
        'CONN_MAX_AGE': 20,
    }
}

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#        'KEY_PREFIX': 'tulius',
#    }
#}
#
#SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
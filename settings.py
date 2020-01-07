"""Django settings for tulius project."""
import os

from django.utils.translation import ugettext_lazy as _

branch = os.environ.get("TULIUS_BRANCH", '')
if branch == 'master':
    env = 'prod'
elif branch == 'dev':
    env = 'qa'
else:
    env = 'dev'

BASE_DIR = os.path.dirname(__file__) + '/'
PROJECT_NAME = 'tulius'

ROOT_URLCONF = 'tulius.urls'

TIME_ZONE = 'Europe/Moscow'
LANGUAGE_CODE = 'ru'
USE_I18N = True
USE_L10N = True
USE_TZ = True
SITE_ID = 1

DEBUG = (env != 'prod')
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = '0q^^#b-w#ae@i%h$da%chx@3ldu52c5%6v)_fiaorkl+4#r%=1'

VK_APP_KEY = '4782118'
VK_APP_SECRET = 'm6GcbXexyppJ4cv1p94y'

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

# TODO remove in 3.6
LANGUAGES = (
    ('ru', _('Russian')),
)

AUTH_USER_MODEL = 'tulius.User'

INSTALLED_APPS = (
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
    # TODO: fix it
    # 'ws4redis',
    'hamlpy',
    'djfw',
    'djfw.datablocks',
    'djfw.logger',
    'djfw.pagination',
    'djfw.flatpages',
    'djfw.tinymce',
    'djfw.wysibb',
    'djfw.inlineformsets',
    'djfw.cataloging',
    'djfw.news',
    'djfw.uploader',
    'djfw.profiler',
    'djfw.photos',
    'djfw.sortable',
    'djfw.custom_views',
    'tulius.pm',
    'tulius',
    'tulius.login',
    'tulius.players',
    'tulius.profile',
    'tulius.games',
    'tulius.forum',
    'tulius.stories',
    'tulius.gameforum',
    'djfw.installer',
    'tulius.events',
    'tulius.vk',
    'tulius.counters',
)

MIDDLEWARE = (
    # 'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'djfw.pagination.middleware.PaginationMiddleware',
    'djfw.flatpages.middleware.FlatpageFallbackMiddleware',
    'djfw.profiler.middleware.ProfilerMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'loaders': [
                'hamlpy.template.loaders.HamlPyFilesystemLoader',
                'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'ws4redis.context_processors.default',
                'djfw.flatpages.context_processors.flatpages',
                'djfw.datablocks.context_processors.datablocks',
            ],
            'libraries': {

            }
        }
    },
]

# TODO that must not work now
# if not DEBUG:
#     TEMPLATES += [
#         {
#             'BACKEND': 'django.template.loaders.cached.Loader'
#         }
#     ]


AUTHENTICATION_BACKENDS = (
    'tulius.vk.backend.VKBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]

INLINE_FORMSET_CLASS = 'table'
ACCOUNT_ACTIVATION_DAYS = 2
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'
AUTOCOMPLETE_MODELS = ('auth.user', 'tulius.user')

DEFAULT_THEME = 'classic'

IMAGE_FORMAT = 'png'

SITE_ROOT = os.path.join(BASE_DIR, 'tulius') + '/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'data', 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'data', 'static')
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
            'class': 'logging.NullHandler',
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
    }
}

if DEBUG:
    import warnings
    warnings.filterwarnings(
        'error', r"DateTimeField received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields')

EMAIL_HOST = 'tulius_mail' if env == 'prod' else 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = '' 
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

if env != 'prod':
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = BASE_DIR +  'mail_dump/'

MAIL_RECEIVERS = ['pm.mail.get_mail']


WS4REDIS_CONNECTION = {
    'host': 'tulius_redis',
    'port': 6379,
    'db': 10,
    'password': '',
}

WS4REDIS_EXPIRE = 60
WS4REDIS_PREFIX = 'ws_{}'.format(env)
WEBSOCKET_URL = '/ws/'
WS4REDIS_SUBSCRIBER = 'websockets.subscriber.RedisSubscriber'
WSGI_APPLICATION = 'ws4redis.django_runserver.application'
WS4REDIS_HEARTBEAT = 'heartbeat'

# Actual credentials are hold in settings_production.py file.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tulius_{}'.format(env),
        'HOST': '127.0.0.1' if env == 'dev' else 'tulius_mysql',
        'USER': 'tulius_{}'.format(env),
        'PASSWORD': 'tulius',
        'PORT': '',
        'CONN_MAX_AGE': 20,
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# CACHES = {
#     'default': {
#         'BACKEND': 'redis_cache.RedisCache',
#         'LOCATION': '/var/run/redis/redis.sock',
#         'KEY_PREFIX': 'tulius',
#     }
# }
#
# SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

if env == 'prod':
    DEFAULT_FROM_EMAIL = 'tulius@tulius.com'
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
            'KEY_PREFIX': 'tulius',
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
    ALLOWED_HOSTS += [
        'tulius.com',
        'tulius.co-de.org',
]
elif env == 'qa':
    DEFAULT_FROM_EMAIL = 'tulius-test@tulius.com'

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
            'KEY_PREFIX': 'testtulius',
        }
    }
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
    ALLOWED_HOSTS += [
        'test.tulius.com',
        'test.tulius.co-de.org',
    ]

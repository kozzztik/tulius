"""Django settings for tulius project."""
import os

from sentry_sdk.integrations.django import DjangoIntegration

branch = os.environ.get("TULIUS_BRANCH", '')
env = {
    'master': 'prod',  # production env
    'dev': 'qa',  # test staging env
    'local': 'dev',  # local development env
    'test': 'test'  # ci tests env
}[branch]
TEST_RUN = bool(os.environ.get("TULIUS_TEST", ''))

ENV = env
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'
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

AUTH_USER_MODEL = 'tulius.User'
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10Mb

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
    'hamlpy',
    'djfw',
    'djfw.datablocks',
    'djfw.pagination',
    'djfw.flatpages',
    'djfw.tinymce',
    'djfw.wysibb',
    'djfw.inlineformsets',
    'djfw.cataloging',
    'djfw.news',
    'djfw.uploader',
    'djfw.photos',
    'djfw.sortable',
    'djfw.custom_views',
    'django_celery_results',
    'tulius.core.debug_mail',
    'tulius.pm',
    'tulius.TuliusConfig',
    'tulius.core.ckeditor',
    'tulius.login',
    'tulius.players',
    'tulius.profile',
    'tulius.games',
    'tulius.forum',
    'tulius.forum.threads.ForumThreadsConfig',
    'tulius.forum.rights.ForumRightsConfig',
    'tulius.forum.comments.ForumCommentsConfig',
    'tulius.forum.read_marks.ForumReadMarksConfig',
    'tulius.forum.other.ForumOtherConfig',
    'tulius.forum.elastic_search.ForumElasticSearchConfig',
    'tulius.stories',
    'tulius.gameforum',
    'tulius.gameforum.threads.GameForumThreadsConfig',
    'tulius.gameforum.comments.GameForumCommentsConfig',
    'tulius.gameforum.other.GameForumOtherConfig',
    'djfw.installer',
    'tulius.events.EventsConfig',
    'tulius.vk',
    'tulius.counters',
    'django_asyncio.DjangoAsyncio',
)

MIDDLEWARE = (
    # 'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
    'tulius.core.profiler.profiler_middleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'djfw.pagination.middleware.pagination_middleware',
    'djfw.flatpages.middleware.flatpage_middleware',
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
                'djfw.flatpages.context_processors.flatpages',
                'djfw.datablocks.context_processors.datablocks',
            ],
            'libraries': {

            }
        }
    },
]

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

ELASTIC_HOSTS = ['localhost:9200'] if env == 'dev' else ['10.5.0.30:9200']
ELASTIC_PREFIX = 'test' if TEST_RUN else env

ELASTIC_MODELS = (
    ('tulius', 'User'),
    ('stories', 'Story'),
    ('stories', 'Role'),
    ('stories', 'Character'),
    ('forum_threads', 'Thread'),
    ('forum_comments', 'Comment'),
    ('game_forum_threads', 'Thread'),
    ('game_forum_comments', 'Comment'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
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
        'sqllogfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': BASE_DIR + 'sql-logfile.txt',
        },
        'log_stash': {
            'level': 'DEBUG',
            'class': 'logstash.TCPLogstashHandler',
            'host': '127.0.0.1' if env == 'dev' else '10.5.0.31',
            'port': 11011,
            'version': 1,
        },
        'elastic_search_indexing': {
            'level': 'DEBUG',
            'class': 'logstash.TCPLogstashHandler',
            'host': '127.0.0.1' if env == 'dev' else '10.5.0.31',
            'port': 11012,
            'version': 1,
        }
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['logfile', 'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
        'installer': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'async_app': {
            'handlers': ['console'],
            'level': 'DEBUG' if env == 'dev' else 'ERROR',
            'propagate': True,
        },
        'profiler': {
            'handlers': ['null' if TEST_RUN else 'log_stash'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'elastic_search_indexing': {
            'handlers': ['elastic_search_indexing'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'elasticsearch': {
            'handlers': ['console'],
            'level': 'DEBUG' if env == 'dev' else 'ERROR',
            'propagate': True,
        },
        'celery.task': {
            'handlers': ['console'],
            'level': 'DEBUG' if env == 'dev' else 'ERROR',
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
    EMAIL_BACKEND = 'tulius.core.debug_mail.backend.EmailBackend'
    EMAIL_FILE_PATH = BASE_DIR + 'data/mail/'

MAIL_RECEIVERS = ['pm.mail.get_mail']


REDIS_CONNECTION = {
    'host': '127.0.0.1' if env in ['dev', 'test'] else 'tulius_redis',
    'port': 6379,
    'db': {'prod': 3, 'qa': 2, 'dev': 1, 'test': 4}[env],
    'password': '',
}

# Actual credentials are hold in settings_production.py file.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tulius_{}'.format(env),
        'HOST': '127.0.0.1' if env in ['dev', 'test'] else 'tulius_mysql',
        'USER': 'travis' if env == 'test' else 'tulius_{}'.format(env),
        'PASSWORD': '' if env == 'test' else 'tulius',
        'PORT': '',
        'CONN_MAX_AGE': 20,
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# it is important to use Redis as session cache as it is used by Async app
# to identify users
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '{host}:{port}'.format(**REDIS_CONNECTION),
        'OPTIONS': {
            'DB': REDIS_CONNECTION['db'],
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'PICKLE_VERSION': -1,
        },
    },
}

if env == 'prod':
    DEFAULT_FROM_EMAIL = 'tulius@tulius.com'
    ALLOWED_HOSTS += [
        'tulius.com',
        'tulius.co-de.org',
    ]
elif env == 'qa':
    DEFAULT_FROM_EMAIL = 'tulius-test@tulius.com'
    ALLOWED_HOSTS += [
        'test.tulius.com',
        'test.tulius.co-de.org',
    ]

RAVEN_CONFIG = {
    'integrations': [DjangoIntegration()],
    'send_default_pii': True,
}

CELERY_RESULT_BACKEND = 'django-db'
CELERY_BROKER_URL = 'redis://{host}:{port}/{db}'.format(**REDIS_CONNECTION)
CELERY_WORKER_CONCURRENCY = 3
CELERY_EVENT_QUEUE_PREFIX = f'{env}_'
CELERY_TASK_ALWAYS_EAGER = TEST_RUN

HTTP_HOST = '0.0.0.0'
HTTP_PORT = os.environ.get('HTTP_PORT', 7000)
HTTP_KEEP_ALIVE = 75.0
HTTP_THREADS = int(os.environ.get('HTTP_THREADS', 10))

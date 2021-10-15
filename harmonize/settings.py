import os
from celery.schedules import crontab

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = True


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'harmonize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'harmonize.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'harmonize.wsgi.application'


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ["DB_PORT"],
    }
}


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


ALLOWED_HOSTS = ['*']
STATIC_URL = '/static/'
CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": f"{os.environ['REDIS_HOST']}:6379",
        "DB": os.environ['REDIS_CACHE_DB'],
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER = f"redis://{os.environ['REDIS_HOST']}:6379/{os.environ['REDIS_CACHE_DB']}"  # noqa: E501
CELERY_TIMEZONE = "US/Pacific"
CELERY_BEAT_SCHEDULE = {
    'store_saved_tracks': {
        'task': 'harmonize.tasks.store_saved_tracks',
        'schedule': crontab(minute=30, hour=0)
    },
    'sync_and_seed': {
        'task': 'harmonize.tasks.seed_and_sync_smart_playlists',
        'schedule': crontab(minute=0, hour=1)
    },
    'transition_saved_albums_to_tracks': {
        'task': 'harmonize.tasks.transition_saved_albums_to_tracks',
        'schedule': crontab(minute=0, hour=0)
    },
    'store_recently_played': {
        'task': 'harmonize.tasks.store_recently_played',
        'schedule': crontab(minute=0, hour='*/2')
    }
}

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_SERVICE_USER_URI = os.environ.get("SPOTIFY_SERVICE_USER_URI")

from pathlib import Path
import os
import sys
from dotenv import load_dotenv
os.environ['OPENBLAS_NUM_THREADS'] = '1'

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY')


ALLOWED_HOSTS = ['logbook.flyhomemn.com',
        'localhost'
        ]

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'ajax_select',
    'aircraft',
    'airport',
    'airline',
    'reports',
    'logbook',
    'user',
    'tinymce',
    'bootstrap5',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_currentuser.middleware.ThreadLocalUserMiddleware',

]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join((BASE_DIR), 'templates/')],
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

WSGI_APPLICATION = 'main.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('database'),
        'HOSTNAME': 'localhost',
        'USER': os.getenv('user'),
        'PASSWORD': os.getenv('password'),
        'Port': '3306',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

# USE_TZ = True



# Determine if in Production or Development
if (len(sys.argv) >= 2 and sys.argv[1] == 'runserver'):
    DEBUG = True 
    #...       
else:
    DEBUG = False
    #...

STATIC_URL = 'static/'
STATICFILES_DIRS = ( os.path.join('static'), )
# STATIC_ROOT = 'static/'
# STATICFILES_DIRS = [
#     "/home/flyhomem/virtualenv/logbook/3.8/lib/python3.8/site-packages/",
#     ]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = 'logbookhome'

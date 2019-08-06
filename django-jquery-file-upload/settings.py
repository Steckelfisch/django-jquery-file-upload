"""
Django settings.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

SOX_CMD = 'sox'  # Ubuntus's sox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OTHER_BASE_DIR = os.getcwd()

print("BASE_DIR "+BASE_DIR)
print("OTHER_BASE_DIR "+OTHER_BASE_DIR)

FILE_STORE_DIR = BASE_DIR

UPLOAD_DIR = 'upload'
DOWNLOAD_DIR = 'download'

# Batmusic BatMusicSession file locations
SESSION_DATA_DIR = 'session-data'  # dir with multiple sessions
SESSION_DATA_PATH = os.path.join(FILE_STORE_DIR, SESSION_DATA_DIR)

UNPROCESSED_DATA_DIR = 'unprocessed'  # archivefiles(zip,tgz) and indifdual uploaded files
EXTRACTED_DATA_DIR = 'unprocessed-extracted'  # extracted files from archive files
BACKUP_DATA_DIR = 'backup'  # original uploaded archivefiles
REJECTED_DATA_DIR = 'rejected'  # data bm could not process
DATA_DIR = 'data'  # all data (one session) that is succefuly accepted




# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9%$in^gpdaig@v3or_to&_z(=n)3)$f1mr3hf9e#kespy2ajlo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]


# Application definition

INSTALLED_APPS = (
    'fileupload.apps.FileuploadConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'debug_toolbar',

)

#MIDDLEWARE_CLASSES = (
MIDDLEWARE = (
'django.middleware.security.SecurityMiddleware',
'django.contrib.sessions.middleware.SessionMiddleware',
'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
#    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'django.middleware.security.SecurityMiddleware',
'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'django-jquery-file-upload.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #'DIRS': ['django-jquery-file-upload/templates'],
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

WSGI_APPLICATION = 'django-jquery-file-upload.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Oslo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    'django-jquery-file-upload/static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'django-jquery-file-upload', 'media')

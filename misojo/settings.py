import os
import sys
from dotenv import load_dotenv

ENV = "dev"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# load environment variables
if ENV == "dev":
    print("running in dev environment")
    load_dotenv = load_dotenv(os.path.join(BASE_DIR, '.env.dev'))
elif ENV == "prod":
    print("running in prod environment")
    load_dotenv = load_dotenv(os.path.join(BASE_DIR, '.env.prod'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("DEBUG") == "True"

ALLOWED_HOSTS = ["*"]

# Application definition
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'storages',
    'audio_generator',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'misojo.urls'

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

WSGI_APPLICATION = 'misojo.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': os.environ.get("DB_ENGINE"),
        'NAME': os.environ.get("DB_NAME"),
        'USER': os.environ.get("DB_USER"),
        'PASSWORD': os.environ.get("DB_PASSWORD"),
        'HOST': os.environ.get("DB_HOST"),
        'PORT': os.environ.get("DB_PORT"),
        'TEST': {
            'NAME': 'test_sorteos_ajolote',
        },
    }
}


# Password validation
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

# Language and timezone
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static and media files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Allow all origins
CORS_ALLOW_ALL_ORIGINS = True

# aws settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_FILE_OVERWRITE = os.getenv('AWS_S3_FILE_OVERWRITE')
AWS_DEFAULT_ACL = None

STORAGES = {
    # Media file (image) management
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
        # Allow to overwrite files
        "AWS_S3_FILE_OVERWRITE": True,
    },
    # CSS and JS file management
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
        # Allow to overwrite files
        "AWS_S3_FILE_OVERWRITE": True,
    },
}

# Redirect to https
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    
# Other rnviroment variables
HOST = os.environ.get("HOST")

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}
from .common import *
from os import environ
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = environ.get('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = [environ.get('HOSTNAME')]

DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': environ.get('MYSQL_DATABASE_NAME'),
            'USER': environ.get('MYSQL_USER'),
            'PASSWORD': environ.get('MYSQL_PASSWORD'),
            'HOST': environ.get('MYSQL_HOST'),
            'PORT': environ.get('MYSQL_PORT'),
        }
}
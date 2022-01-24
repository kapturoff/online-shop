from .common import *
from os import environ
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = environ['SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = [environ('HOSTNAME')]

DATABASES = {
    'default':
        {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': environ('MYSQL_DATABASE_NAME'),
            'USER': environ('MYSQL_USER'),
            'PASSWORD': environ('MYSQL_PASSWORD'),
            'HOST': environ('MYSQL_HOST'),
            'PORT': environ('MYSQL_PORT'),
        }
}
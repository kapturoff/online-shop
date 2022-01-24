from pickle import FALSE
from .common import *
from os import environ

SECRET_KEY = environ['SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = ['0.0.0.0', 'localhost']
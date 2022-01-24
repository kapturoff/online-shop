from pickle import FALSE
from .common import *
from os import environ

SECRET_KEY = environ['SECRET_KEY']

DEBUG = False

# Security warning: Must be replaced with hostname of server where you will run the project
ALLOWED_HOSTS = ['0.0.0.0', 'localhost']
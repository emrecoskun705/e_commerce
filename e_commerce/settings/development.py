from e_commerce.settings.base import *
import os
from decouple import config

DEBUG = config('DEBUG')

ALLOWED_HOSTS = ['*',]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# E-mail console backend for developing purpose
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

#Stripe configiration
STRIPE_PUBLIC_KEY = config('STRIPE_TEST_PUBLIC_KEY')
STRIPE_SECRET_KEY = config('STRIPE_TEST_SECRET_KEY')
STRIPE_WEBHOOK_SECRET_KEY = config('STRIPE_WEBHOOK_SECRET_KEY')
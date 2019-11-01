from .base import *  # noqa

ALLOWED_HOSTS = ['ec.kdl.kcl.ac.uk']

INTERNAL_IPS = INTERNAL_IPS + ['']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'app_ec_liv',
        'USER': 'app_ec',
        'PASSWORD': '',
        'HOST': ''
    },
}

SECRET_KEY = ''

from .base import *
DEBUG=False
ADMINS=(
    ('TESTPRESS','testpress@gmail.com'),
)

ALLOWED_HOSTS=['myproject.com','www.myproject.com']
DATABASES={
    'default':{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'forum',
        'USER': 'forum',
        'PASSWORD':'forum'
    }
}


SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
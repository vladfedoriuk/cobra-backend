import os

from .base import *

INSTALLED_APPS += [
    "django_extensions",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "cobra"),
        "USER": os.environ.get("POSTGRES_USER", "cobra"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "cobra"),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "15432"),
    }
}

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "127.0.0.1")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.environ.get("RABBITMQ_DEFAULT_USER", "cobra")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_DEFAULT_PASS", "cobra")
CELERY_BROKER_URL = (
    f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//"
)

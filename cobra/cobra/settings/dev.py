import os

from .base import *

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

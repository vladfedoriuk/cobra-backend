# Set the default Django settings module for the 'celery' program.
import logging.config
import os

from celery import Celery, signals

from cobra.cobra.settings.base import BASE_DIR

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cobra.cobra.settings.dev")

app = Celery("cobra")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


@signals.setup_logging.connect
def on_celery_setup_logging(**kwargs):
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "file": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"}
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
            },
            "celery": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "formatter": "file",
                "filename": BASE_DIR / "logs" / "celery.log",
            },
        },
        "loggers": {
            "celery": {
                "handlers": ["celery", "console"],
                "propagate": True,
                "level": "DEBUG",
            },
        },
    }

    logging.config.dictConfig(config)

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "file": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"}
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "file",
            "filename": BASE_DIR / "logs" / "app.log",
        },
    },
    "loggers": {
        "root": {
            "level": "INFO",
            "handlers": [
                "file",
                "console",
            ],
        },
        "django": {
            "level": "INFO",
            "handlers": [
                "file",
                "console",
            ],
        },
    },
}

CELERY_LOGGING = {
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

FROM python:3.9.7 as base

FROM base as builder
RUN adduser --disabled-password --gecos '' cobra
ENV PYTHONUNBUFFERED 1
COPY --chown=cobra [ \
    "requirements/base.txt", \
     "requirements/dev.txt", \
     "requirements/prod.txt", \
     "/tmp/" \
    ]
COPY --chown=cobra ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r /tmp/base.txt

FROM builder as dev

ENV DEBUG 1
ENV DJANGO_SETTINGS_MODEULE 'cobra.settings.dev'

RUN --mount=type=cache,target=/root/.cache/pip \
     pip install -r /tmp/dev.txt
WORKDIR /code


FROM dev as cobra-dev

ENTRYPOINT ["/entrypoint.sh"]
CMD ["run_cobra_dev"]

FROM dev as celery-dev

ENTRYPOINT ["/entrypoint.sh"]
CMD ["run_celery_dev"]

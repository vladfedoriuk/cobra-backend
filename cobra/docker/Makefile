.PHONY: build-dev

build-cobra-dev:
	DOCKER_BUILDKIT=1 docker build -t cobra_dev --target cobra-dev -f Dockerfile ../../

build-celery-dev:
	DOCKER_BUILDKIT=1 docker build -t celery_dev --target celery-dev -f Dockerfile ../../

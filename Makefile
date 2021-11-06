IN_DIR=cobra/requirements
DOCKER_DIR=cobra/docker

objects = $(wildcard $(IN_DIR)/*.in)
outputs = $(objects:.in=.txt)

.PHONY: requirements install_dev check_all pre-commit_update services down development

requirements: $(outputs)

# pip-tools
$(IN_DIR)/dev.txt: $(IN_DIR)/base.txt
$(IN_DIR)/prod.txt: $(IN_DIR)/base.txt

%.txt: %.in
	pip-compile -v --output-file $@ $<

# pre-commit
pre-commit_install:
	pip install pre-commit
	pre-commit install

install_dev: pre-commit_install
	pip install -r $(IN_DIR)/dev.txt
	pip install pip-tools

check_all:
	pre-commit run --all-files

pre-commit_update:
	pre-commit autoupdate

# docker
services:
	docker-compose -p cobra -f $(DOCKER_DIR)/docker-compose.services.yml up -d

development: services
	docker-compose -p cobra -f $(DOCKER_DIR)/docker-compose.base.yml -f $(DOCKER_DIR)/docker-compose.dev.yml up -d

down:
	docker-compose -p cobra -f $(DOCKER_DIR)/docker-compose.services.yml -f $(DOCKER_DIR)/docker-compose.dev.yml down \
	 --remove-orphans

IN_DIR=cobra/requirements

objects = $(wildcard $(IN_DIR)/*.in)
outputs = $(objects:.in=.txt)

.PHONY: requirements install_dev check_all pre-commit_update

requirements: $(outputs)

$(IN_DIR)/dev.txt: $(IN_DIR)/base.txt
$(IN_DIR)/prod.txt: $(IN_DIR)/base.txt

%.txt: %.in
	pip-compile -v --output-file $@ $<

pre-commit_install:
	pip install pre-commit
	pre-commit install

install_dev: pre-commit_install
	pip install -r $(IN_DIR)/dev.txt
	pip install pip-tools

check_all: install_dev pre-commit_install
	pre-commit run --all-files

pre-commit_update: install_dev pre-commit_install
	pre-commit autoupdate

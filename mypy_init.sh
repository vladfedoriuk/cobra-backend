#!/bin/bash

pip install -r cobra/requirements/dev.txt > /dev/null
mypy . --show-traceback

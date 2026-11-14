#!/bin/bash
pylint app
pycodestyle app
#path = pwd
export PYTHONPATH=${PYTHONPATH}:/home/user/.../open-event-server
find . -name "*.pyc" -exec rm -rf {} \;
pytest tests/all --cov=app --cov-report=html

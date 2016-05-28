#!/bin/bash

VENV_DIR="gunicorn_example_app"

if [ ! -d ${VENV_DIR} ]; then
	virtualenv ${VENV_DIR}

	INITIALIZE_VENV=1
fi


source ${VENV_DIR}/bin/activate

if [ -v INITIALIZE_VENV ]; then
	pip install -r requirements.txt
fi

echo "Starting new instances..."
gunicorn -b 127.0.0.1:8081 -w 16 --error-logfile app-errors.log --access-logfile app-access.log --log-level DEBUG -D app:app

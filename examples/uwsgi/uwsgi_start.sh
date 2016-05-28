#!/bin/bash

VENV_DIR="uwsgi_example_app"

if [ ! -d ${VENV_DIR} ]; then
	virtualenv ${VENV_DIR}

	INITIALIZE_VENV=1
fi


source ${VENV_DIR}/bin/activate

if [ -v INITIALIZE_VENV ]; then
	pip install -r requirements.txt
fi

echo "Starting new instances..."
uwsgi --ini uwsgi_app.ini --daemonize app.uwsgi.log

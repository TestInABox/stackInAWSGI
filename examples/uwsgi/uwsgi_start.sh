#!/bin/bash

VENV_DIR="uwsgi_example_app"

for ARG in ${@}
do
	echo "Found argument: ${ARG}"
	if [ "${ARG}" == "--reset" ]; then
		echo "	User requested virtualenv reset, long argument name"
		let -i RESET_VENV=1
	elif ["${ARG}" == "-r" ]; then
		echo "	User requested virtualenv reset, short argument name"
		let -i RESET_VENV=2
	fi
done

MD5SUM_ROOT=`ls / | md5sum | cut -f 1 -d ' '`
MD5SUM_VENV=`ls ${VENV_DIR} | md5sum | cut -f 1 -d ' '`
if [ "${MD5SUM_ROOT}" == "${MD5SUM_VENV}" ]; then
	echo "Virtual Environment target is root. Configuration not supported."
	exit 1
fi

if [ -v RESET_VENV ]; then
	echo "Checking for existing virtualenv to remove..."
	if [ -d ${VENV_DIR} ]; then
		echo "Removing virtualenv ${VENV_DIR}..."
		rm -Rf ${VENV_DIR}
	fi
fi

if [ ! -d ${VENV_DIR} ]; then
	echo "Building virtualenv..."
	virtualenv ${VENV_DIR}

	INITIALIZE_VENV=1
fi

source ${VENV_DIR}/bin/activate

if [ -v INITIALIZE_VENV ]; then
	pip install -r requirements.txt
fi

echo "Starting new instances..."
uwsgi --ini uwsgi_app.ini --daemonize app.uwsgi.log

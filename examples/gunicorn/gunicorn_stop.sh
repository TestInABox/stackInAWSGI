#!/bin/bash

echo "Stopping existing instances..."
kill -3 `ps -Aef | grep app\:app | grep -v grep | tr -s ' ' ';' | cut -f 2 -d ';'`

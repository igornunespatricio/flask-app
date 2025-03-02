#!/bin/bash

# Detect the operating system
OS_NAME=$(uname -s)

# Check if running on Windows (inside WSL or otherwise)
if [[ "$OS_NAME" == "Linux" ]]; then
    echo "Running on Linux -> Using Gunicorn"
    exec gunicorn -w 4 -b 0.0.0.0:5000 app:app
else
    echo "Running on Windows -> Using Waitress"
    exec python -m waitress --listen=0.0.0.0:5000 app:app
fi

#!/bin/bash

pid=$1

if [ -z "$pid" ]; then
    echo "Usage: ./stop.sh <pid>"
    exit 1
fi

kill $pid

echo "FastAPI server with PID $pid stopped"

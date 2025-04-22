#!/bin/bash

# Set the environment file to use
if [ "$1" == "dev" ]; then
    NODE_ENV=development yarn build
elif [ "$1" == "prd" ]; then
    NODE_ENV=production yarn build
else
    echo "Usage: ./build.sh <dev|prd>"
    exit 1
fi


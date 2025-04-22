#!/bin/bash

# Set the environment file to use
if [ "$1" == "dev" ]; then
    NODE_ENV=development yarn build
elif [ "$1" == "prd" ]; then
    PUBLIC_URL=/utm yarn build
    # sudo chown -R :www-data /home/max/cleanbeding/clean-utm/build
    # sudo chmod -R 750 /home/max/cleanbeding/clean-utm/build

else
    echo "Usage: ./build.sh <dev|prd>"
    exit 1
fi


#!/bin/bash

# Set the environment file to use
if [ "$1" == "dev" ]; then
    NODE_ENV=development env_file=".env.development"
    # yarn start:development
    elif [ "$1" == "prd" ]; then
    # env_file=".env.production"
    NODE_ENV=production yarn start
else
    echo "Usage: ./start.sh <dev|prd>"
    exit 1
fi

# nohup uvicorn main:app --host 0.0.0.0 --port $CACHE_PORT   >> run.log 2>&1 &
pid=$!
echo "React App server started with PID $pid"
# yarn start

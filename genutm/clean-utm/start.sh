#!/bin/bash

# Set the environment file to use
if [ "$1" == "dev" ]; then
    PORT=4000 NODE_ENV=development env_file=".env.development" yarn start
    
    elif [ "$1" == "prd" ]; then
    # env_file=".env.production"
    HOST=0.0.0.0 PORT=39000 NODE_ENV=production yarn start
    elif [ "$1" == "prdhttp" ]; then
    echo "----------------"
    serve  -p 2000 build
    elif [ "$1" == "daemon" ]; then
    nohup serve  -p 2000 build >>run.log 2>&1 &
else
    echo "Usage: ./start.sh <dev|prd>"
    exit 1
fi

# nohup uvicorn main:app --host 0.0.0.0 --port $CACHE_PORT   >> run.log 2>&1 &
pid=$!
echo "React App server started with PID $pid"
# yarn start

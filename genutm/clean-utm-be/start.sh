#!/bin/bash
PORT=3001
# Set the environment file to use

#build react app
cd ../clean-utm
./build.sh prd
cd -
#kill previous process
kill `lsof -ti tcp:3001`

#start new process
if [ "$1" == "dev" ]; then
    npm start
elif [ "$1" == "" ]; then
    npm start
    # node server.js
elif [ "$1" == "prd" ]; then
    nohup npm start >>run.log 2>&1 &
else
    echo "Usage: ./start.sh <dev|prd>"
    exit 1
fi

# nohup uvicorn main:app --host 0.0.0.0 --port $CACHE_PORT   >> run.log 2>&1 &
pid=$!
echo "React App server started with PID $pid"
# yarn start

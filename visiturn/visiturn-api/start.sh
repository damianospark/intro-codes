#!/bin/bash

if [ "$1" == "dev" ]; then
    export VRP_HOST=127.0.0.1
    export CACHE_HOST=127.0.0.1
    export ORS_HOST=211.208.171.207
elif [ "$1" == "prd" ]; then
    export API_URL=211.208.171.207
    export VRP_HOST=211.208.171.207
    export CACHE_HOST=211.208.171.207
    export ORS_HOST=211.208.171.207
else
    echo "Usage: ./start.sh <dev|prd> [reload]"
    exit 1
fi

export ORS_PORT=50003
export VRP_PORT=51002
export CACHE_PORT=51001

if [ "$1" == "dev" ]; then
    uvicorn main:app --host 0.0.0.0 --port $VRP_PORT --reload
elif [ "$2" == "reload" ]; then
    uvicorn main:app --host 0.0.0.0 --port $VRP_PORT --reload
else
    nohup uvicorn main:app --host 0.0.0.0 --port $VRP_PORT --reload >>run.log 2>&1 &
fi
pid=$!

echo "------------------------------------------------------------------"
echo "FastAPI server started with PID $pid"
echo "Logs are available in run.log"
echo "To stop the server, run './stop.sh $pid'"
echo "------------------------------------------------------------------"


# if [[ "$1" == "prd" && "$2" != "reload" ]]; then
#     tail -f run.log
# fi


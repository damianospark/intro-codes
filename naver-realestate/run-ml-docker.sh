#!/bin/bash

if [ "$(docker ps -q -f name=clbe-ml)" ]; then
    docker exec -it clbe-ml bash -c "cd /workspace && bash"
elif [ "$(docker ps -aq -f status=exited -f name=clbe-ml)" ]; then
    docker start clbe-ml
    docker exec -it clbe-ml bash -c "cd /workspace && bash"
else
    # docker run --gpus all -it --name clbe-ml -v /home/max/cleanbeding/naver-realestate/workspace:/workspace tensorflow/tensorflow:2.4.0-gpu bash -c "cd /workspace && bash"
    echo "run with cpus"
    docker run --gpus all -it --name clbe-ml -p 9999:8888 -v /home/max/cleanbeding/naver-realestate/workspace:/workspace teddylee777/deepko:latest bash -c "cd /workspace && bash"
fi

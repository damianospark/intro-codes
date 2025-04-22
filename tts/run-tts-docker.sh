#!/bin/bash

if [ "$(docker ps -q -f name=tts-torch)" ]; then
    docker exec -it tts-torch bash -c "cd /workspace && bash"
elif [ "$(docker ps -aq -f status=exited -f name=tts-torch)" ]; then
    docker start tts-torch
    docker exec -it tts-torch bash -c "cd /workspace && bash"
else
    docker run --gpus all -it --name tts-torch -v /home/max/cleanbeding/tts/workspace:/workspace pytorch/pytorch:2.2.2-cuda12.1-cudnn8-devel bash -c "cd /workspace && bash"
fi

#!/usr/bin/zsh
. ~/.zshrc
cd /home/max/cleanbeding/dash
nohup python /home/max/cleanbeding/dash/app.py >>/home/max/cleanbeding/dash/run.log 2>&1 &

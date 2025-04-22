#!/bin/bash
# needle_env 환경을 활성화합니다.
source activate needle_env
yesterday=$(date -d "-1 day" +%Y-%m-%d)

cd /home/max/cleanbeding/anycrawler/needle
# python 스크립트를 실행하고 로그를 run.log 파일에 추가합니다.
/home/max/miniconda3/envs/needle_env/bin/python crawl-screen-check.py $yesterday >>/home/max/cleanbeding/anycrawler/needle/run.log 2>&1
# 환경을 비활성화합니다.
source deactivate

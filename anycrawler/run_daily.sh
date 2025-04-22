#!/bin/bash

# 사용자의 zsh 환경 구성을 로드
# source /home/max/.zshrc

# 로그 파일 경로
log_file="/home/max/cleanbeding/anycrawler/run.log"

# 스크립트 시작 로깅
echo "Script started at $(date)" >>"$log_file"

#  스크립트 실행 및 로깅
{
    # Conda 초기화 (이미 .zshrc에 포함되어 있을 수 있음)
    source /home/max/miniconda3/etc/profile.d/conda.sh
    conda activate base

    # 작업 디렉토리로 이동
    cd /home/max/cleanbeding/anycrawler

    # 배송의 경우 접수일 기준이므로 어제 날짜 계산
    yesterday=$(date -d "-1 day" +%Y-%m-%d)
    python tms_result_crawler.py "$yesterday" 배송
    python tms_result_crawler.py "$yesterday" 수거

    /home/max/cleanbeding/anycrawler/deploy.sh missing
} >>"$log_file" 2>&1

# 스크립트 종료 로깅
echo "Script ended at $(date)" >>"$log_file"

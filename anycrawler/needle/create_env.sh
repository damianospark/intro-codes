#!/bin/bash

# 새로운 conda 환경 이름 설정
ENV_NAME="needle_env"

# 필요한 Selenium 버전 설정 (Needle 0.5.0은 Selenium 2.x에서 3.x까지 지원)
SELENIUM_VERSION="3.141.0"

# 새로운 conda 환경 생성 및 활성화
conda create -n $ENV_NAME python=3.7 -y
conda activate $ENV_NAME

# Selenium과 Needle 설치
conda install -c conda-forge selenium=$SELENIUM_VERSION
pip install needle==0.5.0

# WebDriver Manager 설치 (ChromeDriver 관리를 위해)
pip install webdriver-manager

# 필요한 추가 패키지 설치 (예: pytest, pandas 등)
# pip install pytest pandas

echo "환경 '$ENV_NAME'에 Selenium 버전 $SELENIUM_VERSION 및 Needle 설치 완료"

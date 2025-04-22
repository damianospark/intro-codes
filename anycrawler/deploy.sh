#!/bin/bash

# 소스 디렉토리와 대상 디렉토리 설정
src_dir="/home/max/cleanbeding/anycrawler/tms"
dst_dir="/var/www/better/tms"
yesterday=$(date -d "-1 day" +%Y-%m-%d)

# 첫 번째 파라미터 검증
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 {all|missing}"
    exit 1
fi

# 'all' 옵션 처리
if [ "$1" == "all" ]; then
    sudo cp -R "$src_dir/"* "$dst_dir"

# 'missing' 옵션 처리
elif [ "$1" == "missing" ]; then
    # sudo rsync -av --ignore-existing "$src_dir/" "$dst_dir/" #목적지에 없는 것만 복사
    sudo rsync -avu "$src_dir/" "$dst_dir/" #목적지에 없는 것 및 소스폴더에서 업데이트된 것도 복사
python crawl-cross-check.py $yesterday

# 잘못된 파라미터 처리
else
    echo "Invalid option: $1"
    echo "Usage: $0 {all|missing}"
    exit 1
fi

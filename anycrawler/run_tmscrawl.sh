#!/bin/bash

# 시작 날짜와 오늘 날짜 설정
start_date="2023-10-10"
end_date=$(date +"%Y-%m-%d")

# days.csv 파일이 없으면 생성
if [ ! -f days.csv ]; then
    echo "date,status" > days.csv
    current_date=$start_date
    while [[ "$current_date" != "$end_date" ]]; do
        echo "$current_date," >> days.csv
        current_date=$(date -I -d "$current_date + 1 day")
    done
    echo "$end_date," >> days.csv
fi

# days.csv의 각 날짜에 대해 tms_result_crawler.py 실행
while IFS=, read -r date status; do
    if [[ -z $status ]]; then
        ./tms_result_crawler.py "$date" 수거
        if [ $? -eq 0 ]; then
            # 실행 성공 시 'OK'로 업데이트
            sed -i "s/^$date,/$date,OK/" days.csv
        else
            # 실행 실패 시 'FAILED'로 업데이트
            sed -i "s/^$date,/$date,FAILED/" days.csv
        fi
    fi
done < days.csv

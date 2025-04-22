import datetime
import os
import sys
from datetime import timedelta

import pandas as pd
import requests

holiday_file_path = './holiday.csv'
with open(holiday_file_path, 'r', encoding='utf-8') as file:
    holiday_data = file.readlines()

# Processing the data
holiday_data_processed = [line.strip().split('\t') for line in holiday_data if not line.startswith('#')]
holiday_df_processed = pd.DataFrame(holiday_data_processed, columns=['Date', 'Holiday'])
holiday_df_processed['Date'] = pd.to_datetime(holiday_df_processed['Date'], format='%Y%m%d').dt.date
public_holidays_list = holiday_df_processed['Date'].tolist()

# webhook-monitoring-alert
slack_webhook_url = (

)


def send_slack_message(webhook_url, title, message, ok=True):
    ccode = "#2c9b3d" if ok else "#d75c15"
    ok_word = "OK" if ok else "NG"
    slack_data = {
        "attachments": [
            {
                "color": ccode,  # 색상 코드
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*[{ok_word}] {title}*",
                        },  # 타이틀
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"{message}"},
                    },
                ],
            }
        ]
    }
    # slack_data = {
    #     "text": message,
    #     "attachments": [{"text": f"<{link}|바로가기>"}]
    # }
    requests.post(webhook_url, json=slack_data)


def chk_holiday_weekend(date, csv_delivery, html_delivery, csv_return, html_return):
    """
    Check the delivery and return status based on the given date and counts.
    Returns True for 'Normal' conditions and False for 'Abnormal' conditions.

    Args:
    date (str): Date in 'YYYY-MM-DD' format.
    csv_delivery (int): CSV Delivery Count.
    html_delivery (int): HTML Delivery Count.
    csv_return (int): CSV Return Count.
    html_return (int): HTML Return Count.

    Returns:
    bool: True if the conditions are normal, False otherwise.
    """
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()

    # Check if the date is a weekend
    if date_obj.weekday() == 6:  # Sunday
        return True if csv_delivery == 0 and html_delivery == 0 and csv_return != 0 and html_return != 0 else False
    elif date_obj.weekday() == 5:  # Saturday
        return True if csv_delivery == 0 and html_delivery == 0 and csv_return == 0 and html_return == 0 else False

    # Check if the date is a public holiday
    if date_obj in public_holidays_list:
        return True if csv_delivery == 0 and html_delivery == 0 and csv_return != 0 and html_return != 0 else False

    # For weekdays that are not public holidays
    # Check if any of the counts is 0
    if any(count == 0 for count in [csv_delivery, html_delivery, csv_return, html_return]):
        return False

    # If none of the above conditions are met, return True (assuming normal conditions)
    return True


def check_crawled_html_files(base_path, date_to_check, delivery_data, return_data):
    html_file_count_delivery = 0
    html_file_count_return = 0

    # 배송 및 수거 데이터의 월별 폴더 경로 설정
    year_month = date_to_check[:6]  # YYYYMM 형태
    delivery_path = os.path.join(base_path, '배송', year_month, 'html')
    return_path = os.path.join(base_path, '수거', year_month, 'html')

    # tms_delivery.csv 및 tms_return.csv에서 주문번호와 반품번호를 추출
    # delivery_order_numbers = delivery_data[delivery_data['주문번호'].str[0:8] == date_to_check]['주문번호'].tolist()
    # return_order_numbers = return_data[return_data['반품번호'].str[1:9] == date_to_check]['반품번호'].tolist()

    # 배송 데이터에 해당하는 파일 갯수 계산
    if os.path.isdir(delivery_path):
        for file in os.listdir(delivery_path):
            # if file.endswith('.html') and file.split('-')[0] in delivery_order_numbers:
            if file.endswith('.html') and file.split('-')[0] == date_to_check:
                html_file_count_delivery += 1

    # 수거 데이터에 해당하는 파일 갯수 계산
    if os.path.isdir(return_path):
        for file in os.listdir(return_path):
            # if file.endswith('.html') and file.split('.')[0] in return_order_numbers:
            if file.endswith('.html') and file.split('-')[0][1:] in date_to_check:
                html_file_count_return += 1

    return html_file_count_delivery, html_file_count_return


base_dir = '/var/www/better/tms'


def check_crawled_data(date_to_check=None):
    # 점검할 날짜 설정 (기본값은 어제)
    if date_to_check is None:
        date_to_check = (datetime.datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    else:
        date_obj = datetime.datetime.strptime(date_to_check, "%Y-%m-%d")
        date_to_check = date_obj.strftime("%Y%m%d")
    # tms_delivery.csv 및 tms_return.csv 파일 경로

    delivery_file = os.path.join(base_dir, 'tms_shipping.csv')
    return_file = os.path.join(base_dir, 'tms_return.csv')

    # 점검할 날짜의 데이터 건수 확인
    try:
        delivery_data = pd.read_csv(delivery_file)
        return_data = pd.read_csv(return_file)

        csv_delivery_count = delivery_data[delivery_data['주문번호'].str[0:8] == date_to_check].shape[0]
        csv_return_count = return_data[return_data['반품번호'].str[1:9] == date_to_check].shape[0]
    except Exception as e:
        return f"Error reading CSV files: {e}"
    html_delivery_count, html_return_count = check_crawled_html_files(base_dir, date_to_check, delivery_data, return_data)

    return date_to_check, csv_delivery_count, html_delivery_count, csv_return_count, html_return_count


def check_all_past_data():
    start_date = datetime.datetime(2023, 10, 10)  # 시작 날짜, 필요에 따라 변경
    end_date = datetime.datetime.now() - timedelta(days=1)  # 어제 날짜까지

    # 결과를 저장할 리스트와 DataFrame 초기화
    history = []
    different_days = pd.DataFrame(columns=['Date', 'CSV_Delivery_Count', 'HTML_Delivery_Count', 'CSV_Return_Count', 'HTML_Return_Count'])

    # 지정된 기간 동안 데이터 검사
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y%m%d')
        date_to_check, csv_delivery_count, html_delivery_count, csv_return_count, html_return_count = check_crawled_data(date_str)

        # 결과 저장
        history.append([date_to_check, csv_delivery_count, html_delivery_count, csv_return_count, html_return_count])

        # count가 일치하지 않는 경우 different_days에 추가
        if csv_delivery_count != html_delivery_count or csv_return_count != html_return_count:
            different_days = different_days.append({
                'Date': date_to_check,
                'CSV_Delivery_Count': csv_delivery_count,
                'HTML_Delivery_Count': html_delivery_count,
                'CSV_Return_Count': csv_return_count,
                'HTML_Return_Count': html_return_count
            }, ignore_index=True)

        current_date += timedelta(days=1)

    # 결과를 CSV 파일로 저장
    history_df = pd.DataFrame(history, columns=['Date', 'CSV_Delivery_Count', 'HTML_Delivery_Count', 'CSV_Return_Count', 'HTML_Return_Count'])
    history_df.to_csv('crawl_check_history.csv', index=False)

    return different_days


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py YYYY-MM-DD or 'all'")
        sys.exit(1)

    date_to_check = sys.argv[1]

    if date_to_check.lower() == 'all':
        different_days_df = check_all_past_data()
        print("Summary of different days:")
        if different_days_df is None or len(different_days_df) == 0:
            print("과거 수집데이터에 문제가 있는 날이 없음")
        else:
            print("과거 수집데이터에 문제가 있는 날이 발견됨")
        print(different_days_df)
        print("\nFull details are saved in 'crawl_check_history.csv'")
    else:
        try:
            datetime.datetime.strptime(date_to_check, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD format.")
            sys.exit(1)
        date_to_check, csv_delivery_count, html_delivery_count, csv_return_count, html_return_count = check_crawled_data(date_to_check)
        # 결과 출력
        result = f"점검 날짜: {date_to_check}\n"
        result += f"tms_shipping.csv 기록 건수: {csv_delivery_count}\n"
        result += f"tms_return.csv 기록 건수: {csv_return_count}\n"
        result += f"{base_dir} 아래 배송 html 파일 건수: {html_delivery_count}\n"
        result += f"{base_dir} 아래 수거 html 파일 건수: {html_return_count}\n"
        result += f'-------------------------------------------\n'

        date_obj = datetime.datetime.strptime(date_to_check, "%Y%m%d")
        date_to_check = date_obj.strftime("%Y-%m-%d")
        is_valid_result = chk_holiday_weekend(date_to_check, csv_delivery_count, html_delivery_count, csv_return_count, html_return_count)

        reason_troubled = ''
        if not is_valid_result and (csv_delivery_count != html_delivery_count or csv_return_count != html_return_count):
            reason_troubled = ''
            result += "수집에 문제가 있습니다:\n"
            if csv_delivery_count != html_delivery_count:
                result += f" - 배송: 요약 데이터 {csv_delivery_count}건, HTML 파일 {html_delivery_count}건\n"
                reason_troubled += '`배송보고서 수치상이`, '
            if csv_return_count != html_return_count:
                result += f" - 수거: 요약 데이터 {csv_return_count}건, HTML 파일 {html_return_count}건\n"
                reason_troubled += '`수거보고서 수치상이`, '
        if not is_valid_result and (csv_delivery_count == 0 or html_delivery_count == 0):
            result += " - 경고: 배송 데이터가 수집되지 않았습니다.\n"
            reason_troubled += '`배송보고서 수집오류`, '
        if not is_valid_result and (csv_return_count == 0 or html_return_count == 0):
            result += " - 경고: 수거 데이터가 수집되지 않았습니다.\n"
            reason_troubled += '`수거보고서 수집오류`, '

        send_slack_message(
            slack_webhook_url,
            f"`{date_to_check}일` `{base_dir}`아래의 배송/수거 결과보고내역(CSV)과 상세페이지(HTML)교차 검증",
            f"배송보고 (csv:html): `{csv_delivery_count}`,`{html_delivery_count}` \n"
            + f"수거보고 (csv:html): `{csv_return_count}`, `{html_return_count}` \n"
            + f"문제요약:`{reason_troubled or '없음'}`\n"
            + "_툐요일 결과는 배송/수거 모두 0, 일요일/주중공휴일은 배송만 모두 0_",
            (is_valid_result and (csv_delivery_count == html_delivery_count) and (csv_return_count == html_return_count))
        )
        print(result)


if __name__ == "__main__":
    main()

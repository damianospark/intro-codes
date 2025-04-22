from datetime import datetime, timedelta
import pandas as pd
import os
from icecream import ic


def filter_dataframe_by_date(file_name, input_date, dataframe, rem_this_df=False):
    # 날짜 부분 추출
    if 'delivery' in file_name:
        dataframe['date_portion'] = dataframe['주문번호'].str[0:8]
    else:
        dataframe['date_portion'] = dataframe['반품번호'].str[1:9]
    filtered_data = None
    if rem_this_df:
        filtered_data = dataframe[dataframe['date_portion'] != input_date.replace('-', '')]
    else:
        # '-'를 제거한 입력 날짜와 일치하는 행 필터링
        filtered_data = dataframe[dataframe['date_portion'] == input_date.replace('-', '')]

    return filtered_data


# Function to check existing data
def check_existing_data(file_name, directory, input_date):
    file_path = os.path.join(directory, file_name)
    if not os.path.exists(file_path):
        return None  # File does not exist, no existing data to check
    existing_data = pd.read_csv(file_path, )
    # Unkown,No.,최종상태,반품번호,거래처명,반품자명,회수상태,대분류,운송료반환여부,입고,반납,배송특이사항,기본주소,상세주소,공동현관PWD,공동현관PWD (소비자),고객요청사항,최종권역,수량,고객사반품번호,바코드생성여부,상세보기,tms상세주소

    existing_data = filter_dataframe_by_date(file_name, input_date, existing_data)

    return existing_data


fname = 'tms_return.csv'
dirpath = "./tms"
file_path = os.path.join(dirpath, fname)

yesterday = datetime.now() - timedelta(days=1)
input_date = yesterday.strftime("%Y-%m-%d")
df_all = pd.read_csv(file_path)
oldlen = len(df_all)
existing_data = check_existing_data(fname, dirpath, input_date)
print('어제', input_date)
ic(len(existing_data))
# df_all = df_all[~df_all.isin(existing_data)]
df_all = filter_dataframe_by_date(fname, input_date, df_all, rem_this_df=True)
ic(oldlen, len(df_all))

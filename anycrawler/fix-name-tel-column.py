import pandas as pd
fname = './tms/tms_delivery.csv'
# 기존 CSV 파일 읽기
df = pd.read_csv(fname)
if 'shipping' in fname:
    df['실수령자명'] = df['실수령자명'].str.replace('\n', ' ')
else:
    df['반품자명'] = df['반품자명'].str.replace('\n', ' ')
# 수정된 데이터를 새로운 CSV 파일로 저장
df.to_csv(fname, index=False)

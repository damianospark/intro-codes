import pandas as pd

# 기존 CSV 파일 읽기
df = pd.read_csv('./tms/tms_return.csv')

# '운송료반환여부' 필드를 '대분류'와 '입고' 사이에 빈 값으로 삽입
df.insert(df.columns.get_loc('대분류') + 1, '운송료반환여부', '')

# 수정된 데이터를 새로운 CSV 파일로 저장
df.to_csv('./tms/tms_return.csv.new', index=False)

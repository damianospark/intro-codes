import pandas as pd
import os

# CSV 파일 로드
file_path = 'tms/tms_return.csv'
df = pd.read_csv(file_path)

# '상세보기' 컬럼과 '반품번호' 컬럼을 사용하여 파일 경로와 이름 변경
for index, row in df.iterrows():
    old_file_path = row['상세보기']
    return_number = row['반품번호']
    new_file_name = f"{return_number}.html"
    new_file_path = os.path.join(os.path.dirname(old_file_path), new_file_name)

    # 파일명 변경
    if os.path.exists(old_file_path):
        os.rename(old_file_path, new_file_path)

    # DataFrame 업데이트
    df.at[index, '상세보기'] = new_file_path

# 변경된 DataFrame 저장
df.to_csv(file_path, index=False)

# 작업 완료 메시지 출력
print("CSV 파일 업데이트 및 파일 이름 변경 작업 완료")

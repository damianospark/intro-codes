import numpy as np
from spacy import prefer_gpu
import torch
from spacy.util import minibatch, compounding
from spacy.training import offsets_to_biluo_tags
import json
import spacy
import pandas as pd
from spacy.training import Example
import random
import warnings
from qrytool import load_data_into_dataframe, insert_dataframe_into_table

warnings.simplefilter("ignore")

# load data
# 학습된 모델로 주소 분석


def analyze_address(address):
    doc = nlp(address)
    print(f"주소:{address}")
    for ent in doc.ents:
        print(f"{ent.text}: {ent.label_}")


def get_entity_labels(nlp, filename='addr_src.txt'):
    # Create a set to store unique entity labels
    entity_labels = set()

    # Open the file and process each address
    with open(filename, 'r') as file:
        for address in file:
            # Analyze the address with the NLP model
            doc = nlp(address.strip())

            # Add the entity labels to the set
            for ent in doc.ents:
                entity_labels.add(ent.label_)

    # Return the set of entity labels
    return entity_labels


def make_df_with_entities(nlp, entity_labels=None, filename='addr_src.txt'):
    column_order = ['address', '건물', '단지', '건물동', '건물층', '건물호', '시', '도', '군', '구', '읍', '면', '동', '리', '로', '로번호', '번지수', '수신처', '상호', '비번', '요청']
    # Create an empty DataFrame with columns for each entity label
    # df = pd.DataFrame(columns=['address'] + list(entity_labels))
    # df = pd.DataFrame(columns=column_order)
    df = load_data_into_dataframe("""select all_id, 결제자명, 성별, 나이, 회원주소, 결제행정구분,회원lati,회원longi from customatrix""")
    # Open the file and process each address
    entities_list = []
    for idx, address in enumerate(df['회원주소']):
        # Check if address is not None
        if address is not None:
            # Analyze the address with the NLP model
            doc = nlp(address.strip())

            # Create a dictionary to store the entities for this address
            entities = {'index': idx, 'address': address.strip()}

            # Add the entities to the dictionary
            for ent in doc.ents:
                entities[ent.label_] = ent.text

            # Append the entities to the list
            entities_list.append(entities)

        # Append the entities to the DataFrame
    entities_df = pd.DataFrame(entities_list)
    # Merge the original DataFrame with the entities DataFrame
    df = pd.merge(df.reset_index(), entities_df, on='index', how='left')
    # Drop the 'index' column
    df = df.drop(columns='index')
    # df['건물층'] = df['건물호'].apply(get_floor)
    df['건물층'] = np.where(df['건물층'].isna(), df['건물호'].apply(get_floor), df['건물층'])
    # Return the DataFrame
    return df


def get_floor(room_number):
    if not room_number:
        return ""
    # Check if the room number is a string
    if isinstance(room_number, str):
        # Check if the string starts with "비"
        if room_number.startswith("B") or room_number.startswith("b"):
            # Remove "비" from the start of the string
            room_number = room_number[1:]
            # Indicate that this is a basement floor
            floor_indicator = '지하'
        else:
            floor_indicator = ''
        # Remove the string "호" from the room number
        room_number = room_number.replace("호", "")

        # Check if the room number is a digit
        if room_number.isdigit():
            # Take all but the last two digits to get the floor number
            floor_number = room_number[:-2]
            return floor_indicator + str(floor_number) + '층'
        else:
            return "Invalid room number"
    else:
        return ""


# GPU를 사용하도록 설정
if prefer_gpu():
    print("GPU is being used.")
else:
    print("CPU is being used.")
# 새 모델 생성 또는 기존 모델 로드
nlp = spacy.blank('ko')  # 새 모델을 생성하거나
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# nlp = to_device(nlp, device)
# NER 파이프라인 추가
if 'ner' not in nlp.pipe_names:
    ner = nlp.add_pipe('ner', last=True)
else:
    ner = nlp.get_pipe('ner')

# GPU 사용 가능 여부 확인
if torch.cuda.is_available():
    print("GPU is being used.")
else:
    print("CPU is being used.")


# 저장된 모델 로드
nlp = spacy.load("./ko_addr_ner_model_999/")

# entity_labels = get_entity_labels(nlp)
# df = make_df_with_entities(nlp, entity_labels)
df = make_df_with_entities(nlp)
df.to_csv('output.tsv', sep='\t', index=False)

# 전체주소, 건물명_단지명, 동, 층, 호

# 건물명_단지명, : 건물명 또는 단지명이 들어감
# 건물 명이나 단지명은 한 주소에 다음과 같은 형태로 나올 수 있음.
# 1번만 나올 경우  바로 사용 가능
# 두 개 나올 경우
# 1. 둘 다 공백 제거후 같은 이름이면 하나만 사용
# 2. 둘 다 공백 제거후 한쪽의 문자열이 다른 한쪽에 포함 될 경우  더 긴 쪽부터 사용 (사용 가능하면 중지,앞의 내용으로 조회등 동작이 안되면 짧은 내용까지 확인)
# 3. 둘 다 공백 제거후 전혀 같은 문자열이 아닐 경우 무조건 한 번 씩 조회해보고 주소 조회가 안되면 두개를 합친 문자열로 조회해본다.  이 때 나오는 좌표가 기존에 준비해둔 좌표와 더 가까운 것을 사용함.

# with open('addr_src.txt', 'r') as file:
#     for address in file:
#         analyze_address(address.strip())
#         input("Press Enter to continue...")

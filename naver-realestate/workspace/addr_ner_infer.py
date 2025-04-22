from spacy import prefer_gpu
import torch
from spacy.util import minibatch, compounding
from spacy.training import offsets_to_biluo_tags
import json
import spacy
import pandas as pd
from spacy.training import Example
import random


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
nlp = spacy.load("./ko_addr_ner_model_1000/")


# 학습된 모델로 주소 분석
def analyze_address(address):
    doc = nlp(address)
    print(f"주소:{address}")
    for ent in doc.ents:
        print(f"{ent.text}: {ent.label_}")


with open('addr_src.txt', 'r') as file:
    for address in file:
        analyze_address(address.strip())
        input("Press Enter to continue...")

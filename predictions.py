import pandas as pd
from sklearn.metrics import accuracy_score

def prepare_data(data):
    # 예측을 위한 데이터 전처리
    features = [col for col in data.columns if col not in ['중도탈락여부', '중도탈락최소', '중도탈락최대', '연번', '입학년도', '학번', '이름']]
    return data, features

def predict_dropout(model, data, features):
    # 학습에 사용된 피처만 선택
    X_new = data[features].copy()

    # 예측 수행
    data['중도탈락_예측'] = model.predict(X_new)
    data['중도탈락_스코어'] = model.predict_proba(X_new)[:, 1]

    # 리스크 그룹화
    data['리스크_그룹'] = pd.cut(
        data['중도탈락_스코어'],
        bins=[-float('inf'), 0.3, 0.7, float('inf')],
        labels=['저위험', '중위험', '고위험']
    )
    return data
import streamlit as st
import pandas as pd
import joblib
from upload import load_model_and_data
from predictions import prepare_data, predict_dropout
from visualizations import show_overall_results, show_risk_group, show_major_distribution, show_income_distribution, show_gpa_distribution
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from io import BytesIO

# 페이지 설정
st.set_page_config(
    page_title='중도탈락 예측 모듈',
    page_icon=':school:',
    layout='wide'
)

# CSS 스타일 설정
st.markdown("""
    <style>
    .icon {display: inline-block;margin-right: 5px;width: 10px;height: 10px;border-radius: 50%; 
            }
    .red { background-color: #FF0000; }
    .green { background-color: #00FF00; }
    .orange { background-color: #FFA500; }
            .wide-table {
        width: 100%;
    }
    .highlighted-row {
        font-weight: bold;
        text-align: center;
    }
    </style>
    <h2 style="color: #FFA500;">🏫K-LXP 학생 중도탈락 예측 모듈</h1>
    """, unsafe_allow_html=True)

# 페이지 구분
st.sidebar.title("📋 메뉴선택")
page_selection = st.sidebar.radio("페이지", ["파일 업로드", "결과 보기"])

# 파일 업로드 페이지
if page_selection == "파일 업로드":
    st.subheader("모델 업로드")
    st.markdown("""
    <style>
    .box-with-shadow {
        background-color: #C1C1C1FF; /* 박스 배경색 */
        padding: 15px; /* 박스 내부 여백 */
        border-radius: 10px; /* 박스 모서리 둥글게 */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* 그림자 효과 */
        margin-bottom: 15px; /* 박스 하단 간격 */
    }
    .box-with-shadow p {
        margin-bottom: 1px; /* 텍스트 줄 간격 */
        font-size: 16px; /* 글자 크기 조정 */
        font-weight: bold; /* 글자 굵기 */
        color: #333; /* 텍스트 색상 */
    }
    </style>
    <div class="box-with-shadow">
        <p>이 모듈(POC 1.0 버전)은 AI 예측 모델 기반으로 학생 중도 탈락 가능성을 예측합니다.</p>
        <p>중도 탈락 가능성이 높은 학생들을 조기 발굴하고 이를 개선하기 위한 방안을 마련할 수 있습니다.</p>
        <p>학생 데이터는 모듈 검증을 위해 임의로 작성되었습니다. 추후 대학 DB와 실시간 연동이 필요합니다</p>
                
    </div>
    """, unsafe_allow_html=True)
    uploaded_model = st.file_uploader("예측 모델 (.joblib 파일) 업로드", type="joblib")
    uploaded_data = st.file_uploader("테스트 데이터 (.csv 파일) 업로드", type="csv")

    if uploaded_model and uploaded_data:
        # 모델과 데이터를 세션 상태에 저장
        st.session_state.model = joblib.load(BytesIO(uploaded_model.read()))
        st.session_state.uploaded_data = pd.read_csv(uploaded_data)
        st.success("모델과 데이터가 성공적으로 업로드되었습니다.")

# 결과 보기 페이지
if page_selection == "결과 보기":
    if 'model' in st.session_state and 'uploaded_data' in st.session_state:
        model = st.session_state.model
        data = st.session_state.uploaded_data.copy()

        # 학습 시 사용된 피처 이름만 포함한 리스트 정의
        features = [col for col in data.columns if col not in ['중도탈락여부', '연번', '입학년도', '학번', '이름']]

        # 데이터 전처리 및 예측 수행
        data = predict_dropout(model, data, features)

        # 메뉴 옵션별 시각화
        menu_option = st.sidebar.selectbox("결과 보기 옵션", ["전체 예측 결과", "그룹 분포 보기", "전공 분포 비교", "소득 분위 분포 비교", "학점 분포 비교"])
        
        # 각 메뉴 옵션에 따라 시각화 함수 호출
        if menu_option == "전체 예측 결과":
            show_overall_results(data)
        elif menu_option == "그룹 분포 보기":
            show_risk_group(data, features)
        elif menu_option == "전공 분포 비교":
            show_major_distribution(data)
        elif menu_option == "소득 분위 분포 비교":
            show_income_distribution(data)
        elif menu_option == "학점 분포 비교":
            show_gpa_distribution(data)
    else:
        st.warning("먼저 '파일 업로드' 페이지에서 모델과 데이터를 업로드하세요.")

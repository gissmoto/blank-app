import streamlit as st
import pandas as pd
import joblib
from io import BytesIO

def load_model_and_data():
    st.subheader("파일 업로드")

    # 모델 파일 업로드 및 로드
    if 'model' not in st.session_state:
        uploaded_model = st.file_uploader("학습된 예측 모델 (.joblib) 파일을 업로드하세요.", type="joblib")
        if uploaded_model:
            st.session_state.model = joblib.load(BytesIO(uploaded_model.read()))
            st.success("모델이 성공적으로 업로드되었습니다.")
    else:
        st.success("저장된 모델을 사용 중입니다.")

    # 데이터 파일 업로드
    uploaded_data = st.file_uploader("학생 데이터가 포함된 CSV 파일을 업로드하세요.", type="csv")
    if uploaded_data:
        st.session_state.uploaded_data = pd.read_csv(uploaded_data)
        st.success("데이터 파일이 성공적으로 업로드되었습니다.")

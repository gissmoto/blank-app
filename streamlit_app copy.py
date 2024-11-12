import streamlit as st
from upload import load_model, load_data
from predictions import make_predictions
from visualizations import show_major_distribution, show_income_distribution, show_gpa_distribution
import style

# 페이지 설정
st.set_page_config(page_title='중도탈락 예측 모듈', page_icon=':school:')

# 스타일 적용
style.apply_css()

st.title("학생 중도탈락 예측 모듈")
st.write("업로드된 데이터를 바탕으로 학생들의 중도탈락 예측 결과를 화면에 표시합니다.")

# 사이드바 메뉴로 페이지 구분
page_selection = st.sidebar.radio("페이지 선택", ["파일 업로드", "결과 보기"])

# 파일 업로드 페이지
if page_selection == "파일 업로드":
    st.subheader("파일 업로드")
    model = load_model()  # 모델을 세션 상태에 저장
    data = load_data()    # 데이터를 세션 상태에 저장

elif page_selection == "결과 보기":
    model = st.session_state.get("model")
    data = st.session_state.get("data")

    # model이 None이 아니고 data가 DataFrame이며 비어 있지 않을 때만 예측 수행
    if model is not None and data is not None and not data.empty:
        make_predictions(model, data)
    else:
        st.warning("먼저 '파일 업로드' 페이지에서 모델과 데이터를 업로드하세요.")

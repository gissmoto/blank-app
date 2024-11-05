import streamlit as st
import pandas as pd
import joblib
from io import BytesIO
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title='중도탈락 예측 모듈',
    page_icon=':school:',
)

# 배경색을 흰색으로, 글자를 검정색으로 설정하는 CSS 코드
st.markdown(
    """
    <style>
    .icon {
        display: inline-block;
        margin-right: 5px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    .red { background-color: #FF0000; }
    .green { background-color: #00FF00; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("학생 중도탈락 예측 모듈")
st.write("업로드된 데이터를 바탕으로 학생들의 중도탈락 예측 결과를 화면에 표시합니다.")

# 사이드바 메뉴로 페이지 구분
page_selection = st.sidebar.radio("페이지 선택", ["파일 업로드", "결과 보기"])

# 파일 업로드 페이지
if page_selection == "파일 업로드":
    st.subheader("파일 업로드")

    # 모델 파일 업로드 및 로드 (첫 업로드 이후에는 세션에 저장된 모델 재사용)
    if 'model' not in st.session_state:
        uploaded_model = st.file_uploader("학습된 예측 모델 (.joblib) 파일을 업로드하세요.", type="joblib")
        if uploaded_model:
            st.session_state.model = joblib.load(BytesIO(uploaded_model.read()))
            st.success("모델이 성공적으로 업로드되었습니다.")
    else:
        st.success("저장된 모델을 사용 중입니다.")

    # 데이터 파일 업로드 기능
    uploaded_data = st.file_uploader("학생 데이터가 포함된 CSV 파일을 업로드하세요.", type="csv")
    if uploaded_data:
        st.session_state.uploaded_data = pd.read_csv(uploaded_data)
        st.success("데이터 파일이 성공적으로 업로드되었습니다.")

# 결과 보기 페이지
elif page_selection == "결과 보기":
    # 모델과 데이터가 모두 업로드된 경우에만 결과 표시
    if 'model' in st.session_state and 'uploaded_data' in st.session_state:
        model = st.session_state.model
        data = st.session_state.uploaded_data.copy()

        # 예측을 위한 데이터 전처리 (모델 학습 시 사용하지 않은 열 제거)
        features = [col for col in data.columns if col not in ['중도탈락여부', '중도탈락최소', '중도탈락최대', '연번', '입학년도', '학번', '이름']]
        X_new = data[features]
        
        # 예측 수행 전에 중도탈락_예측 컬럼을 제거하여 피처와 일치시킴
        if '중도탈락_예측' in data.columns:
            data = data.drop(columns=['중도탈락_예측'])

        # 예측 수행
        data['중도탈락_예측'] = model.predict(X_new)

        # 중도탈락 학생 필터링
        dropout_students = data[data['중도탈락_예측'] == 1]

        # 전체 예측 결과에서 열 순서 재정렬 및 불필요한 열 제거
        display_data = data.drop(columns=['연번', '입학년도'])
        display_data = display_data[['학번', '이름'] + [col for col in display_data.columns if col not in ['학번', '이름']]]

        # 사이드바에서 항목 선택
        menu_option = st.sidebar.selectbox("결과 보기 옵션", ["전체 예측 결과", "전공 분포 비교", "소득 분위 분포 비교", "학점 분포 비교"])

        if menu_option == "전체 예측 결과":
            st.subheader("전체 예측 결과")
            st.dataframe(display_data)

            # 중도탈락 예측 학생 목록을 아이콘과 함께 표시
            st.subheader("학생 목록 (중도탈락 예측 여부)")
            for index, row in data.iterrows():
                icon_color = "red" if row['중도탈락_예측'] == 1 else "green"
                st.markdown(
                    f'<div class="icon {icon_color}"></div> 학번: {row["학번"]} | 이름: {row["이름"]}',
                    unsafe_allow_html=True
                )

        elif menu_option == "전공 분포 비교":
            st.header("전공 분포 비교")
    
              # 전공 번호를 전공 이름으로 매핑
            major_mapping = {
               1: "기계공학부",
               2: "메카트로닉스공학부",
               3: "전기전자통신공학부",
               4: "컴퓨터공학부",
               5: "에너지신소재화학공학부",
               6: "산업경영학부",
              7: "디자인건축공학부"
            }
    
    # 데이터와 중도탈락 학생 데이터 모두 전공 이름으로 매핑
            data['전공'] = data['전공'].map(major_mapping)
            dropout_students['전공'] = dropout_students['전공'].map(major_mapping)
    
    # 전공별 전체 학생 수와 중도탈락 학생 수 계산
            major_counts_all = data['전공'].value_counts().reset_index()
            major_counts_dropout = dropout_students['전공'].value_counts().reset_index()
            major_counts_all.columns = ['전공', '전체 학생 수']
            major_counts_dropout.columns = ['전공', '중도탈락 학생 수']
    
    # 전공별 데이터 병합 및 시각화
            major_comparison = major_counts_all.merge(major_counts_dropout, on='전공', how='left').fillna(0)
            fig_major = px.bar(major_comparison, x='전공', y=['전체 학생 수', '중도탈락 학생 수'], barmode='group')
            st.plotly_chart(fig_major)

        elif menu_option == "소득 분위 분포 비교":
            st.header("소득 분위 분포 비교")
            income_counts_all = data['소득분위'].value_counts().reset_index()
            income_counts_dropout = dropout_students['소득분위'].value_counts().reset_index()
            income_counts_all.columns = ['소득분위', '전체 학생 수']
            income_counts_dropout.columns = ['소득분위', '중도탈락 학생 수']
            income_comparison = income_counts_all.merge(income_counts_dropout, on='소득분위', how='left').fillna(0)
            fig_income = px.bar(income_comparison, x='소득분위', y=['전체 학생 수', '중도탈락 학생 수'], barmode='group')
            st.plotly_chart(fig_income)

        elif menu_option == "학점 분포 비교":
            st.header("학점 분포 비교")
            fig_gpa = px.histogram(data, x='대학취득평점', color='중도탈락_예측', nbins=20,
                                   labels={'color': '중도탈락 여부'}, title="전체 학생과 중도탈락 학생의 학점 분포")
            st.plotly_chart(fig_gpa)

    else:
        st.warning("먼저 '파일 업로드' 페이지에서 모델과 데이터를 업로드하세요.")

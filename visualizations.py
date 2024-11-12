import streamlit as st
import pandas as pd
import plotly.express as px

def show_overall_results(data):
    st.subheader("학생 목록 (중도탈락 예측 여부 및 산출 스코어)")
    for index, row in data.iterrows():
        if 0.4 <= row['중도탈락_스코어'] <= 0.7:
            icon_color = "orange"
        elif row['중도탈락_예측'] == 1:
            icon_color = "red"
        else:
            icon_color = "green"
        
        dropout_score = f"{row['중도탈락_스코어']:.2f}"
        st.markdown(
            f'<div class="icon {icon_color}"></div> 학번: {row["학번"]} | 이름: {row["이름"]} | '
            f'중도탈락 예상 스코어: {dropout_score}',
            unsafe_allow_html=True
        )

def show_risk_group(data, features):
    # 리스크 그룹별 학생 수 분포
    st.subheader("리스크 그룹별 학생 분포")
    risk_counts = data['리스크_그룹'].value_counts().reset_index()
    risk_counts.columns = ['리스크 그룹', '학생 수']

    # 바 차트: 리스크 그룹별 학생 수
    fig_risk = px.bar(
        risk_counts, 
        x='리스크 그룹', 
        y='학생 수', 
        color='리스크 그룹', 
        title="리스크 그룹별 학생 수 분포", 
        color_discrete_map={'고위험': '#FF6347', '중위험': '#FFA500', '저위험': '#00BFFF'}  # 색상 설정
    )
    fig_risk.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # 투명한 배경
        paper_bgcolor='rgba(0,0,0,0)',
        title=dict(font=dict(size=24), x=0.5),
        xaxis=dict(title='', tickfont=dict(size=14)),
        yaxis=dict(title='학생 수', tickfont=dict(size=14)),
        legend=dict(title='리스크 그룹', font=dict(size=14)),
        hoverlabel=dict(font_size=14)
    )
    st.plotly_chart(fig_risk)

    # 리스크 그룹별 평균 특성
    st.subheader("리스크 그룹별 평균 특성")
    mean_features_by_risk = data.groupby('리스크_그룹')[features].mean().reset_index()
    melted_features = mean_features_by_risk.melt(id_vars='리스크_그룹')

    # 바 차트: 리스크 그룹별 평균 특성
    fig_features = px.bar(
        melted_features,
        x='variable', 
        y='value', 
        color='리스크_그룹', 
        barmode='group',
        title="리스크 그룹별 평균 특성",
        labels={'variable': '특성', 'value': '평균 값'}, 
        color_discrete_map={'고위험': '#FF6347', '중위험': '#FFA500', '저위험': '#00BFFF'}  # 색상 설정
    )
    fig_features.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # 투명한 배경
        paper_bgcolor='rgba(0,0,0,0)',
        title=dict(font=dict(size=24), x=0.5),
        xaxis=dict(title='특성', tickfont=dict(size=14)),
        yaxis=dict(title='평균 값', tickfont=dict(size=14)),
        legend=dict(title='리스크 그룹', font=dict(size=14)),
        hoverlabel=dict(font_size=14)
    )
    st.plotly_chart(fig_features)

    st.subheader("리스크 그룹별 학생 목록")

    # 각 리스크 그룹에 맞는 스타일 적용 함수
     # 각 리스크 그룹에 맞는 스타일 적용 함수
    def highlight_risk(row):
        color = ''
        if row['리스크_그룹'] == '고위험':
            color = ' color: #B22222;'  # 연한 빨간색 배경, 진한 빨간 텍스트
        elif row['리스크_그룹'] == '중위험':
            color = ' color: #CC8400;'  # 연한 오렌지색 배경, 진한 오렌지 텍스트
        elif row['리스크_그룹'] == '저위험':
            color = ' color: #4682B4;'  # 연한 파란색 배경, 진한 파란 텍스트
        return [color] * len(row)

    # 리스크 그룹별로 테이블을 보여주기
    for risk_level in ['고위험', '중위험', '저위험']:
        st.write(f"**{risk_level} 그룹 학생 목록**")

        # 각 그룹의 학생 데이터를 필터링
        risk_data = data[data['리스크_그룹'] == risk_level][['학번', '이름', '중도탈락_스코어', '리스크_그룹']]
        
        # 테이블 스타일 적용
        styled_table = risk_data.style.apply(highlight_risk, axis=1)\
                                      .set_properties(**{'text-align': 'center', 'font-size': '14px'})\
                                      .set_table_attributes('class="wide-table highlighted-row"')
        
        st.write(styled_table.to_html(), unsafe_allow_html=True)
        
def show_major_distribution(data):
    st.header("전공 분포 비교")
    major_mapping = {
        1: "기계공학부", 2: "메카트로닉스공학부", 3: "전기전자통신공학부",
        4: "컴퓨터공학부", 5: "에너지신소재화학공학부", 6: "산업경영학부", 7: "디자인건축공학부"
    }
    data['전공'] = data['전공'].map(major_mapping)
    dropout_students = data[data['중도탈락_예측'] == 1]

    major_counts_all = data['전공'].value_counts().reset_index()
    major_counts_dropout = dropout_students['전공'].value_counts().reset_index()
    major_counts_all.columns = ['전공', '전체 학생 수']
    major_counts_dropout.columns = ['전공', '중도탈락 학생 수']
    major_comparison = major_counts_all.merge(major_counts_dropout, on='전공', how='left').fillna(0)
    major_comparison['중도탈락 학생 수'] = major_comparison['중도탈락 학생 수'].astype(int)

    fig_major = px.bar(major_comparison, x='전공', y=['전체 학생 수', '중도탈락 학생 수'], barmode='group', title="전공별 전체 학생 수와 중도탈락 학생 수 비교")
    st.plotly_chart(fig_major)

def show_income_distribution(data):
    st.header("소득 분위 분포 비교")
    dropout_students = data[data['중도탈락_예측'] == 1]
    income_counts_all = data['소득분위'].value_counts().reset_index()
    income_counts_dropout = dropout_students['소득분위'].value_counts().reset_index()
    income_counts_all.columns = ['소득분위', '전체 학생 수']
    income_counts_dropout.columns = ['소득분위', '중도탈락 학생 수']
    income_comparison = income_counts_all.merge(income_counts_dropout, on='소득분위', how='left').fillna(0)

    fig_income = px.bar(income_comparison, x='소득분위', y=['전체 학생 수', '중도탈락 학생 수'], barmode='group')
    st.plotly_chart(fig_income)

def show_gpa_distribution(data):
    st.header("학점 분포 비교")
    fig_gpa = px.histogram(data, x='대학취득평점', color='중도탈락_예측', nbins=20, labels={'color': '중도탈락 여부'}, title="전체 학생과 중도탈락 학생의 학점 분포")
    st.plotly_chart(fig_gpa)

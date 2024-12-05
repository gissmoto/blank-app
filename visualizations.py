import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
import matplotlib.font_manager as fm

def show_overall_results(data):
    st.subheader("수강 학생 목록 (중도탈락 예측 여부 및 산출 스코어)")
    total_students = len(data)
    high_risk_students = len(data[data['중도탈락_스코어'] >= 0.7])
    high_risk_percentage = (high_risk_students / total_students) * 100
    low_risk_students = total_students - high_risk_students

# CSS 스타일 정의
    st.markdown(
    """
    <style>
    .custom-container {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    .stColumn > div {
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
    )

# 레이아웃 설정
    col1, col2 = st.columns([2, 1])
     
    with col1:
        # 스타일을 적용한 div 추가
        
        for index, row in data.iterrows():
            if 0.4 <= row['중도탈락_스코어'] <= 0.7:
                icon_color = "orange"
            elif row['중도탈락_예측'] == 1:
                icon_color = "red"
            else:
                icon_color = "green"

            dropout_score = f"{row['중도탈락_스코어']:.2f}"
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div class="icon" style="width: 15px; height: 15px; background-color: {icon_color}; border-radius: 50%;"></div>
                    <span style="margin-right: 30px;">학번: {row["학번"]}</span>
                    <span style="margin-right: 30px;">이름: {row["이름"]}</span>
                    <span>중도탈락 예상 스코어: {dropout_score}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        

        
    with col2:
        # 스타일을 적용한 div 추가
        st.markdown(f"""
            <p style="font-size:16px;">고위험군 학생 비율: <strong>{high_risk_percentage:.2f}% ({total_students} 중 {high_risk_students} 명)</strong></p>
        """, unsafe_allow_html=True)

        # Plotly 도넛 차트 생성
        labels = ['High Risk', 'Low Risk']
        sizes = [high_risk_students, low_risk_students]
        colors = ['red', '#A9A9A9']

        fig = go.Figure(go.Pie(
            labels=labels,
            values=sizes,
            hole=0.6,  # 도넛 차트의 구멍 크기
            textinfo='percent+label',
            marker=dict(colors=colors, line=dict(color='#000000', width=2)),
        ))
        st.plotly_chart(fig)
        """
        features = [col for col in data.columns if col not in ['중도탈락_스코어', '중도탈락_예측', '학번', '이름','리스크_그룹']]
        #st.write("중도탈락 스코어에 활용된 특성:", features)
        #st.write("중도탈락 스코어에 활용된 특성:", features)
        X = data[features]
        y = data['중도탈락_스코어']

        # 랜덤 포레스트 모델 학습
        model = RandomForestRegressor(random_state=42)
        model.fit(X, y)

        # 특성 중요도 계산
        importance = model.feature_importances_
        importance_df = pd.DataFrame({
            '특성': features,
            '중요도': importance
        }).sort_values(by='중요도', ascending=False)

        # 중요도 출력
        st.subheader("특성 중요도")
        st.write(importance_df)
               
        """
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

    """#히트맵 그리기
    st.subheader("리스크 그룹별 평균 특성 (히트맵)")

    # 리스크 그룹별 평균 값 계산
    # 리스크 그룹별 합계 대비 비율 계산
    mean_features_by_risk = data.groupby('리스크_그룹')[features].sum()
    proportion_features_by_risk = mean_features_by_risk.div(mean_features_by_risk.sum(axis=1), axis=0) * 100

    # 히트맵 생성 (특성을 가로축에, 리스크 그룹을 세로축에 표시)
    fig_heatmap = px.imshow(
        proportion_features_by_risk,
        labels={"x": "특성", "y": "리스크 그룹", "color": "비율 (%)"},
        x=proportion_features_by_risk.columns,
        y=proportion_features_by_risk.index,
        color_continuous_scale="RdYlBu",  # 색상 스케일: 빨강-노랑-파랑
        range_color=[0, 100]  # 비율은 0%에서 100% 사이로 제한
    )

    # 레이아웃 설정
    fig_heatmap.update_layout(
        autosize=True,            # 그래프 크기 자동 조정
        height=600,               # 높이 설정
        title="리스크 그룹별 특성 비율 (히트맵)",
        title_x=0.5,
        xaxis_title="특성",
        yaxis_title="리스크 그룹",
        xaxis=dict(tickangle=-45, tickfont=dict(size=12)),  # x축 라벨 기울기 설정
        yaxis=dict(tickfont=dict(size=12)),
        coloraxis_colorbar=dict(title="비율 (%)", tickfont=dict(size=12), titlefont=dict(size=14))
    )

    # 그래프 출력
    st.subheader("리스크 그룹별 특성 비율 (히트맵)")
    st.plotly_chart(fig_heatmap)

    # 히트맵 생성 (특성을 가로축에, 리스크 그룹을 세로축에 표시)
    fig_heatmap = px.imshow(
        mean_features_by_risk,
        labels={"x": "특성", "y": "리스크 그룹", "color": "평균 값"},
        x=mean_features_by_risk.columns,
        y=mean_features_by_risk.index,
        color_continuous_scale="RdYlBu",  # 색상 스케일: 빨강-노랑-파랑
        range_color=[mean_features_by_risk.values.min(), mean_features_by_risk.values.max()]  # 색상 범위 최적화
    )

    # 레이아웃 설정
    fig_heatmap.update_layout(
        autosize=True,            # 그래프 크기 자동 조정
        height=600,               # 높이 설정
        title="리스크 그룹별 평균 특성 (히트맵)",
        title_x=0.5,
        xaxis_title="특성",
        yaxis_title="리스크 그룹",
        xaxis=dict(tickangle=-45, tickfont=dict(size=12)),  # x축 라벨 기울기 설정
        yaxis=dict(tickfont=dict(size=12)),
        coloraxis_colorbar=dict(title="평균 값", tickfont=dict(size=12), titlefont=dict(size=14))
    )

    # 그래프 출력
    st.plotly_chart(fig_heatmap)
"""

            # 리스크 그룹별 평균 특성
    st.subheader("리스크 그룹별 평균 특성")

    # 사용자가 선택할 수 있도록 멀티 셀렉트 추가
    selected_features = st.multiselect("보고 싶은 특성을 선택하세요:", options=features, default=[])

    if selected_features:
        # 리스크 그룹별 선택한 특성의 평균 값 계산
        mean_features_by_risk = data.groupby('리스크_그룹')[selected_features].mean().reset_index()
        melted_features = mean_features_by_risk.melt(id_vars='리스크_그룹', value_vars=selected_features)

        # 바 차트: 리스크 그룹별 평균 특성 (가로형)
        fig_features = px.bar(
            melted_features,
            y='variable',      # y축에 '특성'을 설정
            x='value',         # x축에 '평균 값'을 설정
            color='리스크_그룹',
            barmode='group',
            orientation='h',   # 가로 막대 설정
            title="리스크 그룹별 평균 특성",
            labels={'variable': '특성', 'value': '평균 값'}, 
            color_discrete_map={'고위험': '#FF6347', '중위험': '#FFA500', '저위험': '#00BFFF'}  # 색상 설정
        )

        # 레이아웃 설정
        fig_features.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',  # 투명한 배경
            paper_bgcolor='rgba(0,0,0,0)',
            title=dict(font=dict(size=24), x=0.5),
            yaxis=dict(title='특성', tickfont=dict(size=14)),
            xaxis=dict(title='평균 값', tickfont=dict(size=14)),
            legend=dict(title='리스크 그룹', font=dict(size=14)),
            height=800,
            hoverlabel=dict(font_size=14)
        )

        # 그래프 출력
        st.plotly_chart(fig_features)
    else:
        st.warning("특성을 하나 이상 선택하세요.")

    
    




# 예시 데이터로 호출
# show_risk_group_heatmap(data, features)

def show_major_distribution(data):
    st.header("전공 분포 비교")

    # 전공 번호를 전공 이름으로 매핑
    major_mapping = {
        1: "기계공학부", 2: "메카트로닉스공학부", 3: "전기전자통신공학부",
        4: "컴퓨터공학부", 5: "에너지신소재화학공학부", 6: "산업경영학부", 7: "디자인건축공학부"
    }
    data['전공'] = data['전공'].map(major_mapping)
    dropout_students = data[data['중도탈락_예측'] == 1]

    # 전체 학생 수 및 중도탈락 학생 수 계산
    major_counts_all = data['전공'].value_counts().reset_index()
    major_counts_dropout = dropout_students['전공'].value_counts().reset_index()
    major_counts_all.columns = ['전공', '전체 학생 수']
    major_counts_dropout.columns = ['전공', '중도탈락 학생 수']
    major_comparison = major_counts_all.merge(major_counts_dropout, on='전공', how='left').fillna(0)
    major_comparison['중도탈락 학생 수'] = major_comparison['중도탈락 학생 수'].astype(int)

    # Plotly 그래프 생성 및 스타일 추가
    fig_major = px.bar(
        major_comparison,
        x='전공',
        y=['전체 학생 수', '중도탈락 학생 수'],
        barmode='group',
        title="전공별 전체 학생 수와 중도탈락 학생 수 비교",
        labels={'value': '학생 수', 'variable': '학생 구분'},
        color_discrete_map={'전체 학생 수': '#00BFFF', '중도탈락 학생 수': '#d62728'}  # 색상 맵핑
    )

    # 스타일 조정
    fig_major.update_layout(
        title={'text': "전공별 전체 학생 수와 중도탈락 학생 수 비교"},
        xaxis_title="전공",
        yaxis_title="학생 수",
        legend_title_text="학생 구분",
        plot_bgcolor='rgba(0,0,0,0)',  # 투명한 배경
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14),
        xaxis_tickangle=90  # x 축 레이블을 세로로 표시

    )

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

import streamlit as st
import pandas as pd
import plotly.express as px
import glob

# 페이지 설정
st.set_page_config(
    page_title="K콘텐츠 간행물정보 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📚 K콘텐츠 간행물정보 제목 길이별 조회수 분석")
st.markdown("마우스를 점 위에 올리면 **기사 제목, 날짜, 조회수**가 팝업으로 나타나며, 추세선이 함께 표시됩니다.")

# 데이터 로드 함수 (폴더 안의 CSV 파일 자동 탐색)
@st.cache_data
def load_data():
    csv_files = glob.glob("*.csv")
    if not csv_files:
        raise FileNotFoundError("폴더에 CSV 파일이 존재하지 않습니다.")
    
    target_file = csv_files[0]
    
    try:
        df_pub = pd.read_csv(target_file, encoding="utf-8")
    except:
        df_pub = pd.read_csv(target_file, encoding="cp949")
        
    return df_pub, target_file

# 데이터 불러오기 실행
try:
    df_pub, loaded_file_name = load_data()
except Exception as e:
    st.error(f"❌ 파일을 불러오는 중 오류가 발생했습니다. (오류내용: {e})")
    st.stop()

# 탭 구성 (메인 제목 분석 vs 서브제목 분석)
tab1, tab2 = st.tabs(["📖 메인 제목 길이 분석", "📑 서브제목 길이 분석"])

with tab1:
    st.subheader("메인 제목 길이에 따른 조회수")
    
    # 메인 제목 길이 계산
    df_pub['메인제목_길이'] = df_pub['제목'].astype(str).apply(len)
    
    # 주요 지표 요약
    col1, col2, col3 = st.columns(3)
    col1.metric("총 간행물 수", f"{len(df_pub):,}개")
    col2.metric("평균 메인 제목 길이", f"{df_pub['메인제목_길이'].mean():.1f}자")
    col3.metric("평균 조회수", f"{df_pub['조회수'].mean():,.1f}회")
    
    # Plotly 인터랙티브 산점도 + 추세선(trendline="ols") 추가
    fig1 = px.scatter(
        df_pub,
        x='메인제목_길이',
        y='조회수',
        hover_data=['제목', '등록일', '조회수'], 
        labels={'메인제목_길이': '제목 길이 (글자수)', '조회수': '조회수'},
        title="메인 제목 길이별 조회수 분포 및 추세선",
        trendline="ols"  # 회귀선(추세선) 추가
    )
    fig1.update_traces(marker=dict(size=8, color='teal'))
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.subheader("서브제목 길이에 따른 조회수")
    
    # 서브제목이 존재하는 데이터만 추출
    df_pub_sub = df_pub.dropna(subset=['서브제목']).copy()
    df_pub_sub['서브제목_길이'] = df_pub_sub['서브제목'].astype(str).apply(len)
    df_pub_sub['조회수_정제'] = df_pub_sub['서브조회수'].fillna(df_pub_sub['조회수'])
    
    # 주요 지표 요약
    col1, col2, col3 = st.columns(3)
    col1.metric("서브제목 있는 간행물 수", f"{len(df_pub_sub)}개")
    col2.metric("평균 서브제목 길이", f"{df_pub_sub['서브제목_길이'].mean():.1f}자" if len(df_pub_sub) > 0 else "0자")
    col3.metric("평균 조회수", f"{df_pub_sub['조회수_정제'].mean():,.1f}회" if len(df_pub_sub) > 0 else "0회")
    
    if len(df_pub_sub) > 0:
        # Plotly 인터랙티브 산점도 + 추세선(trendline="ols") 추가
        fig2 = px.scatter(
            df_pub_sub,
            x='서브제목_길이',
            y='조회수_정제',
            hover_data=['서브제목', '서브등록일', '조회수_정제'], 
            labels={'서브제목_길이': '서브제목 길이 (글자수)', '조회수_정제': '조회수'},
            title="서브제목 길이별 조회수 분포 및 추세선",
            trendline="ols"  # 회귀선(추세선) 추가
        )
        fig2.update_traces(marker=dict(size=8, color='purple'))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("분석할 서브제목 데이터가 존재하지 않습니다.")

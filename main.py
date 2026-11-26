import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 페이지 설정
st.set_page_config(
    page_title="콘텐츠 제목 길이별 조회수 분석",
    page_icon="📊",
    layout="wide"
)

# 한글 폰트 깨짐 방지 설정
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.title("📊 한국콘텐츠진흥원 데이터 분석 앱")
st.markdown("제목 길이에 따른 조회수 분포를 분석한 대시보드입니다.")

# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    news_file = "한국콘텐츠진흥원_보도자료_20260806.csv"
    pub_file = "한국콘텐츠진흥원_K콘텐츠 간행물정보_20170310.csv"
    
    # 보도자료 파일 읽기
    try:
        df_news = pd.read_csv(news_file, encoding="utf-8")
    except:
        df_news = pd.read_csv(news_file, encoding="cp949")
        
    # 간행물정보 파일 읽기
    try:
        df_pub = pd.read_csv(pub_file, encoding="utf-8")
    except:
        df_pub = pd.read_csv(pub_file, encoding="cp949")
        
    return df_news, df_pub

# 데이터 불러오기 실행
df_news, df_pub = load_data()

# 화면 탭 구성
tab1, tab2 = st.tabs(["📰 1번 보도자료 분석", "🔄 1,2번 서브제목 비교"])

with tab1:
    st.subheader("보도자료 메인 제목 길이에 따른 조회수")
    
    # 제목 길이 계산
    df_news['제목_길이'] = df_news['제목'].astype(str).apply(len)
    
    # 주요 지표 요약
    col1, col2, col3 = st.columns(3)
    col1.metric("총 보도자료 수", f"{len(df_news):,}개")
    col2.metric("평균 제목 길이", f"{df_news['제목_길이'].mean():.1f}자")
    col3.metric("평균 조회수", f"{df_news['조회수'].mean():,.1f}회")
    
    # 시각화 그래프
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df_news, x='제목_길이', y='조회수', alpha=0.6, color='royalblue', ax=ax)
    sns.regplot(data=df_news, x='제목_길이', y='조회수', scatter=False, color='darkorange', ax=ax)
    ax.set_title("보도자료 제목 길이 vs 조회수", fontsize=14)
    ax.set_xlabel("제목 글자수", fontsize=12)
    ax.set_ylabel("조회수", fontsize=12)
    st.pyplot(fig)

with tab2:
    st.subheader("자료별 서브제목 길이에 따른 조회수 비교")
    
    # 1번 자료 서브제목 처리
    df_news_sub = df_news.dropna(subset=['서브제목']).copy()
    df_news_sub['서브제목_길이'] = df_news_sub['서브제목'].astype(str).apply(len)
    df_news_sub['출처'] = '1번 보도자료'
    df_news_sub['조회수_정제'] = df_news_sub['조회수']
    
    # 2번 자료 서브제목 처리
    df_pub_sub = df_pub.dropna(subset=['서브제목']).copy()
    df_pub_sub['서브제목_길이'] = df_pub_sub['서브제목'].astype(str).apply(len)
    df_pub_sub['출처'] = '2번 간행물'
    df_pub_sub['조회수_정제'] = df_pub_sub['서브조회수'].fillna(df_pub_sub['조회수'])
    
    # 데이터 병합
    combined_df = pd.concat([
        df_news_sub[['서브제목_길이', '조회수_정제', '출처']],
        df_pub_sub[['서브제목_길이', '조회수_정제', '출처']]
    ])
    
    # 지표 요약
    col1, col2 = st.columns(2)
    col1.metric("1번 자료 서브제목 수", f"{len(df_news_sub)}개")
    col2.metric("2번 자료 서브제목 수", f"{len(df_pub_sub)}개")
    
    # 시각화 그래프
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=combined_df, x='서브제목_길이', y='조회수_정제', hue='출처', alpha=0.7, ax=ax)
    ax.set_title("서브제목 길이별 조회수 비교", fontsize=14)
    ax.set_xlabel("서브제목 글자수", fontsize=12)
    ax.set_ylabel("조회수", fontsize=12)
    st.pyplot(fig)

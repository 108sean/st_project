import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 페이지 설정
st.set_page_config(
    page_title="콘텐츠 제목 길이별 조회수 분석",
    page_icon="📊",
    layout="wide"
)

# 폰트 설정 (한글 깨짐 방지)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.title("📊 한국콘텐츠진흥원 데이터 분석 앱")

# 데이터 로드 (파일이 없을 경우 업로드 기능 제공)
@st.cache_data
def load_data(news_file, pub_file):
    df_news = pd.read_csv(news_file, encoding="utf-8" if "utf-8" in str(news_file) else "cp949")
    df_pub = pd.read_csv(pub_file, encoding="utf-8" if "utf-8" in str(pub_file) else "cp949")
    return df_news, df_pub

news_path = "한국콘텐츠진흥원_보도자료_20260806.csv"
pub_path = "한국콘텐츠진흥원_K콘텐츠 간행물정보_20170310.csv"

if not os.path.exists(news_path) or not os.path.exists(pub_path):
    st.warning("⚠️ 서버에 기본 CSV 파일이 존재하지 않습니다. 아래에서 파일을 직접 업로드해 주세요.")
    uploaded_news = st.file_uploader("보도자료 CSV 파일 업로드", type="csv")
    uploaded_pub = st.file_uploader("간행물정보 CSV 파일 업로드", type="csv")
    
    if uploaded_news and uploaded_pub:
        df_news = pd.read_csv(uploaded_news)
        df_pub = pd.read_csv(uploaded_pub)
    else:
        st.info("두 개의 CSV 파일을 모두 업로드해주세요.")
        st.stop()
else:
    try:
        df_news, df_pub = load_data(news_path, pub_path)
    except Exception as e:
        # 인코딩 문제 발생 시 cp949 재시도
        df_news = pd.read_csv(news_path, encoding="cp949")
        df_pub = pd.read_csv(pub_path, encoding="cp949")

# 세션 상태(Session State) 관리
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "news_main"

col1, col2 = st.columns(2)
with col1:
    if st.button("📰 1번 자료: 보도자료 제목 길이별 조회수", use_container_width=True):
        st.session_state.view_mode = "news_main"
with col2:
    if st.button("🔄 1,2번 자료 통합/비교: 서브제목 길이별 조회수", use_container_width=True):
        st.session_state.view_mode = "sub_title"

st.divider()

# 1. 1번 자료 보도자료 메인 제목 분석
if st.session_state.view_mode == "news_main":
    st.subheader("📰 [1번 자료] 보도자료 제목 길이에 따른 조회수 분석")
    df_news['제목_길이'] = df_news['제목'].astype(str).apply(len)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("총 데이터 수", f"{len(df_news):,}개")
    m2.metric("평균 제목 길이", f"{df_news['제목_길이'].mean():.1f}자")
    m3.metric("평균 조회수", f"{df_news['조회수'].mean():,.1f}회")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df_news, x='제목_길이', y='조회수', alpha=0.6, color='royalblue', ax=ax)
    sns.regplot(data=df_news, x='제목_길이', y='조회수', scatter=False, color='darkorange', ax=ax)
    ax.set_title("보도자료 제목 길이 vs 조회수", fontsize=14)
    ax.set_xlabel("제목 글자수", fontsize=12)
    ax.set_ylabel("조회수", fontsize=12)
    st.pyplot(fig)

# 2. 서브제목 길이 분석
elif st.session_state.view_mode == "sub_title":
    st.subheader("🔄 [1,2번 자료] 서브제목 길이에 따른 조회수 분석")
    
    df_news_sub = df_news.dropna(subset=['서브제목']).copy()
    df_news_sub['서브제목_길이'] = df_news_sub['서브제목'].astype(str).apply(len)
    df_news_sub['출처'] = '1번 보도자료'
    df_news_sub['조회수_정제'] = df_news_sub['조회수']
    
    df_pub_sub = df_pub.dropna(subset=['서브제목']).copy()
    df_pub_sub['서브제목_길이'] = df_pub_sub['서브제목'].astype(str).apply(len)
    df_pub_sub['출처'] = '2번 간행물정보'
    df_pub_sub['조회수_정제'] = df_pub_sub['서브조회수'].fillna(df_pub_sub['조회수'])
    
    combined_df = pd.concat([
        df_news_sub[['서브제목_길이', '조회수_정제', '출처']],
        df_pub_sub[['서브제목_길이', '조회수_정제', '출처']]
    ])
    
    m1, m2 = st.columns(2)
    m1.metric("1번 자료 서브제목 데이터 수", f"{len(df_news_sub)}개")
    m2.metric("2번 자료 서브제목 데이터 수", f"{len(df_pub_sub)}개")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=combined_df, x='서브제목_길이', y='조회수_정제', hue='출처', alpha=0.7, ax=ax)
    ax.set_title("자료별 서브제목 길이 vs 조회수", fontsize=14)
    ax.set_xlabel("서브제목 글자수", fontsize=12)
    ax.set_ylabel("조회수", fontsize=12)
    st.pyplot(fig)

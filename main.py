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

# 폰트 설정 (한글 깨짐 방지 - 시스템 기본 폰트 적용)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.title("📊 한국콘텐츠진흥원 데이터 분석 앱")
st.markdown("제목(또는 서브제목)의 길이에 따른 조회수 분포를 확인하고, 버튼으로 자료를 전환해 보세요.")

# 데이터 로드 함수 (캐싱 활용)
@st.cache_data
def load_data():
    # 파일 이름이 환경에 따라 다를 수 있으므로 예외처리 또는 정확한 명칭 사용
    try:
        df_news = pd.read_csv("한국콘텐츠진흥원_보도자료_20260806.csv", encoding="utf-8")
    except:
        df_news = pd.read_csv("한국콘텐츠진흥원_보도자료_20260806.csv", encoding="cp949")
        
    try:
        df_pub = pd.read_csv("한국콘텐츠진흥원_K콘텐츠 간행물정보_20170310.csv", encoding="utf-8")
    except:
        df_pub = pd.read_csv("한국콘텐츠진흥원_K콘텐츠 간행물정보_20170310.csv", encoding="cp949")
        
    return df_news, df_pub

df_news, df_pub = load_data()

# 세션 상태(Session State)를 이용해 뷰 모드 관리 (버튼 토글용)
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "news_main" # 기본값: 1번 자료 제목 길이

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
    st.write("한국콘텐츠진흥원 보도자료의 **메인 제목 글자수**와 **조회수**의 관계를 시각화합니다.")
    
    # 데이터 전처리
    df_news['제목_길이'] = df_news['제목'].astype(str).apply(len)
    
    # 지표 요약
    m1, m2, m3 = st.columns(3)
    m1.metric("총 데이터 수", f"{len(df_news):,}개")
    m2.metric("평균 제목 길이", f"{df_news['제목_길이'].mean():.1f}자")
    m3.metric("평균 조회수", f"{df_news['조회수'].mean():,.1f}회")
    
    # 시각화
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df_news, x='제목_길이', y='조회수', alpha=0.6, color='royalblue', ax=ax)
    sns.regplot(data=df_news, x='제목_길이', y='조회수', scatter=False, color='darkorange', ax=ax)
    ax.set_title("보도자료 제목 길이 vs 조회수", fontsize=14)
    ax.set_xlabel("제목 글자수", fontsize=12)
    ax.set_ylabel("조회수", fontsize=12)
    st.pyplot(fig)
    
    with st.expander("데이터 샘플 및 상세 보기"):
        st.dataframe(df_news[['제목', '제목_길이', '조회수', '최초등록일']].head(10))

# 2. 서브제목 길이 분석 (1번 보도자료 & 2번 간행물정보 서브제목 비교)
elif st.session_state.view_mode == "sub_title":
    st.subheader("🔄 [1,2번 자료] 서브제목 길이에 따른 조회수 분석")
    st.write("1번 자료(보도자료)와 2번 자료(간행물정보)의 **서브제목 글자수**와 **조회수** 경향을 비교합니다.")
    
    # 1번 자료 전처리 (서브제목 존재 시)
    df_news_sub = df_news.dropna(subset=['서브제목']).copy()
    df_news_sub['서브제목_길이'] = df_news_sub['서브제목'].astype(str).apply(len)
    df_news_sub['출처'] = '1번 보도자료'
    df_news_sub['조회수_정제'] = df_news_sub['조회수']
    
    # 2번 자료 전처리 (서브제목 존재 시)
    df_pub_sub = df_pub.dropna(subset=['서브제목']).copy()
    df_pub_sub['서브제목_길이'] = df_pub_sub['서브제목'].astype(str).apply(len)
    df_pub_sub['출처'] = '2번 간행물정보'
    # 2번 자료는 서브조회수 또는 조회수 사용 (여기서는 조회수 매칭)
    df_pub_sub['조회수_정제'] = df_pub_sub['서브조회수'].fillna(df_pub_sub['조회수'])
    
    # 통합
    combined_df = pd.concat([
        df_news_sub[['서브제목_길이', '조회수_정제', '출처']],
        df_pub_sub[['서브제목_길이', '조회수_정제', '출처']]
    ])
    
    m1, m2 = st.columns(2)
    m1.metric("1번 자료 서브제목 데이터 수", f"{len(df_news_sub)}개")
    m2.metric("2번 자료 서브제목 데이터 수", f"{len(df_pub_sub)}개")
    
    # 시각화
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=combined_df, x='서브제목_길이', y='조회수_정제', hue='출처', alpha=0.7, ax=ax)
    ax.set_title("자료별 서브제목 길이 vs 조회수", fontsize=14)
    ax.set_xlabel("서브제목 글자수", fontsize=12)
    ax.set_ylabel("조회수", fontsize=12)
    st.pyplot(fig)
    
    with st.expander("통합 서브제목 데이터 샘플 보기"):
        st.dataframe(combined_df.head(10))

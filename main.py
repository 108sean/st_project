import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 페이지 설정
st.set_page_config(
    page_title="K콘텐츠 간행물정보 분석",
    page_icon="📚",
    layout="wide"
)

# 한글 폰트 깨짐 방지 설정
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

st.title("📚 K콘텐츠 간행물정보 제목 길이별 조회수 분석")
st.markdown("간행물 데이터(2번 파일)를 바탕으로 메인 제목 및 서브제목 길이에 따른 조회수 관계를 분석합니다.")

# 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    pub_file = "한국콘텐츠진흥원_K콘텐츠 간행물정보_20170310.csv"
    
    # 간행물정보 파일 읽기
    try:
        df_pub = pd.read_csv(pub_file, encoding="utf-8")
    except:
        df_pub = pd.read_csv(pub_file, encoding="cp949")
        
    return df_pub

# 데이터 불러오기 실행
df_pub = load_data()

# 탭 구성 (메인 제목 분석 vs 서브제목 분석)
tab1, tab2 = st.tabs(["📖 메인 제목 길이 분석", "📑 서브제목 길이 분석"])

with tab1:
    st.subheader("간행물 메인 제목 길이에 따른 조회수")
    
    # 메인 제목 길이 계산
    df_pub['메인제목_길이'] = df_pub['제목'].astype(str).apply(len)
    
    # 주요 지표 요약
    col1, col2, col3 = st.columns(3)
    col1.metric("총 간행물 수", f"{len(df_pub):,}개")
    col2.metric("평균 메인 제목 길이", f"{df_pub['메인제목_길이'].mean():.1f}자")
    col3.metric("평균 조회수", f"{df_pub['조회수'].mean():,.1f}회")
    
    # 시각화 그래프
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df_pub, x='메인제목_길이', y='조회수', alpha=0.6, color='teal', ax=ax)
    sns.regplot(data=df_pub, x='메인제목_길이', y='조회수', scatter=False, color='coral', ax=ax)
    ax.set_title("간행물 메인 제목 길이 vs 조회수", fontsize=14)
    ax.set_xlabel("메인 제목 글자수", fontsize=12)
    ax.set_ylabel("조회수", fontsize=12)
    st.pyplot(fig)

with tab2:
    st.subheader("간행물 서브제목 길이에 따른 서브조회수(또는 조회수) 분석")
    
    # 서브제목이 존재하는 데이터만 추출
    df_pub_sub = df_pub.dropna(subset=['서브제목']).copy()
    df_pub_sub['서브제목_길이'] = df_pub_sub['서브제목'].astype(str).apply(len)
    # 서브조회수가 비어있으면 메인 조회수로 대체
    df_pub_sub['조회수_정제'] = df_pub_sub['서브조회수'].fillna(df_pub_sub['조회수'])
    
    # 주요 지표 요약
    col1, col2, col3 = st.columns(3)
    col1.metric("서브제목 있는 간행물 수", f"{len(df_pub_sub)}개")
    col2.metric("평균 서브제목 길이", f"{df_pub_sub['서브제목_길이'].mean():.1f}자" if len(df_pub_sub) > 0 else "0자")
    col3.metric("평균 서브 조회수", f"{df_pub_sub['조회수_정제'].mean():,.1f}회" if len(df_pub_sub) > 0 else "0회")
    
    if len(df_pub_sub) > 0:
        # 시각화 그래프
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.scatterplot(data=df_pub_sub, x='서브제목_길이', y='조회수_정제', alpha=0.7, color='purple', ax=ax)
        sns.regplot(data=df_pub_sub, x='서브제목_길이', y='조회수_정제', scatter=False, color='darkorange', ax=ax)
        ax.set_title("간행물 서브제목 길이 vs 조회수", fontsize=14)
        ax.set_xlabel("서브제목 글자수", fontsize=12)
        ax.set_ylabel("조회수", fontsize=12)
        st.pyplot(fig)
    else:
        st.info("분석할 서브제목 데이터가 존재하지 않습니다.")

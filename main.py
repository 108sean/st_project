import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob

# 페이지 설정
st.set_page_config(
    page_title="K콘텐츠 간행물정보 분석",
    page_icon="📚",
    layout="wide"
)

st.title("📚 K콘텐츠 간행물정보 제목 길이별 조회수 분석")
st.markdown("간행물 데이터를 바탕으로 메인 제목 및 서브제목 길이에 따른 조회수 관계를 분석합니다.")

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
tab1, tab2 = st.tabs(["Main Title Analysis", "Sub Title Analysis"])

with tab1:
    st.subheader("간행물 메인 제목 길이에 따른 조회수")
    
    df_pub['메인제목_길이'] = df_pub['제목'].astype(str).apply(len)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("총 간행물 수", f"{len(df_pub):,}개")
    col2.metric("평균 메인 제목 길이", f"{df_pub['메인제목_길이'].mean():.1f}자")
    col3.metric("평균 조회수", f"{df_pub['조회수'].mean():,.1f}회")
    
    # 그래프 영문 레이블 적용 (폰트 깨짐 방지)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df_pub, x='메인제목_길이', y='조회수', alpha=0.6, color='teal', ax=ax)
    sns.regplot(data=df_pub, x='메인제목_길이', y='조회수', scatter=False, color='coral', ax=ax)
    ax.set_title("Main Title Length vs Views", fontsize=14)
    ax.set_xlabel("Title Length (Characters)", fontsize=12)
    ax.set_ylabel("Views", fontsize=12)
    st.pyplot(fig)

with tab2:
    st.subheader("간행물 서브제목 길이에 따른 서브조회수(또는 조회수) 분석")
    
    df_pub_sub = df_pub.dropna(subset=['서브제목']).copy()
    df_pub_sub['서브제목_길이'] = df_pub_sub['서브제목'].astype(str).apply(len)
    df_pub_sub['조회수_정제'] = df_pub_sub['서브조회수'].fillna(df_pub_sub['조회수'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("서브제목 있는 간행물 수", f"{len(df_pub_sub)}개")
    col2.metric("평균 서브제목 길이", f"{df_pub_sub['서브제목_길이'].mean():.1f}자" if len(df_pub_sub) > 0 else "0자")
    col3.metric("평균 서브 조회수", f"{df_pub_sub['조회수_정제'].mean():,.1f}회" if len(df_pub_sub) > 0 else "0회")
    
    if len(df_pub_sub) > 0:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.scatterplot(data=df_pub_sub, x='서브제목_길이', y='조회수_정제', alpha=0.7, color='purple', ax=ax)
        sns.regplot(data=df_pub_sub, x='서브제목_길이', y='조회수_정제', scatter=False, color='darkorange', ax=ax)
        ax.set_title("Sub Title Length vs Views", fontsize=14)
        ax.set_xlabel("Sub Title Length (Characters)", fontsize=12)
        ax.set_ylabel("Views", fontsize=12)
        st.pyplot(fig)
    else:
        st.info("분석할 서브제목 데이터가 존재하지 않습니다.")

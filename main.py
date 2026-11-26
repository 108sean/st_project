import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import platform

# 페이지 설정
st.set_page_config(
    page_title="K콘텐츠 간행물정보 분석",
    page_icon="📚",
    layout="wide"
)

# 운영체제별 한글 폰트 설정 (그래프 한글 깨짐 방지)
if platform.system() == 'Darwin': # Mac
    plt.rc('font', family='AppleGothic')
elif platform.system() == 'Windows': # Windows
    plt.rc('font', family='Malgun Gothic')
else: # Linux (Streamlit Cloud 환경 포함)
    # 리눅스 환경 기본 한글 폰트 지정 또는 산세리프 적용
    plt.rc('font', family='NanumGothic')

plt.rcParams['axes.unicode_minus'] = False

st.title("📚 K콘텐츠 간행물정보 제목 길이별 조회수 분석")
st.markdown("간행물 데이터를 바탕으로 제목(글자수)과 조회수의 관계를 분석합니다.")

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
    st.success(f"📂 성공적으로 불러온 데이터 파일: `{loaded_file_name}`")
except Exception as e:
    st.error(f"❌ 파일을 불러오는 중 오류가 발생했습니다. (오류내용: {e})")
    st.stop()

# 탭 구성 (메인 제목 분석 vs 서브제목 분석)
tab1, tab2 = tab1, tab2 = st.tabs(["📖 메인 제목 길이 분석", "📑 서브제목 길이 분석"])

with tab1:
    st.subheader("메인 제목 길이에 따른 조회수")
    
    # 메인 제목 길이 계산
    df_pub['메인제목_길이'] = df_pub['제목'].astype(str).apply(len)
    
    # 주요 지표 요약
    col1, col2, col3 = st.columns(3)
    col1.metric("총 간행물 수", f"{len(df_pub):,}개")
    col2.metric("평균 메인 제목 길이", f"{df_pub['메인제목_길이'].mean():.1f}자")
    col3.metric("평균 조회수", f"{df_pub['조회수'].mean():,.1f}회")
    
    # 시각화 그래프 (가로: 제목 길이, 세로: 조회수)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(data=df_pub, x='메인제목_길이', y='조회수', alpha=0.6, color='teal', ax=ax)
    sns.regplot(data=df_pub, x='메인제목_길이', y='조회수', scatter=False, color='coral', ax=ax)
    ax.set_title("메인 제목 길이별 조회수 분포", fontsize=14)
    ax.set_xlabel("제목 길이 (글자수)", fontsize=12)
    ax.set_ylabel("조회수", fontsize=12)
    st.pyplot(fig)

with tab2:
    st.subheader("서브제목 길이에 따른 조회수")
    
    # 서브제목이 존재하는 데이터만 추출
    df_pub_sub = df_pub.dropna(subset=['서브제목']).copy()
    df_pub_sub['서브제목_길이'] = df_pub_sub['서브제목'].astype(str).apply(len)
    # 서브조회수가 비어있으면 메인 조회수로 대체
    df_pub_sub['조회수_정제'] = df_pub_sub['서브조회수'].fillna(df_pub_sub['조회수'])
    
    # 주요 지표 요약
    col1, col2, col3 = st.columns(3)
    col1.metric("서브제목 있는 간행물 수", f"{len(df_pub_sub)}개")
    col2.metric("평균 서브제목 길이", f"{df_pub_sub['서브제목_길이'].mean():.1f}자" if len(df_pub_sub) > 0 else "0자")
    col3.metric("평균 조회수", f"{df_pub_sub['조회수_정제'].mean():,.1f}회" if len(df_pub_sub) > 0 else "0회")
    
    if len(df_pub_sub) > 0:
        # 시각화 그래프 (가로: 서브제목 길이, 세로: 조회수)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.scatterplot(data=df_pub_sub, x='서브제목_길이', y='조회수_정제', alpha=0.7, color='purple', ax=ax)
        sns.regplot(data=df_pub_sub, x='서브제목_길이', y='조회수_정제', scatter=False, color='darkorange', ax=ax)
        ax.set_title("서브제목 길이별 조회수 분포", fontsize=14)
        ax.set_xlabel("서브제목 길이 (글자수)", fontsize=12)
        ax.set_ylabel("조회수", fontsize=12)
        st.pyplot(fig)
    else:
        st.info("분석할 서브제목 데이터가 존재하지 않습니다.")

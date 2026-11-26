import streamlit as st
import pandas as pd
import plotly.express as px
import glob

# 페이지 설정
st.set_page_config(
    page_title="K콘텐츠 서브제목 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

st.title("📚 K콘텐츠 서브제목 길이 및 키워드별 조회수 분석")
st.markdown("서브제목의 글자수와 조회수의 관계, 그리고 특정 키워드별 조회수를 인터랙티브 그래프로 확인합니다.")

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

# 서브제목 데이터 정제
df_pub_sub = df_pub.dropna(subset=['서브제목']).copy()
df_pub_sub['서브제목_길이'] = df_pub_sub['서브제목'].astype(str).apply(len)
df_pub_sub['조회수_정제'] = df_pub_sub['서브조회수'].fillna(df_pub_sub['조회수'])

# 주요 지표 요약
col1, col2, col3 = st.columns(3)
col1.metric("서브제목 있는 간행물 수", f"{len(df_pub_sub):,}개")
col2.metric("평균 서브제목 길이", f"{df_pub_sub['서브제목_길이'].mean():.1f}자")
col3.metric("평균 조회수", f"{df_pub_sub['조회수_정제'].mean():,.1f}회")

st.divider()

# 1. 서브제목 길이별 조회수 산점도 (아까 보셨던 형태, 마우스 오버 + 툴팁 포함)
st.subheader("📖 서브제목 길이에 따른 조회수 분포")
st.markdown("마우스를 점 위에 올리면 **서브제목, 등록일, 조회수**가 팝업으로 나타납니다.")

fig1 = px.scatter(
    df_pub_sub,
    x='서브제목_길이',
    y='조회수_정제',
    hover_data=['서브제목', '서브등록일', '조회수_정제'],
    labels={'서브제목_길이': '서브제목 길이 (글자수)', '조회수_정제': '조회수'},
    title="서브제목 길이별 조회수 분포"
)
fig1.update_traces(marker=dict(size=8, color='purple'))
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# 2. 키워드별 조회수 비교 분석
st.subheader("🔍 서브제목 키워드별 조회수 비교 분석")
st.markdown("서브제목에 포함된 특정 단어(예: 웹툰, 방송, 게임, 통계, 정책 등)를 기준으로 조회수를 비교합니다.")

default_keywords = ["웹툰", "방송", "게임", "통계", "정책", "글로벌", "시장", "조사"]
selected_keyword = st.selectbox("분석할 키워드를 선택하거나 직접 입력하세요", options=default_keywords)

if selected_keyword:
    df_pub_sub['키워드_포함'] = df_pub_sub['서브제목'].astype(str).str.contains(selected_keyword)
    df_pub_sub['그룹'] = df_pub_sub['키워드_포함'].apply(lambda x: f"'{selected_keyword}' 포함" if x else "기타 (미포함)")
    
    group_avg = df_pub_sub.groupby('그룹')['조회수_정제'].mean().reset_index()
    matched_count = df_pub_sub['키워드_포함'].sum()
    
    st.info(f"📌 **'{selected_keyword}'** 키워드가 포함된 서브제목은 총 **{matched_count}개**입니다.")
    
    # 키워드 포함 vs 미포함 평균 조회수 막대 그래프
    fig_bar = px.bar(
        group_avg,
        x='그룹',
        y='조회수_정제',
        text_auto=',.1f',
        color='그룹',
        labels={'조회수_정제': '평균 조회수', '그룹': '분류'},
        title=f"'{selected_keyword}' 키워드 유무에 따른 평균 조회수 비교"
    )
    fig_bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_bar, use_container_width=True)

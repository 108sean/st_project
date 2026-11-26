import streamlit as st
import pandas as pd
import plotly.express as px
import glob

# 페이지 설정
st.set_page_config(
    page_title="K콘텐츠 간행물 키워드별 조회수 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📚 K콘텐츠 서브제목 키워드별 조회수 분석")
st.markdown("서브제목에 자주 등장하는 주요 키워드별 평균 조회수와 분포를 분석합니다.")

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
df_pub_sub['서브조회수_정제'] = df_pub_sub['서브조회수'].fillna(df_pub_sub['조회수'])

# 주요 지표 요약
col1, col2 = st.columns(2)
col1.metric("서브제목이 있는 총 간행물 수", f"{len(df_pub_sub):,}개")
col2.metric("전체 평균 조회수", f"{df_pub_sub['서브조회수_정제'].mean():,.1f}회")

st.divider()

# 사용자가 직접 분석하고 싶은 키워드를 입력하거나 선택할 수 있는 기능 추가
st.subheader("🔍 키워드별 조회수 비교 분석")
st.markdown("서브제목에 포함된 특정 단어(예: 웹툰, 방송, 게임, 통계, 정책 등)를 기준으로 조회수를 비교합니다.")

# 기본 추천 키워드 리스트 예시 (데이터 특성에 맞게 조정 가능)
default_keywords = ["웹툰", "방송", "게임", "통계", "정책", "글로벌", "시장", "조사"]

# 사용자 입력 또는 선택
selected_keyword = st.selectbox("분석할 키워드를 선택하거나 직접 입력하세요", options=default_keywords)

if selected_keyword:
    # 키워드 포함 여부 컬럼 생성
    df_pub_sub['키워드_포함'] = df_pub_sub['서브제목'].astype(str).str.contains(selected_keyword)
    
    # 키워드 포함 / 미포함 그룹으로 나누기
    df_pub_sub['그룹'] = df_pub_sub['키워드_포함'].apply(lambda x: f"'{selected_keyword}' 포함" if x else "기타 (미포함)")
    
    # 그룹별 평균 조회수 계산
    group_avg = df_pub_sub.groupby('그룹')['서브조회수_정제'].mean().reset_index()
    
    # 지표 표시
    matched_count = df_pub_sub['키워드_포함'].sum()
    st.info(f"📌 **'{selected_keyword}'** 키워드가 포함된 서브제목은 총 **{matched_count}개**입니다.")
    
    # Plotly 바 차트 (키워드 포함 vs 미포함 평균 조회수 비교)
    fig_bar = px.bar(
        group_avg,
        x='그룹',
        y='서브조회수_정제',
        text_auto=',.1f',
        color='그룹',
        labels={'서브조회수_정제': '평균 조회수', '그룹': '분류'},
        title=f"'{selected_keyword}' 키워드 유무에 따른 평균 조회수 비교"
    )
    fig_bar.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # 상세 데이터 산점도 (마우스 오버 시 제목, 날짜, 조회수 표시)
    st.subheader(f"📊 '{selected_keyword}' 포함 간행물 상세 분포")
    fig_scatter = px.scatter(
        df_pub_sub,
        x='서브제목',
        y='서브조회수_정제',
        color='키워드_포함',
        hover_data=['서브제목', '서브등록일', '서브조회수_정제'],
        labels={'서브제목': '서브제목', '서브조회수_정제': '조회수', '키워드_포함': '키워드 포함 여부'},
        title=f"서브제목별 조회수 분포 (키워드: {selected_keyword})"
    )
    fig_scatter.update_traces(marker=dict(size=8))
    st.plotly_chart(fig_scatter, use_container_width=True)

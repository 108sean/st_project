import streamlit as st
import pandas as pd
import plotly.express as px
import glob
from collections import Counter
import re

# 페이지 설정
st.set_page_config(
    page_title="K콘텐츠 서브 카테고리 및 키워드별 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📚 K콘텐츠 서브 카테고리 및 키워드별 조회수 분석")
st.markdown("서브제목 길이별 조회수(회귀선 포함)와, 서브 카테고리별 조회수를 높이는 핵심 키워드를 분석합니다.")

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

# 1. 서브제목 길이별 조회수 산점도 + 회귀선(추세선) 추가
st.subheader("📖 서브제목 길이에 따른 조회수 분포 및 회귀선")
st.markdown("마우스를 점 위에 올리면 **서브제목, 등록일, 조회수**가 팝업으로 나타나며, 전체적인 조회수 추세선(OLS)을 확인할 수 있습니다.")

fig1 = px.scatter(
    df_pub_sub,
    x='서브제목_길이',
    y='조회수_정제',
    hover_data=['서브제목', '서브등록일', '조회수_정제'],
    labels={'서브제목_길이': '서브제목 길이 (글자수)', '조회수_정제': '조회수'},
    title="서브제목 길이별 조회수 분포 및 회귀선",
    trendline="ols"  # 회귀선 추가
)
fig1.update_traces(marker=dict(size=8, color='purple'))
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# 2. 서브 카테고리별 키워드 조회수 분석
st.subheader("🔍 서브 카테고리별 키워드 조회수 분석")
st.markdown("특정 서브 카테고리를 선택한 뒤, 해당 카테고리 내에서 어떤 단어(키워드)가 포함될 때 조회수가 높은지 분석합니다.")

# 데이터 내에 '서브카테고리' 또는 유사한 컬럼명이 있는지 확인 (없을 경우 안내)
category_col = None
for col in df_pub_sub.columns:
    if '카테고리' in col or '분류' in col or '유형' in col:
        category_col = col
        break

if category_col:
    categories = df_pub_sub[category_col].dropna().unique()
    selected_category = st.selectbox("분석할 서브 카테고리를 선택하세요", options=categories)
    
    # 선택한 카테고리 데이터 필터링
    df_cat = df_pub_sub[df_pub_sub[category_col] == selected_category].copy()
    st.info(f"📌 **'{selected_category}'** 카테고리에 속하는 간행물은 총 **{len(df_cat)}개**입니다.")
    
    if len(df_cat) > 0:
        # 간단한 형태소/단어 추출 및 키워드별 평균 조회수 계산 로직
        keyword_stats = []
        
        # 2글자 이상의 한글 단어 추출용 정규식
        words_list = []
        for idx, row in df_cat.iterrows():
            title_text = str(row['서브제목'])
            # 한글 2글자 이상 단어 추출
            words = re.findall(r'[가-힣]{2,}', title_text)
            # 중복 제거 (한 제목 안에서 같은 단어는 1번만)
            unique_words = set(words)
            for w in unique_words:
                words_list.append({'keyword': w, 'views': row['조회수_정제']})
        
        if words_list:
            df_words = pd.DataFrame(words_list)
            # 단어별 빈도수 및 평균 조회수 계산
            word_grouped = df_words.groupby('keyword').agg(
                avg_views=('views', 'mean'),
                count=('views', 'count')
            ).reset_index()
            
            # 최소 2개 이상 등장한 키워드만 필터링하여 신뢰도 확보
            word_grouped = word_grouped[word_grouped['count'] >= 1]
            # 평균 조회수 높은 순으로 상위 10개 추출
            top_keywords = word_grouped.sort_values(by='avg_views', ascending=False).head(10)
            
            if not top_keywords.empty:
                st.markdown(f"📊 **'{selected_category}'** 카테고리 내 조회수를 높여주는 주요 키워드 TOP 10")
                
                # 막대 그래프 생성
                fig_bar = px.bar(
                    top_keywords,
                    x='keyword',
                    y='avg_views',
                    text_auto=',.1f',
                    labels={'keyword': '키워드', 'avg_views': '평균 조회수'},
                    title=f"'{selected_category}' 카테고리 키워드별 평균 조회수"
                )
                fig_bar.update_traces(marker_color='teal', textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("분석할 수 있는 충분한 키워드 데이터가 없습니다.")
        else:
            st.warning("해당 카테고리의 서브제목에서 추출할 수 있는 단어가 부족합니다.")
else:
    st.error("❌ 데이터 파일 안에 '카테고리' 또는 '분류'와 관련된 열(Column)이 존재하지 않습니다. CSV 파일의 열 이름을 확인해 주세요.")

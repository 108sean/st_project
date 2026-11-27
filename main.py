import streamlit as st
import pandas as pd
import plotly.express as px
import statsmodels.api as sm
import glob

# 페이지 설정
st.set_page_config(
    page_title="K콘텐츠 서브 카테고리 회귀 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

st.title("📚 K콘텐츠 서브제목 회귀 분석 대시보드")
st.markdown("서브제목 길이별 회귀 분석과, 서브 카테고리별 키워드가 조회수에 미치는 영향(회귀 계수)을 분석합니다.")

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
st.markdown("마우스를 점 위에 올리면 **서브제목, 등록일, 조회수**가 팝업으로 나타나며, 전체적인 조회수 회귀선(OLS)을 확인할 수 있습니다.")

fig1 = px.scatter(
    df_pub_sub,
    x='서브제목_길이',
    y='조회수_정제',
    hover_data=['서브제목', '서브등록일', '조회수_정제'],
    labels={'서브제목_길이': '서브제목 길이 (글자수)', '조회수_정제': '조회수'},
    title="서브제목 길이별 조회수 OLS 회귀선",
    trendline="ols"  # 회귀선 추가
)
fig1.update_traces(marker=dict(size=8, color='purple'))
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# 2. 서브 카테고리별 키워드 다중 회귀 분석 (조회수 영향력 계수 시각화)
st.subheader("🔍 서브 카테고리별 키워드 회귀 분석 (조회수 영향력)")
st.markdown("선택한 카테고리 내에서 **'콘텐츠'**, **'주도'**, **'동향'** 등 주요 키워드가 조회수에 미치는 순수 영향력(회귀 계수)을 막대 그래프로 분석합니다.")

# 데이터 내 '서브카테고리' 또는 유사한 컬럼 탐색
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
    
    if len(df_cat) > 5:
        # 주요 키워드 목록
        target_keywords = ["콘텐츠", "주도", "동향", "시장", "글로벌", "산업", "정책", "통계"]
        
        # 회귀 분석을 위한 더미 변수(0 또는 1) 생성 테이블 구축
        regression_data = pd.DataFrame({'조회수': df_cat['조회수_정제']})
        active_keywords = []
        
        for kw in target_keywords:
            col_name = f"KW_{kw}"
            regression_data[col_name] = df_cat['서브제목'].astype(str).str.contains(kw).astype(int)
            if regression_data[col_name].sum() > 0:
                active_keywords.append(col_name)
        
        if active_keywords:
            # OLS 다중 회귀 모델 실행
            X = regression_data[active_keywords]
            X = sm.add_constant(X)  # 상수항(절편) 추가
            y = regression_data['조회수']
            
            try:
                model = sm.OLS(y, X).fit()
                coeffs = model.params.drop('const', errors='ignore').reset_index()
                coeffs.columns = ['키워드_변수', '회귀계수']
                coeffs['키워드'] = coeffs['키워드_변수'].str.replace('KW_', '')
                
                # 회귀 계수 막대 그래프 생성
                fig_reg = px.bar(
                    coeffs,
                    x='키워드',
                    y='회귀계수',
                    text_auto='.1f',
                    color='회귀계수',
                    color_continuous_scale='Teal',
                    labels={'회귀계수': '조회수 영향력 (회귀 계수)', '키워드': '키워드'},
                    title=f"'{selected_category}' 카테고리 키워드별 조회수 회귀 계수"
                )
                fig_reg.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                st.plotly_chart(fig_reg, use_container_width=True)
                
                # 통계 요약 테이블 제공
                with st.expander("📋 회귀 분석 상세 통계 보기"):
                    st.text(str(model.summary()))
                    
            except Exception as ex:
                st.warning(f"회귀 분석 중 오류가 발생했습니다: {ex}")
        else:
            st.warning("선택한 카테고리 내에 분석할 키워드가 포함된 서브제목이 없습니다.")
    else:
        st.warning("회귀 분석을 수행하기에 데이터 개수가 너무 부족합니다 (최소 6개 이상 필요).")
else:
    st.error("❌ 데이터 파일 안에 '카테고리' 또는 '분류'와 관련된 열(Column)이 존재하지 않습니다.")

import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection

SHEET_URL = "https://docs.google.com/spreadsheets/d/1nBaJtEC_80aBiw8O5D59x0DZjK_Ik46n3sr2KswZ51Y/edit?usp=sharing"

# 페이지 설정
st.set_page_config(page_title="UFC 백악관 매치 승부 예측 옥타곤", page_icon="🥊", layout="centered")

# 1. 상단 대문 및 레이아웃
# 로고와 'UFC 백악관 매치 승부예측' 텍스트를 나란히 배치
col_logo, col_text = st.columns([1, 8])
with col_logo:
    if os.path.exists('./ufc_logo.png'):
        st.image('./ufc_logo.png', width=70)
with col_text:
    st.markdown("<h2 style='margin-top: 10px; margin-left: -20px;'>UFC 백악관 매치 승부예측</h2>", unsafe_allow_html=True)

# 메인 타이틀 및 구분선
st.title('UFC 백악관 매치 승부 예측 옥타곤')

# 유튜브 영상 자동재생 (최신 브라우저 정책상 mute=1이 있어야 자동재생됨)
video_html = """
<div style="display: flex; justify-content: center; margin-bottom: 20px;">
    <iframe width="100%" height="400" src="https://www.youtube.com/embed/qK7HtIlUNEk?si=uCPaXvxdK_hh6gUX&autoplay=1&mute=1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>
"""
st.markdown(video_html, unsafe_allow_html=True)

st.divider()

# 구글 시트 연결 설정
conn = st.connection("gsheets", type=GSheetsConnection)

# 매치업 및 이미지 데이터 리스트
matchups = [
    {"id": "Match 1", "f1": "일리아 토푸리아", "f2": "저스틴 게이치", "img": "./1r.png"},
    {"id": "Match 2", "f1": "알렉스 페레이라", "f2": "시릴 간", "img": "./2r.png"},
    {"id": "Match 3", "f1": "션 오말리", "f2": "에이만 자하비", "img": "./3r.png"},
    {"id": "Match 4", "f1": "조쉬 호킷", "f2": "데릭 루이스", "img": "./4r.png"},
    {"id": "Match 5", "f1": "마우리시오 루피", "f2": "마이클 챈들러", "img": "./5r.png"}
]

# 2. 예측 투표 폼 (Form) 섹션
with st.form(key='prediction_form'):
    selections = {}
    
    # 파이썬 반복문을 활용한 5경기 렌더링
    for match in matchups:
        st.subheader(f"{match['id']}: {match['f1']} VS {match['f2']}")
        
        # 경기 사진 화면 너비에 꽉 차게 배치
        if os.path.exists(match['img']):
            st.image(match['img'], use_container_width=True)
        else:
            st.info(f"이미지 파일을 찾을 수 없습니다: {match['img']}")
            
        # 사진 바로 아래 라디오 버튼 배치 (horizontal=True)
        selections[match['id']] = st.radio(
            f"{match['id']} 승자 선택",
            options=[match['f1'], match['f2']],
            horizontal=True,
            label_visibility="collapsed" # 라디오 버튼의 기본 라벨 숨김 (깔끔한 UI)
        )
        st.write("") # 각 매치 사이 여백 추가
        
    # 폼 맨 아래 큼직한 제출 버튼
    submit_btn = st.form_submit_button('예측 저장하기', use_container_width=True)

# 3. 데이터 집계 및 시각화 섹션 (하단)
if submit_btn:
    # 1. 구글 시트 기존 데이터 읽어오기
    try:
        existing_data = conn.read(spreadsheet=SHEET_URL, usecols=[0, 1, 2, 3, 4], ttl=0)
        existing_data = existing_data.dropna(how="all")
    except Exception:
        existing_data = pd.DataFrame(columns=["Match 1", "Match 2", "Match 3", "Match 4", "Match 5"])
        
    # 시트가 비어있을 때를 대비한 컬럼 설정
    if existing_data.empty or len(existing_data.columns) < 5:
        existing_data = pd.DataFrame(columns=["Match 1", "Match 2", "Match 3", "Match 4", "Match 5"])

    # 2. 새로운 투표 데이터 생성
    new_row = pd.DataFrame([{
        "Match 1": selections["Match 1"],
        "Match 2": selections["Match 2"],
        "Match 3": selections["Match 3"],
        "Match 4": selections["Match 4"],
        "Match 5": selections["Match 5"],
    }])
    
    # 3. 기존 데이터에 누적(Append)
    updated_data = pd.concat([existing_data, new_row], ignore_index=True)
    
    # 4. 구글 시트에 업데이트
    conn.update(spreadsheet=SHEET_URL, data=updated_data)
    st.success("성공적으로 예측이 구글 시트에 누적 저장되었습니다!")

st.divider()
st.header('🔥 실시간 팬 승리 예측 비율')

# 전체 누적 데이터 실시간 읽어오기
try:
    all_votes_df = conn.read(spreadsheet=SHEET_URL, usecols=[0, 1, 2, 3, 4], ttl=0)
    all_votes_df = all_votes_df.dropna(how="all")
except Exception:
    all_votes_df = pd.DataFrame()

# 5경기에 대한 데이터프레임 생성 및 바 차트 시각화
for match in matchups:
    m_id = match['id']
    f1 = match['f1']
    f2 = match['f2']
    
    # 데이터프레임에서 각 선수의 득표수 집계
    if not all_votes_df.empty and m_id in all_votes_df.columns:
        counts = all_votes_df[m_id].value_counts()
        v1 = counts.get(f1, 0)
        v2 = counts.get(f2, 0)
    else:
        v1 = 0
        v2 = 0
        
    total = v1 + v2
    
    # 득표 비율(%) 계산
    if total > 0:
        p1 = (v1 / total) * 100
        p2 = (v2 / total) * 100
    else:
        p1 = 0.0
        p2 = 0.0
        
    # Pandas 데이터프레임 생성
    df = pd.DataFrame({
        "선수": [f1, f2],
        "득표 비율(%)": [p1, p2]
    }).set_index("선수")
    
    # 각 경기 이름과 함께 바 차트 나열
    st.markdown(f"**{m_id}: {f1} vs {f2}**")
    st.bar_chart(df)

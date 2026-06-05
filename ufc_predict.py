import streamlit as st
import pandas as pd
import os

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
st.divider()

# 세션 상태(session_state) 초기화: 투표 데이터 누적 관리
if 'votes' not in st.session_state:
    st.session_state.votes = {
        'Match 1': {'일리아 토푸리아': 0, '저스틴 게이치': 0},
        'Match 2': {'알렉스 페레이라': 0, '시릴 간': 0},
        'Match 3': {'션 오말리': 0, '에이만 자하비': 0},
        'Match 4': {'조쉬 호킷': 0, '데릭 루이스': 0},
        'Match 5': {'마우리시오 루피': 0, '마이클 챈들러': 0}
    }

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
    # 폼이 제출되면 선택된 선수의 누적 득표수 업데이트
    for match in matchups:
        selected = selections[match['id']]
        st.session_state.votes[match['id']][selected] += 1
    st.success("성공적으로 예측이 저장되었습니다!")

st.divider()
st.header('🔥 실시간 팬 승리 예측 비율')

# 5경기에 대한 데이터프레임 생성 및 바 차트 시각화
for match in matchups:
    v1 = st.session_state.votes[match['id']][match['f1']]
    v2 = st.session_state.votes[match['id']][match['f2']]
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
        "선수": [match['f1'], match['f2']],
        "득표 비율(%)": [p1, p2]
    }).set_index("선수")
    
    # 각 경기 이름과 함께 바 차트 나열
    st.markdown(f"**{match['id']}: {match['f1']} vs {match['f2']}**")
    st.bar_chart(df)

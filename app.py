import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ---------------------------------------------------
# 기본 설정 및 스타일
# ---------------------------------------------------
st.set_page_config(
    page_title="당신의 창업, 얼마나 성공할 수 있을까요?",
    page_icon=None,
    layout="centered"
)

CUSTOM_CSS = """
<style>
    .stApp {
        background-color: #FAF8F3;
    }
    h1, h2, h3 {
        color: #1B4332;
    }
    .stButton > button {
        background-color: #1B4332;
        color: #FAF8F3;
        border: none;
        border-radius: 6px;
        padding: 0.6em 1.5em;
    }
    .stButton > button:hover {
        background-color: #2D6A4F;
        color: #FAF8F3;
    }
    .result-box {
        background-color: #FFFFFF;
        border: 1px solid #D8D2C4;
        border-radius: 10px;
        padding: 1.6em;
        margin-top: 1em;
    }
    .score-warning {
        background-color: #FBEAEA;
        border-left: 4px solid #B3261E;
        padding: 0.8em 1.2em;
        border-radius: 4px;
    }
    .score-ok {
        background-color: #EAF2ED;
        border-left: 4px solid #1B4332;
        padding: 0.8em 1.2em;
        border-radius: 4px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------
# 모델 로드
# ---------------------------------------------------
@st.cache_resource
def load_model():
    return joblib.load("survey_model.pkl")

model = load_model()

MODEL_COLUMNS = [
    'avg_delivery_days_log', 'avg_price_log', 'unique_categories',
    'state_MG', 'state_PR', 'state_RJ', 'state_RS', 'state_SC', 'state_SP', 'state_기타'
]

SCORE_CAP = 11

# ---------------------------------------------------
# 입력 옵션 정의 (구간 선택 + 점수 + 모델 입력용 대표값)
# ---------------------------------------------------
DELIVERY_OPTIONS = {
    "1~7일": {"score": 5, "days": 4},
    "8~11일": {"score": 4, "days": 9.5},
    "12~14일": {"score": 2, "days": 13},
    "15~20일": {"score": 1, "days": 17.5},
    "21일 이상": {"score": 0, "days": 25},
}

PRICE_OPTIONS = {
    "~50R$": {"score": 1, "price": 35},
    "50~100R$": {"score": 3, "price": 75},
    "100~150R$": {"score": 5, "price": 125},
    "150~300R$": {"score": 3, "price": 220},
    "300R$~": {"score": 2, "price": 400},
}

CATEGORY_OPTIONS = {
    "1개": {"score": 1, "n": 1},
    "2개": {"score": 2, "n": 2},
    "3개": {"score": 4, "n": 3},
    "4개 이상": {"score": 5, "n": 4},
}

STATE_OPTIONS = {
    "RS": 5,
    "PR": 4,
    "SC": 4,
    "기타": 4,
    "DF": 4,
    "MG": 3,
    "RJ": 1,
    "SP": 1,
}

# ---------------------------------------------------
# 등급 구간
# ---------------------------------------------------
def get_grade(proba):
    if proba >= 0.75:
        return "S"
    elif proba >= 0.60:
        return "A"
    elif proba >= 0.45:
        return "B"
    elif proba >= 0.30:
        return "C"
    else:
        return "D"

# ---------------------------------------------------
# 세그먼트 네이밍 로직
# ---------------------------------------------------
def get_segment_name(scores):
    # scores: {"배송": int, "가격": int, "카테고리": int, "지역": int}
    max_score = max(scores.values())
    dominant = [k for k, v in scores.items() if v == max_score]

    if max_score <= 2:
        return "신중한 도전형 창업가"

    if len(dominant) >= 3:
        return "밸런스형 창업가"

    if max_score == 5 and len(dominant) == 1:
        name_map = {
            "배송": "초고속 배송형 창업가",
            "가격": "가성비 스위트스팟형 창업가",
            "카테고리": "멀티카테고리형 창업가",
            "지역": "지역 강점 활용형 창업가",
        }
        return name_map[dominant[0]]

    if len(dominant) == 2:
        return "이중 전략형 창업가"

    name_map = {
        "배송": "배송 안정형 창업가",
        "가격": "가격 균형형 창업가",
        "카테고리": "카테고리 확장형 창업가",
        "지역": "입지 활용형 창업가",
    }
    return name_map[dominant[0]]

# ---------------------------------------------------
# 화면 구성
# ---------------------------------------------------
st.title("당신의 창업, 얼마나 성공할 수 있을까요?")
st.write(
    "네 가지 조건을 선택하면, 실제 판매 데이터를 학습한 모델이 "
    "예상 성공 확률을 알려드립니다. 단, 참고용 예측이며 확정적인 진단이 아닙니다."
)

st.markdown("### 조건을 선택해 주세요")

col1, col2 = st.columns(2)
with col1:
    delivery_choice = st.selectbox("평균 배송 소요일", list(DELIVERY_OPTIONS.keys()))
    category_choice = st.selectbox("취급 카테고리 수", list(CATEGORY_OPTIONS.keys()))
with col2:
    price_choice = st.selectbox("평균 판매 가격대", list(PRICE_OPTIONS.keys()))
    state_choice = st.selectbox("판매 지역", list(STATE_OPTIONS.keys()))

scores = {
    "배송": DELIVERY_OPTIONS[delivery_choice]["score"],
    "가격": PRICE_OPTIONS[price_choice]["score"],
    "카테고리": CATEGORY_OPTIONS[category_choice]["score"],
    "지역": STATE_OPTIONS[state_choice],
}
total_score = sum(scores.values())

st.markdown("### 현재 선택 점수")
score_cols = st.columns(4)
score_cols[0].metric("배송", scores["배송"])
score_cols[1].metric("가격", scores["가격"])
score_cols[2].metric("카테고리", scores["카테고리"])
score_cols[3].metric("지역", scores["지역"])

if total_score > SCORE_CAP:
    st.markdown(
        f'<div class="score-warning">현재 총점 {total_score}점으로, '
        f'제한 점수({SCORE_CAP}점)를 {total_score - SCORE_CAP}점 초과했습니다. '
        f'조건을 조정해 주세요.</div>',
        unsafe_allow_html=True
    )
    can_submit = False
else:
    st.markdown(
        f'<div class="score-ok">현재 총점 {total_score}점 / 제한 {SCORE_CAP}점 (통과)</div>',
        unsafe_allow_html=True
    )
    can_submit = True

st.write("")
submit = st.button("결과 확인하기", disabled=not can_submit)

# ---------------------------------------------------
# 결과 출력
# ---------------------------------------------------
if submit:
    row = {c: 0 for c in MODEL_COLUMNS}
    row["avg_delivery_days_log"] = np.log1p(DELIVERY_OPTIONS[delivery_choice]["days"])
    row["avg_price_log"] = np.log1p(PRICE_OPTIONS[price_choice]["price"])
    row["unique_categories"] = CATEGORY_OPTIONS[category_choice]["n"]

    if state_choice != "DF":
        row[f"state_{state_choice}"] = 1

    X_input = pd.DataFrame([row])[MODEL_COLUMNS]
    churn_proba = model.predict_proba(X_input)[0][1]
    success_proba = 1 - churn_proba

    grade = get_grade(success_proba)
    segment_name = get_segment_name(scores)

    st.markdown(
        f"""
        <div class="result-box">
            <p style="font-size: 1.1em; margin-bottom: 0.3em;">예상 성공 확률</p>
            <p style="font-size: 2.4em; font-weight: bold; color: #1B4332; margin: 0;">
                약 {success_proba*100:.0f}%
            </p>
            <p style="margin-top: 0.6em; color: #555;">등급 {grade} · {segment_name}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    st.caption(
        "본 결과는 Olist 이커머스 판매 데이터를 학습한 모델의 예측값으로, "
        "실제 창업 성과를 보장하지 않습니다."
    )


# --- Session State 불 러 오 기 ---
import streamlit as st
import random

# --- Session State 초기화 ---
if 'secret_number' not in st.session_state:
    st.session_state.secret_number = random.randint(1, 100)
if 'guess_count' not in st.session_state:
    st.session_state.guess_count = 0
if 'guesses' not in st.session_state:
    st.session_state.guesses = []
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'high_score' not in st.session_state:
    st.session_state.high_score = 0

def reset_game():
    """게임을 초기화하는 함수"""
    st.session_state.secret_number = random.randint(1, 100)
    st.session_state.guess_count = 0
    st.session_state.guesses = []
    st.session_state.game_over = False
    st.session_state.score = 0

def calculate_score(guess_count):
    """시도 횟수에 따른 점수를 계산하는 함수"""
    return max(0, 100 - (guess_count - 1) * 10)

# --- Streamlit UI 구성 ---
st.title("UP & DOWN 숫자 게임 🎮")
st.markdown("1부터 100 사이의 숫자를 맞춰보세요! 기회는 7번입니다.")
st.markdown("20250718_2238301c - macu 제작, gzen 검수.")
st.markdown("rational-d_wgproject, v poa5")
st.markdown("high reem ")
st.markdown("thx for visiting it")

if st.session_state.high_score > 0:
    st.sidebar.markdown(f"**최고 점수:** {st.session_state.high_score}점 🏆")

st.sidebar.header("게임 정보")
st.sidebar.markdown(f"**남은 기회:** {7 - st.session_state.guess_count}")
st.sidebar.markdown(f"**시도 기록:** {st.session_state.guesses}")

if st.session_state.game_over:
    st.sidebar.markdown("---")
    if st.session_state.score > 0:
        st.sidebar.success(f"**최종 점수:** {st.session_state.score}점")
        if st.session_state.score > st.session_state.high_score:
            st.session_state.high_score = st.session_state.score
            st.sidebar.balloons()
            st.sidebar.info("🎉 최고 점수 갱신! 🎉")
    st.sidebar.button("다시 시작", on_click=reset_game)
else:
    guess = st.number_input("숫자를 입력하세요:", min_value=1, max_value=100, step=1)
    
    if st.button("제출"):
        if 1 <= guess <= 100:
            st.session_state.guess_count += 1
            st.session_state.guesses.append(guess)
            
            if guess < st.session_state.secret_number:
                st.warning("UP! 더 큰 숫자를 입력하세요.")
            elif guess > st.session_state.secret_number:
                st.warning("DOWN! 더 작은 숫자를 입력하세요.")
            else:
                st.success(f"정답입니다! 🎉 {st.session_state.guess_count}번 만에 맞히셨어요!")
                st.session_state.game_over = True
                st.session_state.score = calculate_score(st.session_state.guess_count)

            if st.session_state.guess_count >= 7 and not st.session_state.game_over:
                st.error(f"실패! 기회를 모두 사용했습니다. 정답은 {st.session_state.secret_number}였습니다. 😢")
                st.session_state.game_over = True
        else:
            st.error("1에서 100 사이의 숫자를 입력해주세요.")

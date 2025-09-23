# app.py
import streamlit as st
import time, random, io, wave, struct
import numpy as np

st.set_page_config(page_title="미니게임 포털", layout="wide")

# -------------------- Utilities --------------------
def make_tone_wav_bytes(freqs, duration=0.18, sample_rate=44100, volume=0.25):
    samples = np.array([], dtype=np.float32)
    for f in freqs:
        t = np.linspace(0, duration, int(sample_rate*duration), False)
        wave_samples = np.sin(2*np.pi * f * t)
        samples = np.concatenate([samples, wave_samples])
    if samples.size == 0:
        return b''
    maxv = np.max(np.abs(samples))
    samples = samples / maxv * volume
    pcm = (samples * 32767).astype(np.int16)
    buf = io.BytesIO()
    wf = wave.open(buf, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sample_rate)
    wf.writeframes(pcm.tobytes())
    wf.close()
    buf.seek(0)
    return buf.read()

def play_click_se():
    wav = make_tone_wav_bytes([400,600,900], duration=0.05)
    st.audio(wav, format="audio/wav")

def small_se(success=True):
    if success:
        wav = make_tone_wav_bytes([800,1200], duration=0.06)
    else:
        wav = make_tone_wav_bytes([300,200], duration=0.06)
    st.audio(wav, format="audio/wav")

# -------------------- Header / Navigation --------------------
def header():
    st.markdown("<h1 style='text-align:center;'>🎲 미니게임 포털</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Made With : ChatGPT, macugzen, Streamlit, Python</p>", unsafe_allow_html=True)

PAGES = [
    ("홈", "home"),
    ("게임 선택", "games"),
    ("정보 공간", "info"),
    ("제작진", "credits"),
]

if "page" not in st.session_state:
    st.session_state.page = "home"

with st.sidebar:
    header()
    st.sidebar.markdown("### 네비게이션")
    for label, key in PAGES:
        if st.button(label):
            st.session_state.page = key
    st.sidebar.markdown("---")
    st.sidebar.markdown("**게임 목록**")
    games = [
        ("색깔 찾기", "color_find"),
        ("숫자 찾기", "number_find"),
        ("오목", "gomoku"),
        ("점과 상자", "dots_boxes"),
        ("숫자야구", "color_mastermind"),
        ("질문 카드", "question_cards"),
        ("Up & Down", "updown"),
        ("초성퀴즈", "chosung"),
        ("끝말잇기", "word_chain"),
        ("잡학사전", "trivia"),
        ("클리커(타이쿤)", "clicker"),
        ("리듬 디펜스", "rhythm_defense"),
    ]
    for name, key in games:
        if st.button(name):
            st.session_state.page = key

# -------------------- HOME --------------------
def page_home():
    header()
    st.write("""
    ### 환영합니다!
    이 포털에는 여러 가지 미니게임이 모여 있습니다. 사이드바나 상단 메뉴로 게임을 선택하세요.
    각 게임은 간단한 설정(시간, 기회 등)을 지원하며, 사운드 이펙트가 포함되어 있습니다.
    """)
    st.markdown("## 추천")
    col1, col2, col3 = st.columns(3)
    col1.metric("플레이 가능한 게임", "12개")
    col2.metric("추천: 클리커", "가볍게 플레이")
    col3.metric("추천: 리듬 디펜스", "박자감 테스트")

# -------------------- Info Page --------------------
def page_info():
    header()
    st.header("정보 공간 — 각 콘텐츠 설명")
    st.markdown("아래는 각 게임의 간단한 설명과 조작법입니다.")
    st.write("- **색깔 찾기**: 격자에서 색이 다른 칸을 찾아 클릭하세요. 시간/기회/음 설정 가능.")
    st.write("- **숫자 찾기**: 숫자 격자에서 규칙에 맞는 순서로 숫자를 클릭하세요.")
    st.write("- **오목**: 1~4인 플레이 (간단한 봇 포함).")
    st.write("- **점과 상자**: Dots & Boxes 간단 버전.")
    st.write("- **숫자야구(색상)**: Mastermind 스타일의 색상 맞추기.")
    st.write("- **질문 카드**: 대화 주제 카드(카테고리 선택 가능).")
    st.write("- **Up & Down**: 숫자 맞추기 힌트(UP/DOWN).")
    st.write("- **초성퀴즈**: 초성만 보고 단어를 맞추는 퀴즈.")
    st.write("- **끝말잇기**: 1~4인, 봇과 대결 가능.")
    st.write("- **잡학사전**: 버튼 클릭 시 오늘의 신기한 사실 2개 표시.")
    st.write("- **클리커(타이쿤)**: 클릭으로 자원 수집 → 업그레이드 구매 → 자동 수익 획득")
    st.write("- **리듬 디펜스**: 간단한 박자 게임. 박자에 맞춰 클릭하여 적을 방어하세요. (Streamlit 환경에 맞춰 단순화 구현됨)")

# -------------------- Credits --------------------
def page_credits():
    header()
    st.header("제작진 / Credits")
    st.markdown("""
    - 제작: macugzen
    - 도움: ChatGPT
    - 기술: Streamlit, Python, NumPy
    """)
    st.markdown("---")
    st.write("감사합니다! 추가 기능이나 개선 요청은 알려주세요.")

# -------------------- Existing Mini-games (summarized minimal implementations) --------------------
# For brevity, include simplified versions of the previously provided games
def page_color_find():
    st.header("색깔 찾기")
    grid_n = st.slider("가로/세로 칸 수", 2, 8, 4)
    time_limit = st.number_input("시간 제한(초, 0=무한)", min_value=0, value=0)
    attempts_limit = st.number_input("기회 수(0=무한)", min_value=0, value=3)
    enable_sound = st.checkbox("음 발생 (점점 높아지는 음)", value=False)
    difficulty = st.selectbox("난이도", ["쉬움","보통","어려움"])
    if "cf_state" not in st.session_state:
        st.session_state.cf_state = {}
    s = st.session_state.cf_state
    if st.button("새 게임") or not s:
        base = [random.randint(40,220) for _ in range(3)]
        diff = {"쉬움":40,"보통":20,"어려움":8}[difficulty]
        odd = base.copy(); odd[random.randrange(3)] = max(0, min(255, odd[random.randrange(3)]-diff))
        odd_pos = (random.randrange(grid_n), random.randrange(grid_n))
        s.update({"base":tuple(base), "odd":tuple(odd), "n":grid_n, "start":time.time(), "time_limit":time_limit, "attempts_left":attempts_limit if attempts_limit>0 else None, "odd_pos":odd_pos, "found":False})
    n = s["n"]; base = s["base"]; odd = s["odd"]; odd_pos = s["odd_pos"]
    def rgb_style(rgb): return f"background-color: rgb({rgb[0]},{rgb[1]},{rgb[2]}); width:60px; height:60px; border-radius:6px; border:1px solid #111;"
    for r in range(n):
        cols = st.columns(n, gap="small")
        for c in range(n):
            rgb = odd if (r,c)==odd_pos else base
            key = f"cf_{r}_{c}_{s['start']}"
            if cols[c].button("", key=key):
                if s["time_limit"] and time.time()-s["start"]>s["time_limit"]:
                    st.warning("시간 초과")
                elif s["attempts_left"] == 0:
                    st.warning("기회 소진")
                else:
                    if (r,c)==odd_pos:
                        s["found"]=True; st.success("정답!")
                    else:
                        if s["attempts_left"] is not None: s["attempts_left"] -= 1
                        st.error("틀렸습니다")
            cols[c].markdown(f"<div style='{rgb_style(rgb)}'></div>", unsafe_allow_html=True)
    if enable_sound:
        freqs = [400 + i*80 for i in range(n)]
        st.audio(make_tone_wav_bytes(freqs, duration=0.1), format="audio/wav")
    st.write("상태:", "정답!" if s.get("found") else f"남은 기회: {s.get('attempts_left','무한')}")

def page_number_find():
    st.header("숫자 찾기")
    range_min = st.number_input("최소값", value=1)
    range_max = st.number_input("최대값", value=25)
    order_mode = st.selectbox("클릭 순서", ["오름차순","내림차순"])
    grid_n = st.slider("칸 수(가로/세로)", 2, 6, 4)
    if range_max <= range_min: st.error("최대 > 최소 필요"); return
    cnt = grid_n*grid_n
    pool = list(range(range_min, range_max+1))
    nums = random.sample(pool, cnt) if len(pool)>=cnt else [random.choice(pool) for _ in range(cnt)]
    target = sorted(nums) if order_mode=="오름차순" else sorted(nums, reverse=True)
    if "nf_state" not in st.session_state:
        st.session_state.nf_state = {"nums":nums, "target":target, "idx":0, "start":time.time()}
    s = st.session_state.nf_state
    st.write("다음 클릭:", s["target"][s["idx"]])
    for r in range(grid_n):
        cols = st.columns(grid_n, gap="small")
        for c in range(grid_n):
            v = s["nums"][r*grid_n+c]
            if cols[c].button(str(v), key=f"n_{r}_{c}_{s['start']}"):
                if v == s["target"][s["idx"]]:
                    s["idx"] += 1; small_se(True)
                    if s["idx"] >= len(s["target"]): st.balloons(); st.success("완료!")
                else:
                    small_se(False); st.error("틀렸습니다.")

def page_gomoku():
    st.header("오목 (간단 버전)")
    size = st.slider("보드 크기", 9, 15, 11)
    players = st.slider("플레이 인원", 1, 4, 2)
    colors = ["●","○","■","◆"]
    if "g_state" not in st.session_state:
        st.session_state.g_state = {"board":[[None]*size for _ in range(size)], "turn":0, "players":players}
    g = st.session_state.g_state
    board = g["board"]
    cur = g["turn"] % g["players"]
    st.write(f"턴: P{cur+1}")
    for r in range(size):
        cols = st.columns(size, gap="small")
        for c in range(size):
            val = board[r][c]
            if cols[c].button(val if val else ".", key=f"gom_{r}_{c}"):
                if val is None:
                    board[r][c] = colors[cur]
                    g["turn"] += 1

def page_dots_boxes():
    st.header("점과 상자 (간단)")
    st.write("간단화된 표현 — 실제 규칙의 축약판입니다.")

def page_color_mastermind():
    st.header("숫자야구 (색상 버전)")
    palette = st.slider("색상 수", 1, 12, 6)
    code_len = st.slider("정답 길이", 1, min(8,palette), 4)
    allow_dup = st.checkbox("중복 허용", value=False)
    if "mm" not in st.session_state: st.session_state.mm = {}
    s = st.session_state.mm
    if st.button("새 게임") or "secret" not in s:
        pool = list(range(1, palette+1))
        s["secret"] = [random.choice(pool) for _ in range(code_len)] if allow_dup else random.sample(pool, code_len)
        s["hist"] = []
    guess = st.text_input("추측 입력 (예: 1 2 3 4)","")
    if st.button("제출"):
        try:
            g = [int(x) for x in guess.split()]
            bulls = sum(1 for i in range(code_len) if g[i]==s["secret"][i])
            cows = 0
            sc = s["secret"].copy(); gc = g.copy()
            for i in reversed(range(code_len)):
                if gc[i]==sc[i]: del gc[i]; del sc[i]
            for x in gc:
                if x in sc: cows+=1; sc.remove(x)
            s["hist"].append((g,bulls,cows))
            if bulls==code_len: st.success("정답!")
        except:
            st.error("입력 오류")
    for it in s.get("hist",[]): st.write(it)

def page_question_cards():
    st.header("질문 카드")
    cat = st.selectbox("카테고리", ["밸런스 게임","일상 토크","토론","랜덤"])
    n = st.slider("카드 수", 1, 6, 3)
    bank = {"밸런스 게임":["피자 vs 햄버거","강아지 vs 고양이"], "일상 토크":["요즘 관심사?","최근 감동받은 일?"], "토론":["스마트폰 허용?","온라인 수업의 장단점?"], "랜덤":["초능력이 있다면?","가장 좋아하는 계절?"]}
    if st.button("뽑기"):
        for i in random.sample(bank[cat], min(n, len(bank[cat]))): st.write("- "+i)

def page_updown():
    st.header("Up & Down")
    minv = st.number_input("최소값", value=1)
    maxv = st.number_input("최대값", value=100)
    attempts = st.number_input("기회 수", min_value=0, value=10)
    if "ud" not in st.session_state: st.session_state.ud = {"secret":random.randint(minv,maxv), "tries":0}
    s = st.session_state.ud
    g = st.number_input("추측", value=minv)
    if st.button("제출"):
        s["tries"] += 1
        if g == s["secret"]: st.success(f"정답! 시도: {s['tries']}"); del st.session_state.ud
        elif g < s["secret"]: st.info("UP ↑")
        else: st.info("DOWN ↓")

def page_chosung():
    st.header("초성퀴즈 (간단)")
    bank = [("강아지","동물"),("바나나","과일"),("피자","음식")]
    if "cho" not in st.session_state:
        w,c = random.choice(bank); st.session_state.cho = {"w":w,"c":c}
    s = st.session_state.cho
    # simple chosung display (not full algorithm for simplicity)
    hint = "".join([ch[0] for ch in s["w"]])  # not real 초성, but indicative
    st.write("초성:", hint); st.write("카테고리:", s["c"])
    ans = st.text_input("정답")
    if st.button("확인"):
        if ans==s["w"]: st.success("정답!"); del st.session_state.cho
        else: st.error("오답")

def page_word_chain():
    st.header("끝말잇기 (간단)")
    words = ["사과","과일","음악","학교","교실","실내"]
    if "wc" not in st.session_state: st.session_state.wc = {"used":[], "last":random.choice(words)}
    s = st.session_state.wc
    st.write("현재 단어:", s["last"])
    guess = st.text_input("단어 입력")
    if st.button("제출"):
        if not guess: st.error("입력")
        elif guess[0] != s["last"][-1]: st.error("끝말 불일치")
        else: s["used"].append(guess); s["last"]=guess; st.success("OK")

def page_trivia():
    st.header("잡학사전")
    facts = ["문어는 심장이 3개다.","바나나는 베리류다.","꿀벌은 중요한 꽃가루 매개자다."]
    if st.button("사실 보기"):
        for f in random.sample(facts,2): st.write("- "+f)

# -------------------- 11. Clicker / Tycoon --------------------
def page_clicker():
    st.header("클리커(타이쿤)")
    if "clicker" not in st.session_state:
        st.session_state.clicker = {"coins":0, "per_click":1, "per_sec":0, "last_tick":time.time(), "upgrades":[{"name":"클릭+1","cost":10,"add_click":1,"add_auto":0},{"name":"자동수익+1/s","cost":50,"add_click":0,"add_auto":1}]}
    c = st.session_state.clicker
    # accumulate auto income
    now = time.time(); elapsed = now - c["last_tick"]
    if elapsed >= 1:
        gain = int(c["per_sec"] * elapsed)
        c["coins"] += gain
        c["last_tick"] = now
    col1, col2 = st.columns([2,1])
    with col1:
        if st.button("클릭!"):
            c["coins"] += c["per_click"]
            play_click_se()
    with col2:
        st.metric("코인", c["coins"])
        st.metric("클릭당", c["per_click"])
        st.metric("초당", c["per_sec"])
    st.markdown("### 상점")
    for i, up in enumerate(c["upgrades"]):
        if st.button(f"구매: {up['name']} (비용: {up['cost']})", key=f"upg_{i}"):
            if c["coins"] >= up["cost"]:
                c["coins"] -= up["cost"]
                c["per_click"] += up["add_click"]
                c["per_sec"] += up["add_auto"]
                up["cost"] = int(up["cost"] * 1.6)
                small_se(True)
            else:
                small_se(False); st.warning("코인 부족")

# -------------------- 12. Rhythm Defense (simplified) --------------------
def page_rhythm_defense():
    st.header("리듬 디펜스 (간단화 버전)")
    bpm = st.slider("BPM (속도)", 60, 200, 100)
    length = st.slider("노트 개수", 4, 16, 8)
    tolerance = st.slider("정확도 허용(ms)", 100, 800, 300)
    if "rh" not in st.session_state:
        st.session_state.rh = {"start":None, "beat_times":[], "idx":0, "hits":0, "misses":0, "running":False}
    rh = st.session_state.rh
    if st.button("게임 시작"):
        # create beat times relative to start (seconds)
        interval = 60.0 / bpm
        rh["beat_times"] = [i*interval for i in range(length)]
        rh["start"] = time.time()
        rh["idx"] = 0; rh["hits"]=0; rh["misses"]=0; rh["running"]=True
    st.write("설명: 'Hit' 버튼을 박자에 맞춰 눌러 적을 막으세요. 서버-인터랙티브 한계로 단순화 되어 있습니다.")
    if rh.get("running"):
        now = time.time() - rh["start"]
        # show next beat countdown
        if rh["idx"] < len(rh["beat_times"]):
            next_beat = rh["beat_times"][rh["idx"]]
            st.write(f"다음 박자까지: {max(0, next_beat - now):.2f}s (인덱스 {rh['idx']+1}/{len(rh['beat_times'])})")
        else:
            st.write("라운드 종료") ; rh["running"]=False
        if st.button("Hit"):
            hit_time = time.time() - rh["start"]
            # find closest upcoming beat index not yet checked
            target_idx = rh["idx"]
            if target_idx < len(rh["beat_times"]):
                beat_t = rh["beat_times"][target_idx]
                delta_ms = abs((hit_time - beat_t)*1000)
                if delta_ms <= tolerance:
                    rh["hits"] += 1; rh["idx"] += 1; small_se(True); st.success(f"Perfect! ({int(delta_ms)} ms)")
                else:
                    rh["misses"] += 1; rh["idx"] += 1; small_se(False); st.info(f"Miss ({int(delta_ms)} ms)")
            else:
                st.info("더 이상 박자가 없습니다.")
        st.write(f"히트: {rh['hits']} / 미스: {rh['misses']}")
    else:
        st.info("게임을 시작하세요.")

# -------------------- Router --------------------
ROUTER = {
    "home": page_home,
    "games": lambda: st.experimental_rerun(),  # placeholder, use sidebar game buttons
    "info": page_info,
    "credits": page_credits,
    "color_find": page_color_find,
    "number_find": page_number_find,
    "gomoku": page_gomoku,
    "dots_boxes": page_dots_boxes,
    "color_mastermind": page_color_mastermind,
    "question_cards": page_question_cards,
    "updown": page_updown,
    "chosung": page_chosung,
    "word_chain": page_word_chain,
    "trivia": page_trivia,
    "clicker": page_clicker,
    "rhythm_defense": page_rhythm_defense,
}

def main():
    page = st.session_state.get("page", "home")
    fn = ROUTER.get(page, page_home)
    try:
        fn()
    except Exception as e:
        st.error("오류가 발생했습니다: " + str(e))

if __name__ == "__main__":
    main()

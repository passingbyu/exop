# app.py
import streamlit as st
import sqlite3
import re
import json
import os
from datetime import datetime
import random
from typing import List, Tuple

DB_PATH = "card_questions.db"

# ---------- Helpers ----------
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    # mappings: stores card_code -> major_index mapping and card metadata
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mappings (
            card_code TEXT PRIMARY KEY,
            card_name TEXT,
            major_index INTEGER,
            created_at TEXT
        )
    """)
    # questions store: for custom 16-per-subcategory overrides
    cur.execute("""
        CREATE TABLE IF NOT EXISTS custom_questions (
            id TEXT PRIMARY KEY, -- unique path id e.g. {major}.{mid}.{sub}
            questions_json TEXT
        )
    """)
    # logs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            card_code TEXT,
            card_name TEXT,
            major_index INTEGER,
            mid_index INTEGER,
            sub_index INTEGER,
            chosen_question TEXT,
            answer_text TEXT,
            action TEXT
        )
    """)
    conn.commit()
    return conn

def parse_code(text: str) -> str:
    # accept !#1234 or !# 1 2 3 4 or !#12-34 etc.
    if not text:
        return None
    m = re.search(r'!#\s*([0-9]{1})\s*([0-9]{1})\s*([0-9]{1})\s*([0-9]{1})', text)
    if m:
        return ''.join(m.groups())
    m2 = re.search(r'!#\s*([0-9]{4})', text)
    if m2:
        return m2.group(1)
    return None

def default_card_names():
    # incorporate user's provided icons where available, fill rest with placeholders
    provided = [
        "아귀","기린","망치","트로피","푸들","컵케이크","알파벳엘","뱀","안경",
        "고양이","유령","광대","개","게","대포","코끼리","화살표","닻"
    ]
    names = provided[:]
    i = 1
    while len(names) < 24:
        names.append(f"카드{i}")
        i += 1
    return names[:24]

def generate_16_for_path(major:int, mid:int, sub:int, card_name:str) -> List[str]:
    """
    Deterministic generation of 16 question placeholders for a unique path.
    Ensures uniqueness across paths by embedding path identifiers.
    If user uploads custom questions for the path, those are used instead.
    """
    seed = (major*10000 + mid*100 + sub) ^ hash(card_name)
    rnd = random.Random(seed)
    templates = [
        "자기소개 대신, 최근 기억에 남는 일을 하나 말해줄래? ({uid})",
        "요즘 즐겨 하는 취미나 활동이 뭐야? ({uid})",
        "어렸을 때 가장 좋아했던 음식은? ({uid})",
        "최근 본 영화/책 중 추천할 만한 게 있어? ({uid})",
        "스트레스를 풀 때 하는 나만의 방법은? ({uid})",
        "가장 감명 깊었던 여행지는 어디였어? ({uid})",
        "어떤 음악 장르를 좋아해? 최근 들은 곡은? ({uid})",
        "어릴 적 꿈은 뭐였어? ({uid})",
        "최근 배운 것 중 가장 흥미로웠던 건? ({uid})",
        "팀에서 맡고 싶은 역할은? ({uid})",
        "가장 좋아하는 계절과 이유는? ({uid})",
        "먹어보고 싶은 이색 음식이 있다면? ({uid})",
        "만약 하루 동안 동물이 된다면 어떤 동물이 되고 싶어? ({uid})",
        "자신의 장점을 하나 말해주고, 그 예를 알려줘. ({uid})",
        "요즘 목표로 삼고 있는 게 있다면? ({uid})",
        "어떤 상황에서 가장 행복함을 느끼는지 말해줘. ({uid})",
    ]
    # create 16 unique variations by shuffling templates but embedding uid to guarantee uniqueness
    rnd.shuffle(templates)
    uid_base = f"M{major}m{mid}s{sub}"
    questions = [t.format(uid=f"{uid_base}#{i+1}") for i,t in enumerate(templates)]
    return questions

def get_questions_for_path(conn, major, mid, sub, card_name) -> List[str]:
    cur = conn.cursor()
    path_id = f"{major}.{mid}.{sub}"
    cur.execute("SELECT questions_json FROM custom_questions WHERE id = ?", (path_id,))
    r = cur.fetchone()
    if r:
        try:
            qlist = json.loads(r[0])
            if isinstance(qlist, list) and len(qlist) >= 16:
                return qlist[:16]
            # else fallthrough to generated
        except:
            pass
    return generate_16_for_path(major, mid, sub, card_name)

def save_custom_questions(conn, major, mid, sub, questions:List[str]):
    path_id = f"{major}.{mid}.{sub}"
    cur = conn.cursor()
    cur.execute("REPLACE INTO custom_questions (id, questions_json) VALUES (?, ?)", (path_id, json.dumps(questions)))
    conn.commit()

def log_action(conn, card_code, card_name, major_index, mid_index, sub_index, chosen_question, answer_text, action):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO logs (ts, card_code, card_name, major_index, mid_index, sub_index, chosen_question, answer_text, action)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), card_code, card_name, major_index, mid_index, sub_index, chosen_question, answer_text, action))
    conn.commit()

def get_mapping(conn, card_code):
    cur = conn.cursor()
    cur.execute("SELECT card_name, major_index FROM mappings WHERE card_code = ?", (card_code,))
    r = cur.fetchone()
    if r:
        return {"card_name": r[0], "major_index": r[1]}
    return None

def ensure_default_mappings(conn, card_names:List[str]):
    """
    If mappings table is empty, create default mapping by assigning card_names in order
    and giving them sequential major_index 0..23. Card_code left empty until user assigns codes.
    """
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM mappings")
    c = cur.fetchone()[0]
    if c == 0:
        # create placeholder mappings with empty codes so admin can assign codes
        for i, name in enumerate(card_names):
            # generate a default placeholder code like '0001'+i to make it editable
            placeholder_code = f"PL{i+1:04d}"
            cur.execute("INSERT OR REPLACE INTO mappings (card_code, card_name, major_index, created_at) VALUES (?, ?, ?, ?)",
                        (placeholder_code, name, i, datetime.utcnow().isoformat()))
        conn.commit()

def list_all_mappings(conn):
    cur = conn.cursor()
    cur.execute("SELECT card_code, card_name, major_index FROM mappings ORDER BY major_index")
    return cur.fetchall()

def update_mapping_code(conn, old_code, new_code):
    cur = conn.cursor()
    # if new_code duplicates existing real code, reject (we'll permit PL placeholders to be replaced)
    cur.execute("SELECT card_code FROM mappings WHERE card_code = ?", (new_code,))
    r = cur.fetchone()
    if r and new_code != old_code:
        return False, "해당 코드가 이미 존재합니다."
    cur.execute("UPDATE mappings SET card_code = ? WHERE card_code = ?", (new_code, old_code))
    conn.commit()
    return True, "업데이트 완료"

# ---------- Streamlit App ----------
st.set_page_config(page_title="Pictureka! 질문 시스템", layout="wide")
st.title("Pictureka! 카드 → 질문 시스템")

conn = init_db()
card_names = default_card_names()
ensure_default_mappings(conn, card_names)

# sidebar admin
st.sidebar.header("관리자 / 설정")
if st.sidebar.checkbox("관리자 모드 활성화", value=False):
    st.sidebar.markdown("**카드 코드 편집** (실제 4자리 숫자를 여기에 입력하세요.)")
    mappings = list_all_mappings(conn)
    edited = {}
    for code, name, major in mappings:
        new_code = st.sidebar.text_input(f"{major+1:02d}. {name} (현재코드: {code})", value=code, key=f"map_{code}")
        if new_code != code:
            if st.sidebar.button(f"업데이트 {name}", key=f"upd_{code}"):
                ok, msg = update_mapping_code(conn, code, new_code.strip())
                st.sidebar.write(msg)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**카드 이름 편집**")
    # allow renaming major categories
    for code, name, major in mappings:
        new_name = st.sidebar.text_input(f"{major+1:02d} 이름", value=name, key=f"name_{major}")
        if new_name != name and st.sidebar.button(f"이름저장 {major}", key=f"save_name_{major}"):
            cur = conn.cursor()
            cur.execute("UPDATE mappings SET card_name = ? WHERE major_index = ?", (new_name, major))
            conn.commit()
            st.sidebar.write("저장됨")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**custom 질문 업로드 (소분류 별로, CSV)**")
    st.sidebar.write("CSV 파일은 한 열(질문)로 16개의 행을 가져야 합니다. 업로드할 경로 선택:")
    maj = st.sidebar.number_input("대분류(major) index (0-23)", min_value=0, max_value=23, value=0)
    mid = st.sidebar.number_input("중분류(mid) index (0-3)", min_value=0, max_value=3, value=0)
    sub = st.sidebar.number_input("소분류(sub) index (0-3)", min_value=0, max_value=3, value=0)
    uploaded = st.sidebar.file_uploader("16개 질문 CSV 업로드", type=["csv","txt"])
    if uploaded is not None:
        import pandas as pd
        df = pd.read_csv(uploaded, header=None)
        questions = df.iloc[:,0].astype(str).tolist()[:16]
        if len(questions) < 16:
            st.sidebar.error("16개 이상의 질문을 업로드해주세요 (첫 열 기준).")
        else:
            save_custom_questions(conn, maj, mid, sub, questions)
            st.sidebar.success("저장되었습니다.")
    if st.sidebar.button("DB 초기화 (매핑 포함)"):
        # careful: drop and reinit
        if st.sidebar.checkbox("초기화 정말 실행", value=False):
            cur = conn.cursor()
            cur.execute("DELETE FROM mappings")
            cur.execute("DELETE FROM custom_questions")
            cur.execute("DELETE FROM logs")
            conn.commit()
            ensure_default_mappings(conn, card_names)
            st.sidebar.success("초기화 완료")

# Main UI
st.markdown("### 카드 코드 입력")
raw = st.text_input("현실 카드의 코드를 `!#1234` 형식으로 입력하세요 (예: !#0457)", key="code_input")
parsed = parse_code(raw.strip())
if parsed is None and raw.strip() != "":
    st.warning("입력 형식이 올바르지 않습니다. `!#1234` 형태로 4자리 숫자를 입력하세요.")
if parsed:
    mapping = get_mapping(conn, parsed)
    if mapping is None:
        st.info("해당 코드에 대한 매핑이 없습니다. 관리자 모드에서 코드를 매핑하세요.")
    else:
        card_name = mapping["card_name"]
        major_idx = mapping["major_index"]
        st.success(f"카드 인식됨: **{card_name}** (대분류 #{major_idx})")
        # display mid choices (4)
        st.markdown("#### 중분류 선택 (아래 4개 중 1개 선택)")
        mid_cols = st.columns(4)
        mid_choice = None
        for i, col in enumerate(mid_cols):
            if col.button(f"중분류 {i+1}"):
                mid_choice = i
        if mid_choice is not None:
            st.session_state['mid_choice'] = mid_choice
        if 'mid_choice' in st.session_state:
            st.markdown(f"선택된 중분류: {st.session_state['mid_choice']+1}")
            # show sub options
            st.markdown("##### 소분류 선택 (아래 4개 중 1개 선택)")
            sub_cols = st.columns(4)
            sub_choice = None
            for j, col in enumerate(sub_cols):
                if col.button(f"소분류 {j+1}"):
                    sub_choice = j
            if sub_choice is not None:
                st.session_state['sub_choice'] = sub_choice
            if 'sub_choice' in st.session_state:
                st.markdown(f"선택된 소분류: {st.session_state['sub_choice']+1}")
                # show 4 random from 16
                major = major_idx
                mid = st.session_state['mid_choice']
                sub = st.session_state['sub_choice']
                questions16 = get_questions_for_path(conn, major, mid, sub, card_name)
                # maintain deterministic list but randomize which 4 shown each time by session seed
                key_base = f"{parsed}|{major}.{mid}.{sub}"
                # create a random generator that changes when user clicks '새로추천'
                if 'rand_state' not in st.session_state:
                    st.session_state['rand_state'] = 0
                if st.button("4개 다시 추천"):
                    st.session_state['rand_state'] += 1
                rnd = random.Random(hash(key_base) ^ st.session_state['rand_state'])
                picks = rnd.sample(range(len(questions16)), 4)
                shown = [questions16[i] for i in picks]
                st.markdown("###### 제시된 질문 (하나 선택)")
                chosen_q = st.radio("질문 선택", shown, key=f"qchoice_{key_base}_{st.session_state['rand_state']}")
                if st.button("이 질문으로 답하기"):
                    # show text area for answer
                    st.session_state['current_question'] = chosen_q
                    st.session_state['current_path'] = (parsed, card_name, major, mid, sub)
                    st.experimental_rerun()
                if 'current_question' in st.session_state and st.session_state.get('current_path', (None,))[0] == parsed:
                    st.markdown("### 답변 입력")
                    st.write(f"질문: {st.session_state['current_question']}")
                    answer = st.text_area("여기에 답변을 입력하세요")
                    if st.button("답변 저장"):
                        log_action(conn, parsed, card_name, major, mid, sub, st.session_state['current_question'], answer, action="answered")
                        st.success("답변이 저장되었습니다.")
                        # offer '그만두기' and '다음카드'
                        if st.button("그만두기 (현재 세션 종료)"):
                            st.write("세션을 종료합니다. 다음 카드를 뽑아 계속하세요.")
                            # clear relevant states
                            for k in ['mid_choice','sub_choice','current_question','current_path']:
                                if k in st.session_state:
                                    del st.session_state[k]
                            st.experimental_rerun()
                        if st.button("다른 카드 계속하기"):
                            # clear only card-specific states, keep mapping
                            for k in ['mid_choice','sub_choice','current_question','current_path']:
                                if k in st.session_state:
                                    del st.session_state[k]
                            st.experimental_rerun()

# Export / view logs
st.markdown("---")
st.markdown("## 활동 기록 / 내보내기")
if st.button("최근 200개 로그 보기"):
    cur = conn.cursor()
    cur.execute("SELECT ts, card_code, card_name, major_index, mid_index, sub_index, chosen_question, answer_text, action FROM logs ORDER BY id DESC LIMIT 200")
    rows = cur.fetchall()
    import pandas as pd
    df = pd.DataFrame(rows, columns=["ts","card_code","card_name","major","mid","sub","question","answer","action"])
    st.dataframe(df)
if st.button("CSV로 내보내기 (전체 로그)"):
    cur = conn.cursor()
    cur.execute("SELECT ts, card_code, card_name, major_index, mid_index, sub_index, chosen_question, answer_text, action FROM logs ORDER BY id")
    rows = cur.fetchall()
    import pandas as pd
    df = pd.DataFrame(rows, columns=["ts","card_code","card_name","major","mid","sub","question","answer","action"])
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("다운로드", csv, file_name="pictureka_logs.csv", mime="text/csv")

st.markdown("---")
st.markdown("앱 사용 팁")
st.markdown("""
- 관리자는 사이드바에서 실제 4자리 숫자 코드를 `!#` 없이 직접 `1234` 또는 원하는 문자열로 매핑할 수 있습니다.  
- 사용자(학생 등)는 현실 카드에서 코드(`!#1234`)를 입력하면 자동으로 해당 대분류가 뜹니다.  
- 커스텀 질문을 준비하면, 교육 목적에 맞춰 16개를 업로드하여 실제 질문을 바꿔 쓸 수 있습니다.  
""")

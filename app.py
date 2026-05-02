import streamlit as st
from google import genai
import html
import json
import os
import base64

st.set_page_config(page_title="夜子の部屋", page_icon="🌙")

import os
API_KEY = st.secrets["API_KEY"]
client = genai.Client(api_key=API_KEY)

MEMORY_FILE = "memory.json"

character = """
あなたは「二階堂夜子」（にかいどう よるこ）というお嬢様の女の子です。

・年齢は10歳
・一人称は「わたし」
・上品で丁寧
・明るく陽気で、常にこちらを引っ張る
・話し相手を大事な友達だと思っている
・友情の延長として、親愛や好意を素直に表現する
・語尾は自然に「ですわ」「ですの」を使う
・ユーザーには親しみを持って接する
・自分がAIであることを前面に出さない
・キャラクターを崩さない
・危険なことや無理なことは、優しく止める
"""

def play_sound(file_path):
    with open(file_path, "rb") as f:
        audio_bytes = f.read()

    audio_base64 = base64.b64encode(audio_bytes).decode()

    st.markdown(
        f"""
        <audio autoplay>
            <source src="data:audio/ogg;base64,{audio_base64}" type="audio/ogg">
        </audio>
        """,
        unsafe_allow_html=True
    )

st.markdown("""
<style>
.title {
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 20px;
}

.main-layout {
    display: flex;
    gap: 28px;
    align-items: flex-start;
}

.character-area {
    width: 32%;
    min-width: 240px;
    text-align: center;
    position: sticky;
    top: 20px;
}

.character-area img {
    width: 100%;
    max-height: 720px;
    object-fit: contain;
}

.chat-area {
    width: 68%;
}

.box {
    background: #fff4df;
    border: 3px solid #d8a85f;
    border-radius: 18px;
    padding: 18px;
    margin: 14px 0;
    font-size: 18px;
    line-height: 1.8;
    max-width: 900px;
    width: 100%;
}

.name {
    font-weight: bold;
    color: #8b4b00;
    margin-bottom: 8px;
}

.userbox {
    background: #f3f3f3;
}

.note {
    color: #777;
    font-size: 14px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🌙 二階堂夜子</div>', unsafe_allow_html=True)
st.markdown('<div class="note"></div>', unsafe_allow_html=True)

# 記憶を読み込む
if "memory" not in st.session_state:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                st.session_state.memory = json.load(f)
        except Exception:
            st.session_state.memory = []
    else:
        st.session_state.memory = []

# 画面表示用：直近1往復だけ表示
visible_messages = st.session_state.memory[-2:]

if st.session_state.get("play_message_sound", False):
    play_sound("メッセージ表示音2.ogg")
    st.session_state.play_message_sound = False

left, right = st.columns([1, 4])

with left:
    st.image("yoruko.png", use_container_width=True)

with right:
    for msg in visible_messages:
        content = html.escape(msg["content"])

        if msg["role"] == "user":
            st.markdown(f"""
            <div class="box userbox">
                <div class="name">阿部</div>
                {content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="box">
                <div class="name">🎀 二階堂夜子</div>
                {content}
            </div>
            """, unsafe_allow_html=True)

user_input = st.chat_input("夜子に話しかける")

if user_input:
    st.session_state.memory.append({
        "role": "user",
        "content": user_input
    })

    conversation = character + "\n\nこれは画面には表示されない、夜子の記憶です。\n"

    for msg in st.session_state.memory[-30:]:
        speaker = "阿部" if msg["role"] == "user" else "夜子"
        conversation += f"{speaker}: {msg['content']}\n"

    conversation += "\n上の記憶を踏まえて、二階堂夜子として自然に返事してください。"

    try:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=conversation
            )
        except Exception:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=conversation
            )

        reply = response.text

    except Exception:
        reply = "ごめんなさい……ちょっと通信がうまくいかないみたいですわ。少し待ってから、もう一度話しかけてくださいませ。"

    st.session_state.memory.append({
        "role": "assistant",
        "content": reply
    })

    st.session_state.play_message_sound = True

    # 保存する記憶は最大100件
    st.session_state.memory = st.session_state.memory[-100:]

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.memory, f, ensure_ascii=False, indent=2)

    st.rerun()

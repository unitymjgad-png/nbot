import streamlit as st
from groq import Groq
import base64

# ============================================================
# ページ設定
# ============================================================
st.set_page_config(
    page_title="Cloud LLM Chat",
    page_icon="☁️",
    layout="wide"
)

# ============================================================
# 背景画像設定
# imageフォルダ内の「にゃんこ.jpg」を使用
# ============================================================
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

img = get_base64_image("image/にゃんこ.jpg")

st.markdown(
    f"""
    <style>

    /* 背景画像 */
    .stApp {{
        background:
            linear-gradient(
                rgba(0,0,0,0.35),
                rgba(0,0,0,0.35)
            ),
            url("data:image/jpeg;base64,{img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* タイトル */
    h1 {{
        color: black;
        text-align: center;
        text-shadow: 2px 2px 8px black;
    }}

    /* チャット入力欄 */
    .stChatInput {{
        background-color: rgba(255,255,255,0.85);
        border-radius: 15px;
    }}

    /* ユーザー・AIの吹き出し */
    [data-testid="stChatMessage"] {{
        background-color: rgba(1,1,1,0.75);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# アイコン画像の定義
# ============================================================
# ユーザーとAIの画像パスをここで指定します
AVATARS = {
    "user": "image/user.jpg",       # ユーザーの画像パス
    "assistant": "image/にゃんこ.jpg" # AI（にゃんこ）の画像パス
}

# ============================================================
# タイトル
# ============================================================
st.title("にゃんこ　チャット")

# ============================================================
# APIキー（Streamlit CloudのSecrets）
# ============================================================
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# ============================================================
# Groqクライアント
# ============================================================
client = Groq(api_key=GROQ_API_KEY)

# ============================================================
# 会話履歴
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================================
# 過去の会話を表示
# ============================================================
for message in st.session_state.messages:
    # 定義した辞書からロールに応じた画像を取得
    role = message["role"]
    avatar_img = AVATARS.get(role)
    
    with st.chat_message(role, avatar=avatar_img):
        st.markdown(message["content"])

# ============================================================
# ユーザー入力
# ============================================================
if user_input := st.chat_input("メッセージを入力してください..."):

    # ユーザー表示
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(user_input)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # AI応答
    with st.chat_message("assistant", avatar=AVATARS["assistant"]):

        try:

            stream = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": msg["role"],
                        "content": msg["content"]
                    }
                    for msg in st.session_state.messages
                ],
                stream=True,
            )

            def generate_chunks():
                for chunk in stream:
                    if (
                        chunk.choices
                        and chunk.choices[0].delta
                        and chunk.choices[0].delta.content
                    ):
                        yield chunk.choices[0].delta.content

            full_response = st.write_stream(generate_chunks())

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )

        except Exception as e:
            st.error(f"エラーが発生しました。\n\n{e}")

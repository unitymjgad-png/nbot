import streamlit as st
from groq import Groq
import base64
import streamlit.components.v1 as components

# ============================================================
# ページ設定
# ============================================================
st.set_page_config(
    page_title="Cloud LLM Chat",
    page_icon="☁️",
    layout="wide"
)

# ============================================================
# 画像ファイルパスの設定
# ============================================================
BACKGROUND_IMAGE = "image/背景にゃんこ.jpg"  # 背景用の画像
AI_AVATAR_IMAGE  = "image/AIにゃんこ.jpg"    # AI（チャット用）の画像
USER_AVATAR_IMAGE = "image/ユーザー.jpg"      # ユーザー（チャット用）の画像

# ============================================================
# 背景画像設定 & CSS
# ============================================================
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

bg_img = get_base64_image(BACKGROUND_IMAGE)

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
            url("data:image/jpeg;base64,{bg_img}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* ヘッダー（上部バー）の完全透明化・非表示 */
    [data-testid="stHeader"], .stAppHeader {{
        background-color: transparent !important;
        background: transparent !important;
        box-shadow: none !important;
        border-bottom: none !important;
    }}

    /* 右上のアイコンの色を背景に馴染む薄いグレーに変更 */
    [data-testid="stHeader"] *, .stAppHeader * {{
        color: #aaaaaa !important;
    }}

    /* フッターの完全非表示・透明化 */
    footer, .stAppFooter, [data-testid="stFooter"] {{
        visibility: hidden !important;
        height: 0px !important;
        display: none !important;
        background-color: transparent !important;
        background: transparent !important;
        border-top: none !important;
    }}

    /* メインコンテンツエリアの上部余白を調整して背景を広く見せる */
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 2rem !important;
    }}

    /* タイトル */
    h1 {{
        color: white;
        text-align: center;
        text-shadow: 2px 2px 8px black;
    }}

    /* 【新規追加】チャット入力欄の外枠コンテナ（黒い帯）を完全に透明化 */
    [data-testid="stChatInputBottomContainer"] {{
        background-color: transparent !important;
        background: transparent !important;
    }}

    /* チャット入力欄自体のデザイン */
    .stChatInput {{
        background-color: rgba(255,255,255,0.9) !important;
        border-radius: 15px;
        border: 1px solid rgba(0,0,0,0.2) !important;
    }}

    /* ユーザー・AIの吹き出し（背景を黒透過） */
    [data-testid="stChatMessage"] {{
        background-color: rgba(1,1,1,0.75) !important;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }}

    /* 吹き出し内のすべての文字（Markdown）を白に変更して視認性を確保 */
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] h1, 
    [data-testid="stChatMessage"] h2, 
    [data-testid="stChatMessage"] h3 {{
        color: #ffffff !important;
    }}

    /* ストリーミング表示（文字の書き込み中）の文字色も白にする */
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {{
        color: #ffffff !important;
    }}

    /* リンク文字を明るい水色にして見やすくする */
    [data-testid="stChatMessage"] a {{
        color: #4af !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# アイコン画像の辞書定義
# ============================================================
AVATARS = {
    "user": USER_AVATAR_IMAGE,
    "assistant": AI_AVATAR_IMAGE
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
                    if chunk.choices:
                        delta = chunk.choices.delta
                        if hasattr(delta, "content") and delta.content:
                            yield delta.content

            full_response = st.write_stream(generate_chunks())

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response
                }
            )

        except Exception as e:
            st.error(f"エラーが発生しました。\n\n{e}")

# ============================================================
# 最下部へ自動スクロールするJavaScript
# ============================================================
if len(st.session_state.messages) > 0:
    components.html(
        """
        <script>
            function scrollToBottom() {
                const selectors = [
                    '[data-testid="stAppViewHeightContainer"]',
                    '[data-testid="stAppViewContainer"]',
                    '.stApp'
                ];
                selectors.forEach(selector => {
                    window.parent.document.querySelectorAll(selector).forEach(el => {
                        el.scrollTop = el.scrollHeight;
                    });
                });
            }
            setTimeout(scrollToBottom, 50);
        </script>
        """,
        height=0,
    )

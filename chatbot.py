import streamlit as st
from groq import Groq

# ページの設定
st.set_page_config(page_title="Cloud LLM Chat", page_icon="☁️")
st.title("最新クラウドチャットボット")

# 1. Streamlit SecretsからAPIキーを読み込む
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# クライアントの初期化
client = Groq(api_key=GROQ_API_KEY)

# 2. 会話履歴の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. 過去の会話履歴を描画
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. ユーザー入力の受付
if user_input := st.chat_input("メッセージを入力してください..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 5. Groq API を使ってストリーミング返答
    with st.chat_message("assistant"):
        try:
            # 💡 【重要】現在利用可能な有効なモデル名に修正します
            stream = client.chat.completions.create(
                model="openai/gpt-oss-120b",  # 高速・軽量な推奨モデル
                # より高性能なモデルを試したい場合は "openai/gpt-oss-120b" も利用可能です
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            # ジェネレータ関数を作成して st.write_stream に渡す
            def generate_chunks():
                for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta

            # 安全にストリーミング表示し、戻り値として全文を取得
            full_response = st.write_stream(generate_chunks())
            
            # 履歴に追加
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

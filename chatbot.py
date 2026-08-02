import streamlit as st
from groq import Groq

# ページの設定
st.set_page_config(page_title="Cloud LLM Chat", page_icon="☁️")
st.title("Llama 3.1 クラウドチャットボット")

# 1. Streamlit Secrets（または環境変数）からAPIキーを読み込む
# 修正後
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
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Groqで Llama 3.1 (70b または 8b) を呼び出す
            # 利用可能な最新の正確なモデル名はGroq公式ドキュメントをご確認ください
            stream = client.chat.completions.create(
                # または、軽量で高速なモデルにしたい場合
                model="openai/gpt-oss-20b", 
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            for chunk in stream:
                # 差分テキストを取得して結合
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

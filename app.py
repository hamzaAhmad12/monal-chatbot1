from __future__ import annotations

import streamlit as st

from rag.retriever import answer_question

st.set_page_config(page_title="Monal Peshawar", page_icon="🍽️")

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 50% -10%, rgba(0, 210, 255, .20), transparent 34%),
            linear-gradient(135deg, #030b18 0%, #0b1f3a 52%, #07152a 100%);
        color: #f4f7fb;
        overflow: hidden;
    }
    .stApp::before {
        content: "";
        position: fixed;
        inset: -20%;
        pointer-events: none;
        opacity: .18;
        background-image:
            linear-gradient(90deg, transparent 96%, #00d9ff 97%, transparent 98%),
            linear-gradient(0deg, transparent 96%, #00d9ff 97%, transparent 98%);
        background-size: 42px 42px;
        transform: perspective(420px) rotateX(58deg) translateY(16%);
        transform-origin: center bottom;
        animation: matrix-drift 14s linear infinite;
    }
    @keyframes matrix-drift {
        from { background-position: 0 0; }
        to { background-position: 0 42px; }
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 760px; padding-top: 3rem; position: relative; z-index: 1; }
    h1 {
        color: #ffffff;
        text-shadow: 0 0 10px rgba(0, 217, 255, .65), 0 4px 0 #075078;
        margin-bottom: .2rem;
    }
    .welcome-text {
        color: #58e6ff;
        font-size: 1.05rem;
        letter-spacing: .04em;
        text-shadow: 0 0 12px rgba(0, 217, 255, .55);
        margin-bottom: 2rem;
    }
    .suggestion-title {
        color: #b9c9dc;
        margin-bottom: .45rem;
    }
    div.stButton > button {
        color: #d9f8ff;
        background: rgba(19, 55, 91, .72);
        border: 1px solid rgba(73, 211, 255, .28);
        border-radius: 8px;
        text-align: left;
        transition: all .2s ease;
    }
    div.stButton > button:hover {
        color: #ffffff;
        border-color: #58e6ff;
        box-shadow: 0 0 14px rgba(0, 217, 255, .35);
        transform: translateY(-1px);
    }
    [data-testid="stChatMessage"] {
        background: linear-gradient(145deg, rgba(24, 64, 103, .92), rgba(8, 27, 53, .94));
        border: 1px solid rgba(73, 211, 255, .28);
        border-radius: 10px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, .28), inset 0 1px rgba(255, 255, 255, .08);
    }
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li { color: #ffffff !important; }
    [data-testid="stChatInput"] textarea {
        color: #111827 !important;
        background: #ffffff !important;
        border-radius: 10px !important;
    }
    [data-testid="stChatInput"] textarea::placeholder { color: #111827 !important; opacity: 1; }
    [data-testid="stChatInput"] { border-color: #426487; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Monal Peshawar")
st.markdown('<div class="welcome-text">Welcome to Monal Peshawar</div>', unsafe_allow_html=True)

suggestions = [
    "What is the address of Monal Peshawar?",
    "What is included in the buffet?",
    "Show me vegetarian options.",
]
st.markdown('<div class="suggestion-title">Suggested questions</div>', unsafe_allow_html=True)
for index, suggestion in enumerate(suggestions):
    if st.button(f"• {suggestion}", key=f"suggestion_{index}", use_container_width=True):
        st.session_state["chat_input"] = suggestion

if "messages" not in st.session_state:
    st.session_state.messages = []
question = st.chat_input("Ask about Monal Peshawar", key="chat_input")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("Searching the knowledge base..."):
        try:
            answer, _ = answer_question(question)
        except (FileNotFoundError, RuntimeError) as error:
            answer = str(error)
        except Exception:
            answer = "The AI service could not answer right now. Check your Groq model and API key."
    st.session_state.messages.append({"role": "assistant", "content": answer})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

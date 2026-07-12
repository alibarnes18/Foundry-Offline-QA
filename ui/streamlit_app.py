import os
import sys

# Add the project root directory to sys.path to allow importing from 'src'
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

import streamlit as st
from src.llm import generate_answer_local_api
from src.retrieval import get_top_chunks
from src.prompts import build_messages

st.set_page_config(page_title="Local RAG Assistant", page_icon="🤖")
st.title("🤖 Local RAG Assistant")
st.caption("Powered by Foundry Local + Azure OpenAI — runs offline")

if "history" not in st.session_state:
    st.session_state.history = []

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Ask a question..."):
    st.session_state.history.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            chunks = get_top_chunks(question)
            messages = build_messages(chunks, question)
            answer = generate_answer_local_api(messages)

        st.markdown(answer)

        with st.expander("Sources"):
            for i, chunk in enumerate(chunks, start=1):
                st.markdown(f"**{i}. {chunk.get('source', 'Unknown')}**")
                st.write(chunk.get("chunk", ""))
                st.divider()

    st.session_state.history.append({"role": "assistant", "content": answer})
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import threading
from src.llm import get_llm_manager, LLM_ALIAS
from src.retrieval import get_top_chunks
from src.prompts import build_messages

st.set_page_config(page_title="Local RAG Assistant", page_icon="🤖")
st.title("🤖 Local RAG Assistant")
st.caption("Powered by Foundry Local + Azure OpenAI — runs offline")

@st.cache_resource
def load_model():
    manager = get_llm_manager()
    model = manager.catalog.get_model(LLM_ALIAS)
    model.download(lambda p: None)
    model.load()
    return model.get_chat_client()

if "client" not in st.session_state:
    with st.spinner("Loading model..."):
        st.session_state.client = load_model()

if "history" not in st.session_state:
    st.session_state.history = []

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def run_inference(client, messages, result):
    try:
        response = client.complete_chat(messages)
        answer = response.choices[0].message.content
        if "<think>" in answer and "</think>" in answer:
            answer = answer.split("</think>")[-1].strip()
        result["answer"] = answer
    except Exception as e:
        result["error"] = str(e)

if question := st.chat_input("Ask a question..."):
    st.session_state.history.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            chunks = get_top_chunks(question)
            messages = build_messages(chunks, question)
            
            result = {}
            thread = threading.Thread(
                target=run_inference,
                args=(st.session_state.client, messages, result)
            )
            thread.start()
            thread.join(timeout=120)
            
            if "error" in result:
                answer = f"Error: {result['error']}"
            elif "answer" in result:
                answer = result["answer"]
            else:
                answer = "Timeout — model did not respond."

        st.markdown(answer)

        with st.expander("Sources"):
            for i, chunk in enumerate(chunks, start=1):
                st.markdown(f"**{i}. {chunk.get('source', 'Unknown')}**")
                st.write(chunk.get("chunk", ""))
                st.divider()

    st.session_state.history.append({"role": "assistant", "content": answer})
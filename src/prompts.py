SYSTEM_PROMPT = """You are a helpful assistant.
Answer question ONLY using the context provided below.
If the answer is not in the context, say "I don't have information about this."
Always mention which source you used: e.g. (Source: filename.txt)
Be concise and clear.  """

def build_messages(context_chunks: list, user_question: str) -> list:
    context_text = "\n\n".join(
        f"[Source: {c['source']}]\n {c['chunk']}"
        for c in context_chunks
    )

    return [
        {
            "role": "system",
             "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"Context:\n{context_text}\n\nQuestion. {user_question}"
        }
    ]


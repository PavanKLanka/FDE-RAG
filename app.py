from src.rag import answer_question
import streamlit as st

st.set_page_config(page_title="Support AI", page_icon="🤖")


st.title("🤖 Support AI")
st.caption("AI Assistant")


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Ask a question about CloudDesk..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # RAG call will happen here
    result = answer_question(prompt)
    answer = result["answer"]
    intent = result.get("intent", "unknown")

    if result["sources"]:
        st.markdown("### 📚 Sources")

        for source in result["sources"]:
            st.write(f"- {source}")

    if result["handoff"]:
        st.warning("👤 Human support is recommended.")

    with st.chat_message("assistant"):
        st.markdown(answer)
        st.caption(f"Intent: {intent.upper()}")

    st.session_state.messages.append({"role": "assistant", "content": answer})

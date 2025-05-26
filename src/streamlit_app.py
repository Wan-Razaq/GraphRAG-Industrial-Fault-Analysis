import streamlit as st
from chatbot_service import detect_language, generate_answer
from retriever import retriever

# Initialize session state on first load
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # will store tuples of (role, message)
if "latest_graph_data" not in st.session_state:
    st.session_state.latest_graph_data = None  # store graph nodes/edges for visualization

query = st.text_input("Your question:", value="", key="query_input")
if st.button("Send", type="primary"):
    if query.strip():
        lang = detect_language(query)
        retriever_result = retriever.search(query_text=query, top_k=3)
        # Iterate over each retrieved graph result:
        context_str = ""
        for item in retriever_result.items:
            meta = item.metadata
            if meta:
                location = meta.get("location", "")
                symptom = meta.get("symptom", "")
                reason = meta.get("reason", "")
                measure = meta.get("measure", "")

                context_str += f"Location: {location}\n"
                if symptom:
                    context_str += f"Symptom: {symptom}\n"
                if reason:
                    context_str += f"Reason: {reason}\n"
                if measure:
                    context_str += f"Measure: {measure}\n"
                context_str += "\n"
        if not context_str:
            context_str = "(No direct graph context found; relying on general knowledge.)"
        # generate answer
        answer = generate_answer(query, context_str, lang)
        # Append question and answer to chat history
        st.session_state.chat_history.append(("user", query))
        st.session_state.chat_history.append(("assistant", answer))

        # Prepare nodes and links for D3

# Display the conversation history
for role, message in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"**💬 User:** {message}")
    else:
        st.markdown(f"**🤖 Assistant:** {message}")

# New Conversation button
if st.button("Start New Conversation"):
    st.session_state.chat_history = []
    st.session_state.latest_graph_data = None
    st.experimental_rerun()  # refresh the app
    
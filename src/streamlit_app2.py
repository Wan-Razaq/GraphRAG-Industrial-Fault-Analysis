import streamlit as st
import streamlit.components.v1 as components
import json

from chatbot_service import detect_language, generate_answer
from retriever import retriever  # HybridCypherRetriever instance
from pathlib import Path

if "conversations" not in st.session_state:
    st.session_state.conversations = [{
    "title": "Conversation 1",
    "messages": [],
    "latest_graph": {"nodes": [], "links": []}
    }]
    st.session_state.current_conv_index = 0
    st.session_state.graph_panel_expanded = True

# Short-hand references
conversations = st.session_state.conversations
current_idx = st.session_state.current_conv_index
current_conv = conversations[current_idx]

# --- Sidebar: Conversation Navigation ---
st.sidebar.title("Conversations")
# List existing conversations with buttons for selection
for i, conv in enumerate(conversations):
    btn_label = conv["title"]
    if st.sidebar.button(btn_label, key=f"select_{i}"):
        # Update current conversation index when a title is clicked
        st.session_state.current_conv_index = i
        current_idx = i
        current_conv = conversations[i]
# Button to start a new conversation
if st.sidebar.button("Start New Conversation", key="new_conv"):
    new_index = len(conversations)
    conversations.append({
        "title": f"Conversation {new_index+1}",
        "messages": [],
        "latest_graph": {"nodes": [], "links": []}
    })
    st.session_state.current_conv_index = new_index
    current_idx = new_index
    current_conv = conversations[new_index]

# --- Main Interface (Center Panel) ---
st.title("Chatbot Assistant with Knowledge Graph Context")


# Initialize expand state if it doesn't exist yet
if "graph_expanded" not in st.session_state:
    st.session_state.graph_expanded = False

# Button at the top to expand/collapse
expand_button_label = "↔️ Expand Graph" if not st.session_state.graph_expanded else "↩️ Collapse Graph"
if st.button(expand_button_label, key="expand_graph"):
    st.session_state.graph_expanded = not st.session_state.graph_expanded

# Change layout dynamically based on state
if st.session_state.graph_expanded:
    chat_col, graph_col = st.columns([0.5, 0.5])  # Half-half expanded view
else:
    chat_col, graph_col = st.columns([0.7, 0.3])  # Default view

# Chat history and input in the chat_col
with chat_col:
    # Form for new question input
    with st.form(key="question_form", clear_on_submit=True):
        user_input = st.text_input("Ask a question:", placeholder="Type your question here...")
        submit_clicked = st.form_submit_button("Send")

    if submit_clicked and user_input:
        # 1. Detect language of the user input
        lang = detect_language(user_input)

        # 2. Retrieve relevant graph context using the retriever
        retriever_result = retriever.search(query_text=user_input, top_k=5)

        # 3. Prepare the concise context string for LLM prompt
        context_str = ""
        node_dict = {}
        links = []

        for item in retriever_result.items:
            meta = item.metadata
            if not meta:
                continue

            if meta.get("location_id") and meta.get("location"):
                node_dict[meta["location_id"]] = {"id": meta["location_id"], "label": meta["location"], "type": "location"}
            if meta.get("symptom_id") and meta.get("symptom"):
                node_dict[meta["symptom_id"]] = {"id": meta["symptom_id"], "label": meta["symptom"], "type": "symptom"}
                if meta.get("location_id"):
                    links.append({"source": meta["location_id"], "target": meta["symptom_id"], "type": "HAS_FAULT"})
            if meta.get("reason_id") and meta.get("reason"):
                node_dict[meta["reason_id"]] = {"id": meta["reason_id"], "label": meta["reason"], "type": "reason"}
                if meta.get("symptom_id"):
                    links.append({"source": meta["symptom_id"], "target": meta["reason_id"], "type": "CAUSED_BY"})
            if meta.get("measure_id") and meta.get("measure"):
                node_dict[meta["measure_id"]] = {"id": meta["measure_id"], "label": meta["measure"], "type": "measure"}
                if meta.get("symptom_id"):
                    links.append({"source": meta["symptom_id"], "target": meta["measure_id"], "type": "MITIGATED_BY"})

            snippet = ""
            if meta.get("location"):
                snippet += f"Location: {meta['location']}\n"
            if meta.get("symptom"):
                snippet += f"Symptom: {meta['symptom']}\n"
            if meta.get("reason"):
                snippet += f"Reason: {meta['reason']}\n"
            if meta.get("measure"):
                snippet += f"Measure: {meta['measure']}\n"
            context_str += snippet + "\n"

        if not context_str:
            context_str = "(No direct graph context found; relying on general knowledge.)"

        # Use latest user language if conversation exists
        lang_used = lang
        for msg in reversed(current_conv["messages"]):
            if msg["role"] == "user" and "lang" in msg:
                lang_used = msg["lang"]
                break

        # Include previous messages plus current question
        conversation_so_far = current_conv["messages"] + [{"role": "user", "content": user_input}]
        answer = generate_answer(conversation_so_far, context_str, lang_used)

        # 5. Store conversation and graph data
        current_conv["messages"].append({"role": "user", "content": user_input, "lang": lang})
        current_conv["messages"].append({"role": "assistant", "content": answer})
        current_conv["latest_graph"] = {"nodes": list(node_dict.values()), "links": links}


    # 🔁 Now display messages AFTER the form and answer generation
    for msg in current_conv["messages"]:
        if msg["role"] == "user":
            st.markdown(f"**💬 User:** {msg['content']}")
        else:
            st.markdown(f"**🤖 Assistant:** {msg['content']}")

# --- Graph Visualization (Right Panel) ---
with graph_col:
    graph_data = current_conv.get("latest_graph", {"nodes": [], "links": []})
    if graph_data and graph_data.get("nodes"):
        template_path = Path("d3_graph.html")
        template = template_path.read_text()
        filled_template = template.replace("{{GRAPH_DATA_JSON}}", json.dumps(graph_data))
        components.html(filled_template, height=650, scrolling=True)

            
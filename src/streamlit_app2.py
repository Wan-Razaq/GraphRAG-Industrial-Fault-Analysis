import streamlit as st
import streamlit.components.v1 as components
import json

from utils.chatbot_service import detect_language, generate_answer
from utils.retriever import retriever  # HybridCypherRetriever instance
from pathlib import Path

st.set_page_config(layout="wide", page_title="Chatbot Fault Diagnosis Assistant with Knowledge Graph Context")

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
    chat_col, graph_col = st.columns([0.4, 0.6])  # Half-half expanded view
else:
    chat_col, graph_col = st.columns([0.7, 0.3])  # Default view

# Chat history and input in the chat_col
with chat_col:
    # 1. Handle input submission FIRST (before rendering messages)
    with st.form(key="chat_input_form", clear_on_submit=True):
        user_input = st.text_input(
            "Ask a question...",
            label_visibility="collapsed",
            placeholder="Ask your question here"
        )
        submit_clicked = st.form_submit_button("➤ Send")

    if submit_clicked and user_input:
        lang = detect_language(user_input)
        retriever_result = retriever.search(query_text=user_input, top_k=5)

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

        lang_used = lang
        for msg in reversed(current_conv["messages"]):
            if msg["role"] == "user" and "lang" in msg:
                lang_used = msg["lang"]
                break

        conversation_so_far = current_conv["messages"] + [{"role": "user", "content": user_input}]
        answer = generate_answer(conversation_so_far, context_str, lang_used)

        current_conv["messages"].append({"role": "user", "content": user_input, "lang": lang})
        current_conv["messages"].append({"role": "assistant", "content": answer})
        current_conv["latest_graph"] = {"nodes": list(node_dict.values()), "links": links}

    # 2. Now render the messages AFTER the state update
    with st.container():
        st.markdown('<div id="chat-box" class="chat-container">', unsafe_allow_html=True)

        # Group messages into pairs: (user, assistant)
        pairs = []
        msgs = current_conv["messages"]
        i = 0
        while i < len(msgs) - 1:
            if msgs[i]["role"] == "user" and msgs[i+1]["role"] == "assistant":
                pairs.append((msgs[i], msgs[i+1]))
                i += 2
            else:
                i += 1  # Skip broken pair

        # Show latest pair first, but user before assistant in each pair
        for user_msg, assistant_msg in reversed(pairs):
            st.markdown(f'<div class="chat-message">💬 <strong>User:</strong> {user_msg["content"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-message">🤖 <strong>Assistant:</strong> {assistant_msg["content"]}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# --- Graph Visualization (Right Panel) ---
with graph_col:
    graph_data = current_conv.get("latest_graph", {"nodes": [], "links": []})
    if graph_data and graph_data.get("nodes"):
        template_path = Path("src/d3_graph.html")
        template = template_path.read_text()
        filled_template = template.replace("{{GRAPH_DATA_JSON}}", json.dumps(graph_data))
        components.html(filled_template, height=650, scrolling=True)

            
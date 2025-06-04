import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd

from utils.chatbot_service import detect_language, generate_answer
from utils.retriever import retriever  # HybridCypherRetriever instance
from pathlib import Path

st.set_page_config(layout="wide", page_title="Chatbot Fault Diagnosis Assistant with Knowledge Graph Context")

# Session State and Conversations
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

# --- Main Interface (Single Page, no columns) ---
# Helper to generate graph, cypher, and table for a given answer
def graph_context_content(graph_data, cypher_query, table_rows):
    tabs = st.tabs(["Graph Visualization", "Cypher Query", "Extracted Entities Table"])
    neo4j_browser_url = "https://9ce13d2b.databases.neo4j.io/browser/"
    with tabs[0]:
        if graph_data and graph_data.get("nodes"):
            template_path = Path("src/d3_graph.html")
            template = template_path.read_text()
            filled_template = template.replace("{{GRAPH_DATA_JSON}}", json.dumps(graph_data))
            components.html(filled_template, height=400, scrolling=True)
        else:
            st.info("No graph data found for this question.")
    with tabs[1]:
        if cypher_query and cypher_query.strip():
            st.code(cypher_query, language="cypher")
            st.markdown(
                f"Copy-paste this Cypher query to visualize the graph &nbsp; &rarr; [Open Graph Database]({neo4j_browser_url})",
                unsafe_allow_html=True
            )
        else:
            st.info("No Cypher query found.")
    with tabs[2]:
        st.markdown("#### Extracted Graph Entities")
        if table_rows:
            def style_row(row):
                color = 'background-color: #d9d9d9;' if row["Entity"] == "FaultLocation" else ''
                return [color, color]
            styled_df = pd.DataFrame(table_rows)
            st.dataframe(styled_df.style.apply(style_row, axis=1), use_container_width=True)
        else:
            st.info("No graph entities found for this question.")

# Display conversation history with expanders/tabs under assistant replies
i = 0
pair_idx = 0
while i < len(current_conv["messages"]):
    if current_conv["messages"][i]["role"] == "user":
        # Show user message
        with st.chat_message("user"):
            st.markdown(f" {current_conv['messages'][i]['content']}")
        # Check if next message is assistant
        if i + 1 < len(current_conv["messages"]) and current_conv["messages"][i+1]["role"] == "assistant":
            # Show assistant message
            with st.chat_message("assistant"):
                st.markdown(f" {current_conv['messages'][i+1]['content']}")
            # Attach expanders/tabs with answer context
            if "latest_graphs" in current_conv and pair_idx < len(current_conv["latest_graphs"]):
                graph_data = current_conv["latest_graphs"][pair_idx].get("graph_data", {"nodes": [], "links": []})
                cypher_query = current_conv["latest_graphs"][pair_idx].get("cypher_query", "")
                table_rows = current_conv["latest_graphs"][pair_idx].get("table_rows", [])
                with st.expander("Show Knowledge Graph Context", expanded=False):
                    graph_context_content(graph_data, cypher_query, table_rows)
            pair_idx += 1
        i += 2
    else:
        i += 1


# Persistent input at bottom (no st.form needed)
user_input = st.chat_input("Ask your question here...")
    
if user_input:
    table_rows = []
    lang = detect_language(user_input)
    retriever_result = retriever.search(query_text=user_input, top_k=3)
    
    context_str = ""
    node_dict = {}
    links = []
    table_set = set()

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
            if ( "FaultLocation", meta["location"]) not in table_set:
                table_rows.append({"Entity": "FaultLocation", "Remarks": meta["location"]})
                table_set.add(( "FaultLocation", meta["location"] ))
        if meta.get("symptom"):
            snippet += f"Symptom: {meta['symptom']}\n"
            if ( "FaultSymptom", meta["symptom"]) not in table_set:
                table_rows.append({"Entity": "FaultSymptom", "Remarks": meta["symptom"]})
                table_set.add(( "FaultSymptom", meta["symptom"] ))
        if meta.get("reason"):
            snippet += f"Reason: {meta['reason']}\n"
            if ( "FaultReason", meta["reason"]) not in table_set:
                table_rows.append({"Entity": "FaultReason", "Remarks": meta["reason"]})
                table_set.add(( "FaultReason", meta["reason"] ))
        if meta.get("measure"):
            snippet += f"Measure: {meta['measure']}\n"
            if ( "FaultMeasure", meta["measure"]) not in table_set:
                table_rows.append({"Entity": "FaultMeasure", "Remarks": meta["measure"]})
                table_set.add(( "FaultMeasure", meta["measure"] ))
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

    # Collect all element IDs for Cypher query
    node_ids = [f"'{node['id']}'" for node in node_dict.values()]
    id_list_str = ", ".join(node_ids)

    # Prepare Cypher query string for copy-paste
    cypher_query = f"""
    MATCH (n)
    WHERE elementId(n) IN [{id_list_str}]
    OPTIONAL MATCH (n)-[r]->(m)
    WHERE elementId(m) IN [{id_list_str}]
    RETURN n, r, m
    """
    # Ensure latest_graphs is in sync
    if "latest_graphs" not in current_conv:
        current_conv["latest_graphs"] = []
    current_conv["latest_graphs"].append({
        "graph_data": {"nodes": list(node_dict.values()), "links": links},
        "cypher_query": cypher_query,
        "table_rows": table_rows
    })
    st.rerun()




            
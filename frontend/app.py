import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from agents.graph import app as graph_app
from agents.query_cache import (
    build_conversation_context,
    database_revision,
    invoke_with_response_cache,
    is_cacheable_response,
    make_response_cache_key,
    response_cache,
)

_MAX_SESSION_HISTORY = 50

load_dotenv()

st.set_page_config(page_title="DB Assistant", layout="wide")
st.title("Database Assistant")

if "history" not in st.session_state:
    st.session_state.history = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())
if "schema_context" not in st.session_state:
    st.session_state.schema_context = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None

left, right = st.columns([1, 2])

with left:
    st.subheader("History")
    if not st.session_state.history:
        st.caption("No questions yet.")
    for item in reversed(st.session_state.history):
        st.markdown(f"**{item['question']}**")
        st.caption(item["explanation"])
        st.divider()

with right:
    result = st.session_state.last_result
    if result:
        with st.expander("Generated SQL", expanded=False):
            st.code(result.get("generated_sql", ""), language="sql")

        if result.get("query_result"):
            st.dataframe(pd.DataFrame(result["query_result"]), use_container_width=True)

        st.write(result.get("explanation", ""))
        if result.get("response_cache_hit"):
            st.caption("Reused cached response")
        elif result.get("sql_cache_hit"):
            st.caption("Reused cached query results")

        if result.get("should_chart") and result.get("chart_config"):
            cfg = result["chart_config"]
            df = pd.DataFrame(result["query_result"])
            x, y = cfg.get("x_column"), cfg.get("y_column")
            if x and y and x in df.columns and y in df.columns:
                chart_fn = px.bar if cfg.get("chart_type") == "bar" else px.line
                fig = chart_fn(df, x=x, y=y, title=cfg.get("chart_title", ""))
                st.plotly_chart(fig, use_container_width=True)

question = st.chat_input("Ask a question about the database...")

if question:
    conversation_context = build_conversation_context(
        st.session_state.history,
        question,
    )
    revision = database_revision()
    cached_schema = st.session_state.schema_context
    cache_key = (
        make_response_cache_key(
            question,
            cached_schema,
            revision,
            conversation_id=st.session_state.conversation_id,
            conversation_context=conversation_context,
        )
        if cached_schema
        else None
    )
    request_state = {
        "user_question": question,
        "schema_context": cached_schema,
        "conversation_id": st.session_state.conversation_id,
        "conversation_context": conversation_context,
        "retry_count": 0,
        "sql_error": None,
        "generated_sql": "",
        "query_result": [],
        "explanation": "",
        "should_chart": False,
        "chart_config": None,
    }

    with st.spinner("Thinking..."):
        state = invoke_with_response_cache(
            response_cache,
            cache_key,
            request_state,
            graph_app.invoke,
        )

    st.session_state.schema_context = state.get(
        "schema_context", st.session_state.schema_context
    )
    if cache_key is None and is_cacheable_response(state):
        resolved_key = make_response_cache_key(
            question,
            st.session_state.schema_context,
            database_revision(),
            conversation_id=st.session_state.conversation_id,
            conversation_context=conversation_context,
        )
        if resolved_key is not None:
            response_cache.set(resolved_key, state)

    st.session_state.last_result = state
    st.session_state.history.append(
        {
            "question": question,
            "explanation": state.get("explanation", ""),
            "generated_sql": state.get("generated_sql", ""),
            "columns": state.get("query_columns", []),
            "sample_rows": state.get("query_result", [])[:5],
            "successful": is_cacheable_response(state),
        }
    )
    st.session_state.history = st.session_state.history[-_MAX_SESSION_HISTORY:]
    st.rerun()

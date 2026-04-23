import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from agents.graph import app as graph_app

load_dotenv()

st.set_page_config(page_title="DB Assistant", layout="wide")
st.title("Database Assistant")

if "history" not in st.session_state:
    st.session_state.history = []
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

        if result.get("should_chart") and result.get("chart_config"):
            cfg = result["chart_config"]
            df  = pd.DataFrame(result["query_result"])
            x, y = cfg.get("x_column"), cfg.get("y_column")
            if x and y and x in df.columns and y in df.columns:
                chart_fn = px.bar if cfg.get("chart_type") == "bar" else px.line
                fig = chart_fn(df, x=x, y=y, title=cfg.get("chart_title", ""))
                st.plotly_chart(fig, use_container_width=True)

question = st.chat_input("Ask a question about the database...")

if question:
    with st.spinner("Thinking..."):
        state = graph_app.invoke({
            "user_question":  question,
            "schema_context": st.session_state.schema_context,
            "retry_count":    0,
            "sql_error":      None,
            "generated_sql":  "",
            "query_result":   [],
            "explanation":    "",
            "should_chart":   False,
            "chart_config":   None,
        })

    st.session_state.schema_context = state.get("schema_context", st.session_state.schema_context)
    st.session_state.last_result    = state
    st.session_state.history.append({
        "question":    question,
        "explanation": state.get("explanation", ""),
    })
    st.rerun()

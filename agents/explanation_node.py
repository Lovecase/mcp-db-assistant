import json

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from agents.state import AgentState

load_dotenv()

_llm = ChatGroq(model="openai/gpt-oss-20b")

_PROMPT = ChatPromptTemplate.from_template(
    'You are a data analyst assistant. A user asked: "{user_question}"\n\n'
    "The query returned {row_count} rows. Here is a sample (up to 10 rows):\n"
    "{sample_rows}\n\n"
    "Please:\n"
    "1. Write a 2-3 sentence plain-English summary of what the data shows.\n"
    "2. Decide if a bar chart or line chart would help visualise this data.\n\n"
    "Respond ONLY in this JSON format:\n"
    "{{\n"
    '  "explanation": "...",\n'
    '  "should_chart": true or false,\n'
    '  "chart_type": "bar" or "line" or null,\n'
    '  "x_column": "column name for x axis or null",\n'
    '  "y_column": "column name for y axis or null",\n'
    '  "chart_title": "short title or null"\n'
    "}}"
)


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(inner)
    return json.loads(text.strip())


def explanation_node(state: AgentState) -> dict:
    query_result = state.get("query_result", [])

    chain = _PROMPT | _llm
    response = chain.invoke(
        {
            "user_question": state["user_question"],
            "row_count": len(query_result),
            "sample_rows": json.dumps(query_result[:10], indent=2),
        }
    )

    try:
        parsed = _parse_json(response.content)
        explanation = parsed.get("explanation", response.content)
        should_chart = bool(parsed.get("should_chart", False))
        chart_config = (
            {
                "chart_type": parsed.get("chart_type"),
                "x_column": parsed.get("x_column"),
                "y_column": parsed.get("y_column"),
                "chart_title": parsed.get("chart_title"),
            }
            if should_chart
            else None
        )
    except (json.JSONDecodeError, ValueError):
        explanation = response.content
        should_chart = False
        chart_config = None

    return {
        "explanation": explanation,
        "should_chart": should_chart,
        "chart_config": chart_config,
    }

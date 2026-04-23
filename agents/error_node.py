from agents.state import AgentState


def error_node(state: AgentState) -> dict:
    return {
        "explanation": (
            "I was unable to generate a valid SQL query for your question after 3 attempts. "
            f"The last error was: {state.get('sql_error')}. "
            "Please try rephrasing your question."
        ),
        "should_chart": False,
        "chart_config": None,
    }

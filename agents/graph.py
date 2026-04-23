from langgraph.graph import END, StateGraph

from agents.error_node import error_node
from agents.explanation_node import explanation_node
from agents.query_node import query_node
from agents.schema_node import schema_node
from agents.state import AgentState


def route_after_query(state: AgentState) -> str:
    if state.get("sql_error"):
        if state.get("retry_count", 0) < 3:
            return "query_node"
        return "error_node"
    return "explanation_node"


def build_graph() -> StateGraph:
    g = StateGraph(AgentState)
    g.add_node("schema_node",     schema_node)
    g.add_node("query_node",      query_node)
    g.add_node("explanation_node", explanation_node)
    g.add_node("error_node",      error_node)
    g.set_entry_point("schema_node")
    g.add_edge("schema_node", "query_node")
    g.add_conditional_edges("query_node", route_after_query)
    g.add_edge("explanation_node", END)
    g.add_edge("error_node", END)
    return g.compile()


app = build_graph()

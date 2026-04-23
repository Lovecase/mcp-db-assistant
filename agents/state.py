from typing import Optional, TypedDict


class AgentState(TypedDict):
    user_question:  str
    schema_context: str
    generated_sql:  str
    query_result:   list[dict]
    sql_error:      Optional[str]
    retry_count:    int
    explanation:    str
    should_chart:   bool
    chart_config:   Optional[dict]

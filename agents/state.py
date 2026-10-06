from typing import NotRequired, TypedDict


class AgentState(TypedDict):
    user_question: str
    schema_context: str
    generated_sql: str
    query_result: list[dict]
    sql_error: str | None
    retry_count: int
    explanation: str
    should_chart: bool
    chart_config: dict | None
    conversation_id: NotRequired[str]
    conversation_context: NotRequired[list[dict]]
    query_columns: NotRequired[list[str]]
    sql_cache_hit: NotRequired[bool]
    response_cache_hit: NotRequired[bool]

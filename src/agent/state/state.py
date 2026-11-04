from typing import TypedDict, List, Dict, Optional


class SocraticAgentState(TypedDict):
    # data about the problem
    file_path: str
    function_name: Optional[str]
    line_number: int
    line_content: str
    code_snippet: str
    error_type: str
    error_name: str

    # Metrics Event Tracking ID (UUID in database)
    event_id: Optional[str]

    # root cause of the problem
    root_cause: str

    # chat with user
    dialogue_history: List[Dict[str, str]]

    # dose problem is solved or not !
    is_solved: bool

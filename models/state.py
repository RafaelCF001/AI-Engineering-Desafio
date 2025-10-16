from typing import TypedDict, List, Dict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    results: Dict[str, str]
    taxas: List[float]
    report: str

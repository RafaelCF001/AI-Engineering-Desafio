
from nodes.planner_node import SragAgent
from nodes.final_review_node import final_review_node
from models.state import AgentState
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from typing import List, Dict





def graph() -> StateGraph:

    workflow = StateGraph(AgentState)

    from nodes.synthesizer_node import synthesizer_node

    workflow.add_node("srag_agent", SragAgent().execute)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("revisor", final_review_node)

    workflow.set_entry_point("srag_agent")

    workflow.add_edge("srag_agent", "synthesizer")
    workflow.add_edge("synthesizer", "revisor")

    def review_router(state: AgentState) -> str:
        """
        Routes workflow based on review result.
        If review is 'false', returns to srag_agent for revision; else, ends workflow.
        """
        review_result = state.get("results", {}).get("review", "true")
        if isinstance(review_result, str) and review_result.lower() == "false":
            return "srag_agent"
        return END

    workflow.add_conditional_edges(
        "revisor",
        review_router,
        {
            "srag_agent": "srag_agent",
            END: END
        }
    )

    app = workflow.compile()
    return app

import logging
from typing import List
from pydantic import BaseModel, Field
from typing_extensions import Literal
from langchain_core.prompts import ChatPromptTemplate
from agents.state import BRDWorkflowState, JobStatus
from agents.llm import get_llm

logger = logging.getLogger(__name__)

# Note: You can move these models into agents/state.py for architectural consistency
class Ticket(BaseModel):
    id: str = Field(description="Unique ticket ID like TICKET-01")
    req_id: str = Field(description="Match req_id to the requirement it comes from (e.g., REQ-01)")
    title: str = Field(description="Short ticket title")
    user_story: str = Field(description="As a [user], I want [goal] so that [benefit]")
    acceptance_criteria_summary: str = Field(description="One line description of done condition")
    story_points: int = Field(description="Fibonacci: 1, 2, 3, 5, 8, or 13")
    priority: Literal["high", "medium", "low"] = Field(description="Priority level")

class Tickets(BaseModel):
    items: List[Ticket] = Field(description="List of all generated tickets")

def get_ticket_chain():
    llm = get_llm()
    structured_llm = llm.with_structured_output(Tickets)
    
    system_prompt = """You are a product manager.
    Convert the following requirements into Jira-style user story tickets.
    One ticket per requirement."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "REQUIREMENTS:\n{requirements}")
    ])
    
    return prompt | structured_llm

def ticket_node(state: BRDWorkflowState) -> dict:
    brd_id = state.get('brd_id', 'Unknown')
    logger.info(f"[{brd_id}] ticket_node started")
    print("WORKER RUNNING — GENERATING TICKETS")

    if state.get("status") == JobStatus.FAILED:
        return {}

    try:
        ticket_chain = get_ticket_chain()
        
        # Format requirements list into a readable string for the LLM
        reqs = state.get("requirements", [])
        reqs_string = "\n".join([f"ID: {r.id}, Title: {r.title}, Desc: {r.description}" for r in reqs])
        
        print("Calling LLM to convert requirements to Jira tickets...")
        tickets_data = ticket_chain.invoke({"requirements": reqs_string})
        
        logger.info(f"[{brd_id}] ticket_node done — {len(tickets_data.items)} tickets generated")
        print(f"Successfully generated {len(tickets_data.items)} tickets")
        
        return {
            "tickets": tickets_data.items,
            "current_node": "ticket_node",
        }
        
    except Exception as e:
        logger.error(f"[{brd_id}] ticket_node error: {e}")
        return {
            "status": JobStatus.FAILED,
            "errors": (state.get("errors") or []) + [f"ticket_node: {e}"],
        }
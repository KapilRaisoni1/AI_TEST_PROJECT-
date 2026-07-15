import logging
from langchain_core.prompts import ChatPromptTemplate
from agents.state import BRDWorkflowState, Requirements, JobStatus
from agents.llm import get_llm

logger = logging.getLogger(__name__)

def get_requirement_chain():
    llm = get_llm()
    structured_llm = llm.with_structured_output(Requirements)
    
    system_prompt = """You are a senior business analyst.
    Extract ALL requirements from the provided Business Requirements Document (BRD).
    Do NOT skip any requirement, even implied ones."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "BRD DOCUMENT:\n{brd_text}")
    ])
    
    return prompt | structured_llm

def requirement_node(state: BRDWorkflowState) -> dict:
    brd_id = state.get('brd_id', 'Unknown')
    logger.info(f"[{brd_id}] requirement_node started")
    print("ORCHESTRATOR RUNNING — EXTRACTING REQUIREMENTS")

    try:
        req_chain = get_requirement_chain()
        
        # Supporting both 'full_text' and 'content' keys for compatibility
        brd_text = state.get("content", state.get("full_text", ""))
        
        print("Calling LLM for requirements extraction...")
        requirements_data = req_chain.invoke({"brd_text": brd_text})
        
        logger.info(f"[{brd_id}] requirement_node done — {len(requirements_data.items)} requirements extracted")
        print(f"Successfully extracted {len(requirements_data.items)} requirements")
        
        return {
            "requirements": requirements_data.items,
            "current_node": "requirement_node",
        }
        
    except Exception as e:
        logger.error(f"[{brd_id}] requirement_node error: {e}")
        return {
            "status": JobStatus.FAILED,
            "errors": (state.get("errors") or []) + [f"requirement_node: {e}"],
        }
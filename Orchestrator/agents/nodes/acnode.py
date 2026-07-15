import logging
from langchain_core.prompts import ChatPromptTemplate
from agents.state import WorkerState, RequirementAC
from agents.llm import get_llm

logger = logging.getLogger(__name__)

def get_ac_chain():
    llm = get_llm()
    structured_llm = llm.with_structured_output(RequirementAC)
    
    system_prompt = """You are a senior QA engineer.
    Generate Given/When/Then acceptance criteria for this requirement.
    Cover happy paths AND edge/negative cases. Be specific.

    Requirement ID: {req_id}
    Title: {title}
    Description: {description}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{req_id},{title},{description}")
    ])
    
    return prompt | structured_llm

def ac_node(state: WorkerState) -> dict:
    req = state["requirement"]
    logger.info(f"[{req.id}] ac_node started")
    print(f"WORKER ASSIGNED.. WORKING ON {req.title}")
    
    ac_chain = get_ac_chain()
    
    acceptance_criterias = ac_chain.invoke({
        "req_id": req.id,
        "title": req.title,
        "description": req.description
    })
    
    return {"completed_ac": [acceptance_criterias]}
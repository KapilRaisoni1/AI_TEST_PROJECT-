import logging
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langchain_core.prompts import ChatPromptTemplate

from agents.state import (
    BRDWorkflowState, WorkerState, TestWorkerState,
    Requirements, RequirementAC
)
from agents.llm import get_llm
from config import settings
from github import Github

logger = logging.getLogger(__name__)


def push_to_github(content: str, filename: str):
    g = Github(settings.GITHUB_TOKEN)
    repo = g.get_repo(f"{settings.GIT_REPO_OWNER}/{settings.GIT_REPO_NAME}")
    path = f"testcases/{filename}"
    try:
        repo.create_file(
            path=path,
            message=f"Add test case: {filename}",
            content=content,
            branch=settings.GIT_BASE_BRANCH,
        )
        print(f"Pushed to GitHub: {path}")
    except Exception as e:
        print(f"GitHub push failed for {filename}: {e}")


def orchestrator(state: BRDWorkflowState):
    print("ORCHESTRATOR RUNNING — EXTRACTING REQUIREMENTS")

    llm = get_llm()
    structured_llm = llm.with_structured_output(Requirements)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior business analyst.
Extract ALL requirements from the BRD below.
For each requirement provide: id (REQ-01 format), title, description, type, priority.

BRD:
{content}"""),
        ("human", "{content}"),
    ])

    chain = prompt | structured_llm
    requirements = chain.invoke({"content": state["content"]})

    print(f"Extracted {len(requirements.items)} requirements")
    return {"requirements": requirements.items}


def assign_ac_workers(state: BRDWorkflowState):
    print("ASSIGNING AC WORKERS")
    return [
        Send("ac_worker", {"requirement": req, "completed_ac": []})
        for req in state["requirements"]
    ]


def ac_worker(state: WorkerState):
    req = state["requirement"]
    print(f"AC WORKER: {req.title}")

    llm = get_llm()
    structured_llm = llm.with_structured_output(RequirementAC)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior QA engineer.
Generate Given/When/Then acceptance criteria for this requirement.
Cover happy paths AND edge/negative cases. Be specific.

Requirement ID: {req_id}
Title: {title}
Description: {description}"""),
        ("human", "{req_id},{title},{description}"),
    ])

    chain = prompt | structured_llm
    ac = chain.invoke({
        "req_id": req.id,
        "title": req.title,
        "description": req.description,
    })

    return {"completed_ac": [ac]}


def synthesizer(state: BRDWorkflowState):
    print("SYNTHESIZING AC")
    ac_dict = {}
    for ac in state["completed_ac"]:
        ac_dict[ac.req_id] = ac.criterias
    return {"all_ac": ac_dict}


def assign_test_workers(state: BRDWorkflowState):
    print("ASSIGNING TEST WORKERS")
    sends = []
    for ac in state["completed_ac"]:
        req = next(r for r in state["requirements"] if r.id == ac.req_id)
        sends.append(Send("test_worker", {
            "requirement": req,
            "acceptance_criteria": ac,
        }))
    return sends


def test_worker(state: TestWorkerState):
    req = state["requirement"]
    ac = state["acceptance_criteria"]
    print(f"TEST WORKER: {req.title}")

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior QA automation engineer.
Write a complete runnable pytest test script for the given requirement and acceptance criteria.

Use the `requests` library. Use pytest fixtures for base_url and auth_headers (from conftest.py).
Return ONLY valid Python code. No markdown. No explanation.

Title: {title}
Description: {description}
Acceptance Criteria: {criteria}"""),
        ("human", "{title},{description},{criteria}"),
    ])

    chain = prompt | llm
    response = chain.invoke({
        "title": req.title,
        "description": req.description,
        "criteria": [f"Given {c.given} When {c.when} Then {c.then}" for c in ac.criterias],
    })

    safe_title = req.title.lower().replace(" ", "_").replace("/", "_")
    filename = f"test_{safe_title}.py"

    push_to_github(content=response.content, filename=filename)

    return {"completed_tests": [{"req_id": req.id, "filename": filename, "code": response.content}]}


def synthesize_tests(state: BRDWorkflowState):
    print("SYNTHESIZING TEST CASES")
    return {"all_tests": {t["req_id"]: t["code"] for t in state["completed_tests"]}}


def build_graph():
    graph = StateGraph(BRDWorkflowState)

    graph.add_node("orchestrator", orchestrator)
    graph.add_node("ac_worker", ac_worker)
    graph.add_node("synthesizer", synthesizer)
    graph.add_node("test_worker", test_worker)
    graph.add_node("synthesize_tests", synthesize_tests)

    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges("orchestrator", assign_ac_workers, ["ac_worker"])
    graph.add_edge("ac_worker", "synthesizer")
    graph.add_conditional_edges("synthesizer", assign_test_workers, ["test_worker"])
    graph.add_edge("test_worker", "synthesize_tests")
    graph.add_edge("synthesize_tests", END)

    return graph.compile()


workflow = build_graph()
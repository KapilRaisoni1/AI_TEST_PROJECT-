import logging
from github import Github
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from agents.state import TestWorkerState
from agents.llm import get_llm

logger = logging.getLogger(__name__)

def push_to_github(content: str, filename: str):
    try:
        g = Github(settings.GITHUB_TOKEN)
        repo = g.get_repo(f"{settings.GIT_REPO_OWNER}/{settings.GIT_REPO_NAME}")
        path = f"testcases/{filename}"
        repo.create_file(
            path=path,
            message=f"Add test case for: {filename.split('.')[0]}",
            content=content,
            branch=settings.GIT_BASE_BRANCH,
        )
        print(f"Test Case Pushed to GitHub: {path}")
    except Exception as e:
        logger.error(f"Not able to push {filename} due to {e}")
        print(f"Not able to push {filename} due to {e}")

def get_test_chain():
    llm = get_llm()
    
    system_prompt = """You are a senior QA automation engineer.
    Write a complete runnable pytest test script for the given requirement and acceptance criteria.

    Use the `requests` library. Use pytest fixtures for base_url and auth_headers (from conftest.py).
    Return ONLY valid Python code. No markdown. No explanation. No code fences.

    Title: {title}
    Description: {description}
    Acceptance Criteria: 
    {criteria}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{title},{description},{criteria}")
    ])
    
    return prompt | llm

def testcase_node(state: TestWorkerState) -> dict:
    req = state["requirement"]
    ac = state["acceptance_criteria"]
    
    logger.info(f"[{req.id}] testcase_node started")
    print(f"TEST WORKER: Generating test for {req.title}")

    test_chain = get_test_chain()
    
    # Format the Pydantic models directly into readable strings
    ac_list = [f"Given {c.given} When {c.when} Then {c.then}" for c in ac.criterias]
    ac_string = "\n".join(ac_list)

    response = test_chain.invoke({
        "title": req.title,
        "description": req.description,
        "criteria": ac_string
    })

    safe_title = req.title.lower().replace(" ", "_").replace("/", "_")
    filename = f"test_{safe_title}.py"
    
    print(f"Generated Test Cases for {req.title}\nNow Pushing to GitHub.....")
    push_to_github(content=response.content, filename=filename)

    return {"completed_tests": [{"req_id": req.id, "filename": filename, "code": response.content}]}
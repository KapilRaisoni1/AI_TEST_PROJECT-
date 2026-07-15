import os
import operator
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

# Import your state models
from agents.state import BRDWorkflowState
# Import your refactored nodes
from agents.nodes.requirementnode import requirement_node
from agents.nodes.ticketnode import ticket_node
from agents.nodes.acnode import ac_node
from agents.nodes.testcasenode import testcase_node

# Load environment variables (.env)
load_dotenv()

# --- Edge Routing Functions ---
def assign_ac_workers(state: BRDWorkflowState):
    print("ROUTING: Assigning parallel AC workers...")
    # Send each requirement to a parallel AC worker
    return [
        Send("ac_node", {"requirement": req}) 
        for req in state.get("requirements", [])
    ]

def assign_test_workers(state: BRDWorkflowState):
    print("ROUTING: Assigning parallel Test Case workers...")
    sends = []
    for ac in state.get("completed_ac", []):
        # Match the AC back to its original requirement
        req = next((r for r in state["requirements"] if r.id == ac.req_id), None)
        if req:
            sends.append(Send("testcase_node", {
                "requirement": req,
                "acceptance_criteria": ac
            }))
    return sends

def synthesize_ac(state: BRDWorkflowState):
    # Simply pass the state forward after AC parallel nodes join
    print("ROUTING: AC generation complete. Moving to Test Case generation...")
    return state

# --- Build and Compile the Graph ---
def build_graph():
    graph = StateGraph(BRDWorkflowState)

    # Add Nodes
    graph.add_node("requirement_node", requirement_node)
    graph.add_node("ticket_node", ticket_node)
    graph.add_node("ac_node", ac_node)
    graph.add_node("synthesize_ac", synthesize_ac)
    graph.add_node("testcase_node", testcase_node)

    # Wire Edges
    graph.add_edge(START, "requirement_node")
    graph.add_edge("requirement_node", "ticket_node")
    
    # Conditional edge to fan-out to parallel AC workers
    graph.add_conditional_edges("ticket_node", assign_ac_workers, ["ac_node"])
    
    # Fan-in from AC workers
    graph.add_edge("ac_node", "synthesize_ac")
    
    # Conditional edge to fan-out to parallel Test Case workers
    graph.add_conditional_edges("synthesize_ac", assign_test_workers, ["testcase_node"])
    
    # Fan-in to the end
    graph.add_edge("testcase_node", END)

    return graph.compile()

# --- Execution Entry Point ---
if __name__ == "__main__":
    # 1. Read the Mock BRD
    with open("mock_brd.md", "r") as file:
        brd_content = file.read()

    # 2. Compile Graph
    app = build_graph()
    
    print("Starting AI Test Generation Pipeline...\n" + "="*40)

    # 3. Invoke Workflow
    initial_state = {
        "content": brd_content,
        "brd_id": "MOCK-BRD-001"
    }
    
    final_state = app.invoke(initial_state)
    
    print("\n" + "="*40 + "\nPipeline Complete! Check your GitHub repository for the pushed test files.")
"""
Quick test — runs just the requirement node without FastAPI or Celery.
Use this to verify your setup works before the full pipeline.
"""

import fitz
from agents.state import JobStatus
from agents.nodes.requirementnode import requirement_node

# Point this to any PDF you have
PDF_PATH = "sample_brd.pdf"

# Extract text
doc = fitz.open(PDF_PATH)
full_text = "\n\n".join(page.get_text() for page in doc)
doc.close()

# Build a mock state
mock_state = {
    "brd_id":              "test-001",
    "filename":            "sample_brd.pdf",
    "full_text":           full_text,
    "page_count":          doc.page_count,
    "requirements":        None,
    "tickets":             None,
    "acceptance_criteria": None,
    "test_cases":          None,
    "test_scripts":        None,
    "validation":          None,
    "git_status":          None,
    "current_node":        None,
    "status":              JobStatus.PROCESSING,
    "errors":              [],
}

# Run just the requirement node
print("Running requirement node...")
result = requirement_node(mock_state)

# Print output
import json
print(f"\nStatus: {result['status']}")
print(f"Requirements extracted: {len(result.get('requirements') or [])}")
print(json.dumps(result.get("requirements"), indent=2))
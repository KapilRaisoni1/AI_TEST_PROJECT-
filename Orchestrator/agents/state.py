import operator
from enum import Enum
from typing import TypedDict, Annotated, List
from pydantic import BaseModel, Field
from typing_extensions import Literal

class JobStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Requirement(BaseModel):
    id:          str = Field(description="Unique ID like REQ-01")
    title:       str = Field(description="Short title")
    description: str = Field(description="Full requirement description")
    type:        Literal["functional", "non_functional"] = Field(description="Requirement type")
    priority:    Literal["high", "medium", "low"] = Field(description="Priority level")

class Requirements(BaseModel):
    items: List[Requirement] = Field(description="List of all requirements")

class AcceptanceCriteria(BaseModel):
    given: str = Field(description="Given condition")
    when:  str = Field(description="When action")
    then:  str = Field(description="Then expected result")

class RequirementAC(BaseModel):
    req_id:   str = Field(description="Requirement ID this AC belongs to")
    title:    str = Field(description="Requirement title")
    criterias: List[AcceptanceCriteria] = Field(description="List of AC for this requirement")

class BRDWorkflowState(TypedDict, total=False):
    brd_id:       str
    content:      str                 
    requirements: List[Requirement]
    tickets:      list
    completed_ac: Annotated[list, operator.add]
    all_ac:       dict                   
    completed_tests: Annotated[list, operator.add]
    all_tests:    dict
    status:       JobStatus
    errors:       list
    current_node: str

class WorkerState(TypedDict):
    requirement: Requirement
    completed_ac: Annotated[list, operator.add]

class TestWorkerState(TypedDict):
    requirement:         Requirement
    acceptance_criteria: RequirementAC
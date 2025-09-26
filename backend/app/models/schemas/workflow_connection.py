from pydantic import BaseModel
from typing import Optional

class WorkflowConnectionBase(BaseModel):
    workflow_id: int
    from_step_id: int
    to_step_id: int
    condition: Optional[str] = None

class WorkflowConnectionCreate(WorkflowConnectionBase):
    pass

class WorkflowConnectionUpdate(BaseModel):
    from_step_id: Optional[int] = None
    to_step_id: Optional[int] = None
    condition: Optional[str] = None

class WorkflowConnection(WorkflowConnectionBase):
    id: int

    class Config:
        from_attributes = True  

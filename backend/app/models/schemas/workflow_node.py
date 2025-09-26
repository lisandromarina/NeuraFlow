from pydantic import BaseModel
from typing import Optional, Dict


class WorkflowNodeBase(BaseModel):
    workflow_id: int
    node_id: int
    name: str
    position_x: float
    position_y: float
    custom_config: Optional[Dict] = None


# For creating a node (input only)
class WorkflowNodeCreate(WorkflowNodeBase):
    pass


# For returning a node (output with id)
class WorkflowNode(WorkflowNodeBase):
    id: int

    class Config:
        from_attributes  = True

class WorkflowNodeUpdate(BaseModel):
    """
    Schema for updating an existing WorkflowNode.
    Only fields that can change are included.
    """
    name: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    custom_config: Optional[Dict] = None


class WorkflowNodeSchema(WorkflowNodeBase):
    """
    Schema returned by API responses.
    """
    id: int

    model_config = {
        "from_attributes": True  # ✅ enables from_orm()
    }
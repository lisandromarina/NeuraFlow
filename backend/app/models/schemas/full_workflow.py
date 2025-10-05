from pydantic import BaseModel
from typing import Optional, List

class WorkflowConnectionSchema(BaseModel):
    id: int
    from_step_id: int
    to_step_id: int
    condition: Optional[str] = None

    model_config = {"from_attributes": True}


class WorkflowNodeFullSchema(BaseModel):
    id: int
    workflow_id: int
    node_id: int
    name: str
    position_x: float
    position_y: float
    custom_config: Optional[dict] = None
    node_type: Optional[str] = None  # from Node.type

    model_config = {"from_attributes": True}


class WorkflowFullSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    nodes: List[WorkflowNodeFullSchema] = []
    connections: List[WorkflowConnectionSchema] = []
    is_active: bool

    model_config = {"from_attributes": True}

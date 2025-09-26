from pydantic import BaseModel
from typing import Optional

class WorkflowNodeBase(BaseModel):
    name: str
    workflow_id: int
    position_x: int
    position_y: int
    custom_config: Optional[dict] = {}

class WorkflowNodeCreate(BaseModel):
    workflow_id: int
    node_id: int
    name: str
    position_x: float   # <-- float instead of int
    position_y: float   # <-- float instead of int
    custom_config: dict | None = None

    model_config = {"from_attributes": True}  # for from_orm

class WorkflowNodeUpdate(BaseModel):
    name: Optional[str]
    position_x: float   # <-- float instead of int
    position_y: float
    custom_config: Optional[dict]

class WorkflowNodeSchema(BaseModel):
    id: int
    workflow_id: int
    node_id: int
    name: str
    position_x: float  # <-- change to float
    position_y: float  # <-- change to float
    custom_config: dict | None = None

    model_config = {"from_attributes": True}

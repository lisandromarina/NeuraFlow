from pydantic import BaseModel
from typing import Dict, Optional

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
    name: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    custom_config: Optional[Dict] = None

class WorkflowNodeSchema(BaseModel):
    id: int
    workflow_id: int
    node_id: int
    name: str
    position_x: float  # <-- change to float
    position_y: float  # <-- change to float
    custom_config: dict | None = None

    node_type: Optional[str] = None
    node_category: Optional[str] = None 

    model_config = {"from_attributes": True}

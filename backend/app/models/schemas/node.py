from pydantic import BaseModel
from typing import Optional, Dict


class NodeBase(BaseModel):
    name: str
    type: str
    global_config: Optional[Dict] = None


class NodeCreate(NodeBase):
    pass


class NodeUpdate(BaseModel):
    type: Optional[str] = None
    global_config: Optional[Dict] = None


class NodeResponse(NodeBase):
    id: int

    class Config:
        from_attributes = True  # ORM mode

from pydantic import BaseModel
from typing import Optional

class Workflow(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None

    model_config = {
        "from_attributes": True  # <-- required for from_orm() in Pydantic v2
    }


class WorkflowUpdate(BaseModel):
    name: str
    description: Optional[str] = None
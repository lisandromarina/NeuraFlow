from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base  # assuming you have base.py with Base = declarative_base()

class WorkflowConnection(Base):
    __tablename__ = "workflow_connections"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    from_step_id = Column(Integer, ForeignKey("workflow_nodes.id"), nullable=False)
    to_step_id = Column(Integer, ForeignKey("workflow_nodes.id"), nullable=False)
    condition = Column(String, nullable=True)  # e.g., "approved", "rejected"

    # Relationships
    workflow = relationship("WorkflowDB", back_populates="connections")
    from_step = relationship(
        "WorkflowNode", 
        foreign_keys=[from_step_id], 
        back_populates="outgoing_connections"
    )
    to_step = relationship(
        "WorkflowNode", 
        foreign_keys=[to_step_id], 
        back_populates="incoming_connections"
    )

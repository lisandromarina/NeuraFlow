# workflow_node.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base

class WorkflowNode(Base):
    __tablename__ = "workflow_nodes"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    name = Column(String, nullable=False)
    position_x = Column(Float, nullable=False)  # Horizontal position
    position_y = Column(Float, nullable=False) 
    custom_config = Column(JSON, nullable=True)

    workflow = relationship("WorkflowDB", back_populates="nodes")
    node = relationship("Node", back_populates="workflow_nodes")

    # Correct string references for foreign_keys
    outgoing_connections = relationship(
        "WorkflowConnection",
        foreign_keys="WorkflowConnection.from_step_id",
        back_populates="from_step"
    )
    incoming_connections = relationship(
        "WorkflowConnection",
        foreign_keys="WorkflowConnection.to_step_id",
        back_populates="to_step"
    )

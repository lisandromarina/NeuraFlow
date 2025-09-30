# node.py
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) 
    type = Column(String, nullable=False) 
    config_metadata = Column(JSON, nullable=False)

    # Relationships
    workflow_nodes = relationship("WorkflowNode", back_populates="node")

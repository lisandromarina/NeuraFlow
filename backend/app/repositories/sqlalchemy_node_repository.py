from sqlalchemy.orm import Session
from typing import List, Optional
from models.db_models.node_db import Node
from models.schemas.node import NodeCreate, NodeUpdate


class SqlAlchemyNodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_nodes(self, skip: int = 0, limit: int = 10) -> List[Node]:
        return self.db.query(Node).offset(skip).limit(limit).all()

    def get_node(self, node_id: int) -> Optional[Node]:
        return self.db.query(Node).filter(Node.id == node_id).first()

    def create_node(self, node_data: NodeCreate) -> Node:
        node = Node(**node_data.dict())
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        return node

    def update_node(self, node_id: int, node_data: NodeUpdate) -> Optional[Node]:
        node = self.get_node(node_id)
        if not node:
            return None
        for key, value in node_data.dict(exclude_unset=True).items():
            setattr(node, key, value)
        self.db.commit()
        self.db.refresh(node)
        return node

    def delete_node(self, node_id: int) -> bool:
        node = self.get_node(node_id)
        if not node:
            return False
        self.db.delete(node)
        self.db.commit()
        return True

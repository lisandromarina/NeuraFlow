from typing import List, Optional
from models.schemas.node import NodeCreate, NodeUpdate
from models.db_models.node_db import Node
from repositories.sqlalchemy_node_repository import SqlAlchemyNodeRepository


class NodeService:
    def __init__(self, repository: SqlAlchemyNodeRepository):
        self.repository = repository

    def list_nodes(self, skip: int = 0, limit: int = 10) -> List[Node]:
        return self.repository.list_nodes(skip=skip, limit=limit)

    def get_node(self, node_id: int) -> Optional[Node]:
        return self.repository.get_node(node_id)

    def create_node(self, node_data: NodeCreate) -> Node:
        return self.repository.create_node(node_data)

    def update_node(self, node_id: int, node_data: NodeUpdate) -> Optional[Node]:
        return self.repository.update_node(node_id, node_data)

    def delete_node(self, node_id: int) -> bool:
        return self.repository.delete_node(node_id)

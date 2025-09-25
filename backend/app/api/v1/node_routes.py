from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.schemas.node import NodeCreate, NodeUpdate, NodeResponse
from services.node_service import NodeService
from repositories.sqlalchemy_node_repository import SqlAlchemyNodeRepository
from dependencies import get_node_repository

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.get("/", response_model=List[NodeResponse])
def list_nodes(repo: SqlAlchemyNodeRepository = Depends(get_node_repository)):
    service = NodeService(repo)
    return service.list_nodes()


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(node_id: int, repo: SqlAlchemyNodeRepository = Depends(get_node_repository)):
    service = NodeService(repo)
    node = service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.post("/", response_model=NodeResponse)
def create_node(node_data: NodeCreate, repo: SqlAlchemyNodeRepository = Depends(get_node_repository)):
    service = NodeService(repo)
    return service.create_node(node_data)


@router.put("/{node_id}", response_model=NodeResponse)
def update_node(
    node_id: int,
    node_data: NodeUpdate,
    repo: SqlAlchemyNodeRepository = Depends(get_node_repository)
):
    service = NodeService(repo)
    updated = service.update_node(node_id, node_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Node not found")
    return updated


@router.delete("/{node_id}")
def delete_node(node_id: int, repo: SqlAlchemyNodeRepository = Depends(get_node_repository)):
    service = NodeService(repo)
    success = service.delete_node(node_id)
    if not success:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"message": "Node deleted successfully"}

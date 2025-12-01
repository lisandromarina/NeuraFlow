# dependencies.py (or a new file, e.g., auth_dependencies.py)
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime
import os
from dependencies import get_db_session
from repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from repositories.sqlalchemy_workflow_repository import SqlAlchemyWorkflowRepository
from models.db_models.user_credentials_db import UserCredentialDB
from models.db_models.workflow_nodes import WorkflowNode
from models.db_models.workflow_db import WorkflowDB
from models.db_models.workflow_connections_db import WorkflowConnection
from sqlalchemy.orm import Session

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Missing environment variable: SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # login endpoint

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_session)
):
    """
    Dependency to get the current user from JWT token.
    Verifies token validity, checks expiration, and verifies user exists in database.
    Raises 401 if token is invalid, expired, or user doesn't exist.
    Returns user info with user_id and email.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token expired")
        
        # Get user info from token
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Verify user exists in database
        user_repo = SqlAlchemyUserRepository(db)
        db_user = user_repo.get_by_email(email)
        
        if not db_user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Verify user_id matches
        if db_user.id != user_id:
            raise HTTPException(status_code=401, detail="Token user mismatch")
        
        return {
            "user_id": user_id,
            "email": email,
            "username": email  # Keep for backward compatibility
        }
    except HTTPException:
        raise
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


# Authorization helper functions
def verify_workflow_ownership(
    workflow_id: int,
    current_user: dict,
    db: Session
):
    """
    Verifies that the current user owns the specified workflow.
    Raises 403 Forbidden if user doesn't own the workflow.
    Raises 404 Not Found if workflow doesn't exist.
    """
    
    workflow_repo = SqlAlchemyWorkflowRepository(db)
    workflow = workflow_repo.get_by_id(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden: You don't have access to this workflow")
    
    return workflow


def verify_credential_ownership(
    credential_id: int,
    current_user: dict,
    db: Session
):
    """
    Verifies that the current user owns the specified credential.
    Raises 403 Forbidden if user doesn't own the credential.
    Raises 404 Not Found if credential doesn't exist.
    """
    
    credential = db.query(UserCredentialDB).filter(UserCredentialDB.id == credential_id).first()
    
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    if credential.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden: You don't have access to this credential")
    
    return credential


def verify_workflow_node_ownership(
    workflow_node_id: int,
    current_user: dict,
    db: Session
):
    """
    Verifies that the current user owns the workflow that contains the specified workflow node.
    Raises 403 Forbidden if user doesn't own the workflow.
    Raises 404 Not Found if workflow node doesn't exist.
    """
    
    workflow_node = db.query(WorkflowNode).filter(WorkflowNode.id == workflow_node_id).first()
    
    if not workflow_node:
        raise HTTPException(status_code=404, detail="Workflow node not found")
    
    workflow = db.query(WorkflowDB).filter(WorkflowDB.id == workflow_node.workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden: You don't have access to this workflow node")
    
    return workflow_node


def verify_workflow_connection_ownership(
    connection_id: int,
    current_user: dict,
    db: Session
):
    """
    Verifies that the current user owns the workflow that contains the specified connection.
    Raises 403 Forbidden if user doesn't own the workflow.
    Raises 404 Not Found if connection doesn't exist.
    """
    
    connection = db.query(WorkflowConnection).filter(WorkflowConnection.id == connection_id).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Workflow connection not found")
    
    workflow = db.query(WorkflowDB).filter(WorkflowDB.id == connection.workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Forbidden: You don't have access to this workflow connection")
    
    return connection

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import workflow_routes
from api.v1 import auth_routes
from api.v1 import node_routes
from api.v1 import workflow_node_router
from api.v1 import workflow_connection_routes
from api.v1 import credentials_routes
from api.v1 import telegram_routes
from config import settings
import nodes  # SUPER NEEDED, IMPORTS AND REGISTER ALL THE NODES
from alembic.config import Config
from alembic import command

app = FastAPI()


@app.on_event("startup")
async def run_migrations():
    """Run database migrations on startup."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        # Log error but don't crash the app - migrations can be run manually
        print(f"Warning: Failed to run migrations on startup: {e}")
        print("Please run migrations manually with: alembic upgrade head")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Restricted to specific methods
    allow_headers=["Authorization", "Content-Type", "Accept"],  # Explicit allowed headers
    max_age=600,  # Cache preflight requests for 10 minutes
)

app.include_router(workflow_routes.router)
app.include_router(node_routes.router)
app.include_router(workflow_node_router.router)
app.include_router(workflow_connection_routes.router)
app.include_router(auth_routes.router)
app.include_router(credentials_routes.router) 
app.include_router(telegram_routes.router)


@app.get("/ping")
def health_check():
    return {"status": "ok"}

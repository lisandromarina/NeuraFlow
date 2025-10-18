import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import workflow_routes
from api.v1 import auth_routes
from api.v1 import node_routes
from api.v1 import workflow_node_router
from api.v1 import workflow_connection_routes
from api.v1 import google_routes
import nodes  # SUPER NEEDED, IMPORTS AND REGISTER ALL THE NODES

app = FastAPI()

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL")
if not frontend_url:
    raise ValueError("Missing environment variable: FRONTEND_URL")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(workflow_routes.router)
app.include_router(node_routes.router)
app.include_router(workflow_node_router.router)
app.include_router(workflow_connection_routes.router)
app.include_router(auth_routes.router)
app.include_router(google_routes.router) 


@app.get("/ping")
def health_check():
    return {"status": "ok"}

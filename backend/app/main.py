from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import workflow_routes
from api.v1 import node_routes
from api.v1 import workflow_node_router
from api.v1 import workflow_connection_routes
import nodes  # SUPER NEEDED, IMPORTS AND REGISTER ALL THE NODES

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.include_router(workflow_routes.router)
app.include_router(node_routes.router)
app.include_router(workflow_node_router.router)
app.include_router(workflow_connection_routes.router)


@app.get("/ping")
def health_check():
    return {"status": "ok"}

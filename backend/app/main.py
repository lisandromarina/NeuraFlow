from datetime import datetime, timedelta
from http.client import HTTPException
import os
from typing import Optional
from pydantic import BaseModel
from services.scheduler_service import SchedulerService
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


REDIS_URL = os.getenv("REDIS_URL", "redis://redis_db:6379/0")
scheduler = SchedulerService(redis_url=REDIS_URL)

class ScheduleRequest(BaseModel):
    workflow_id: int
    delay_seconds: int = 60
    interval_seconds: Optional[int] = None
    max_occurrences: Optional[int] = None
    until: Optional[str] = None
    context: Optional[dict] = None

@app.post("/redis")
def schedule_workflow(request: ScheduleRequest):
    try:
        start_time = datetime.utcnow() + timedelta(seconds=request.delay_seconds)
        scheduler.register_schedule(
            workflow_id=request.workflow_id,
            start_time=start_time,
            interval_seconds=request.interval_seconds,
            max_occurrences=request.max_occurrences,
            until=request.until,
            context=request.context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule workflow: {str(e)}")

    return {"message": f"Workflow {request.workflow_id} scheduled to run in {request.delay_seconds} seconds"}

@app.delete("/redis")
def root():
    """
    Register a workflow to run 1 minute from now
    """
    
    workflow_id = 1  # make sure this workflow exists in DB
    delay_seconds = 20  # 1 minute
    context = {"test_param": "hello_from_scheduler"}

    try:
        scheduler.delete_redis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule workflow: {str(e)}")

    return {"message": f"Workflow {workflow_id} scheduled to run in {delay_seconds} seconds"}

@app.get("/ping")
def health_check():
    return {"status": "ok"}

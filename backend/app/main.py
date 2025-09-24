from api.v1 import workflow_routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
def root():
    return {"message": "Hello from FastAPI backend!"}

@app.get("/ping")
def health_check():
    return {"status": "ok"}

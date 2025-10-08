from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import extraction_controller, query_controller

app = FastAPI(
    title="FastAPI Server",
    version="1.0.0",
    description="A simple FastAPI application with MVC architecture",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(extraction_controller.router)
app.include_router(query_controller.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI Server",
        "docs": "/docs",
    }

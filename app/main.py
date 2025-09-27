from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.document_extractor import DocumentExtractor

app = FastAPI(
    title="FastAPI Server",
    version="1.0.0",
    description="A simple FastAPI application with MVC architecture"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI Server",
        "docs": "/docs",
    }

@app.get("/extract")
async def extract_pdf():
    document_extractor = DocumentExtractor()
    pdf_path = '/Users/shamikbera/Documents/Projects/finance-advisor-rag/app/data/Millennia Credit Card Statement Sept 2025.pdf'
    result = document_extractor.extract_statement(pdf_path)
    print(result)
    
    

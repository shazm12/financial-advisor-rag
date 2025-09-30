from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.request import QueryRequest
from app.models.response import ExtractionResponse, QueryResponse, Status
from app.utils.chains.query_chain import QueryChain
from app.utils.create_embeddings import CreateEmbeddings
from app.utils.document_extractor import DocumentExtractor
from app.utils.redisdb import RedisDB
from app.utils.retreiver import Retreiver
from dotenv import load_dotenv
import os

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")


transactions_retreiver = Retreiver()
full_text_retreiver = Retreiver()
document_extractor = DocumentExtractor()
embedding = CreateEmbeddings()
redis_db = RedisDB(redis_url=REDIS_URL)

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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI Server",
        "docs": "/docs",
    }


@app.get("/extract", response_model=ExtractionResponse)
async def extract_pdf():
    try:
        redis_db.ping()
        redis_db.flush_memory()
        pdf_path = "/Users/shamikbera/Documents/Projects/finance-advisor-rag/app/data/Millennia Credit Card Statement Sept 2025.pdf"
        result = document_extractor.extract_statement(pdf_path)
        transactions_data = result["tables_data"]["transactions"]
        text_data = result["full_text"]
        trxn_rds = embedding.create_embeddings_for_transactions_data(
            transactions_data=transactions_data
        )
        text_rds = embedding.create_embeddings_for_text_data(
            text_data=text_data, index_name="full_text_data"
        )
        transactions_retreiver.set_retreiver(trxn_rds)
        full_text_retreiver.set_retreiver(text_rds)
        response = ExtractionResponse(
            status=Status.SUCCESS, description="Extraction Successful"
        )
        return response
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=400,
            detail=ExtractionResponse(
                status=Status.FAILURE, description=f"{e}"
            ).model_dump(mode="json"),
        )


@app.post("/query")
async def query(request: QueryRequest):
    try:
        query_chain = QueryChain(
            transactions_retriever=transactions_retreiver,
            full_text_retriever=full_text_retreiver,
        )
        answer = query_chain.invoke(request.prompt)
        response = QueryResponse(status=Status.SUCCESS, response=answer)
        return response
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=400,
            detail=ExtractionResponse(
                status=Status.FAILURE, description=f"{e}"
            ).model_dump(mode="json"),
        )

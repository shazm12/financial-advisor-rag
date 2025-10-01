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

from app.utils.session_manager import SessionManager

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")


document_extractor = DocumentExtractor()
embedding = CreateEmbeddings()
session_manager = SessionManager()
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
        session_id = session_manager.create_sesssion()
        pdf_path = "/Users/shamikbera/Documents/Projects/finance-advisor-rag/app/data/Millennia Credit Card Statement Sept 2025.pdf"
        result = document_extractor.extract_statement(pdf_path)
        transactions_data = result["tables_data"]["transactions"]
        text_data = result["full_text"]
        trxn_rds = embedding.create_embeddings_for_transactions_data(
            transactions_data=transactions_data, session_id=session_id
        )
        text_rds = embedding.create_embeddings_for_text_data(
            text_data=text_data, index_name="full_text_data", session_id=session_id
        )
        transactions_retreiver = Retreiver(rds=trxn_rds)
        full_text_retreiver = Retreiver(rds=text_rds)
        session_manager.add_retreivers_to_session(
            session_id,
            {
                "transactions_retreiver": transactions_retreiver,
                "full_text_retreiver": full_text_retreiver,
            },
        )
        response = ExtractionResponse(
            status=Status.SUCCESS,
            description="Extraction Successful",
            session_id=session_id,
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
        session_id = request.session_id
        if not session_manager.session_exists(session_id):
            raise HTTPException(
                status_code=400,
                detail=QueryResponse(
                    status=Status.FAILURE,
                    response="",
                    description="Session does not exist",
                    session_id=session_id,
                ).model_dump(mode="json"),
            )
        transactions_retreiver = session_manager.get_session_retreivers_by_id(
            session_id
        )["transactions_retreiver"]
        full_text_retreiver = session_manager.get_session_retreivers_by_id(session_id)[
            "full_text_retreiver"
        ]
        query_chain = QueryChain(
            transactions_retriever=transactions_retreiver,
            full_text_retriever=full_text_retreiver,
        )
        answer = query_chain.invoke(request.prompt)
        response = QueryResponse(
            status=Status.SUCCESS, session_id=session_id, response=answer
        )
        return response
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=400,
            detail=ExtractionResponse(
                status=Status.FAILURE, description=f"{e}", session_id=session_id
            ).model_dump(mode="json"),
        )

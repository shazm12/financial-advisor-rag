# app/controllers/extraction_controller.py
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from app.models.response import ExtractionResponse, Status
from app.utils.create_embeddings import CreateEmbeddings
from app.utils.dependencies import (
    get_document_extractor,
    get_embedding,
    get_session_manager,
    get_redis_db
)
from app.utils.document_extractor import DocumentExtractor
from app.utils.redisdb import RedisDB
from app.utils.retreiver import Retreiver
from app.utils.session_manager import SessionManager

router = APIRouter(prefix="/api/extraction", tags=["extraction"])


@router.post("/process", response_model=ExtractionResponse)
async def process_document_extraction(
    pdf_path: str,
    redis_db: Annotated[RedisDB, Depends(get_redis_db)],
    session_manager: Annotated[SessionManager, Depends(get_session_manager)],
    document_extractor: Annotated[DocumentExtractor, Depends(get_document_extractor)],
    embedding: Annotated[CreateEmbeddings, Depends(get_embedding)]
) -> ExtractionResponse:
    """
    Extract and process PDF document to create embeddings

    Args:
        pdf_path: Path to the PDF file to process

    Returns:
        ExtractionResponse with status and session ID
    """
    try:
        redis_db.ping()
        redis_db.flush_memory()

        session_id = session_manager.create_sesssion()

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

        return ExtractionResponse(
            status=Status.SUCCESS,
            description="Extraction Successful",
            session_id=session_id,
        )

    except Exception as e:
        print(f"Error in extraction: {e}")
        raise HTTPException(
            status_code=400,
            detail=ExtractionResponse(
                status=Status.FAILURE, description=str(e)
            ).model_dump(mode="json"),
        )

# app/controllers/extraction_controller.py
from typing import Annotated, Dict, final
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from app.models.response import ExtractionResponse, Status
from app.utils.create_embeddings import CreateEmbeddings
from app.utils.dependencies import (
    get_document_extractor,
    get_embedding,
    get_session_manager,
    get_redis_db,
)
from app.utils.document_extractor import DocumentExtractor
from app.utils.redisdb import RedisDB
from app.utils.retreiver import Retreiver
from app.utils.session_manager import SessionManager
import shutil
import tempfile
import os
import logging

router = APIRouter(prefix="/api/extraction", tags=["extraction"])
logger = logging.getLogger(__name__)

@router.post("/process", response_model=ExtractionResponse)
async def process_document_extraction(
    file: Annotated[UploadFile, File()],
    redis_db: Annotated[RedisDB, Depends(get_redis_db)],
    session_manager: Annotated[SessionManager, Depends(get_session_manager)],
    document_extractor: Annotated[DocumentExtractor, Depends(get_document_extractor)],
    embedding: Annotated[CreateEmbeddings, Depends(get_embedding)],
) -> ExtractionResponse:
    """
    Extract and process PDF document to create embeddings

    Args:
        file: PDF file to process (must be PDF format, max 10MB)
        redis_db: Redis database instance for storing embeddings
        session_manager: Session manager for handling user sessions
        document_extractor: Document extraction utility
        embedding: Embedding creation utility

    Returns:
        ExtractionResponse with status and session ID

    Raises:
        HTTPException: If file validation fails or processing errors occur
    """
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit"
        )
    
    logger.info(f"Starting document extraction for file: {file.filename}")

    fd, temp_path = tempfile.mkstemp(
        suffix=file.filename, prefix="finance-rag-file-upload-"
    )

    try:
        with os.fdopen(fd, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
        
        await file.close()
        logger.info(f"File saved to temporary location: {temp_path}")

        redis_db.ping()
        redis_db.flush_memory()

        session_id = session_manager.create_sesssion()
        logger.info(f"Created session: {session_id}")

        result = document_extractor.extract_statement(temp_path)
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in document extraction: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during extraction: {str(e)}"
        )
        
    finally:
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        else:
            raise HTTPException(
                status_code=500,
                detail="Internal server error during extraction"
            )
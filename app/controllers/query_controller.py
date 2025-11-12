from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from app.models.request import QueryRequest
from app.models.response import QueryResponse, Status
from app.utils.dependencies import get_session_manager
from fastapi.responses import StreamingResponse
from app.utils.session_manager import SessionManager
from app.utils.chains.query_chain import QueryChain


router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query_document(
    request: QueryRequest,
    session_manager: Annotated[SessionManager, Depends(get_session_manager)],
) -> StreamingResponse:
    """
    Query the extracted document using natural language

    Args:
        request: QueryRequest containing session_id and prompt
        session_manager: Injected SessionManager instance
        QueryChain: Injected QueryChain class

    Returns:
        QueryResponse with the answer to the query

    Raises:
        HTTPException: If session doesn't exist or query fails
    """
    try:
        session_id = request.session_id
        if not session_manager.session_exists(session_id):
            raise HTTPException(
                status_code=404,
                detail=QueryResponse(
                    status=Status.FAILURE,
                    response="",
                    description="Session does not exist",
                    session_id=session_id,
                ).model_dump(mode="json"),
            )

        retrievers = session_manager.get_session_retreivers_by_id(session_id)
        transactions_retreiver = retrievers["transactions_retreiver"]
        full_text_retreiver = retrievers["full_text_retreiver"]

        query_chain = QueryChain(
            transactions_retriever=transactions_retreiver,
            full_text_retriever=full_text_retreiver,
        )

        return StreamingResponse(
            query_chain.generate_response(request.prompt),
            media_type="text/event-stream"
        )

    except HTTPException:
        raise

    except Exception as e:
        print(f"Error in query execution: {e}")
        raise HTTPException(
            status_code=400,
            detail=QueryResponse(
                status=Status.FAILURE,
                response="",
                description=f"Query failed: {str(e)}",
                session_id=request.session_id,
            ).model_dump(mode="json"),
        )

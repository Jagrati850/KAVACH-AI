"""
KAVACH AI — RAG Advisory API Router
Exposes query endpoints for checking official cybercrime, MHA, CERT-In, and RBI guides.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.config import get_settings
from app.dependencies import CurrentUser
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.ai.rag.engine import RAGEngine

router = APIRouter()
rag_engine = RAGEngine()
settings = get_settings()


@router.post("/query", response_model=RAGQueryResponse)
async def query_advisories(
    payload: RAGQueryRequest,
    current_user: CurrentUser,
):
    """
    RAG Search Query Endpoint.
    Searches matching Cyber Advisories from RBI, CERT-In, and MHA.
    Returns synthesized advice and verified source references.
    """
    if not settings.rag_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG Advisory service is currently disabled in configuration.",
        )

    try:
        results = rag_engine.query(payload.query)
        return RAGQueryResponse(**results)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query RAG engine: {str(e)}"
        )

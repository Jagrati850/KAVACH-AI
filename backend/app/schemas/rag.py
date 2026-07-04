"""
KAVACH AI — Schemas for RAG Module
Pydantic model structures for input queries and retrieved advisory outputs.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    """Request payload for government advisory lookup."""
    query: str = Field(..., min_length=3, max_length=500, description="The security question or scenario to search against government advisories.")


class RetrievedSource(BaseModel):
    """Source tracking metadata for transparency."""
    title: str = Field(..., description="Document title")
    source: str = Field(..., description="Issuing government agency (e.g. MHA, CERT-In, RBI)")
    document_type: str = Field(..., description="Type of document (Advisory, Guideline, Directive)")
    relevance_score: float = Field(..., description="Matching similarity confidence score")
    url: Optional[str] = Field(None, description="Official portal link to source document")


class RAGQueryResponse(BaseModel):
    """Response returned containing matching advisory summaries and key tasks."""
    query: str
    answer: str = Field(..., description="Synthesized plain-text answer directly addressing search parameters.")
    key_actions: List[str] = Field(..., description="Actionable bullet points for the citizen to safeguard themselves.")
    retrieved_sources: List[RetrievedSource] = Field(default_factory=list, description="List of primary and secondary government advisories found.")

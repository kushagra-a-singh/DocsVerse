from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class Citation(BaseModel):
    document_id: str
    document_name: str
    page: Optional[int] = None
    paragraph: Optional[int] = None
    text: Optional[str] = None

class DocumentQueryResponse(BaseModel):
    document_id: str
    document_name: str
    extracted_answer: str
    citations: List[Citation]
    relevance_score: Optional[float] = None

class ThemeIdentification(BaseModel):
    theme_name: str
    description: str
    supporting_documents: List[str]
    confidence_score: Optional[float] = None

class SynthesizedResponse(BaseModel):
    query: str
    answer: str
    themes: List[ThemeIdentification]
    document_responses: List[DocumentQueryResponse]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class QueryRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None
    max_documents: int = 10
    include_citations: bool = True
    citation_level: str = "document"

class QueryResponse(BaseModel):
    query: str
    document_responses: List[DocumentQueryResponse] = []
    synthesized_response: Optional[SynthesizedResponse] = None
    
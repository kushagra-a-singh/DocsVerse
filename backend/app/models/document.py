from datetime import datetime
from enum import Enum as PyEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DocumentStatus(PyEnum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    ERROR = "ERROR"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    file_path = Column(String)
    file_type = Column(String)
    document_type = Column(String, nullable=True)
    author = Column(String, nullable=True)
    date = Column(String, nullable=True)
    upload_date = Column(DateTime)
    status = Column(
        Enum(
            DocumentStatus,
            values_callable=lambda obj: [e.value for e in obj],
            name="documentstatus",
            create_constraint=True,
            validate_strings=True,
        )
    )
    page_count = Column(Integer, default=0)
    error = Column(String, nullable=True)


class DocumentBase(BaseModel):
    """Base document model with common fields"""

    name: str
    document_type: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Model for document creation"""

    id: str
    file_path: str
    file_type: str
    upload_date: str
    status: str = DocumentStatus.UPLOADED.value  
    page_count: int = 0
    error: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Model for document updates"""

    name: Optional[str] = None
    document_type: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    status: Optional[str] = None
    page_count: Optional[int] = None
    error: Optional[str] = None


class DocumentResponse(BaseModel):
    """Model for document responses"""

    id: str
    name: str
    status: str
    document_type: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    upload_date: Optional[str] = None
    page_count: Optional[int] = None
    file_type: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None


class DocumentList(BaseModel):
    """Model for document list responses"""

    documents: List[DocumentResponse]
    total: int


class DocumentPage(BaseModel):
    """Model for document page content"""

    document_id: str
    page_number: int
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    """Model for document chunks used in vector storage"""

    id: str  
    document_id: str
    chunk_number: int
    content: str
    page_number: Optional[int] = None
    paragraph_number: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

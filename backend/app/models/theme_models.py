import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database import Base  
from pydantic import BaseModel, Field, validator
from sqlalchemy import (  
    JSON,
    Column,
    DateTime,
    Float,
    String,
)
from sqlalchemy.dialects.sqlite import (
    JSON as SQLiteJSON,  
)


class ThemeBase(BaseModel):
    """Base model shared by Pydantic theme models"""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    keywords: Optional[List[str]] = Field(default_factory=list, max_items=20)
    document_ids: List[str] = Field(default_factory=list)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator("keywords", each_item=True)
    def validate_keywords(cls, v):
        if len(v) > 50:
            raise ValueError("Keyword too long (max 50 chars)")
        return v.lower()


class ThemeCreate(ThemeBase):
    """Model for theme creation"""
    pass


class ThemeUpdate(BaseModel):
    """Model for theme updates"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    keywords: Optional[List[str]] = Field(None, max_items=20)
    document_ids: Optional[List[str]] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = None


class Theme(Base):
    """SQLAlchemy Theme model"""

    __tablename__ = "themes"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    keywords = Column(JSON().with_variant(SQLiteJSON(), "sqlite"), default=list)
    document_ids = Column(JSON().with_variant(SQLiteJSON(), "sqlite"), default=list)
    confidence_score = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True
    )
    metadata_ = Column(JSON().with_variant(SQLiteJSON(), "sqlite"), default=dict)


class ThemeResponse(BaseModel):
    """Response model for themes"""

    id: str
    name: str
    description: str
    keywords: Optional[List[str]] = None
    document_ids: List[str]
    confidence_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata_")

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}
        populate_by_name = True


class ThemeList(BaseModel):
    """Paginated theme list response"""

    themes: List[ThemeResponse]
    total: int
    skip: int = 0
    limit: int = 100


class ThemeAnalysisRequest(BaseModel):
    """Request model for theme analysis"""

    document_ids: List[str] = Field(..., min_items=1)
    min_confidence: float = Field(0.7, ge=0.1, le=0.99)
    max_themes: int = Field(10, ge=1, le=50)
    analysis_type: str = Field("default", pattern="^(default|detailed|quick)$")


class ThemeAnalysisResponse(BaseModel):
    """Response model for theme analysis"""

    themes: List[ThemeResponse]
    document_count: int
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: float
    warnings: List[str] = Field(default_factory=list)

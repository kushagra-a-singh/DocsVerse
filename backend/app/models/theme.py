from datetime import datetime
from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field, validator

class ThemeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    keywords: List[str] = Field(default_factory=list, max_items=20)
    document_ids: List[str] = Field(default_factory=list)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('keywords', each_item=True)
    def validate_keywords(cls, v):
        if len(v) > 50:
            raise ValueError("Keyword too long (max 50 chars)")
        return v.lower()

class ThemeCreate(ThemeBase):
    pass

class ThemeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    keywords: Optional[List[str]] = Field(None, max_items=20)
    document_ids: Optional[List[str]] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    metadata: Optional[Dict[str, Any]] = None

    @validator('name', pre=True, always=True)
    def validate_name(cls, v):
        if v is not None and len(v) > 100:
            raise ValueError("Name too long (max 100 chars)")
        return v

    @validator('description', pre=True, always=True)
    def validate_description(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError("Description too long (max 500 chars)")
        return v

class Theme(ThemeBase):
    id: str
    version: int = Field(default=1, description="Version number for optimistic concurrency control")
    created_at: datetime
    updated_at: datetime

class ThemeResponse(Theme):
    pass

class ThemeList(BaseModel):
    themes: List[ThemeResponse]
    total: int

class ThemeAnalysisRequest(BaseModel):
    """Request model for theme analysis"""
    document_ids: List[str] = Field(..., min_items=1,
                                  description="List of document IDs to analyze")
    min_confidence: float = Field(0.7, ge=0.1, le=0.99,
                                description="Minimum confidence threshold")
    max_themes: int = Field(10, ge=1, le=50,
                           description="Maximum number of themes to return")
    analysis_type: Literal["default", "detailed", "quick"] = Field("default",
                               description="Type of analysis to perform")

class ThemeAnalysisResponse(BaseModel):
    themes: List[ThemeResponse]
    document_count: int
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict)

import logging
from typing import List, Optional

from app.models.query import QueryRequest
from app.models.theme_models import (
    ThemeAnalysisRequest,
    ThemeAnalysisResponse,
    ThemeCreate,
    ThemeList,
    ThemeResponse,
    ThemeUpdate,
)
from app.services.llm_service import LLMService
from app.services.theme_identifier import ThemeIdentifier
from app.services.vector_store import VectorStore
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Query,
    status,
)

router = APIRouter(tags=["themes"])
logger = logging.getLogger(__name__)
theme_identifier = ThemeIdentifier()
llm_service = LLMService()
vector_store = VectorStore()


async def get_documents_by_ids(document_ids: List[str]):
    """Helper function to get documents from VectorStore"""
    documents = []
    for doc_id in document_ids:
        document = await vector_store.get_document(doc_id)
        if document:
            documents.append(document)
    return documents


@router.post(
    "/analyze", response_model=ThemeAnalysisResponse, status_code=status.HTTP_200_OK
)
async def analyze_themes(request: ThemeAnalysisRequest):
    """Analyze documents to identify themes"""
    try:
        documents = await get_documents_by_ids(request.document_ids)

        if not documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No documents found to analyze",
            )

        query_request = QueryRequest(
            query="Identify the main themes across these documents",
            document_ids=request.document_ids,
            max_documents=len(request.document_ids),
            include_citations=True,
        )

        document_responses = await llm_service.process_query(query_request, documents)

        synthesized_response = await theme_identifier.identify_themes(
            query=query_request.query, document_responses=document_responses
        )

        all_saved_themes = await theme_identifier.list_themes()

        filtered_themes = []
        for theme in all_saved_themes:
            if (
                theme.confidence_score is None
                or theme.confidence_score >= request.min_confidence
            ):
                filtered_themes.append(theme)

        if request.max_themes and len(filtered_themes) > request.max_themes:
            filtered_themes = filtered_themes[: request.max_themes]

        return ThemeAnalysisResponse(
            themes=filtered_themes,
            document_count=len(documents),
            processing_time_ms=100,
            analysis_metadata={
                "query": query_request.query,
                "min_confidence": request.min_confidence,
                "max_themes": request.max_themes,
            },
        )

    except Exception as e:
        logger.error(f"Error analyzing themes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing themes: {str(e)}",
        )


@router.post("/", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
async def create_theme(theme: ThemeCreate):
    """Create a new theme"""
    try:
        theme_response = await theme_identifier.create_theme(theme)
        return theme_response

    except Exception as e:
        logger.error(f"Error creating theme: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating theme: {str(e)}",
        )


@router.get("/", response_model=ThemeList, status_code=status.HTTP_200_OK)
async def list_themes():
    """List all themes"""
    try:
        themes = await theme_identifier.list_themes()

        theme_data = [theme.model_dump() for theme in themes]

        return ThemeList(themes=theme_data, total=len(themes))

    except Exception as e:
        logger.error(f"Error listing themes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing themes: {str(e)}",
        )


@router.put("/{theme_id}", response_model=ThemeResponse)
async def update_theme(
    theme_id: str,
    theme_update: ThemeUpdate,
    if_match: str = Header(..., description="Current version of the theme"),
):
    """Update an existing theme"""
    try:
        expected_version = int(if_match)
        return await theme_identifier.update_theme(
            theme_id=theme_id,
            theme_update=theme_update,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid version format"
        )


@router.get("/{theme_id}", response_model=ThemeResponse, status_code=status.HTTP_200_OK)
async def get_theme(theme_id: str):
    """Get theme by ID"""
    try:
        theme = await theme_identifier.get_theme(theme_id)

        if not theme:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Theme not found"
            )

        return theme

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting theme: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting theme: {str(e)}",
        )

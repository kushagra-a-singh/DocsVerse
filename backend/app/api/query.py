import logging
from typing import List, Optional

from app.api.document import router as document_router
from app.models.document import DocumentResponse
from app.models.query import QueryRequest, QueryResponse
from app.services.llm_service import LLMService
from app.services.theme_identifier import ThemeIdentifier
from app.services.vector_store import VectorStore
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.routing import APIRoute
from app.models.query import SynthesizedResponse

router = APIRouter(tags=["query"])
logger = logging.getLogger(__name__)

llm_service = LLMService()
theme_identifier = ThemeIdentifier()
vector_store = VectorStore()


@router.post("/", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def process_query(request: QueryRequest):
    """Process a query against documents"""
    try:
        documents = await vector_store.get_documents_by_ids(request.document_ids)

        if not documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No documents found to query against",
            )

        document_responses = await llm_service.process_query(request, documents)

        response = QueryResponse(
            query=request.query, document_responses=document_responses
        )

        return response

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}",
        )


@router.post(
    "/with-themes", response_model=QueryResponse, status_code=status.HTTP_200_OK
)
async def process_query_with_themes(request: QueryRequest):
    """Process a query against documents and identify themes"""
    try:
        documents = await vector_store.get_documents_by_ids(request.document_ids)

        if not documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No documents found to query against",
            )

        document_responses = await llm_service.process_query(request, documents)

        logger.info(
            f"[QUERY API] Calling identify_themes with documents count: {len(documents) if documents else 0}"
        )
        synthesized_response = None  
        try:
            synthesized_response = await theme_identifier.identify_themes(
                query=request.query, documents=documents
            )
            logger.info(f"[QUERY API] identify_themes completed successfully.")
        except Exception as e:
            logger.error(
                f"[QUERY API] Error during theme identification: {str(e)}",
                exc_info=True,
            )

        logger.info(
            f"[QUERY API] identify_themes returned object type: {type(synthesized_response)}"
        )
        if isinstance(synthesized_response, SynthesizedResponse):
            logger.info(
                f"[QUERY API] SynthesizedResponse themes count: {len(synthesized_response.themes) if synthesized_response.themes else 0}"
            )
            logger.info(
                f"[QUERY API] SynthesizedResponse answer length: {len(synthesized_response.answer) if synthesized_response.answer else 0}"
            )
            logger.info(
                f"[QUERY API] SynthesizedResponse document_responses count: {len(synthesized_response.document_responses) if synthesized_response.document_responses else 0}"
            )
            if synthesized_response.metadata:
                logger.info(
                    f"[QUERY API] SynthesizedResponse metadata keys: {list(synthesized_response.metadata.keys())}"
                )

        logger.info("[QUERY API] Attempting to create QueryResponse")

        logger.info(
            f"[QUERY API] Final document_responses type: {type(document_responses)}"
        )
        if isinstance(document_responses, list) and len(document_responses) > 0:
            logger.info(
                f"[QUERY API] Final document_responses[0] type: {type(document_responses[0])}"
            )
            if hasattr(document_responses[0], "__dict__"):
                logger.info(
                    f"[QUERY API] Final document_responses[0] attributes: {document_responses[0].__dict__.keys()}"
                )
            else:
                logger.info(
                    f"[QUERY API] Final document_responses[0] attributes: {dir(document_responses[0])}"
                )

        logger.info(
            f"[QUERY API] Final synthesized_response type: {type(synthesized_response)}"
        )
        if synthesized_response and hasattr(synthesized_response, "__dict__"):
            logger.info(
                f"[QUERY API] Final synthesized_response attributes: {synthesized_response.__dict__.keys()}"
            )
        elif synthesized_response:
            logger.info(
                f"[QUERY API] Final synthesized_response attributes: {dir(synthesized_response)}"
            )

        response = QueryResponse(
            query=request.query,
            document_responses=(
                document_responses if document_responses else []
            ),  
            synthesized_response=synthesized_response,  
        )

        logger.info("[QUERY API] Successfully processed query with themes")
        return response

    except Exception as e:
        logger.error(f"Error processing query with themes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query with themes: {str(e)}",
        )


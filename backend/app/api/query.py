import logging
from typing import List, Optional

from app.api.document import router as document_router
from app.models.document import DocumentResponse
from app.models.query import QueryRequest, QueryResponse, SynthesizedResponse
from app.services.chat_service import ChatService
from app.services.llm_service import LLMService
from app.services.theme_identifier import ThemeIdentifier
from app.services.vector_store import VectorStore
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.routing import APIRoute

router = APIRouter(tags=["query"])
logger = logging.getLogger(__name__)

llm_service = LLMService()
theme_identifier = ThemeIdentifier()
vector_store = VectorStore()
chat_service = ChatService()


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
        # Use the chat service to process the query
        response = await chat_service.process_query(request.query, request.document_ids)

        # Add logging to inspect the response from chat_service.process_query
        logger.info(
            f"[QUERY API] Response from chat_service.process_query type: {type(response)}"
        )
        logger.info(
            f"[QUERY API] Response from chat_service.process_query keys: {dir(response) if hasattr(response, '__dict__') else 'N/A'}"
        )

        # Get the synthesized response with themes
        synthesized_response = None
        try:
            # Ensure we pass the document_responses list from the chat service response
            synthesized_response = await theme_identifier.identify_themes(
                query=request.query,
                document_responses=response.document_responses,  # Pass the document_responses list
            )
            logger.info(f"[QUERY API] identify_themes completed successfully.")
        except Exception as e:
            logger.error(
                f"[QUERY API] Error during theme identification: {str(e)}",
                exc_info=True,
            )

        # Create the final response
        final_response = QueryResponse(
            query=request.query,
            document_responses=response.document_responses,
            synthesized_response=synthesized_response,
        )

        logger.info("[QUERY API] Successfully processed query with themes")
        return final_response

    except Exception as e:
        logger.error(f"Error processing query with themes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query with themes: {str(e)}",
        )

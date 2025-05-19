import logging
import os
from typing import Dict, List, Optional

from ..config import settings
from ..database import SessionLocal
from ..models.document import Document
from ..models.query import DocumentQueryResponse, QueryResponse, SynthesizedResponse
from .image_processor import ImageProcessor
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat interactions with both text and image documents"""

    def __init__(self):
        """Initialize the chat service with vector store and image processor"""
        self.vector_store = VectorStore()
        self.image_processor = ImageProcessor()

    def _get_image_path(self, doc: Document) -> Optional[str]:
        """Get the correct absolute path for an image file with forward slashes, checking potential locations."""
        # Check original file path first
        if doc.file_path and os.path.exists(doc.file_path):
            return os.path.abspath(doc.file_path).replace("\\", "/")

        # Check in processed directory
        processed_path_candidate = os.path.join(
            settings.file_storage.processed_dir,
            f"{doc.id}{os.path.splitext(doc.file_path)[1]}",
        )
        if os.path.exists(processed_path_candidate):
            return os.path.abspath(processed_path_candidate).replace("\\", "/")

        # Check in uploads directory
        uploads_path_candidate = os.path.join(
            settings.file_storage.upload_dir,
            f"{doc.id}{os.path.splitext(doc.file_path)[1]}",
        )
        if os.path.exists(uploads_path_candidate):
            return os.path.abspath(uploads_path_candidate).replace("\\", "/")

        return None

    async def process_query(self, query: str, document_ids: List[str]) -> QueryResponse:
        """Process a query against selected documents"""
        try:
            # Get documents from database
            documents = []
            image_documents = []
            db = SessionLocal()

            try:
                for doc_id in document_ids:
                    doc = db.query(Document).filter(Document.id == doc_id).first()
                    if doc:
                        if doc.file_type.lower() in ["png", "jpg", "jpeg"]:
                            image_documents.append(doc)
                        else:
                            documents.append(doc)
            finally:
                db.close()

            # Process text documents
            text_responses = []
            if documents:
                try:
                    text_responses = await self.vector_store.query_documents(
                        query, [doc.id for doc in documents]
                    )
                except Exception as e:
                    logger.error(f"Error querying vector store: {str(e)}")
                    text_responses = []

            # Process image documents
            image_responses = []
            for doc in image_documents:
                try:
                    image_path = self._get_image_path(doc)
                    if not image_path:
                        raise FileNotFoundError(
                            f"Image file not found for document {doc.id}"
                        )
                
                    try:
                        response = await self.image_processor.process_image(image_path, query)
                        print("\n===== RAW GEMINI RESPONSE =====")
                        print(response)  # Debug raw response
                    except Exception as e:
                        print("\n===== PROCESSING ERROR =====")
                        print(f"Error: {str(e)}")
                        if 'response' in locals():
                            print(f"Response text: {response.text if hasattr(response, 'text') else 'No text attribute'}")
                        raise
                    
                    image_responses.append(
                        DocumentQueryResponse(
                            document_id=doc.id,
                            document_name=doc.name,
                            extracted_answer=response['candidates'][0]['content']['parts'][0]['text'],
                            citations=[],
                            relevance_score=1.0,
                        )
                    )
                except Exception as e:
                    logger.error(
                        f"Error processing image {doc.id}: {str(e)}", exc_info=True
                    )
                    image_responses.append(
                        DocumentQueryResponse(
                            document_id=doc.id,
                            document_name=doc.name,
                            extracted_answer=f"Error processing image: {str(e)}",
                            citations=[],
                            relevance_score=0.0,
                        )
                    )

            # Convert text responses to DocumentQueryResponse objects
            document_responses = []
            for response in text_responses:
                if isinstance(response, dict):
                    document_responses.append(
                        DocumentQueryResponse(
                            document_id=response.get("document_id", ""),
                            document_name=response.get("document_name", ""),
                            extracted_answer=response.get("extracted_answer", ""),
                            citations=response.get("citations", []),
                            relevance_score=response.get("relevance_score", 0.0),
                        )
                    )
                else:
                    document_responses.append(response)

            # Add image responses
            document_responses.extend(image_responses)

            if not document_responses:
                raise Exception("No valid responses from any documents")

            return QueryResponse(
                query=query,
                document_responses=document_responses,
                synthesized_response=SynthesizedResponse(
                    query=query,
                    answer="",
                    themes=[],
                    document_responses=[],
                    metadata={},
                ),
            )

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            raise

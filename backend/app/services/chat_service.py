import logging
import os
from typing import Dict, List, Optional

from ..config import settings
from ..database import SessionLocal
from ..models.document import Document
from ..models.query import (
    Citation,
    DocumentQueryResponse,
    QueryResponse,
    SynthesizedResponse,
)
from .image_processor import ImageProcessor
from .llm_service import LLMService
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat interactions with both text and image documents"""

    def __init__(self):
        """Initialize the chat service with vector store, image processor, and LLM service"""
        self.vector_store = VectorStore()
        self.image_processor = ImageProcessor()
        self.llm_service = LLMService()

    def _get_image_path(self, doc: Document) -> Optional[str]:
        """Get the correct absolute path for an image file with forward slashes, checking potential locations."""
       
        if doc.file_path and os.path.exists(doc.file_path):
            return os.path.abspath(doc.file_path).replace("\\", "/")

       
        processed_path_candidate = os.path.join(
            settings.file_storage.processed_dir,
            f"{doc.id}{os.path.splitext(doc.file_path)[1]}",
        )
        if os.path.exists(processed_path_candidate):
            return os.path.abspath(processed_path_candidate).replace("\\", "/")

   
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
          
            documents = []
            image_documents = []
            text_documents = []
            db = SessionLocal()

            try:
                for doc_id in document_ids:
                    doc = db.query(Document).filter(Document.id == doc_id).first()
                    if doc:
                        if doc.file_type.lower() in ["png", "jpg", "jpeg"]:
                            image_documents.append(doc)
                        else:
                            text_documents.append(doc)
                    else:
                        logger.warning(
                            f"Document with ID {doc_id} not found in database."
                        )
            finally:
                db.close()

            document_responses = []
            synthesized_answer = ""
            synthesized_citations = []

           
            if text_documents:
                try:
                   
                    text_document_ids = [doc.id for doc in text_documents]
                    text_search_results = await self.vector_store.search(
                        query=query,
                        document_ids=text_document_ids,
                        limit=settings.vector_db.search_limit * len(text_document_ids),
                    )

                    if text_search_results:
                       
                        synthesized_answer, synthesized_citations_dict = (
                            await self.llm_service._generate_answer(
                                query=query,
                                chunks=text_search_results,
                                citation_level="chunk",
                            )
                        )

                       
                        synthesized_citations = [
                            Citation(**cit) for cit in synthesized_citations_dict
                        ]

                        
                        text_synth_response = DocumentQueryResponse(
                            document_id="synthesized_text",
                            document_name="Synthesized Text Response",
                            extracted_answer=synthesized_answer,
                            citations=synthesized_citations,
                            relevance_score=1.0,
                        )
                        document_responses.append(text_synth_response)
                    else:
                        logger.info(
                            f"No search results found for text documents: {text_document_ids}"
                        )

                except Exception as e:
                    logger.error(
                        f"Error processing text documents with LLM: {str(e)}",
                        exc_info=True,
                    )
                   
                    document_responses.append(
                        DocumentQueryResponse(
                            document_id="text_processing_error",
                            document_name="Text Processing Error",
                            extracted_answer=f"Error processing text documents: {str(e)}",
                            citations=[],
                            relevance_score=0.0,
                        )
                    )

           
            for doc in image_documents:
                try:
                    image_path = self._get_image_path(doc)
                    if not image_path:
                        raise FileNotFoundError(
                            f"Image file not found for document {doc.id}"
                        )

                    try:
                        response = await self.image_processor.process_image(
                            image_path, query
                        )
                        print("\n===== RAW GEMINI RESPONSE ====")
                        print(response)  
                    except Exception as e:
                        print("\n===== PROCESSING ERROR ====")
                        print(f"Error: {str(e)}")
                        if "response" in locals():
                            if (
                                isinstance(response, tuple)
                                and len(response) > 0
                                and hasattr(response[0], "text")
                            ):
                                print(f"Response text: {response[0].text}")
                            elif hasattr(
                                response, "text"
                            ):  
                                print(f"Response text: {response.text}")
                            else:
                                print("Response does not have a text attribute")
                        raise

                    image_answer = "Could not extract answer from image."
                    image_citations = []

                    if isinstance(response, tuple) and len(response) == 2:
                        image_answer = response[
                            0
                        ]  
                        citations_data = response[
                            1
                        ] 

                        if isinstance(citations_data, list):
                            image_citations = [
                                Citation(**cit)
                                for cit in citations_data
                                if isinstance(cit, dict)
                            ]
                        else:
                            logger.warning(
                                f"Image processor returned citations data in unexpected format: {type(citations_data)}"
                            )

                    document_responses.append(
                        DocumentQueryResponse(
                            document_id=doc.id,
                            document_name=doc.name,
                            extracted_answer=image_answer,
                            citations=image_citations,  
                            relevance_score=1.0,
                        )
                    )
                except Exception as e:
                    logger.error(
                        f"Error processing image {doc.id}: {str(e)}", exc_info=True
                    )
                    document_responses.append(
                        DocumentQueryResponse(
                            document_id=doc.id,
                            document_name=doc.name,
                            extracted_answer=f"Error processing image: {str(e)}",
                            citations=[],
                            relevance_score=0.0,
                        )
                    )

            if not document_responses:
                logger.error("No valid responses from any documents")
                raise Exception("No valid responses from any documents")

            #synthesized_response will contain the LLM's output for text documents
            final_synthesized_response = None
            if synthesized_answer or synthesized_citations:
                final_synthesized_response = SynthesizedResponse(
                    query=query,
                    answer=synthesized_answer,
                    themes=[],
                    document_responses=[],
                    metadata={},
                )

            return QueryResponse(
                query=query,
                document_responses=document_responses,
                synthesized_response=final_synthesized_response,
            )

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            raise

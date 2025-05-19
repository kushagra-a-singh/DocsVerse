import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.config import settings
from app.database import get_db
from app.models.query import (
    DocumentQueryResponse,
    SynthesizedResponse,
    ThemeIdentification,
)
from app.models.theme_models import (
    Theme,
    ThemeCreate,
    ThemeList,
    ThemeResponse,
    ThemeUpdate,
)
from app.services.document_processor import DocumentProcessor
from app.services.llm_service import LLMService
from app.services.vector_store import VectorStore
from fastapi import Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

llm_service = LLMService()
vector_store = VectorStore()
document_processor = DocumentProcessor()


class ThemeIdentifier:
    """Service for identifying themes across document responses"""

    def __init__(self):
        """Initialize the theme identifier with LLM service"""
        self.llm_service = LLMService()
        self.document_processor = DocumentProcessor()

    async def identify_themes(
        self, query: str, document_responses: List[DocumentQueryResponse]
    ) -> SynthesizedResponse:
        """Identify themes across document responses"""
        logger.info(
            f"[THEME] Identifying themes for {len(document_responses)} document responses"
        )

        try:
            # Prepare document response content for LLM analysis
            # Extract content from each document query response
            document_content_for_theme_analysis = []
            for response in document_responses:
                try:
                    # Use extracted_answer from DocumentQueryResponse
                    content = (
                        response.extracted_answer if response.extracted_answer else ""
                    )

                    # Only include responses with actual content for theme analysis
                    if (
                        content
                        and content != "Could not process image"
                        and not content.startswith("Error processing image")
                    ):
                        document_content_for_theme_analysis.append(
                            {
                                "document_id": response.document_id,
                                "document_name": response.document_name,
                                "content": content,
                            }
                        )
                    else:
                        logger.warning(
                            f"[THEME] Skipping theme analysis for document {response.document_id} due to empty or error content."
                        )
                except Exception as e:
                    logger.error(
                        f"[THEME] Error processing document response for theme analysis {response.document_id}: {str(e)}",
                        exc_info=True,
                    )

            if not document_content_for_theme_analysis:
                logger.warning(
                    "[THEME] No valid document response content available for theme identification."
                )
                return SynthesizedResponse(
                    query=query,
                    answer="No valid document response content available for theme identification.",
                    themes=[],
                    document_responses=document_responses,  # Return original document responses
                    metadata={
                        "document_count": len(document_responses),
                        "theme_count": 0,
                    },
                )

            themes, synthesized_answer_text = await self._generate_themes_and_answer(
                query, document_content_for_theme_analysis
            )

            if not isinstance(themes, list):
                logger.error(
                    f"[THEME] _generate_themes_and_answer did not return a list of themes. Returned type: {type(themes)}"
                )
                themes = []

            # Store themes in database (assuming _generate_themes_and_answer returns ThemeIdentification objects)
            # In this flow, we are not saving themes directly after every query with themes.
            # The ThemeIdentification objects are part of the SynthesizedResponse.

            # Note: The original code seemed to have a step to list/fetch saved themes here, which doesn't fit the immediate response flow.
            # We will return the themes identified in this query run.

            return SynthesizedResponse(
                query=query,
                answer=synthesized_answer_text,
                themes=themes,  # Return the themes generated in this query
                document_responses=document_responses,  # Return the original document responses
                metadata={
                    "document_count": len(document_responses),
                    "theme_count": len(themes),
                },
            )

        except Exception as e:
            logger.error(
                f"[THEME] An unexpected error occurred during theme identification: {str(e)}",
                exc_info=True,
            )
            # In case of error, still return the original document responses and an error message
            return SynthesizedResponse(
                query=query,
                answer=f"An error occurred during theme identification: {str(e)}",
                themes=[],
                document_responses=document_responses,
                metadata={
                    "document_count": len(document_responses),
                    "theme_count": 0,
                    "error": str(e),
                },
            )

    async def create_theme(
        self, theme: ThemeCreate, db: Session = Depends(get_db)
    ) -> ThemeResponse:
        """Create a new theme"""
        # Note: The Depends(get_db) is for API endpoints. For service internal use, manage session directly.
        db = next(get_db())  # Get a new session for service internal use
        try:
            db_theme = Theme(
                id=str(uuid4()),
                name=theme.name,
                description=theme.description,
                keywords=theme.keywords,
                document_ids=theme.document_ids,
                confidence_score=theme.confidence_score,
                metadata_=theme.metadata,  # Use metadata_ for SQLAlchemy model
            )
            db.add(db_theme)
            db.commit()
            db.refresh(db_theme)
            return ThemeResponse.from_orm(db_theme)
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating theme: {str(e)}")
            raise
        finally:
            db.close()

    async def update_theme(
        self, theme_id: str, theme: ThemeUpdate, db: Session = Depends(get_db)
    ) -> Optional[ThemeResponse]:
        # Note: The Depends(get_db) is for API endpoints. For service internal use, manage session directly.
        db = next(get_db())  # Get a new session for service internal use
        try:
            db_theme = db.query(Theme).filter(Theme.id == theme_id).first()
            if db_theme:
                update_data = theme.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    # Handle metadata_ mapping if needed
                    if key == "metadata":
                        setattr(db_theme, "metadata_", value)
                    else:
                        setattr(db_theme, key, value)

                db.commit()
                db.refresh(db_theme)
                return ThemeResponse.from_orm(db_theme)
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating theme {theme_id}: {str(e)}")
            raise
        finally:
            db.close()

    async def list_themes(self) -> List[ThemeResponse]:
        """List all saved themes"""
        db = next(get_db())
        try:
            themes = db.query(Theme).all()
            return [ThemeResponse.from_orm(theme) for theme in themes]
        except Exception as e:
            logger.error(f"Error listing themes: {str(e)}")
            return []
        finally:
            db.close()

    async def get_theme(
        self, theme_id: str, db: Session = Depends(get_db)
    ) -> Optional[ThemeResponse]:
        # Note: The Depends(get_db) is for API endpoints. For service internal use, manage session directly.
        db = next(get_db())  # Get a new session for service internal use
        try:
            theme = db.query(Theme).filter(Theme.id == theme_id).first()
            if theme:
                return ThemeResponse.from_orm(theme)
            return None
        except Exception as e:
            logger.error(f"Error getting theme {theme_id}: {str(e)}")
            return None
        finally:
            db.close()

    async def delete_theme(self, theme_id: str) -> bool:
        """Delete a theme"""
        db = next(get_db())
        try:
            db_theme = db.query(Theme).filter(Theme.id == theme_id).first()
            if db_theme:
                db.delete(db_theme)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting theme {theme_id}: {str(e)}")
            return False
        finally:
            db.close()

    async def _generate_themes_and_answer(
        self, query: str, documents: List[Dict]
    ) -> tuple[List[ThemeIdentification], str]:
        """Generate themes and synthesized answer using LLM"""

        context = ""
        for i, doc_data in enumerate(documents):
            # Use the data dictionary directly
            context += f"\nDOCUMENT {i+1}: {doc_data['document_name']}\n{doc_data['content']}\n"

        prompt = f"""
        You are an AI assistant that analyzes multiple documents to identify common themes and synthesize information.

        USER QUERY: {query}

        DOCUMENT CONTENTS:
        {context}

        Based on the documents above, please:
        1. Identify the main themes that appear across multiple documents
        2. Provide a comprehensive answer to the user query that synthesizes information from all documents

        Format your response as a JSON object with the following structure:
        {{"themes": [
            {{"theme_name": "Name of theme 1",
             "description": "Description of theme 1",
             "supporting_documents": [list of document indices that support this theme],
             "confidence_score": confidence score between 0 and 1
            }},
            ...
         ],
         "synthesized_answer": "Your comprehensive answer that addresses the query and incorporates the identified themes"
        }}

        Identify 3-5 significant themes that appear across multiple documents. For each theme, provide a clear name, description, and list of supporting documents (using the document numbers from 1 to {len(documents)}).
        """

        try:
            if settings.llm.provider.lower() == "openai":
                response = await self.llm_service._call_openai(prompt)
            elif settings.llm.provider.lower() == "google":
                response = await self.llm_service._call_google(prompt)
            elif settings.llm.provider.lower() == "groq":
                response = await self.llm_service._call_groq(prompt)
            else:
                raise ValueError(f"Unsupported LLM provider: {settings.llm.provider}")

            try:
                response_text = response.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                response_data = json.loads(response_text)
                themes = []
                for theme_data in response_data.get("themes", []):

                    supporting_docs = []
                    # Map document indices back to document_ids from the input list
                    for idx in theme_data.get("supporting_documents", []):
                        if isinstance(idx, int) and 1 <= idx <= len(documents):
                            # documents here is the list of dictionaries prepared for the LLM
                            supporting_docs.append(documents[idx - 1]["document_id"])

                    theme = ThemeIdentification(
                        theme_name=theme_data["theme_name"],
                        description=theme_data["description"],
                        supporting_documents=supporting_docs,
                        confidence_score=theme_data.get("confidence_score", 0.5),
                    )
                    themes.append(theme)
                return themes, response_data.get("synthesized_answer", "")

            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON response from LLM: {response}")
                # In case of invalid JSON, return empty themes and the raw response as answer
                return [], response

        except Exception as e:
            logger.error(f"Error generating themes: {str(e)}")
            # In case of error during LLM call, return empty themes and an error message
            return [], f"Error generating themes: {str(e)}"


theme_identifier = ThemeIdentifier()

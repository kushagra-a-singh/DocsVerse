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
        self, query: str, documents: List["DocumentResponse"]
    ) -> SynthesizedResponse:
        """Identify themes across documents"""
        logger.info(f"[THEME] Identifying themes for {len(documents)} documents")

        try:
            #prepare document content for LLM analysis
            #extract content from each document
            documents_content = []
            for doc in documents:
                try:
                    if doc.status == "PROCESSED":
                        content_response = (
                            await self.document_processor.get_document_content(doc.id)
                        ) 
                        content = (
                            content_response.get("content", "")
                            if isinstance(content_response, dict)
                            else ""
                        )
                        documents_content.append(
                            {
                                "document_id": doc.id,
                                "document_name": doc.name,
                                "content": content,
                            }
                        )
                    else:
                        logger.warning(
                            f"[THEME] Document {doc.id} not PROCESSED. Skipping theme analysis for this document."
                        )
                except Exception as e:
                    logger.error(
                        f"[THEME] Error getting content for document {doc.id}: {str(e)}",
                        exc_info=True,
                    )

            if not documents_content:
                logger.warning(
                    "[THEME] No processed document content available for theme identification."
                )
                return SynthesizedResponse(
                    query=query,
                    answer="No processed document content available for theme identification.",
                    themes=[],
                    document_responses=[], 
                    metadata={
                        "document_count": len(documents),
                        "theme_count": 0,
                    },
                )

            
            themes, synthesized_answer_text = await self._generate_themes_and_answer(
                query, documents_content
            )

            if not isinstance(themes, list):
                logger.error(
                    f"[THEME] _generate_themes_and_answer did not return a list of themes. Returned type: {type(themes)}"
                )
                themes = [] 

            #store themes in database
            #the themes returned are ThemeIdentification objects.

            #fetch the saved themes from the database as ThemeResponse objects
            saved_themes = await self.list_themes()

            return SynthesizedResponse(
                query=query,
                answer=synthesized_answer_text,
                themes=saved_themes,
                document_responses=[],
                metadata={
                    "document_count": len(documents),
                    "theme_count": len(saved_themes),
                },
            )

        except Exception as e:
            logger.error(
                f"[THEME] An unexpected error occurred during theme identification: {str(e)}",
                exc_info=True,
            )
            return SynthesizedResponse(
                query=query,
                answer=f"An error occurred during theme identification: {str(e)}",
                themes=[],
                document_responses=[],
                metadata={
                    "document_count": len(documents),
                    "theme_count": 0,
                    "error": str(e),
                },
            )

    async def create_theme(self, theme: ThemeCreate) -> ThemeResponse:
        """Create a new theme"""
        db = next(get_db())
        try:
            #convert Pydantic model to SQLAlchemy model instance
            db_theme = Theme(
                id=str(uuid4()),
                name=theme.name,
                description=theme.description,
                keywords=theme.keywords,
                document_ids=theme.document_ids,
                confidence_score=theme.confidence_score,
                created_at=datetime.utcnow(),
                metadata_=theme.metadata,
            )
            db.add(db_theme)
            db.commit()
            db.refresh(db_theme)
            return ThemeResponse.from_orm(db_theme)

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating theme: {str(e)}")
            raise e
        finally:
            db.close()

    async def update_theme(
        self, theme_id: str, theme_update: ThemeUpdate
    ) -> Optional[ThemeResponse]:
        """Update an existing theme"""
        db = next(get_db())
        try:
            db_theme = db.query(Theme).filter(Theme.id == theme_id).first()
            if not db_theme:
                return None

            for var, value in theme_update.dict(exclude_unset=True).items():
    
                if var == "metadata":
                    setattr(db_theme, "metadata_", value)
                else:
                    setattr(db_theme, var, value)
            db_theme.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(db_theme)
    
            return ThemeResponse.from_orm(db_theme)

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating theme {theme_id}: {str(e)}")
            raise
        finally:
            db.close()

    async def list_themes(self) -> List[ThemeResponse]:
        """List all themes"""
        db = next(get_db())
        try:
            #use ORM query to fetch themes
            themes = db.query(Theme).order_by(Theme.created_at.desc()).all()

            return [ThemeResponse.from_orm(theme) for theme in themes]

        except Exception as e:
            logger.error(f"Error listing themes: {str(e)}")
            return []
        finally:
            db.close()

    async def get_theme(self, theme_id: str) -> Optional[ThemeResponse]:
        """Get theme by ID"""
        db = next(get_db())
        try:
            theme = db.query(Theme).filter(Theme.id == theme_id).first()
            if theme:
                return ThemeResponse.from_orm(theme)
            return None
        except Exception as e:
            logger.error(f"Error getting theme: {str(e)}")
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
        for i, doc in enumerate(documents):
            context += f"\nDOCUMENT {i+1}: {doc['document_name']}\n{doc['content']}\n"

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
                    for idx in theme_data.get("supporting_documents", []):
                        if isinstance(idx, int) and 1 <= idx <= len(documents):
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
                return [], response

        except Exception as e:
            logger.error(f"Error generating themes: {str(e)}")
            return [], f"Error generating themes: {str(e)}"


theme_identifier = ThemeIdentifier()

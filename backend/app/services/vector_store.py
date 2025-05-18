import logging
import os
from typing import Any, Dict, List, Optional

import chromadb
from app.config import settings
from app.models.document import DocumentChunk, DocumentResponse
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class VectorStore:
    """Singleton service for managing document vectors in ChromaDB"""

    _instance = None
    _embedding_function = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            cls._initialize()
        return cls._instance

    @classmethod
    def _initialize(cls):
        """Initialize embeddings and client only once"""
        if cls._embedding_function is None:
            logger.info(
                f"[VECTOR] Initializing embedding model: {settings.vector_db.model_name}"
            )
            try:
                cls._embedding_function = (
                    embedding_functions.SentenceTransformerEmbeddingFunction(
                        model_name=settings.vector_db.model_name
                    )
                )
                logger.info("[VECTOR] Embedding function initialized successfully")

                test_embedding = cls._embedding_function(["test"])
                logger.info(f"[VECTOR] Embedding dimensions: {len(test_embedding[0])}")

                try:
                    cls._client = chromadb.PersistentClient(
                        path=settings.vector_db.persist_directory
                    )
                    logger.info("[VECTOR] ChromaDB client initialized successfully")

                    collections = cls._client.list_collections()
                    logger.info(
                        f"[VECTOR] Found {len(collections)} collections in ChromaDB"
                    )

                except Exception as e:
                    logger.error(
                        f"[VECTOR] Failed to initialize ChromaDB client: {str(e)}",
                        exc_info=True,
                    )
                    raise
            except Exception as e:
                logger.error(
                    f"[VECTOR] Failed to initialize VectorStore: {str(e)}",
                    exc_info=True,
                )
                raise

    def __init__(self):
        if not hasattr(self, "collection"):
            self.collection = self._client.get_or_create_collection(
                name=settings.vector_db.collection_name,
                embedding_function=self._embedding_function,
                metadata={"description": "Document chunks for semantic search"},
            )

    async def add_document(self, document_id: str, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to the vector store"""
        try:
            logger.info(
                f"[VECTOR] Adding {len(chunks)} chunks for document {document_id}"
            )
            ids = [chunk.id for chunk in chunks]
            documents = [chunk.content for chunk in chunks]
            metadatas = []
            for chunk in chunks:
                metadata = {
                    "document_id": chunk.document_id,
                    "chunk_number": chunk.chunk_number,
                    "page_number": chunk.page_number or 0,
                    **chunk.metadata,
                }
                cleaned_metadata = {
                    k: "" if v is None else v for k, v in metadata.items()
                }
                metadatas.append(cleaned_metadata)

            self.collection.add(ids=ids, documents=documents, metadatas=metadatas)
            logger.info(
                f"[VECTOR] Successfully added {len(chunks)} chunks for document {document_id}"
            )
            return True
        except Exception as e:
            logger.error(
                f"[VECTOR] Error adding document {document_id}: {str(e)}", exc_info=True
            )
            return False

    async def delete_document(self, document_id: str) -> bool:
        """Delete document chunks from the vector store"""
        try:
            logger.info(f"[VECTOR] Deleting document {document_id} from vector store")
            
            self.collection.delete(where={"document_id": document_id})
            logger.info(f"[VECTOR] Deleted document {document_id} from vector store")
            return True

        except Exception as e:
            logger.error(
                f"[VECTOR] Error deleting document {document_id} from vector store: {str(e)}",
                exc_info=True,
            )
            return False

    async def search(
        self, query: str, document_ids: Optional[List[str]] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for relevant document chunks"""
        try:
            logger.info(
                f"[VECTOR] Searching vector store. Query: '{query}', Document IDs: {document_ids}, Limit: {limit}"
            )
            where_filter = None
            if document_ids:
                where_filter = {"document_id": {"$in": document_ids}}

            results = self.collection.query(
                query_texts=[query], n_results=limit, where=where_filter
            )

            formatted_results = []
            if results and results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append(
                        {
                            "content": doc,
                            "metadata": (
                                results["metadatas"][0][i]
                                if results["metadatas"] and results["metadatas"][0]
                                else {}
                            ),
                            "id": (
                                results["ids"][0][i]
                                if results["ids"] and results["ids"][0]
                                else ""
                            ),
                            "distance": (
                                results["distances"][0][i]
                                if results["distances"] and results["distances"][0]
                                else 0
                            ),
                        }
                    )

            logger.info(f"[VECTOR] Search returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(
                f"[VECTOR] Error searching vector store: {str(e)}", exc_info=True
            )
            return []

    async def get_documents_by_ids(
        self, document_ids: List[str]
    ) -> List[DocumentResponse]:
        """Get multiple documents by their IDs"""
        documents = []
        for doc_id in document_ids:
            document = await self.get_document(doc_id)
            if document:
                documents.append(document)
        return documents

    async def get_document(self, document_id: str) -> Optional[DocumentResponse]:
        """Get a single document by ID"""
        try:
            logger.info(f"[VECTOR] Getting document {document_id} from vector store")
            results = self.collection.get(where={"document_id": document_id}, limit=1)
            if results and results["documents"]:
                logger.info(f"[VECTOR] Document {document_id} found in vector store")
                return DocumentResponse(
                    id=document_id,
                    name=results["metadatas"][0].get("name", ""),
                    status="processed", 
                )
            logger.info(f"[VECTOR] Document {document_id} not found in vector store")
            return None
        except Exception as e:
            logger.error(
                f"[VECTOR] Error getting document {document_id}: {str(e)}",
                exc_info=True,
            )
            return None

    async def list_documents(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        document_type: Optional[str] = None,
        author: Optional[str] = None,
    ) -> List[DocumentResponse]:
        """List documents with optional filtering"""
        try:
            logger.info(
                f"[VECTOR] Listing documents. Skip: {skip}, Limit: {limit}, Status: {status}, Type: {document_type}, Author: {author}"
            )
            where_filter = {}
            if status:
                where_filter["status"] = status
            if document_type:
                where_filter["document_type"] = document_type
            if author:
                where_filter["author"] = author

            query_params = {"limit": limit, "offset": skip}
            if where_filter:
                query_params["where"] = where_filter

            results = self.collection.get(**query_params)

            documents = []
            if results and results["ids"]:
                for i, doc_id in enumerate(results["ids"]):
                    documents.append(
                        DocumentResponse(
                            id=doc_id,
                            name=results["metadatas"][i].get("name", ""),
                            status=results["metadatas"][i].get("status", "unknown"),
                            document_type=results["metadatas"][i].get("document_type"),
                            author=results["metadatas"][i].get("author"),
                        )
                    )
            logger.info(f"[VECTOR] Listed {len(documents)} documents from vector store")
            return documents

        except Exception as e:
            logger.error(f"[VECTOR] Error listing documents: {str(e)}", exc_info=True)
            return []

    async def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            results = self.collection.get(where={"document_id": document_id})

            formatted_results = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"]):
                    formatted_results.append(
                        {
                            "content": doc,
                            "metadata": (
                                results["metadatas"][i] if results["metadatas"] else {}
                            ),
                            "id": results["ids"][i] if results["ids"] else "",
                        }
                    )

            formatted_results.sort(key=lambda x: x["metadata"].get("chunk_number", 0))

            return formatted_results

        except Exception as e:
            logger.error(f"Error getting chunks for document {document_id}: {str(e)}")
            return []

    def __del__(self):
        """Cleanup resources when instance is destroyed"""
        if hasattr(self, "_client"):
            try:
                self._client.close()
            except Exception as e:
                logger.warning(f"Error closing ChromaDB client: {str(e)}")

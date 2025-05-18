import asyncio
import logging
import os
import shutil
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PIL import Image

logger = logging.getLogger(__name__)
from app.config import settings
from app.models.document import (
    DocumentChunk,
    DocumentCreate,
    DocumentStatus,
    DocumentUpdate,
)
from app.services.vector_store import VectorStore

try:
    import pytesseract
except ImportError:
    pytesseract = None
    logger.warning("pytesseract not installed - OCR functionality will be disabled")


class DocumentProcessor:
    """Service for processing documents, extracting text, and preparing for vector storage"""

    def __init__(self):
        """Initialize the document processor with OCR and vector store"""
        logger.info("[PROCESS] DocumentProcessor initialized")
        self.provider = settings.llm.provider.lower()
        self.upload_dir = settings.file_storage.upload_dir
        self.processed_dir = settings.file_storage.processed_dir
        self.ocr_enabled = settings.ocr.enabled and pytesseract is not None
        if settings.ocr.enabled and pytesseract is None:
            logger.warning(
                "OCR is enabled in settings but pytesseract is not installed"
            )
        self.vector_store = VectorStore()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.vector_db.chunk_size,
            chunk_overlap=settings.vector_db.chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        )

    async def process_document(self, document: DocumentCreate) -> DocumentUpdate:
        """Process a document and extract text"""
        logger.info(f"[PROCESS] Entering process_document for document {document.id}")
        logger.info(f"[PROCESS] DocumentProcessor instance: {self}")
        try:
            logger.info(
                f"[PROCESS] Starting processing for document {document.id} at {document.file_path}"
            )
            update = DocumentUpdate(status=DocumentStatus.PROCESSING.value)

            file_path = os.path.join(self.upload_dir, document.file_path)
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == ".pdf":
                logger.info(f"[PROCESS] Detected PDF file: {file_path}")
                text, page_count, metadata = await self._process_pdf(file_path)
            elif file_extension in [".png", ".jpg", ".jpeg"]:
                logger.info(f"[PROCESS] Detected image file: {file_path}")
                text, page_count, metadata = await self._process_image(file_path)
            else:
                logger.error(f"[PROCESS] Unsupported file type: {file_extension}")
                raise ValueError(f"Unsupported file type: {file_extension}")

            logger.info(
                f"[PROCESS] Text extraction complete for document {document.id}. Length: {len(text)} chars"
            )
            logger.info(f"[PROCESS] Creating chunks for document {document.id}")
        
            metadata = {
                **metadata,
                "name": document.name,
                "status": document.status,
                "document_type": document.document_type,
                "author": document.author,
                "date": document.date,
                "upload_date": document.upload_date,
                "file_type": document.file_type,
                "file_path": document.file_path,
            }

            chunks = self._create_chunks(document.id, text, metadata)
            logger.info(
                f"[PROCESS] Created {len(chunks)} chunks for document {document.id}"
            )

            if not chunks:
                logger.error(
                    f"[PROCESS] No chunks created for document {document.id}. Text extraction likely failed."
                )
                return DocumentUpdate(
                    status=DocumentStatus.ERROR.value,
                    error="Text extraction failed or resulted in empty content.",
                )

            vector_result = await self.vector_store.add_document(document.id, chunks)
            logger.info(f"[PROCESS] Vector store add_document result: {vector_result}")

            processed_dir_path = settings.file_storage.processed_dir
            processed_path = os.path.join(
                processed_dir_path, os.path.basename(file_path)
            )

            os.makedirs(processed_dir_path, exist_ok=True)

            logger.info(
                f"Attempting to move file from {file_path} to {processed_path}"
            )
            try:
                shutil.move(file_path, processed_path)
                logger.info(
                    f"Successfully moved file to {processed_path}"
                ) 
            except FileNotFoundError:
                logger.error(
                    f"File not found during move operation: {file_path}", exc_info=True
                )
                update.status = DocumentStatus.ERROR.value
                update.error = f"File not found during move operation: {file_path}"
                return update
            except PermissionError:
                logger.error(
                    f"Permission denied during file move to: {processed_path}",
                    exc_info=True,
                )
                update.status = DocumentStatus.ERROR.value
                update.error = (
                    f"Permission denied during file move to: {processed_path}"
                )
                return update
            except Exception as e:
                logger.error(
                    f"An unexpected error occurred during file move: {str(e)}",
                    exc_info=True,
                )
                update.status = DocumentStatus.ERROR.value
                update.error = (
                    f"An unexpected error occurred during file move: {str(e)}"
                )
                return update

            logger.info(f"Document processing completed for ID: {document.id}")

            update.status = DocumentStatus.PROCESSED.value
            update.page_count = page_count

            if "author" in metadata and not document.author:
                update.author = metadata.get("author")
            if "date" in metadata and not document.date:
                update.date = metadata.get("date")
            if "document_type" in metadata and not document.document_type:
                update.document_type = metadata.get("document_type")

            logger.info(f"[PROCESS] Finished processing document {document.id}")
            return update

        except Exception as e:
            logger.error(
                f"[PROCESS] Error processing document {document.id}: {str(e)}",
                exc_info=True,
            )
            logger.error(f"[PROCESS] File path being processed: {file_path}")
            return DocumentUpdate(status=DocumentStatus.ERROR.value, error=str(e))

    async def _process_pdf(self, file_path: str) -> Tuple[str, int, Dict[str, Any]]:
        """Process a PDF file and extract text"""
        metadata = {}
        full_text = ""

        try:
            with open(os.path.abspath(file_path), "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)

                if pdf_reader.metadata:
                    if pdf_reader.metadata.author:
                        metadata["author"] = pdf_reader.metadata.author
                    if pdf_reader.metadata.creation_date:
                        metadata["date"] = str(pdf_reader.metadata.creation_date)

                for i, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text:
                        full_text += f"Page {i+1}:\n{text}\n\n"

            return full_text, page_count, metadata

        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise

    async def _process_image(self, file_path: str) -> Tuple[str, int, Dict[str, Any]]:
        """Process an image file using OCR"""
        if not self.ocr:
            raise ValueError("OCR is not enabled but image processing was requested")

        try:
            with Image.open(file_path) as img:
                metadata = {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                }

            text = await self._process_page_with_ocr(file_path)

            return text, 1, metadata 

        except Exception as e:
            logger.error(f"Error processing image {file_path}: {str(e)}")
            raise

    async def _process_page_with_ocr(
        self, file_path: str, page_num: Optional[int] = None
    ) -> str:
        """Process a page with OCR using pytesseract"""
        if not self.ocr_enabled:
            logger.warning("OCR requested but not enabled/available")
            return ""

        try:
            with Image.open(file_path) as img:
                text = pytesseract.image_to_string(img, lang=settings.ocr.language)
            return text
        except Exception as e:
            logger.error(f"Error during OCR processing: {str(e)}")
            return ""

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.ocr.ocr, file_path, page_num)

        if not result or not result[0]:
            return ""

        text = ""
        for line in result[0]:
            if line[1][0]:  
                text += line[1][0] + "\n"

        return text

    def _create_chunks(
        self, document_id: str, text: str, metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """Split text into chunks for vector storage"""
    
        chunks = self.text_splitter.split_text(text)

        doc_chunks = []
        for i, chunk in enumerate(chunks):
            page_number = None
            for line in chunk.split("\n"):
                if line.startswith("Page ") and ":" in line:
                    try:
                        page_number = int(line.split("Page ")[1].split(":")[0])
                        break
                    except ValueError:
                        pass

            chunk_id = f"{document_id}_{i}"
            doc_chunk = DocumentChunk(
                id=chunk_id,
                document_id=document_id,
                chunk_number=i,
                content=chunk,
                page_number=page_number,
                metadata={**metadata, "chunk_id": chunk_id, "chunk_index": i},
            )
            doc_chunks.append(doc_chunk)

        return doc_chunks

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks from storage"""
        try:
            await self.vector_store.delete_document(document_id)
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")


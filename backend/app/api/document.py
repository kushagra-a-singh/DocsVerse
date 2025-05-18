import logging
import os
import shutil
import uuid
from datetime import datetime
from typing import List, Optional

from app.database import Base, SessionLocal, engine, get_db
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..models.document import (
    Document,
    DocumentCreate,
    DocumentList,
    DocumentResponse,
    DocumentStatus,
)

from ..services.document_processor import DocumentProcessor
from ..services.vector_store import VectorStore

router = APIRouter()

document_processor = DocumentProcessor()
vector_store = VectorStore()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=List[DocumentResponse])
async def upload_document(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    document_name: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
):
    """Upload documents for processing and indexing"""
    results = []
    upload_dir = os.path.abspath(settings.file_storage.upload_dir)
    os.makedirs(upload_dir, exist_ok=True) 

    for file in files:
        doc_id = str(uuid.uuid4())
        try:
            logger.info(
                f"[UPLOAD] Starting processing for file: {file.filename} with ID: {doc_id}"
            )

            allowed_extensions = [".pdf", ".png", ".jpg", ".jpeg"]
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_extensions:
                logger.error(
                    f"[UPLOAD] Unsupported file type for {file.filename}: {file_ext}"
                )
                results.append(
                    DocumentResponse(
                        id=doc_id,
                        name=file.filename,
                        status=DocumentStatus.ERROR.value,
                        error=f"Unsupported file type: {file_ext}",
                        message="Upload failed due to unsupported file type.",
                    )
                )
                continue

            current_document_name = (
                document_name if document_name else os.path.splitext(file.filename)[0]
            )

            file_path = os.path.join(upload_dir, f"{doc_id}{file_ext}")
            try:
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                logger.info(
                    f"[UPLOAD] File saved successfully for {file.filename} to {file_path}"
                )
            except Exception as e:
                logger.error(
                    f"[UPLOAD] Error saving file {file.filename}: {str(e)}",
                    exc_info=True,
                )
                results.append(
                    DocumentResponse(
                        id=doc_id,
                        name=current_document_name,
                        status=DocumentStatus.ERROR.value,
                        error=f"Failed to save file: {str(e)}",
                        message="Upload failed during file saving.",
                    )
                )
                continue 

            document_data = DocumentCreate(
                id=doc_id,
                name=current_document_name,
                file_path=os.path.abspath(file_path),  
                file_type=file_ext.replace(".", ""),
                document_type=document_type,
                author=author,
                date=date,
                upload_date=datetime.now().isoformat(),
                status=DocumentStatus.PROCESSING.value,  
                page_count=0,
            )

            db = SessionLocal()
            db_document = None  
            try:
                db_document = Document(
                    id=document_data.id,
                    name=document_data.name,
                    file_path=document_data.file_path,
                    file_type=document_data.file_type,
                    document_type=document_data.document_type,
                    author=document_data.author,
                    date=document_data.date,
                    upload_date=datetime.now(), 
                    status=DocumentStatus.PROCESSING.value,
                    page_count=0,
                )
                db.add(db_document)
                db.commit()
                db.refresh(db_document) 
                logger.info(
                    f"[UPLOAD] Document {db_document.id} stored in database with PROCESSING status"
                )
            except Exception as e:
                db.rollback()  
                logger.error(
                    f"[UPLOAD] Error storing document {doc_id} in database: {str(e)}",
                    exc_info=True,
                )
                results.append(
                    DocumentResponse(
                        id=doc_id,
                        name=current_document_name,
                        status=DocumentStatus.ERROR.value,
                        error=f"Failed to store document in database: {str(e)}",
                        message="Upload failed during database storage.",
                    )
                )
                db.close()  
                continue  
            finally:
                if (
                    db is not None and db.is_active
                ): 
                    try:
                        db.close()
                    except Exception as close_e:
                        logger.error(
                            f"Error closing DB session after potential rollback for {doc_id}: {str(close_e)}",
                            exc_info=True,
                        )

            db_for_update = SessionLocal()
            try:
                logger.info(
                    f"[UPLOAD] Directly calling document processor for {doc_id}"
                )
                processing_update = await document_processor.process_document(
                    document_data
                )
                logger.info(
                    f"[UPLOAD] Document processor finished for {doc_id} with status: {processing_update.status}"
                )

                db_document_to_update = (
                    db_for_update.query(Document).filter(Document.id == doc_id).first()
                )
                if db_document_to_update:
                    db_document_to_update.status = processing_update.status
                    db_document_to_update.page_count = processing_update.page_count
                    db_document_to_update.error = processing_update.error
                    if processing_update.author is not None:
                        db_document_to_update.author = processing_update.author
                    if processing_update.date is not None:
                        db_document_to_update.date = processing_update.date
                    if processing_update.document_type is not None:
                        db_document_to_update.document_type = (
                            processing_update.document_type
                        )

                    db_for_update.commit()
                    db_for_update.refresh(db_document_to_update)
                    logger.info(
                        f"[UPLOAD] Database updated with final processing status for {doc_id}"
                    )

                    results.append(
                        DocumentResponse(
                            id=db_document_to_update.id,
                            name=db_document_to_update.name,
                            status=db_document_to_update.status.value,
                            file_type=db_document_to_update.file_type,
                            upload_date=(
                                db_document_to_update.upload_date.isoformat()
                                if db_document_to_update.upload_date
                                else None
                            ),
                            document_type=db_document_to_update.document_type,
                            author=db_document_to_update.author,
                            date=db_document_to_update.date,
                            page_count=db_document_to_update.page_count,
                            error=db_document_to_update.error,
                            message=f"Document processed with status: {db_document_to_update.status.value}",
                        )
                    )
                else:
                    logger.error(
                        f"[UPLOAD] Document {doc_id} not found in DB after processing attempt."
                    )
                    results.append(
                        DocumentResponse(
                            id=doc_id,
                            name=current_document_name,
                            status=DocumentStatus.ERROR.value,
                            error="Document not found in DB after processing.",
                            message="Processing status could not be updated.",
                        )
                    )

            except Exception as e:
                db_for_update.rollback()
                logger.error(
                    f"[UPLOAD] Exception during processing for {doc_id}: {str(e)}",
                    exc_info=True,
                )
                db_document_to_update = (
                    db_for_update.query(Document).filter(Document.id == doc_id).first()
                )
                if db_document_to_update:
                    if db_document_to_update.status != DocumentStatus.ERROR.value:
                        db_document_to_update.status = DocumentStatus.ERROR.value
                        db_document_to_update.error = f"Processing failed: {str(e)}"
                        try:
                            db_for_update.commit()
                            db_for_update.refresh(db_document_to_update)
                        except Exception as commit_e:
                            logger.error(
                                f"Failed to commit ERROR status after processing crash for {doc_id}: {str(commit_e)}",
                                exc_info=True,
                            )

                    results.append(
                        DocumentResponse(
                            id=db_document_to_update.id,
                            name=db_document_to_update.name,
                            status=db_document_to_update.status.value,
                            file_type=db_document_to_update.file_type,
                            upload_date=(
                                db_document_to_update.upload_date.isoformat()
                                if db_document_to_update.upload_date
                                else None
                            ),
                            document_type=db_document_to_update.document_type,
                            author=db_document_to_update.author,
                            date=db_document_to_update.date,
                            page_count=db_document_to_update.page_count,
                            error=db_document_to_update.error,
                            message=f"Processing failed: {str(e)}",
                        )
                    )
                else:
                    results.append(
                        DocumentResponse(
                            id=doc_id,
                            name=current_document_name,
                            status=DocumentStatus.ERROR.value,
                            error=f"Processing failed: {str(e)}. Document not found in DB to update status.",
                            message="Processing failed.",
                        )
                    )

            finally:
                db_for_update.close()

        except Exception as e:
            logger.error(
                f"[UPLOAD] Unexpected error processing file {file.filename}: {str(e)}",
                exc_info=True,
            )
            results.append(
                DocumentResponse(
                    id=doc_id,
                    name=file.filename,
                    status=DocumentStatus.ERROR.value,
                    error=f"An unexpected error occurred: {str(e)}",
                    message="An unexpected error occurred during upload.",
                )
            )

    logger.info(
        f"[UPLOAD] Finished processing all files. Returning {len(results)} results."
    )
    return results


@router.get("/", response_model=DocumentList)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List all uploaded documents with optional filtering"""
    try:
        query = db.query(Document)
        if status:
            try:
                status_enum = DocumentStatus[status.upper()]
                query = query.filter(Document.status == status_enum.value)
            except KeyError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status value. Must be one of: {', '.join([s.name for s in DocumentStatus])}",
                )
        if document_type:
            query = query.filter(Document.document_type == document_type)
        if author:
            query = query.filter(Document.author == author)

        db_documents = query.offset(skip).limit(limit).all()

        documents = []
        for doc in db_documents:
            documents.append(
                DocumentResponse(
                    id=doc.id,
                    name=doc.name,
                    status=doc.status.value, 
                    document_type=doc.document_type,
                    author=doc.author,
                    date=doc.date,
                    upload_date=(
                        doc.upload_date.isoformat() if doc.upload_date else None
                    ),
                    file_type=doc.file_type,
                    page_count=doc.page_count,
                    error=doc.error,  
                )
            )
        return DocumentList(documents=documents, total=len(documents))
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error listing documents: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document details by ID"""
    try:
        db = SessionLocal()
        document = db.query(Document).filter(Document.id == document_id).first()
        db.close()

        if not document:
            document = await vector_store.get_document(document_id)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            return DocumentResponse(
                id=document.id,
                name=document.name,
                status=document.status, 
            )

        return DocumentResponse(
            id=document.id,
            name=document.name,
            status=document.status.value,  
            document_type=document.document_type,
            author=document.author,
            date=document.date,
            upload_date=(
                document.upload_date.isoformat() if document.upload_date else None
            ),
            file_type=document.file_type,
            page_count=document.page_count,
            error=document.error, 
        )

    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting document: {str(e)}")


@router.delete("/{document_id}", response_model=DocumentResponse)
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document by ID"""
    try:
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if not db_document:
            raise HTTPException(status_code=404, detail="Document not found")

        await vector_store.delete_document(document_id)

        if db_document.file_path and os.path.exists(db_document.file_path):
            if os.path.commonpath(
                [
                    os.path.abspath(db_document.file_path),
                    os.path.abspath(settings.file_storage.upload_dir),
                ]
            ) == os.path.abspath(
                settings.file_storage.upload_dir
            ) or os.path.commonpath(
                [
                    os.path.abspath(db_document.file_path),
                    os.path.abspath(settings.file_storage.processed_dir),
                ]
            ) == os.path.abspath(
                settings.file_storage.processed_dir
            ): 
                try:
                    os.remove(db_document.file_path)
                    logger.info(
                        f"[DELETE] Successfully deleted file: {db_document.file_path}"
                    )
                except Exception as file_delete_error:
                    logger.error(
                        f"[DELETE] Error deleting physical file {db_document.file_path}: {str(file_delete_error)}",
                        exc_info=True,
                    )
            else:
                logger.warning(
                    f"[DELETE] Attempted to delete file outside of allowed directories: {db_document.file_path}"
                )

        processed_path = os.path.join(
            settings.file_storage.processed_dir, f"{document_id}.txt"
        )
        if os.path.exists(processed_path):
            try:
                os.remove(processed_path)
                logger.info(
                    f"[DELETE] Successfully deleted processed file: {processed_path}"
                )
            except Exception as processed_delete_error:
                logger.error(
                    f"[DELETE] Error deleting processed file {processed_path}: {str(processed_delete_error)}",
                    exc_info=True,
                )

        db.delete(db_document)
        db.commit()
        logger.info(
            f"[DELETE] Successfully deleted document {document_id} from database."
        )

        return DocumentResponse(
            id=document_id,
            name=db_document.name,
            status="deleted",
            message="Document deleted successfully",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting document: {str(e)}"
        )


@router.get("/by-ids", response_model=List[DocumentResponse])
async def get_documents_by_ids(document_ids: List[str] = Query(...)):
    """Get multiple documents by their IDs"""
    documents = []
    db = SessionLocal()
    try:
        db_documents = db.query(Document).filter(Document.id.in_(document_ids)).all()
        
        documents = [
            DocumentResponse(
                id=doc.id,
                name=doc.name,
                status=doc.status.value,  
                document_type=doc.document_type,
                author=doc.author,
                date=doc.date,
                upload_date=doc.upload_date.isoformat() if doc.upload_date else None,
                file_type=doc.file_type,
                page_count=doc.page_count,
                error=doc.error,  
            )
            for doc in db_documents
        ]
    except Exception as e:
        logger.error(f"Error getting documents by IDs: {str(e)}")
    finally:
        db.close()
    return documents


@router.get("/{document_id}/content")
async def get_document_content(document_id: str, page: Optional[int] = Query(None)):
    """Get the processed content of a document"""
    try:
        db = SessionLocal()
        document = db.query(Document).filter(Document.id == document_id).first()
        db.close()

        if not document:
            raise HTTPException(
                status_code=404, detail="Document not found in database"
            )

        if document.status != DocumentStatus.PROCESSED.value:
            raise HTTPException(
                status_code=400,
                detail=f"Document is not fully processed yet. Current status: {document.status}",
            )

        content = await document_processor.get_document_content(document_id, page)

        return {"content": content}
    except Exception as e:
        logger.error(f"Error getting content for document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting document content: {str(e)}"
        )


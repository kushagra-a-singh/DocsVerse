from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


class QueryRequest(BaseModel):
    query: str
    document_ids: List[str]


@router.post("/with-themes")
async def query_with_themes(request: QueryRequest):
    try:
        response = await chat_service.process_query(request.query, request.document_ids)
        
        # TEMPORARY DEBUGGING:
        print("\n=== FULL RESPONSE ===")
        print(response)
        if hasattr(response, 'document_responses'):
            for doc in response.document_responses:
                print(f"\nDocument {doc.document_id}:")
                print(doc.extracted_answer)
        
        return response
    except Exception as e:
        print(f"!!! ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
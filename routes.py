from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
generator = GeminiDocumentGenerator()


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    parties: str = Field(..., min_length=2, max_length=3000)
    terms: str = Field(..., min_length=2, max_length=10000)
    effective_date: str = Field(..., min_length=2, max_length=100)
    jurisdiction: Optional[str] = Field(default="", max_length=200)


class DocumentResponse(BaseModel):
    success: bool
    content: str
    demo_mode: bool = False
    model: str


@router.post("/generate", response_model=DocumentResponse, tags=["Documents"])
def generate_document(request: DocumentRequest):
    try:
        result = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
            jurisdiction=request.jurisdiction or "",
        )
        return DocumentResponse(
            success=True,
            content=result["content"],
            demo_mode=result["demo_mode"],
            model=result["model"],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {exc}")

from fastapi import APIRouter, HTTPException

from .ai_core.gemini_generator import GeminiDocumentGenerator
from .models import DocumentRequest, DocumentResponse
from .services.text_utils import sanitize_text

router = APIRouter()
_generator = GeminiDocumentGenerator()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "LegalEase API", "ai_configured": bool(_generator.api_key), "model": _generator.model}


@router.post("/generate", response_model=DocumentResponse)
def generate_document(request: DocumentRequest) -> DocumentResponse:
    try:
        result = _generator.generate_document(
            request.document_type,
            request.parties,
            request.terms,
            request.effective_date,
            request.jurisdiction,
        )
        return DocumentResponse(
            document_type=request.document_type,
            content=sanitize_text(result.text),
            model=result.model,
            fallback=result.fallback,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Document generation failed: {exc}") from exc

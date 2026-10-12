from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=2, max_length=120)
    parties: str = Field(..., min_length=3, max_length=5000)
    terms: str = Field(..., min_length=3, max_length=12000)
    effective_date: str = Field(..., min_length=2, max_length=100)
    jurisdiction: str = Field(default="", max_length=300)

    @field_validator("document_type", "parties", "terms", "effective_date", "jurisdiction")
    @classmethod
    def strip_strings(cls, value: str) -> str:
        return value.strip()


class DocumentResponse(BaseModel):
    document_type: str
    content: str
    model: str
    fallback: bool = False

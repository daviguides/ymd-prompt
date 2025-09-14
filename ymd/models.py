from __future__ import annotations
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

class Prompt(BaseModel):
    id: str = Field(..., min_length=1)
    kind: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1, description="Semver string, e.g., 0.2.0")
    title: str = Field(..., min_length=1)

    system: str
    instructions: str
    user: str

    developer: Optional[str] = None
    expected_output: Optional[str] = None

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not v or not any(ch.isdigit() for ch in v):
            raise ValueError("version must contain at least one digit, e.g., '0.1.0'")
        return v

    def sections(self) -> Dict[str, str]:
        data: Dict[str, Any] = self.model_dump()
        out: Dict[str, str] = {}
        for key in ("system", "instructions", "developer", "expected_output", "user"):
            val = data.get(key)
            if isinstance(val, str):
                out[key] = val
        return out

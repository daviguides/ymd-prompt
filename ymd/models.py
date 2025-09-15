from pydantic import BaseModel, Field, field_validator


class DefaultMeta(BaseModel):
    id: str | None = Field(None, min_length=1)
    kind: str | None = Field(None, min_length=1)
    version: str | None = Field(
        None,
        min_length=1,
        description="version string, e.g., 0.2.0",
    )
    title: str | None = Field(None, min_length=1)

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not v or not any(ch.isdigit() for ch in v):
            raise ValueError(
                "version must contain at least one digit, e.g., '0.1.0'",
            )
        return v


class DefaultSections(BaseModel):
    system: str | None = None
    instructions: str | None = None
    expected_output: str | None = None
    user: str | None = None

    def keys(self) -> dict[str, str]:
        return self.model_dump().keys()

from pydantic import BaseModel, ConfigDict, Field


class AgeResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"age": 42, "birth_year": 1984, "current_year": 2026}]}
    )

    age: int = Field(description="Age in years, computed as current_year - birth_year")
    birth_year: int
    current_year: int

from pydantic import BaseModel, ConfigDict


class HobbyResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{"id": 1, "name": "Gardening"}]})

    id: int
    name: str

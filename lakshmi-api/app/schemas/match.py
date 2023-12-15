from typing import List

from app.schemas.base import Base
from app.schemas.pyobjectid import PyObjectId
from bson import ObjectId
from pydantic import BaseModel, Field, conint

weight = conint(ge=0, le=100)


class Recommendation(BaseModel):
    candidate_id: str
    score: conint(ge=0, le=100) = 0


class Match(Base):
    """Recomendações de candidatos
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    position_id: int = Field(...)
    candidates: List[Recommendation] = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "position_id": 99,
                "candidates": [
                    {
                        "candidate_id": 20,
                        "score": 93
                    },
                    {
                        "candidate_id": 27,
                        "score": 86
                    }
                ],
                "created_at": "2022-06-13T20:50:26.701495",
                "updated_at": None
            }
        }

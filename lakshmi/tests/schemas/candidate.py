from typing import Dict, Optional

from tests.schemas.base import Base
from tests.schemas.pyobjectid import PyObjectId
from bson import ObjectId
from pydantic import BaseModel, Field, conint


class Candidate(Base):
    """Candidate

    Representa um candidato
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    candidate_id: str = Field(...)
    carreer_id: int = Field(...)  # TODO: allow multiple carreers
    traits: Dict[str, conint(ge=0, le=100)] = Field(...)
    dirty: bool = True

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "candidate_id": "1752",
                "carreer_id": 2,
                "traits": {"1": 10, "2": 20},
                "created_at": "2022-06-13T20:41:45.404717",
                "updated_at": None,
                "dirty": True
            }
        }


class UpdateCandidate(BaseModel):
    candidate_id: Optional[str]  # TODO: avoid changing candidate_id
    carreer_id: Optional[int]
    traits: Optional[Dict[str, int]]

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "candidate_id": "1752",
                "carreer_id": 2,
                "traits": {"1": 10, "2": 20, "3": 30}
            }
        }

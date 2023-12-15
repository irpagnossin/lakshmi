from typing import Dict, List, Optional

from tests.schemas.base import Base
from tests.schemas.pyobjectid import PyObjectId
from bson import ObjectId
from pydantic import Field, conint

weight = conint(ge=0, le=100)


class JobPosition(Base):
    """Vaga de trabalho

    Representa uma vaga de trabalho
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    position_id: int = Field(...)
    carreer_id: int = Field(...)
    traits: Dict[str, List[int]] = Field(...)
    weights: Dict[str, weight] = Field(...)
    dirty: bool = True

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "position_id": 99,
                "carreer_id": 2,
                "traits": {
                    "11": [1, 2],
                    "22": [3, 4]
                },
                "weights": {
                    "11": 50,
                    "22": 80
                },
                "created_at": "2022-06-13T20:50:26.701495",
                "updated_at": None,
                "dirty": False
            }
        }


class UpdateJobPosition(Base):
    position_id: Optional[int]
    carreer_id: Optional[int]
    traits: Optional[Dict[str, List[int]]] = Field(...)
    weights: Optional[Dict[str, weight]] = Field(...)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "position_id": 99,
                "carreer_id": 2,
                "traits": {
                    "11": [1, 2],
                    "22": [3, 5],
                    "33": [6]
                },
                "weights": {
                    "11": 50,
                    "22": 80,
                    "33": 30
                }
            }
        }

from app.schemas.base import Base
from app.schemas.pyobjectid import PyObjectId
from bson import ObjectId
from pydantic import EmailStr, Field


class User(Base):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr = Field(...)
    password: str = Field(...)

    @classmethod
    async def find(self, database, email):
        user = await database.users.find_one({'email': email})

        if user is not None:
            return User(email=user['email'], password=user['password'])

    def serialize(self):
        return self.email

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "user@company.com",
                "password": "user"
            }
        }

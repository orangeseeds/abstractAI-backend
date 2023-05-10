from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, EmailStr


class SummaryRequestSchema(BaseModel):
    request: str = Field(...)
    domain: str | None = Field(...)
    createdAt: datetime | None = Field(...)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "request": "request text",
                "domain": "localhost",
                "createdAt": "2023-05-10T12:33:30.724Z",
            }
        }


class SummaryBaseSchema(BaseModel):
    id: str | None = None
    request: str
    response: str
    domain: str | None = None
    createdAt: datetime | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListSummaryResponse(BaseModel):
    status: str
    results: int
    notes: List[SummaryRequestSchema]


class UserSchema(BaseModel):
    user_name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "user_name": "Abdulazeez Abdulazeez Adeshina",
                "email": "abdulazeez@x.com",
                "password": "weakpassword",
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "abdulazeez@x.com",
                "password": "weakpassword",
            }
        }

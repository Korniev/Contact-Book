from datetime import date

from pydantic import BaseModel, Field, EmailStr


class ContactSchema(BaseModel):
    name: str = Field(max_length=150)
    surname: str = Field(max_length=150)
    email: EmailStr
    phone: str
    birthday: date


class ContactUpdate(BaseModel):
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date


class ContactResponse(BaseModel):
    id: int = 1
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date

    class Config:
        from_attributes = True

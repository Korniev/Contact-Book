from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class ContactSchema(BaseModel):
    name: str = Field(max_length=150)
    surname: str = Field(max_length=150)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?1?\d{9,15}$")
    birthday: date


class ContactUpdate(BaseModel):
    name: Optional[str] = Field(max_length=150)
    surname: Optional[str] = Field(max_length=150)
    email: Optional[EmailStr]
    phone: Optional[str] = Field(None, pattern=r"^\+?1?\d{9,15}$")
    birthday: Optional[date]


class ContactResponse(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date

    class Config:
        from_attributes = True

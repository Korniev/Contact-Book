from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, EmailStr, field_validator


class ContactSchema(BaseModel):
    name: str = Field(max_length=150)
    surname: str = Field(max_length=150)
    email: EmailStr
    phone: str = Field(..., regex=r"^\+?1?\d{9,15}$")
    birthday: date

    @field_validator('birthday')
    def birthday_must_be_in_the_past(self, v):
        if v >= date.today():
            raise ValueError('Birthday must be in the past')
        return v


class ContactUpdate(BaseModel):
    name: Optional[str] = Field(max_length=150)
    surname: Optional[str] = Field(max_length=150)
    email: Optional[EmailStr]
    phone: Optional[str] = Field(None, regex=r"^\+?1?\d{9,15}$")
    birthday: Optional[date]

    @field_validator('birthday')
    def birthday_must_be_in_the_past(self, v):
        if v is not None and v >= date.today():
            raise ValueError('Birthday must be in the past')
        return v


class ContactResponse(BaseModel):
    id: int
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date

    class Config:
        from_attributes = True

from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone_number: str
    birthday: date
    additional_data: str


class ContactUpdateSchema(ContactSchema):
    pass


class ContactResponse(ContactSchema):
    id: int
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None

    class Config:
        from_attributes = True

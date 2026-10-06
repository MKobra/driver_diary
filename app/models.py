from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Trip(BaseModel):
    owner_id: str = ""
    id: str = Field(min_length=1)
    start: datetime
    end: datetime
    amount: int = Field(gt=0)
    payment: Literal["cash", "card"]
    commission: int = Field(ge=0)

    @field_validator("start", "end")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Дата и время должны содержать часовой пояс")
        return value

    @model_validator(mode="after")
    def validate_interval(self) -> "Trip":
        if self.end <= self.start:
            raise ValueError("Время окончания должно быть позже времени начала")
        return self


class UserAccount(BaseModel):
    id: str
    phone: str
    password_hash: str


class RegisterRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str = Field(min_length=8, max_length=128)

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        normalized = "".join(character for character in value if character.isdigit())
        if not 10 <= len(normalized) <= 15:
            raise ValueError("Укажите корректный номер телефона")
        return normalized

    @model_validator(mode="after")
    def validate_passwords(self) -> "RegisterRequest":
        if self.password != self.password_confirm:
            raise ValueError("Пароли не совпадают")
        return self


class LoginRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=32)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str) -> str:
        normalized = "".join(character for character in value if character.isdigit())
        if not 10 <= len(normalized) <= 15:
            raise ValueError("Укажите корректный номер телефона")
        return normalized


class UserPublic(BaseModel):
    id: str
    phone: str


class AuthResponse(BaseModel):
    message: str
    user: UserPublic


class TripResponse(BaseModel):
    message: str
    trip: Trip
    created: bool


class TripPage(BaseModel):
    items: list[Trip]
    page: int
    page_size: int
    total: int
    total_pages: int


class PaymentSummary(BaseModel):
    trips_count: int = 0
    revenue: int = 0
    commission: int = 0
    net: int = 0


class DaySummary(BaseModel):
    date: date
    trips_count: int
    revenue: int
    commission: int
    net: int
    cash: PaymentSummary
    card: PaymentSummary

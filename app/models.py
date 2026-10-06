from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Trip(BaseModel):
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

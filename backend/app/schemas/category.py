from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


def _clean_name(v: str) -> str:
    v = " ".join(v.split())
    if not v:
        raise ValueError("must not be empty")
    if len(v) > 50:
        raise ValueError("must be at most 50 characters")
    return v


class CategoryCreate(BaseModel):
    name: str

    _clean = field_validator("name")(_clean_name)


class CategoryUpdate(BaseModel):
    name: str

    _clean = field_validator("name")(_clean_name)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime

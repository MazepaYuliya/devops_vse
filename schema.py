from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class DogTypeSchema(str, Enum):
    """Class for types of dogs"""

    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"

    class Config:
        orm_mode = True
        use_enum_values = True


class DogSchema(BaseModel):
    """Class for dogs"""

    name: str
    pk: int
    kind: DogTypeSchema

    class Config:
        orm_mode = True
        use_enum_values = True


class TimestampSchema(BaseModel):
    """Class for timestamps of post queries"""

    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

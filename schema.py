from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class DogType(str, Enum):
    """Class for types of dogs"""

    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"

    class Config:
        orm_mode = True
        use_enum_values = True


class Dog(BaseModel):
    """Class for dogs"""

    name: str
    pk: int
    kind: DogType

    class Config:
        orm_mode = True
        use_enum_values = True


class Timestamp(BaseModel):
    """Class for timestamps of post queries"""

    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

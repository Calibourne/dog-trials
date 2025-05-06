from pydantic import BaseModel, Field
from typing import Literal, Union, Optional

class BaseCommand(BaseModel):
    command: str
    performed: bool
    come_method: Optional[str] = None
    fake_sit: Optional[bool] = False

class StrictCommand(BaseCommand):
    command_type: Literal["strict"]
    attempts: int = Field(..., ge=0)

class SoftCommand(BaseCommand):
    command_type: Literal["soft"]
    extra_entries: int = Field(..., ge=0)

# Union type for FastAPI to parse properly
CommandEntry = Union[StrictCommand, SoftCommand]
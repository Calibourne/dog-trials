from pydantic import BaseModel
from typing import List, Literal
from datetime import date
from backend.models.command import CommandEntry

class Trial(BaseModel):
    trial_number: int
    commands: List[CommandEntry]

class Submission(BaseModel):
    date: date
    dog_name: str
    training_location: Literal["in-building", "outdoor"]
    trials: List[Trial]

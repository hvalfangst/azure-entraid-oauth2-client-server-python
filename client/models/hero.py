from typing import Optional
from pydantic import BaseModel


class Hero(BaseModel):
    id: str
    name: str
    race: str
    class_: str  # Avoids conflict with the Python `class` keyword
    level: int
    background: Optional[str] = None
    alignment: Optional[str] = None
    hit_points: int
    armor_class: int
    speed: int
    personality_traits: Optional[str] = None
    ideals: Optional[str] = None
    bonds: Optional[str] = None
    flaws: Optional[str] = None

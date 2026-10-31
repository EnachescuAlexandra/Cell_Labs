
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.rule import TransitionRule


NeighborhoodType = Literal["moore", "von_neumann"]
BoundaryType = Literal["fixed"]
DefaultBehavior = Literal["keep"]


class AutomatonDefinition(BaseModel):
    """
    General definition of a deterministic,
    two-dimensional cellular automaton.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(min_length=1, max_length=100)

    width: int = Field(ge=1, le=100)
    height: int = Field(ge=1, le=100)

    states: list[str] = Field(min_length=2)

    neighborhood: NeighborhoodType = "moore"
    boundary: BoundaryType = "fixed"

    default: DefaultBehavior = "keep"

    rules: list[TransitionRule] = Field(default_factory=list)

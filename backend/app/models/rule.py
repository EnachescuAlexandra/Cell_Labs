
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ComparisonOperator = Literal["==", "!=", "<", "<=", ">", ">="]


class NeighborCondition(BaseModel):
    """
    A condition based on the number of neighboring cells
    that have a specific state.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    state: str = Field(min_length=1)
    operator: ComparisonOperator
    value: int = Field(ge=0, le=8)


class TransitionRule(BaseModel):
    """
    A transition from one cell state to another.

    All conditions must be satisfied for the rule
    to be applicable.

    An empty conditions list means the transition
    is unconditional.
    """

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        populate_by_name=True
    )

    from_state: str = Field(alias="from", min_length=1)
    to: str = Field(min_length=1)
    conditions: list[NeighborCondition] = Field(default_factory=list)

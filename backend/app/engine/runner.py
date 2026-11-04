"""Small, deterministic experiment runner built on the existing engine."""

from pydantic import BaseModel, ConfigDict, Field

from app.engine.simulator import next_generation
from app.models.automaton import AutomatonDefinition
from app.validators.validation_service import validate_configuration


class ExperimentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    generations: int = Field(default=1, ge=1)
    retain_history: bool = False
    save_result: bool = False


def run_simulation(initial_grid: list[list[str]],
                   definition: AutomatonDefinition,
                   config: ExperimentConfig | None = None) -> dict:
    """Run exactly N steps; history includes generation zero when requested.

    Saving is an orchestration decision; this function never performs I/O.
    Without history only the current and next grids are needed during stepping.
    """
    config = ExperimentConfig.model_validate(
        config.model_dump() if config is not None else {}
    )
    validation = validate_configuration(definition, initial_grid)
    if not validation["valid"]:
        raise ValueError(validation["errors"])
    current = [row.copy() for row in initial_grid]
    history = [current] if config.retain_history else None
    for _ in range(config.generations):
        current = next_generation(current, definition)
        if history is not None:
            history.append(current)
    return {"final_state": current, "history": history}

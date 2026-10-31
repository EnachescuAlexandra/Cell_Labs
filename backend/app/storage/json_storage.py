
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.models.automaton import AutomatonDefinition
from app.validators.validation_service import (
    validate_configuration,
)


DEFAULT_SAVE_DIR = (
    Path(__file__).resolve().parents[2] / "saved_runs"
)


def save_transition(
    definition: AutomatonDefinition,
    current_grid: list[list[str]],
    next_grid: list[list[str]],
    save_dir: Path = DEFAULT_SAVE_DIR
) -> Path:
    """Saves the current and next states to JSON."""

    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    run_id = uuid4().hex
    file_path = save_dir / f"{run_id}.json"

    data = {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(),
        "automaton": definition.model_dump(by_alias=True),
        "initial_state": current_grid,
        "next_state": next_grid
    }

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return file_path


def load_transition(file_path: Path) -> dict:
    """Loads and validates a previously saved transition."""

    file_path = Path(file_path)

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    definition = AutomatonDefinition.model_validate(
        data["automaton"]
    )

    validation = validate_configuration(
        definition,
        data["initial_state"]
    )

    if not validation["valid"]:
        raise ValueError(validation["errors"])

    from app.validators.automaton_validator import (
        validate_initial_state,
    )

    errors = validate_initial_state(
        definition, data["next_state"]
    )

    if errors:
        raise ValueError(errors)

    return data

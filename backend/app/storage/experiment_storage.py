"""Versioned experiment records, separate from legacy transition snapshots."""

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.engine.runner import ExperimentConfig
from app.engine.simulator import next_generation
from app.models.automaton import AutomatonDefinition
from app.storage.json_storage import DEFAULT_SAVE_DIR
from app.validators.automaton_validator import validate_initial_state
from app.validators.validation_service import validate_configuration


def validate_record(data: dict) -> None:
    if not isinstance(data, dict) or data.get("format") != "cellab-experiment":
        raise ValueError("Not a CelLab experiment record.")
    if type(data.get("version")) is not int or data["version"] != 1:
        raise ValueError("Unsupported experiment record version.")
    definition = AutomatonDefinition.model_validate(data["automaton"])
    config = ExperimentConfig.model_validate(data["experiment"])
    validation = validate_configuration(definition, data["initial_state"])
    if not validation["valid"]:
        raise ValueError(validation["errors"])
    errors = validate_initial_state(definition, data["final_state"])
    if errors:
        raise ValueError(errors)
    history = data.get("history")
    if config.retain_history:
        if not isinstance(history, list) or len(history) != config.generations + 1:
            raise ValueError("History must contain generations 0 through N.")
        for grid in history:
            errors = validate_initial_state(definition, grid)
            if errors:
                raise ValueError(errors)
        if history[0] != data["initial_state"] or history[-1] != data["final_state"]:
            raise ValueError("History endpoints do not match the stored states.")
    elif history is not None:
        raise ValueError("History is present but retention is disabled.")
    current = data["initial_state"]
    for index in range(config.generations):
        current = next_generation(current, definition)
        if history is not None and current != history[index + 1]:
            raise ValueError(f"Incorrect stored generation {index + 1}.")
    if current != data["final_state"]:
        raise ValueError("Final state does not match the experiment.")


def save_experiment(
    definition: AutomatonDefinition,
    initial_grid: list[list[str]],
    config: ExperimentConfig,
    result: dict,
    save_dir: Path = DEFAULT_SAVE_DIR,
) -> Path:
    data = {
        "format": "cellab-experiment", "version": 1,
        "run_id": uuid4().hex,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "automaton": definition.model_dump(by_alias=True),
        "experiment": config.model_dump(),
        "initial_state": initial_grid,
        "final_state": result["final_state"],
        "history": result["history"],
    }
    validate_record(data)
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    path = save_dir / f"{data['run_id']}.json"
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    return path


def load_experiment(path: Path) -> dict:
    with Path(path).open(encoding="utf-8") as file:
        data = json.load(file)
    validate_record(data)
    return data

"""Regression coverage for the existing >= 1 Crystal Growth rule."""

import json
from pathlib import Path

from app.engine.simulator import next_generation
from app.models.automaton import AutomatonDefinition
from app.validators.validation_service import validate_configuration


def test_crystal_growth_expands_then_remains_stable():
    path = Path(__file__).resolve().parents[1] / "automata/crystal_growth.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    validation = validate_configuration(data["automaton"], data["initial_state"])
    assert validation["valid"], validation["errors"]
    definition = AutomatonDefinition.model_validate(data["automaton"])

    first = next_generation(data["initial_state"], definition)
    assert first == [
        ["EMPTY"] * 5,
        ["EMPTY", "CRYSTAL", "CRYSTAL", "CRYSTAL", "EMPTY"],
        ["EMPTY", "CRYSTAL", "CRYSTAL", "CRYSTAL", "EMPTY"],
        ["EMPTY", "CRYSTAL", "CRYSTAL", "CRYSTAL", "EMPTY"],
        ["EMPTY"] * 5,
    ]

    second = next_generation(first, definition)
    # >= 1 fills the entire outer ring, including all four corners: 16 additions.
    assert second == [["CRYSTAL"] * 5 for _ in range(5)]
    assert all(second[row][col] == "CRYSTAL"
               for row, col in ((0, 0), (0, 4), (4, 0), (4, 4)))
    current = second
    for _ in range(3):
        current = next_generation(current, definition)
        assert current == second

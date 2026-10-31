
import json
from pathlib import Path

import pytest

from app.models.automaton import AutomatonDefinition
from app.engine.simulator import next_generation
from app.storage.json_storage import (
    save_transition,
    load_transition,
)
from app.validators.validation_service import (
    validate_configuration,
)


AUTOMATA_DIR = Path(__file__).resolve().parents[1] / "automata"


def load_example(filename):
    """Loads and validates an automaton from JSON."""

    with (AUTOMATA_DIR / filename).open(
        "r", encoding="utf-8"
    ) as file:
        data = json.load(file)

    result = validate_configuration(
        data["automaton"],
        data["initial_state"]
    )

    assert result["valid"], result["errors"]

    definition = AutomatonDefinition.model_validate(
        data["automaton"]
    )

    return definition, data["initial_state"]


@pytest.mark.parametrize(
    "filename",
    [
        "game_of_life.json",
        "brians_brain.json",
        "forest_fire.json",
        "cyclic_automaton.json"
    ]
)
def test_automata_generate_next_state(filename):
    """
    Verifies that the generic engine generates
    a valid next state for every automaton.
    """

    definition, grid = load_example(filename)

    result = next_generation(grid, definition)

    assert len(result) == definition.height

    assert all(
        len(row) == definition.width
        for row in result
    )

    assert all(
        cell in definition.states
        for row in result
        for cell in row
    )


def test_game_of_life_blinker():
    """
    A vertical Blinker becomes horizontal
    after exactly one transition.
    """

    definition, grid = load_example(
        "game_of_life.json"
    )

    result = next_generation(grid, definition)

    expected = [["DEAD"] * 5 for _ in range(5)]

    expected[2][1] = "ALIVE"
    expected[2][2] = "ALIVE"
    expected[2][3] = "ALIVE"

    assert result == expected


def test_forest_fire():
    """
    The center FIRE becomes EMPTY.
    All surrounding TREE cells become FIRE.
    """

    definition, grid = load_example(
        "forest_fire.json"
    )

    result = next_generation(grid, definition)

    expected = [
        ["FIRE", "FIRE", "FIRE"],
        ["FIRE", "EMPTY", "FIRE"],
        ["FIRE", "FIRE", "FIRE"]
    ]

    assert result == expected


def test_brians_brain():
    """
    FIRING cells become DYING and OFF cells
    with exactly two FIRING neighbors become FIRING.
    """

    definition, grid = load_example(
        "brians_brain.json"
    )

    result = next_generation(grid, definition)

    expected = [
        ["OFF", "OFF", "FIRING", "OFF", "OFF"],
        ["OFF", "DYING", "FIRING", "DYING", "OFF"],
        ["OFF", "OFF", "FIRING", "OFF", "OFF"],
        ["OFF", "OFF", "OFF", "OFF", "OFF"],
        ["OFF", "OFF", "OFF", "OFF", "OFF"]
    ]

    assert result == expected


def test_cyclic_automaton():
    """
    Verifies the cyclic transitions:
    0 -> 1 -> 2 -> 3 -> 0

    A transition occurs only when at least
    two neighbors have the next cyclic state.
    """

    definition, grid = load_example(
        "cyclic_automaton.json"
    )

    result = next_generation(grid, definition)

    expected = [
        ["0", "0", "2", "1"],
        ["0", "3", "2", "2"],
        ["3", "3", "2", "2"]
    ]

    assert result == expected


def test_original_grid_unchanged():
    """
    The generic engine must not modify
    the original generation.
    """

    definition, grid = load_example(
        "forest_fire.json"
    )

    original = [row.copy() for row in grid]

    next_generation(grid, definition)

    assert grid == original


def test_save_and_recover(tmp_path):
    """
    Saves a transition to JSON and verifies
    that all essential data can be recovered.
    """

    definition, grid = load_example(
        "forest_fire.json"
    )

    result = next_generation(grid, definition)

    file_path = save_transition(
        definition,
        grid,
        result,
        save_dir=tmp_path
    )

    assert file_path.exists()

    recovered = load_transition(file_path)

    assert recovered["automaton"]["name"] == "Forest Fire"
    assert recovered["initial_state"] == grid
    assert recovered["next_state"] == result

    assert recovered["automaton"] == (
        definition.model_dump(by_alias=True)
    )

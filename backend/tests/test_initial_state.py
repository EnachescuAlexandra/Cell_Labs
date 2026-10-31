
from app.models.automaton import AutomatonDefinition
from app.validators.automaton_validator import validate_initial_state


def create_automaton():
    return AutomatonDefinition(
        name="Forest Fire",
        width=3,
        height=2,
        states=["EMPTY", "TREE", "FIRE"],
        neighborhood="moore",
        boundary="fixed",
        default="keep",
        rules=[]
    )


def test_valid_initial_state():
    automaton = create_automaton()

    grid = [
        ["TREE", "FIRE", "EMPTY"],
        ["EMPTY", "TREE", "TREE"]
    ]

    assert validate_initial_state(automaton, grid) == []


def test_invalid_row_count():
    automaton = create_automaton()

    grid = [
        ["TREE", "FIRE", "EMPTY"]
    ]

    errors = validate_initial_state(automaton, grid)

    assert len(errors) == 1
    assert "Expected 2 rows" in errors[0]["message"]


def test_invalid_column_count():
    automaton = create_automaton()

    grid = [
        ["TREE", "FIRE"],
        ["EMPTY", "TREE", "TREE"]
    ]

    errors = validate_initial_state(automaton, grid)

    assert len(errors) == 1
    assert "Expected 3 columns" in errors[0]["message"]


def test_unknown_cell_state():
    automaton = create_automaton()

    grid = [
        ["TREE", "WATER", "EMPTY"],
        ["EMPTY", "TREE", "TREE"]
    ]

    errors = validate_initial_state(automaton, grid)

    assert len(errors) == 1
    assert errors[0]["field"] == "initial_state[0][1]"
    assert "Unknown state 'WATER'" in errors[0]["message"]


def test_non_string_cell():
    automaton = create_automaton()

    grid = [
        ["TREE", 10, "EMPTY"],
        ["EMPTY", "TREE", "TREE"]
    ]

    errors = validate_initial_state(automaton, grid)

    assert len(errors) == 1
    assert errors[0]["field"] == "initial_state[0][1]"
    assert "must be a string" in errors[0]["message"]


def test_invalid_grid_type():
    automaton = create_automaton()

    errors = validate_initial_state(automaton, "TREE")

    assert len(errors) == 1
    assert errors[0]["field"] == "initial_state"


def test_multiple_errors():
    automaton = create_automaton()

    grid = [
        ["TREE", "WATER"],
        ["EMPTY", 10, "TREE"]
    ]

    errors = validate_initial_state(automaton, grid)

    assert len(errors) == 3


def test_invalid_row_type():
    automaton = create_automaton()

    grid = [
        "TREE",
        ["EMPTY", "TREE", "FIRE"]
    ]

    errors = validate_initial_state(automaton, grid)

    assert len(errors) == 1
    assert errors[0]["field"] == "initial_state[0]"


def test_empty_grid():
    automaton = create_automaton()

    errors = validate_initial_state(automaton, [])

    assert len(errors) == 1
    assert "Expected 2 rows" in errors[0]["message"]


from app.models.automaton import AutomatonDefinition
from app.validators.validation_service import (
    validate_configuration,
)


def get_valid_definition():
    return {
        "name": "Forest Fire",
        "width": 3,
        "height": 2,
        "states": ["EMPTY", "TREE", "FIRE"],
        "neighborhood": "moore",
        "boundary": "fixed",
        "default": "keep",
        "rules": [
            {
                "from": "FIRE",
                "to": "EMPTY",
                "conditions": []
            },
            {
                "from": "TREE",
                "to": "FIRE",
                "conditions": [
                    {
                        "state": "FIRE",
                        "operator": ">=",
                        "value": 1
                    }
                ]
            }
        ]
    }


def get_valid_grid():
    return [
        ["TREE", "FIRE", "TREE"],
        ["EMPTY", "TREE", "EMPTY"]
    ]


def test_valid_configuration():
    result = validate_configuration(
        get_valid_definition(),
        get_valid_grid()
    )

    assert result == {
        "valid": True,
        "errors": []
    }


def test_accepts_pydantic_model():
    automaton = AutomatonDefinition.model_validate(
        get_valid_definition()
    )

    result = validate_configuration(
        automaton,
        get_valid_grid()
    )

    assert result["valid"] is True
    assert result["errors"] == []


def test_invalid_grid():
    grid = get_valid_grid()
    grid[0][1] = "WATER"

    result = validate_configuration(
        get_valid_definition(),
        grid
    )

    assert result["valid"] is False
    assert any(
        error["field"] == "initial_state[0][1]"
        for error in result["errors"]
    )


def test_invalid_rule():
    definition = get_valid_definition()
    definition["rules"][0]["to"] = "UNKNOWN"

    result = validate_configuration(
        definition,
        get_valid_grid()
    )

    assert result["valid"] is False
    assert any(
        error["field"] == "rules[0].to"
        for error in result["errors"]
    )


def test_multiple_validation_errors():
    definition = get_valid_definition()
    definition["rules"][0]["to"] = "UNKNOWN"

    grid = get_valid_grid()
    grid[0][0] = "WATER"

    result = validate_configuration(
        definition,
        grid
    )

    assert result["valid"] is False
    assert len(result["errors"]) == 2


def test_invalid_structure():
    definition = get_valid_definition()
    definition["width"] = -3

    result = validate_configuration(
        definition,
        get_valid_grid()
    )

    assert result["valid"] is False
    assert any(
        error["field"] == "width"
        for error in result["errors"]
    )


def test_invalid_automaton_type():
    result = validate_configuration(
        "not an automaton",
        get_valid_grid()
    )

    assert result["valid"] is False
    assert result["errors"][0]["field"] == "automaton"


def test_invalid_nested_condition():
    definition = get_valid_definition()
    definition["rules"][1]["conditions"][0]["value"] = -2

    result = validate_configuration(
        definition,
        get_valid_grid()
    )

    assert result["valid"] is False
    assert any(
        error["field"] == "rules[1].conditions[0].value"
        for error in result["errors"]
    )

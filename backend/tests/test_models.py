
import pytest

from pydantic import ValidationError

from app.models.automaton import AutomatonDefinition


def get_valid_automaton():
    return {
        "name": "Custom Automaton",
        "width": 5,
        "height": 5,
        "states": ["EMPTY", "WATER", "ICE"],
        "neighborhood": "moore",
        "boundary": "fixed",
        "default": "keep",
        "rules": [
            {
                "from": "WATER",
                "to": "ICE",
                "conditions": [
                    {
                        "state": "ICE",
                        "operator": ">=",
                        "value": 3
                    }
                ]
            }
        ]
    }


def test_valid_automaton():
    automaton = AutomatonDefinition.model_validate(
        get_valid_automaton()
    )

    assert automaton.name == "Custom Automaton"
    assert automaton.width == 5
    assert automaton.height == 5
    assert len(automaton.states) == 3
    assert len(automaton.rules) == 1


def test_invalid_width():
    data = get_valid_automaton()
    data["width"] = -5

    with pytest.raises(ValidationError):
        AutomatonDefinition.model_validate(data)


def test_invalid_operator():
    data = get_valid_automaton()
    data["rules"][0]["conditions"][0]["operator"] = "approximately"

    with pytest.raises(ValidationError):
        AutomatonDefinition.model_validate(data)


def test_invalid_neighborhood():
    data = get_valid_automaton()
    data["neighborhood"] = "random"

    with pytest.raises(ValidationError):
        AutomatonDefinition.model_validate(data)


def test_invalid_neighbor_count():
    data = get_valid_automaton()
    data["rules"][0]["conditions"][0]["value"] = 10

    with pytest.raises(ValidationError):
        AutomatonDefinition.model_validate(data)


def test_json_uses_from_alias():
    automaton = AutomatonDefinition.model_validate(
        get_valid_automaton()
    )

    exported = automaton.model_dump(by_alias=True)

    assert exported["rules"][0]["from"] == "WATER"
    assert "from_state" not in exported["rules"][0]


def test_unknown_field_is_rejected():
    data = get_valid_automaton()
    data["unknown_field"] = 123

    with pytest.raises(ValidationError):
        AutomatonDefinition.model_validate(data)

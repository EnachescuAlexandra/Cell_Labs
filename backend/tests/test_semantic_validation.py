
from app.models.automaton import AutomatonDefinition
from app.validators.automaton_validator import validate_automaton


def create_automaton(
    states=None,
    rules=None,
    width=5,
    height=5,
    neighborhood="moore"
):
    return AutomatonDefinition(
        name="Test Automaton",
        width=width,
        height=height,
        states=states if states is not None else [
            "EMPTY", "TREE", "FIRE"
        ],
        neighborhood=neighborhood,
        boundary="fixed",
        default="keep",
        rules=rules if rules is not None else []
    )


def has_error(errors, text):
    return any(
        text.lower() in error["message"].lower()
        for error in errors
    )


def test_valid_automaton():
    automaton = create_automaton(
        rules=[
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
    )

    assert validate_automaton(automaton) == []


def test_duplicate_states():
    automaton = create_automaton(
        states=["EMPTY", "TREE", "TREE"]
    )

    errors = validate_automaton(automaton)

    assert has_error(errors, "Duplicate state")


def test_empty_state_name():
    automaton = create_automaton(
        states=["EMPTY", "", "FIRE"]
    )

    errors = validate_automaton(automaton)

    assert has_error(errors, "State names cannot be empty")


def test_unknown_source_state():
    automaton = create_automaton(
        rules=[
            {
                "from": "WATER",
                "to": "FIRE",
                "conditions": []
            }
        ]
    )

    errors = validate_automaton(automaton)

    assert has_error(errors, "Unknown source state")


def test_unknown_destination_state():
    automaton = create_automaton(
        rules=[
            {
                "from": "TREE",
                "to": "WATER",
                "conditions": []
            }
        ]
    )

    errors = validate_automaton(automaton)

    assert has_error(errors, "Unknown destination state")


def test_unknown_condition_state():
    automaton = create_automaton(
        rules=[
            {
                "from": "TREE",
                "to": "FIRE",
                "conditions": [
                    {
                        "state": "WATER",
                        "operator": "==",
                        "value": 2
                    }
                ]
            }
        ]
    )

    errors = validate_automaton(automaton)

    assert has_error(errors, "Unknown neighbor state")


def test_impossible_conditions():
    automaton = create_automaton(
        rules=[
            {
                "from": "TREE",
                "to": "FIRE",
                "conditions": [
                    {
                        "state": "FIRE",
                        "operator": "==",
                        "value": 2
                    },
                    {
                        "state": "FIRE",
                        "operator": "==",
                        "value": 3
                    }
                ]
            }
        ]
    )

    errors = validate_automaton(automaton)

    assert has_error(errors, "cannot be satisfied")


def test_impossible_combined_neighbor_counts():
    automaton = create_automaton(
        rules=[
            {
                "from": "TREE",
                "to": "FIRE",
                "conditions": [
                    {
                        "state": "FIRE",
                        "operator": ">=",
                        "value": 6
                    },
                    {
                        "state": "TREE",
                        "operator": ">=",
                        "value": 6
                    }
                ]
            }
        ]
    )

    errors = validate_automaton(automaton)

    assert has_error(errors, "cannot be satisfied")


def test_conflicting_rules():
    automaton = create_automaton(
        rules=[
            {
                "from": "TREE",
                "to": "FIRE",
                "conditions": []
            },
            {
                "from": "TREE",
                "to": "EMPTY",
                "conditions": []
            }
        ]
    )

    errors = validate_automaton(automaton)

    assert has_error(errors, "Conflicting rules")


def test_non_overlapping_rules_are_valid():
    automaton = create_automaton(
        states=["DEAD", "ALIVE"],
        rules=[
            {
                "from": "ALIVE",
                "to": "DEAD",
                "conditions": [
                    {
                        "state": "ALIVE",
                        "operator": "<",
                        "value": 2
                    }
                ]
            },
            {
                "from": "ALIVE",
                "to": "ALIVE",
                "conditions": [
                    {
                        "state": "ALIVE",
                        "operator": ">=",
                        "value": 2
                    },
                    {
                        "state": "ALIVE",
                        "operator": "<=",
                        "value": 3
                    }
                ]
            }
        ]
    )

    assert validate_automaton(automaton) == []


def test_impossible_rule_on_single_cell():
    automaton = create_automaton(
        width=1,
        height=1,
        rules=[
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
    )

    errors = validate_automaton(automaton)

    assert has_error(errors, "cannot be satisfied")


def test_multiple_semantic_errors():
    automaton = create_automaton(
        states=["EMPTY", "TREE", "TREE"],
        rules=[
            {
                "from": "WATER",
                "to": "ICE",
                "conditions": []
            }
        ]
    )

    errors = validate_automaton(automaton)

    assert len(errors) >= 3


def test_same_destination_rules_are_compatible():
    automaton = create_automaton(
        rules=[
            {
                "from": "TREE",
                "to": "FIRE",
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
    )

    assert validate_automaton(automaton) == []

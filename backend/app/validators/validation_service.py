
from typing import Any

from pydantic import ValidationError

from app.models.automaton import AutomatonDefinition
from app.validators.automaton_validator import (
    validate_automaton,
    validate_initial_state,
)


def _format_pydantic_errors(
    exception: ValidationError
) -> list[dict[str, str]]:
    """
    Converts Pydantic validation errors into
    the standard CelLab error format.
    """

    errors = []

    for error in exception.errors():
        location = error["loc"]

        field = ""
        for part in location:
            if isinstance(part, int):
                field += f"[{part}]"
            else:
                field += f".{part}" if field else str(part)

        errors.append({
            "field": field or "automaton",
            "message": error["msg"]
        })

    return errors


def validate_configuration(
    automaton: AutomatonDefinition | dict[str, Any],
    initial_state: Any
) -> dict[str, Any]:
    """
    Validates a complete CelLab configuration.

    Accepts either an AutomatonDefinition instance
    or a dictionary containing an automaton definition.

    Returns:
        {
            "valid": bool,
            "errors": [
                {
                    "field": str,
                    "message": str
                }
            ]
        }
    """

    # Step 1: Structural validation with Pydantic.
    if isinstance(automaton, dict):
        try:
            automaton = AutomatonDefinition.model_validate(
                automaton
            )
        except ValidationError as exception:
            return {
                "valid": False,
                "errors": _format_pydantic_errors(exception)
            }

    elif not isinstance(automaton, AutomatonDefinition):
        return {
            "valid": False,
            "errors": [{
                "field": "automaton",
                "message": (
                    "Automaton must be a valid definition "
                    "or a dictionary."
                )
            }]
        }

    # Step 2: Semantic rule validation.
    semantic_errors = validate_automaton(automaton)

    # Step 3: Initial grid validation.
    grid_errors = validate_initial_state(
        automaton,
        initial_state
    )

    # Step 4: Combine all errors.
    errors = semantic_errors + grid_errors

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

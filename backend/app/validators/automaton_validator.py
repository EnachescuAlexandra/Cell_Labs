
from typing import Any

from app.models.automaton import AutomatonDefinition
from app.models.rule import NeighborCondition


def validate_initial_state(
    automaton: AutomatonDefinition,
    initial_state: Any
) -> list[dict[str, str]]:
    """
    Validates the initial grid of a cellular automaton.

    Returns an empty list if the grid is valid.
    Otherwise, returns a list of validation errors.
    """

    errors = []

    # 1. The initial state must be a 2D list.
    if not isinstance(initial_state, list):
        return [{
            "field": "initial_state",
            "message": "Initial state must be a 2D list."
        }]

    # 2. Check the number of rows.
    if len(initial_state) != automaton.height:
        errors.append({
            "field": "initial_state",
            "message": (
                f"Expected {automaton.height} rows, "
                f"but received {len(initial_state)}."
            )
        })

    # 3. Validate each row.
    for row_index, row in enumerate(initial_state):

        if not isinstance(row, list):
            errors.append({
                "field": f"initial_state[{row_index}]",
                "message": "Each row must be a list."
            })
            continue

        # 4. Check the number of columns.
        if len(row) != automaton.width:
            errors.append({
                "field": f"initial_state[{row_index}]",
                "message": (
                    f"Expected {automaton.width} columns, "
                    f"but received {len(row)}."
                )
            })

        # 5. Validate every cell.
        for col_index, cell in enumerate(row):

            if not isinstance(cell, str):
                errors.append({
                    "field": f"initial_state[{row_index}][{col_index}]",
                    "message": "Cell state must be a string."
                })
                continue

            if cell not in automaton.states:
                errors.append({
                    "field": f"initial_state[{row_index}][{col_index}]",
                    "message": (
                        f"Unknown state '{cell}'. "
                        f"Allowed states: {automaton.states}."
                    )
                })

    return errors


# -------------------------------------------------
# Task 1.3 - Semantic validation of automaton rules
# -------------------------------------------------


def _compare(actual: int, operator: str, expected: int) -> bool:
    """
    Checks one numeric comparison.
    """

    if operator == "==":
        return actual == expected
    if operator == "!=":
        return actual != expected
    if operator == "<":
        return actual < expected
    if operator == "<=":
        return actual <= expected
    if operator == ">":
        return actual > expected
    if operator == ">=":
        return actual >= expected

    raise ValueError(f"Unsupported operator: {operator}")


def _possible_neighbor_counts(
    automaton: AutomatonDefinition
) -> set[int]:
    """
    Returns the neighbor counts available at actual
    positions in the configured grid.

    For fixed boundaries, corner and edge cells can
    have fewer neighbors than interior cells.
    """

    if automaton.neighborhood == "moore":
        offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
    else:
        offsets = [
            (-1, 0),
            (0, -1), (0, 1),
            (1, 0)
        ]

    possible_counts = set()

    for row in range(automaton.height):
        for col in range(automaton.width):
            count = sum(
                1
                for dr, dc in offsets
                if (
                    0 <= row + dr < automaton.height
                    and 0 <= col + dc < automaton.width
                )
            )
            possible_counts.add(count)

    return possible_counts


def _conditions_are_possible(
    conditions: list[NeighborCondition],
    automaton: AutomatonDefinition,
    possible_degrees: set[int]
) -> bool:
    """
    Checks whether all conditions can be true
    simultaneously for at least one grid position.

    Neighbor counts for different states must share
    the same total number of neighboring cells.
    """

    grouped_conditions: dict[str, list[NeighborCondition]] = {}

    for condition in conditions:
        grouped_conditions.setdefault(
            condition.state, []
        ).append(condition)

    referenced_states = list(grouped_conditions)

    if any(
        state not in automaton.states
        for state in referenced_states
    ):
        return False

    for degree in possible_degrees:

        # For every referenced state, find all allowed
        # counts satisfying its conditions.
        allowed_counts = []

        for state in referenced_states:
            candidates = {
                count
                for count in range(degree + 1)
                if all(
                    _compare(
                        count,
                        condition.operator,
                        condition.value
                    )
                    for condition in grouped_conditions[state]
                )
            }

            if not candidates:
                break

            allowed_counts.append(candidates)

        if len(allowed_counts) != len(referenced_states):
            continue

        # Combine counts without exceeding the number
        # of available neighboring positions.
        possible_sums = {0}

        for candidates in allowed_counts:
            possible_sums = {
                current_sum + count
                for current_sum in possible_sums
                for count in candidates
                if current_sum + count <= degree
            }

            if not possible_sums:
                break

        # If all states are referenced, their counts
        # must account for every neighbor.
        if len(referenced_states) == len(automaton.states):
            if degree in possible_sums:
                return True
        else:
            # Remaining positions can use other,
            # unreferenced states.
            if possible_sums:
                return True

    return False


def validate_automaton(
    automaton: AutomatonDefinition
) -> list[dict[str, str]]:
    """
    Validates semantic consistency of an automaton.

    The Pydantic model must already be structurally
    valid before this function is called.

    Returns an empty list for a valid automaton.
    """

    errors: list[dict[str, str]] = []

    # 1. Check state identifiers and uniqueness.
    seen_states = set()

    for index, state in enumerate(automaton.states):

        if not state.strip() or state != state.strip():
            errors.append({
                "field": f"states[{index}]",
                "message": (
                    "State names cannot be empty "
                    "or have surrounding whitespace."
                )
            })

        if state in seen_states:
            errors.append({
                "field": f"states[{index}]",
                "message": f"Duplicate state '{state}'."
            })

        seen_states.add(state)

    declared_states = set(automaton.states)

    # 2. Validate state references in every rule.
    invalid_rule_indices = set()

    for index, rule in enumerate(automaton.rules):

        if rule.from_state not in declared_states:
            errors.append({
                "field": f"rules[{index}].from",
                "message": (
                    f"Unknown source state "
                    f"'{rule.from_state}'."
                )
            })
            invalid_rule_indices.add(index)

        if rule.to not in declared_states:
            errors.append({
                "field": f"rules[{index}].to",
                "message": (
                    f"Unknown destination state "
                    f"'{rule.to}'."
                )
            })
            invalid_rule_indices.add(index)

        for condition_index, condition in enumerate(
            rule.conditions
        ):
            if condition.state not in declared_states:
                errors.append({
                    "field": (
                        f"rules[{index}].conditions"
                        f"[{condition_index}].state"
                    ),
                    "message": (
                        f"Unknown neighbor state "
                        f"'{condition.state}'."
                    )
                })
                invalid_rule_indices.add(index)

    # Further logical checks require valid references.
    possible_degrees = _possible_neighbor_counts(automaton)

    # 3. Detect impossible rule conditions.
    impossible_rule_indices = set()

    for index, rule in enumerate(automaton.rules):

        if index in invalid_rule_indices:
            continue

        if not _conditions_are_possible(
            rule.conditions,
            automaton,
            possible_degrees
        ):
            errors.append({
                "field": f"rules[{index}].conditions",
                "message": (
                    "Rule conditions cannot be satisfied "
                    "simultaneously by any cell."
                )
            })
            impossible_rule_indices.add(index)

    # 4. Detect conflicting rules.
    # Rules with different destinations must never
    # be applicable to the same cell at the same time.
    for first_index, first_rule in enumerate(automaton.rules):

        if first_index in (
            invalid_rule_indices | impossible_rule_indices
        ):
            continue

        for second_index in range(
            first_index + 1,
            len(automaton.rules)
        ):
            second_rule = automaton.rules[second_index]

            if second_index in (
                invalid_rule_indices | impossible_rule_indices
            ):
                continue

            if first_rule.from_state != second_rule.from_state:
                continue

            if first_rule.to == second_rule.to:
                continue

            combined_conditions = (
                first_rule.conditions
                + second_rule.conditions
            )

            if _conditions_are_possible(
                combined_conditions,
                automaton,
                possible_degrees
            ):
                errors.append({
                    "field": (
                        f"rules[{first_index}], "
                        f"rules[{second_index}]"
                    ),
                    "message": (
                        "Conflicting rules: both can apply "
                        "to the same cell but produce "
                        "different destination states."
                    )
                })

    return errors

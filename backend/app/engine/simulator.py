
from app.models.automaton import AutomatonDefinition
from app.models.rule import NeighborCondition


def get_neighbors(
    grid: list[list[str]],
    row: int,
    col: int,
    neighborhood: str
) -> list[str]:
    """Returns valid neighbors of a cell."""

    if neighborhood == "moore":
        offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
    elif neighborhood == "von_neumann":
        offsets = [
            (-1, 0),
            (0, -1), (0, 1),
            (1, 0)
        ]
    else:
        raise ValueError("Unsupported neighborhood")

    neighbors = []
    height = len(grid)
    width = len(grid[0])

    for dr, dc in offsets:
        nr = row + dr
        nc = col + dc

        if 0 <= nr < height and 0 <= nc < width:
            neighbors.append(grid[nr][nc])

    return neighbors


def evaluate_condition(
    neighbors: list[str],
    condition: NeighborCondition
) -> bool:
    """Evaluates a neighbor-count condition."""

    count = neighbors.count(condition.state)
    value = condition.value
    operator = condition.operator

    if operator == "==":
        return count == value
    if operator == "!=":
        return count != value
    if operator == "<":
        return count < value
    if operator == "<=":
        return count <= value
    if operator == ">":
        return count > value
    if operator == ">=":
        return count >= value

    raise ValueError("Unsupported comparison operator")


def next_generation(
    current_grid: list[list[str]],
    definition: AutomatonDefinition
) -> list[list[str]]:
    """
    Applies the configured rules synchronously
    and returns exactly one new generation.

    The input grid is never modified.
    """

    next_grid = []

    for row in range(definition.height):
        new_row = []

        for col in range(definition.width):
            current_state = current_grid[row][col]

            neighbors = get_neighbors(
                current_grid,
                row,
                col,
                definition.neighborhood
            )

            applicable_destinations = set()

            for rule in definition.rules:
                if rule.from_state != current_state:
                    continue

                if all(
                    evaluate_condition(neighbors, condition)
                    for condition in rule.conditions
                ):
                    applicable_destinations.add(rule.to)

            if len(applicable_destinations) > 1:
                raise ValueError(
                    f"Conflicting transitions at ({row}, {col})"
                )

            if applicable_destinations:
                new_state = applicable_destinations.pop()
            else:
                new_state = current_state

            new_row.append(new_state)

        next_grid.append(new_row)

    return next_grid

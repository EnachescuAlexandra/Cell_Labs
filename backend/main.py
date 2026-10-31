
import json
from pathlib import Path

from app.models.automaton import AutomatonDefinition
from app.engine.simulator import next_generation
from app.storage.json_storage import (
    save_transition,
    load_transition,
)
from app.validators.validation_service import (
    validate_configuration,
)


BASE_DIR = Path(__file__).resolve().parent
AUTOMATA_DIR = BASE_DIR / "automata"
SAVED_DIR = BASE_DIR / "saved_runs"

AUTOMATA = {
    "1": "game_of_life.json",
    "2": "brians_brain.json",
    "3": "forest_fire.json",
    "4": "cyclic_automaton.json"
}


def display_grid(grid: list[list[str]]) -> None:
    """Displays a cellular automaton grid."""
    for row in grid:
        print(" ".join(row))


def run_automaton(
    filename: str,
    ask_to_save: bool = True
) -> None:
    """Loads, validates and executes one transition."""

    path = AUTOMATA_DIR / filename

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    validation = validate_configuration(
        data["automaton"],
        data["initial_state"]
    )

    if not validation["valid"]:
        print("\nINVALID CONFIGURATION:")
        for error in validation["errors"]:
            print(f"  {error['field']}: {error['message']}")
        return

    definition = AutomatonDefinition.model_validate(
        data["automaton"]
    )

    current_grid = data["initial_state"]
    next_grid = next_generation(current_grid, definition)

    print(f"\n========== {definition.name} ==========")

    print("\nCurrent generation:")
    display_grid(current_grid)

    print("\nNext generation:")
    display_grid(next_grid)

    print("\nTransition completed successfully.")

    if ask_to_save:
        answer = input("\nSave transition? (y/n): ").strip().lower()

        if answer == "y":
            saved_path = save_transition(
                definition,
                current_grid,
                next_grid
            )
            print(f"Saved to: {saved_path.name}")


def recover_simulation() -> None:
    """Displays a previously saved transition."""

    if not SAVED_DIR.exists():
        print("\nNo saved simulations.")
        return

    files = sorted(SAVED_DIR.glob("*.json"))

    if not files:
        print("\nNo saved simulations.")
        return

    print("\nSaved simulations:")

    for index, file in enumerate(files, start=1):
        print(f"{index}. {file.name}")

    try:
        selection = int(input("\nChoose saved simulation: "))
    except ValueError:
        print("Invalid selection.")
        return

    if not 1 <= selection <= len(files):
        print("Invalid selection.")
        return

    try:
        data = load_transition(files[selection - 1])
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Could not recover simulation: {error}")
        return

    print(f"\nRecovered: {data['automaton']['name']}")

    print("\nCurrent generation:")
    display_grid(data["initial_state"])

    print("\nNext generation:")
    display_grid(data["next_state"])


def main() -> None:
    """Main application menu."""

    while True:
        print("\n========== CELLLAB - L6 ==========")
        print("1. Game of Life")
        print("2. Brian's Brain")
        print("3. Forest Fire")
        print("4. Cyclic Cellular Automaton")
        print("5. Run ALL")
        print("6. Recover saved simulation")
        print("0. Exit")

        choice = input("\nSelect option: ").strip()

        if choice in AUTOMATA:
            run_automaton(AUTOMATA[choice])

        elif choice == "5":
            for filename in AUTOMATA.values():
                run_automaton(
                    filename,
                    ask_to_save=False
                )

        elif choice == "6":
            recover_simulation()

        elif choice == "0":
            print("\nExiting CelLab.")
            break

        else:
            print("\nInvalid option.")


if __name__ == "__main__":
    main()

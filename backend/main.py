
import json
from pathlib import Path

from app.models.automaton import AutomatonDefinition
from app.engine.runner import ExperimentConfig, run_simulation
from app.storage.experiment_storage import save_experiment, load_experiment
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


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    while True:
        answer = input(prompt).strip().lower()
        if not answer:
            return default
        if answer in ("y", "n"):
            return answer == "y"
        print("Please enter y or n.")


def run_automaton(filename: str, ask_to_save: bool = True) -> None:
    """Run a selected configuration; Run ALL remains a one-step demo."""
    try:
        path = AUTOMATA_DIR / filename
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a JSON object.")
        validation = validate_configuration(data["automaton"], data["initial_state"])
        if not validation["valid"]:
            print("INVALID CONFIGURATION:")
            for error in validation["errors"]:
                print(f"  {error['field']}: {error['message']}")
            return
        definition = AutomatonDefinition.model_validate(data["automaton"])
        config = ExperimentConfig.model_validate(data.get("experiment", {}))
        print(f"\n========== {definition.name} ==========")
        if ask_to_save:
            while True:
                answer = input(f"Generations [{config.generations}]: ").strip()
                try:
                    generations = int(answer) if answer else config.generations
                    config = ExperimentConfig(generations=generations,
                                              retain_history=config.retain_history,
                                              save_result=config.save_result)
                    break
                except ValueError:
                    print("Generation count must be a positive integer.")
            retain = ask_yes_no("Retain/show intermediate generations? (y/n) "
                                f"[{'y' if config.retain_history else 'n'}]: ",
                                config.retain_history)
            config = ExperimentConfig(generations=config.generations,
                                      retain_history=retain,
                                      save_result=config.save_result)
        else:
            config = ExperimentConfig()
        grid = data["initial_state"]
        result = run_simulation(grid, definition, config)
        print("\nInitial grid (generation 0):")
        display_grid(grid)
        if result["history"] is not None:
            for index, generation in enumerate(result["history"][1:-1], start=1):
                print(f"\nGeneration {index}:")
                display_grid(generation)
        print(f"\nFinal grid (generation {config.generations}):")
        display_grid(result["final_state"])
        print("\nTransition completed successfully.")
        if ask_to_save and ask_yes_no(
            f"Save result? (y/n) [{'y' if config.save_result else 'n'}]: ",
            config.save_result
        ):
            config = ExperimentConfig(generations=config.generations,
                                      retain_history=config.retain_history,
                                      save_result=True)
            if config.generations == 1 and not config.retain_history:
                saved = save_transition(definition, grid, result["final_state"])
            else:
                saved = save_experiment(definition, grid, config, result)
            print(f"Saved to: {saved.name}")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Could not run simulation: {error}")


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
        selected = files[selection - 1]
        with selected.open(encoding="utf-8") as file:
            header = json.load(file)
        if isinstance(header, dict) and "format" in header:
            data = load_experiment(selected)
        else:
            data = load_transition(selected)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Could not recover simulation: {error}")
        return

    print(f"\nRecovered: {data['automaton']['name']}")

    print("\nCurrent generation:")
    display_grid(data["initial_state"])

    if data.get("format") == "cellab-experiment":
        history = data.get("history")
        if history and ask_yes_no("Show intermediate generations? (y/n) [n]: "):
            for index, grid in enumerate(history[1:-1], start=1):
                print(f"\nGeneration {index}:")
                display_grid(grid)
        print(f"\nFinal generation {data['experiment']['generations']}:")
        display_grid(data["final_state"])
    else:
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
        print("7. Load compatible JSON file")
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

        elif choice == "7":
            filename = input("JSON path (relative to backend/automata or absolute): ").strip()
            if filename:
                run_automaton(filename)
            else:
                print("Please enter a JSON path.")

        elif choice == "0":
            print("\nExiting CelLab.")
            break

        else:
            print("\nInvalid option.")


if __name__ == "__main__":
    main()

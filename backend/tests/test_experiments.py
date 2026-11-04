import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import main
from app.engine.runner import ExperimentConfig, run_simulation
from app.engine.simulator import next_generation
from app.models.automaton import AutomatonDefinition
from app.storage.experiment_storage import load_experiment, save_experiment
from app.storage.json_storage import load_transition, save_transition

ROOT = Path(__file__).resolve().parents[1]


def example(name="game_of_life.json"):
    data = json.loads((ROOT / "automata" / name).read_text())
    return AutomatonDefinition.model_validate(data["automaton"]), data["initial_state"]


@pytest.mark.parametrize("name", main.AUTOMATA.values())
def test_runner_matches_steps_and_preserves_input(name):
    definition, grid = example(name)
    original = copy.deepcopy(grid)
    one = next_generation(grid, definition)
    assert run_simulation(grid, definition)["final_state"] == one
    expected = next_generation(next_generation(one, definition), definition)
    result = run_simulation(grid, definition, ExperimentConfig(generations=3))
    assert result == {"final_state": expected, "history": None}
    assert grid == original


def test_blinker_two_generations_and_history():
    definition, grid = example()
    result = run_simulation(grid, definition, ExperimentConfig(generations=2, retain_history=True))
    assert result["final_state"] == grid
    assert result["history"] == [grid, next_generation(grid, definition), grid]
    result["history"][0][0][0] = "ALIVE"
    assert grid[0][0] == "DEAD"


@pytest.mark.parametrize("value", [0, -1, True, 1.5, "2", None])
def test_invalid_generation_count(value):
    with pytest.raises(ValidationError):
        ExperimentConfig(generations=value)


@pytest.mark.parametrize("retain", [False, True])
def test_experiment_round_trip(tmp_path, retain):
    definition, grid = example()
    config = ExperimentConfig(generations=3, retain_history=retain, save_result=True)
    result = run_simulation(grid, definition, config)
    path = save_experiment(definition, grid, config, result, tmp_path)
    data = load_experiment(path)
    assert data["initial_state"] == grid
    assert data["final_state"] == result["final_state"]
    assert data["history"] == result["history"]
    assert data["experiment"] == config.model_dump()


@pytest.mark.parametrize("damage", ["version", "length", "state", "transition", "endpoint", "count", "config"])
def test_corrupt_experiment_rejected(tmp_path, damage):
    definition, grid = example()
    config = ExperimentConfig(generations=2, retain_history=True)
    path = save_experiment(definition, grid, config, run_simulation(grid, definition, config), tmp_path)
    data = json.loads(path.read_text())
    if damage == "version": data["version"] = 2
    if damage == "length": data["history"].pop()
    if damage == "state": data["history"][1][0][0] = "UNKNOWN"
    if damage == "transition": data["history"][1][0][0] = "ALIVE"
    if damage == "endpoint": data["final_state"][0][0] = "ALIVE"
    if damage == "count": data["experiment"]["generations"] = 0
    if damage == "config": data["automaton"]["states"].append("ALIVE")
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError): load_experiment(path)


@pytest.mark.parametrize("path", sorted((ROOT / "saved_runs").glob("*.json")), ids=lambda p: p.name)
def test_existing_save_compatible(path):
    header = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(header, dict) and "format" in header:
        # The local saves directory also contains versioned experiment records.
        load_experiment(path)
        return
    data = load_transition(path)
    definition = AutomatonDefinition.model_validate(data["automaton"])
    assert next_generation(data["initial_state"], definition) == data["next_state"]


def answers(monkeypatch, values):
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(iterator))


def test_cli_normal_and_invalid_input(monkeypatch, capsys):
    answers(monkeypatch, ["bad", "1", "0", "abc", "2", "maybe", "y", "n", "0"])
    main.main()
    output = capsys.readouterr().out
    assert "Invalid option" in output
    assert output.count("Generation count must be a positive integer") == 2
    assert "Please enter y or n" in output
    assert "Generation 1:" in output
    assert "Final grid (generation 2)" in output


def test_cli_all_no_extra_prompts(monkeypatch, capsys):
    answers(monkeypatch, ["5", "0"])
    main.main()
    assert capsys.readouterr().out.count("Transition completed successfully") == 4


@pytest.mark.parametrize("text", ["[]", "{}", "not JSON"])
def test_cli_malformed_file(tmp_path, capsys, text):
    path = tmp_path / "bad.json"
    path.write_text(text)
    main.run_automaton(str(path))
    assert "Could not run simulation" in capsys.readouterr().out


def test_cli_missing_file(capsys):
    main.run_automaton("does-not-exist.json")
    assert "Could not run simulation" in capsys.readouterr().out


@pytest.mark.parametrize("retain", [False, True])
def test_cli_save_and_recover(tmp_path, monkeypatch, capsys, retain):
    monkeypatch.setattr(main, "save_transition", lambda *args: save_transition(*args, save_dir=tmp_path))
    monkeypatch.setattr(main, "save_experiment", lambda *args: save_experiment(*args, save_dir=tmp_path))
    monkeypatch.setattr(main, "SAVED_DIR", tmp_path)
    answers(monkeypatch, ["2" if retain else "", "y" if retain else "n", "y"])
    main.run_automaton("game_of_life.json")
    answers(monkeypatch, ["1", "y"] if retain else ["1"])
    main.recover_simulation()
    output = capsys.readouterr().out
    assert "Saved to:" in output and "Recovered: Game of Life" in output
    assert ("Final generation 2" if retain else "Next generation") in output


@pytest.mark.parametrize("selection", ["abc", "0", "2"])
def test_cli_invalid_recovery_selection(tmp_path, monkeypatch, capsys, selection):
    (tmp_path / "bad.json").write_text("[]")
    monkeypatch.setattr(main, "SAVED_DIR", tmp_path)
    answers(monkeypatch, [selection])
    main.recover_simulation()
    assert "Invalid selection" in capsys.readouterr().out


def test_cli_corrupt_recovery(tmp_path, monkeypatch, capsys):
    (tmp_path / "bad.json").write_text("[]")
    monkeypatch.setattr(main, "SAVED_DIR", tmp_path)
    answers(monkeypatch, ["1"])
    main.recover_simulation()
    assert "Could not recover" in capsys.readouterr().out


def test_custom_json_with_experiment_defaults(tmp_path, monkeypatch, capsys):
    data = json.loads((ROOT / "automata/game_of_life.json").read_text())
    data["experiment"] = {"generations": 2, "retain_history": True, "save_result": False}
    path = tmp_path / "custom.json"
    path.write_text(json.dumps(data))
    answers(monkeypatch, ["7", str(path), "", "", "", "0"])
    main.main()
    output = capsys.readouterr().out
    assert "Generation 1:" in output and "Final grid (generation 2)" in output

# CelLab architecture

## Implemented modules

Paths below are relative to `backend/`.

| Module | Responsibility |
| --- | --- |
| `main.py` | Console menu, JSON loading, parameter prompts, display, save selection, and recovery dispatch. Options 1-4 select bundled examples; 5 runs those four once without prompts; 6 recovers saves; 7 loads another compatible JSON path. |
| `app/models/automaton.py` | Pydantic definition: dimensions, states, neighborhood, fixed boundary, keep default, and rules. |
| `app/models/rule.py` | Transition and neighbor-count condition schemas. |
| `app/validators/validation_service.py` | Uniform structural, semantic, and grid validation results. |
| `app/validators/automaton_validator.py` | Grid shape/state checks, rule references, impossible conditions, and conflicting destinations. |
| `app/engine/simulator.py` | Neighbor lookup, numeric comparison evaluation, and one synchronous `next_generation` step. |
| `app/engine/runner.py` | Strict `ExperimentConfig` and N-step execution using the single-step engine. Preserves the input; optional history contains generations 0 through N. No console or storage I/O. |
| `app/storage/json_storage.py` | Legacy single-transition JSON snapshots and validated recovery. |
| `app/storage/experiment_storage.py` | Separate version 1 experiment records, optional history, grid validation, and replay verification on save/load. |
| `automata/`, `saved_runs/` | Definitions with initial grids; persisted records and tracked saved examples. |

`app/api`, `app/database`, and `app/services` currently contain empty package markers. They provide no API, database, or service functionality.

## Data flow

```mermaid
flowchart TD
    J[JSON definition and initial grid] --> C[Console orchestration]
    C --> V[Pydantic and semantic/grid validation]
    V --> R[Experiment runner: N steps]
    R --> E[Generic synchronous transition engine]
    E --> R
    R --> D[Display initial/final and optional history]
    R --> S[Optional snapshot or versioned experiment save]
    S --> F[JSON files]
    F --> L[Load and validate; replay experiment records]
    L --> D
```

The CLI reads `automaton` and `initial_state`, validates them, and parses an optional sibling `experiment` object. Its fields are `generations` (positive strict integer, default 1), `retain_history` (default false), and `save_result` (default false). The CLI can override these defaults. Saving remains a CLI/storage responsibility; the runner does not act on `save_result`.

Rules match the current cell's source state and all neighbor-count conditions. Each step reads only the previous grid and creates a new grid. N steps are executed even if the state stabilizes. Without retained history, stepping memory is independent of N; retained history requires N+1 grids.

One step without history uses the original snapshot fields. Other runs use `cellab-experiment`, version 1, with parameters, initial/final states, and optional history. Legacy loading validates configuration and grids; experiment loading also replays transitions. Recovery displays results rather than resuming simulation. Writes are plain JSON and are not transactional.

## Dependencies

`requirements.txt` declares Pydantic 2, pytest 9, FastAPI with standard extras, NumPy, and HTTPX. Current application runtime uses Pydantic and Python's standard library. Tests use pytest and standard-library mocking. FastAPI, NumPy, and HTTPX are installed but unused by the current application; their presence does not mean an API or learning experiment exists. No dependency changes are proposed for L6.

## Rule language and limits

The grid is rectangular (dimensions 1-100), with one declared string state per cell. Radius-one Moore or von Neumann neighborhoods omit out-of-grid positions; boundary cells still update. Conditions compare a state's neighbor count against an integer constant 0-8 using `==`, `!=`, `<`, `<=`, `>`, or `>=`. Conditions are AND-combined. Empty conditions mean unconditional transition; no matching rule means keep the state.

Rule order gives no priority. Overlapping matches may share a destination, but different destinations conflict. Semantic validation checks feasibility against actual grid geometry, not reachability from the initial grid. Positional checks, wrapping, stochastic transitions, arithmetic updates, agent movement, and arbitrary expressions are unsupported. The engine is generic within this language, rather than universal.

## Adding an automaton

Create a JSON object with `automaton` and `initial_state`, following an existing file's schema. An optional `experiment` object supplies defaults. Use existing declared states and supported conditions, and avoid conflicting or impossible rules. Select menu option 7 and enter the filename relative to `backend/automata`, or an absolute path. No Python edit is required. Run ALL intentionally remains limited to its original four registered examples.

`crystal_growth.json` demonstrates this path: a center seed becomes a 3x3 crystal block at generation 1, then the entire 5x5 grid at generation 2. The existing `>= 1` condition adds 16 cells at generation 2, including the four corners. The filled grid is a fixed point.

## Tests

- `test_models.py`: structural constraints and aliases.
- `test_initial_state.py`: grid dimensions and state membership.
- `test_semantic_validation.py`: impossible conditions and conflicting rules.
- `test_validation_service.py`: combined validation and error reporting.
- `test_l6.py`: exact original automaton transitions, unchanged input, snapshot round trip.
- `test_experiments.py`: runner equivalence/history, strict counts, legacy and local experiment saves, versioned storage corruption, and CLI success/error paths.
- `test_crystal_growth.py`: exact generation 1, filled generation 2 including corners, and subsequent fixed-point steps using the generic engine.

Run from `backend` with `..\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider --basetemp=.test-tmp -q`.

## Future React + TypeScript and FastAPI integration (not implemented)

React + TypeScript would own the grid visualization/editor, parameter forms, navigation, and result presentation. FastAPI would own request validation, simulation invocation, persistence access, and consistent error responses. It should call the existing validation service and runner directly, without console input or display functions. The synchronous transition algorithm remains shared and authoritative in Python.

Before exposing long runs, define request/response schemas, computation/history limits, and safe execution outside the asynchronous request loop when necessary. File paths must stay server-controlled rather than accepting the CLI's arbitrary local paths. See [ROADMAP.md](ROADMAP.md) for deferred integration work.

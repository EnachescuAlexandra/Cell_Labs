# CelLab - Cellular Automata Simulator

University Artificial Intelligence project developed by a team of four. Deliverable 2 (L6) models a world, transition rules, experiment parameters, and state storage/recovery.

## Current features

- A generic deterministic, synchronous transition engine using JSON definitions.
- Game of Life, Brian's Brain, deterministic Forest Fire, and a four-state Cyclic Cellular Automaton.
- Strict structural validation, grid validation, impossible-condition checks, and conflicting-rule detection.
- Explicit experiment parameters: positive generation count (default 1), optional history retention, and optional saving.
- Console display of initial/final states and optional intermediate generations.
- Legacy transition snapshots and versioned multi-generation experiment records.
- Loading additional compatible JSON files through the console.
- Crystal Growth is included as an additional JSON example, loadable through option 7.

Multi-generation execution is a small enhancement beyond L6's minimum demonstration of one transition.

## Installation on Windows (PowerShell)

From the repository root, with Python 3.14 installed:

```powershell
py -3.14 --version
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

If `.venv` already exists, reuse it. No global installations are needed.

## Run

```powershell
cd backend
..\.venv\Scripts\python.exe main.py
```

Menu: `1` Game of Life, `2` Brian's Brain, `3` Forest Fire, `4` Cyclic Cellular Automaton, `5` Run ALL, `6` Recover, `7` Load compatible JSON, `0` Exit.

Select an automaton, enter a positive generation count (Enter accepts 1), and choose whether to retain/show intermediate generations. After displaying the result, choose whether to save. Invalid generation counts and yes/no answers are retried.

Run ALL keeps the original workflow: one generation per automaton, without parameter or save prompts. Option 7 accepts an absolute path or a path relative to `backend/automata`; no Python menu edit is needed for a new compatible definition.

## JSON configuration and limits

Each file contains `automaton` and `initial_state`. The existing four files remain unchanged. An optional sibling object supplies experiment defaults:

```json
"experiment": {
  "generations": 3,
  "retain_history": true,
  "save_result": false
}
```

Insert this object alongside `automaton` and `initial_state` in a complete configuration. The CLI allows overrides; `save_result` sets the default answer to the save prompt. The runner performs no file I/O itself. JSON generation counts must be integers greater than zero; booleans, fractional values, and strings are rejected.

The supported rule language uses:

- Rectangular grids, width/height 1-100, with one declared string state per cell.
- Radius-one Moore (8 possible neighbors) or von Neumann (4) neighborhoods.
- Fixed boundaries: positions outside the grid are omitted; edge cells still update.
- Rules containing `from`, `to`, and AND-combined neighbor-count conditions.
- Comparisons `==`, `!=`, `<`, `<=`, `>`, `>=` against constants 0-8.
- Empty conditions for unconditional transitions; no match keeps the current state.
- No rule priority: simultaneous matches with different destinations are invalid.

This engine is generic within that language: all four examples use identical Python transition code. Directional conditions, wrapping, probability, arithmetic updates, agent movement, and general expressions are not supported. Impossible rules are rejected even when they would simply remain unused on a small grid.

Every generation reads only the previous grid and builds a new grid. The original input is preserved. History includes generation 0 through generation N when enabled; otherwise only stepping grids are retained, using memory independent of N. Retained history uses memory proportional to N and grid size.

## Storage and recovery

Saves go to `backend/saved_runs/`. Existing tracked examples remain available; new local saves are ignored by Git.

- One generation without history uses the existing transition format: definition, initial state, next state, ID, timestamp.
- Multi-generation results or retained history use a separate `cellab-experiment` version 1 record containing parameters, initial/final grids, and optional history.
- Recovery option 6 lists both formats. Select the displayed number. Retained intermediate grids can be shown on request.
- Experiment recovery validates the configuration and all stored grids and replays the N steps to verify results. Legacy recovery preserves its original structural/semantic checks without replay verification.

Recovery displays stored results; it does not resume an interactive simulation. Saves are plain JSON, without transactional durability. Large generation counts can take time; history increases memory and file size, and experiment verification repeats the computation.

## Tests

From the repository root:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider --basetemp=backend/.test-tmp -q
```

Or from `backend`:

```powershell
..\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider --basetemp=.test-tmp -q
```

The root `pytest.ini` sets `pythonpath = backend` and `testpaths = backend/tests`, so both commands discover the same suite without changing application imports. The temporary directory stays inside the repository and is ignored. Pytest reuses/clears this dedicated test directory; do not store personal files there. Tests cover legacy and experiment save/recovery, all four original next-state examples, and Crystal Growth expansion and stability. The test count can vary with local saved records, which are also checked for compatibility.

## Quick demonstration

1. Select `1`, accept one generation, answer `n` for history: the vertical Life blinker becomes horizontal.
2. Save with `y`; select `6` and recover the file with the printed ID.
3. Select `2` for Brian's Brain to demonstrate three states.
4. Select `1`, enter `2`, choose history: the Life blinker returns to its initial grid.
5. Select `5` to show all four examples in one pass.

See [the 2-3 minute demonstration guide](docs/L6_DEMO.md).

## Structure and future work

`backend/app/models` defines schemas; `validators` checks configurations; `engine/simulator.py` computes a single step; `engine/runner.py` repeats it; `storage` handles snapshots/experiments; `backend/main.py` provides the CLI. Definitions are in `backend/automata`, tests in `backend/tests`.

L11 dataset/NN/RL work and L13 natural-language parsing are future deliverables. A GUI, automatic question answering, cycle detection, and arbitrary cellular automata are not implemented. There are no runtime assistant calls.

AI documentation is indexed in [docs/AI_Interactions.md](docs/AI_Interactions.md). The earlier document is a reconstructed summary, not a complete original conversation archive. Team members must import available original exports as explained in [docs/ai-interactions/README.md](docs/ai-interactions/README.md).

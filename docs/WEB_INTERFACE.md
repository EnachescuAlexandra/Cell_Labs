# CelLab optional L6 web interface

The web application wraps the existing Python engine without changing CLI behavior, definitions, or storage formats. It is a local development application. React displays grids and never evaluates automaton rules.

## Running

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.api.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd frontend
npm.cmd ci --cache .npm-cache
npm.cmd run dev
```

Open http://127.0.0.1:5173. The original CLI remains `cd backend` followed by `..\.venv\Scripts\python.exe main.py`. Stop either development server with Ctrl+C.

## REST endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | API availability |
| GET | `/api/automata` | Metadata for all five built-ins |
| GET | `/api/automata/{identifier}` | Validated definition, initial grid, experiment defaults |
| POST | `/api/configurations/validate` | Validate uploaded JSON configuration |
| POST | `/api/simulations/next` | Exactly one transition |
| POST | `/api/simulations/run` | N transitions, optional history |
| POST | `/api/simulations/run-all` | One transition for the original four systems |
| POST | `/api/experiments` | Validate and save a supplied experiment result |
| GET | `/api/experiments` | List saved identifiers |
| GET | `/api/experiments/{identifier}` | Validate and recover either storage format |

Configuration requests use `{automaton, initial_state, experiment}`. `experiment` uses the existing strict positive-integer `generations`, Boolean `retain_history`, and Boolean `save_result` fields. Simulation results add `final_state` and `history`. Indices are relative to the supplied initial grid: initial is 0 and final is `experiment.generations`; retained history contains N+1 grids. Missing history is `null`, never an invented sequence or an empty list. The UI offsets each returned batch into its current timeline.

Saving accepts the simulation-result shape. It verifies the supplied result against Python execution. One transition without retained history uses the legacy snapshot writer; other cases use the versioned experiment writer. Saving is always explicit; the runner's `save_result` flag itself causes no I/O. Recovery normalizes legacy snapshots to generation 0/1 with null history, and returns complete experiment history only when it exists. Legacy records retain the original loader's structural validation behavior.

Errors use `{"error":{"message":"...","details":[...]}}`; details are present for request/configuration validation. Invalid requests return 422, unknown resources 404, invalid save identifiers 400, and unexpected internal failures a sanitized 500. Local CORS permits only the two loopback Vite origins on port 5173. No client-supplied filesystem path is opened.

## CLI parity checklist

| Existing workflow | Web equivalent | Implemented |
| --- | --- | --- |
| 1. Game of Life | Built-in selector | Yes |
| 2. Brian's Brain | Built-in selector | Yes |
| 3. Forest Fire | Built-in selector | Yes |
| 4. Cyclic Cellular Automaton | Built-in selector | Yes |
| 5. Run All | Original-four one-step comparison cards; inspect result | Yes |
| 6. Recover Saved Simulation | Browse saved, select identifier, Recover | Yes, both formats |
| 7. Load Compatible JSON File | Local JSON picker and backend validation | Yes |
| 0. Exit | Pause, Reset, or leave the page | Yes, adapted to web |
| Crystal Growth extension | Fifth built-in selection or JSON picker | Yes |
| Generation count | Positive integer batch input | Yes |
| Optional history | Retain toggle; only actual grids are navigable | Yes |
| Initial/current/final display | Generation labels and Previous/Next navigation | Yes |
| Save results | Explicit Save experiment | Yes |
| Validation feedback | Structured API errors displayed in alert | Yes |

Reset restores the selected definition's original initial grid, including recovered/custom configurations. Previous jumps to the nearest available earlier frame. When viewing an earlier frame, Next first visits a known later frame; Run N computes a new branch and removes future frames. Save always targets the final computed frame, even if an earlier frame is being viewed. Complete history is saved only when retention is enabled and every frame is available; otherwise it is null. Playback performs sequential one-step API calls and can be paused while a call finishes. Reset discards a late response but cannot cancel server-side computation.

## Verification performed on 2026-11-04

- Full Python suite: **102 passed**, including all pre-existing tests and 14 new API cases. Command from root: `.\.venv\Scripts\python.exe -B -m pytest -p no:cacheprovider --basetemp=backend/.test-tmp -q`.
- API coverage includes five-system discovery/loading, one-step/N-step execution, input preservation, history/no-history, strict invalid counts, legacy and experiment save/recovery, rejected altered results, malformed/custom/conflicting configuration, invalid save identifiers, corrupt records, Run All, and local CORS.
- `npm.cmd ci` is the reproducible installation command; this session initially installed with `npm.cmd install --cache .npm-cache`, producing the lockfile. Installation audit reported zero vulnerabilities.
- `npm.cmd run build`: TypeScript compilation and Vite production build passed. Output approximately 233.48 kB JavaScript (73.18 kB gzip), 5.68 kB CSS (1.86 kB gzip).
- `npm.cmd test`: **4 passed** in jsdom using mocked HTTP responses. These verify API-backed stepping, retained-history navigation, Reset, Play/Pause, switching during playback, validation-error/loading-state recovery, prevention of overlapping requests, and rejection of late responses after Reset. They are component tests, not browser end-to-end tests.
- Live HTTP integration: started real FastAPI and Vite processes; checked Vite HTML, proxied health/discovery, loading and next/two-step execution for all five automata, agreement of one-step results with history index 1, original-four Run All, and structured 422 validation errors. All passed. This check did not drive a browser or exercise persistence through a browser; storage workflows were verified by API tests in temporary directories.
- Browser visual/layout inspection, file-picker interaction, and a complete manual browser save/recover demonstration remain unverified. No browser automation capability was available in this session.

Windows sandbox restrictions initially blocked npm downloads and esbuild configuration access. Installation, build, tests, and local Vite startup were retried with the required execution approvals and succeeded.

## Files

Added: `backend/app/api/main.py`, `backend/tests/test_api.py`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts`, `frontend/index.html`, `frontend/src/api.ts`, `frontend/src/App.tsx`, `frontend/src/main.tsx`, `frontend/src/style.css`, `frontend/src/App.test.tsx`, and this document.

Modified: root `README.md`, `.gitignore`, `docs/ARCHITECTURE.md`, `docs/L6_DEMO.md`, and `docs/AI_Interactions.md`. Python engine, validators, CLI, definitions, and tracked saves were preserved.

## Limitations

Large generation counts remain unbounded to match the runner; computation and replay validation can take time, and retained history can consume substantial memory. There is no server cancellation, job queue, authentication, production deployment, transactional storage, or guarantee against simultaneous writes from multiple independent clients. A server restart is needed if API code changes without the optional uvicorn reload flag. Production hosting must serve the frontend build and proxy `/api` to FastAPI. Missing intermediate history cannot be recovered through navigation.

## Two-minute demo

1. **0:00–0:25:** Select Game of Life, enable history, step once, and compare state counts. Previous shows generation 0.
2. **0:25–0:50:** Play, Pause, Reset. Run two generations with history; the blinker returns to its initial state.
3. **0:50–1:15:** Save, Browse saved, select the returned identifier, Recover, and navigate the recovered frames.
4. **1:15–1:40:** Select Crystal Growth and run two generations. Load Brian's Brain JSON using the picker. Demonstrate an invalid-state JSON error if a prepared invalid file is available.
5. **1:40–2:00:** Run All, inspect one of the four returned results, and Pause or Reset before leaving.

This is a proposed demo scenario, not a record of a completed manual browser demonstration. Work remains on `feature/react-frontend-mvp`; no branch switch, commit, push, or merge was performed.

# CelLab development roadmap

## Completed L6

JSON world/rule modeling, structural and semantic validation, synchronous generic stepping, explicit experiment parameters, N-step runner with optional history, legacy snapshots, versioned experiment recovery, console demonstration, compatible JSON loading, and regression tests are implemented. Crystal Growth uses the existing engine without new rule semantics. Full original AI conversation exports still need importing by the team; reconstructed summaries are labeled as such.

## L11: dataset and NN/RL experiment

Choose a bounded task and automata; generate reproducible trajectories using the runner and retain definitions, initial states, generation indices, and provenance. Separate training/validation/test data by complete trajectories to avoid leakage. Implement one manageable NN or RL experiment, compare against a simple baseline, and report metrics and failure cases. Keep training outside the runtime simulator. Agree dataset size and compute budget before adding infrastructure.

## L13: natural-language descriptions

Define a supported vocabulary and mapping to the existing JSON rule language. Parse locally with an explicit grammar or bounded parser, then use current validators and show understandable errors. Test ambiguous, invalid, and unsupported descriptions; do not silently approximate unsupported automata. Final runtime must not call online or offline conversational agents.

## Final integration and analysis

Add FastAPI schemas and endpoints around the runner, then a React + TypeScript grid interface for configuration and generation display. Add simulation questions incrementally: state/count after N steps, stable-state detection, cycles, and bounded configuration search. Distinguish bounded search from proofs about all future states. Test API contracts, frontend workflows, persistence compatibility, and the complete demonstration. Keep L11/L13 and final interface work separate from the L6 branch's immediate scope.

## Targeted maintainability follow-ups (deferred beyond L6)

- `main.py` repeats `ExperimentConfig` construction and validates definitions before the runner validates again. Keep the current boundary checks for L6; later introduce one shared orchestration operation returning validated data for both CLI and API.
- Recovery reads JSON once to choose a loader and again inside that loader. A common record reader/dispatcher could remove this duplication after compatibility tests cover both formats.
- `ExperimentConfig` currently lives in the runner module and includes a save preference that the pure runner does not execute. Consider moving shared request/configuration models to `app/models` when API schemas are needed; preserve existing imports if moved.
- Storage imports the legacy module's default directory and returns plain dictionaries. Before API integration, make persistence location injectable and define typed result/record contracts without changing legacy fields.
- Engine and validator duplicate neighborhood offsets and comparisons. Do not refactor them before L6; any later shared implementation needs geometry/conflict regression coverage.
- Empty API/database/services packages are placeholders, and FastAPI/NumPy/HTTPX are unused in the current runtime. Populate only when needed; do not invent service layers or remove planned dependencies during final L6 preparation.
- Large N and replay verification are synchronous CPU work; retained history is unbounded. Set execution/history limits and decide how FastAPI handles long work before public access. Keep server filesystem paths private and add atomic persistence if durability is required.

No dead execution path or unused import requiring immediate removal was found in the inspected runner, storage integration, or CLI. The only immediate maintainability adjustment is adding parameter annotations to `save_experiment`; runtime behavior is unchanged.

## Possible division for four team members

| Member | Primary responsibility | Cross-review |
| --- | --- | --- |
| 1 | Engine reuse, simulation analysis, dataset generation | Parser semantics and automaton regressions |
| 2 | L11 NN/RL experiment, evaluation, reproducibility | Dataset splits and analysis results |
| 3 | L13 parser, FastAPI contracts and persistence integration | API validation and error handling |
| 4 | React + TypeScript interface, end-to-end tests, demo integration | Usability and documentation accuracy |

All four members preserve their original AI exports, review another member's changes, and rehearse the final presentation. This is a suggested allocation, not a record of individual contributions.

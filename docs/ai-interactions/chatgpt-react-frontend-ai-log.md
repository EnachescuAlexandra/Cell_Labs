# CelLab — ChatGPT AI Interaction Log: React + FastAPI Web Interface

**Date:** 2026-11-04
**Project:** CelLab (Cell_Labs)
**Feature branch:** `feature/react-frontend-mvp`
**AI assistant:** ChatGPT
**Implementation assistant:** Codex (separate original session must also be preserved)

> **Record integrity:** This is a curated record of the major ChatGPT-produced prompts and decisions from the conversation. The prompt blocks below are reproduced as authored in the chat, except for Markdown presentation/escaping. It is **not** a verbatim export of the entire conversation; the original chat and Codex session should be preserved separately if the instructor requires complete AI interaction records. Do not treat stated design goals as verified implemented functionality.

## 1. Starting point and objectives

Before web-interface work, the CelLab L6 Python CLI and JSON-defined automata were reported stable, with 88 passing Python tests. The user wanted a light-mode visual interface covering the existing CLI, while preserving the Python simulation engine and the completed L6 work. ChatGPT recommended React + TypeScript + Vite with FastAPI, on a separate feature branch and without immediate merge to `main`. A simpler MVP was discussed before choosing full CLI parity. The assistant explained that React handles visualization, Python remains the source of truth for transitions, and a first Codex prompt does not itself prove the features were implemented.

## 2. Prompt A — Initial optional web MVP (original ChatGPT draft)

```text
# CelLab — React + FastAPI Light MVP

We are developing CelLab, a university project for modeling and simulating cellular automata.

The L6 implementation is complete, integrated into `main`, and verified with 88 passing tests.

I want to prototype a modern, visually appealing web interface that uses the EXISTING Python simulation engine.

## Goal

Build a small but functional web MVP using:

- React + TypeScript + Vite for the frontend.
- FastAPI for the Python backend API.
- A clean, modern LIGHT theme.
- The existing cellular automata engine, validators, and JSON configurations.

This is an optional prototype for our upcoming demonstration, not a replacement for the stable CLI.

## 1. Safety constraints

- Work only on `feature/react-frontend-mvp`.
- Do not switch branches.
- Do not commit, push, or merge.
- Preserve the existing CLI and all L6 functionality.
- Do not rewrite the simulation engine in TypeScript.
- Do not alter existing automata rules or JSON configurations.
- Avoid unnecessary dependencies and architectural complexity.
- Do not implement future NN/RL or natural-language parsing features.
- Do not modify files outside this repository.

## 2. Backend — FastAPI

Create a minimal REST API that reuses the existing Python engine.

Provide endpoints for:

- Listing available automata.
- Loading an automaton's configuration and initial grid.
- Validating a configuration.
- Computing the next generation of a grid.

Use the existing Pydantic models and validators.

Do not duplicate transition logic.

Handle invalid input with meaningful HTTP errors.

Configure CORS only for local frontend development.

Keep the API independent from the CLI so both interfaces can coexist.

## 3. Frontend — React

Create a frontend in `frontend/` using React, TypeScript, and Vite.

Build a polished, responsive LIGHT-MODE interface.

### Layout

- Header with CelLab branding.
- Left sidebar for automaton selection and simulation information.
- Central interactive 2D grid.
- Simulation controls beneath the grid.
- Right panel or compact section for generation statistics and state legend.

### Functionality

- Select among the existing automata, including Crystal Growth.
- Display the initial grid.
- Color cells based on their states, using consistent colors.
- Advance one generation using the Python API.
- Reset to the original grid.
- Run multiple generations with Play/Pause.
- Display the current generation number.
- Show a legend and counts for each cell state.
- Display useful loading and error states.

Play/Pause must avoid duplicate requests or overlapping asynchronous updates.

Use the real backend results. No hardcoded simulation outcomes or fake data.

## 4. Visual design

Use a modern, minimal scientific dashboard aesthetic.

Design requirements:
- Light theme with white/off-white surfaces.
- Subtle borders and shadows.
- Clear typography and good visual hierarchy.
- Rounded controls and cards.
- Responsive layout.
- Accessible color contrast.
- Smooth but restrained animations.
- Visually distinct cell states.

Avoid clutter, excessive gradients, or unnecessary decorative elements.

Do not use generated images or external image dependencies.

## 5. Implementation quality

- Use TypeScript types for API requests and responses.
- Keep components reasonably small and reusable.
- Avoid unnecessary state-management libraries.
- Use React hooks and clean component composition.
- Keep simulation state synchronized with backend responses.
- Do not create placeholder features that appear functional but are not.

Update `.gitignore` for Node/Vite-generated files.

## 6. Testing

- Preserve all existing Python tests.
- Add a few focused API tests.
- Run the Python tests.
- Install frontend dependencies locally.
- Run TypeScript checking and the production build.
- Verify that the React frontend communicates with FastAPI.
- Report any integration issues honestly.

## 7. Documentation

Update README with a short optional section explaining how to run:

1. The FastAPI backend.
2. The Vite React frontend.
3. The existing CLI.

Clearly label the web interface as an experimental MVP.

Document this Codex interaction factually in the existing AI documentation. Do not fabricate verbatim transcripts.

## 8. Final report

Report:
- Files created and modified.
- API endpoints.
- Features implemented.
- Test and build results.
- Exact commands to launch the backend and frontend.
- Any remaining issues.

Do not commit, push, merge, or switch branches.

Prioritize a genuinely functional MVP over visual complexity. If a feature is too risky, implement the simpler reliable version rather than compromising the stable backend.
```

**Decision:** The user subsequently requested complete functional parity with the CLI, instead of only this limited MVP.

## 3. Prompt B — Full CLI parity addendum (original ChatGPT draft)

```text
## Functional parity with the existing CLI

The web interface must expose all existing CelLab L6 functionality, not just basic grid visualization.

In addition to the previously specified features, implement:

1. An explicit generation-count input allowing the user to run exactly N generations.
2. Optional retention and visualization of intermediate generations, including Previous/Next navigation.
3. Saving experiments through the existing Python storage modules.
4. Listing and recovering previously saved simulations, supporting both legacy transitions and newer experiment records.
5. Loading user-provided compatible JSON automaton definitions through the browser, with structural and semantic validation.
6. A Run All action equivalent to the existing CLI behavior.
7. Clear validation errors and recovery errors.
8. Consistent initial, current, and final generation displays.

All functionality must use the real existing Python engine, validators, runner, and persistence modules. Do not implement duplicate simulation rules in React.

Use an appropriate local-development API for reading and saving experiment files. Avoid arbitrary filesystem access or unsafe path handling.

Preserve backwards compatibility with existing saved records and all CLI functionality.

Keep the interface visually clean and responsive. If necessary, organize secondary features into collapsible panels or tabs rather than cluttering the main simulation view.

Add focused API and frontend tests for the new functionality, run the relevant test/build checks, and report any incomplete features honestly.
```

## 4. Prompt C — Final full L6 implementation prompt (original ChatGPT draft)

```text
# CelLab — Full L6 Web Interface (React + FastAPI)

## Project context

CelLab is a university Artificial Intelligence project developed by a team of four students.

The existing L6 implementation is complete, stable, merged into `main`, and verified with 88 passing Python tests.

The backend currently provides:
- A generic cellular automata engine.
- JSON-defined states and transition rules.
- Structural and semantic validation.
- Moore and von Neumann neighborhoods.
- Five working automata: Game of Life, Brian's Brain, Forest Fire, Cyclic Cellular Automaton, and Crystal Growth.
- Configurable multi-generation execution.
- Optional intermediate generation history.
- Saving and recovering simulations.
- Loading compatible custom JSON definitions.
- A working CLI.

**Goal:** Build a polished, functional web application with complete feature parity with the existing L6 CLI.

The implementation must use React + TypeScript + Vite for the frontend and FastAPI for the Python backend.

The visual design should be modern, clean, professional, and primarily LIGHT MODE.

This should be a real integrated application, not a static UI mockup.

## 1. Git and safety constraints

Before modifying files:
- Verify the current branch is `feature/react-frontend-mvp`.
- Preserve all existing changes.
- Do not switch branches.
- Do not commit, push, or merge.
- Do not modify files outside this repository.
- Do not rewrite the existing simulation engine in JavaScript.
- Do not change existing automata rules or JSON definitions.
- Do not break the current CLI.
- Avoid unnecessary refactoring or new dependencies.
- Do not implement unrelated future L11 NN/RL or L13 natural-language parsing features.

If the current branch is incorrect, stop and report it.

## 2. Architecture

Use the following separation:

**Frontend — React + TypeScript + Vite**
- User interface.
- Simulation visualization.
- User controls.
- Generation navigation.
- State legends and statistics.
- API communication.

**Backend — Python + FastAPI**
- Configuration loading.
- Existing Pydantic validation.
- Generic simulation engine.
- Experiment runner.
- Saving and recovering experiments.
- API request validation.

Preserve the existing Python modules.

Create a minimal API layer in `backend/app/api/` that invokes existing functionality rather than duplicating simulation logic.

The CLI and web API must coexist independently.

Use JSON over HTTP.

Configure CORS for local development only.

Use minimal dependencies and maintain a clear, documented architecture.

## 3. Backend API functionality

Implement REST endpoints for the following features.

### Automata discovery
- List all available built-in automata.
- Include Crystal Growth.
- Return names, state identifiers, dimensions, and relevant metadata.

### Automaton loading
- Load a selected built-in automaton.
- Return its definition and initial grid.
- Validate the definition and initial state before returning it.

### Custom JSON loading
- Accept a user-provided JSON automaton definition.
- Use existing validators and schemas.
- Return the validated configuration and initial grid.
- Do not require modification of Python source files to load another compatible automaton.
- Reject invalid JSON or invalid rules with meaningful error messages.
- Avoid unsafe arbitrary filesystem path access.

### Simulation
- Compute exactly one next generation.
- Compute N generations using the existing experiment runner.
- Accept a configurable positive generation count.
- Optionally retain intermediate generations.
- Preserve the original grid.
- Return consistent generation indices and state data.
- Support all five existing automata.
- Avoid unnecessary history allocation when history retention is disabled.

### Saving experiments
- Save a simulation using the existing Python storage modules.
- Support both single-transition and multi-generation results.
- Preserve the current storage format and compatibility.
- Return a save identifier and confirmation.

### Recovering experiments
- List existing saved simulations.
- Recover legacy single-transition records.
- Recover multi-generation experiment records.
- Validate recovered records.
- Return the initial grid, generation count, final grid, and intermediate history when available.
- Distinguish unavailable historical data from an empty history.
- Do not fabricate missing generations.

### Run All
- Provide a Run All operation equivalent to the existing CLI's one-generation behavior.
- Return the results for the original four built-in automata.
- Do not silently change the CLI's Run All semantics.

### Error handling
- Handle malformed JSON, missing configurations, invalid states, conflicting rules, invalid generation counts, and invalid save identifiers.
- Return appropriate HTTP status codes and structured error messages.
- Do not expose internal filesystem paths or stack traces to the frontend.

Use Pydantic request/response models where appropriate, without unnecessary abstraction.

## 4. React frontend

Create the web application inside:

`frontend/`

Use:
- React.
- TypeScript.
- Vite.
- Modern CSS.

Prefer lightweight dependencies. Do not introduce an elaborate component or state-management framework unless justified.

### Main interface layout

Build a polished scientific simulation dashboard.

**Header**
- CelLab branding.
- Clear project title.
- Current automaton name.
- Small status indicator for API availability.

**Left panel — Automaton configuration**
- Dropdown or cards for available automata.
- State list.
- Neighborhood type.
- Grid dimensions.
- Load custom JSON option.
- Clear information about the selected automaton.

**Central panel — Simulation grid**
- Responsive two-dimensional grid.
- Distinct colors for each cell state.
- Clear cell borders.
- Smooth, restrained state-change animations.
- Proper support for different grid sizes.
- Display of the current generation index.

**Simulation controls**
- Next Generation.
- Previous Generation when history is available.
- Reset.
- Play.
- Pause.
- Configurable playback speed.
- Run N Generations.
- Generation count input.
- History retention toggle.
- Save Experiment.
- Recover Experiment.
- Run All.

**Right panel — Information and statistics**
- State legend.
- Number of cells in each state.
- Current generation number.
- Total requested generations.
- Simulation status.
- Optional concise explanation of the active automaton.

Avoid excessive visual complexity. Secondary controls can use tabs, drawers, or collapsible panels.

## 5. Complete CLI feature parity

The web UI must support every existing L6 CLI workflow:

1. Select Game of Life.
2. Select Brian's Brain.
3. Select Forest Fire.
4. Select Cyclic Cellular Automaton.
5. Run All (preserving the original four-automaton behavior).
6. Recover Saved Simulation.
7. Load Compatible JSON File.
8. Exit equivalent: stop/pause playback and reset or leave the simulation view safely.

Also expose the existing additional functionality:
- Configurable generation count.
- Optional intermediate generation history.
- Initial/current/final generation display.
- Saving results.
- Recovering results.
- Validation feedback.

Do not implement an artificial Exit button merely to imitate the CLI. Adapt CLI functionality appropriately to a web interface.

## 6. Simulation behavior and state management

This is particularly important.

- Python remains the only source of truth for cellular automata transitions.
- React must not independently compute transition rules.
- Prevent concurrent or overlapping simulation requests.
- Correctly stop playback when switching automata.
- Correctly stop playback when resetting.
- Avoid stale responses overwriting newer simulation states.
- Handle API failures gracefully.
- Keep generation indices accurate.
- Do not display fabricated intermediate generations.
- Ensure Previous Generation uses actual stored history.
- Reset must restore the selected automaton's original initial grid.
- Do not silently change the meaning of saved experiments.
- Do not make a UI control appear functional unless it is implemented.

For playback, prefer a simple, reliable approach rather than complex asynchronous state management.

## 7. Visual design — light mode

Create a professional, modern interface appropriate for an academic simulation application.

Style:
- Bright white or off-white background.
- Neutral panels and subtle borders.
- Rounded cards and buttons.
- Consistent typography.
- Restrained use of accent colors.
- Clear hierarchy.
- Accessible contrast.
- Responsive layout.
- Useful loading indicators.
- Clean error and success messages.

The cellular grid should be the visual focus.

Use state-dependent colors with a clear legend.

Suggested examples:
- Forest Fire: TREE green, FIRE red/orange, EMPTY light gray.
- Game of Life: ALIVE dark blue or teal, DEAD light gray.
- Crystal Growth: CRYSTAL blue/cyan, EMPTY light gray.

Make sure the colors remain distinguishable and state labels are accessible.

No external images or unnecessary animations are required.

## 8. Testing and verification

Preserve the existing 88 passing Python tests.

Add focused tests for the new API:

- Built-in automata discovery.
- Loading and validation.
- One-generation simulation.
- N-generation simulation.
- Invalid generation counts.
- Save and recover.
- Legacy saved-record compatibility.
- Custom JSON validation.
- Run All.

For the frontend:
- Install dependencies locally.
- Run TypeScript checks.
- Run the production build.
- Add focused frontend tests where practical.
- Verify API integration and loading/error states.
- Verify Play/Pause, Reset, Next, history navigation, and automaton switching.

Run the full existing backend test suite.

Do not report features as tested if they were not actually verified.

## 9. Documentation

Update the root README with separate instructions for:

1. Installing Python backend dependencies.
2. Starting FastAPI.
3. Installing frontend dependencies.
4. Starting Vite.
5. Running the original CLI.
6. Running tests.
7. Building the frontend for production.

Use Windows PowerShell examples compatible with the current project.

Update `docs/ARCHITECTURE.md` to reflect the implemented frontend and API.

Add a short frontend demo section to `docs/L6_DEMO.md`, clearly distinguishing the optional web interface from the already verified CLI.

Update `.gitignore` for Node.js, Vite, and frontend-generated files.

Record this Codex interaction factually in the existing AI interaction documentation. Preserve earlier records, and do not fabricate original transcripts.

## 10. Scope and priorities

Prioritize in this order:

1. Working FastAPI integration with the existing Python engine.
2. Accurate grid visualization and automaton selection.
3. One-generation and N-generation execution.
4. Playback, reset, and history navigation.
5. Saving and recovering experiments.
6. Custom JSON loading.
7. Run All.
8. Visual polish and responsive design.

If an optional visual enhancement threatens functionality, simplify it.

Do not create placeholder buttons, hardcoded simulation results, or fake backend responses.

Do not implement neural networks, reinforcement learning, or natural-language parsing.

Do not modify the existing engine semantics.

## 11. Final handoff

After implementation, provide:

- Summary of implemented features.
- Files added and modified.
- REST API endpoint list.
- Exact commands to run backend and frontend.
- Python test results.
- TypeScript/build results.
- Frontend/API integration verification results.
- Remaining bugs or limitations.
- A checklist comparing the web interface against every existing CLI feature.
- A short 2-minute web demonstration scenario.

Do not commit, push, merge, or switch branches.

**Success criterion:** A real, working light-mode React interface with complete L6 CLI feature parity, using the existing Python engine, without destabilizing the tested L6 implementation.
```

## 5. Implementation and testing evidence reported by Codex

The user pasted a Codex implementation report stating:

- Implemented React + TypeScript + Vite on `feature/react-frontend-mvp`, integrated with FastAPI.
- Supported five built-in automata, custom JSON validation, next/previous, N-generation runs, optional history, playback and speed, reset, statistics, save/recover, and original-four Run All.
- **102 Python tests passed; 4 frontend tests passed; TypeScript checks and Vite production build passed.**
- Live Vite → FastAPI HTTP checks passed for five automata, one/N-step execution, Run All, and validation errors.
- **Not yet manually verified at report time:** browser appearance, browser file picker, complete save/recover flow.
- Codex stated it did not commit, push, merge, or switch branches.
- Reported limitations: unbounded long runs/history, inability of reset to cancel existing server computation, nontransactional JSON storage, no production hosting/authentication.

### Approvals and command execution discussed

ChatGPT advised that the user could approve specific, recognized development/test commands after checking their working directory and scripts. These were:

```text
npm.cmd run build
npm.cmd test
npm.cmd run dev
```

The user also showed a long Python command updating `README.md`, `docs/ARCHITECTURE.md`, and `docs/L6_DEMO.md`. ChatGPT advised that only the particular reviewed command should be approved, and that documentation diffs should be checked afterward. The pasted command was truncated, so not all contents were independently verifiable in chat.

### Manual browser observations reported in conversation

The user provided screenshots of the light-mode interface, including a Game of Life grid and a Run All panel. ChatGPT observed that the UI displayed the number of rules but not their rule definitions and that saved experiments were identified by technical IDs. A saved Cyclic Cellular Automaton record was inspected in JSON. Backend logs shown by the user included a `201 Created` response from `POST /api/experiments` and `200 OK` for experiment recovery; this confirms successful HTTP requests, not automatically full browser state reconstruction. The user later stated a new saved experiment appeared to work. The Run All screenshot showed all four original systems.

## 6. Prompt D — Optional combined polish (original ChatGPT draft; may not have been sent to Codex)

```text
Please make two targeted usability improvements to the existing CelLab React frontend.

1. **Display automaton transition rules**
   - In the Configuration panel, add a collapsible "Transition rules" section.
   - Show every rule of the currently selected automaton, including custom JSON configurations.
   - Display the source state, destination state, and all conditions in a readable format.
   - Clearly indicate AND conditions and unconditional transitions.
   - Use the existing configuration data returned by FastAPI.
   - Do not hardcode rules or change engine semantics.
   - Do not implement a rule editor; this is read-only visualization.

2. **Improve saved experiment labels**
   - Keep existing save identifiers unchanged internally.
   - In the saved experiments list, display a friendly label using available metadata, such as automaton name and generation number.
   - Keep the full identifier accessible, for example in smaller text.
   - Do not invent unavailable metadata.
   - Preserve legacy and new experiment recovery compatibility.

Constraints:
- Work only on the current `feature/react-frontend-mvp` branch.
- Keep all existing CLI and API functionality unchanged.
- Make minimal, focused changes.
- Add or adjust frontend tests for these features.
- Run Python tests, frontend tests, TypeScript checking, and production build.
- Do not commit, push, merge, or switch branches.
- Report exactly what was changed and verified.
```

## 7. Prompt E — Full pre-submission polish alternative (original ChatGPT draft; may not have been sent)

```text
Please perform the final targeted polish of the CelLab React interface before GitHub submission.

The current React + FastAPI application is implemented and tested. Keep the existing design, architecture, and simulation functionality unchanged.

### 1. Display transition rules

Add a clean, collapsible "Transition rules" section to the left Configuration panel.

Requirements:
- Show every transition rule for the currently selected automaton.
- Support built-in automata and custom JSON configurations.
- Display source state, target state, and all conditions.
- Render operators and thresholds accurately.
- Show how multiple conditions are combined (AND).
- Clearly distinguish unconditional rules.
- Explain the default behavior when no rule applies.
- Use the actual validated configuration returned by the Python API.
- Do not hardcode rule descriptions.
- Do not modify the engine or implement a rule editor.
- Keep the layout compact and consistent with the existing light-mode design.

### 2. Improve saved experiment labels

The saved experiment dropdown currently displays long technical identifiers.

Make the list easier to understand:
- Display a friendly label using metadata actually available, such as automaton name and number of generations.
- Preserve the original identifier for recovery.
- Keep full identifiers accessible.
- Do not fabricate unavailable metadata.
- Preserve compatibility with legacy and newer experiment formats.
- Avoid introducing expensive or unnecessary API requests.

### 3. Verification

- Preserve existing frontend/backend behavior.
- Add focused tests for displaying rules and saved experiment labels.
- Run the complete Python test suite.
- Run frontend tests.
- Run TypeScript type checking.
- Run the production build.
- Verify that custom JSON rules are displayed correctly.
- Check for regressions in saving and recovering experiments.
- Update documentation only where needed.

### 4. Git safety

- Stay on `feature/react-frontend-mvp`.
- Do not commit, push, merge, or switch branches.
- Do not introduce unrelated changes.

At the end, report the files modified, test results, and any remaining limitations.
```

## 8. Prompt F — Final recommended minimal rule-display polish (original ChatGPT draft)

```text
Please make one small, targeted improvement to the existing CelLab React frontend.

Add a collapsible **Transition rules** section in the Configuration panel.

Requirements:
- Display all actual transition rules of the selected automaton.
- Support both built-in automata and user-uploaded JSON definitions.
- Show the source state, target state, comparison operator, threshold, and relevant neighboring state.
- Display multiple conditions accurately, including AND relationships.
- Clearly indicate unconditional transitions and the default behavior when no rule matches.
- Read rules directly from the validated automaton configuration already available in React.
- Do not hardcode descriptions or change simulation logic.
- Preserve the current light-mode design.
- Make the smallest reasonable changes.

Safety:
- Stay on `feature/react-frontend-mvp`.
- Do not modify the Python engine, storage, API contracts, or existing JSON definitions.
- Do not commit, push, or merge.
- Do not perform unrelated refactoring.

Add a focused frontend test for rule rendering, then run the existing Python tests, frontend tests, TypeScript checks, and production build.

Report the changes and results.
```

**Status:** This prompt was recommended near the end of the conversation. The chat does not establish that the user executed it or that it was successfully implemented; update only when Codex supplies actual evidence.

## 9. Prompt G — AI documentation organization (original ChatGPT draft; proposed rather than confirmed executed)

```text
Please organize the existing CelLab AI interaction documentation for the React + FastAPI implementation.

Update `docs/AI_Interactions.md` with a short factual entry for November 4, 2026, referencing the frontend implementation, AI tools used, verification results and links to detailed records.

Preserve all existing documentation and records.

Create or update the relevant files under `docs/ai-interactions/` using only original prompts and responses actually available in the current Codex session.

Do not fabricate, paraphrase or claim that reconstructed summaries are verbatim transcripts.

If the complete ChatGPT conversation is not accessible, leave a clearly marked placeholder for manual insertion rather than inventing it.

Do not modify application code, commit, push or merge.

Report what was documented and which original transcripts still need to be added.
```

## 10. Manual test procedure discussed with ChatGPT

A step-by-step browser verification plan was supplied:

1. Select Game of Life, reset, then step twice to verify the blinker alternates vertical/horizontal.
2. Run 10 generations with history enabled, navigate between frames, confirm three live cells.
3. Select Crystal Growth, run two generations and confirm 25 CRYSTAL cells.
4. Use the browser file picker to load `backend/automata/crystal_growth.json`, then inspect invalid-JSON feedback.
5. Run Game of Life for five generations with retained history, save the experiment, switch automata, recover by exact ID, verify state and history.
6. Check Play/Pause/Reset.
7. Run All to display the four original automata.

The discussion also clarified that randomly generated technical experiment identifiers are legitimate; the exact saved record must be matched to the ID, and the success of HTTP save/recover requests does not alone establish that all UI state was restored correctly.

## 11. What remains and what should NOT be claimed

- React/FastAPI are now reported implemented and integrated; tests/build/HTTP checks were reported passing as above.
- The browser file-picker and full history recovery needed manual confirmation at the time of the Codex report; do not mark as manually verified without independent evidence.
- Rule-display polish is requested/proposed, not yet confirmed in this ChatGPT conversation.
- Human-readable save labels are optional and were explicitly deferred to avoid excessive scope.
- The final academic requirements — NN/RL experiment, NLP handling, and automated answers to additional questions — are not claimed as completed by this frontend feature.
- The user's full ChatGPT conversation and Codex session contain more messages than this curated log and must be archived separately when a complete transcript is required.

## 12. Source archive checklist

- [ ] Preserve original exported ChatGPT conversation (if complete transcript is required).
- [ ] Preserve original Codex implementation session, including exact submitted prompt, tool approvals, test results, and final report.
- [ ] Mark which optional polish prompts were actually sent and which were only suggested.
- [ ] Update rule-rendering test evidence once the feature is implemented.
- [ ] Link this curated file from `docs/AI_Interactions.md` without overwriting earlier L6 records.

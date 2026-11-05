# L6 demonstration - 2-3 minutes

Start from the repository root:

```powershell
cd backend
..\.venv\Scripts\python.exe main.py
```

## Sequence

1. **0:00-0:40 - World, rules, one transition.** Select `1` (Game of Life). Press Enter for 1 generation, Enter for no history. Explain DEAD/ALIVE and the JSON rules. The three vertical ALIVE cells become three horizontal cells. "Every cell reads the same old generation. We build a separate next grid, so newly changed cells do not influence this step."
2. **0:40-1:15 - Storage/recovery.** Enter `y` to save; note the printed filename. Select `6`, choose that filename's displayed number, and show the recovered initial/next grids. This is the legacy transition format.
3. **1:15-1:50 - Multiple states.** Select `2` (Brian's Brain), Enter for 1, Enter for no history, then `n` for save. Explain FIRING -> DYING -> OFF and OFF firing with exactly two FIRING neighbors. The same engine applies these JSON rules.
4. **1:50-2:30 - Small multi-generation enhancement.** Select `1`, enter `2`, enter `y` for history. Generation 1 is horizontal; generation 2 is vertical again. Enter `y` to save. Select `6` and the new filename; enter `y` to show the intermediate grid. This uses the versioned experiment format.
5. **2:30-3:00 - Optional breadth/check.** Select `5` to run all four examples without further prompts. Select `0` to exit.

Recovery numbers depend on existing saves; choose by the filename printed when saving. Option `7` can load another compatible JSON configuration by path. Enter `0` as a generation count to demonstrate rejection, then Enter to accept the default.

## Five likely technical questions

1. **Why is the engine generic?** It interprets source/destination states and neighbor-count conditions; there are no automaton-name branches. New compatible JSON can be loaded with option 7.
2. **What guarantees synchronous updates?** `next_generation` reads the old grid and constructs a separate grid. The runner calls it once per generation and preserves the original input.
3. **What happens when two rules match?** Same destination is allowed; different destinations are rejected by validation and guarded against by the engine. List order provides no priority.
4. **What is stored?** Legacy saves contain definition and before/after grids. Version 1 experiments also contain generation count, retention/save settings, final grid, and optional generations 0 through N. Recovery validates records; experiment records are replay-checked.
5. **Can it simulate every example in the PDF?** No. It supports deterministic discrete states and local neighbor-count rules with fixed edges. Rule 30 needs positional checks; agents, probability, and arithmetic need extensions. Natural-language parsing and NN/RL work belong to later deliverables.

## Optional Crystal Growth example

Select `7`, enter `crystal_growth.json`, enter `3` generations, and choose `y` for history. Generation 1 is the central 3x3 crystal block. Generation 2 fills the whole 5x5 grid (16 additions, including the four corners); generation 3 is unchanged. The existing rule is EMPTY -> CRYSTAL with at least one CRYSTAL Moore neighbor, so generation 2 adds more than just the four corners. Choose `n` to skip saving, or `y` to recover the history later through option 6. This demonstrates another compatible JSON file without changing the engine or the four-option registry.


## Optional web interface demonstration (two minutes)

The CLI remains independently available; the web interface is an optional L6 presentation layer over the same engine. Start FastAPI and Vite using the root README.

1. (0:00-0:25) Select Game of Life, enable history, and click Next Generation. Show the changed blinker and state counts; Previous returns to the actual initial grid.
2. (0:25-0:50) Play, Pause, then Reset. Run two generations with history and navigate the stored frames.
3. (0:50-1:15) Save, Browse saved, select the new identifier, and Recover. Show initial/final generation indices. Disable history for another batch and explain the missing intermediate frames.
4. (1:15-1:40) Select Crystal Growth and run two steps to fill the grid. Load backend/automata/brians_brain.json through the JSON picker; an invalid-state file produces validation feedback.
5. (1:40-2:00) Run All to compare one-step results for the original four systems. Inspect a result. Pause or Reset to leave the workspace safely.

See WEB_INTERFACE.md for actual automated verification and remaining manual browser checks; this scenario is a presentation guide, not a claim that a human performed it.

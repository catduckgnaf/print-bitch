# Print Bitch

Reliable Discord and AI integration framework for ZMod AD5X 3D printers.

Print Bitch connects AI agents to Klipper and Moonraker 3D printers through Discord without getting stuck in runaway command loops, spamming mobile chat UIs, or breaking native printer firmware features.

## Why Print Bitch

Connecting autonomous or conversational AI agents to 3D printers over Discord creates distinct failure modes:

1. Infinite polling loops where an agent repeats the same command waiting for a print state change.
2. Discord mobile UI breakage when an agent outputs long clarification lists that exceed visible screen real estate.
3. Overengineered plugins that duplicate features already built into printer firmware.

Print Bitch solves these problems by providing lightweight, deterministic interaction guards while delegating physical printer logic to native ZMod firmware and stock OrcaSlicer Flatpak.

## Core Architecture

### 1. Deterministic Discord Interaction Guards

Located in `plugins/print-feedback/__init__.py`, these pure Python standard library hooks register as agent pre tool call interceptors:

* **Choice Capping**: Automatically caps clarification question lists to 4 choices on Discord and appends notice that an Other path exists. This keeps interactive messages readable on phone screens.
* **Command Loop Protection**: Detects identical terminal command executions within a single turn and halts the third repetition. This prevents agents from polling Moonraker or Klipper indefinitely.

### 2. Native ZMod AD5X Infinite Spool

Rather than installing third party multi spool plugins like Bambufy, Print Bitch relies on native ZMod firmware logic:

* When multiple spools share matching color and material type, the printer switches spools automatically upon runout.
* Bambufy was evaluated and rejected because it conflicts with the native AD5X touch screen.
* The complete firmware compatibility contract is documented in `docs/AD5X-CONTRACT.md`.

### 3. Direct Moonraker and Stock Slicer Workflow

Print Bitch avoids custom slicer forks or background daemon bloat:

* Preserves the standard OrcaSlicer Flatpak for slicing and tool mapping.
* Direct Moonraker API control for print execution.
* Zero third party Python dependencies required for guard primitives.

## Running Tests

Print Bitch includes an isolated test suite requiring only the Python standard library.

Run tests:

```sh
python3 -m unittest discover -s tests -v
```

All 6 test cases verify choice truncation, command loop blocking, session isolation, and hook registration without connecting to live hardware.

## Repository Layout

* `plugins/print-feedback/`: Core interaction guard hooks for AI agent environments.
* `tests/`: Portable unit tests for interaction guards.
* `docs/AD5X-CONTRACT.md`: ZMod AD5X compatibility contract and infinite spool rules.
* `docs/REUSE-MAP.md`: Architectural analysis of upstream references including ZMod, Bambufy, Orca MCP, and Klipper MCP.
* `references/manifest.json`: Pinned cryptographic hashes of evaluated upstream projects.

## Getting Started for ZMod Users

1. Clone this repository into your agent environment or workspace.
2. Register the hooks in your agent runtime using `plugins/print-feedback/register(ctx)` or environment variables.
3. Configure your printer spools in ZMod with identical color and material names to enable automatic infinite spool fallback.
4. Issue print instructions through your Discord bot with confidence that runaway agent loops will be caught before they spam your channel.

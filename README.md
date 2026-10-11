# Print Buddy

Drop a link. Drop a file. Let Discord handle the rest.

Print Buddy is an automated 3D printing pipeline designed for Discord. It removes the desktop slicer, manual SD card shuffling, and confusing printer menus from household printing. Anyone in the house can drop a MakerWorld link, a Printables link, or a raw 3MF or STL file into a Discord channel, and the bot handles downloading, multi plate packing, color matching, headless slicing, and print staging.

## Why This Exists: The Household Test

Standard desktop 3D printing is built for hobbyists who enjoy tinkering with layer heights, tree supports, and temperature towers. It is terrible for anyone who just wants an object out of the printer.

Print Buddy was built so catduck's wife could see a model on MakerWorld, drop the URL into `#3d-printer` on Discord, and get a finished print without ever launching OrcaSlicer, selecting printer profiles, or guessing which spool is loaded in which slot.

## How It Works in Discord

Everything happens inside a single Discord channel. The bot speaks in plain English, keeps terminal spam out of the chat, and provides immediate feedback.

### 1. Drop a link or file

A user posts a link or uploads a file into the `#3d-printer` channel:

> **Mrs catduck:** https://makerworld.com/en/models/931302-holder-for-post-it-notes

### 2. Instant receipt

The bot responds in seconds with a plain English confirmation, an estimated preparation time, and a witty remark:

> **Print Buddy:** Downloading the file from MakerWorld and prepping it for the printer, about 2 minutes. The desk organizer is already more structured than catduck's weekend plans.

### 3. Automated preparation and job card

Behind the scenes, the pipeline:
* Fetches the model files and metadata
* Merges multi plate assemblies onto the bed
* Matches requested colors with loaded filaments in Spoolman
* Runs headless slicing through OrcaSlicer
* Verifies nozzle size, temperatures, and printer readiness

The bot posts the job summary with a single interactive button:

> **Print Buddy:**
> **Model:** Post it Note Holder with Stencils
> **Filament:** Matte Black PLA (~48g)
> **Estimated print time:** 1 hour 14 minutes
> **Target printer:** Flashforge AD5X (ZMod Klipper)
> 
> [🔘 Slice and print now (bed is clear)]

### 4. One tap launch and live updates

Once someone confirms the bed is clear by clicking the button, the print starts immediately:

> **Print Buddy:** Bed heating started. Job sent to Moonraker. Finish time estimated for 4:22 PM ET. Don't touch the build plate.

When the print finishes, the bot posts completion stats and records the job details directly to an Obsidian archive note for maintenance tracking.

## Architecture and Pipeline

Print Buddy ties several open tools into a single conversational interface:

* **Discord Interface:** Powered by Hermes Agent in the `#3d-printer` channel.
* **Intake and Scraping:** Fetches model packages from MakerWorld and Printables or extracts uploaded attachments.
* **Headless Slicing:** Uses the OrcaSlicer Flatpak in CLI mode, applying calibrated printer and filament profiles.
* **Filament and Spool Inventory:** Queries Spoolman over LAN to match requested colors and materials against loaded slots.
* **Printer Control:** Sends G-code directly to Moonraker and Klipper over the local network.
* **Interaction Guards:** Python hooks prevent runaway agent command loops and enforce concise UI button choices.

## Hardware Support and ZMod Plugin

The live setup runs on a Flashforge Adventurer 5M / AD5X running ZMod Klipper firmware with an internal filament system (IFS).

### Spool Slot Matching Macro (`print_bitch.cfg`)

ZMod natively supports infinite spool switching during a print when an active spool runs out, provided another slot contains the exact same color and material.

The included `print_bitch.cfg` Klipper macro lets users check backup compatibility before a job begins:

```gcode
PRINT_BITCH SLOT=1
```

If slot 1 and slot 3 are both black PETG, the macro confirms:
```
PRINT_BITCH: black / PETG also on slot 3. ZMod can switch. This macro does not.
```

Querying `PRINT_BITCH COLOR=black MATERIAL=PETG` checks availability across all four slots without assuming an active toolhead.

### ZMod Plugin Installation

Run on the printer console:

```gcode
ENABLE_PLUGIN name=print-bitch
```

Add your slot assignments to `mod_data/user.cfg` in a `[gcode_macro _PRINT_BITCH_VARS]` block, then run `FIRMWARE_RESTART`.

Moonraker update manager entry:

```ini
[update_manager print-bitch]
type: git_repo
path: /root/printer_data/config/mod_data/plugins/print-bitch
origin: https://github.com/catduckgnaf/print-bitch.git
primary_branch: main
managed_services: klipper
channel: dev
is_system_service: False
```

## Repository Structure

* `plugins/print-feedback/`: Hermes pre-tool execution guards that limit excessive clarify choices and block repeated terminal loops.
* `print_bitch.cfg`: Klipper G-code macro for checking backup IFS slot matching.
* `install.sh` / `uninstall.sh` / `update.sh`: ZMod plugin lifecycle scripts.
* `tests/`: Unit tests verifying macro logic and interaction guards without requiring physical hardware.
* `docs/`: Technical specifications for AD5X integration and upstream tool research.

## Running Tests

Run the test suite with standard Python:

```bash
python3 -m unittest discover -s tests -v
```

## Roadmap: Expanding to More Klipper Printers

* **TODO: Generic Klipper printer support.** The pipeline currently targets a Flashforge AD5X on ZMod, but the core intake, slicing, and Moonraker dispatch are printer agnostic. Adding other Klipper printers (such as Sovol, Voron, or custom beds) is architecturally straightforward:
  * Replace hardcoded bed dimensions (220x220) and nozzle parameters with configurable printer profiles.
  * Support single extruder workflows without multi spool IFS requirements.
  * Standardize start, cancel, and status calls using generic Klipper macros.
  * This is not difficult to implement, but requires thorough real world testing on physical hardware before claiming support.

## Links and Reference

* ZMod AD5X docs: [AD5X.md at 0017033](https://github.com/ghzserg/zmod/blob/001703371c90e228defce41bb4230b7fafd37fea/docs/en/AD5X.md)
* ZMod firmware project: [ghzserg/zmod](https://github.com/ghzserg/zmod)
* ZMod plugin guide: [wiki.zmod.link/Plugin](https://wiki.zmod.link/Plugin/)
* OrcaSlicer CLI documentation: [CLI mode](https://github.com/OrcaSlicer/OrcaSlicer/wiki/cli_mode)



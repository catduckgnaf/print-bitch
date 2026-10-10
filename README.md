# Print Bitch

Discord intake and an AD5X print workflow for MakerWorld and Printables 3MF jobs.

The code in this repository is a Hermes pre-tool hook. It is not a ZMod plugin and it does not talk to a printer. Slicing, color assignment, and print start live in the private AD5X skill that drives a stock OrcaSlicer Flatpak and Moonraker. That split is deliberate. A ZMod plugin runs on the printer as Klipper config. This hook runs in the agent, before a tool call.

## What is in this repository

`plugins/print-feedback/__init__.py` registers two guards. Both are stdlib only.

* Choice cap. On the Discord printer profile, a clarify question with more than four choices keeps the first four and says an Other path exists.
* Repeat stop. The third identical terminal command in one turn is blocked. Distinct commands are not limited. Without a turn id, the guard does nothing.

Tests are `python3 -m unittest discover -s tests -v`. They do not contact a printer, Discord, or the network.

`docs/AD5X-CONTRACT.md` records the ZMod same-color, same-material infinite-spool rule and the local extra checks. Native selection order and installed screen behavior are not verified here.

`docs/REUSE-MAP.md` and `references/manifest.json` pin five upstream archives by commit and SHA-256: mcp-3D-printer-server, orcaslicer-mcp, klipper-mcp, zmod, and bambufy. Those archives are not in this repo. Nothing from them is installed.

## AD5X workflow this documents

These behaviors are implemented in the printer skill, not in the files above. The skill target is a Flashforge AD5X on ZMod, 220 by 220 mm, stock OrcaSlicer Flatpak, direct Moonraker. No Prusa slicing path. No Room, no custom slicer fork, no MCP.

* MakerWorld and Printables links. A reposted link is a new intake. Old jobs, colors, and approvals are not reused.
* 3MF plate inventory before any slice. Source triangles and transforms are kept. Author settings that Orca rejects are clamped in the job, never written back into the source file.
* Multi-plate 3MF files merge onto one AD5X bed and slice once. Separate plates only when asked.
* Color and slot assignment stays bound to that source. Slicer tools are not physical IFS slots. A link or a color choice is not permission to slice, upload, or start.
* One-line preview after a model link and before color selection: what it is, estimated time, estimated filament. Missing numbers stay missing.
* Job details after a real start: model, time plus warmup and finish, filament weight, slot, color, material, printer, nozzle, temperatures, calibration.
* AD5X startup uses the installed ZMod macros. Native screen mode owns mesh and Z offset. Screenless mode is a separate checked state.
* Print start is one shot after the bed is confirmed clear. A timed-out start is checked once and not retried.
* Native infinite spool is the backup plan: same stored color and material. No agent polling loop. No Bambufy. Bambufy fights the native screen.
* Spoolman is the inventory record once seeded. Physical sensors own presence. Automatic runout switching is not claimed.

## Not a ZMod plugin

ZMod installs a plugin with `ENABLE_PLUGIN`, then runs that repo's `install.sh`. The plugin is Klipper config, usually `name.cfg`, plus optional `uninstall.sh` and `update.sh`. See the [ZMod plugin guide](https://wiki.zmod.link/Plugin/) and the [g28_tenz example](https://github.com/ghzserg/g28_tenz).

This repository has none of that. Turning the Discord hook into `install.sh` would put agent policy on the printer, which is the wrong machine. A printer-side plugin would be a new Klipper extra with its own install scripts. Whether any of this workflow belongs there is tracked as an open issue, including a generic Klipper path that is not AD5X-only.

## Links

* ZMod AD5X docs, pinned: [AD5X.md at 0017033](https://github.com/ghzserg/zmod/blob/001703371c90e228defce41bb4230b7fafd37fea/docs/en/AD5X.md)
* ZMod: [ghzserg/zmod](https://github.com/ghzserg/zmod)
* Plugin guide: [wiki.zmod.link/Plugin](https://wiki.zmod.link/Plugin/)
* OrcaSlicer CLI: [CLI mode](https://github.com/OrcaSlicer/OrcaSlicer/wiki/cli_mode)
* MakerWorld and Printables are the two source sites. Model files are downloaded per intake and are not stored here.

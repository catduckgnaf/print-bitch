# Print Bitch

Discord intake and an AD5X print workflow for MakerWorld and Printables 3MF jobs.

The code in this repository is two things that do not share a process. `plugins/print-feedback` is a Hermes pre-tool hook. It is not installed on the printer. `print_bitch.cfg` plus `install.sh` is a ZMod plugin. `ENABLE_PLUGIN` runs the script on the printer and Klipper loads the cfg. The macro reports matching IFS slots. It does not switch filament, and it does not load the Discord hook.

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

## ZMod plugin

`ENABLE_PLUGIN name=print-bitch` runs `install.sh`. The script does not edit `printer.base.cfg`. Copy the four slot colors and materials into `mod_data/user.cfg` as a `[gcode_macro _PRINT_BITCH_VARS]` block, then `FIRMWARE_RESTART`. Query with `PRINT_BITCH SLOT=1`, or `PRINT_BITCH COLOR=black MATERIAL=PETG`.

A match is the same stored color and the same stored material, which is the rule ZMod already uses for infinite spool. A value of `0` is ignored. The reply names the other slots. ZMod does the switch. This macro does not call `SET_EXTRUDER_SLOT` and does not feed filament.

Moonraker update manager, if you want it:

```
[update_manager print-bitch]
type: git_repo
path: /root/printer_data/config/mod_data/plugins/print-bitch
origin: https://github.com/catduckgnaf/print-bitch.git
primary_branch: main
managed_services: klipper
channel: dev
is_system_service: False
```

`update.sh` replaces the plugin files and leaves `user.cfg` alone. `DISABLE_PLUGIN` runs `uninstall.sh`, then ZMod deletes the plugin directory. Remove the variable block yourself.

Slicing, color assignment, and print start still live in the private AD5X skill. Those do not run on the printer. A generic Klipper path that is not AD5X-only stays an open issue.

## Links

* ZMod AD5X docs, pinned: [AD5X.md at 0017033](https://github.com/ghzserg/zmod/blob/001703371c90e228defce41bb4230b7fafd37fea/docs/en/AD5X.md)
* ZMod: [ghzserg/zmod](https://github.com/ghzserg/zmod)
* Plugin guide: [wiki.zmod.link/Plugin](https://wiki.zmod.link/Plugin/)
* OrcaSlicer CLI: [CLI mode](https://github.com/OrcaSlicer/OrcaSlicer/wiki/cli_mode)
* MakerWorld and Printables are the two source sites. Model files are downloaded per intake and are not stored here.

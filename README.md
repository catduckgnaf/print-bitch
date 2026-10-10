# Print Bitch

Fast printing tools for ZMod AD5X, preserving direct Moonraker control and the existing OrcaSlicer Flatpak.

## Status
Private project with a small, offline-testable Discord interaction-guard module. It caps clarification choices and limits identical terminal-command repeats within one identified turn. It does not control the printer, slicer, files, network, or live services, and it has not been installed or printer validated. Existing hardening remains paused pending reference research.

## Tests

Run the portable guard tests with Python 3.10 or newer:

```sh
python3 -m unittest discover -s tests -v
```

The module requires only the Python standard library. The test suite exercises the isolated guards without loading Hermes, Discord, printer state, Moonraker, or slicer integrations. These are portable guard primitives; they do not represent a complete Discord reliability audit or enable live intake behavior.

## MVP
Exact-job/color regression, native same-color and same-material infinite spool fallback, installed-version ZMod compatibility, Discord reliability and latency preservation.

## Boundaries
No MCP installation, custom ZMod plugin, slicer migration or new service in MVP. ZMod owns physical fallback; printer specialist owns physical acceptance. No private job records, secrets, webhook URLs or machine configuration in this repository. Upstream material is reference, not operating authority.

## Tracking
[Issues](https://github.com/catduckgnaf/print-bitch/issues) own features and defects. [MVP milestone](https://github.com/catduckgnaf/print-bitch/milestone/1) defines release acceptance. Kanban remains for specialist handoffs and dependencies, not duplicate feature tracking. No unattended work without verified completion and failure delivery.

## Prioritized backlog
- [#1 Restore exact-job slicing and color assignment regression](https://github.com/catduckgnaf/print-bitch/issues/1)
- [#2 Integrate native ZMod infinite spool fallback](https://github.com/catduckgnaf/print-bitch/issues/2)
- [#3 Verify installed ZMod AD5X compatibility contract](https://github.com/catduckgnaf/print-bitch/issues/3)
- [#4 Audit Discord intake and job event reliability](https://github.com/catduckgnaf/print-bitch/issues/4)
- [#5 Measure and protect routine-path latency](https://github.com/catduckgnaf/print-bitch/issues/5)
- [#6 Add optional artifact-bound color and object previews](https://github.com/catduckgnaf/print-bitch/issues/6)
- [#7 Evaluate Bambufy and related ZMod plugins without installation](https://github.com/catduckgnaf/print-bitch/issues/7)
- [#8 Capture pinned upstream references with provenance and license review](https://github.com/catduckgnaf/print-bitch/issues/8)
- [#9 Evaluate offline slice analysis and print outcome learning](https://github.com/catduckgnaf/print-bitch/issues/9)

## Sources
- https://wiki.zmod.link/AD5X
- https://wiki.zmod.link/Plugin/
- https://github.com/ghzserg/notify
- https://github.com/function3d/bambufy
- https://github.com/DMontgomery40/mcp-3D-printer-server
- https://github.com/MaxEllis/orcaslicer-mcp
- https://github.com/MaxEllis/klipper-mcp

License for project code is not yet selected; third-party code is not imported or relicensed.

# ZMod AD5X MVP implementation contract

## Source authority
Official AD5X documentation at ZMod commit 001703371c90e228defce41bb4230b7fafd37fea states that multiple spools assigned the same color AND material type automatically switch when the active spool runs out.
https://github.com/ghzserg/zmod/blob/001703371c90e228defce41bb4230b7fafd37fea/docs/en/AD5X.md

## Required implementation
- Use native infinite-spool handling. No AI polling/switch loop, new plugin or MCP.
- Verify same stored color and material type; additionally check compatible material variant and calibrated profile. These extra compatibility checks are local requirements, not claimed firmware capabilities.
- Keep slicer tools T0/T1 distinct from physical IFS slots and backup candidates.
- COLOR assigns spool metadata. SET_EXTRUDER_SLOT records which spool is loaded; it does not configure backups.
- Exclude unavailable/empty or unverified backup candidates. No eligible backup means native pause/error recovery, not guessed substitution.
- Preserve existing job identity/accounting and latency; no required new LLM calls or rendering.

## Acceptance
Offline tests: compatible backup, different color, different material, incompatible variant/profile, empty backup, stale metadata, exhausted candidates, remapped active slot and duplicate events. Installed-mode acceptance belongs to printer specialist. Native selection order and installed firmware/screen behavior have not been verified. No forced runout or physical print authorized by this reference phase.

## Compatibility
AD5X-specific docs govern over generic Klipper recommendations. Preserve existing start/end, purge, checksum, mesh/Z and IFS authority. Review object-exclusion crash warning before adoption. Keep existing Orca Flatpak. Bambufy is optional and officially incompatible with the native screen; no installation in MVP.

## Status
Contract delivered; runtime fallback integration and physical acceptance remain OPEN in issue #2. Existing hardening remains paused until coordinator release. Notify/Apprise audit is deferred, existing Discord behavior unchanged.

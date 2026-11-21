# CalendarCat operational handoff integration

2026-11-21: normal private newsroom reports now pass through the reviewed date-only MasterCat consumer after source/inbox/briefing archive readback. Its receipt is archived privately under mastercat-calendar-consumption. No forecast inputs or publication gates are enabled.

Private engine: fb411d3b3a12e5725d151028b18c37711cbb14b9 (PR171; offline/research/browser/paired CI44845611004 all passed).

The dedicated calendar-handoff-verification workflow runs only when its file changes on main. It shares the existing newsroom concurrency group, reads real natural and Saturday-ET archive evidence, intentionally exits75 once after storing a private immutable failure receipt, and must be rerun as the same run attempt2. It will then attest the first failed attempt and exact input hashes before writing a private candidate acceptance. This is a controlled drill, not an unexpected provider outage. No auto-retry loop and no data replacement.

Gate count remains40/48 until the regular path, controlled recovery and private immutable receipts are independently checked. Official publication stays locked. US/JPX special-holiday coverage, numerical first-release vintages, other seven departments and model performance remain separate checks.

Rollback: revert the workflow integration; preserve all private append-only evidence.

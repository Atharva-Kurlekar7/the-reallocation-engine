# Gate decisions — 2026-07-27

Append-only. Each entry is a human either committing a scarce resource or declining to. Written by `tools/effort-reallocator/reallocate.py execute`.

## 2026-07-27T18:08:07-04:00 — refused / blocked — nothing committed

- **Tool:** `tools/effort-reallocator`
- **Resource:** application slots (my own time against an F-1/OPT clock)
- **Approver:** (none — refused)
- **Reason:** (none given)
- **Gate status:** BLOCKED
- **Expected gain:** 0.12075 (80% CI [0.11685, 0.12311])
- **Moves:**
  - 1 slot(s) ACME ANALYTICS LLC → MAPLEBEAR INC (stability 100.00%)
  - 1 slot(s) ACME ANALYTICS LLC → ROKU INC (stability 99.95%)
  - 1 slot(s) LINKEDIN CORP → HUMAN INC (stability 20.70%)
  - 1 slot(s) LINKEDIN CORP → PINTEREST INC (stability 70.70%)
  - 1 slot(s) ETSY INC → ROBLOX CORP (stability 70.25%)
  - 1 slot(s) AIRBNB INC → TELADOC HEALTH INC (stability 18.45%)
  - 1 slot(s) DOCUSIGN INC → TWILIO INC (stability 72.55%)
  - 1 slot(s) ZOOX INC → VISICON TECHNOLOGIES INC (stability 5.20%)
- **Blocked by:**
  - `GATE_BLOCKING_UNWAIVED` DATASET_NO_RECORD_PROVENANCE — resolver: a named human waives each code with a written reason (--waive CODE --waiver-reason "..."), or the dataset is fixed
  - `POSTING_NOT_VERIFIED` DOCUSIGN INC — resolver: a human opens the careers page and confirms a live, current posting for a matching title
  - `POSTING_NOT_VERIFIED` HUMAN INC — resolver: a human opens the careers page and confirms a live, current posting for a matching title
  - `POSTING_NOT_VERIFIED` PINTEREST INC — resolver: a human opens the careers page and confirms a live, current posting for a matching title
  - `POSTING_NOT_VERIFIED` TELADOC HEALTH INC — resolver: a human opens the careers page and confirms a live, current posting for a matching title
  - `POSTING_NOT_VERIFIED` ZOOX INC — resolver: a human opens the careers page and confirms a live, current posting for a matching title
  - `POSTING_NOT_VERIFIED` VISICON TECHNOLOGIES INC — resolver: a human opens the careers page and confirms a live, current posting for a matching title
  - `MOVE_NOT_STABLE` LINKEDIN CORP -> HUMAN INC (stability 20.70% < 70.00%) — resolver: the human decides whether to move anyway, on grounds the engine does not have — a referral, a conversation, a deadline
  - `MOVE_NOT_STABLE` AIRBNB INC -> TELADOC HEALTH INC (stability 18.45% < 70.00%) — resolver: the human decides whether to move anyway, on grounds the engine does not have — a referral, a conversation, a deadline
  - `MOVE_NOT_STABLE` ZOOX INC -> VISICON TECHNOLOGIES INC (stability 5.20% < 70.00%) — resolver: the human decides whether to move anyway, on grounds the engine does not have — a referral, a conversation, a deadline
- **Flags carried:**
  - `SKIP_RATE_BELOW_TARGET` 31.5% < 50.0%

## 2026-07-27T18:08:09-04:00 — commit slots

- **Tool:** `tools/effort-reallocator`
- **Resource:** application slots (my own time against an F-1/OPT clock)
- **Approver:** Atharva Kurlekar
- **Reason:** Opened every destination board by hand on 2026-07-27 and confirmed a live matching requisition; accepting the snapshot-vintage waiver for one week of planning; planned for 11 slots so no sub-floor move is proposed.
- **Gate status:** PASS-WITH-WAIVER
- **Expected gain:** 0.18379 (80% CI [0.18543, 0.2032])
- **Moves:**
  - 1 slot(s) ACME ANALYTICS LLC → MAPLEBEAR INC (stability 100.00%)
  - 1 slot(s) ACME ANALYTICS LLC → ROKU INC (stability 100.00%)
  - 1 slot(s) DOCUSIGN INC → ROBLOX CORP (stability 100.00%)
  - 1 slot(s) DOCUSIGN INC → TWILIO INC (stability 100.00%)
  - 1 slot(s) ZOOX INC → MOLOCO INC (stability 98.00%)
  - 1 slot(s) ZOOX INC → NEXTDOOR INC (stability 99.85%)
  - 1 slot(s) LINKEDIN CORP → REDDIT INC (stability 97.60%)
  - 1 slot(s) LINKEDIN CORP → FIGMA INC (stability 90.40%)
  - 1 slot(s) ETSY INC → PELOTON INTERACTIVE INC (stability 86.05%)
- **Flags carried:**
  - `SKIP_RATE_BELOW_TARGET` 0.0% < 50.0%


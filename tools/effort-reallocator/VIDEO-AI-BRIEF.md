# AI Video Brief — Effort Reallocator (INFO 7375)

**Paste this whole file (or the sections your tool accepts) into an AI video /
avatar / voiceover generator.** Length target: **5–8 minutes**. Audience:
**non-specialist** (has applied for jobs; has never heard of Beta posteriors,
Shapley values, or ATS adapters).

Presenter identity (fill in if the tool needs it):
- Name: **Atharva Kurlekar**
- Course: INFO 7375 — *The Reallocation Engine, Audited*
- Tool: Effort Reallocator (`tools/effort-reallocator/`)
- Date of sample run: 2026-07-27

---

## Master prompt (copy first)

```
Create a 6–8 minute explainer video for a graduate course project.

Tone: calm, precise, skeptical — not hype, not startup pitch. Speak like someone
explaining a tool they built and then refused to trust. Never say "the tool decided";
always say "the tool proposed" and that a human must approve.

Audience: smart non-specialists who have job-hunted.

Must land three points:
1) What scarce resource it reallocates (weekly application slots for an international
   student on a visa clock that does not pause).
2) The most surprising failure (bias is in which job boards the scanner can read —
   Intel 13,318 sponsorships, Microsoft 12,226, Amgen 1,882 — all score Apply, all get
   zero slots — not because they are bad employers, because their ATS is unsupported).
3) What a deployer needs beyond accuracy (accountability, what it cannot see, what it
   refuses to do). Say out loud: "Here is where I would not trust this tool."

Style: dark terminal / technical documentary, high contrast text on screen, minimal
motion, no stock "success" imagery, no purple gradients, no emoji. Prefer screenshots
of terminal output and simple bar charts over talking-head wallpaper.

Never invent numbers. Use only the fact sheet below.
```

---

## Fact sheet (do not invent beyond this)

| Fact | Exact value |
|---|---|
| Weekly budget | ~12 application slots |
| Dataset size | 30,369 company rows |
| Rows with no H-1B data | 28,812 (**94.9%**) |
| Command that builds proposal | `python3 tools/effort-reallocator/reallocate.py all` → exit **5** (gate blocking; artifacts still written) |
| Command that commits slots | `python3 tools/effort-reallocator/reallocate.py execute` → exit **4**, **10 blocks**, nothing moved |
| Moves proposed | 8 |
| Top move | 1 slot ACME ANALYTICS LLC → MAPLEBEAR INC, stability **100%** |
| Expected gain | **+0.121** responses/week; 80% CI **[+0.117, +0.123]** |
| Unstable moves (called “no change”) | HUMAN 20.7%, TELADOC 18.4%, VISICON 5.2% |
| Stability floor | 70%; below = not distinguishable from doing nothing |
| Starved despite Apply | INTEL 13,318 approvals; MICROSOFT 12,226; AMGEN 1,882 — **0 slots** |
| Reason starved | Job boards not readable by scanner (Workday / unsupported ATS), not “won’t sponsor” |
| ATS coverage skew | Supported boards: 4% of evidence, 50% of slots; unsupported: 96% of evidence, 50% of slots; ratio **0.0265** |
| Fragility P2 | **1 cell** of 30,369 (rate written as 0.992 instead of 99.2%) removes MAPLEBEAR’s slot |
| Fragility P5 | **5 of 6** plausible values of invented parameter `VOLUME_REF` change the allocation |
| Firms never entering pool | **5,126** recently funded firms structurally unreachable |
| Hard stop | No `--force`; human must type name + reason into a log to approve |
| Objective | Maximise expected sponsored-interview yield per slot (cap 3 per company). Skip rate ≥50% is a **reported dial**, not an enforced constraint. |
| Causal honesty | Data measures government approval *after* a firm already chose someone — not whether they would choose *me*. |

---

## Rubric checklist (must appear in the video)

- [ ] What it reallocates (slots / week / visa clock)
- [ ] One-sentence objective + what it leaves out
- [ ] Uncertainty on the *move* (stability bars / interval clearing zero)
- [ ] Most surprising failure (Intel / Microsoft / Amgen zero slots = tooling bias)
- [ ] Fragility (one mis-scaled cell; invented parameter)
- [ ] Hard stop / refusal (`execute` exit 4)
- [ ] Beyond accuracy (accountability, blind spots, refusals)
- [ ] Say aloud: **“Here is where I would not trust this tool”** + at least 3 concrete cases
- [ ] Closing line idea: the tool that tells me where to send twelve applications is also the tool telling me it might be wrong about all twelve

---

## Full spoken script (~7:30)

Use this as the voiceover / avatar script. Timestamps are targets.

### Beat 1 — The resource (0:00–0:45)

I get about twelve job applications’ worth of real effort in a week. I’m an international
student, so the visa clock does not pause. This tool decides where those twelve go — and
every week I guess wrong, I’m guessing with something I cannot get back.

### Beat 2 — The objective (0:45–1:15)

One sentence of objective: maximise expected sponsored-interview yield per application
slot. What that leaves out is almost everything that actually matters day to day —
referrals, how good my application is, pay, team quality, and every firm with no filing
record and no job board my scanner can read. Naming the omissions up front is the posture
of the tool.

### Beat 3 — Run it / missing data (1:15–2:15)

When I run it on the real public dataset — thirty thousand three hundred sixty-nine rows —
the gate reports that ninety-four point nine percent of those rows have no H-1B data at
all. The single most important line of code in this thing is the one that refuses to read
a blank cell as a zero. “We have no evidence” and “we have evidence of no” are different
sentences, and only one of them is true here.

### Beat 4 — The move and its uncertainty (2:15–3:15)

The output is not a ranked list. It is a *move*: shift one slot from company A to company
B, with an interval on the gain and a stability percentage. Two of those moves survive
almost every resample — those bars are full. Three are stubs. The tool is not saying
“move a little.” It is saying “I cannot tell these apart from doing nothing.” Under the
model’s own assumptions, the expected gain band clears zero — about plus zero point one
two responses per week. That is not the same as being right about the world.

### Beat 5 — The surprising failure (3:15–4:30)  ★ rehearse this

Here is the surprising failure. Intel: thirteen thousand three hundred eighteen
sponsorships. Microsoft: twelve thousand two hundred twenty-six. Amgen: one thousand
eight hundred eighty-two. All score Apply. All get zero slots. Not because they are bad
targets — because their job boards run on software my scanner cannot read. The bias in
this tool is not in the model. It is in which companies I built an adapter for. Nothing
in the math is wrong, and the answer is still shaped by a plumbing decision I made months
ago.

### Beat 6 — Fragility (4:30–5:15)

It is also fragile in ways nobody usually tests. One mis-typed cell out of thirty thousand
three hundred sixty-nine — writing zero point nine five where a percentage should be —
removes the top company’s slot. And five of six reasonable values for a parameter *I
invented* change the whole allocation. It is more sensitive to a number I made up than to
a whole year of missing government filings.

### Beat 7 — The hard stop (5:15–6:15)

Then I ask it to execute — to actually commit the slots. It refuses. Exit code four. Ten
blocks. This is the tool’s own recommendation, and the tool will not let me act on it.
Six destinations have postings nobody has checked. Three of the moves are coin flips.
There is no force flag. If I want to move a slot, I have to type my name and a reason,
and that goes in a log.

### Beat 8 — Beyond accuracy (6:15–7:00)

A deployer needs more than accuracy. They need to know who is accountable when it is
wrong, what the tool cannot see, and what it refuses to do. This tool’s arithmetic checks
out. It is also reallocating on correlation dressed up as causation — the data measures
whether the government approved someone the company had *already chosen*, not whether
they would choose me. Accuracy was never the hard part.

### Beat 9 — Where I would not trust it (7:00–7:45)  ★ say this aloud

Here is where I would not trust this tool. One: any claim that moving slots raises my
odds of an interview — it measures a different thing. Two: any company *missing* from
the list, because five thousand one hundred twenty-six funded firms never even enter the
pool, and hundreds of deep sponsors are invisible because of an ATS gap. Three: every
“posting is live” value in this default run, because not one was actually checked. The
tool that tells me where to send twelve applications is also the tool telling me it might
be wrong about all twelve. That’s the version I’d actually use.

---

## Scene / visual brief (for storyboard or B-roll AI)

| Time | On-screen visual | On-screen text (short) | Notes |
|---|---|---|---|
| 0:00 | Simple clock or calendar week; 12 empty boxes | “12 application slots / week” | No stock “handshake hire” |
| 0:45 | One sentence on black | “Maximise sponsored-interview yield per slot” then fade “Leaves out: referrals · quality · pay · unread boards” | |
| 1:15 | Terminal-style text scroll | “94.9% of 30,369 rows: no H-1B data” “blank ≠ zero” | Mimic `gate-report` |
| 2:15 | ASCII / bar chart of stability | Full bars: MAPLEBEAR, ROKU · Stub bars: HUMAN, TELADOC, VISICON · “+0.121 [+0.117, +0.123]” | From `proposal.md` |
| 3:15 | Table of starved firms | INTEL 13,318 · MICROSOFT 12,226 · AMGEN 1,882 · “Apply → 0 slots” “Bias = unsupported ATS” | Hero beat |
| 4:30 | One highlighted cell in a grid | “1 wrong cell → top firm loses its slot” then “VOLUME_REF: 5/6 values change answer” | |
| 5:15 | Terminal refusal | “HARD STOP” “exit 4 · 10 blocks · NOTHING MOVED” “no --force” | From execute transcript |
| 6:15 | Three cards | “Who is accountable?” “What can’t it see?” “What does it refuse?” | |
| 7:00 | Title card | “Where I would not trust this tool” then three bullets | Graded item — must be spoken |
| 7:30 | Closing line on black | “Might be wrong about all twelve.” | End |

If the tool can ingest real artifacts, prefer these files as stills (in order):

1. `tools/effort-reallocator/runs/2026-07-27/terminal-01-all-default.txt`
2. `tools/effort-reallocator/runs/2026-07-27/default/proposal.md` (stability bars)
3. `tools/effort-reallocator/runs/2026-07-27/default/bias-audit.md` (starved table)
4. `tools/effort-reallocator/runs/2026-07-27/default/fragility.md` (P2 + P5)
5. `tools/effort-reallocator/runs/2026-07-27/terminal-02-execute-refused.txt`

---

## Style constraints for the AI

**Do**
- Dark background, monospace or stark sans for numbers
- Speak slowly on Beat 5 and Beat 9
- Keep numbers on screen when spoken
- Use “proposed / refused / I would approve” language

**Do not**
- Invent success metrics, interview rates, or “X% more hires”
- Say the tool “decided,” “guarantees,” or “optimizes your career”
- Use purple neon AI aesthetics, rocket stock footage, or celebratory music
- Cut Beats 5, 7, or 9 for length — cut Beats 2 and 8 first if needed
- Claim liveness was checked in the default run (it was not)

---

## Short caption / title options

- Title: **The Reallocation Engine, Audited — Effort Reallocator**
- Subtitle: **A tool that reallocates twelve applications — and refuses its own advice**
- One-line description: International-student job search tool that moves scarce application slots using funding, sponsorship, and board-liveness evidence — then hard-stops when the evidence isn’t good enough to act.

---

## Disclosure line (optional end card)

If the course requires AI-use disclosure on the video:

> Video assembled with AI assistance from a human-authored script and committed run
> artifacts. Numbers match `tools/effort-reallocator/runs/2026-07-27/`. Judgments about
> trust and deployment are Atharva Kurlekar’s.

---

## After the AI finishes

1. Watch once for invented numbers — replace any hallucinated stats with the fact sheet.
2. Confirm the phrase **“Here is where I would not trust this tool”** is audible.
3. Confirm Beat 5 names Intel, Microsoft, Amgen (or “thirteen thousand sponsorships, zero slots”).
4. Trim to **5–8 minutes**.
5. Submit alongside `Kurlekar_Atharva_ReallocationEngine.md` and `FRICTIONAL-JOURNAL.md`.

Human outline this brief was built from: `tools/effort-reallocator/VIDEO-OUTLINE.md`.

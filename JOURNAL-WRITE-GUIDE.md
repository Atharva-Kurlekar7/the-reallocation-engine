# Write the journal prediction + reflection — in your own words

**Worth +10 on the grade.** The hostile grader deducts −10 if Entry 1 is blank or
AI-written, and another −10 if the reflection judgments are blank. The tool is done;
this file is the remaining human half.

**Where to write:** open [`FRICTIONAL-JOURNAL.md`](FRICTIONAL-JOURNAL.md) and replace every
`**[FILL IN]**` with your answers. Do **not** edit Entry 1’s timestamp
(`2026-07-27 14:54 EDT`) — it must stay as the pre-build marker.

**Rule:** an AI-written prediction measures nothing about *your* calibration. Paste
prompts into a chat if you want help thinking, but the sentences that land in
`FRICTIONAL-JOURNAL.md` must be yours.

---

## Before you start

1. Read §4 of `FRICTIONAL-JOURNAL.md` (the factual log) — already filled from the sample run.
2. Skim `Kurlekar_Atharva_ReallocationEngine.md` §§ “headline finding”, Check 5, and
   “Where I would not trust this tool” if you need the story fresh.
3. Write Entry 1 first (prediction), then Entry 2 §§1–3 and 5 (reflection).  
   Entry 1 is *as if* before the build: what you expected, not what you now know. If you
   never wrote a real prediction before coding, be honest in the reflection that the
   Entry 1 answers are reconstructed — and still make them specific enough to be wrong.

---

## Entry 1 — Prediction (three answers + one number)

Paste into `FRICTIONAL-JOURNAL.md` under Entry 1. A few sentences each is enough.

### 1. Hardest failure you expected

Prompt: *What did you expect to go wrong most stubbornly — data, math, allocation, or your
own reasoning? Be specific enough that reality can prove you wrong.*

Starter shapes (pick one direction and make it yours — do not copy verbatim):

- “I thought the sponsorship signal would look strongest where n is too small…”
- “I thought missing H-1B would get treated as zero and poison the ranks…”
- “I thought the composite would be fine and the allocation would be the fragile part…”

### 2. Causal validity you expected

Prompt: *Did you expect an interventional engine, or correlation dressed as a decision?
Which confounder did you think mattered most? Which piece, if any, did you think survives
Pearl’s Rung 2?*

Starter shapes:

- “I expected correlation only; the biggest confounder I feared was ___.”
- “I thought liveness was the only thing that might be truly causal because ___.”

### 3. Confidence number

- One integer **0–100**.
- One line: what that number is a claim about (trust in the math? trust that you’d
  actually apply there? trust that yield would rise?).

Example form (replace with your number and claim):

```
**Confidence: 35 / 100**

**What that number claims:** how likely I would have been to spend a real week of
applications on the tool’s top move without opening the boards myself.
```

Delete the Entry 1 blockquote that says `[FILL IN — in your own words…]` when you’re done.

---

## Entry 2 — Reflection (write after reading §4)

Set **Timestamp (immediately after the build)** to today’s date/time when you finish writing.

### 1. What actually happened

Use §4 as evidence. Cover at least:

- Top move (ACME → MAPLEBEAR, 1 slot, ~100% stable).
- Gain interval (~[+0.117, +0.123]).
- That `execute` refused the default recommendation (hard stop).
- The one finding you’d put in a single sentence (blind spot / ATS bias / fragility / etc.).

### 2. Where your prediction was wrong

Name the gap Entry 1 → reality. Both directions count.

Check against §4:

| If you predicted… | What actually dominated |
|---|---|
| Thin records / small-n | Pool filter selecting on the outcome — 5,126 funded firms never enter |
| Noisy filing counts | One mis-scaled cell in 30,369; `VOLUME_REF` (5 of 6 values change the allocation) |
| Bias in model weights | ATS coverage — Intel/Microsoft/Amgen score Apply, get zero slots |
| The engine always has an answer | It refused its own recommendation (exit 4) |

### 3. What that says about your calibration

Was the confidence number too high or too low? Do you over-trust arithmetic, or over-trust
your own skepticism?

Useful test from §4: the math was often *correct* when the output was *meaningless*
(alphabetical slots at `VOLUME_REF=100`; identical Shapley φ for firms 10× apart in
approvals). If your confidence was “will the arithmetic work?”, you answered the wrong
question.

### 5. One sentence for the next person

Not a summary of the build — the warning that would have saved you the most time.

Delete the Entry 2 scaffolding blockquote when you’re done. **Leave §4 alone** — it is the
factual log for graders to cross-check.

---

## Done checklist

- [ ] Entry 1 §§1–3 filled in your words; confidence number set; blockquote removed
- [ ] Entry 1 timestamp untouched (`2026-07-27 14:54 EDT`)
- [ ] Entry 2 timestamp filled
- [ ] Entry 2 §§1, 2, 3, 5 filled; blockquote removed
- [ ] §4 unchanged
- [ ] Commit `FRICTIONAL-JOURNAL.md` when finished

When this is done, the next +10 is the video (`tools/effort-reallocator/VIDEO-OUTLINE.md`).

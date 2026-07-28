# Video explainer — 5–8 minutes

Audience: **a non-specialist.** Someone who has applied for jobs but has never heard of a
Beta posterior, a Shapley value, or an ATS. Assume nothing; explain the visa clock in one
sentence and move on.

Three things the video must land, per the rubric: **what it reallocates**, **the most
surprising failure**, and **what a deployer needs beyond accuracy**. Say "here is where I
would not trust this tool" **out loud** — that is a graded item.

Everything below is on screen already. Have these open in order and let the terminal do the
talking; do not read the report aloud.

| # | Beat | Time | On screen | Say this |
|---|---|---|---|---|
| 1 | The resource | 0:00–0:45 | *nothing / you* | "I get about twelve job applications' worth of real effort a week, and I'm an international student, so the clock does not pause. This tool decides where those twelve go — and every week I guess, I'm guessing with something I can't get back." |
| 2 | The one-sentence objective | 0:45–1:15 | `README.md` top | Objective: maximise expected sponsored-interview yield per slot. Then immediately: what it leaves out — referrals, my own application quality, pay, and every firm with no filing record. Naming the omissions up front is the whole posture of the tool. |
| 3 | Run it | 1:15–2:15 | `reallocate.py all` live, or `terminal-01-all-default.txt` | Let the gate scroll. Land on **94.9% of 30,369 rows have no H-1B data**, and: "the single most important line of code in this thing is the one that refuses to read a blank cell as a zero. 'We have no evidence' and 'we have evidence of no' are different sentences, and only one of them is true here." |
| 4 | The move, with its uncertainty | 2:15–3:15 | `proposal.md` — the stability bars | Point at the picture, not the numbers. Two bars are full: those moves survive resampling. Three are stubs: "the tool is telling me it cannot distinguish these from doing nothing. It is not saying 'move a little' — it is saying 'I don't know'." Then the gain interval with the `0` marker: the band clears zero, under the model's own assumptions. |
| 5 | **The surprising failure** | 3:15–4:30 | `bias-audit.md`, starved table | This is the beat that matters. **Intel: 13,318 sponsorships. Microsoft: 12,226. Amgen: 1,882. All score "Apply". All get zero slots.** Not because they are bad targets — because their job boards run on software my scanner cannot read. "The bias in this tool is not in the model. It is in which companies I built an adapter for. Nothing in the math is wrong, and the answer is still shaped by a plumbing decision I made months ago." |
| 6 | The fragility nobody tests | 4:30–5:15 | `fragility.md` P2 and P5 | One mis-typed cell out of 30,369 removes the top company's slot — and it is not a typo you'd catch, because `0.95` in a column of percentages looks like a perfectly normal number. Then P5: five of six reasonable values for a parameter *I invented* change the answer. "It is more sensitive to a number I made up than to a whole year of missing government filings." |
| 7 | The hard stop | 5:15–6:15 | `terminal-02-execute-refused.txt` | Run `execute` with no arguments. It refuses. Exit code 4, ten blocks. "This is the tool's own recommendation, and the tool will not let me act on it — six of these companies have postings nobody has checked, and three of the moves are coin flips. There is no `--force` flag. If I want to move a slot, I have to type my name and a reason, and that goes in a log." |
| 8 | Beyond accuracy | 6:15–7:00 | `execution-decision.json` or the delegation table | The closing argument: a deployer needs to know **who is accountable when it's wrong**, **what it cannot see**, and **what it refuses to do**. "This tool is accurate. Its arithmetic checks out to eight decimal places. It is also reallocating on correlation dressed up as causation — the data measures whether the government approved someone the company had *already chosen*, not whether they'd choose me. Accuracy was never the hard part." |
| 9 | **Where I would not trust it** — say it aloud | 7:00–7:45 | `Kurlekar_Atharva_ReallocationEngine.md` § *Where I would not trust this tool* | Pick three, out loud: (1) any claim that this raises my odds of an interview — it measures a different thing; (2) any company *missing* from the list, because 5,126 funded firms never even enter the pool; (3) every "posting is live" value in this run, because not one was actually checked. Close: "The tool that tells me where to send twelve applications is also the tool telling me it might be wrong about all twelve. That's the version I'd actually use." |

## Recording notes

- **Do not narrate code.** Screen time belongs to `terminal-01`, `proposal.md`'s stability
  bars, the starved-companies table, and the refusal. Four visuals, seven minutes.
- **Beat 5 is the one to rehearse.** "Intel, thirteen thousand sponsorships, zero slots,
  because of the software their job board runs on" is the line a non-specialist will
  remember, and it is the honest centre of the whole project.
- **Never say "the tool decided".** Say "the tool proposed and I approved", every time. That
  distinction is the assignment.
- If you run live, run `rm -rf tools/effort-reallocator/out` first so the artifacts are
  visibly written during the take. `all` takes ~30 seconds — start it, then talk over it.
- Total 7:45 leaves slack inside the 5–8 window. If you need to cut, compress beat 2 and
  beat 8; never cut 5, 7, or 9.

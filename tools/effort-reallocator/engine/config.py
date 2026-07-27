"""Every tunable number in the engine, with its provenance.

The rule (SNICKERDOODLE P3, Ch.11 "the cautionary mirror"): a parameter you cannot
trace is a parameter you cannot defend. Each entry below carries a source label:

  [Ch.11]     pinned by the book — changing it breaks parity with the manuscript
  [VERIFY]    the book does NOT pin this; the repo's own defect list says so
  [your-input] my judgment as the candidate — not a record, not a finding
  [derived]   a modeling choice made here, in this tool, for stated reasons

Parameters marked [VERIFY] or [your-input] are the ones the uncertainty and
fragility passes are pointed at. They are not settled facts and the tool never
reports them as such.
"""

# ── Ch.11 composite: votes, gates, thresholds ────────────────────────────────
WEIGHTS = {
    "sponsorship": 0.35,   # [Ch.11] stated explicitly
    "fit": 0.30,           # [Ch.11] stated explicitly
    "role_quality": 0.0,   # [VERIFY] "other weighted factors" — unpinned by Ch.11 and
                           #   by docs/search-profile-design.md (DOMAIN.md defect 3).
                           #   0.0 reproduces the book's worked example and means the
                           #   Ch.9 role-quality signal contributes NOTHING. Treated as
                           #   an uncertain parameter, not a settled one.
}
APPLY_THRESHOLD = 0.30     # [Ch.11] "a decision threshold near 0.3"
CONSIDER_FLOOR = 0.20      # [VERIFY] lower edge of the Consider band — not pinned
GATE_ZERO = 0.05           # [derived] a gate at/below this is closed -> Skip
SOFT_SPONSORSHIP_TIERS = ("likely", "possible", "unknown")  # [Ch.11] soft spot demotes Apply->Consider

# ── Sponsorship evidence model ───────────────────────────────────────────────
# Two different things live in the DOL data and must not be conflated:
#   (a) P(approval | the firm filed)  -- the Approval_Rate column
#   (b) whether the firm sponsors AT ALL, AT VOLUME -- the approvals count
# A firm with 2 approvals and 0 denials has a 100% approval rate and has sponsored
# twice. Reporting (a) alone as "P(sponsorship)" is the small-n trap, so the tool
# multiplies the Beta posterior mean by a volume factor.
BETA_PRIOR_ALPHA = 1.0     # [derived] Beta(approvals+1, denials+1) — uniform prior,
BETA_PRIOR_BETA = 1.0      #   deliberately weak so small n stays visibly uncertain
VOLUME_REF = 500.0         # [your-input] approvals at which volume evidence saturates.
                           #   LOAD-BEARING and arbitrary — the fragility pass sweeps it.
                           #   Started at 100 and raised after the first run: at 100 the
                           #   volume factor saturated for nearly every mid-size sponsor,
                           #   every p pinned to the 0.95 cap, and the allocation ended up
                           #   breaking ties ALPHABETICALLY. The tie report in the proposal
                           #   exists because of that run.
P_SPONSORSHIP_CAP = 0.95   # [derived] no filing record justifies P = 1.0
CI_LOW_Q = 0.10            # 80% credible interval (10th/90th percentile)
CI_HIGH_Q = 0.90
CI_DRAWS = 4000            # [derived] draws for the per-company interval
CI_SEED = 20260727         # fixed so intervals are reproducible

# Tier boundaries, in the vocabulary of Ch.7 (Proven / Likely / Possible / Unknown).
TIER_PROVEN_MIN_APPROVALS = 25    # [your-input]
TIER_PROVEN_MIN_RATE = 90.0       # [your-input] percent
TIER_LIKELY_MIN_APPROVALS = 5     # [your-input]
SMALL_N_APPROVALS = 25            # [derived] below this, the record is thin — used by
                                  #   the fairness pass as a protected-group boundary

# ── Fit (a model judgment, deterministic rubric — NOT an LLM call) ───────────
FIT_FLOOR = 0.30           # [your-input] a company that sponsors my titles at all
FIT_CEILING = 0.85         # [your-input] never claim a better read than a human screen
FIT_TITLE_HIT = 0.09       # [your-input] per matched target title, additive
FIT_SENIORITY_PENALTY = 0.10  # [your-input] all-senior title history, no entry rung
FIT_EXCLUDED_PENALTY = 0.08   # [your-input] history dominated by excluded titles (PhD/research)

# ── Liveness: a GATE (Ch.11), and the honest part is what we did NOT check ───
# This run performs no network calls. Liveness is therefore UNVERIFIED for every
# company. What differs between companies is whether it is even CHECKABLE: the
# repo's scanner supports greenhouse / lever / ashby only.
LIVENESS_POLICIES = ("neutral-flagged", "legacy-zero", "block")
LIVENESS_DEFAULT_POLICY = "neutral-flagged"
# neutral-flagged: unverifiable -> factor 1.0 + manual_verification_required.
#   The engine may still recommend the move; the HARD STOP refuses to execute it
#   until a human verifies a live posting. Missing evidence is not evidence of absence.
# legacy-zero: unverifiable -> factor 0.0. Reproduces the behaviour of the earlier
#   worked run, where AMGEN INC (1,882 approvals) scored 0.000 purely because its
#   board is Workday. Kept runnable so the bias can be measured, not just asserted.
# block: unverifiable -> excluded from allocation entirely, listed separately.
LIVENESS_VERIFIABLE_FACTOR = 1.0   # [derived] checkable-but-unchecked; carries a flag

# ── Allocation ───────────────────────────────────────────────────────────────
SLOTS_PER_WEEK = 12          # [your-input] Ch.15's 3-hour apply block, ~15 min/application
PER_COMPANY_CAP = 3          # [your-input] more than 3 open applications at one firm is noise
REPEAT_SLOT_DECAY = 0.5      # [your-input] value of the k-th slot at one company = value * decay^(k-1).
                             #   LOAD-BEARING: without decay every slot piles onto one company.
BASE_RESPONSE_RATE = 0.06    # [your-input] my own historical response rate per application.
                             #   Converts a unitless composite into an "expected responses"
                             #   number. If this is wrong, every yield figure scales with it.
MIN_SKIP_RATE = 0.50         # [Ch.15] "the target is a skip rate of at least fifty percent"

# ── Uncertainty ──────────────────────────────────────────────────────────────
MC_DRAWS = 2000              # [derived]
MC_SEED = 20260727
FIT_JITTER = 0.10            # [derived] +/- uniform jitter on fit: it is a judgment, not a record
ROLE_QUALITY_WEIGHT_MAX = 0.20  # [VERIFY] plausible upper end for the unpinned weight
MNAR_ALPHA = 1.0             # [derived] pessimistic Beta(1,4) for firms with NO filing record,
MNAR_BETA = 4.0              #   under the assumption that absence correlates with not sponsoring
MOVE_STABILITY_FLOOR = 0.70  # [derived] below this, a move is reported as
                             #   "not distinguishable from no change" and the hard stop blocks it
CANDIDATE_POOL_CAP = 80      # [derived] MC re-allocates over the top-N shortlist for speed

# ── GIGO gate ────────────────────────────────────────────────────────────────
FUNDING_STALE_YEARS = 3          # [your-input] a Form D older than this is not a liveness signal
RATE_ARITHMETIC_TOLERANCE = 0.5  # [derived] percentage points
EARLY_STAGES = ("Pre-Seed", "Seed", "Series A")  # [derived] stage-vs-volume implausibility check
IMPLAUSIBLE_STAGE_APPROVALS = 100  # [derived] early stage + this many approvals = mislabel

# ── Paths, relative to the repository root ───────────────────────────────────
DEFAULT_CSV = "data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv"
DEFAULT_BLS = "data/BLS/compact/soc_occupation_compact.csv"
DEFAULT_PORTALS = "data/examples/erp-to-ai-portals.yml"
GATE_DECISIONS_DIR = "logs/gate-decisions"

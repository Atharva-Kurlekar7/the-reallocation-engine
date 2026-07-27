"""Small shared helpers: paths, provenance labels, number formatting, IO.

Standard library only. The tool must run from a clean clone with no install step,
because a validation tool nobody can run is not a validation tool.
"""

import json
import os
import re

# Provenance labels, from Ch.11's audit trace. Every number the tool emits carries one.
RECORD = "record"                  # a government/company filing, quoted as-is
DERIVED = "derived"                # arithmetic over records, plus a stated parameter
MODEL = "model-judgment"           # a judgment (here: a deterministic rubric, not an LLM)
INPUT = "your-input"               # my own assumption about my own situation

_SUFFIXES = (
    "inc", "incorporated", "corp", "corporation", "llc", "lp", "llp", "ltd",
    "limited", "co", "company", "plc", "holdings", "holding", "group", "trust",
    "technologies", "technology", "labs", "the",
)


def repo_root():
    """The repository root, found by walking up from this file."""
    here = os.path.abspath(os.path.dirname(__file__))
    for _ in range(6):
        if os.path.isdir(os.path.join(here, ".git")) or os.path.isfile(
            os.path.join(here, "SNICKERDOODLE.md")
        ):
            return here
        here = os.path.dirname(here)
    # Fall back to two levels above tools/effort-reallocator/engine/
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def tool_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def resolve(path):
    """Resolve a path that may be relative to the repo root."""
    if os.path.isabs(path):
        return path
    direct = os.path.abspath(path)
    if os.path.exists(direct):
        return direct
    return os.path.join(repo_root(), path)


def normalize_company(name):
    """Uppercase, strip punctuation and corporate suffixes.

    Used for joining datasets that spell the same firm differently. This is a
    heuristic and the gate reports where it collides, because a wrong join
    silently merges two companies' evidence.
    """
    if not name:
        return ""
    s = re.sub(r"[^A-Za-z0-9 ]", " ", str(name)).lower()
    tokens = [t for t in s.split() if t]
    while tokens and tokens[-1] in _SUFFIXES:
        tokens.pop()
    while tokens and tokens[0] in _SUFFIXES:
        tokens.pop(0)
    return " ".join(tokens).upper()


def to_float(value):
    """Parse a CSV cell to float, or None. Empty string is None, never 0.0.

    This one-line distinction is the whole GIGO gate in miniature: ~95% of rows
    have no H-1B fields, and reading those as zero would report "this company does
    not sponsor" on the strength of a blank cell.
    """
    if value is None:
        return None
    s = str(value).strip()
    if s == "" or s.lower() in ("na", "n/a", "null", "none", "nan"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_titles(cell):
    """The top_job_titles_sponsored column holds a Python-ish list literal."""
    if not cell:
        return []
    s = str(cell).strip()
    if not s:
        return []
    parts = re.findall(r"'([^']*)'|\"([^\"]*)\"", s)
    titles = [(a or b).strip() for a, b in parts]
    if not titles:
        titles = [t.strip(" []'\"") for t in s.split(",")]
    return [t for t in titles if t]


def quantile(sorted_values, q):
    """Linear-interpolated quantile of an already-sorted list."""
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    idx = q * (len(sorted_values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = idx - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def fmt(x, places=3):
    if x is None:
        return "—"
    return f"{float(x):.{places}f}"


def pct(x, places=1):
    if x is None:
        return "—"
    return f"{100.0 * float(x):.{places}f}%"


def money(x):
    if x is None:
        return "—"
    x = float(x)
    if x >= 1e9:
        return f"${x / 1e9:.2f}B"
    if x >= 1e6:
        return f"${x / 1e6:.1f}M"
    return f"${x:,.0f}"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def write_json(path, obj):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=False)
        f.write("\n")
    return path


def read_json(path):
    with open(resolve(path), encoding="utf-8") as f:
        return json.load(f)


def write_text(path, text):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def rel(path):
    try:
        return os.path.relpath(path, repo_root())
    except ValueError:
        return path


def bar(value, width=28, vmax=1.0):
    """A text bar. Used so the Markdown reports carry a visual, not just digits."""
    if value is None:
        return " " * width
    n = int(round(max(0.0, min(1.0, value / vmax)) * width))
    return "#" * n + "-" * (width - n)


def interval_bar(low, high, point, width=30, vmin=None, vmax=None):
    """An ASCII interval: the point estimate inside its 80% band.

    Uncertainty communication is a graded component, and a point estimate printed
    alone is the thing the rubric is warning about.

    The axis auto-scales around the interval and always includes zero, because for a
    reallocation the only question a reader needs answered from the picture is whether
    the band clears zero. A fixed 0-vmax axis rendered a genuinely narrow interval as a
    single character, which hid the one comparison the chart exists to make.
    """
    vals = [v for v in (low, high, point) if v is not None]
    if not vals:
        return " " * width
    lo_axis = vmin if vmin is not None else min(0.0, min(vals))
    hi_axis = vmax if vmax is not None else max(0.0, max(vals))
    pad = (hi_axis - lo_axis) * 0.12 or 0.01
    lo_axis, hi_axis = lo_axis - pad, hi_axis + pad
    if hi_axis <= lo_axis:
        return " " * width

    def pos(v):
        frac = (v - lo_axis) / (hi_axis - lo_axis)
        return max(0, min(width - 1, int(round(frac * (width - 1)))))

    cells = ["."] * width
    cells[pos(0.0)] = "0"          # the reference a reader actually cares about
    if low is not None and high is not None:
        for i in range(pos(low), pos(high) + 1):
            cells[i] = "="
        cells[pos(low)] = "["
        cells[pos(high)] = "]"
    if point is not None:
        cells[pos(point)] = "|"
    return "".join(cells)


def axis_label(low, high, point):
    """The numeric axis that goes with `interval_bar`, so the picture is readable."""
    vals = [v for v in (low, high, point) if v is not None]
    if not vals:
        return ""
    lo_axis, hi_axis = min(0.0, min(vals)), max(0.0, max(vals))
    pad = (hi_axis - lo_axis) * 0.12 or 0.01
    return f"axis {lo_axis - pad:+.3f} to {hi_axis + pad:+.3f}"

"""The Effort Reallocator engine.

A reallocation engine for a scarce resource that is not money: the ~12 job
applications one week of Chapter 15's apply block actually buys. Every module
here is standard library only and every number it emits carries a provenance
label (record / derived / model-judgment / your-input).

Module map, in pipeline order:

  config      every tunable number, with its source and whether the book pins it
  util        paths, provenance labels, formatting, ASCII interval bars
  gigo        the data gate — runs BEFORE anything is allowed to reallocate
  evidence    CSV -> per-company evidence with Beta posteriors and gate factors
  composite   the Ch.11 arithmetic: (sum vote*weight) x liveness x timeline
  allocate    slots -> an explicit move (Q slots from A to B)
  uncertainty Monte Carlo over the parameters the book does not pin
  explain     exact Shapley by enumeration + counterfactual flip distance
  fairness    who this engine starves, with two metrics that disagree
  adversarial where the recommendation breaks, and how little it takes
  hardstop    nothing moves without a named human and a written reason
"""

__version__ = "0.1.0"

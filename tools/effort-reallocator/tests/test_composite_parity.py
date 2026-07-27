"""The composite is a reimplementation. These tests are why that is defensible.

`scripts/score/role-scorer.mjs` is the repo's Node implementation of the Chapter 11
scorer. This tool reimplements it in Python so the whole engine runs with no install.
A reimplementation nobody checked is a second source of truth, which is worse than
none — so:

  * test_parity_with_repo_scorer   feeds the same committed fixture to this code and
                                   compares against the Node scorer's committed output
  * test_chapter_11_worked_example verifies the book's own numbers (0.4463 / 0.1785)
  * test_gate_is_multiplicative    verifies a closed gate zeroes strong votes
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine import composite, config, util  # noqa: E402

REPO = util.repo_root()
FIXTURE_ROLES = os.path.join(REPO, "data", "examples", "erp-to-ai-roles.json")
FIXTURE_SCORES = os.path.join(REPO, "data", "examples", "role-scores.json")
CH11_ROLES = os.path.join(REPO, "data", "examples", "ch11-roles.json")


class TestParity(unittest.TestCase):
    def test_parity_with_repo_scorer(self):
        """Same input, same output as the Node scorer — to 4 decimal places."""
        roles = util.read_json(FIXTURE_ROLES)
        expected = util.read_json(FIXTURE_SCORES)
        self.assertEqual(expected["config"]["weights"]["sponsorship"],
                         config.WEIGHTS["sponsorship"],
                         "weights drifted from the committed Node config")
        self.assertEqual(expected["config"]["apply_threshold"], config.APPLY_THRESHOLD)

        by_id = {r["role_id"]: r for r in expected["roles"]}
        self.assertEqual(len(roles), len(by_id))
        for role in roles:
            got = composite.score_role(role, needs_sponsor=expected["profile_needs_sponsorship"])
            want = by_id[role["role_id"]]
            with self.subTest(role=role["role_id"]):
                self.assertAlmostEqual(got["composite"], want["composite"], places=4)
                self.assertEqual(got["recommendation"], want["recommendation"])
                self.assertEqual(got["machine_recommendation"], want["machine_recommendation"])
                self.assertAlmostEqual(got["trace"]["vote_sum"], want["trace"]["vote_sum"],
                                       places=4)
                self.assertAlmostEqual(got["trace"]["gate_product"],
                                       want["trace"]["gate_product"], places=4)

    def test_chapter_11_worked_example(self):
        """Ch.11: same candidate, same fit — sponsorship decides. 0.446 vs 0.178.

        The exact arithmetic is checked too, because the published figures are the
        rounded ones: (0.9x0.35 + 0.7x0.30) x 1.0 x 0.85 = 0.44625, and the identical
        candidate at a non-sponsor gets (0.0x0.35 + 0.7x0.30) x 1.0 x 0.85 = 0.1785.
        """
        roles = {r["role_id"]: r for r in util.read_json(CH11_ROLES)}
        biotech = composite.score_role(roles["biotech-data"])
        nonsponsor = composite.score_role(roles["household-nonsponsor"])

        # DOMAIN.md quotes these as 0.446 and 0.178 — the same values, truncated by
        # the Node scorer's toFixed(). The exact arithmetic is the assertion that means
        # something; the display rounding is not a property worth pinning.
        self.assertAlmostEqual(biotech["composite_exact"], 0.44625, places=8)
        self.assertEqual(biotech["recommendation"], "Apply")
        self.assertAlmostEqual(nonsponsor["composite_exact"], 0.1785, places=8)
        self.assertEqual(nonsponsor["recommendation"], "Skip")
        self.assertGreater(biotech["composite"], nonsponsor["composite"])

    def test_gate_is_multiplicative_not_additive(self):
        """A ghost posting zeroes a strong role. The gate is not a vote."""
        roles = {r["role_id"]: r for r in util.read_json(CH11_ROLES)}
        ghost = composite.score_role(roles["ghost-posting"])
        self.assertEqual(ghost["composite"], 0.0)
        self.assertEqual(ghost["recommendation"], "Skip")
        self.assertIn("gated", ghost["reason"])
        self.assertGreater(ghost["trace"]["vote_sum"], config.APPLY_THRESHOLD,
                           "the votes should be strong — that is the point of the case")

    def test_soft_tier_demotes_apply_to_consider(self):
        roles = {r["role_id"]: r for r in util.read_json(CH11_ROLES)}
        soft = composite.score_role(roles["likely-soft"])
        self.assertGreaterEqual(soft["composite"], config.APPLY_THRESHOLD)
        self.assertEqual(soft["recommendation"], "Consider")

    def test_override_requires_a_documented_reason(self):
        roles = {r["role_id"]: r for r in util.read_json(CH11_ROLES)}
        ov = composite.score_role(roles["override-demo"])
        self.assertEqual(ov["machine_recommendation"], "Skip")
        self.assertEqual(ov["recommendation"], "Apply", "a reasoned override should hold")

        stripped = dict(roles["override-demo"])
        stripped["override"] = {"decision": "Apply", "reason": "   "}
        bare = composite.score_role(stripped)
        self.assertEqual(bare["recommendation"], "Skip",
                         "an override with no reason is ignoring the math, not overriding it")
        self.assertIn("_warning", bare["override"])

    def test_no_sponsorship_need_zeroes_that_weight(self):
        w, needs = composite.apply_profile(config.WEIGHTS,
                                           {"authorization": "US citizen"})
        self.assertFalse(needs)
        self.assertEqual(w["sponsorship"], 0.0)
        w2, needs2 = composite.apply_profile(config.WEIGHTS,
                                             {"authorization": "F-1 student, requires H-1B sponsorship"})
        self.assertTrue(needs2)
        self.assertEqual(w2["sponsorship"], 0.35)


if __name__ == "__main__":
    unittest.main()

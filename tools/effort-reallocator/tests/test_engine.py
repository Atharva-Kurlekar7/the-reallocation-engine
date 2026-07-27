"""Golden tests for the behaviours that would be silently wrong.

Each test here corresponds to a claim the report makes. If a test fails, a claim in
the report is false — that is the point of writing them.
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine import allocate, composite, config, evidence, explain, gigo, hardstop, util  # noqa: E402
from engine import uncertainty  # noqa: E402

PROFILE = util.read_json(os.path.join(util.tool_root(), "examples", "profile.json"))


class TestMissingIsNotZero(unittest.TestCase):
    """The single most important behaviour in the tool."""

    def test_blank_h1b_fields_yield_unknown_not_zero(self):
        rng = random.Random(1)
        s = evidence.sponsorship_evidence(None, None, rng)
        self.assertIsNone(s["p"], "a blank cell must not become a number")
        self.assertEqual(s["tier"], "unknown")
        self.assertNotEqual(s["tier"], "none")

    def test_zero_approvals_is_different_from_missing(self):
        rng = random.Random(1)
        missing = evidence.sponsorship_evidence(None, None, rng)
        actual_zero = evidence.sponsorship_evidence(0.0, 4.0, rng)
        self.assertIsNone(missing["p"])
        self.assertIsNotNone(actual_zero["p"],
                             "a recorded zero IS evidence and must be scored")
        self.assertEqual(actual_zero["tier"], "none")

    def test_withheld_vote_does_not_contribute(self):
        comp, vote_sum, _ = composite.composite_from_terms(
            {"sponsorship": None, "fit": 0.6, "role_quality": None},
            {"liveness": 1.0, "timeline": 1.0}, config.WEIGHTS)
        self.assertAlmostEqual(vote_sum, 0.6 * 0.30, places=6)

    def test_to_float_never_turns_blank_into_zero(self):
        for blank in ("", "  ", "NA", "n/a", None, "null"):
            self.assertIsNone(util.to_float(blank))
        self.assertEqual(util.to_float("0"), 0.0)


class TestSponsorshipEvidence(unittest.TestCase):
    def test_small_n_gets_a_wider_interval_than_large_n(self):
        rng = random.Random(config.CI_SEED)
        thin = evidence.sponsorship_evidence(2.0, 0.0, rng)
        deep = evidence.sponsorship_evidence(4962.0, 28.0, rng)
        thin_w = thin["ci80"][1] - thin["ci80"][0]
        deep_w = deep["ci80"][1] - deep["ci80"][0]
        self.assertGreater(thin_w, deep_w)
        self.assertLess(thin["p"], deep["p"],
                        "a 100% rate over 2 filings must not outrank 99% over 4,962")

    def test_perfect_rate_never_reaches_certainty(self):
        rng = random.Random(config.CI_SEED)
        s = evidence.sponsorship_evidence(10000.0, 0.0, rng)
        self.assertLessEqual(s["p"], config.P_SPONSORSHIP_CAP)
        self.assertLess(s["p"], 1.0, "no filing record justifies P = 1.0")

    def test_tiers_follow_the_documented_boundaries(self):
        rng = random.Random(config.CI_SEED)
        self.assertEqual(evidence.sponsorship_evidence(100.0, 1.0, rng)["tier"], "proven")
        self.assertEqual(evidence.sponsorship_evidence(6.0, 0.0, rng)["tier"], "likely")
        self.assertEqual(evidence.sponsorship_evidence(2.0, 0.0, rng)["tier"], "possible")
        self.assertEqual(evidence.sponsorship_evidence(0.0, 2.0, rng)["tier"], "none")

    def test_volume_factor_discounts_thin_records(self):
        self.assertEqual(evidence.volume_factor(None), 0.0)
        self.assertLess(evidence.volume_factor(2), evidence.volume_factor(200))
        self.assertEqual(evidence.volume_factor(10 ** 6), 1.0)


class TestLivenessPolicies(unittest.TestCase):
    def test_unverifiable_is_flagged_not_zeroed_by_default(self):
        live = evidence.liveness_evidence(None, "neutral-flagged")
        self.assertEqual(live["factor"], 1.0)
        self.assertTrue(live["manual_verification_required"])

    def test_legacy_zero_reproduces_the_amgen_skip(self):
        live = evidence.liveness_evidence(None, "legacy-zero")
        self.assertEqual(live["factor"], 0.0)
        comp, _, _ = composite.composite_from_terms(
            {"sponsorship": 0.95, "fit": 0.6, "role_quality": None},
            {"liveness": live["factor"], "timeline": 0.85}, config.WEIGHTS)
        self.assertEqual(comp, 0.0, "a strong sponsor is zeroed purely by its ATS provider")

    def test_supported_provider_is_marked_unchecked_not_verified(self):
        live = evidence.liveness_evidence({"enabled": True, "provider": "greenhouse"},
                                          "neutral-flagged")
        self.assertEqual(live["status"], "checkable-but-unchecked")
        self.assertFalse(live["manual_verification_required"])


class TestGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gate = gigo.run_gate(util.resolve(config.DEFAULT_CSV))

    def test_gate_blocks_on_absent_record_provenance(self):
        self.assertEqual(self.gate["status"], "BLOCKED")
        self.assertIn("DATASET_NO_RECORD_PROVENANCE", self.gate["blocking_unwaived"])

    def test_a_waiver_clears_the_block_and_is_recorded(self):
        g = gigo.run_gate(util.resolve(config.DEFAULT_CSV),
                          waivers=["DATASET_NO_RECORD_PROVENANCE"],
                          waiver_reason="accepted for one week of planning")
        self.assertEqual(g["blocking_unwaived"], [])
        self.assertEqual(g["status"], "PASS-WITH-WAIVER")
        self.assertEqual(g["waivers"][0]["reason"], "accepted for one week of planning")

    def test_the_gate_actually_rejects_rows(self):
        self.assertGreater(self.gate["reject_total"], 0,
                           "a gate that rejects nothing has not been tested against data")
        self.assertIn("IDENTITY_AMBIGUOUS", self.gate["reject_counts"])

    def test_known_artifacts_are_found(self):
        self.assertGreater(self.gate["checks"]["WAGE_IN_TITLE"]["count"], 0)
        self.assertGreater(self.gate["checks"]["ENTITY_COLLISION"]["count"], 0)
        self.assertGreater(self.gate["checks"]["FUNDING_STAGE_IMPLAUSIBLE"]["count"], 0)
        self.assertGreater(self.gate["h1b_missing_rate"], 0.9)


class TestAllocation(unittest.TestCase):
    def setUp(self):
        rng = random.Random(config.CI_SEED)

        def cand(name, approvals, fit, live=1.0, mvr=False):
            c = {
                "company_name": name, "normalized": name,
                "industry": "", "state": "", "titles_sponsored": [],
                "total_funding": None, "latest_funding_stage": "", "latest_funding_date": "",
                "sponsorship": evidence.sponsorship_evidence(approvals, 1.0, rng),
                "fit": {"p": fit, "source": util.MODEL},
                "role_quality": {"p": None, "source": util.RECORD},
                "liveness": {"factor": live, "source": util.DERIVED, "status": "x",
                             "manual_verification_required": mvr},
                "timeline": {"factor": 0.85, "source": util.INPUT},
                "ats": {"supported_provider": True, "provider": "greenhouse",
                        "portal_name": name, "in_portals_config": True},
                "flags": [], "manual_verification_required": mvr,
            }
            return composite.score_candidate(c)

        self.cands = [cand("STRONG", 900.0, 0.8), cand("MID", 400.0, 0.6),
                      cand("WEAK", 200.0, 0.45), cand("GHOST", 900.0, 0.8, live=0.0)]
        self.baseline = {"week_of": "x", "allocations": [
            {"company_name": "WEAK", "slots": 4}]}

    def test_per_company_cap_is_respected(self):
        p = allocate.propose(self.cands, self.baseline, PROFILE, slots=12, cap=3, decay=0.5)
        for row in p["target"]["rows"]:
            self.assertLessEqual(row["slots"], 3)

    def test_a_gated_company_never_receives_a_slot(self):
        p = allocate.propose(self.cands, self.baseline, PROFILE, slots=12, cap=3, decay=0.5)
        self.assertNotIn("GHOST", [r["normalized"] for r in p["target"]["rows"]])

    def test_output_is_a_move_not_a_ranking(self):
        p = allocate.propose(self.cands, self.baseline, PROFILE, slots=4, cap=3, decay=0.5)
        self.assertTrue(p["moves"], "a reallocation must name what to stop doing")
        m = p["moves"][0]
        for key in ("quantity", "from", "to", "from_why", "to_why"):
            self.assertIn(key, m)
        self.assertGreater(m["quantity"], 0)

    def test_decay_spreads_slots_across_companies(self):
        flat = allocate.propose(self.cands, self.baseline, PROFILE, slots=6, cap=6, decay=1.0)
        steep = allocate.propose(self.cands, self.baseline, PROFILE, slots=6, cap=6, decay=0.1)
        self.assertLessEqual(len(flat["target"]["rows"]), len(steep["target"]["rows"]))

    def test_skip_is_a_legitimate_outcome(self):
        weak_only = [c for c in self.cands if c["normalized"] == "GHOST"]
        p = allocate.propose(weak_only, self.baseline, PROFILE, slots=12, cap=3, decay=0.5)
        self.assertEqual(p["target"]["total_slots"], 0)
        self.assertEqual(p["target"]["unspent_slots"], 12)

    def test_unscored_baseline_company_is_labelled_not_scored_zero(self):
        baseline = {"week_of": "x", "allocations": [
            {"company_name": "NOT IN DATA CO", "slots": 3}]}
        p = allocate.propose(self.cands, baseline, PROFILE, slots=6, cap=3, decay=0.5)
        row = p["baseline"]["rows"][0]
        self.assertEqual(row["status"], "not in the evidence set")
        self.assertIsNone(row["composite"])


class TestUncertainty(unittest.TestCase):
    def test_same_seed_same_answer(self):
        rng = random.Random(config.CI_SEED)
        cands = []
        for name, appr, fit in (("A", 900.0, 0.8), ("B", 300.0, 0.6), ("C", 150.0, 0.5)):
            c = {"company_name": name, "normalized": name, "industry": "", "state": "",
                 "titles_sponsored": [], "total_funding": None,
                 "latest_funding_stage": "", "latest_funding_date": "",
                 "sponsorship": evidence.sponsorship_evidence(appr, 1.0, rng),
                 "fit": {"p": fit, "source": util.MODEL},
                 "role_quality": {"p": None, "source": util.RECORD},
                 "liveness": {"factor": 1.0, "source": util.DERIVED, "status": "x"},
                 "timeline": {"factor": 0.85, "source": util.INPUT},
                 "ats": {"supported_provider": True, "provider": "greenhouse",
                         "portal_name": name, "in_portals_config": True},
                 "flags": [], "manual_verification_required": False}
            cands.append(composite.score_candidate(c))
        baseline = {"week_of": "x", "allocations": [{"company_name": "C", "slots": 3}]}
        prop = allocate.propose(cands, baseline, PROFILE, slots=6, cap=3, decay=0.5)
        a = uncertainty.analyze(cands, baseline, PROFILE, prop, 6, 3, 0.5, draws=120, seed=7)
        b = uncertainty.analyze(cands, baseline, PROFILE, prop, 6, 3, 0.5, draws=120, seed=7)
        self.assertEqual(a["expected_gain"]["ci80"], b["expected_gain"]["ci80"])
        self.assertEqual([m["stability"] for m in a["moves"]],
                         [m["stability"] for m in b["moves"]])

    def test_both_missingness_scenarios_are_sampled(self):
        rng = random.Random(config.CI_SEED)
        c = {"company_name": "A", "normalized": "A", "industry": "", "state": "",
             "titles_sponsored": [], "total_funding": None, "latest_funding_stage": "",
             "latest_funding_date": "",
             "sponsorship": evidence.sponsorship_evidence(500.0, 5.0, rng),
             "fit": {"p": 0.7, "source": util.MODEL},
             "role_quality": {"p": None, "source": util.RECORD},
             "liveness": {"factor": 1.0, "source": util.DERIVED, "status": "x"},
             "timeline": {"factor": 0.85, "source": util.INPUT},
             "ats": {"supported_provider": True, "provider": "greenhouse",
                     "portal_name": "A", "in_portals_config": True},
             "flags": [], "manual_verification_required": False}
        cands = [composite.score_candidate(c)]
        baseline = {"week_of": "x", "allocations": []}
        prop = allocate.propose(cands, baseline, PROFILE, slots=3, cap=3, decay=0.5)
        u = uncertainty.analyze(cands, baseline, PROFILE, prop, 3, 3, 0.5, draws=200, seed=3)
        self.assertGreater(u["scenario_counts"]["MCAR"], 0)
        self.assertGreater(u["scenario_counts"]["MNAR"], 0)
        self.assertIn("optimizers_curse", u)


class TestShapley(unittest.TestCase):
    def test_additivity_is_exact(self):
        actual = {"sponsorship": 0.9, "fit": 0.7, "role_quality": 0.5,
                  "liveness": 1.0, "timeline": 0.85}
        reference = {"sponsorship": 0.5, "fit": 0.5, "role_quality": 0.5,
                     "liveness": 1.0, "timeline": 1.0}
        weights = {"sponsorship": 0.35, "fit": 0.30, "role_quality": 0.10}
        phi, v_empty, v_full, coalitions = explain.shapley(actual, reference, weights)
        self.assertEqual(coalitions, 32, "all 2^5 coalitions must be evaluated")
        self.assertAlmostEqual(sum(phi.values()), v_full - v_empty, places=12)

    def test_zero_weight_feature_gets_zero_credit(self):
        actual = {"sponsorship": 0.9, "fit": 0.7, "role_quality": 0.9,
                  "liveness": 1.0, "timeline": 0.85}
        reference = {"sponsorship": 0.5, "fit": 0.5, "role_quality": 0.1,
                     "liveness": 1.0, "timeline": 1.0}
        phi, _, _, _ = explain.shapley(actual, reference, config.WEIGHTS)
        self.assertAlmostEqual(phi["role_quality"], 0.0, places=12,
                               msg="role_quality weight is 0.0, so it cannot contribute")

    def test_gated_role_explains_as_a_gate_not_a_weak_role(self):
        actual = {"sponsorship": 0.95, "fit": 0.8, "role_quality": 0.0,
                  "liveness": 0.0, "timeline": 0.85}
        reference = {"sponsorship": 0.5, "fit": 0.5, "role_quality": 0.0,
                     "liveness": 1.0, "timeline": 1.0}
        phi, _, v_full, _ = explain.shapley(actual, reference, config.WEIGHTS)
        self.assertEqual(v_full, 0.0)
        self.assertLess(phi["liveness"], 0.0)
        self.assertGreater(abs(phi["liveness"]), abs(phi["fit"]))


class TestHardStop(unittest.TestCase):
    def test_unwaived_gate_blocks(self):
        v = hardstop.evaluate({"moves": [], "manual_verification_required": []},
                              {"blocking_unwaived": ["DATASET_NO_RECORD_PROVENANCE"]})
        self.assertEqual(v["decision"], "block")
        self.assertEqual(v["blocks"][0]["code"], "GATE_BLOCKING_UNWAIVED")

    def test_unverified_posting_blocks(self):
        v = hardstop.evaluate({"moves": [], "manual_verification_required": ["AMGEN INC"]},
                              {"blocking_unwaived": []})
        self.assertEqual(v["decision"], "block")
        self.assertEqual(v["blocks"][0]["code"], "POSTING_NOT_VERIFIED")

    def test_unstable_move_blocks(self):
        v = hardstop.evaluate(
            {"moves": [{"from": "A", "to": "B", "quantity": 1, "stability": 0.4,
                        "stable": False}],
             "manual_verification_required": []},
            {"blocking_unwaived": []})
        self.assertEqual(v["decision"], "block")
        self.assertEqual(v["blocks"][0]["code"], "MOVE_NOT_STABLE")

    def test_sub_floor_stability_is_not_stable_even_when_rounding_would_pass(self):
        # The bug: round(0.6995, 3) == 0.700, which cleared a 70% floor. Strict
        # comparison must refuse; the hard stop must block.
        stability = 0.6995
        self.assertLess(stability, config.MOVE_STABILITY_FLOOR)
        self.assertFalse(stability >= config.MOVE_STABILITY_FLOOR,
                         "round() must not be used to decide the floor")
        self.assertEqual(round(stability, 3), 0.700,
                         "documenting why the old comparison was wrong")
        v = hardstop.evaluate(
            {"moves": [{"from": "AIRBNB INC", "to": "APPLOVIN CORP", "quantity": 1,
                        "stability": stability, "stable": False}],
             "manual_verification_required": []},
            {"blocking_unwaived": []})
        self.assertEqual(v["decision"], "block")
        self.assertEqual(v["blocks"][0]["code"], "MOVE_NOT_STABLE")
        # Fallback path when the stable flag is absent must also refuse.
        v2 = hardstop.evaluate(
            {"moves": [{"from": "AIRBNB INC", "to": "APPLOVIN CORP", "quantity": 1,
                        "stability": stability}],
             "manual_verification_required": []},
            {"blocking_unwaived": []})
        self.assertEqual(v2["decision"], "block")
        self.assertEqual(v2["blocks"][0]["code"], "MOVE_NOT_STABLE")

    def test_a_clean_proposal_is_approval_eligible_not_auto_approved(self):
        v = hardstop.evaluate(
            {"moves": [{"from": "A", "to": "B", "quantity": 1, "stability": 0.95,
                        "stable": True, "to_sponsorship_p": 0.9, "to_approvals": 900}],
             "manual_verification_required": [],
             "skip_rate": {"rate": 0.8}, "expected_gain": {"ci80": [0.1, 0.2]}},
            {"blocking_unwaived": []})
        self.assertEqual(v["decision"], "approve-eligible",
                         "eligible is not the same as executed — a human still has to sign")
        self.assertEqual(v["blocks"], [])

    def test_thin_record_destination_is_flagged(self):
        v = hardstop.evaluate(
            {"moves": [{"from": "A", "to": "B", "quantity": 1, "stability": 0.95,
                        "stable": True, "to_sponsorship_p": 0.6, "to_approvals": 3}],
             "manual_verification_required": []},
            {"blocking_unwaived": []})
        self.assertIn("THIN_SPONSORSHIP_RECORD", [f["code"] for f in v["flags"]])


if __name__ == "__main__":
    unittest.main()

"""Freshness on reused answers, and re-verification when a source changes.

The registry replays a SOURCED claim forever. These controls hold the two properties
that make that honest: every reused answer carries the age of the evidence it rests on,
and a source whose cited span has disappeared unsettles the claim and names every answer
that depended on it.

No network. The document cache is redirected to a temporary file and its contents are
written by the test, so every "source change" here is SYNTHETIC and is labelled as such.
"""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clearance import dictionary, instruments, recheck, refusal_log

URL = "https://example.org/spec"
# SYNTHETIC document bodies. Nothing here was fetched from the live web.
BODY_V1 = ("Specification, revision one. The retry budget is capped at three attempts "
           "per request. Unrelated boilerplate follows.")
SPAN = "The retry budget is capped at three attempts per request."
BODY_V2_SPAN_INTACT = ("Specification, revision two, reordered. Unrelated boilerplate "
                       "first. The retry budget is capped at three attempts per "
                       "request. And a new closing paragraph.")
BODY_V2_SPAN_GONE = ("Specification, revision two. The retry budget was removed in this "
                     "revision and is no longer specified.")
ASSERTION = "The specification caps the retry budget at three attempts per request."


class FreshnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = self.root / "refusal_log.db"
        self.env = patch.dict(os.environ, {"REFUSAL_LOG_DB": str(self.db)})
        self.env.start()
        self.cache = patch.object(instruments, "DOCS", self.root / "documents.json")
        self.cache.start()
        self.write_source(BODY_V1, fetched_at="2026-06-01T00:00:00+00:00")
        self.con = refusal_log.connect(self.db)

    def tearDown(self):
        self.con.close()
        self.cache.stop()
        self.env.stop()
        self.temp.cleanup()

    # --- helpers -----------------------------------------------------------
    def write_source(self, text, *, fetched_at="2026-09-01T00:00:00+00:00"):
        """Install a SYNTHETIC snapshot of the cited document."""
        instruments.DOCS.write_text(json.dumps(
            {URL: {"text": text, "fetched_at": fetched_at}}))

    def establish(self):
        """Save the claim the way the engine saves a verified one."""
        refusal_log.record(self.con, term="retry budget", assertion=ASSERTION,
                           verdict="GREEN", production="test", basis="primary",
                           citation_url=URL, quoted_terms=SPAN)

    def row(self):
        return self.con.execute(
            "SELECT * FROM claims WHERE slot=?",
            (refusal_log.claim_key(ASSERTION),)).fetchone()

    # --- controls ----------------------------------------------------------
    def test_a_saved_claim_records_the_snapshot_its_span_was_read_from(self):
        self.establish()
        row = self.row()
        self.assertEqual(row["source_fetched_at"], "2026-06-01T00:00:00+00:00")
        self.assertTrue(row["source_sha256"], "no content hash bound to the evidence")

    def test_a_reused_answer_carries_the_age_of_its_evidence(self):
        """A free replay must be distinguishable from a fresh read."""
        self.establish()
        result = dictionary.lookup(ASSERTION, db=self.db)
        self.assertEqual(result["label"], "SOURCED")
        self.assertEqual(result["cost_tier"], "free")
        fresh = result["freshness"]
        self.assertEqual(fresh["source_fetched_at"], "2026-06-01T00:00:00+00:00")
        self.assertGreater(fresh["evidence_age_days"], 90,
                           "evidence read in June is not reported as days old")
        self.assertEqual(result["evidence_age_days"], fresh["evidence_age_days"])

    def test_the_exact_replay_route_also_carries_the_evidence_age(self):
        """The cheapest route of all is the one most likely to hide staleness."""
        self.establish()
        dictionary.lookup(ASSERTION, db=self.db)          # first ask: registry
        replay = dictionary.lookup(ASSERTION, db=self.db)  # second ask: exact replay
        self.assertEqual(replay["source"], "dictionary_exact")
        self.assertEqual(replay["freshness"]["source_fetched_at"],
                         "2026-06-01T00:00:00+00:00")
        self.assertGreater(replay["evidence_age_days"], 90)

    def test_evidence_age_is_the_documents_age_not_the_rows_write_time(self):
        """`first_seen_at` is overwritten on every write; the age must not follow it."""
        self.establish()
        self.establish()  # rewrite the row today, same old snapshot
        fresh = refusal_log.freshness_of(self.row())
        self.assertEqual(fresh["source_fetched_at"], "2026-06-01T00:00:00+00:00")
        self.assertGreater(fresh["evidence_age_days"], 90,
                           "a row rewritten today reports its evidence as fresh")

    def test_a_claim_with_no_recorded_snapshot_reports_unknown_not_fresh(self):
        fresh = refusal_log.freshness_of({"source_fetched_at": None})
        self.assertIsNone(fresh["evidence_age_days"])
        self.assertIn("unknown", fresh["basis"])

    def test_an_unchanged_source_moves_nothing_and_stamps_the_check(self):
        self.establish()
        report = recheck.recheck(db=self.db)
        self.assertEqual(report["counts"][recheck.UNCHANGED], 1)
        self.assertEqual(self.row()["verdict"], "GREEN")
        self.assertTrue(self.row()["evidence_checked_at"])

    def test_a_changed_source_that_keeps_the_span_does_not_move_the_verdict(self):
        self.establish()
        before = self.row()["source_sha256"]
        self.write_source(BODY_V2_SPAN_INTACT)  # SYNTHETIC revision
        report = recheck.recheck(db=self.db)
        self.assertEqual(report["counts"][recheck.CHANGED_INTACT], 1)
        self.assertEqual(self.row()["verdict"], "GREEN",
                         "a reordered page unsettled a claim its own text still states")
        self.assertNotEqual(self.row()["source_sha256"], before,
                            "the claim is still bound to the superseded snapshot")

    def test_a_changed_source_that_loses_the_span_unsettles_the_claim(self):
        self.establish()
        self.write_source(BODY_V2_SPAN_GONE)  # SYNTHETIC revision
        report = recheck.recheck(db=self.db)
        self.assertEqual(report["counts"][recheck.CHANGED_ABSENT], 1)
        row = self.row()
        self.assertEqual(row["verdict"], "UNKNOWN")
        self.assertEqual(row["cause"], "source_does_not_state_it")
        self.assertEqual(row["refusal_code"], recheck.REFUSAL_CODE)
        self.assertFalse(
            refusal_log.is_settled_for_reuse(verdict=row["verdict"], cause=row["cause"]))

    def test_a_rebind_does_not_erase_how_the_claim_was_established(self):
        """Re-reading a document is not new knowledge about how the claim was found."""
        refusal_log.record(self.con, term="retry budget", assertion=ASSERTION,
                           verdict="GREEN", production="test", basis="primary",
                           citation_url=URL, quoted_terms=SPAN,
                           origins=["registry-of-specs"],
                           trail=[{"span": "a rejected span", "why": "wrong section"}])
        self.write_source(BODY_V2_SPAN_INTACT)  # SYNTHETIC revision, span intact
        recheck.recheck(db=self.db)
        row = self.row()
        self.assertTrue(refusal_log.trail_of(row),
                        "the locator trail was erased by a rebind")
        self.assertEqual(json.loads(row["origins"]), ["registry-of-specs"],
                         "the claim's origins were erased by a rebind")

    def test_the_refusal_cause_stays_inside_the_engines_closed_vocabulary(self):
        from clearance import verdict as V
        self.establish()
        self.write_source(BODY_V2_SPAN_GONE)
        recheck.recheck(db=self.db)
        self.assertIn(self.row()["cause"], V.CAUSES,
                      "recheck invented a cause the engine cannot prove")

    def test_the_previous_observation_survives_the_flip(self):
        self.establish()
        self.write_source(BODY_V2_SPAN_GONE)
        recheck.recheck(db=self.db)
        payloads = [json.loads(r["payload"]) for r in self.con.execute(
            "SELECT payload FROM claim_observations WHERE assertion=? ORDER BY id",
            (ASSERTION,))]
        self.assertIn("GREEN", [p.get("verdict") for p in payloads],
                      "the supporting observation was overwritten, not retained")

    def test_a_flipped_claim_names_every_answer_that_depended_on_the_source(self):
        self.establish()
        dictionary.lookup(ASSERTION, db=self.db)   # one logged answer on this URL
        dictionary.lookup("an unrelated question about nothing", db=self.db)
        self.write_source(BODY_V2_SPAN_GONE)
        report = recheck.recheck(db=self.db)
        finding = next(f for f in report["findings"]
                       if f["status"] == recheck.CHANGED_ABSENT)
        dep = finding["dependents"]
        self.assertEqual(dep["answers_on_this_url"], 1)
        self.assertEqual(dep["answers_total"], 2,
                         "the flagged count is printed without its denominator")
        self.assertEqual(report["answers_flagged"], 1)

    def test_a_source_that_cannot_be_read_is_unchecked_not_unchanged(self):
        self.establish()
        instruments.DOCS.write_text(json.dumps({}))  # snapshot no longer available
        report = recheck.recheck(db=self.db)
        self.assertEqual(report["counts"][recheck.UNCHECKED], 1)
        self.assertEqual(report["counts"][recheck.UNCHANGED], 0)
        self.assertEqual(self.row()["verdict"], "GREEN",
                         "a failed read moved a verdict")

    def test_the_registry_stops_replaying_a_claim_whose_span_disappeared(self):
        self.establish()
        self.assertEqual(dictionary.lookup(ASSERTION, db=self.db)["label"], "SOURCED")
        self.write_source(BODY_V2_SPAN_GONE)
        recheck.recheck(db=self.db)
        after = dictionary.lookup(ASSERTION, db=self.db)
        self.assertNotEqual(after["label"], "SOURCED",
                            "a claim whose evidence vanished is still served as sourced")
        self.assertEqual(after["cause"], "prior_claim_unsettled")
        self.assertEqual(after["prior"]["cause"], "source_does_not_state_it")
        self.assertIn("re-verify", after["resolves_with"])

    def test_a_related_question_retrieves_candidates_without_reusing_the_verdict(self):
        self.establish()
        result = dictionary.lookup(
            "What is the retry budget in the specification?", db=self.db)
        self.assertEqual(result["label"], "NOT_CLEARED",
                         "a different question was answered with another claim's verdict")
        self.assertTrue(result["candidates"],
                        "the registry holds a related claim and offered nothing")
        self.assertEqual(result["candidates"][0]["established"], ASSERTION)


if __name__ == "__main__":
    unittest.main()

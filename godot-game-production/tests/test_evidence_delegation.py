"""Structural acceptance fixtures, not evidence from a real Godot game."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_run as ledger
import visual_contract as visual


class DelegationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "project.godot").write_text("; synthetic test project\n")
        self.data = ledger._manifest_template(
            builder_id="builder", dimension="3d", procedural_mode="none")
        self.reviewer = "reviewer-independent"
        self.data["game"].update(godot_version="test", target_hardware="synthetic")
        decision = json.loads((ROOT / "tests/fixtures/visual-decision.json").read_text())
        plan = decision["reference_plan"]
        approval = {
            "schema_version": "visual-scope-approval/v1",
            "approval_artifact_id": "scope", "decision_id": decision["decision_id"],
            "reviewer_id": self.reviewer, "decision": "approved",
            "recorded_at": "2026-10-09T01:01:00Z",
            "decision_sha256": visual.canonical_sha256(decision),
            "plan_sha256": visual.canonical_plan_sha256(plan),
            "approved_slot_ids": [r["reference_slot_id"] for r in plan["rows"]],
        }
        authorization = visual.build_generation_authorization(
            decision, approval, authorization_id="auth-test",
            issued_at="2026-10-09T01:02:00Z")
        self.data["visual_decisions"] = [decision]
        self.data["visual_scope_approvals"] = [approval]
        self.data["visual_generation_authorizations"] = [authorization]
        self.data["reference_plans"] = [dict(copy.deepcopy(plan), approval=approval)]
        self.add_artifact("scope", "review_record", approval)
        contract = {"contract_id": "vc-test", "base_contract_id": None,
                    "plan_id": plan["plan_id"], "plan_revision": plan["revision"],
                    "targets": []}
        captures = []
        for i, slot in enumerate(plan["rows"]):
            target = self.add_artifact(
                f"target-{i}", "target_gameplay_image", {"synthetic_image": i},
                path=f"docs/visual-contract/vc-test/targets/{i}.json",
                target_id=f"target-{i}", reference_slot_id=slot["reference_slot_id"],
                coverage=slot["coverage"], generated_at="2026-10-09T01:03:00Z",
                plan_id=plan["plan_id"], plan_revision=plan["revision"],
                authorization_id="auth-test")
            contract["targets"].append({
                "reference_slot_id": slot["reference_slot_id"], "target_id": target["id"],
                "artifact_id": target["id"], "path": target["path"], "sha256": target["sha256"]})
            capture = self.add_artifact(f"capture-{i}", "canonical_godot_capture",
                                        {"synthetic_capture": i}, target_id=target["id"],
                                        approved_target_sha256=target["sha256"])
            captures.append(capture["id"])
        contract["approval"] = {
            "approval_artifact_id": "target-approval", "reviewer_id": self.reviewer,
            "decision": "approved", "recorded_at": "2026-10-09T01:04:00Z",
            "binding_sha256": visual.canonical_sha256(contract),
        }
        self.add_artifact("target-approval", "review_record", contract["approval"])
        self.data["visual_contract_versions"] = [contract]
        self.data["active_visual_contract_id"] = "vc-test"
        for facet in ledger.FACETS:
            ids = list(captures) if facet == "visual" else []
            if facet != "visual":
                for choice in sorted(ledger.REQUIRED_KINDS[facet]):
                    kind = choice.split("|")[0]
                    artifact_id = f"{facet}-{kind}"
                    extras = {"coverage": ["action", "danger", "success", "failure", "ambience"]} if kind == "runtime_audio_video" else {}
                    self.add_artifact(artifact_id, kind, {"synthetic": artifact_id}, **extras)
                    ids.append(artifact_id)
                    if kind == "release_build":
                        self.data["game"]["build_artifact_id"] = artifact_id
            review = {"id": f"review-{facet}", "facet": facet,
                      "review_artifact_id": f"record-{facet}", "reviewer_id": self.reviewer,
                      "role": "user" if facet == "visual" else "cold_player" if facet == "ux_onboarding" else "independent_reviewer",
                      "artifact_ids_reviewed": ids, "verdict": "accept",
                      "rationale": "Synthetic structural fixture only."}
            self.add_artifact(review["review_artifact_id"], "review_record", review)
            self.data["reviews"].append(review)
            self.data["facets"][facet] = {"intent": "SUBMITTED", "evidence_ids": ids,
                                          "review_ids": [review["id"]]}

    def add_artifact(self, artifact_id, kind, content, *, path=None, **extras):
        row = {"id": artifact_id, "kind": kind,
               "provenance": "user_instruction" if kind == "visual_review_delegation" else sorted(ledger.KIND_PROVENANCES[kind])[0],
               "path": path or f"evidence/{artifact_id}.json", "sha256": "0" * 64,
               "media_type": "application/json", **extras}
        self.data["artifacts"].append(row)
        self.write_artifact(row, content)
        return row

    def write_artifact(self, row, content):
        raw = json.dumps(content, sort_keys=True).encode()
        path = self.root / row["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        row["sha256"] = hashlib.sha256(raw).hexdigest()

    def review(self, facet="visual"):
        return next(r for r in self.data["reviews"] if r["facet"] == facet)

    def grant(self, **changes):
        active = next(row for row in self.data["visual_contract_versions"]
                      if row["contract_id"] == self.data["active_visual_contract_id"])
        record = {"schema_version": "visual-review-delegation/v1",
                  "run_id": self.data["run_id"], "contract_id": active["contract_id"],
                  "contract_sha256": visual.canonical_sha256([
                      {k: v for k, v in contract.items() if k != "approval"}
                      for contract in self.data["visual_contract_versions"]]),
                  "reviewer_id": self.reviewer, "grantor_role": "user",
                  "scope": "visual_review", "source_ref": "conversation:test/user:1",
                  "authorization_quote": "Approve references autonomously; keep independent review.",
                  "recorded_at": "2026-10-09T01:00:00Z", **changes}
        row = self.add_artifact("delegation", "visual_review_delegation", record)
        self.data["visual_review_delegations"] = [row["id"]]
        self.review()["role"] = "independent_reviewer"
        return row, record

    def append_delta(self):
        """Add one target while inheriting both original targets."""
        decision = copy.deepcopy(self.data["visual_decisions"][0])
        decision.update(
            decision_id="22222222-2222-2222-2222-222222222222", decision_kind="delta_scope",
            state="VISUAL_DELTA_PENDING", change_scope="local", blocked_work=["new room"],
            continuing_work=[], preserved_bindings=[{k: t[k] for k in ("target_id", "path", "sha256")}
                for t in self.data["visual_contract_versions"][0]["targets"]],
            affected_targets=[{"target_id": "target-new", "change_kind": "add", "dependent_work": ["new room"]}],
            target_approval_scope="complete_delta_batch_only")
        plan = decision["reference_plan"]
        plan.update(plan_id="vrp-002", kind="delta", base_contract_id="vc-test",
                    rows=[copy.deepcopy(plan["rows"][0])])
        plan["rows"][0].update(reference_slot_id="REF-03", change_kind="add")
        approval = copy.deepcopy(self.data["visual_scope_approvals"][0])
        approval.update(approval_artifact_id="scope2", decision_id=decision["decision_id"],
                        decision_sha256=visual.canonical_sha256(decision),
                        plan_sha256=visual.canonical_plan_sha256(plan), approved_slot_ids=["REF-03"])
        auth = visual.build_generation_authorization(
            decision, approval, authorization_id="auth-delta", issued_at="2026-10-09T01:02:00Z")
        self.data["visual_decisions"].append(decision)
        self.data["visual_scope_approvals"].append(approval)
        self.data["visual_generation_authorizations"].append(auth)
        self.data["reference_plans"].append(dict(copy.deepcopy(plan), approval=approval))
        self.add_artifact("scope2", "review_record", approval)
        target = self.add_artifact(
            "target-new", "target_gameplay_image", {"synthetic_image": "delta"},
            path="docs/visual-contract/vc-delta/targets/new.json", target_id="target-new",
            reference_slot_id="REF-03", coverage=plan["rows"][0]["coverage"],
            generated_at="2026-10-09T01:03:00Z", plan_id=plan["plan_id"], plan_revision=1,
            authorization_id="auth-delta")
        contract = {"contract_id": "vc-delta", "base_contract_id": "vc-test",
                    "plan_id": plan["plan_id"], "plan_revision": 1,
                    "targets": [{k: target[k] for k in ("reference_slot_id", "target_id", "path", "sha256")}
                                | {"artifact_id": target["id"]}]}
        contract["approval"] = {
            "approval_artifact_id": "target-approval2", "reviewer_id": self.reviewer,
            "decision": "approved", "recorded_at": "2026-10-09T01:04:00Z",
            "binding_sha256": visual.canonical_sha256(contract)}
        self.add_artifact("target-approval2", "review_record", contract["approval"])
        self.data["visual_contract_versions"].append(contract)
        self.data["active_visual_contract_id"] = "vc-delta"
        self.add_artifact("capture-new", "canonical_godot_capture", {"synthetic_capture": "delta"},
                          target_id=target["id"], approved_target_sha256=target["sha256"])
        self.data["facets"]["visual"]["evidence_ids"].append("capture-new")

    def test_inherited_target_change_needs_new_delegation(self):
        self.append_delta()
        grant, record = self.grant()
        self.assertEqual("VERIFIED", self.evaluate()["overall"])
        base = self.data["visual_contract_versions"][0]
        target = base["targets"][0]
        artifact = next(row for row in self.data["artifacts"] if row["id"] == target["artifact_id"])
        self.write_artifact(artifact, {"synthetic_image": "changed inherited target"})
        target["sha256"] = artifact["sha256"]
        base["approval"]["binding_sha256"] = visual.canonical_sha256({k: v for k, v in base.items() if k != "approval"})
        self.write_artifact(next(row for row in self.data["artifacts"] if row["id"] == "target-approval"), base["approval"])
        next(row for row in self.data["artifacts"] if row["id"] == "capture-0")["approved_target_sha256"] = artifact["sha256"]
        self.assertEqual(grant["sha256"], hashlib.sha256((self.root / grant["path"]).read_bytes()).hexdigest())
        result = self.evaluate()
        self.assertEqual("FAILED", result["overall"])
        self.assertTrue(any("delegation contract binding drifted" in error for error in result["errors"]), result)

    def test_chain_binding_uses_ancestry_not_storage_order(self):
        self.append_delta()
        self.grant()
        self.data["visual_contract_versions"].reverse()
        self.assertEqual("VERIFIED", self.evaluate()["overall"])
        self.assertEqual(0, self.cli().returncode)

    def evaluate(self):
        return ledger._evaluate(self.root, ledger._validate_schema(self.data))

    def assert_not_verified(self):
        try:
            result = self.evaluate()
        except ledger.SchemaError:
            return
        self.assertNotEqual("VERIFIED", result["overall"], result)

    def cli(self):
        manifest = self.root / "evidence-run.json"
        manifest.write_text(json.dumps(self.data), encoding="utf-8")
        return subprocess.run([sys.executable, str(ROOT / "scripts/evidence_run.py"),
                               "validate", "--project-root", str(self.root),
                               "--manifest", str(manifest), "--report", str(self.root / "report.json"),
                               "--strict"], capture_output=True, text=True)

    def test_existing_user_review_remains_verified(self):
        self.assertEqual("VERIFIED", self.evaluate()["overall"])
        self.assertEqual(0, self.cli().returncode)

    def test_authorized_independent_visual_review_is_verified(self):
        self.grant()
        self.assertEqual("VERIFIED", self.evaluate()["overall"])
        self.assertEqual(0, self.cli().returncode)

    def test_empty_extension_preserves_old_behavior(self):
        self.data["visual_review_delegations"] = []
        self.assertEqual("VERIFIED", self.evaluate()["overall"])

    def test_independent_review_without_authorization_fails(self):
        self.review()["role"] = "independent_reviewer"
        self.assert_not_verified()
        self.assertEqual(2, self.cli().returncode)

    def test_wrong_authority_bindings_fail(self):
        for field, value in [("run_id", "other"), ("contract_id", "vc-other"),
                             ("contract_sha256", "a" * 64),
                             ("reviewer_id", "other"), ("grantor_role", "assistant"),
                             ("scope", "all"), ("source_ref", ""),
                             ("authorization_quote", ""), ("recorded_at", "yesterday")]:
            with self.subTest(field=field):
                self.setUp()
                self.grant(**{field: value})
                self.assert_not_verified()

    def test_builder_cannot_review_even_when_named(self):
        self.reviewer = "builder"
        self.review()["reviewer_id"] = "builder"
        self.grant()
        self.assert_not_verified()

    def test_hash_drift_missing_and_wrong_kind_fail(self):
        for mode in ("hash", "missing", "kind"):
            with self.subTest(mode=mode):
                self.setUp()
                row, record = self.grant()
                path = self.root / row["path"]
                if mode == "hash":
                    path.write_text("{}")
                elif mode == "missing":
                    path.unlink()
                else:
                    row.update(kind="review_record", provenance="review_record")
                self.assert_not_verified()

    def test_duplicate_or_orphan_grants_fail(self):
        for mode in ("duplicate", "orphan", "unused"):
            with self.subTest(mode=mode):
                self.setUp()
                self.grant()
                if mode == "duplicate":
                    self.data["visual_review_delegations"].append("delegation")
                elif mode == "orphan":
                    self.data["visual_review_delegations"] = []
                else:
                    self.review()["role"] = "user"
                self.assert_not_verified()

    def test_malformed_grant_fails(self):
        for content in ({}, [], "grant", None):
            with self.subTest(content=content):
                self.setUp()
                row, record = self.grant()
                self.write_artifact(row, content)
                self.assert_not_verified()

    def test_grant_does_not_relax_other_evidence_gates(self):
        for mode in ("coverage", "reject", "cold_role", "target_hash", "approval_reviewer"):
            with self.subTest(mode=mode):
                self.setUp()
                self.grant()
                if mode == "coverage":
                    self.review()["artifact_ids_reviewed"] = []
                elif mode == "reject":
                    self.review()["verdict"] = "reject"
                elif mode == "cold_role":
                    self.review("ux_onboarding")["role"] = "independent_reviewer"
                elif mode == "target_hash":
                    self.data["visual_contract_versions"][0]["targets"][0]["sha256"] = "f" * 64
                else:
                    self.data["visual_contract_versions"][0]["approval"]["reviewer_id"] = "other"
                self.assert_not_verified()


if __name__ == "__main__":
    unittest.main()

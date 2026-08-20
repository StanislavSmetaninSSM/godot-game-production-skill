"""Initialize and validate project-local Godot evidence ledgers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Sequence

import visual_contract


FACETS = (
    "core_play",
    "systems_holism",
    "content",
    "visual",
    "audio_feedback",
    "ux_onboarding",
    "reliability_performance",
    "ship",
)

KIND_PROVENANCES = {
    "target_gameplay_image": {"imagegen_target"},
    "rejected_target_image": {"imagegen_target"},
    "canonical_godot_capture": {"godot_runtime"},
    "input_trace": {"input_trace"},
    "state_transition_trace": {"state_trace"},
    "outcome_record": {"godot_runtime", "state_trace"},
    "runtime_filmstrip": {"godot_runtime"},
    "runtime_video": {"godot_runtime"},
    "runtime_session": {"godot_runtime"},
    "systems_trace": {"godot_runtime", "state_trace"},
    "complete_session": {"godot_runtime"},
    "content_analysis": {"godot_runtime", "review_record"},
    "runtime_audio_video": {"godot_runtime"},
    "first_session_capture": {"godot_runtime"},
    "target_session_capture": {"godot_runtime"},
    "target_hardware_report": {"environment_report"},
    "telemetry": {"godot_runtime", "environment_report"},
    "release_build": {"build_output"},
    "clean_install_record": {"godot_runtime", "environment_report"},
    "save_restart_capture": {"godot_runtime"},
    "review_record": {"review_record"},
    "procedural_grammar": {"review_record"},
    "procedural_population": {"review_record"},
    "procedural_output": {"godot_runtime"},
}
ARTIFACT_KINDS = set(KIND_PROVENANCES)
PROVENANCES = {
    "imagegen_target",
    "godot_runtime",
    "build_output",
    "input_trace",
    "state_trace",
    "review_record",
    "environment_report",
}
REQUIRED_KINDS = {
    "core_play": {
        "input_trace",
        "state_transition_trace",
        "outcome_record",
        "runtime_filmstrip|runtime_video",
    },
    "systems_holism": {"runtime_session", "systems_trace"},
    "content": {"complete_session", "content_analysis"},
    "visual": {"canonical_godot_capture"},
    "audio_feedback": {"runtime_audio_video"},
    "ux_onboarding": {"first_session_capture"},
    "reliability_performance": {
        "target_session_capture",
        "target_hardware_report",
        "telemetry",
    },
    "ship": {"release_build", "clean_install_record", "save_restart_capture"},
}
HEX = set("0123456789abcdef")
APPROVAL_FIELDS = {
    "approval_artifact_id", "reviewer_id", "decision", "recorded_at",
    "binding_sha256",
}
REJECTED_TARGET_FIELDS = {
    "id",
    "kind",
    "provenance",
    "path",
    "sha256",
    "media_type",
    "target_id",
    "reference_slot_id",
    "coverage",
    "generated_at",
    "plan_id",
    "plan_revision",
    "rejected_at",
    "rejection_artifact_id",
    "rejection_reviewer_id",
    "authorization_id",
}
VISUAL_CONTRACT_FIELDS = {
    "contract_id", "base_contract_id", "plan_id", "plan_revision",
    "targets", "approval",
}
VISUAL_TARGET_FIELDS = {
    "reference_slot_id", "target_id", "artifact_id", "sha256", "path"
}
TARGET_KINDS = {
    "location", "gameplay_state", "ui_mode", "character", "asset_family"
}


class SchemaError(ValueError):
    """The manifest cannot be interpreted safely."""


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evidence_run.py")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--project-root", required=True)
    init.add_argument("--manifest", required=True)
    init.add_argument("--builder-id", required=True)
    init.add_argument("--dimension", choices=("2d", "2.5d", "3d"), required=True)
    init.add_argument("--procedural-mode", choices=("none", "seeded"), required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--project-root", required=True)
    validate.add_argument("--manifest", required=True)
    validate.add_argument("--report", required=True)
    validate.add_argument(
        "--strict",
        action="store_true",
        help="compatibility flag; validation is always fail-closed",
    )
    return parser


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _manifest_template(
    *, builder_id: str, dimension: str, procedural_mode: str
) -> dict[str, object]:
    return {
        "schema_version": "evidence-run/v2",
        "run_id": str(uuid.uuid4()),
        "project_root": ".",
        "builder_id": builder_id,
        "game": {
            "godot_version": "",
            "dimension": dimension,
            "build_artifact_id": "",
            "target_hardware": "",
        },
        "artifacts": [],
        "reference_plans": [],
        "visual_decisions": [],
        "visual_scope_approvals": [],
        "visual_correction_approvals": [],
        "visual_generation_authorizations": [],
        "visual_contract_versions": [],
        "active_visual_contract_id": None,
        "facets": {
            name: {"intent": "PENDING", "evidence_ids": [], "review_ids": []}
            for name in FACETS
        },
        "reviews": [],
        "procedural_mode": procedural_mode,
        "procedural_none_reason": (
            "No procedural systems are declared for this evidence run."
            if procedural_mode == "none"
            else None
        ),
        "procedural_systems": [],
    }


def _atomic_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SchemaError(message)


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and set(value).issubset(HEX)
    )


def _require_text(value: object, label: str) -> None:
    _require(isinstance(value, str) and bool(value.strip()), f"{label} is empty")


def _validate_approval_schema(value: object, label: str) -> None:
    if value is None:
        return
    _require(
        isinstance(value, dict) and set(value) == APPROVAL_FIELDS,
        f"{label} fields differ",
    )
    for field in ("approval_artifact_id", "reviewer_id", "recorded_at"):
        _require_text(value[field], f"{label} {field}")
    _require(value["decision"] in {"approved", "rejected"}, f"{label} decision is unknown")
    _require(
        visual_contract.is_aware_timestamp(value["recorded_at"]),
        f"{label} recorded_at is not a timezone-aware ISO-8601 timestamp",
    )
    _require(
        _is_sha256(value["binding_sha256"]),
        f"{label} binding SHA-256 is malformed",
    )


def _validate_visual_contract_schema(value: object) -> None:
    _require(
        isinstance(value, dict) and set(value) == VISUAL_CONTRACT_FIELDS,
        "visual contract version fields differ",
    )
    for field in ("contract_id", "plan_id"):
        _require_text(value[field], f"visual contract {field}")
    _require(value["contract_id"].startswith("vc-"), "visual contract contract_id is malformed")
    _require(
        value["base_contract_id"] is None
        or (
            isinstance(value["base_contract_id"], str)
            and bool(value["base_contract_id"].strip())
        ),
        "visual contract base_contract_id is malformed",
    )
    _require(
        isinstance(value["plan_revision"], int)
        and not isinstance(value["plan_revision"], bool)
        and value["plan_revision"] > 0,
        "visual contract plan_revision is invalid",
    )
    _require(
        isinstance(value["targets"], list) and bool(value["targets"]),
        "visual contract targets are empty",
    )
    for target in value["targets"]:
        _require(
            isinstance(target, dict) and set(target) == VISUAL_TARGET_FIELDS,
            "visual target fields differ",
        )
        for field in ("reference_slot_id", "target_id", "artifact_id", "path"):
            _require_text(target[field], f"visual target {field}")
        _require(_is_sha256(target["sha256"]), "visual target SHA-256 is malformed")
    _validate_approval_schema(value["approval"], "target approval")


def _validate_schema(data: object) -> dict[str, object]:
    _require(isinstance(data, dict), "manifest must be an object")
    required = {
        "schema_version",
        "run_id",
        "project_root",
        "builder_id",
        "game",
        "artifacts",
        "reference_plans",
        "visual_decisions",
        "visual_scope_approvals",
        "visual_correction_approvals",
        "visual_generation_authorizations",
        "visual_contract_versions",
        "active_visual_contract_id",
        "facets",
        "reviews",
        "procedural_mode",
        "procedural_none_reason",
        "procedural_systems",
    }
    _require(set(data) == required, "top-level manifest fields differ")
    _require(data["schema_version"] == "evidence-run/v2", "wrong schema version")
    try:
        uuid.UUID(data["run_id"])
    except (AttributeError, TypeError, ValueError) as error:
        raise SchemaError("run_id is not a UUID") from error
    _require(data["project_root"] == ".", "project_root must be portable")
    _require(isinstance(data["builder_id"], str) and bool(data["builder_id"].strip()), "builder_id is empty")
    game = data["game"]
    _require(isinstance(game, dict), "game must be an object")
    _require(
        set(game) == {"godot_version", "dimension", "build_artifact_id", "target_hardware"},
        "game fields differ",
    )
    _require(game["dimension"] in {"2d", "2.5d", "3d"}, "unsupported dimension")
    for field in ("godot_version", "build_artifact_id", "target_hardware"):
        _require(isinstance(game[field], str), f"game.{field} must be text")

    artifacts = data["artifacts"]
    _require(isinstance(artifacts, list), "artifacts must be a list")
    artifact_required = {"id", "kind", "provenance", "path", "sha256", "media_type"}
    artifact_optional = {
        "target_id",
        "approved_target_sha256",
        "coverage",
        "reference_slot_id",
        "generated_at",
        "plan_id",
        "plan_revision",
        "rejected_at",
        "rejection_artifact_id",
        "rejection_reviewer_id",
        "authorization_id",
    }
    for row in artifacts:
        _require(isinstance(row, dict), "artifact must be an object")
        _require(artifact_required.issubset(row), "artifact fields are missing")
        _require(set(row).issubset(artifact_required | artifact_optional), "artifact fields are unknown")
        _require(isinstance(row["id"], str) and bool(row["id"].strip()), "artifact id is empty")
        _require(row["kind"] in ARTIFACT_KINDS, "artifact kind is unknown")
        _require(row["provenance"] in PROVENANCES, "artifact provenance is unknown")
        _require(isinstance(row["path"], str) and bool(row["path"]), "artifact path is empty")
        _require(_is_sha256(row["sha256"]), "artifact SHA-256 is malformed")
        _require(isinstance(row["media_type"], str) and bool(row["media_type"]), "media type is empty")
        if "approved_target_sha256" in row:
            _require(_is_sha256(row["approved_target_sha256"]), "approved target SHA-256 is malformed")
        if "coverage" in row:
            _require(
                isinstance(row["coverage"], list)
                and all(isinstance(item, str) and item for item in row["coverage"]),
                "artifact coverage is malformed",
            )
        if row["kind"] == "target_gameplay_image":
            _require(
                {"target_id", "reference_slot_id", "generated_at", "coverage", "plan_id", "plan_revision"}.issubset(row),
                "target image fields are missing",
            )
            _require_text(row["target_id"], "target image target_id")
            _require_text(row["reference_slot_id"], "target image reference_slot_id")
            _require_text(row.get("authorization_id"), "target image authorization_id")
            _require_text(row["plan_id"], "target image plan_id")
            _require(
                isinstance(row["plan_revision"], int)
                and not isinstance(row["plan_revision"], bool)
                and row["plan_revision"] > 0,
                "target image plan_revision must be a positive integer",
            )
            _require(
                visual_contract.is_aware_timestamp(row["generated_at"]),
                "target image generated_at is not a timezone-aware ISO-8601 timestamp",
            )
        if row["kind"] == "rejected_target_image":
            _require(
                set(row) == REJECTED_TARGET_FIELDS,
                "rejected target fields differ",
            )
            _require(bool(row["coverage"]), "rejected target coverage is empty")
            _require_text(row["target_id"], "rejected target target_id")
            _require_text(row["reference_slot_id"], "rejected target reference_slot_id")
            _require_text(row["authorization_id"], "target image authorization_id")
            _require_text(row["plan_id"], "rejected target plan_id")
            _require(
                isinstance(row["plan_revision"], int)
                and not isinstance(row["plan_revision"], bool)
                and row["plan_revision"] > 0,
                "rejected target plan_revision must be a positive integer",
            )
            _require_text(
                row["rejection_artifact_id"],
                "rejected target rejection_artifact_id",
            )
            _require_text(
                row["rejection_reviewer_id"],
                "rejected target rejection_reviewer_id",
            )
            _require(
                visual_contract.is_aware_timestamp(row["generated_at"]),
                "rejected target generated_at is not a timezone-aware ISO-8601 timestamp",
            )
            _require(
                visual_contract.is_aware_timestamp(row["rejected_at"]),
                "rejected target rejected_at is not a timezone-aware ISO-8601 timestamp",
            )
            _require(
                _timestamp(row["generated_at"]) < _timestamp(row["rejected_at"]),
                "rejected target was rejected before it was generated",
            )
        if row["kind"] not in {"target_gameplay_image", "rejected_target_image"}:
            _require(
                "authorization_id" not in row,
                "only generated target artifacts may carry authorization_id",
            )

    facets = data["facets"]
    _require(isinstance(facets, dict), "facets must be an object")
    _require(set(facets).issubset(FACETS), "unknown facet")
    for row in facets.values():
        _require(isinstance(row, dict), "facet must be an object")
        _require(set(row) in ({"intent", "evidence_ids", "review_ids"}, {"intent", "evidence_ids", "review_ids", "blocker"}), "facet fields differ")
        _require(row["intent"] in {"SUBMITTED", "PENDING", "FAILED", "PIVOT", "STOP"}, "unknown facet intent")
        for field in ("evidence_ids", "review_ids"):
            _require(
                isinstance(row[field], list)
                and all(isinstance(item, str) and item for item in row[field]),
                f"facet {field} is malformed",
            )
        if "blocker" in row:
            _require(isinstance(row["blocker"], str), "facet blocker must be text")

    reviews = data["reviews"]
    _require(isinstance(reviews, list), "reviews must be a list")
    review_fields = {
        "id",
        "facet",
        "review_artifact_id",
        "reviewer_id",
        "role",
        "artifact_ids_reviewed",
        "verdict",
        "rationale",
    }
    for row in reviews:
        _require(isinstance(row, dict) and set(row) == review_fields, "review fields differ")
        _require(isinstance(row["id"], str) and bool(row["id"]), "review id is empty")
        _require(row["facet"] in FACETS, "review facet is unknown")
        _require(isinstance(row["review_artifact_id"], str) and bool(row["review_artifact_id"]), "review artifact id is empty")
        _require(isinstance(row["reviewer_id"], str) and bool(row["reviewer_id"].strip()), "reviewer id is empty")
        _require(row["role"] in {"user", "independent_reviewer", "cold_player"}, "review role is unknown")
        _require(
            isinstance(row["artifact_ids_reviewed"], list)
            and all(isinstance(item, str) and item for item in row["artifact_ids_reviewed"]),
            "review coverage is malformed",
        )
        _require(row["verdict"] in {"accept", "reject"}, "review verdict is unknown")
        _require(isinstance(row["rationale"], str) and bool(row["rationale"].strip()), "review rationale is empty")

    decisions = data["visual_decisions"]
    _require(isinstance(decisions, list), "visual_decisions must be a list")
    decision_by_id: dict[str, dict[str, object]] = {}
    for row in decisions:
        try:
            visual_contract.validate_visual_decision(row)
        except visual_contract.SchemaError as error:
            raise SchemaError(str(error)) from error
        decision_id = row["decision_id"]
        _require(decision_id not in decision_by_id, "visual decision ids are duplicate")
        decision_by_id[decision_id] = row

    scope_approvals = data["visual_scope_approvals"]
    _require(isinstance(scope_approvals, list), "visual_scope_approvals must be a list")
    approval_by_id: dict[str, dict[str, object]] = {}
    for row in scope_approvals:
        _require(isinstance(row, dict), "scope approval must be an object")
        approval_id = row.get("approval_artifact_id")
        _require(isinstance(approval_id, str) and bool(approval_id.strip()), "scope approval approval_artifact_id is empty")
        _require(approval_id not in approval_by_id, "scope approval artifact ids are duplicate")
        decision = decision_by_id.get(row.get("decision_id"))
        _require(decision is not None, "scope approval decision does not resolve")
        _require(
            decision["decision_kind"] != "reference_not_proof",
            "reference_not_proof decision may not be referenced by a scope approval",
        )
        try:
            visual_contract.validate_scope_approval(row, decision)
        except visual_contract.SchemaError as error:
            raise SchemaError(str(error)) from error
        approval_by_id[approval_id] = row

    corrections = data["visual_correction_approvals"]
    _require(isinstance(corrections, list), "visual_correction_approvals must be a list")
    correction_ids: set[str] = set()
    for row in corrections:
        _require(isinstance(row, dict), "correction approval must be an object")
        approval_id = row.get("approval_artifact_id")
        _require(isinstance(approval_id, str) and bool(approval_id.strip()), "correction approval artifact id is empty")
        _require(approval_id not in approval_by_id, "approval artifact ids are duplicate")
        _require(approval_id not in correction_ids, "correction approval artifact ids are duplicate")
        correction_ids.add(approval_id)

    authorizations = data["visual_generation_authorizations"]
    _require(isinstance(authorizations, list), "visual_generation_authorizations must be a list")
    authorization_ids: set[str] = set()
    for row in authorizations:
        try:
            visual_contract.validate_generation_authorization(row)
        except visual_contract.SchemaError as error:
            raise SchemaError(str(error)) from error
        authorization_id = row["authorization_id"]
        _require(authorization_id not in authorization_ids, "authorization ids are duplicate")
        authorization_ids.add(authorization_id)
        decision = decision_by_id.get(row["decision_id"])
        _require(
            decision is None or decision["decision_kind"] != "reference_not_proof",
            "reference_not_proof decision may not be referenced by an authorization",
        )

    plans = data["reference_plans"]
    _require(isinstance(plans, list), "reference_plans must be a list")
    for row in plans:
        _require(isinstance(row, dict), "reference plan must be an object")
        stored_plan = dict(row)
        stored_approval = stored_plan.get("approval")
        stored_plan["approval"] = None
        try:
            visual_contract.validate_reference_plan(stored_plan, allow_placeholders=False)
        except visual_contract.SchemaError as error:
            raise SchemaError(str(error)) from error
        _require(isinstance(stored_approval, dict), "reference plan scope approval does not resolve")
        approval_id = stored_approval.get("approval_artifact_id")
        approval = approval_by_id.get(approval_id)
        _require(approval == stored_approval, "reference plan scope approval does not resolve")
        decision = decision_by_id.get(approval["decision_id"])
        _require(decision is not None, "reference plan decision does not resolve")
        _require(
            decision["decision_kind"] != "reference_not_proof",
            "reference_not_proof decision may not be referenced by a plan",
        )
        _require(
            decision["reference_plan"] == stored_plan,
            "decision reference plan differs",
        )
        try:
            visual_contract.validate_scope_approval(approval, decision)
        except visual_contract.SchemaError as error:
            raise SchemaError(str(error)) from error

    versions = data["visual_contract_versions"]
    _require(isinstance(versions, list), "visual_contract_versions must be a list")
    for row in versions:
        _validate_visual_contract_schema(row)

    active_contract_id = data["active_visual_contract_id"]
    _require(
        active_contract_id is None
        or (isinstance(active_contract_id, str) and bool(active_contract_id.strip())),
        "active_visual_contract_id is malformed",
    )

    _require(data["procedural_mode"] in {"none", "seeded"}, "procedural mode is unknown")
    _require(
        data["procedural_none_reason"] is None
        or isinstance(data["procedural_none_reason"], str),
        "procedural none reason is malformed",
    )
    _require(isinstance(data["procedural_systems"], list), "procedural systems must be a list")
    return data


def _safe_artifact(root: Path, row: dict[str, object]) -> tuple[Path | None, str | None]:
    relative = Path(row["path"])
    if relative.is_absolute() or ".." in relative.parts:
        return None, f"artifact {row['id']} escapes the project root"
    candidate = root / relative
    try:
        resolved = candidate.resolve(strict=True)
    except OSError:
        return None, f"artifact {row['id']} is missing"
    if not _inside(root, resolved) or not resolved.is_file():
        return None, f"artifact {row['id']} is not an inside-root regular file"
    return resolved, None


def _artifact_index(
    root: Path, artifacts: list[dict[str, object]]
) -> tuple[dict[str, dict[str, object]], list[str]]:
    indexed: dict[str, dict[str, object]] = {}
    errors: list[str] = []
    hashes: dict[Path, str] = {}
    seen: set[str] = set()
    for row in artifacts:
        artifact_id = row["id"]
        if artifact_id in seen:
            errors.append(f"duplicate artifact id: {artifact_id}")
            indexed.pop(artifact_id, None)
            continue
        seen.add(artifact_id)
        artifact_errors: list[str] = []
        if row["provenance"] not in KIND_PROVENANCES[row["kind"]]:
            artifact_errors.append(
                f"artifact {artifact_id} has provenance incompatible with {row['kind']}"
            )
        resolved, error = _safe_artifact(root, row)
        if error:
            artifact_errors.append(error)
        else:
            assert resolved is not None
            digest = hashes.get(resolved)
            if digest is None:
                digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
                hashes[resolved] = digest
            if digest != row["sha256"]:
                artifact_errors.append(f"artifact {artifact_id} SHA-256 mismatch")
        if artifact_errors:
            errors.extend(artifact_errors)
        else:
            indexed[artifact_id] = row
    return indexed, errors


def _review_index(reviews: list[dict[str, object]]) -> tuple[dict[str, dict[str, object]], list[str]]:
    indexed: dict[str, dict[str, object]] = {}
    errors: list[str] = []
    for row in reviews:
        if row["id"] in indexed:
            errors.append(f"duplicate review id: {row['id']}")
        else:
            indexed[row["id"]] = row
    return indexed, errors


def _required_kind_errors(facet: str, rows: list[dict[str, object]]) -> list[str]:
    kinds = {row["kind"] for row in rows}
    errors: list[str] = []
    for required in REQUIRED_KINDS[facet]:
        choices = set(required.split("|"))
        if not kinds & choices:
            errors.append(f"{facet} lacks {required}")
    if facet == "audio_feedback":
        audio = [row for row in rows if row["kind"] == "runtime_audio_video"]
        covered = {item for row in audio for item in row.get("coverage", [])}
        required_audio = {"action", "danger", "success", "failure", "ambience"}
        if covered != required_audio:
            errors.append("audio_feedback coverage is incomplete")
    return errors


def _review_errors(
    facet: str,
    facet_row: dict[str, object],
    review_index: dict[str, dict[str, object]],
    artifact_index: dict[str, dict[str, object]],
    builder_id: str,
    *,
    approval_reviewer: str | None = None,
) -> list[str]:
    errors: list[str] = []
    evidence_ids = set(facet_row["evidence_ids"])
    reviewed: set[str] = set()
    expected_role = "user" if facet == "visual" else "cold_player" if facet == "ux_onboarding" else "independent_reviewer"
    for review_id in facet_row["review_ids"]:
        review = review_index.get(review_id)
        if review is None:
            errors.append(f"{facet} references missing review {review_id}")
            continue
        if review["facet"] != facet:
            errors.append(f"review {review_id} belongs to another facet")
        if review["verdict"] != "accept":
            errors.append(f"review {review_id} rejected the evidence")
        if review["role"] != expected_role:
            errors.append(f"review {review_id} has the wrong role")
        if facet in {"visual", "ux_onboarding"} and review["reviewer_id"] == builder_id:
            errors.append(f"{facet} reviewer is the builder")
        if approval_reviewer is not None and review["reviewer_id"] != approval_reviewer:
            errors.append("visual review does not bind the approval reviewer")
        review_artifact = artifact_index.get(review["review_artifact_id"])
        if review_artifact is None or review_artifact["kind"] != "review_record":
            errors.append(f"review {review_id} lacks its immutable record")
        reviewed.update(review["artifact_ids_reviewed"])
    if reviewed != evidence_ids:
        errors.append(f"{facet} reviews do not cover the exact evidence set")
    return errors


def _timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def _unique_index(
    rows: list[dict[str, object]], key, label: str
) -> tuple[dict[object, dict[str, object]], list[str]]:
    """Index source records without letting duplicate identities choose a winner."""
    indexed: dict[object, dict[str, object]] = {}
    errors: list[str] = []
    for row in rows:
        identity = key(row)
        if identity in indexed:
            errors.append(f"duplicate {label}: {identity}")
        else:
            indexed[identity] = row
    return indexed, errors


def _generation_authorization_errors(
    data: dict[str, object], artifact_index: dict[str, dict[str, object]]
) -> list[str]:
    """Resolve every generated image through its immutable authorization chain."""
    errors: list[str] = []
    decisions, duplicate_errors = _unique_index(
        data["visual_decisions"], lambda row: row.get("decision_id"), "visual decision id"
    ); errors.extend(duplicate_errors)
    scopes, duplicate_errors = _unique_index(
        data["visual_scope_approvals"], lambda row: row.get("approval_artifact_id"), "scope approval artifact id"
    ); errors.extend(duplicate_errors)
    corrections, duplicate_errors = _unique_index(
        data["visual_correction_approvals"], lambda row: row.get("approval_artifact_id"), "correction approval artifact id"
    ); errors.extend(duplicate_errors)
    authorizations, duplicate_errors = _unique_index(
        data["visual_generation_authorizations"], lambda row: row.get("authorization_id"), "authorization id"
    ); errors.extend(duplicate_errors)
    plans, duplicate_errors = _unique_index(
        data["reference_plans"], lambda row: (row.get("plan_id"), row.get("revision")), "reference plan revision"
    ); errors.extend(duplicate_errors)

    resolved: dict[str, tuple[dict[str, object], dict[str, object]]] = {}
    for authorization_id, authorization in sorted(authorizations.items(), key=lambda item: str(item[0])):
        decision = decisions.get(authorization.get("decision_id"))
        plan = plans.get((authorization.get("plan_id"), authorization.get("plan_revision")))
        scope = scopes.get(authorization.get("approval_artifact_id"))
        if decision is None:
            errors.append(f"authorization {authorization_id} decision does not resolve")
        if plan is None:
            errors.append(f"authorization {authorization_id} plan does not resolve")
        if scope is None:
            errors.append(f"authorization {authorization_id} scope approval does not resolve")
        if decision is None or plan is None or scope is None:
            continue
        try:
            visual_contract.validate_visual_decision(decision)
            visual_contract.validate_scope_approval(scope, decision)
            visual_contract.validate_generation_authorization(authorization)
        except visual_contract.SchemaError as error:
            errors.append(f"authorization {authorization_id} {error}")
            continue
        decision_plan = decision["reference_plan"]
        stored_plan = dict(plan)
        stored_plan["approval"] = None
        if decision_plan != stored_plan:
            errors.append(f"authorization {authorization_id} decision plan binding drifted")
        if authorization["decision_sha256"] != visual_contract.canonical_sha256(decision):
            errors.append(f"authorization {authorization_id} decision binding drifted")
        if authorization["plan_sha256"] != visual_contract.canonical_plan_sha256(decision_plan):
            errors.append(f"authorization plan binding drifted: {authorization_id}")
        if authorization["approval_sha256"] != visual_contract.canonical_sha256(scope):
            errors.append(f"authorization {authorization_id} scope approval binding drifted")
        if authorization["batch_kind"] != ("initial" if plan["kind"] == "initial" else "delta") and authorization["batch_kind"] != "correction":
            errors.append(f"authorization {authorization_id} batch kind differs from plan")
        approved_slots = [row["reference_slot_id"] for row in plan["rows"]]
        authorized_slots = [row["reference_slot_id"] for row in authorization["authorized_slots"]]
        if authorization["batch_kind"] != "correction" and authorized_slots != approved_slots:
            errors.append(f"authorization slot set differs from approved plan: {authorization_id}")
        expected_supersedes = [row["supersedes_target_id"] for row in plan["rows"] if row["change_kind"] == "replace"]
        if authorization["supersedes_target_ids"] != expected_supersedes:
            errors.append(f"authorization supersession set differs: {authorization_id}")
        if authorization["base_contract_id"] != plan["base_contract_id"]:
            errors.append(f"authorization {authorization_id} base contract binding drifted")
        resolved[str(authorization_id)] = (authorization, plan)

    generated = [row for row in artifact_index.values() if row["kind"] in {"target_gameplay_image", "rejected_target_image"}]
    counts: dict[tuple[str, str], int] = {}
    rejected_by_target: dict[str, dict[str, object]] = {}
    prior_rejections: dict[tuple[str, int, str], list[dict[str, object]]] = {}
    for rejected in generated:
        if rejected["kind"] == "rejected_target_image":
            rejection_key = (
                rejected["plan_id"], rejected["plan_revision"],
                rejected["reference_slot_id"],
            )
            prior_rejections.setdefault(rejection_key, []).append(rejected)
            rejected_by_target[str(rejected["target_id"])] = rejected
    for attempts in prior_rejections.values():
        attempts.sort(key=lambda row: (_timestamp(row["rejected_at"]), str(row["id"])))
    for artifact in sorted(generated, key=lambda row: str(row["id"])):
        authorization_id = artifact.get("authorization_id")
        if authorization_id not in resolved:
            errors.append(f"artifact {artifact['id']} authorization does not resolve: {authorization_id}")
            if artifact["kind"] == "target_gameplay_image" and any(
                rejected.get("reference_slot_id") == artifact.get("reference_slot_id")
                for rejected in generated
                if rejected["kind"] == "rejected_target_image"
            ):
                errors.append(f"replacement target lacks correction authorization: {artifact['target_id']}")
            continue
        authorization, plan = resolved[authorization_id]
        slot_id = artifact.get("reference_slot_id")
        slots = {row["reference_slot_id"] for row in authorization["authorized_slots"]}
        if slot_id not in slots:
            errors.append(f"artifact {artifact['id']} slot is outside its authorization: {slot_id}")
            continue
        plan_slot = next((row for row in plan["rows"] if row["reference_slot_id"] == slot_id), None)
        if plan_slot is None or artifact.get("coverage") != plan_slot["coverage"]:
            errors.append(f"artifact {artifact['id']} plan row binding drifted")
        if artifact["plan_id"] != plan["plan_id"] or artifact["plan_revision"] != plan["revision"]:
            errors.append(f"artifact {artifact['id']} plan binding drifted")
        if _timestamp(artifact["generated_at"]) <= _timestamp(authorization["issued_at"]):
            errors.append(f"artifact {artifact['id']} generated before authorization")
        key = (authorization_id, slot_id)
        counts[key] = counts.get(key, 0) + 1
        if artifact["kind"] == "target_gameplay_image":
            rejection_key = (plan["plan_id"], plan["revision"], slot_id)
            previous = [
                row for row in prior_rejections.get(rejection_key, [])
                if _timestamp(row["rejected_at"]) < _timestamp(artifact["generated_at"])
            ]
            if previous:
                latest = previous[-1]
                correction = corrections.get(authorization["correction_approval_artifact_id"])
                if (
                    authorization["batch_kind"] != "correction"
                    or authorization["rejected_target_id"] != latest["target_id"]
                    or correction is None
                ):
                    errors.append(
                        f"replacement target lacks correction authorization: {artifact['target_id']}"
                    )

    for authorization_id, (authorization, _) in sorted(resolved.items()):
        for slot in authorization["authorized_slots"]:
            key = (authorization_id, slot["reference_slot_id"])
            count = counts.get(key, 0)
            if count > slot["result_budget"]:
                errors.append(f"authorization slot result budget exceeded: {authorization_id} {slot['reference_slot_id']}")
            if count == 0:
                errors.append(f"authorization has no generated result: {authorization_id} {slot['reference_slot_id']}")
        if authorization["batch_kind"] == "correction":
            rejected = rejected_by_target.get(str(authorization["rejected_target_id"]))
            correction = corrections.get(authorization["correction_approval_artifact_id"])
            if rejected is None or correction is None:
                errors.append(f"authorization {authorization_id} replacement target lacks correction authorization")
                continue
            correction_slots = [row["reference_slot_id"] for row in authorization["authorized_slots"]]
            if correction_slots != [rejected["reference_slot_id"]]:
                errors.append(
                    f"correction authorization slot set differs: {authorization_id}"
                )
            decision = decisions.get(authorization["decision_id"])
            try:
                projection = {field: rejected[field] for field in visual_contract.REJECTED_AUTH_INPUT_FIELDS}
                visual_contract.validate_correction_approval(correction, decision, projection)
            except (KeyError, visual_contract.SchemaError) as error:
                errors.append(f"authorization {authorization_id} {error}")
            if _timestamp(authorization["issued_at"]) <= _timestamp(rejected["rejected_at"]):
                errors.append(f"authorization {authorization_id} correction authorization precedes rejection")
    return sorted(set(errors))


def _approval_record_errors(
    label: str,
    approval: dict[str, object] | None,
    artifact_index: dict[str, dict[str, object]],
    builder_id: str,
    expected_binding: str,
) -> list[str]:
    if approval is None:
        return [f"{label} is missing"]
    errors: list[str] = []
    if approval["decision"] != "approved":
        errors.append(f"{label} is not approved")
    artifact = artifact_index.get(approval["approval_artifact_id"])
    if artifact is None or artifact["kind"] != "review_record":
        errors.append(f"{label} record is missing")
    if approval["reviewer_id"] == builder_id:
        errors.append(f"{label} reviewer is the builder")
    binding = (
        approval["plan_sha256"]
        if approval.get("schema_version") == "visual-scope-approval/v1"
        else approval["binding_sha256"]
    )
    if binding != expected_binding:
        errors.append(f"{label} binding drifted")
    return errors


def _approved_visual_chain(
    data: dict[str, object],
) -> tuple[list[dict[str, object]], list[str]]:
    errors: list[str] = []
    approved: dict[str, dict[str, object]] = {}
    for row in data["visual_contract_versions"]:
        approval = row["approval"]
        if approval is None or approval["decision"] != "approved":
            continue
        contract_id = row["contract_id"]
        if contract_id in approved:
            errors.append(f"duplicate approved visual contract id: {contract_id}")
        approved[contract_id] = row
    active_id = data["active_visual_contract_id"]
    if active_id is None or active_id not in approved:
        return [], errors + ["active visual contract does not resolve exactly once"]

    reverse_chain: list[dict[str, object]] = []
    seen: set[str] = set()
    current_id: str | None = active_id
    while current_id is not None:
        if current_id in seen:
            return [], errors + ["visual contract ancestry contains a cycle"]
        seen.add(current_id)
        current = approved.get(current_id)
        if current is None:
            return [], errors + [f"visual contract base {current_id} is missing"]
        reverse_chain.append(current)
        current_id = current["base_contract_id"]
    chain = list(reversed(reverse_chain))
    if set(approved) != seen:
        errors.append("approved visual contract history branches or is stale")
    if chain and chain[0]["base_contract_id"] is not None:
        errors.append("visual contract root has a base")
    return chain, errors


def _active_visual_contract_state(
    data: dict[str, object],
    artifact_index: dict[str, dict[str, object]],
) -> tuple[dict[str, dict[str, object]], list[str], str | None]:
    errors: list[str] = _generation_authorization_errors(data, artifact_index)
    plans: dict[tuple[str, int], dict[str, object]] = {}
    for row in data["reference_plans"]:
        key = (row["plan_id"], row["revision"])
        if key in plans:
            errors.append(f"duplicate reference plan revision: {key[0]} r{key[1]}")
        plans[key] = row

    active: dict[str, dict[str, object]] = {}
    referenced_artifacts: set[str] = set()
    historical_target_ids: set[str] = set()
    rejected_artifact_ids: set[str] = set()
    rejected_attempts: dict[
        tuple[str, int, str], list[dict[str, object]]
    ] = {}
    for artifact in artifact_index.values():
        if artifact["kind"] != "rejected_target_image":
            continue
        rejected_artifact_ids.add(artifact["id"])
        rejection_key = (
            artifact["plan_id"],
            artifact["plan_revision"],
            artifact["reference_slot_id"],
        )
        rejected_attempts.setdefault(rejection_key, []).append(artifact)
        target_id = artifact["target_id"]
        if target_id in historical_target_ids:
            errors.append(f"rejected target id {target_id} is reused")
        historical_target_ids.add(target_id)

        plan_row = plans.get((artifact["plan_id"], artifact["plan_revision"]))
        if plan_row is None:
            errors.append(f"rejected target {target_id} plan revision is missing")
        else:
            errors.extend(
                _approval_record_errors(
                    f"rejected target {target_id} scope approval",
                    plan_row["approval"],
                    artifact_index,
                    data["builder_id"],
                visual_contract.canonical_plan_sha256(
                        {
                            key: value
                            for key, value in plan_row.items()
                            if key != "approval"
                        }
                    ),
                )
            )
            slot_row = next(
                (
                    row
                    for row in plan_row["rows"]
                    if row["reference_slot_id"] == artifact["reference_slot_id"]
                ),
                None,
            )
            if slot_row is None:
                errors.append(
                    f"rejected target {target_id} slot is outside its approved plan"
                )
            elif artifact["coverage"] != slot_row["coverage"]:
                errors.append(f"rejected target {target_id} coverage drifted")
            if plan_row["approval"] is not None:
                scope_time = _timestamp(plan_row["approval"]["recorded_at"])
                if _timestamp(artifact["generated_at"]) <= scope_time:
                    errors.append(
                        f"rejected target {target_id} was generated before scope approval"
                    )

        rejection_record = artifact_index.get(artifact["rejection_artifact_id"])
        if rejection_record is None or rejection_record["kind"] != "review_record":
            errors.append(f"rejected target {target_id} rejection record is missing")
        if artifact["rejection_reviewer_id"] == data["builder_id"]:
            errors.append(f"rejected target {target_id} reviewer is the builder")

    latest_rejection_by_slot: dict[tuple[str, int, str], datetime] = {}
    for rejection_key, attempts in rejected_attempts.items():
        attempts.sort(key=lambda row: _timestamp(row["generated_at"]))
        previous_rejected_at: datetime | None = None
        latest_rejected_at: datetime | None = None
        for attempt in attempts:
            generated_at = _timestamp(attempt["generated_at"])
            if (
                previous_rejected_at is not None
                and generated_at <= previous_rejected_at
            ):
                errors.append(
                    f"target {attempt['target_id']} was generated before prior "
                    "rejection authorization"
                )
            rejected_at = _timestamp(attempt["rejected_at"])
            previous_rejected_at = rejected_at
            if latest_rejected_at is None or rejected_at > latest_rejected_at:
                latest_rejected_at = rejected_at
        assert latest_rejected_at is not None
        latest_rejection_by_slot[rejection_key] = latest_rejected_at

    mapped_artifact_ids = {
        target["artifact_id"]
        for version in data["visual_contract_versions"]
        for target in version["targets"]
    }
    for artifact_id in sorted(rejected_artifact_ids & mapped_artifact_ids):
        errors.append(
            f"rejected target artifact {artifact_id} is referenced by a visual contract"
        )

    chain, chain_errors = _approved_visual_chain(data)
    errors.extend(chain_errors)
    for version in chain:
        plan_row = plans.get((version["plan_id"], version["plan_revision"]))
        if plan_row is None:
            errors.append(f"visual contract {version['contract_id']} plan is missing")
            continue
        errors.extend(
            _approval_record_errors(
                "scope approval",
                plan_row["approval"],
                artifact_index,
                data["builder_id"],
                    visual_contract.canonical_plan_sha256(
                    {key: value for key, value in plan_row.items() if key != "approval"}
                ),
            )
        )
        errors.extend(
            _approval_record_errors(
                "target approval",
                version["approval"],
                artifact_index,
                data["builder_id"],
                visual_contract.canonical_sha256(
                    {key: value for key, value in version.items() if key != "approval"}
                ),
            )
        )
        is_root = version is chain[0]
        expected_kind = "initial" if is_root else "delta"
        if plan_row["kind"] != expected_kind:
            errors.append(
                f"visual contract {version['contract_id']} uses the wrong plan kind"
            )
        if plan_row["base_contract_id"] != version["base_contract_id"]:
            errors.append(f"visual contract {version['contract_id']} plan base differs")

        plan_slots = {row["reference_slot_id"]: row for row in plan_row["rows"]}
        target_slots = {
            row["reference_slot_id"]: row for row in version["targets"]
        }
        if len(plan_slots) != len(plan_row["rows"]):
            errors.append("reference plan slot ids are duplicate")
        if len(target_slots) != len(version["targets"]):
            errors.append("visual target slot ids are duplicate")
        if set(plan_slots) != set(target_slots):
            errors.append("visual targets do not exactly cover approved reference slots")

        scope_time = (
            _timestamp(plan_row["approval"]["recorded_at"])
            if plan_row["approval"] is not None
            else None
        )
        approval_time = (
            _timestamp(version["approval"]["recorded_at"])
            if version["approval"] is not None
            else None
        )
        if approval_time is not None:
            plan_authorizations = {
                row["authorization_id"]
                for row in data["visual_generation_authorizations"]
                if row["plan_id"] == plan_row["plan_id"]
                and row["plan_revision"] == plan_row["revision"]
            }
            batch = [
                row for row in artifact_index.values()
                if row["kind"] == "target_gameplay_image"
                and row.get("authorization_id") in plan_authorizations
            ]
            if batch and max(_timestamp(row["generated_at"]) for row in batch) >= approval_time:
                errors.append("target approval precedes complete authorized batch")
        for slot_id, target in target_slots.items():
            slot_row = plan_slots.get(slot_id)
            if slot_row is None:
                continue
            target_id = target["target_id"]
            if target_id in historical_target_ids:
                errors.append(
                    f"target id {target_id} is reused in visual contract history"
                )
            historical_target_ids.add(target_id)
            artifact = artifact_index.get(target["artifact_id"])
            referenced_artifacts.add(target["artifact_id"])
            if artifact is None:
                errors.append(f"target artifact is missing: {target_id}")
                continue
            expected_parent = (
                Path("docs") / "visual-contract" / version["contract_id"] / "targets"
            )
            if Path(target["path"]).parent != expected_parent:
                errors.append(
                    f"target {target_id} is not at its contract version path"
                )
            if (
                artifact["kind"] != "target_gameplay_image"
                or artifact["provenance"] != "imagegen_target"
                or artifact["target_id"] != target_id
                or artifact["reference_slot_id"] != slot_id
                or artifact["path"] != target["path"]
                or artifact["sha256"] != target["sha256"]
                or artifact["coverage"] != slot_row["coverage"]
            ):
                errors.append(f"target {target_id} mapping or bytes drifted")
            generated = _timestamp(artifact["generated_at"])
            if scope_time is not None and generated <= scope_time:
                errors.append(
                    f"target {target_id} was generated before scope approval"
                )
            latest_rejection = latest_rejection_by_slot.get(
                (version["plan_id"], version["plan_revision"], slot_id)
            )
            if latest_rejection is not None and generated <= latest_rejection:
                errors.append(
                    f"target {target_id} was generated before prior "
                    "rejection authorization"
                )
            if approval_time is not None and generated >= approval_time:
                errors.append(
                    f"target {target_id} was generated after target approval"
                )

            if slot_row["change_kind"] == "replace":
                old_id = slot_row["supersedes_target_id"]
                if old_id not in active:
                    errors.append(f"replacement target {old_id} is not active")
                else:
                    del active[old_id]
            if target_id in active:
                errors.append(f"duplicate active target id: {target_id}")
            else:
                active[target_id] = target

    for artifact in artifact_index.values():
        if (
            artifact["kind"] == "target_gameplay_image"
            and artifact["id"] not in referenced_artifacts
        ):
            errors.append(
                f"generated target artifact {artifact['id']} is outside an approved plan"
            )
    reviewer = (
        chain[-1]["approval"]["reviewer_id"]
        if chain and chain[-1]["approval"] is not None
        else None
    )
    return active, errors, reviewer


def _visual_errors(
    data: dict[str, object],
    facet_row: dict[str, object],
    rows: list[dict[str, object]],
    artifact_index: dict[str, dict[str, object]],
) -> tuple[list[str], str | None]:
    approved, errors, approval_reviewer = _active_visual_contract_state(
        data, artifact_index
    )

    captures = [row for row in rows if row["kind"] == "canonical_godot_capture"]
    captured_ids: set[str] = set()
    for capture in captures:
        target_id = capture.get("target_id")
        if not isinstance(target_id, str) or target_id in captured_ids:
            errors.append("visual capture target identity is missing or duplicate")
            continue
        captured_ids.add(target_id)
        target = approved.get(target_id)
        if target is None or capture.get("approved_target_sha256") != target["sha256"]:
            errors.append(f"visual capture {capture['id']} approval binding drifted")
        if capture["provenance"] != "godot_runtime":
            errors.append(f"visual capture {capture['id']} is not Godot runtime evidence")
    if captured_ids != set(approved):
        errors.append("visual captures do not cover every approved target")
    return errors, approval_reviewer


def _procedural_results(
    data: dict[str, object], artifact_index: dict[str, dict[str, object]]
) -> tuple[dict[str, dict[str, object]], list[str], bool]:
    results: dict[str, dict[str, object]] = {}
    errors: list[str] = []
    systems = data["procedural_systems"]
    if data["procedural_mode"] == "none":
        if systems or not isinstance(data["procedural_none_reason"], str) or not data["procedural_none_reason"].strip():
            errors.append("procedural none mode lacks its reason or contains systems")
        return results, errors, False
    if data["procedural_none_reason"] not in {None, ""}:
        errors.append("seeded mode still has a none reason")
    if not systems:
        return results, errors, not errors
    seen: set[str] = set()
    for system in systems:
        system_errors: list[str] = []
        seen_seeds: set[tuple[str, str]] = set()
        seen_outputs: set[str] = set()
        if not isinstance(system, dict) or set(system) != {"id", "grammar_artifact_id", "seed_cases"}:
            errors.append("procedural system fields differ")
            continue
        system_id = system["id"]
        if not isinstance(system_id, str) or not system_id or system_id in seen:
            errors.append("procedural system id is missing or duplicate")
            continue
        seen.add(system_id)
        grammar = artifact_index.get(system["grammar_artifact_id"])
        if grammar is None or grammar["kind"] != "procedural_grammar":
            system_errors.append("procedural grammar artifact is missing")
        cases = system["seed_cases"]
        if not isinstance(cases, list):
            system_errors.append("seed cases must be a list")
            cases = []
        required_classes = {"canonical", "random", "boundary", "worst_observed"}
        classes: list[str] = []
        for case in cases:
            if not isinstance(case, dict):
                system_errors.append("seed case is not an object")
                continue
            seed_class = case.get("class")
            if not isinstance(seed_class, str) or seed_class not in required_classes:
                system_errors.append("seed case class is unknown")
                continue
            classes.append(seed_class)
            expected_fields = {"class", "seed", "artifact_ids"}
            if seed_class == "worst_observed":
                expected_fields |= {"population_artifact_id", "selection_method"}
            if set(case) != expected_fields:
                system_errors.append(f"seed case {seed_class} fields differ")
                continue
            seed = case["seed"]
            if not (
                (isinstance(seed, int) and not isinstance(seed, bool))
                or (isinstance(seed, str) and bool(seed.strip()))
            ):
                system_errors.append(f"seed case {seed_class} has an invalid seed")
            else:
                seed_key = (type(seed).__name__, str(seed))
                if seed_key in seen_seeds:
                    system_errors.append(
                        f"seed case {seed_class} reuses another case seed"
                    )
                seen_seeds.add(seed_key)
            ids = case.get("artifact_ids")
            if (
                not isinstance(ids, list)
                or not ids
                or any(not isinstance(item, str) for item in ids)
                or len(set(ids)) != len(ids)
                or any(item not in artifact_index for item in ids)
            ):
                system_errors.append(f"seed case {seed_class} lacks existing artifacts")
                rows = []
                artifact_ids: list[str] = []
            else:
                rows = [artifact_index[item] for item in ids]
                artifact_ids = ids
            if not any(
                row["kind"] == "procedural_output"
                and row["provenance"] == "godot_runtime"
                for row in rows
            ):
                system_errors.append(
                    f"seed case {seed_class} lacks a Godot procedural output"
                )
            for row in rows:
                if (
                    row["kind"] == "procedural_output"
                    and row["provenance"] == "godot_runtime"
                ):
                    output_key = row["sha256"]
                    if output_key in seen_outputs:
                        system_errors.append(
                            f"seed case {seed_class} reuses another case output"
                        )
                    seen_outputs.add(output_key)
            if seed_class == "worst_observed":
                population_id = case.get("population_artifact_id")
                population = (
                    artifact_index.get(population_id)
                    if isinstance(population_id, str)
                    else None
                )
                if (
                    population is None
                    or population["kind"] != "procedural_population"
                    or population_id in artifact_ids
                    or not isinstance(case.get("selection_method"), str)
                    or not case["selection_method"].strip()
                ):
                    system_errors.append("worst_observed lacks population or selection method")
        if set(classes) != required_classes or len(classes) != len(required_classes):
            system_errors.append("procedural system lacks one exact four-class seed suite")
        result = "FAILED" if system_errors else "VERIFIED"
        results[system_id] = {"result": result, "errors": system_errors}
        errors.extend(f"{system_id}: {item}" for item in system_errors)
    return results, errors, False


def _candidate_errors(
    data: dict[str, object],
    artifact_index: dict[str, dict[str, object]],
    facet_results: dict[str, dict[str, object]],
    procedural_results: dict[str, dict[str, object]],
    procedural_pending: bool,
) -> list[str]:
    if (
        procedural_pending
        or any(row["result"] != "VERIFIED" for row in facet_results.values())
        or any(row["result"] != "VERIFIED" for row in procedural_results.values())
    ):
        return []
    errors: list[str] = []
    game = data["game"]
    for field in ("godot_version", "build_artifact_id", "target_hardware"):
        if not game[field].strip():
            errors.append(f"game.{field} is required for a verified candidate")
    build_id = game["build_artifact_id"]
    build = artifact_index.get(build_id)
    ship_ids = set(data["facets"]["ship"]["evidence_ids"])
    if (
        build is None
        or build["kind"] != "release_build"
        or build_id not in ship_ids
    ):
        errors.append("game.build_artifact_id is not the submitted ship release")
    return errors


def _evaluate(root: Path, data: dict[str, object]) -> dict[str, object]:
    artifact_index, global_errors = _artifact_index(root, data["artifacts"])
    global_errors.extend(_generation_authorization_errors(data, artifact_index))
    review_index, review_index_errors = _review_index(data["reviews"])
    global_errors.extend(review_index_errors)
    review_references: dict[str, list[str]] = {}
    for facet_name, facet_row in data["facets"].items():
        for review_id in facet_row["review_ids"]:
            review_references.setdefault(review_id, []).append(facet_name)
    for review_id, review in review_index.items():
        references = review_references.get(review_id, [])
        if len(references) != 1:
            global_errors.append(
                f"review {review_id} must be referenced exactly once by its facet"
            )
        if review["verdict"] == "reject":
            global_errors.append(f"review {review_id} records a rejection")
    facet_results: dict[str, dict[str, object]] = {}
    for facet in FACETS:
        facet_row = data["facets"].get(facet)
        if facet_row is None or facet_row["intent"] == "PENDING":
            facet_results[facet] = {"result": "PENDING", "errors": ["facet is pending"]}
            continue
        if facet_row["intent"] in {"FAILED", "PIVOT", "STOP"}:
            facet_results[facet] = {"result": "FAILED", "errors": [f"facet intent is {facet_row['intent']}"]}
            continue
        errors: list[str] = []
        evidence_ids = facet_row["evidence_ids"]
        if len(set(evidence_ids)) != len(evidence_ids) or not evidence_ids:
            errors.append(f"{facet} evidence ids are empty or duplicate")
        rows = []
        for artifact_id in evidence_ids:
            artifact = artifact_index.get(artifact_id)
            if artifact is None:
                errors.append(f"{facet} references missing artifact {artifact_id}")
            else:
                rows.append(artifact)
        errors.extend(_required_kind_errors(facet, rows))
        approval_reviewer = None
        if facet == "visual":
            visual_errors, approval_reviewer = _visual_errors(
                data, facet_row, rows, artifact_index
            )
            errors.extend(visual_errors)
        errors.extend(
            _review_errors(
                facet,
                facet_row,
                review_index,
                artifact_index,
                data["builder_id"],
                approval_reviewer=approval_reviewer,
            )
        )
        facet_results[facet] = {
            "result": "FAILED" if errors else "VERIFIED",
            "errors": errors,
        }
    procedural_results, procedural_errors, procedural_pending = _procedural_results(
        data, artifact_index
    )
    global_errors.extend(procedural_errors)
    global_errors.extend(
        _candidate_errors(
            data,
            artifact_index,
            facet_results,
            procedural_results,
            procedural_pending,
        )
    )
    if (
        global_errors
        or any(row["result"] == "FAILED" for row in facet_results.values())
        or any(row["result"] == "FAILED" for row in procedural_results.values())
    ):
        overall = "FAILED"
    elif procedural_pending or any(
        row["result"] == "PENDING" for row in facet_results.values()
    ):
        overall = "PENDING"
    else:
        overall = "VERIFIED"
    return {
        "schema_version": "evidence-report/v1",
        "run_id": data["run_id"],
        "overall": overall,
        "facets": facet_results,
        "procedural_systems": procedural_results,
        "errors": global_errors,
        "trust_boundary": (
            "Structural completeness and local byte integrity do not prove human "
            "identity, provenance truth, artistic quality, fun, or shipping readiness."
        ),
    }


def _init(args: argparse.Namespace) -> int:
    builder_id = args.builder_id.strip()
    if not builder_id:
        return 3

    root = Path(args.project_root).resolve()
    manifest = Path(args.manifest).resolve()
    if not root.is_dir() or not (root / "project.godot").is_file():
        return 3
    if not _inside(root, manifest) or manifest.exists():
        return 3

    try:
        _atomic_json(
            manifest,
            _manifest_template(
                builder_id=builder_id,
                dimension=args.dimension,
                procedural_mode=args.procedural_mode,
            ),
        )
    except (OSError, ValueError):
        return 3
    return 0


def _validate(args: argparse.Namespace) -> int:
    root = Path(args.project_root).resolve()
    manifest = Path(args.manifest).resolve()
    report = Path(args.report).resolve()
    if (
        not root.is_dir()
        or not (root / "project.godot").is_file()
        or not _inside(root, manifest)
        or not manifest.is_file()
        or not _inside(root, report)
    ):
        return 3
    try:
        data = _validate_schema(
            visual_contract.loads_json(manifest.read_text(encoding="utf-8"))
        )
    except (OSError, UnicodeError, json.JSONDecodeError, SchemaError):
        return 3
    protected = {manifest, (root / "project.godot").resolve()}
    for artifact in data["artifacts"]:
        protected.add((root / Path(artifact["path"])).resolve())
    for version in data["visual_contract_versions"]:
        for target in version["targets"]:
            protected.add((root / Path(target["path"])).resolve())
    if report.suffix.lower() != ".json" or report in protected:
        return 3
    if report.exists():
        if not report.is_file():
            return 3
        try:
            previous = visual_contract.loads_json(
                report.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, json.JSONDecodeError, SchemaError):
            return 3
        if not (
            isinstance(previous, dict)
            and previous.get("schema_version") == "evidence-report/v1"
            and isinstance(previous.get("run_id"), str)
            and previous.get("overall") in {"VERIFIED", "PENDING", "FAILED"}
            and isinstance(previous.get("facets"), dict)
        ):
            return 3
    try:
        result = _evaluate(root, data)
        _atomic_json(report, result)
    except (OSError, ValueError):
        return 3
    if result["overall"] == "VERIFIED":
        return 0
    if result["overall"] == "PENDING":
        return 1
    return 2


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
    except SystemExit:
        return 3
    if args.command == "init":
        return _init(args)
    if args.command == "validate":
        return _validate(args)
    return 3


if __name__ == "__main__":
    sys.exit(main())

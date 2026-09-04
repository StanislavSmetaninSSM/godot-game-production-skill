"""Pure schemas and bindings for deterministic visual authorization."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from pathlib import PurePosixPath


CANONICAL_SCOPE_QUESTION = (
    "Do you exactly approve the proposed reference slot ID set?"
)
CANONICAL_TARGET_QUESTION = (
    "Do you exactly approve the displayed target ID set?"
)
PLACEHOLDER = "<required-value>"
CANONICAL_PROOF_GATES = (
    "actual bitmap presentation",
    "project-local PNG",
    "SHA-256 binding",
    "buildability",
    "motion cue",
    "sound cue",
    "target-Godot input/state/outcome evidence",
    "TDD",
    "independent review",
    "core play",
    "systems/holism",
    "content",
    "visual",
    "audio/feedback",
    "UX/onboarding",
    "reliability/performance",
    "ship",
)
HEX = set("0123456789abcdef")
REFERENCE_PLAN_FIELDS = {
    "plan_id", "revision", "kind", "base_contract_id", "rows", "approval",
}
REFERENCE_SLOT_FIELDS = {
    "reference_slot_id", "target_kind", "subject", "visual_question",
    "coverage", "composition", "motion_cue", "sound_cue",
    "dependent_work", "rationale", "image_count", "change_kind",
    "supersedes_target_id",
}
COMPOSITION_FIELDS = {
    "camera", "angle", "environment", "characters", "ui", "vfx",
}
TARGET_KINDS = {
    "location", "gameplay_state", "ui_mode", "character", "asset_family",
}
COMMON_DECISION_FIELDS = {
    "schema_version", "decision_id", "builder_id", "created_at",
    "decision_kind", "state", "generation_status",
}
INITIAL_DECISION_FIELDS = COMMON_DECISION_FIELDS | {
    "reference_plan", "scope_question",
}
DELTA_DECISION_FIELDS = COMMON_DECISION_FIELDS | {
    "change_scope", "reference_plan", "blocked_work", "continuing_work",
    "preserved_bindings", "affected_targets", "target_approval_scope",
    "scope_question",
}
PROOF_DECISION_FIELDS = COMMON_DECISION_FIELDS | {
    "verdict", "preserved_evidence",
}
PRESERVED_BINDING_FIELDS = {"target_id", "sha256", "path"}
AFFECTED_TARGET_FIELDS = {"target_id", "dependent_work", "change_kind"}
SCOPE_APPROVAL_FIELDS = {
    "schema_version", "approval_artifact_id", "decision_id", "reviewer_id",
    "decision", "recorded_at", "decision_sha256", "plan_sha256",
    "approved_slot_ids",
}
CORRECTION_APPROVAL_FIELDS = {
    "schema_version", "approval_artifact_id", "reviewer_id", "decision",
    "recorded_at", "plan_id", "plan_revision", "reference_slot_id",
    "rejected_target_id", "rejected_target_sha256", "correction_direction",
}
REJECTED_AUTH_INPUT_FIELDS = {
    "target_id", "reference_slot_id", "sha256", "plan_id", "plan_revision",
    "authorization_id", "generated_at", "rejected_at",
}
AUTHORIZATION_FIELDS = {
    "schema_version", "authorization_id", "status", "batch_kind", "issued_at",
    "decision_id", "decision_sha256", "plan_id", "plan_revision",
    "plan_sha256", "approval_artifact_id", "approval_sha256",
    "authorized_slots", "base_contract_id", "supersedes_target_ids",
    "rejected_target_id", "correction_approval_artifact_id",
}
AUTHORIZED_SLOT_FIELDS = {"reference_slot_id", "result_budget"}


class SchemaError(ValueError):
    """JSON structure is unsafe or does not match the declared schema."""


class InvariantError(SchemaError):
    """The object has a known shape but violates a visual contract."""


def _schema(condition: bool, message: str) -> None:
    if not condition:
        raise SchemaError(message)


def _invariant(condition: bool, message: str) -> None:
    if not condition:
        raise InvariantError(message)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise SchemaError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def loads_json(text: str) -> object:
    return json.loads(text, object_pairs_hook=_unique_object)


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonical_plan_sha256(plan: dict[str, object]) -> str:
    return canonical_sha256(
        {key: value for key, value in plan.items() if key != "approval"}
    )


def is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and set(value).issubset(HEX)
    )


def is_aware_timestamp(value: object) -> bool:
    if not isinstance(value, str) or "T" not in value:
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def is_portable_relative_path(value: object) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or ":" in value
        or value.startswith("/")
    ):
        return False
    path = PurePosixPath(value)
    return (
        value == path.as_posix()
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def _text(value: object, label: str) -> str:
    _invariant(
        isinstance(value, str) and bool(value.strip()),
        f"{label} is empty",
    )
    return value


def _text_list(
    value: object, label: str, *, allow_empty: bool = False
) -> list[str]:
    _schema(isinstance(value, list), f"{label} must be a list")
    _invariant(
        (allow_empty or bool(value))
        and all(isinstance(item, str) and bool(item.strip()) for item in value),
        f"{label} is malformed",
    )
    return value


def _is_placeholder_text(value: str) -> bool:
    normalized = value.strip().casefold()
    if normalized in {
        PLACEHOLDER,
        "unspecified",
        "not specified",
        "unknown",
        "tbd",
        "todo",
        "to be determined",
        "to be decided",
    }:
        return True
    if normalized.startswith("<required-value:") and normalized.endswith(">"):
        return True
    if normalized.startswith(("pending_", "pending-", "pending ")):
        return True
    words = (
        normalized.replace("_", "-")
        .replace(" ", "-")
        .replace("<", "-")
        .replace(">", "-")
        .split("-")
    )
    return "placeholder" in words


def _has_placeholder(value: object) -> bool:
    if isinstance(value, str) and _is_placeholder_text(value):
        return True
    if isinstance(value, list):
        return any(_has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(_has_placeholder(item) for item in value.values())
    return False


def validate_reference_plan(
    value: object, *, allow_placeholders: bool
) -> dict[str, object]:
    _schema(
        isinstance(value, dict) and set(value) == REFERENCE_PLAN_FIELDS,
        "reference plan fields differ",
    )
    _text(value["plan_id"], "reference plan plan_id")
    _invariant(
        isinstance(value["revision"], int)
        and not isinstance(value["revision"], bool)
        and value["revision"] > 0,
        "reference plan revision is invalid",
    )
    _schema(isinstance(value["kind"], str), "reference plan kind must be text")
    _invariant(value["kind"] in {"initial", "delta"}, "reference plan kind is unknown")
    if value["kind"] == "initial":
        _invariant(value["base_contract_id"] is None, "initial plan has a base")
    else:
        _text(value["base_contract_id"], "delta plan base_contract_id")
    _schema(isinstance(value["rows"], list), "reference plan rows must be a list")
    _invariant(bool(value["rows"]), "reference plan rows are empty")
    _invariant(value["approval"] is None, "pending plan approval is not null")
    slot_ids: set[str] = set()
    for row in value["rows"]:
        _schema(
            isinstance(row, dict) and set(row) == REFERENCE_SLOT_FIELDS,
            "reference slot fields differ",
        )
        slot_id = _text(row["reference_slot_id"], "reference slot id")
        _invariant(slot_id not in slot_ids, "reference plan slot ids are duplicate")
        slot_ids.add(slot_id)
        _schema(isinstance(row["target_kind"], str), "target kind must be text")
        _invariant(row["target_kind"] in TARGET_KINDS, "target kind is unknown")
        for field in (
            "subject", "visual_question", "motion_cue", "sound_cue", "rationale",
        ):
            _text(row[field], f"reference slot {field}")
        for field in ("coverage", "dependent_work"):
            _text_list(row[field], f"reference slot {field}")
        _schema(
            isinstance(row["composition"], dict)
            and set(row["composition"]) == COMPOSITION_FIELDS,
            "reference slot composition fields differ",
        )
        for field in COMPOSITION_FIELDS:
            _text(row["composition"][field], f"composition {field}")
        _invariant(
            isinstance(row["image_count"], int)
            and not isinstance(row["image_count"], bool)
            and row["image_count"] == 1,
            "reference slot image_count must equal integer 1",
        )
        expected = {"initial"} if value["kind"] == "initial" else {"add", "replace"}
        _schema(
            isinstance(row["change_kind"], str),
            "reference slot change_kind must be text",
        )
        _invariant(
            row["change_kind"] in expected,
            "reference slot change_kind conflicts with plan kind",
        )
        if row["change_kind"] == "replace":
            _text(row["supersedes_target_id"], "replacement supersedes_target_id")
        else:
            _invariant(
                row["supersedes_target_id"] is None,
                "non-replacement supersedes a target",
            )
    if not allow_placeholders:
        _invariant(not _has_placeholder(value), "unresolved placeholder")
    return value


def _validate_common_decision(value: dict[str, object]) -> None:
    _invariant(
        value["schema_version"] == "visual-decision/v1",
        "wrong visual decision schema version",
    )
    try:
        uuid.UUID(value["decision_id"])
    except (AttributeError, TypeError, ValueError) as error:
        raise InvariantError("decision_id is not a UUID") from error
    _text(value["builder_id"], "decision builder_id")
    _invariant(is_aware_timestamp(value["created_at"]), "decision timestamp is invalid")


def validate_visual_decision(value: object) -> dict[str, object]:
    _schema(isinstance(value, dict), "visual decision must be an object")
    decision_kind = value.get("decision_kind")
    _schema(isinstance(decision_kind, str), "visual decision kind must be text")
    expected_fields = {
        "initial_scope": INITIAL_DECISION_FIELDS,
        "delta_scope": DELTA_DECISION_FIELDS,
        "reference_not_proof": PROOF_DECISION_FIELDS,
    }.get(decision_kind)
    _invariant(expected_fields is not None, "visual decision kind is unknown")
    field_label = decision_kind.removesuffix("_scope")
    _schema(set(value) == expected_fields, f"{field_label} decision fields differ")
    _validate_common_decision(value)
    if decision_kind == "initial_scope":
        _invariant(value["state"] == "REFERENCE_SCOPE_PENDING", "initial state differs")
        _invariant(value["generation_status"] == "not_started", "generation started")
        plan = validate_reference_plan(value["reference_plan"], allow_placeholders=True)
        _invariant(plan["kind"] == "initial", "initial decision uses a delta plan")
        _invariant(value["scope_question"] == CANONICAL_SCOPE_QUESTION, "scope question differs")
    elif decision_kind == "delta_scope":
        _invariant(value["state"] == "VISUAL_DELTA_PENDING", "delta state differs")
        _invariant(value["generation_status"] == "not_started", "generation started")
        _schema(isinstance(value["change_scope"], str), "delta scope must be text")
        _invariant(value["change_scope"] in {"local", "global"}, "delta scope differs")
        plan = validate_reference_plan(value["reference_plan"], allow_placeholders=True)
        _invariant(plan["kind"] == "delta", "delta decision uses an initial plan")
        blocked_work = _text_list(
            value["blocked_work"], "blocked_work", allow_empty=True
        )
        continuing_work = _text_list(
            value["continuing_work"], "continuing_work", allow_empty=True
        )
        _invariant(
            not ({item.strip() for item in blocked_work}
                 & {item.strip() for item in continuing_work}),
            "blocked and continuing work overlap",
        )
        _schema(isinstance(value["preserved_bindings"], list), "preserved_bindings must be a list")
        preserved_target_ids: list[str] = []
        for binding in value["preserved_bindings"]:
            _schema(isinstance(binding, dict) and set(binding) == PRESERVED_BINDING_FIELDS, "preserved binding fields differ")
            preserved_target_ids.append(
                _text(binding["target_id"], "preserved target_id").strip()
            )
            _invariant(is_portable_relative_path(binding["path"]), "preserved path is not portable")
            _invariant(binding["sha256"] == PLACEHOLDER or is_sha256(binding["sha256"]), "preserved SHA-256 is malformed")
        _invariant(
            len(preserved_target_ids) == len(set(preserved_target_ids)),
            "preserved target ids are duplicate",
        )
        _schema(isinstance(value["affected_targets"], list), "affected_targets must be a list")
        _invariant(bool(value["affected_targets"]), "affected_targets is empty")
        affected_target_ids: list[str] = []
        affected_replacement_ids: set[str] = set()
        for target in value["affected_targets"]:
            _schema(isinstance(target, dict) and set(target) == AFFECTED_TARGET_FIELDS, "affected target fields differ")
            target_id = _text(target["target_id"], "affected target_id").strip()
            affected_target_ids.append(target_id)
            _text_list(target["dependent_work"], "affected dependent_work")
            _schema(
                isinstance(target["change_kind"], str),
                "affected change_kind must be text",
            )
            _invariant(
                target["change_kind"] in {"add", "replace"},
                "affected change_kind differs",
            )
            if target["change_kind"] == "replace":
                affected_replacement_ids.add(target_id)
        _invariant(
            len(affected_target_ids) == len(set(affected_target_ids)),
            "affected target ids are duplicate",
        )
        _invariant(
            not (set(preserved_target_ids) & set(affected_target_ids)),
            "preserved and affected targets overlap",
        )
        plan_replacement_ids = {
            row["supersedes_target_id"].strip()
            for row in plan["rows"]
            if row["change_kind"] == "replace"
        }
        _invariant(
            plan_replacement_ids == affected_replacement_ids,
            "replacement targets differ from plan supersessions",
        )
        _invariant(value["target_approval_scope"] == "complete_delta_batch_only", "target approval scope differs")
        _invariant(value["scope_question"] == CANONICAL_SCOPE_QUESTION, "scope question differs")
    else:
        _invariant(value["state"] == "UNCHANGED", "proof decision state differs")
        _invariant(value["generation_status"] == "not_authorized", "proof decision authorized generation")
        _invariant(value["verdict"] == "rejected", "proof claim was not rejected")
        _invariant(value["preserved_evidence"] == list(CANONICAL_PROOF_GATES), "proof gates differ")
    return value


def build_decision_report(decision: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": "visual-decision-report/v1",
        "decision_id": decision["decision_id"],
        "decision_sha256": canonical_sha256(decision),
        "status": "VALID_PENDING",
        "errors": [],
    }


def validate_scope_approval(
    value: object, decision: dict[str, object]
) -> dict[str, object]:
    _schema(isinstance(value, dict) and set(value) == SCOPE_APPROVAL_FIELDS, "scope approval fields differ")
    _invariant(value["schema_version"] == "visual-scope-approval/v1", "wrong scope approval schema")
    for field in ("approval_artifact_id", "decision_id", "reviewer_id", "recorded_at"):
        _text(value[field], f"scope approval {field}")
    _invariant(value["decision"] == "approved", "scope is not approved")
    _invariant(is_aware_timestamp(value["recorded_at"]), "scope approval timestamp is invalid")
    _invariant(value["decision_id"] == decision["decision_id"], "scope approval decision differs")
    _invariant(value["reviewer_id"] != decision["builder_id"], "scope approval reviewer is the builder")
    _invariant(value["decision_sha256"] == canonical_sha256(decision), "scope approval decision binding drifted")
    plan = decision["reference_plan"]
    _invariant(value["plan_sha256"] == canonical_plan_sha256(plan), "scope approval plan binding drifted")
    expected_slots = [row["reference_slot_id"] for row in plan["rows"]]
    _invariant(value["approved_slot_ids"] == expected_slots, "approved slot set differs")
    _invariant(timestamp(value["recorded_at"]) > timestamp(decision["created_at"]), "approval precedes decision")
    return value


def _validate_rejected_authorization_input(
    value: object, decision: dict[str, object]
) -> dict[str, object]:
    _schema(
        isinstance(value, dict) and set(value) == REJECTED_AUTH_INPUT_FIELDS,
        "rejected target authorization fields differ",
    )
    for field in (
        "target_id", "reference_slot_id", "plan_id", "authorization_id",
    ):
        _text(value[field], f"rejected target {field}")
    _invariant(is_sha256(value["sha256"]), "rejected target SHA-256 is malformed")
    _invariant(
        isinstance(value["plan_revision"], int)
        and not isinstance(value["plan_revision"], bool)
        and value["plan_revision"] > 0,
        "rejected target plan revision is invalid",
    )
    for field in ("generated_at", "rejected_at"):
        _invariant(
            is_aware_timestamp(value[field]),
            f"rejected target {field.removesuffix('_at')} timestamp is invalid",
        )
    _invariant(
        timestamp(value["generated_at"]) < timestamp(value["rejected_at"]),
        "rejected target does not follow generation",
    )
    plan = decision["reference_plan"]
    _invariant(
        value["plan_id"] == plan["plan_id"]
        and value["plan_revision"] == plan["revision"],
        "rejected target plan differs",
    )
    approved_slots = {row["reference_slot_id"] for row in plan["rows"]}
    _invariant(
        value["reference_slot_id"] in approved_slots,
        "rejected target slot is not approved",
    )
    return value


def validate_correction_approval(
    value: object, decision: dict[str, object], rejected_target: dict[str, object]
) -> dict[str, object]:
    _validate_rejected_authorization_input(rejected_target, decision)
    _schema(isinstance(value, dict) and set(value) == CORRECTION_APPROVAL_FIELDS, "correction approval fields differ")
    _invariant(value["schema_version"] == "visual-correction-approval/v1", "wrong correction approval schema")
    _invariant(value["decision"] == "approved", "correction is not approved")
    _invariant(value["reviewer_id"] != decision["builder_id"], "correction reviewer is the builder")
    _invariant(is_aware_timestamp(value["recorded_at"]), "correction timestamp is invalid")
    for field in ("approval_artifact_id", "reviewer_id", "reference_slot_id", "rejected_target_id", "correction_direction"):
        _text(value[field], f"correction {field}")
    _invariant(
        not _has_placeholder(value["correction_direction"]),
        "unresolved placeholder",
    )
    plan = decision["reference_plan"]
    _invariant(value["plan_id"] == plan["plan_id"] and value["plan_revision"] == plan["revision"], "correction plan differs")
    _invariant(value["reference_slot_id"] == rejected_target["reference_slot_id"], "correction slot differs")
    _invariant(value["rejected_target_id"] == rejected_target["target_id"], "correction target differs")
    _invariant(value["rejected_target_sha256"] == rejected_target["sha256"], "correction target binding drifted")
    _invariant(timestamp(value["recorded_at"]) > timestamp(rejected_target["rejected_at"]), "correction precedes rejection")
    return value


def validate_generation_authorization(value: object) -> dict[str, object]:
    _schema(isinstance(value, dict) and set(value) == AUTHORIZATION_FIELDS, "authorization fields differ")
    _invariant(value["schema_version"] == "visual-generation-authorization/v1", "wrong authorization schema")
    _invariant(value["status"] == "AUTHORIZED", "authorization status differs")
    _schema(
        isinstance(value["batch_kind"], str),
        "authorization batch kind must be text",
    )
    _invariant(value["batch_kind"] in {"initial", "delta", "correction"}, "authorization batch kind differs")
    for field in ("authorization_id", "issued_at", "decision_id", "plan_id", "approval_artifact_id"):
        _text(value[field], f"authorization {field}")
    _invariant(is_aware_timestamp(value["issued_at"]), "authorization timestamp is invalid")
    for field in ("decision_sha256", "plan_sha256", "approval_sha256"):
        _invariant(is_sha256(value[field]), f"authorization {field} is malformed")
    _invariant(isinstance(value["plan_revision"], int) and not isinstance(value["plan_revision"], bool) and value["plan_revision"] > 0, "authorization plan revision is invalid")
    _invariant(value["base_contract_id"] is None or isinstance(value["base_contract_id"], str) and bool(value["base_contract_id"].strip()), "authorization base contract is malformed")
    if value["batch_kind"] == "initial":
        _invariant(value["base_contract_id"] is None, "initial authorization has a base")
    elif value["batch_kind"] == "delta":
        _text(value["base_contract_id"], "delta authorization base contract")
    _schema(isinstance(value["supersedes_target_ids"], list), "authorization supersessions must be a list")
    _invariant(all(isinstance(item, str) and bool(item.strip()) for item in value["supersedes_target_ids"]) and len(value["supersedes_target_ids"]) == len(set(value["supersedes_target_ids"])), "authorization supersessions are malformed")
    if value["batch_kind"] == "correction":
        _text(value["rejected_target_id"], "authorization rejected target")
        _text(value["correction_approval_artifact_id"], "authorization correction approval")
    else:
        _invariant(value["rejected_target_id"] is None, "full authorization names a rejected target")
        _invariant(value["correction_approval_artifact_id"] is None, "full authorization names a correction approval")
    _schema(isinstance(value["authorized_slots"], list), "authorized_slots must be a list")
    _invariant(bool(value["authorized_slots"]), "authorized_slots is empty")
    seen: set[str] = set()
    for row in value["authorized_slots"]:
        _schema(isinstance(row, dict) and set(row) == AUTHORIZED_SLOT_FIELDS, "authorized slot fields differ")
        slot_id = _text(row["reference_slot_id"], "authorized slot id")
        _invariant(slot_id not in seen, "authorized slot ids are duplicate")
        seen.add(slot_id)
        _invariant(isinstance(row["result_budget"], int) and not isinstance(row["result_budget"], bool) and row["result_budget"] == 1, "authorized result budget must equal integer 1")
    return value


def build_generation_authorization(
    decision: dict[str, object], approval: dict[str, object], *,
    authorization_id: str, issued_at: str,
    rejected_target: dict[str, object] | None = None,
    correction: dict[str, object] | None = None,
) -> dict[str, object]:
    validate_visual_decision(decision)
    _invariant(not _has_placeholder(decision), "unresolved placeholder")
    plan = validate_reference_plan(decision["reference_plan"], allow_placeholders=False)
    validate_scope_approval(approval, decision)
    _text(authorization_id, "authorization id")
    _invariant(is_aware_timestamp(issued_at), "authorization timestamp is invalid")
    _schema((rejected_target is None) == (correction is None), "correction inputs must appear together")
    if rejected_target is None:
        batch_kind = "initial" if plan["kind"] == "initial" else "delta"
        slots = [row["reference_slot_id"] for row in plan["rows"]]
        rejected_id = None
        correction_id = None
        earliest = timestamp(approval["recorded_at"])
    else:
        validate_correction_approval(correction, decision, rejected_target)
        _invariant(
            authorization_id != rejected_target["authorization_id"],
            "correction authorization reuses rejected target authorization",
        )
        batch_kind = "correction"
        slots = [rejected_target["reference_slot_id"]]
        rejected_id = rejected_target["target_id"]
        correction_id = correction["approval_artifact_id"]
        earliest = timestamp(correction["recorded_at"])
    _invariant(timestamp(issued_at) > earliest, "authorization precedes approval")
    authorization = {
        "schema_version": "visual-generation-authorization/v1",
        "authorization_id": authorization_id,
        "status": "AUTHORIZED",
        "batch_kind": batch_kind,
        "issued_at": issued_at,
        "decision_id": decision["decision_id"],
        "decision_sha256": canonical_sha256(decision),
        "plan_id": plan["plan_id"],
        "plan_revision": plan["revision"],
        "plan_sha256": canonical_plan_sha256(plan),
        "approval_artifact_id": approval["approval_artifact_id"],
        "approval_sha256": canonical_sha256(approval),
        "authorized_slots": [{"reference_slot_id": slot_id, "result_budget": 1} for slot_id in slots],
        "base_contract_id": plan["base_contract_id"],
        "supersedes_target_ids": [row["supersedes_target_id"] for row in plan["rows"] if row["change_kind"] == "replace"],
        "rejected_target_id": rejected_id,
        "correction_approval_artifact_id": correction_id,
    }
    return validate_generation_authorization(authorization)

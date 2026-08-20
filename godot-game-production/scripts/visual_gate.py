"""Validate visual decisions and issue generation authorizations."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import visual_contract


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="visual_gate.py")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check-decision")
    check.add_argument("--decision", required=True)
    check.add_argument("--report", required=True)
    authorize = commands.add_parser("authorize-generation")
    authorize.add_argument("--decision", required=True)
    authorize.add_argument("--approval", required=True)
    authorize.add_argument("--authorization", required=True)
    authorize.add_argument("--rejected-target")
    authorize.add_argument("--correction-approval")
    return parser


def _atomic_json(path: Path, value: dict[str, object]) -> None:
    if path.exists():
        if not path.is_file():
            raise OSError("output is not a file")
        previous = visual_contract.loads_json(
            path.read_text(encoding="utf-8")
        )
        if previous != value:
            raise OSError("output binding differs")
        return
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


def _check_decision(args: argparse.Namespace) -> int:
    decision_path = Path(args.decision).resolve()
    report_path = Path(args.report).resolve()
    if (
        not decision_path.is_file()
        or report_path == decision_path
        or report_path.suffix.lower() != ".json"
    ):
        return 3
    try:
        parsed = visual_contract.loads_json(
            decision_path.read_text(encoding="utf-8")
        )
        decision = visual_contract.validate_visual_decision(parsed)
        _atomic_json(
            report_path, visual_contract.build_decision_report(decision)
        )
    except visual_contract.InvariantError:
        return 2
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        visual_contract.SchemaError,
    ):
        return 3
    return 0


def _load_json_file(path: Path) -> object:
    if not path.is_file():
        raise OSError("input is not a regular file")
    return visual_contract.loads_json(path.read_text(encoding="utf-8"))


def _authorize_generation(args: argparse.Namespace) -> int:
    decision_path = Path(args.decision).resolve()
    approval_path = Path(args.approval).resolve()
    authorization_path = Path(args.authorization).resolve()
    rejected_path = (
        Path(args.rejected_target).resolve()
        if args.rejected_target is not None else None
    )
    correction_path = (
        Path(args.correction_approval).resolve()
        if args.correction_approval is not None else None
    )
    if (
        authorization_path.suffix.lower() != ".json"
        or authorization_path in {
            decision_path, approval_path, rejected_path, correction_path,
        }
        or (rejected_path is None) != (correction_path is None)
    ):
        return 3
    try:
        decision = _load_json_file(decision_path)
        approval = _load_json_file(approval_path)
        rejected_target = (
            _load_json_file(rejected_path) if rejected_path is not None else None
        )
        correction = (
            _load_json_file(correction_path) if correction_path is not None else None
        )
        if authorization_path.exists():
            previous = visual_contract.validate_generation_authorization(
                _load_json_file(authorization_path)
            )
            authorization_id = previous["authorization_id"]
            issued_at = previous["issued_at"]
        else:
            authorization_id = f"vga-{uuid.uuid4()}"
            issued_at = datetime.now(timezone.utc).isoformat()
        authorization = visual_contract.build_generation_authorization(
            decision, approval,
            authorization_id=authorization_id,
            issued_at=issued_at,
            rejected_target=rejected_target,
            correction=correction,
        )
        _atomic_json(authorization_path, authorization)
    except visual_contract.InvariantError:
        return 2
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        visual_contract.SchemaError,
    ):
        return 3
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
    except SystemExit:
        return 3
    if args.command == "check-decision":
        return _check_decision(args)
    if args.command == "authorize-generation":
        return _authorize_generation(args)
    return 3


if __name__ == "__main__":
    sys.exit(main())

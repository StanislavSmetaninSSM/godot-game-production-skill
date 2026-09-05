import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "godot-game-production"


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def assert_contains_all(
    case: unittest.TestCase, text: str, required: tuple[str, ...]
) -> None:
    for value in required:
        case.assertIn(value, text, f"missing required contract text: {value}")


class ProductionOperationsContractTests(unittest.TestCase):
    def test_main_skill_routes_conditionally_and_owns_facts(self) -> None:
        text = read("godot-game-production/SKILL.md")
        assert_contains_all(
            self,
            text,
            (
                "Read `references/production-operations.md` when the current "
                "production interval",
                "has two or more implementation slices",
                "multiple agents or worktrees",
                "Do not read it merely for several serial steps",
                "exactly one authoritative owner",
                "must not infer, shadow, or independently write a competing version",
            ),
        )

    def test_operations_reference_defines_the_slice_contract(self) -> None:
        path = SKILL_ROOT / "references" / "production-operations.md"
        self.assertTrue(path.is_file(), "production operations reference is missing")
        text = path.read_text(encoding="utf-8")
        assert_contains_all(
            self,
            text,
            (
                "# Production Operations",
                "## Activation",
                "## Authoritative ownership",
                "## Slice contract",
                "`slice_id`",
                "`zone`",
                "`authoritative_owner`",
                "`player_visible_outcome`",
                "`baseline`",
                "`postcondition`",
                "`non_goals`",
                "`dependencies`",
                "`conflicts`",
                "`verification`",
                "`runtime_artifacts`",
                "`integration_target`",
                "No concurrent slices may change the same authoritative owner",
                "An individually passing slice is not a passing candidate",
                "Risk focus never replaces",
            ),
        )
        for forbidden in ("Orca", "model routing", "15%", "20%"):
            self.assertNotIn(forbidden, text)

    def test_gameplay_evidence_defines_diversity_and_fixture_limits(self) -> None:
        text = read("godot-game-production/references/gameplay-evidence.md")
        assert_contains_all(
            self,
            text,
            (
                "## Playtest matrix",
                "`scenario`",
                "`prior_state`",
                "`seed`",
                "`input`",
                "`expected_transition`",
                "`artifact`",
                "does not count as diversified coverage",
                "A fixture does not prove the complete player journey",
                "authoritative owner and zone",
            ),
        )

    def test_release_checks_reject_contaminated_performance_capture(self) -> None:
        text = read("godot-game-production/references/release-checks.md")
        assert_contains_all(
            self,
            text,
            (
                "## Controlled performance capture",
                "foreground and background load",
                "must not overlap when",
                "they can materially contend",
                "pre-existing processes require user confirmation",
                "Never terminate unrelated user processes",
                "`reliability_performance`",
                "`PENDING`",
                "cannot support a milestone or release pass",
            ),
        )

    def test_readme_mentions_conditional_operations(self) -> None:
        text = read("README.md")
        assert_contains_all(
            self,
            text,
            (
                "For concurrent production work",
                "`references/production-operations.md`",
                "one authoritative owner",
            ),
        )

    def test_existing_nonnegotiable_gates_remain(self) -> None:
        main = read("godot-game-production/SKILL.md")
        release = read("godot-game-production/references/release-checks.md")
        assert_contains_all(
            self,
            main,
            (
                "AUDIT -> SPECIFY -> VISUAL_PENDING -> VISUAL_APPROVED -> "
                "GODOT_FEASIBILITY ->\nCORE_LOOP -> PRODUCTION -> RELEASE",
                "present-target-question",
                "`test-driven-development`",
                "`requesting-code-review`",
                "`verification-before-completion`",
            ),
        )
        assert_contains_all(
            self,
            release,
            (
                "`core_play`",
                "`systems_holism`",
                "`content`",
                "`visual`",
                "`audio_feedback`",
                "`ux_onboarding`",
                "`reliability_performance`",
                "`ship`",
            ),
        )

    def test_every_routed_reference_exists(self) -> None:
        main = read("godot-game-production/SKILL.md")
        references = re.findall(r"`(references/[^`]+\.md)`", main)
        self.assertGreater(len(references), 0)
        for relative_path in references:
            self.assertTrue(
                (SKILL_ROOT / relative_path).is_file(),
                f"routed reference does not exist: {relative_path}",
            )

    def test_behavioral_catalog_contains_all_eight_cases(self) -> None:
        text = read("tests/behavioral/production-operations-cases.md")
        self.assertEqual(text.count("## OPS-"), 8)
        for number in range(1, 9):
            self.assertIn(f"## OPS-{number:02d}", text)


if __name__ == "__main__":
    unittest.main()

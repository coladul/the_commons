from __future__ import annotations

import argparse
import asyncio
import dataclasses
import hashlib
import importlib.metadata
import json
import os
import random
import re
import sys
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any, Literal

from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parent
MODEL = os.getenv("COMMONS_MODEL", "gpt-5.6-luna")

PILOT_SEED = 6020260815
PILOT_RUN_ORDER_SEED = 6020260816
PILOT_WORLD_COUNT = 5

EXPERIMENT_NAME = "The Commons v0.6 Source-Linkage Test"
PHASE = "five-world replacement engineering pilot"
FAILED_PILOT_ROOT = ROOT / "experiments" / "v0_6" / "pilot"
FAILED_PILOT_FILE_COUNT = 68
FAILED_PILOT_AGGREGATE_SHA256 = (
    "1386b24511a787e1f95571dc7f4a073bee7248b1a52a20e19aa00c40fdae93f8"
)
FAILED_EXECUTED_SCRIPT_PATH = (
    ROOT
    / "experiments"
    / "v0_6"
    / "history"
    / "the_commons_v0_6_failed_pilot_executed.py"
)
FAILED_EXECUTED_SCRIPT_SHA256 = (
    "1a4ea925d581a62984e6f8fde67bda4c7bea4c9f78d17d6d8fe17d0fe041d01e"
)

# All current preparation and future run writes are isolated from the immutable
# failed pilot at experiments/v0_6/pilot/.
ARTIFACT_ROOT = ROOT / "experiments" / "v0_6" / "replacement_pilot_01"
WORLDS_PATH = ARTIFACT_ROOT / "pilot_worlds.json"
PROMPTS_DIR = ARTIFACT_ROOT / "rendered_prompts"
RAW_OUTPUTS_DIR = ARTIFACT_ROOT / "raw_outputs"
VALIDATION_JSON_PATH = ARTIFACT_ROOT / "validation.json"
VALIDATION_MD_PATH = ARTIFACT_ROOT / "validation.md"
RUN_STATE_PATH = ARTIFACT_ROOT / "pilot_run_state.json"
RESULTS_PATH = ARTIFACT_ROOT / "pilot_results.json"
REPORT_PATH = ARTIFACT_ROOT / "pilot_report.md"

TEMP_DOMAIN = range(0, 41)
DENSITY_DOMAIN = range(0, 101)

CONDITION_ORDER = [
    "No Archive",
    "Correct Claim Only",
    "False Claim Only",
    "Full Reports - Provenance Masked",
    "Full Reports - Valid Provenance",
    "Full Reports - Shuffled Provenance",
]

CONDITION_CODES = {
    "No Archive": "no_archive",
    "Correct Claim Only": "correct_claim_only",
    "False Claim Only": "false_claim_only",
    "Full Reports - Provenance Masked": "masked",
    "Full Reports - Valid Provenance": "valid",
    "Full Reports - Shuffled Provenance": "shuffled",
}

CORE_CONDITIONS = [
    "Full Reports - Provenance Masked",
    "Full Reports - Valid Provenance",
    "Full Reports - Shuffled Provenance",
]

SOURCE_A = "SOURCE_A"
SOURCE_B = "SOURCE_B"
SOURCE_MASKED = "SOURCE_X"
SOURCE_IDS = (SOURCE_A, SOURCE_B)

TRUE_PACKET = "true_rule_report"
FALSE_PACKET = "false_rule_report"

Relation = Literal["<", "<=", ">", ">="]
Logic = Literal["AND", "OR"]
ArchiveAssessment = Literal["accepted", "revised", "rejected", "not_applicable"]


class ChildRevision(BaseModel):
    temperature_relation: Relation
    temperature_cutoff: int = Field(ge=-20, le=60)
    density_relation: Relation
    density_cutoff: int = Field(ge=-20, le=150)
    logic: Logic
    archive_assessment: ArchiveAssessment
    confidence: float = Field(ge=0.0, le=1.0)
    commons_claim: str = Field(
        description="A concise operational rule worth preserving for later researchers."
    )
    evidence_summary: str = Field(
        description="The material that most strongly supports the proposed rule."
    )
    rationale: str = Field(
        description="Why this rule is preferable to plausible alternatives."
    )


@dataclasses.dataclass(frozen=True)
class World:
    world_id: str
    max_hunt_temp: int
    min_hunt_density: int
    reliable_source: str
    weaker_source: str
    packet_order: tuple[str, str]

    @property
    def false_temp(self) -> int:
        return self.max_hunt_temp + 2

    @property
    def false_density(self) -> int:
        return self.min_hunt_density + 15

    def to_dict(self) -> dict[str, Any]:
        return {
            "world_id": self.world_id,
            "max_hunt_temp": self.max_hunt_temp,
            "min_hunt_density": self.min_hunt_density,
            "false_temp": self.false_temp,
            "false_density": self.false_density,
            "reliable_source": self.reliable_source,
            "weaker_source": self.weaker_source,
            "packet_order": list(self.packet_order),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "World":
        return cls(
            world_id=data["world_id"],
            max_hunt_temp=int(data["max_hunt_temp"]),
            min_hunt_density=int(data["min_hunt_density"]),
            reliable_source=data["reliable_source"],
            weaker_source=data["weaker_source"],
            packet_order=tuple(data["packet_order"]),
        )


@dataclasses.dataclass(frozen=True)
class Trial:
    trial_id: str
    world: World
    condition: str
    condition_code: str
    archive: str
    new_evidence: str
    system_instructions: str
    user_prompt: str


CHILD_INSTRUCTIONS = """
You are a field researcher studying a fictional Drel/Cassik interaction.

Methodologists have established that the hunting rule belongs to this hypothesis class:
- one comparison on temperature;
- one comparison on Drel density;
- joined by either AND or OR.

Allowed operators: <, <=, >, >=.

You may receive an earlier archive and you will receive new confirmed observations.
Archive source-report packets are reports made by sources; they are not guaranteed to be
ground truth and may conflict. Separate calibration records, when present, contain verified
outcomes from other cases and the reports those sources made on those cases. Evaluate the
archive rather than treating it as authority.

An ancestral claim, when present, is deliberately unattributed. Do not assume it was written
by either source merely because it appears near source reports.

Do not use real-world biology. Do not invent observations. Infer the best-supported
operational rule. Your output becomes a Commons entry for possible later research.
""".strip()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def directory_aggregate_sha256(path: Path) -> tuple[str, int]:
    """Hash file names, sizes, and contents without changing the directory."""
    aggregate = hashlib.sha256()
    files = sorted(
        (item for item in path.rglob("*") if item.is_file()),
        key=lambda item: item.relative_to(path).as_posix(),
    )
    for item in files:
        relative = item.relative_to(path).as_posix()
        # The frozen baseline used literal escaped separators. Keep that exact
        # representation so future checks remain comparable.
        record = f"{relative}\\0{item.stat().st_size}\\0{sha256_file(item)}\\n"
        aggregate.update(record.encode("utf-8"))
    return aggregate.hexdigest(), len(files)


def runtime_versions() -> dict[str, str]:
    packages = ["openai-agents", "openai", "pydantic", "tiktoken"]
    versions = {"python": sys.version.split()[0]}
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not installed"
    return versions


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def atomic_write_json(path: Path, data: Any) -> None:
    atomic_write_text(
        path,
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def truth(world: World, temperature: int, density: int) -> bool:
    return temperature <= world.max_hunt_temp and density >= world.min_hunt_density


def false_rule_value(world: World, temperature: int, density: int) -> bool:
    return temperature <= world.false_temp and density >= world.false_density


def correct_claim(world: World) -> str:
    return (
        f"Drel hunts Cassik when temperature is at most {world.max_hunt_temp}°C "
        f"AND drel_density is at least {world.min_hunt_density}; otherwise it does not hunt."
    )


def false_claim(world: World) -> str:
    return (
        f"Drel hunts Cassik when temperature is at most {world.false_temp}°C "
        f"AND drel_density is at least {world.false_density}; otherwise it does not hunt."
    )


def claim_block(claim: str) -> str:
    return f"""UNATTRIBUTED ANCESTRAL CLAIM
-----------------------------
Claim:
{claim}

Recorded confidence: 0.99

No author or source identity was retained for this claim."""


def new_rows(world: World) -> list[tuple[int, int, bool]]:
    t = world.max_hunt_temp
    d = world.min_hunt_density
    raw = [
        (t, d + 5),
        (t, max(0, d - 2)),
        (t + 1, min(100, d + 30)),
        (t - 1, d + 14),
        (t + 2, min(100, d + 40)),
        (t - 2, d + 10),
    ]
    return [(tt, dd, truth(world, tt, dd)) for tt, dd in raw]


def source_report_inputs(world: World) -> list[tuple[int, int]]:
    t = world.max_hunt_temp
    d = world.min_hunt_density
    return [
        (t, d),
        (t, max(0, d - 1)),
        (t + 1, d + 15),
        (t - 1, d + 14),
        (t + 2, d + 15),
        (t + 3, min(100, d + 30)),
        (max(0, t - 3), d + 20),
        (t, d + 15),
    ]


def source_report_rows(
    world: World,
    packet_kind: str,
) -> list[tuple[int, int, bool]]:
    rows = []
    for t, d in source_report_inputs(world):
        if packet_kind == TRUE_PACKET:
            reported = truth(world, t, d)
        elif packet_kind == FALSE_PACKET:
            reported = false_rule_value(world, t, d)
        else:
            raise ValueError(packet_kind)
        rows.append((t, d, reported))
    return rows


def rows_to_text(
    rows: list[tuple[int, int, bool]],
    outcome_header: str,
) -> str:
    lines = [f"temperature_c | drel_density | {outcome_header}"]
    for t, d, value in rows:
        lines.append(f"{t:<13} | {d:<12} | {'yes' if value else 'no'}")
    return "\n".join(lines)


def new_evidence_text(world: World) -> str:
    return rows_to_text(new_rows(world), "Cassik hunted?")


def calibration_rows(world: World) -> list[dict[str, str]]:
    verified = [True, False, True, False, True, False, True, False]
    reliable_reports = [True, False, True, False, True, False, True, True]
    weaker_reports = [True, True, False, False, False, True, False, False]

    rows = []
    for idx, expected in enumerate(verified):
        reports = {
            world.reliable_source: reliable_reports[idx],
            world.weaker_source: weaker_reports[idx],
        }
        rows.append(
            {
                "case": f"K{idx + 1:02d}",
                "verified": "yes" if expected else "no",
                SOURCE_A: "yes" if reports[SOURCE_A] else "no",
                SOURCE_B: "yes" if reports[SOURCE_B] else "no",
            }
        )
    return rows


def calibration_text(world: World) -> str:
    lines = [
        "case | independently verified outcome | SOURCE_A report | SOURCE_B report",
    ]
    for row in calibration_rows(world):
        lines.append(
            f"{row['case']:<4} | {row['verified']:<30} | "
            f"{row[SOURCE_A]:<15} | {row[SOURCE_B]}"
        )
    return "\n".join(lines)


def actual_source_for_packet(world: World, packet_kind: str) -> str:
    if packet_kind == TRUE_PACKET:
        return world.reliable_source
    if packet_kind == FALSE_PACKET:
        return world.weaker_source
    raise ValueError(packet_kind)


def opposite_source(source: str) -> str:
    if source == SOURCE_A:
        return SOURCE_B
    if source == SOURCE_B:
        return SOURCE_A
    raise ValueError(source)


def displayed_source_for_packet(
    world: World,
    packet_kind: str,
    condition: str,
) -> str:
    actual = actual_source_for_packet(world, packet_kind)
    if condition == "Full Reports - Valid Provenance":
        return actual
    if condition == "Full Reports - Provenance Masked":
        return SOURCE_MASKED
    if condition == "Full Reports - Shuffled Provenance":
        return opposite_source(actual)
    raise ValueError(condition)


def report_packet_text(
    world: World,
    packet_number: int,
    packet_kind: str,
    displayed_source: str,
) -> str:
    rows = source_report_rows(world, packet_kind)
    return f"""SOURCE REPORT PACKET {packet_number}
----------------------
Packet source ID: {displayed_source}

Reported outcomes:
{rows_to_text(rows, 'source-reported hunting?')}

These are outcomes reported by the named source, not independently verified observations."""


def full_archive(world: World, condition: str) -> str:
    packets = []
    for packet_number, packet_kind in enumerate(world.packet_order, start=1):
        packets.append(
            report_packet_text(
                world,
                packet_number,
                packet_kind,
                displayed_source_for_packet(world, packet_kind, condition),
            )
        )

    return "\n\n".join(
        [
            claim_block(false_claim(world)),
            """SOURCE CALIBRATION HISTORY
--------------------------
The outcomes in the verified column were independently checked on separate prior cases.
The source columns show what each source reported before the outcomes were verified.

""" + calibration_text(world),
            *packets,
        ]
    )


def archive_for(world: World, condition: str) -> str:
    if condition == "No Archive":
        return "No earlier archive material is available for this interaction."
    if condition == "Correct Claim Only":
        return claim_block(correct_claim(world))
    if condition == "False Claim Only":
        return claim_block(false_claim(world))
    if condition in CORE_CONDITIONS:
        return full_archive(world, condition)
    raise ValueError(condition)


def render_user_prompt(archive: str, new_evidence: str) -> str:
    return f"""EARLIER ARCHIVE
---------------
{archive}
---------------

NEW CONFIRMED OBSERVATIONS
--------------------------
{new_evidence}
--------------------------

Infer the best-supported rule and write the revised Commons entry.""".strip()


def render_full_prompt(system_instructions: str, user_prompt: str) -> str:
    return f"""===== SYSTEM INSTRUCTIONS =====
{system_instructions}

===== USER PROMPT =====
{user_prompt}
"""


def make_worlds() -> list[World]:
    rng = random.Random(PILOT_SEED)
    candidates = [
        (t, d)
        for t in range(12, 25)
        for d in range(15, 51, 5)
    ]
    rng.shuffle(candidates)

    worlds = []
    for idx, (t, d) in enumerate(candidates[:PILOT_WORLD_COUNT], start=1):
        reliable = SOURCE_A if idx % 2 == 1 else SOURCE_B
        weaker = opposite_source(reliable)
        # Packet position is counterbalanced independently of which source has
        # the stronger calibration history. Five worlds cannot be perfectly
        # balanced, but this pattern covers all four source/order combinations.
        true_packet_first = idx in {1, 2, 5}
        packet_order = (
            (TRUE_PACKET, FALSE_PACKET)
            if true_packet_first
            else (FALSE_PACKET, TRUE_PACKET)
        )
        worlds.append(
            World(
                world_id=f"P{idx:02d}",
                max_hunt_temp=t,
                min_hunt_density=d,
                reliable_source=reliable,
                weaker_source=weaker,
                packet_order=packet_order,
            )
        )
    return worlds


def build_trials(worlds: list[World]) -> list[Trial]:
    trials = []
    for world in worlds:
        new_evidence = new_evidence_text(world)
        for condition_index, condition in enumerate(CONDITION_ORDER, start=1):
            archive = archive_for(world, condition)
            user_prompt = render_user_prompt(archive, new_evidence)
            trials.append(
                Trial(
                    trial_id=f"{world.world_id}_C{condition_index}",
                    world=world,
                    condition=condition,
                    condition_code=CONDITION_CODES[condition],
                    archive=archive,
                    new_evidence=new_evidence,
                    system_instructions=CHILD_INSTRUCTIONS,
                    user_prompt=user_prompt,
                )
            )
    return trials


def trial_filename(trial: Trial) -> str:
    return f"{trial.trial_id}_{trial.condition_code}.txt"


def freeze_worlds(worlds: list[World], trials: list[Trial]) -> dict[str, Any]:
    run_order = [trial.trial_id for trial in trials]
    random.Random(PILOT_RUN_ORDER_SEED).shuffle(run_order)
    frozen = {
        "experiment": EXPERIMENT_NAME,
        "phase": PHASE,
        "artifact_namespace": str(ARTIFACT_ROOT.relative_to(ROOT)),
        "replacement_for_failed_pilot": str(FAILED_PILOT_ROOT.relative_to(ROOT)),
        "failed_pilot_aggregate_sha256": FAILED_PILOT_AGGREGATE_SHA256,
        "created_at": utc_now(),
        "pilot_seed": PILOT_SEED,
        "run_order_seed": PILOT_RUN_ORDER_SEED,
        "model": MODEL,
        "model_settings": {
            "temperature": "SDK/model default (not explicitly set)",
            "max_turns": 1,
            "session": None,
            "structured_output": "ChildRevision",
        },
        "runtime_versions": runtime_versions(),
        "world_count": len(worlds),
        "condition_count": len(CONDITION_ORDER),
        "authorized_api_calls": len(trials),
        "generation_count": 1,
        "conditions": CONDITION_ORDER,
        "core_conditions": CORE_CONDITIONS,
        "worlds": [world.to_dict() for world in worlds],
        "run_order": run_order,
        "script_sha256": sha256_file(Path(__file__)),
    }

    if WORLDS_PATH.exists():
        existing = load_json(WORLDS_PATH)
        stable_keys = [
            "pilot_seed",
            "run_order_seed",
            "model",
            "model_settings",
            "runtime_versions",
            "world_count",
            "condition_count",
            "authorized_api_calls",
            "generation_count",
            "conditions",
            "core_conditions",
            "artifact_namespace",
            "replacement_for_failed_pilot",
            "failed_pilot_aggregate_sha256",
            "worlds",
            "run_order",
        ]
        mismatches = [key for key in stable_keys if existing.get(key) != frozen.get(key)]
        if mismatches:
            api_activity_exists = RUN_STATE_PATH.exists() or any(
                RAW_OUTPUTS_DIR.glob("*.json")
            )
            if api_activity_exists:
                raise RuntimeError(
                    "Existing frozen pilot worlds disagree with the current design after API activity: "
                    + ", ".join(mismatches)
                )
            # Preparation is allowed to repair a failed pre-API freeze. Once a
            # run-state or raw-output file exists, the frozen worlds are locked.
            atomic_write_json(WORLDS_PATH, frozen)
            return frozen
        existing["script_sha256"] = frozen["script_sha256"]
        atomic_write_json(WORLDS_PATH, existing)
        return existing

    atomic_write_json(WORLDS_PATH, frozen)
    return frozen


LINKAGE_LINE_RE = re.compile(r"^Packet source ID: SOURCE_[ABX]$", re.MULTILINE)


def linkage_values(prompt: str) -> list[str]:
    return [line.rsplit(" ", 1)[-1] for line in LINKAGE_LINE_RE.findall(prompt)]


def canonicalize_linkage(prompt: str) -> str:
    return LINKAGE_LINE_RE.sub("Packet source ID: SOURCE_*", prompt)


def whitespace_token_count(text: str) -> int:
    return len(text.split())


def validate_historical_files() -> dict[str, Any]:
    manifest_path = ROOT / "MANIFEST.sha256"
    wanted = {
        "the_commons.py",
        "the_commons_v0_2.py",
        "the_commons_v0_3.py",
        "the_commons_v0_4.py",
        "the_commons_v0_5.py",
    }
    expected = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([0-9a-f]{64})\s+\./(.+)$", line)
        if match and match.group(2) in wanted:
            expected[match.group(2)] = match.group(1)

    rows = []
    for name in sorted(wanted):
        actual = sha256_file(ROOT / name)
        rows.append(
            {
                "file": name,
                "expected_sha256": expected.get(name),
                "actual_sha256": actual,
                "pass": expected.get(name) == actual,
            }
        )
    return {"pass": all(row["pass"] for row in rows), "files": rows}


def validate_failed_pilot_immutable() -> dict[str, Any]:
    if not FAILED_PILOT_ROOT.is_dir():
        return {
            "pass": False,
            "artifact_root": str(FAILED_PILOT_ROOT.relative_to(ROOT)),
            "error": "Failed-pilot artifact directory is missing.",
        }

    aggregate, file_count = directory_aggregate_sha256(FAILED_PILOT_ROOT)
    copied_script_exists = FAILED_EXECUTED_SCRIPT_PATH.is_file()
    copied_script_sha256 = (
        sha256_file(FAILED_EXECUTED_SCRIPT_PATH) if copied_script_exists else None
    )
    checks = {
        "artifact_file_count_unchanged": file_count == FAILED_PILOT_FILE_COUNT,
        "artifact_aggregate_sha256_unchanged": (
            aggregate == FAILED_PILOT_AGGREGATE_SHA256
        ),
        "executed_script_copy_exists": copied_script_exists,
        "executed_script_copy_matches": (
            copied_script_sha256 == FAILED_EXECUTED_SCRIPT_SHA256
        ),
        "replacement_namespace_is_distinct": (
            ARTIFACT_ROOT.resolve() != FAILED_PILOT_ROOT.resolve()
        ),
    }
    return {
        "pass": all(checks.values()),
        "artifact_root": str(FAILED_PILOT_ROOT.relative_to(ROOT)),
        "expected_file_count": FAILED_PILOT_FILE_COUNT,
        "actual_file_count": file_count,
        "expected_aggregate_sha256": FAILED_PILOT_AGGREGATE_SHA256,
        "actual_aggregate_sha256": aggregate,
        "executed_script_copy": str(FAILED_EXECUTED_SCRIPT_PATH.relative_to(ROOT)),
        "expected_executed_script_sha256": FAILED_EXECUTED_SCRIPT_SHA256,
        "actual_executed_script_sha256": copied_script_sha256,
        "checks": checks,
    }


def validate_world(world: World) -> dict[str, Any]:
    calibration = calibration_rows(world)
    reliable_correct = sum(
        row[world.reliable_source] == row["verified"] for row in calibration
    )
    weaker_correct = sum(
        row[world.weaker_source] == row["verified"] for row in calibration
    )
    true_inputs = [(t, d) for t, d, _ in source_report_rows(world, TRUE_PACKET)]
    false_inputs = [(t, d) for t, d, _ in source_report_rows(world, FALSE_PACKET)]
    report_disagreements = sum(
        a[2] != b[2]
        for a, b in zip(
            source_report_rows(world, TRUE_PACKET),
            source_report_rows(world, FALSE_PACKET),
        )
    )
    checks = {
        "source_ids_distinct": world.reliable_source != world.weaker_source,
        "sources_valid": set((world.reliable_source, world.weaker_source)) == set(SOURCE_IDS),
        "packet_kinds_once_each": set(world.packet_order) == {TRUE_PACKET, FALSE_PACKET},
        "matched_report_inputs": true_inputs == false_inputs,
        "eight_rows_per_report": len(true_inputs) == len(false_inputs) == 8,
        "reports_conflict_on_diagnostic_rows": report_disagreements >= 3,
        "reliable_calibration_score": reliable_correct == 7,
        "weaker_calibration_score": weaker_correct == 3,
        "new_evidence_has_six_rows": len(new_rows(world)) == 6,
    }
    return {
        "world_id": world.world_id,
        "pass": all(checks.values()),
        "checks": checks,
        "reliable_source": world.reliable_source,
        "weaker_source": world.weaker_source,
        "reliable_calibration_correct": reliable_correct,
        "weaker_calibration_correct": weaker_correct,
        "report_disagreements": report_disagreements,
        "packet_order": list(world.packet_order),
    }


def validate_core_prompts(world: World, trials_by_key: dict[tuple[str, str], Trial]) -> dict[str, Any]:
    core = {
        condition: trials_by_key[(world.world_id, condition)]
        for condition in CORE_CONDITIONS
    }
    prompts = {condition: trial.user_prompt for condition, trial in core.items()}
    archives = {condition: trial.archive for condition, trial in core.items()}

    canonical = {condition: canonicalize_linkage(prompt) for condition, prompt in prompts.items()}
    lengths = {condition: len(prompt) for condition, prompt in prompts.items()}
    byte_lengths = {condition: len(prompt.encode("utf-8")) for condition, prompt in prompts.items()}
    whitespace_counts = {
        condition: whitespace_token_count(prompt) for condition, prompt in prompts.items()
    }
    source_lines = {condition: linkage_values(prompt) for condition, prompt in prompts.items()}

    valid_expected = [
        actual_source_for_packet(world, packet_kind) for packet_kind in world.packet_order
    ]
    shuffled_expected = [opposite_source(source) for source in valid_expected]
    masked_expected = [SOURCE_MASKED, SOURCE_MASKED]

    claim = claim_block(false_claim(world))
    calibration = calibration_text(world)
    report_payloads = {
        packet_kind: rows_to_text(
            source_report_rows(world, packet_kind),
            "source-reported hunting?",
        )
        for packet_kind in (TRUE_PACKET, FALSE_PACKET)
    }

    checks = {
        "canonical_prompts_identical": len(set(canonical.values())) == 1,
        "character_lengths_identical": len(set(lengths.values())) == 1,
        "byte_lengths_identical": len(set(byte_lengths.values())) == 1,
        "whitespace_token_counts_identical": len(set(whitespace_counts.values())) == 1,
        "exactly_two_linkage_fields_each": all(len(values) == 2 for values in source_lines.values()),
        "masked_mapping_expected": source_lines[
            "Full Reports - Provenance Masked"
        ] == masked_expected,
        "valid_mapping_expected": source_lines[
            "Full Reports - Valid Provenance"
        ] == valid_expected,
        "shuffled_mapping_expected": source_lines[
            "Full Reports - Shuffled Provenance"
        ] == shuffled_expected,
        "false_claim_identical_and_once": all(
            archive.count(claim) == 1 for archive in archives.values()
        ),
        "false_claim_unattributed": all(
            "No author or source identity was retained for this claim." in archive
            for archive in archives.values()
        ),
        "calibration_identical_and_once": all(
            archive.count(calibration) == 1 for archive in archives.values()
        ),
        "report_payloads_identical_and_once": all(
            all(archive.count(payload) == 1 for payload in report_payloads.values())
            for archive in archives.values()
        ),
        "new_evidence_identical": len(
            {trial.new_evidence for trial in core.values()}
        ) == 1,
        "system_instructions_identical": len(
            {trial.system_instructions for trial in core.values()}
        ) == 1,
        "condition_names_absent_from_prompts": all(
            condition not in trial.user_prompt for condition, trial in core.items()
        ),
    }

    return {
        "world_id": world.world_id,
        "pass": all(checks.values()),
        "checks": checks,
        "prompt_sha256": {
            condition: sha256_text(prompt) for condition, prompt in prompts.items()
        },
        "canonical_prompt_sha256": sha256_text(next(iter(canonical.values()))),
        "false_claim_block_sha256": sha256_text(claim),
        "calibration_table_sha256": sha256_text(calibration),
        "report_payload_sha256": {
            kind: sha256_text(payload) for kind, payload in report_payloads.items()
        },
        "new_evidence_sha256": sha256_text(next(iter(core.values())).new_evidence),
        "character_lengths": lengths,
        "byte_lengths": byte_lengths,
        "whitespace_token_counts": whitespace_counts,
        "displayed_source_lines": source_lines,
        "expected_valid_mapping": valid_expected,
        "expected_shuffled_mapping": shuffled_expected,
    }


def optional_tiktoken_counts(trials: list[Trial]) -> dict[str, Any]:
    try:
        import tiktoken  # type: ignore
    except ImportError:
        return {
            "available": False,
            "pass": None,
            "note": "tiktoken is not installed; exact character, byte, and whitespace-token equality were checked.",
        }

    try:
        try:
            encoding = tiktoken.encoding_for_model(MODEL)
            encoding_name = getattr(encoding, "name", "model-default")
        except KeyError:
            encoding = tiktoken.get_encoding("o200k_base")
            encoding_name = "o200k_base fallback"

        by_world = {}
        trials_by_key = {(t.world.world_id, t.condition): t for t in trials}
        all_pass = True
        for world_id in sorted({t.world.world_id for t in trials}):
            counts = {
                condition: len(
                    encoding.encode(trials_by_key[(world_id, condition)].user_prompt)
                )
                for condition in CORE_CONDITIONS
            }
            passed = len(set(counts.values())) == 1
            all_pass = all_pass and passed
            by_world[world_id] = {"counts": counts, "pass": passed}
        return {
            "available": True,
            "encoding": encoding_name,
            "pass": all_pass,
            "by_world": by_world,
        }
    except Exception as exc:
        return {
            "available": True,
            "pass": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def run_validation(worlds: list[World], trials: list[Trial], frozen: dict[str, Any]) -> dict[str, Any]:
    trials_by_key = {(trial.world.world_id, trial.condition): trial for trial in trials}
    historical = validate_historical_files()
    failed_pilot = validate_failed_pilot_immutable()
    world_checks = [validate_world(world) for world in worlds]
    prompt_checks = [validate_core_prompts(world, trials_by_key) for world in worlds]
    tokenizer = optional_tiktoken_counts(trials)

    reliable_counts = Counter(world.reliable_source for world in worlds)
    true_first = sum(world.packet_order[0] == TRUE_PACKET for world in worlds)
    false_first = len(worlds) - true_first
    source_order_combinations = {
        (world.reliable_source, world.packet_order[0]) for world in worlds
    }
    valid_first_source_counts = Counter(
        actual_source_for_packet(world, world.packet_order[0]) for world in worlds
    )
    balance_checks = {
        "reliable_source_counterbalanced": abs(
            reliable_counts[SOURCE_A] - reliable_counts[SOURCE_B]
        ) <= 1,
        "packet_order_counterbalanced": abs(true_first - false_first) <= 1,
        "all_source_order_combinations_covered": len(source_order_combinations) == 4,
        "valid_first_source_counterbalanced": abs(
            valid_first_source_counts[SOURCE_A]
            - valid_first_source_counts[SOURCE_B]
        ) <= 1,
    }

    prompt_files = list(PROMPTS_DIR.glob("*.txt")) if PROMPTS_DIR.exists() else []
    artifact_checks = {
        "world_file_exists": WORLDS_PATH.exists(),
        "world_file_authorizes_30_calls": frozen.get("authorized_api_calls") == 30,
        "world_file_generation_count_one": frozen.get("generation_count") == 1,
        "thirty_trials_built": len(trials) == 30,
        "thirty_rendered_prompt_files": len(prompt_files) == 30,
        "run_order_has_each_trial_once": (
            len(frozen.get("run_order", [])) == 30
            and set(frozen.get("run_order", [])) == {trial.trial_id for trial in trials}
        ),
    }

    mandatory_groups_pass = all(
        [
            historical["pass"],
            failed_pilot["pass"],
            all(row["pass"] for row in world_checks),
            all(row["pass"] for row in prompt_checks),
            all(balance_checks.values()),
            all(artifact_checks.values()),
        ]
    )
    tokenizer_gate_pass = tokenizer.get("pass") is not False
    overall_pass = mandatory_groups_pass and tokenizer_gate_pass

    return {
        "experiment": EXPERIMENT_NAME,
        "phase": PHASE,
        "artifact_namespace": str(ARTIFACT_ROOT.relative_to(ROOT)),
        "validated_at": utc_now(),
        "overall_pass": overall_pass,
        "historical_v0_1_to_v0_5": historical,
        "failed_pilot_immutability": failed_pilot,
        "world_checks": world_checks,
        "core_prompt_checks": prompt_checks,
        "counterbalancing": {
            "pass": all(balance_checks.values()),
            "checks": balance_checks,
            "reliable_source_counts": dict(reliable_counts),
            "valid_first_source_counts": dict(valid_first_source_counts),
            "source_order_combinations": [
                list(item) for item in sorted(source_order_combinations)
            ],
            "true_packet_first": true_first,
            "false_packet_first": false_first,
        },
        "artifact_checks": {
            "pass": all(artifact_checks.values()),
            "checks": artifact_checks,
        },
        "tokenizer_check": tokenizer,
        "script_sha256_at_validation": sha256_file(Path(__file__)),
        "frozen_worlds_sha256": sha256_file(WORLDS_PATH),
    }


def validation_markdown(validation: dict[str, Any]) -> str:
    lines = [
        "# The Commons v0.6 pilot validation",
        "",
        f"- Overall result: **{'PASS' if validation['overall_pass'] else 'FAIL'}**",
        f"- Validated at: `{validation['validated_at']}`",
        f"- Historical v0.1–v0.5 hashes: **{'PASS' if validation['historical_v0_1_to_v0_5']['pass'] else 'FAIL'}**",
        f"- Failed pilot immutability: **{'PASS' if validation['failed_pilot_immutability']['pass'] else 'FAIL'}**",
        f"- Replacement namespace: `{validation['artifact_namespace']}`",
        f"- World-generator checks: **{'PASS' if all(x['pass'] for x in validation['world_checks']) else 'FAIL'}**",
        f"- Core prompt matching: **{'PASS' if all(x['pass'] for x in validation['core_prompt_checks']) else 'FAIL'}**",
        f"- Counterbalancing: **{'PASS' if validation['counterbalancing']['pass'] else 'FAIL'}**",
        f"- Frozen artifacts: **{'PASS' if validation['artifact_checks']['pass'] else 'FAIL'}**",
        "",
        "## Core prompt invariants",
        "",
        "| World | Canonical match | Same chars/bytes | Same whitespace tokens | Claim identical/unattributed | Correct mappings |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in validation["core_prompt_checks"]:
        c = row["checks"]
        lines.append(
            f"| {row['world_id']} | "
            f"{'yes' if c['canonical_prompts_identical'] else 'no'} | "
            f"{'yes' if c['character_lengths_identical'] and c['byte_lengths_identical'] else 'no'} | "
            f"{'yes' if c['whitespace_token_counts_identical'] else 'no'} | "
            f"{'yes' if c['false_claim_identical_and_once'] and c['false_claim_unattributed'] else 'no'} | "
            f"{'yes' if c['masked_mapping_expected'] and c['valid_mapping_expected'] and c['shuffled_mapping_expected'] else 'no'} |"
        )

    tokenizer = validation["tokenizer_check"]
    lines += [
        "",
        "## Tokenizer check",
        "",
        f"- Available: `{tokenizer.get('available')}`",
        f"- Result: `{tokenizer.get('pass')}`",
    ]
    if tokenizer.get("note"):
        lines.append(f"- Note: {tokenizer['note']}")
    if tokenizer.get("encoding"):
        lines.append(f"- Encoding: `{tokenizer['encoding']}`")

    lines += [
        "",
        "## Counterbalancing",
        "",
        f"- Reliable source counts: `{validation['counterbalancing']['reliable_source_counts']}`",
        f"- True-report packet first: `{validation['counterbalancing']['true_packet_first']}`",
        f"- False-report packet first: `{validation['counterbalancing']['false_packet_first']}`",
        "",
        "The pilot run command refuses to make API calls unless this validation passes.",
        "",
    ]
    return "\n".join(lines)


def prepare_pilot() -> dict[str, Any]:
    worlds = make_worlds()
    trials = build_trials(worlds)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    frozen = freeze_worlds(worlds, trials)

    for trial in trials:
        atomic_write_text(
            PROMPTS_DIR / trial_filename(trial),
            render_full_prompt(trial.system_instructions, trial.user_prompt),
        )

    validation = run_validation(worlds, trials, frozen)
    atomic_write_json(VALIDATION_JSON_PATH, validation)
    atomic_write_text(VALIDATION_MD_PATH, validation_markdown(validation))
    return validation


def load_frozen_worlds() -> tuple[dict[str, Any], list[World]]:
    if not WORLDS_PATH.exists():
        raise RuntimeError("Pilot worlds are not frozen. Run `prepare` first.")
    frozen = load_json(WORLDS_PATH)
    worlds = [World.from_dict(data) for data in frozen["worlds"]]
    return frozen, worlds


def compare(value: int, relation: str, cutoff: int) -> bool:
    if relation == "<":
        return value < cutoff
    if relation == "<=":
        return value <= cutoff
    if relation == ">":
        return value > cutoff
    if relation == ">=":
        return value >= cutoff
    raise ValueError(relation)


def apply_child_rule(rule: ChildRevision, temperature: int, density: int) -> bool:
    t_ok = compare(temperature, rule.temperature_relation, rule.temperature_cutoff)
    d_ok = compare(density, rule.density_relation, rule.density_cutoff)
    return (t_ok and d_ok) if rule.logic == "AND" else (t_ok or d_ok)


def full_domain_score(world: World, rule: ChildRevision) -> tuple[int, int]:
    correct = 0
    total = 0
    for t in TEMP_DOMAIN:
        for d in DENSITY_DOMAIN:
            total += 1
            correct += int(apply_child_rule(rule, t, d) == truth(world, t, d))
    return correct, total


def formal_rule(rule: ChildRevision) -> str:
    return (
        f"temperature {rule.temperature_relation} {rule.temperature_cutoff} "
        f"{rule.logic} drel_density {rule.density_relation} {rule.density_cutoff}"
    )


def to_jsonable(value: Any, depth: int = 0) -> Any:
    if depth > 20:
        return safe_repr(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    # Pydantic model classes expose BaseModel.model_dump as an unbound method.
    # They must never be treated as model instances (the failed pilot's exact
    # failure mode for ChildRevision inside an SDK item).
    if isinstance(value, type):
        return {
            "__kind__": "python_class",
            "module": getattr(value, "__module__", None),
            "qualname": getattr(value, "__qualname__", getattr(value, "__name__", None)),
        }
    if isinstance(value, BaseModel):
        return to_jsonable(value.model_dump(mode="json"), depth + 1)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: to_jsonable(getattr(value, field.name), depth + 1)
            for field in dataclasses.fields(value)
        }
    if isinstance(value, dict):
        return {str(k): to_jsonable(v, depth + 1) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(v, depth + 1) for v in value]
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        try:
            return to_jsonable(model_dump(mode="json"), depth + 1)
        except TypeError:
            return to_jsonable(model_dump(), depth + 1)
    if hasattr(value, "__dict__"):
        return {
            str(k): to_jsonable(v, depth + 1)
            for k, v in vars(value).items()
            if not str(k).startswith("_")
        }
    return safe_repr(value)


def safe_repr(value: Any) -> str:
    try:
        return repr(value)
    except Exception as exc:
        return f"<repr failed: {type(exc).__name__}: {exc}>"


def core_usage_dict(usage: Any) -> dict[str, int]:
    return {
        "requests": int(getattr(usage, "requests", 0) or 0),
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
        "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
    }


def serialize_optional_value(label: str, value: Any) -> tuple[Any, dict[str, str] | None]:
    try:
        return to_jsonable(value), None
    except Exception as exc:
        error = {
            "field": label,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        return {
            "__serialization_failed__": True,
            **error,
            "repr": safe_repr(value),
        }, error


def response_id_from_result(result: Any) -> str | None:
    try:
        response_id = getattr(result, "last_response_id", None)
        if response_id:
            return str(response_id)
    except Exception:
        pass

    try:
        raw_responses = getattr(result, "raw_responses", None) or []
        if raw_responses:
            response_id = getattr(raw_responses[-1], "response_id", None)
            if response_id:
                return str(response_id)
    except Exception:
        pass
    return None


def commit_successful_trial_record(
    output_path: Path,
    raw_record: dict[str, Any],
    trial: Trial,
    revision: ChildRevision,
    usage: Any,
    result: Any,
) -> tuple[int, int, list[dict[str, str]]]:
    """Persist scored scientific data before attempting SDK-object serialization."""
    correct, possible = full_domain_score(trial.world, revision)
    raw_record.update(
        {
            "finished_at": utc_now(),
            "status": "parsed",
            "response_id": response_id_from_result(result),
            "final_output": revision.model_dump(mode="json"),
            "formal_rule": formal_rule(revision),
            "commons_claim": revision.commons_claim,
            "evidence_summary": revision.evidence_summary,
            "rationale": revision.rationale,
            "full_domain_correct": correct,
            "full_domain_possible": possible,
            "full_domain_accuracy": correct / possible,
            "semantic_equivalent": correct == possible,
            "usage": core_usage_dict(usage),
            "essential_record_committed": True,
        }
    )

    # This first atomic commit is intentionally before any optional SDK internals.
    atomic_write_json(output_path, raw_record)

    optional_errors: list[dict[str, str]] = []
    optional_values: list[tuple[str, Any]] = [("usage_details", usage)]
    for field_name in ("raw_responses", "new_items", "last_agent"):
        try:
            value = getattr(result, field_name, None)
        except Exception as exc:
            error = {
                "field": field_name,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            raw_record[field_name] = {"__attribute_access_failed__": True, **error}
            optional_errors.append(error)
        else:
            optional_values.append((field_name, value))

    for field_name, value in optional_values:
        serialized, error = serialize_optional_value(field_name, value)
        raw_record[field_name] = serialized
        if error is not None:
            optional_errors.append(error)

    raw_record["optional_serialization_errors"] = optional_errors
    raw_record["optional_serialization_complete"] = not optional_errors
    atomic_write_json(output_path, raw_record)
    return correct, possible, optional_errors


def raw_path_for_trial(trial: Trial) -> Path:
    return RAW_OUTPUTS_DIR / f"{trial.trial_id}_{trial.condition_code}.json"


def initial_run_state(frozen: dict[str, Any]) -> dict[str, Any]:
    return {
        "experiment": frozen["experiment"],
        "phase": frozen["phase"],
        "model": frozen["model"],
        "authorized_api_calls": frozen["authorized_api_calls"],
        "started_at": utc_now(),
        "completed_at": None,
        "status": "running",
        "attempted_calls": [],
    }


def validate_run_gate(frozen: dict[str, Any], worlds: list[World], trials: list[Trial]) -> dict[str, Any]:
    if MODEL != frozen["model"]:
        raise RuntimeError(
            f"Frozen model is {frozen['model']!r}, but COMMONS_MODEL resolves to {MODEL!r}."
        )
    if frozen["authorized_api_calls"] != 30 or len(trials) != 30:
        raise RuntimeError("The pilot authorization must be exactly 30 logical model calls.")
    if frozen.get("generation_count") != 1:
        raise RuntimeError("The pilot must contain Generation Two only.")
    if frozen.get("script_sha256") != sha256_file(Path(__file__)):
        raise RuntimeError(
            "The v0.6 script changed after pilot preparation. Run `prepare` again before any API call."
        )

    validation = run_validation(worlds, trials, frozen)
    atomic_write_json(VALIDATION_JSON_PATH, validation)
    atomic_write_text(VALIDATION_MD_PATH, validation_markdown(validation))
    if not validation["overall_pass"]:
        raise RuntimeError("Pre-API validation failed. No API calls will be made.")
    return validation


async def call_trial(trial: Trial) -> tuple[ChildRevision, Any, Any]:
    try:
        from agents import Agent, Runner
    except ImportError as exc:
        raise RuntimeError(
            "The `openai-agents` dependency is not installed in this Python environment."
        ) from exc

    agent = Agent(
        name="Generation Two Source-Linkage Researcher",
        model=MODEL,
        output_type=ChildRevision,
        instructions=trial.system_instructions,
    )
    result = await Runner.run(agent, trial.user_prompt, max_turns=1)
    revision = result.final_output
    if not isinstance(revision, ChildRevision):
        raise TypeError(f"Unexpected output type: {type(revision).__name__}")
    return revision, result.context_wrapper.usage, result


async def run_pilot() -> None:
    frozen, worlds = load_frozen_worlds()
    trials = build_trials(worlds)
    trials_by_id = {trial.trial_id: trial for trial in trials}
    validate_run_gate(frozen, worlds, trials)

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Frozen worlds, prompts, and validation are saved; no API calls were made."
        )

    RAW_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if RUN_STATE_PATH.exists():
        state = load_json(RUN_STATE_PATH)
        if state.get("status") == "complete":
            print("The frozen pilot is already complete; no API calls were made.")
            write_pilot_results(frozen, worlds, trials)
            return
    else:
        state = initial_run_state(frozen)
        atomic_write_json(RUN_STATE_PATH, state)

    attempted_ids = {row["trial_id"] for row in state["attempted_calls"]}
    authorized = int(state["authorized_api_calls"])

    for position, trial_id in enumerate(frozen["run_order"], start=1):
        trial = trials_by_id[trial_id]
        if trial_id in attempted_ids:
            continue
        if len(state["attempted_calls"]) >= authorized:
            break

        attempt = {
            "trial_id": trial_id,
            "world_id": trial.world.world_id,
            "condition": trial.condition,
            "position": position,
            "started_at": utc_now(),
            "finished_at": None,
            "status": "started",
            "raw_output_path": str(raw_path_for_trial(trial).relative_to(ROOT)),
        }
        state["attempted_calls"].append(attempt)
        atomic_write_json(RUN_STATE_PATH, state)

        print(f"[{len(state['attempted_calls'])}/{authorized}] {trial_id} / {trial.world.world_id}")
        raw_record: dict[str, Any] = {
            "experiment": frozen["experiment"],
            "phase": frozen["phase"],
            "trial_id": trial.trial_id,
            "world": trial.world.to_dict(),
            "condition": trial.condition,
            "condition_code": trial.condition_code,
            "model": MODEL,
            "system_instructions": trial.system_instructions,
            "user_prompt": trial.user_prompt,
            "rendered_prompt_sha256": sha256_text(
                render_full_prompt(trial.system_instructions, trial.user_prompt)
            ),
            "started_at": attempt["started_at"],
        }

        try:
            revision, usage, result = await call_trial(trial)
            _, _, optional_errors = commit_successful_trial_record(
                raw_path_for_trial(trial),
                raw_record,
                trial,
                revision,
                usage,
                result,
            )
            attempt["status"] = "parsed"
            attempt["optional_serialization_error_count"] = len(optional_errors)
        except Exception as exc:
            raw_record.update(
                {
                    "finished_at": utc_now(),
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                }
            )
            attempt["status"] = "error"
            attempt["error_type"] = type(exc).__name__
            attempt["error"] = str(exc)

        attempt["finished_at"] = raw_record["finished_at"]
        atomic_write_json(raw_path_for_trial(trial), raw_record)
        atomic_write_json(RUN_STATE_PATH, state)

    state["completed_at"] = utc_now()
    state["status"] = (
        "complete" if len(state["attempted_calls"]) == authorized else "incomplete"
    )
    atomic_write_json(RUN_STATE_PATH, state)
    write_pilot_results(frozen, worlds, trials)


def load_raw_records(trials: list[Trial]) -> list[dict[str, Any]]:
    records = []
    for trial in trials:
        path = raw_path_for_trial(trial)
        if path.exists():
            records.append(load_json(path))
    return records


def paired_differences(
    parsed_by_key: dict[tuple[str, str], dict[str, Any]],
    worlds: list[World],
    condition_a: str,
    condition_b: str,
) -> dict[str, Any]:
    diffs = []
    semantic_diffs = []
    missing = []
    for world in worlds:
        a = parsed_by_key.get((world.world_id, condition_a))
        b = parsed_by_key.get((world.world_id, condition_b))
        if not a or not b:
            missing.append(world.world_id)
            continue
        diffs.append(a["full_domain_accuracy"] - b["full_domain_accuracy"])
        semantic_diffs.append(
            int(a["semantic_equivalent"]) - int(b["semantic_equivalent"])
        )
    return {
        "condition_a": condition_a,
        "condition_b": condition_b,
        "n_paired_worlds": len(diffs),
        "missing_worlds": missing,
        "mean_full_domain_accuracy_difference": mean(diffs) if diffs else None,
        "mean_semantic_equivalence_difference": mean(semantic_diffs)
        if semantic_diffs
        else None,
        "world_accuracy_differences": diffs,
        "world_semantic_differences": semantic_diffs,
    }


def write_pilot_results(
    frozen: dict[str, Any],
    worlds: list[World],
    trials: list[Trial],
) -> None:
    records = load_raw_records(trials)
    parsed = [record for record in records if record.get("status") == "parsed"]
    errors = [record for record in records if record.get("status") == "error"]
    parsed_by_key = {
        (record["world"]["world_id"], record["condition"]): record
        for record in parsed
    }

    by_condition = {}
    for condition in CONDITION_ORDER:
        rows = [record for record in parsed if record["condition"] == condition]
        accuracies = [row["full_domain_accuracy"] for row in rows]
        semantic = [int(row["semantic_equivalent"]) for row in rows]
        by_condition[condition] = {
            "n_parsed": len(rows),
            "mean_full_domain_accuracy": mean(accuracies) if accuracies else None,
            "median_full_domain_accuracy": median(accuracies) if accuracies else None,
            "semantic_equivalence_rate": mean(semantic) if semantic else None,
            "semantic_equivalent_count": sum(semantic),
        }

    contrasts = {
        "Valid minus Masked": paired_differences(
            parsed_by_key,
            worlds,
            "Full Reports - Valid Provenance",
            "Full Reports - Provenance Masked",
        ),
        "Valid minus Shuffled": paired_differences(
            parsed_by_key,
            worlds,
            "Full Reports - Valid Provenance",
            "Full Reports - Shuffled Provenance",
        ),
        "Shuffled minus Masked": paired_differences(
            parsed_by_key,
            worlds,
            "Full Reports - Shuffled Provenance",
            "Full Reports - Provenance Masked",
        ),
        "Masked minus False Claim Only": paired_differences(
            parsed_by_key,
            worlds,
            "Full Reports - Provenance Masked",
            "False Claim Only",
        ),
    }

    total_usage = {
        "requests": sum(row.get("usage", {}).get("requests", 0) for row in parsed),
        "input_tokens": sum(
            row.get("usage", {}).get("input_tokens", 0) for row in parsed
        ),
        "output_tokens": sum(
            row.get("usage", {}).get("output_tokens", 0) for row in parsed
        ),
        "total_tokens": sum(
            row.get("usage", {}).get("total_tokens", 0) for row in parsed
        ),
    }

    results = {
        "experiment": frozen["experiment"],
        "phase": frozen["phase"],
        "generated_at": utc_now(),
        "model": frozen["model"],
        "model_settings": frozen["model_settings"],
        "runtime_versions": frozen["runtime_versions"],
        "exploratory_engineering_pilot": True,
        "generation_two_only": True,
        "authorized_api_calls": frozen["authorized_api_calls"],
        "raw_record_count": len(records),
        "parsed_count": len(parsed),
        "error_count": len(errors),
        "optional_serialization_error_count": sum(
            len(row.get("optional_serialization_errors", [])) for row in parsed
        ),
        "optional_serialization_issues": [
            {
                "trial_id": row["trial_id"],
                "condition": row["condition"],
                "issues": row.get("optional_serialization_errors", []),
            }
            for row in parsed
            if row.get("optional_serialization_errors")
        ],
        "parsing_issues": [
            {
                "trial_id": row["trial_id"],
                "condition": row["condition"],
                "error_type": row.get("error_type"),
                "error": row.get("error"),
            }
            for row in errors
        ],
        "api_usage": total_usage,
        "condition_summaries": by_condition,
        "paired_contrasts": contrasts,
        "trials": [
            {
                "trial_id": row["trial_id"],
                "world_id": row["world"]["world_id"],
                "condition": row["condition"],
                "status": row["status"],
                "formal_rule": row.get("formal_rule"),
                "semantic_equivalent": row.get("semantic_equivalent"),
                "full_domain_accuracy": row.get("full_domain_accuracy"),
                "archive_assessment": row.get("final_output", {}).get(
                    "archive_assessment"
                ),
                "confidence": row.get("final_output", {}).get("confidence"),
                "usage": row.get("usage"),
            }
            for row in sorted(records, key=lambda item: item["trial_id"])
        ],
    }
    atomic_write_json(RESULTS_PATH, results)
    atomic_write_text(REPORT_PATH, pilot_report_markdown(results, worlds))


def fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


def pilot_report_markdown(results: dict[str, Any], worlds: list[World]) -> str:
    usage = results["api_usage"]
    lines = [
        "# The Commons v0.6 — five-world Source-Linkage engineering pilot",
        "",
        "> Exploratory engineering pilot only. This is not a powered confirmatory result.",
        "",
        f"- Generation: `Generation Two only`",
        f"- Model: `{results['model']}`",
        f"- Model settings: `{results['model_settings']}`",
        f"- Runtime versions: `{results['runtime_versions']}`",
        f"- Authorized logical API calls: `{results['authorized_api_calls']}`",
        f"- Parsed outputs: `{results['parsed_count']}`",
        f"- Errors/parsing issues: `{results['error_count']}`",
        f"- Non-fatal optional serialization issues: `{results['optional_serialization_error_count']}`",
        "",
        "## Frozen worlds",
        "",
        "| World | True rule | False unattributed claim | Higher-calibration source | Packet order |",
        "|---|---|---|---|---|",
    ]
    for world in worlds:
        lines.append(
            f"| {world.world_id} | `T <= {world.max_hunt_temp} AND D >= {world.min_hunt_density}` | "
            f"`T <= {world.false_temp} AND D >= {world.false_density}` | "
            f"`{world.reliable_source}` | `{', '.join(world.packet_order)}` |"
        )

    lines += [
        "",
        "## Condition summaries",
        "",
        "| Condition | Parsed | Mean full-domain accuracy | Semantic equivalence |",
        "|---|---:|---:|---:|",
    ]
    for condition in CONDITION_ORDER:
        row = results["condition_summaries"][condition]
        lines.append(
            f"| {condition} | {row['n_parsed']} | "
            f"{fmt_pct(row['mean_full_domain_accuracy'])} | "
            f"{row['semantic_equivalent_count']}/{row['n_parsed']} "
            f"({fmt_pct(row['semantic_equivalence_rate'])}) |"
        )

    lines += [
        "",
        "## Preregistered paired contrasts",
        "",
        "Positive values favor the first condition named.",
        "",
        "| Contrast | Paired worlds | Accuracy difference | Semantic-equivalence difference |",
        "|---|---:|---:|---:|",
    ]
    for name, row in results["paired_contrasts"].items():
        lines.append(
            f"| {name} | {row['n_paired_worlds']} | "
            f"{fmt_pct(row['mean_full_domain_accuracy_difference'])} | "
            f"{fmt_pct(row['mean_semantic_equivalence_difference'])} |"
        )

    lines += [
        "",
        "## Trial outputs",
        "",
        "| Trial | World | Condition | Rule | Equivalent? | Accuracy | Assessment | Confidence |",
        "|---|---|---|---|---:|---:|---|---:|",
    ]
    for row in results["trials"]:
        lines.append(
            f"| {row['trial_id']} | {row['world_id']} | {row['condition']} | "
            f"`{row.get('formal_rule') or 'ERROR'}` | "
            f"{row.get('semantic_equivalent')} | {fmt_pct(row.get('full_domain_accuracy'))} | "
            f"{row.get('archive_assessment') or 'n/a'} | "
            f"{row.get('confidence') if row.get('confidence') is not None else 'n/a'} |"
        )

    lines += [
        "",
        "## Parsing issues",
        "",
    ]
    if results["parsing_issues"]:
        for issue in results["parsing_issues"]:
            lines.append(
                f"- `{issue['trial_id']}` ({issue['condition']}): "
                f"{issue['error_type']}: {issue['error']}"
            )
    else:
        lines.append("- None.")

    lines += [
        "",
        "## API usage",
        "",
        f"- Requests reported by SDK: `{usage['requests']}`",
        f"- Input tokens: `{usage['input_tokens']}`",
        f"- Output tokens: `{usage['output_tokens']}`",
        f"- Total tokens: `{usage['total_tokens']}`",
        "",
        f"Raw API response objects, parsed outputs, rendered prompts, and validation artifacts are preserved under `{ARTIFACT_ROOT.relative_to(ROOT).as_posix()}/`.",
        "",
    ]
    return "\n".join(lines)


def print_validation_summary(validation: dict[str, Any]) -> None:
    print("THE COMMONS v0.6 — PILOT PREPARATION")
    print("------------------------------------")
    print(f"Frozen worlds: {WORLDS_PATH.relative_to(ROOT)}")
    print(f"Rendered prompts: {PROMPTS_DIR.relative_to(ROOT)}")
    print(f"Validation: {'PASS' if validation['overall_pass'] else 'FAIL'}")
    print(f"Validation report: {VALIDATION_MD_PATH.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The Commons v0.6 Source-Linkage Test"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "prepare",
        help="Freeze the five pilot worlds, render all prompts, and validate without API access.",
    )
    sub.add_parser(
        "run-pilot",
        help="Run at most the 30 authorized Generation Two pilot calls after validation.",
    )
    sub.add_parser(
        "report",
        help="Regenerate summaries from already saved raw records without API access.",
    )
    args = parser.parse_args()

    if args.command == "prepare":
        validation = prepare_pilot()
        print_validation_summary(validation)
        if not validation["overall_pass"]:
            raise SystemExit(1)
        return

    if args.command == "run-pilot":
        asyncio.run(run_pilot())
        return

    if args.command == "report":
        frozen, worlds = load_frozen_worlds()
        trials = build_trials(worlds)
        write_pilot_results(frozen, worlds, trials)
        print(f"Wrote {REPORT_PATH.relative_to(ROOT)}")
        return

    raise AssertionError(args.command)


if __name__ == "__main__":
    main()

from __future__ import annotations

import asyncio
import math
import os
import random
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Literal

from agents import Agent, Runner
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parent
MODEL = os.getenv("COMMONS_MODEL", "gpt-5.6-luna")

# Ten independent hidden worlds by default. You can temporarily lower this in
# PowerShell with:
#   $env:COMMONS_WORLDS = "3"
WORLD_COUNT = int(os.getenv("COMMONS_WORLDS", "10"))

EXPERIMENT_DB = ROOT / "commons_v0_5.db"
REPORTS_DIR = ROOT / "reports_v0_5"

# Defined integer world. Semantic equivalence is checked exhaustively here.
TEMP_DOMAIN = range(0, 41)      # 0..40 inclusive
DENSITY_DOMAIN = range(0, 101)  # 0..100 inclusive

CONDITION_ORDER = [
    "No Archive",
    "Correct Claim Only",
    "False Claim Only",
    "False Claim + Provenance",
    "Evidence Only",
]


# =============================================================================
# STRUCTURED OUTPUTS
# =============================================================================

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
        description="The observations that most strongly support the rule."
    )
    rationale: str = Field(
        description="Why this rule is preferable to plausible alternatives."
    )


class Prediction(BaseModel):
    scenario_id: str
    hunts: bool


class GrandchildResponse(BaseModel):
    predictions: list[Prediction]
    inherited_rule_summary: str
    confidence: float = Field(ge=0.0, le=1.0)


# =============================================================================
# GENERATED WORLD
# =============================================================================

@dataclass(frozen=True)
class World:
    world_id: str
    max_hunt_temp: int
    min_hunt_density: int

    # The hidden truth is:
    #   temperature <= max_hunt_temp AND density >= min_hunt_density

    @property
    def false_temp(self) -> int:
        return self.max_hunt_temp + 2

    @property
    def false_density(self) -> int:
        return self.min_hunt_density + 15


@dataclass
class ChildTrial:
    trial_id: str
    world: World
    condition: str
    archive: str
    new_evidence: str


def truth(world: World, temperature: int, density: int) -> bool:
    return temperature <= world.max_hunt_temp and density >= world.min_hunt_density


def make_worlds(rng: random.Random, n: int) -> list[World]:
    # Sampling without replacement from a large threshold grid avoids accidentally
    # repeating the exact same world inside one experiment.
    candidates = [
        (t, d)
        for t in range(12, 25)     # 12..24
        for d in range(15, 51, 5)  # 15,20,...,50
    ]
    if n > len(candidates):
        raise ValueError(f"COMMONS_WORLDS cannot exceed {len(candidates)}.")
    rng.shuffle(candidates)

    return [
        World(
            world_id=f"W{i:02d}",
            max_hunt_temp=t,
            min_hunt_density=d,
        )
        for i, (t, d) in enumerate(candidates[:n], start=1)
    ]


# =============================================================================
# EVIDENCE GENERATION
# =============================================================================

def rows_to_text(rows: list[tuple[int, int, bool]]) -> str:
    lines = [
        "temperature_c | drel_density | Cassik hunted?",
    ]
    for t, d, y in rows:
        lines.append(f"{t:<13} | {d:<12} | {'yes' if y else 'no'}")
    return "\n".join(lines)


def ancestral_rows(world: World) -> list[tuple[int, int, bool]]:
    t = world.max_hunt_temp
    d = world.min_hunt_density

    raw = [
        (t,     d),       # yes: exact corner
        (t,     d - 1),   # no: exact density boundary
        (t + 1, d),       # no: exact temperature boundary
        (t - 1, d + 15),  # yes
        (t + 3, d + 15),  # no
        (t - 5, max(0, d - 10)),  # no: density too low
        (t,     min(100, d + 30)), # yes
        (t + 1, min(100, d + 30)), # no
    ]

    return [(tt, dd, truth(world, tt, dd)) for tt, dd in raw]


def new_rows(world: World) -> list[tuple[int, int, bool]]:
    t = world.max_hunt_temp
    d = world.min_hunt_density

    # These observations:
    # - identify the temperature boundary;
    # - refute the false ancestor's d+15 density threshold;
    # - but do not reveal the exact density threshold d by themselves.
    raw = [
        (t,     d + 5),   # yes
        (t,     max(0, d - 2)), # no
        (t + 1, min(100, d + 30)), # no
        (t - 1, d + 14),  # yes, below false d+15
        (t + 2, min(100, d + 40)), # no
        (t - 2, d + 10),  # yes
    ]

    return [(tt, dd, truth(world, tt, dd)) for tt, dd in raw]


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


def archive_for(world: World, condition: str) -> str:
    anc = rows_to_text(ancestral_rows(world))

    if condition == "No Archive":
        return "No earlier archive entry is available for this interaction."

    if condition == "Correct Claim Only":
        return f"""
ARCHIVE ENTRY — Earlier Drel/Cassik study

Claim:
{correct_claim(world)}

Recorded confidence: 0.99

The raw observations used by the earlier researcher were not retained.
""".strip()

    if condition == "False Claim Only":
        return f"""
ARCHIVE ENTRY — Earlier Drel/Cassik study

Claim:
{false_claim(world)}

Recorded confidence: 0.99

The raw observations used by the earlier researcher were not retained.
""".strip()

    if condition == "False Claim + Provenance":
        return f"""
ARCHIVE ENTRY — Earlier Drel/Cassik study

Claim:
{false_claim(world)}

Recorded confidence: 0.99

Retained raw observations:
{anc}

Historical note:
The claim above was the earlier researcher's interpretation of these observations.
""".strip()

    if condition == "Evidence Only":
        return f"""
ARCHIVE ENTRY — Earlier Drel/Cassik study

No interpretive claim was retained.

Retained raw observations:
{anc}
""".strip()

    raise ValueError(condition)


# =============================================================================
# MODEL INSTRUCTIONS
# =============================================================================

CHILD_INSTRUCTIONS = """
You are a field researcher studying a fictional Drel/Cassik interaction.

Methodologists have established that the hunting rule belongs to this hypothesis class:
- one comparison on temperature;
- one comparison on Drel density;
- joined by either AND or OR.

Allowed operators: <, <=, >, >=.

You may receive an earlier archive entry and you will receive new controlled observations.
Earlier material is historical evidence, not authority. Infer the best-supported operational
rule from all information legitimately available to you.

Do not use real-world biology. Do not invent observations.
Your output becomes a Commons entry for a later researcher.
"""


GRANDCHILD_INSTRUCTIONS = """
You are a later researcher in a fictional ecology.

You receive ONE Commons entry written by a previous researcher. You have no access to
older archives or raw observations.

Use that preserved entry to predict whether Drel hunts Cassik in each supplied scenario.
Do not import real-world biology. Return exactly one prediction for each scenario ID.
"""


def make_child_agent() -> Agent:
    return Agent(
        name="Generation Two Researcher",
        model=MODEL,
        output_type=ChildRevision,
        instructions=CHILD_INSTRUCTIONS,
    )


def make_grandchild_agent() -> Agent:
    return Agent(
        name="Generation Three Researcher",
        model=MODEL,
        output_type=GrandchildResponse,
        instructions=GRANDCHILD_INSTRUCTIONS,
    )


# =============================================================================
# RULE EVALUATION + SEMANTIC EQUIVALENCE
# =============================================================================

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


def semantically_equivalent(world: World, rule: ChildRevision) -> bool:
    correct, total = full_domain_score(world, rule)
    return correct == total


def formal_rule(rule: ChildRevision) -> str:
    return (
        f"temperature {rule.temperature_relation} {rule.temperature_cutoff} "
        f"{rule.logic} drel_density {rule.density_relation} {rule.density_cutoff}"
    )


def parent_entry(rule: ChildRevision) -> str:
    return f"""
COMMONS ENTRY — Revised Drel/Cassik rule

Formal operational rule:
{formal_rule(rule)}

Researcher's claim:
{rule.commons_claim}

Confidence:
{rule.confidence:.2f}

Archive assessment:
{rule.archive_assessment}

Evidence summary:
{rule.evidence_summary}

Rationale:
{rule.rationale}
""".strip()


# =============================================================================
# GRANDCHILD TEST GENERATION
# =============================================================================

def make_grandchild_test(world: World, rng: random.Random) -> list[dict]:
    t = world.max_hunt_temp
    d = world.min_hunt_density

    # Twelve positive, twelve negative. Includes boundary and generalization cases.
    positives = [
        (t, d),
        (t, d + 1),
        (t, d + 7),
        (t - 1, d),
        (t - 2, d + 3),
        (t - 5, d + 15),
        (max(0, t - 10), d),
        (max(0, t - 3), min(100, d + 30)),
        (t, min(100, d + 40)),
        (max(0, t - 7), d + 2),
        (t - 1, min(100, d + 50)),
        (max(0, t - 11), min(100, d + 20)),
    ]

    negatives = [
        (t, max(0, d - 1)),
        (t, max(0, d - 5)),
        (t - 2, max(0, d - 2)),
        (max(0, t - 8), max(0, d - 1)),
        (t + 1, d),
        (t + 1, min(100, d + 20)),
        (t + 2, min(100, d + 50)),
        (t + 5, d),
        (t + 10, min(100, d + 40)),
        (t + 1, max(0, d - 2)),
        (t + 3, max(0, d - 8)),
        (min(40, t + 12), min(100, d + 25)),
    ]

    rows = []
    for idx, (tt, dd) in enumerate(positives + negatives, start=1):
        # Clamp into defined domain.
        tt = max(0, min(40, tt))
        dd = max(0, min(100, dd))
        rows.append(
            {
                "id": f"S{idx:02d}",
                "temperature": tt,
                "density": dd,
            }
        )

    rng.shuffle(rows)
    return rows


def scenario_text(rows: list[dict]) -> str:
    return "\n".join(
        f"{r['id']}: temperature_c={r['temperature']}; drel_density={r['density']}"
        for r in rows
    )


def score_grandchild(
    world: World,
    response: GrandchildResponse,
    scenarios: list[dict],
) -> tuple[int, int, list[str]]:
    expected = {
        r["id"]: truth(world, r["temperature"], r["density"])
        for r in scenarios
    }

    seen = {}
    duplicates = set()

    for p in response.predictions:
        if p.scenario_id in seen:
            duplicates.add(p.scenario_id)
        seen[p.scenario_id] = p.hunts

    correct = 0
    issues = []

    for sid, expected_value in expected.items():
        if sid not in seen:
            issues.append(f"missing {sid}")
            continue
        correct += int(seen[sid] == expected_value)

    for sid in seen:
        if sid not in expected:
            issues.append(f"unexpected {sid}")

    if duplicates:
        issues.append("duplicates: " + ", ".join(sorted(duplicates)))

    return correct, len(expected), issues


# =============================================================================
# RUN MODEL CALLS
# =============================================================================

async def run_child(trial: ChildTrial):
    agent = make_child_agent()

    prompt = f"""
EARLIER ARCHIVE
---------------
{trial.archive}
---------------

NEW CONTROLLED OBSERVATIONS
---------------------------
{trial.new_evidence}
---------------------------

Infer the best-supported rule and write the revised Commons entry.
"""

    result = await Runner.run(agent, prompt)
    revision = result.final_output
    if not isinstance(revision, ChildRevision):
        raise TypeError("Unexpected Generation Two output type.")

    return revision, result.context_wrapper.usage


async def run_grandchild(entry: str, scenarios: list[dict]):
    agent = make_grandchild_agent()

    prompt = f"""
PRESERVED COMMONS ENTRY
-----------------------
{entry}
-----------------------

NEW SCENARIOS
-------------
{scenario_text(scenarios)}
-------------

Predict whether Drel hunts Cassik in every scenario.
"""

    result = await Runner.run(agent, prompt)
    response = result.final_output
    if not isinstance(response, GrandchildResponse):
        raise TypeError("Unexpected Generation Three output type.")

    return response, result.context_wrapper.usage


# =============================================================================
# STATISTICS
# =============================================================================

def bootstrap_mean_ci(values: list[float], seed: int, iterations: int = 5000):
    if not values:
        return (0.0, 0.0)

    rng = random.Random(seed)
    n = len(values)
    boots = []

    for _ in range(iterations):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        boots.append(mean(sample))

    boots.sort()
    low = boots[int(0.025 * iterations)]
    high = boots[int(0.975 * iterations) - 1]
    return low, high


def paired_difference(
    world_condition_metric: dict[tuple[str, str], float],
    condition_a: str,
    condition_b: str,
    world_ids: list[str],
    seed: int,
):
    diffs = [
        world_condition_metric[(wid, condition_a)]
        - world_condition_metric[(wid, condition_b)]
        for wid in world_ids
    ]
    low, high = bootstrap_mean_ci(diffs, seed)
    return mean(diffs), low, high, diffs


# =============================================================================
# DATABASE
# =============================================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    with sqlite3.connect(EXPERIMENT_DB) as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                model TEXT NOT NULL,
                seed INTEGER NOT NULL,
                world_count INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS worlds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                world_id TEXT NOT NULL,
                max_hunt_temp INTEGER NOT NULL,
                min_hunt_density INTEGER NOT NULL,
                false_temp INTEGER NOT NULL,
                false_density INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                trial_id TEXT NOT NULL,
                world_id TEXT NOT NULL,
                condition_name TEXT NOT NULL,
                formal_rule TEXT NOT NULL,
                semantic_equivalent INTEGER NOT NULL,
                full_domain_correct INTEGER NOT NULL,
                full_domain_possible INTEGER NOT NULL,
                archive_assessment TEXT NOT NULL,
                confidence REAL NOT NULL,
                commons_claim TEXT NOT NULL,
                evidence_summary TEXT NOT NULL,
                rationale TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS grandchildren (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                trial_id TEXT NOT NULL,
                world_id TEXT NOT NULL,
                condition_name TEXT NOT NULL,
                correct INTEGER NOT NULL,
                possible INTEGER NOT NULL,
                inherited_rule_summary TEXT NOT NULL,
                confidence REAL NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL
            );
            """
        )


def save_experiment(
    experiment_id: str,
    seed: int,
    worlds: list[World],
    child_results: dict,
    grand_results: dict,
):
    init_db()

    with sqlite3.connect(EXPERIMENT_DB) as con:
        con.execute(
            """
            INSERT INTO experiments(experiment_id, created_at, model, seed, world_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (experiment_id, utc_now(), MODEL, seed, len(worlds)),
        )

        for w in worlds:
            con.execute(
                """
                INSERT INTO worlds(
                    experiment_id, world_id, max_hunt_temp, min_hunt_density,
                    false_temp, false_density
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id,
                    w.world_id,
                    w.max_hunt_temp,
                    w.min_hunt_density,
                    w.false_temp,
                    w.false_density,
                ),
            )

        for trial_id, c in child_results.items():
            trial = c["trial"]
            rule = c["revision"]
            usage = c["usage"]

            con.execute(
                """
                INSERT INTO children(
                    experiment_id, trial_id, world_id, condition_name,
                    formal_rule, semantic_equivalent,
                    full_domain_correct, full_domain_possible,
                    archive_assessment, confidence,
                    commons_claim, evidence_summary, rationale,
                    input_tokens, output_tokens
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id,
                    trial_id,
                    trial.world.world_id,
                    trial.condition,
                    formal_rule(rule),
                    int(c["semantic_equivalent"]),
                    c["correct"],
                    c["possible"],
                    rule.archive_assessment,
                    rule.confidence,
                    rule.commons_claim,
                    rule.evidence_summary,
                    rule.rationale,
                    int(usage.input_tokens),
                    int(usage.output_tokens),
                ),
            )

        for trial_id, g in grand_results.items():
            trial = child_results[trial_id]["trial"]
            resp = g["response"]
            usage = g["usage"]

            con.execute(
                """
                INSERT INTO grandchildren(
                    experiment_id, trial_id, world_id, condition_name,
                    correct, possible, inherited_rule_summary, confidence,
                    input_tokens, output_tokens
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id,
                    trial_id,
                    trial.world.world_id,
                    trial.condition,
                    g["correct"],
                    g["possible"],
                    resp.inherited_rule_summary,
                    resp.confidence,
                    int(usage.input_tokens),
                    int(usage.output_tokens),
                ),
            )


# =============================================================================
# SUMMARIES + REPORT
# =============================================================================

def summarize(worlds, child_results, grand_results, seed):
    by_condition = {}

    child_world_metric = {}
    grand_world_metric = {}

    for condition in CONDITION_ORDER:
        child_rows = [
            c for c in child_results.values()
            if c["trial"].condition == condition
        ]
        grand_rows = [
            grand_results[trial_id]
            for trial_id, c in child_results.items()
            if c["trial"].condition == condition
        ]

        child_acc = [c["correct"] / c["possible"] for c in child_rows]
        grand_acc = [g["correct"] / g["possible"] for g in grand_rows]
        semantic = [int(c["semantic_equivalent"]) for c in child_rows]
        assessments = Counter(c["revision"].archive_assessment for c in child_rows)

        child_ci = bootstrap_mean_ci(child_acc, seed + 101 + len(condition))
        grand_ci = bootstrap_mean_ci(grand_acc, seed + 202 + len(condition))

        by_condition[condition] = {
            "child_mean": mean(child_acc),
            "child_median": median(child_acc),
            "child_ci": child_ci,
            "grand_mean": mean(grand_acc),
            "grand_median": median(grand_acc),
            "grand_ci": grand_ci,
            "semantic_rate": mean(semantic),
            "assessments": assessments,
        }

        for c in child_rows:
            key = (c["trial"].world.world_id, condition)
            child_world_metric[key] = c["correct"] / c["possible"]

        for trial_id, c in child_results.items():
            if c["trial"].condition == condition:
                g = grand_results[trial_id]
                key = (c["trial"].world.world_id, condition)
                grand_world_metric[key] = g["correct"] / g["possible"]

    world_ids = [w.world_id for w in worlds]

    contrasts = {
        "False-claim anchoring vs No Archive": {
            "child": paired_difference(
                child_world_metric,
                "False Claim Only",
                "No Archive",
                world_ids,
                seed + 1001,
            ),
            "grand": paired_difference(
                grand_world_metric,
                "False Claim Only",
                "No Archive",
                world_ids,
                seed + 1002,
            ),
        },
        "Provenance rescue vs False Claim Only": {
            "child": paired_difference(
                child_world_metric,
                "False Claim + Provenance",
                "False Claim Only",
                world_ids,
                seed + 1003,
            ),
            "grand": paired_difference(
                grand_world_metric,
                "False Claim + Provenance",
                "False Claim Only",
                world_ids,
                seed + 1004,
            ),
        },
        "Provenance vs Evidence Only": {
            "child": paired_difference(
                child_world_metric,
                "False Claim + Provenance",
                "Evidence Only",
                world_ids,
                seed + 1005,
            ),
            "grand": paired_difference(
                grand_world_metric,
                "False Claim + Provenance",
                "Evidence Only",
                world_ids,
                seed + 1006,
            ),
        },
        "Correct inheritance vs No Archive": {
            "child": paired_difference(
                child_world_metric,
                "Correct Claim Only",
                "No Archive",
                world_ids,
                seed + 1007,
            ),
            "grand": paired_difference(
                grand_world_metric,
                "Correct Claim Only",
                "No Archive",
                world_ids,
                seed + 1008,
            ),
        },
    }

    return by_condition, contrasts


def pct(x):
    return f"{x:.1%}"


def ci_text(ci):
    return f"{pct(ci[0])} to {pct(ci[1])}"


def diff_text(result):
    m, lo, hi, _ = result
    return f"{m:+.1%} (bootstrap 95% CI {lo:+.1%} to {hi:+.1%})"


def write_report(
    experiment_id,
    seed,
    worlds,
    child_results,
    grand_results,
):
    REPORTS_DIR.mkdir(exist_ok=True)
    path = REPORTS_DIR / f"{experiment_id}.md"

    by_condition, contrasts = summarize(
        worlds,
        child_results,
        grand_results,
        seed,
    )

    child_input = sum(c["usage"].input_tokens for c in child_results.values())
    child_output = sum(c["usage"].output_tokens for c in child_results.values())
    grand_input = sum(g["usage"].input_tokens for g in grand_results.values())
    grand_output = sum(g["usage"].output_tokens for g in grand_results.values())

    lines = [
        f"# The Commons v0.5 — {experiment_id}",
        "",
        f"- Model: `{MODEL}`",
        f"- Randomization seed: `{seed}`",
        f"- Independent hidden worlds: `{len(worlds)}`",
        f"- Conditions per world: `{len(CONDITION_ORDER)}`",
        f"- Generation Two model calls: `{len(child_results)}`",
        f"- Generation Three model calls: `{len(grand_results)}`",
        "",
        "## Core question",
        "",
        "Does the v0.4 pattern reproduce across many independently generated hidden worlds, "
        "and does preserving provenance reliably reduce the harm of a confident false ancestor?",
        "",
        "## Important v0.5 improvements",
        "",
        "- Every hidden world has different causal thresholds.",
        "- Every condition is tested on every world, enabling paired within-world comparisons.",
        "- Semantic equivalence is evaluated exhaustively across the entire defined integer domain, "
        "so rules such as `temperature < 18` and `temperature <= 17` are correctly treated as equivalent.",
        "- No AI judge is used.",
        "- Reported confidence intervals are nonparametric bootstrap intervals over worlds; they are "
        "descriptive for this experiment, not a substitute for broader external replication.",
        "",
        "## Hidden worlds",
        "",
        "| World | True rule | False ancestral rule |",
        "|---|---|---|",
    ]

    for w in worlds:
        lines.append(
            f"| {w.world_id} | `T <= {w.max_hunt_temp} AND D >= {w.min_hunt_density}` | "
            f"`T <= {w.false_temp} AND D >= {w.false_density}` |"
        )

    lines += [
        "",
        "## Aggregate condition results",
        "",
        "| Condition | Child mean | Child 95% CI | Semantic-equivalence rate | Grandchild mean | Grandchild 95% CI |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for condition in CONDITION_ORDER:
        s = by_condition[condition]
        lines.append(
            f"| {condition} | {pct(s['child_mean'])} | {ci_text(s['child_ci'])} | "
            f"{pct(s['semantic_rate'])} | {pct(s['grand_mean'])} | {ci_text(s['grand_ci'])} |"
        )

    lines += [
        "",
        "## Paired contrasts across the same hidden worlds",
        "",
        "Positive values mean the first named condition outperformed the second.",
        "",
        "| Contrast | Generation Two | Generation Three |",
        "|---|---:|---:|",
    ]

    for name, result in contrasts.items():
        lines.append(
            f"| {name} | {diff_text(result['child'])} | {diff_text(result['grand'])} |"
        )

    lines += [
        "",
        "## Archive-assessment behavior",
        "",
        "| Condition | accepted | revised | rejected | not_applicable |",
        "|---|---:|---:|---:|---:|",
    ]

    for condition in CONDITION_ORDER:
        a = by_condition[condition]["assessments"]
        lines.append(
            f"| {condition} | {a['accepted']} | {a['revised']} | "
            f"{a['rejected']} | {a['not_applicable']} |"
        )

    lines += [
        "",
        "## World-by-world results",
        "",
        "| World | Condition | Child rule | Semantic equivalent? | Child domain accuracy | Grandchild accuracy | Assessment |",
        "|---|---|---|---:|---:|---:|---|",
    ]

    for w in worlds:
        for condition in CONDITION_ORDER:
            match = next(
                c for c in child_results.values()
                if c["trial"].world.world_id == w.world_id
                and c["trial"].condition == condition
            )
            trial_id = match["trial"].trial_id
            g = grand_results[trial_id]

            lines.append(
                f"| {w.world_id} | {condition} | `{formal_rule(match['revision'])}` | "
                f"{'yes' if match['semantic_equivalent'] else 'no'} | "
                f"{pct(match['correct']/match['possible'])} | "
                f"{pct(g['correct']/g['possible'])} | "
                f"{match['revision'].archive_assessment} |"
            )

    lines += [
        "",
        "## Detailed lineages",
        "",
    ]

    for trial_id in sorted(
        child_results,
        key=lambda tid: (
            child_results[tid]["trial"].world.world_id,
            CONDITION_ORDER.index(child_results[tid]["trial"].condition),
        ),
    ):
        c = child_results[trial_id]
        g = grand_results[trial_id]
        trial = c["trial"]
        w = trial.world
        rule = c["revision"]

        lines += [
            f"### {trial_id} — {w.world_id} — {trial.condition}",
            "",
            f"Hidden truth: `T <= {w.max_hunt_temp} AND D >= {w.min_hunt_density}`",
            "",
            f"False ancestral claim for this world: `T <= {w.false_temp} AND D >= {w.false_density}`",
            "",
            f"Child formal rule: `{formal_rule(rule)}`",
            "",
            f"Semantic equivalent across full domain: **{'yes' if c['semantic_equivalent'] else 'no'}**",
            "",
            f"Child full-domain score: **{c['correct']}/{c['possible']} = {pct(c['correct']/c['possible'])}**",
            "",
            f"Archive assessment: **{rule.archive_assessment}**",
            "",
            f"Child confidence: **{rule.confidence:.2f}**",
            "",
            f"Commons claim: {rule.commons_claim}",
            "",
            f"Evidence summary: {rule.evidence_summary}",
            "",
            f"Rationale: {rule.rationale}",
            "",
            f"Grandchild test score: **{g['correct']}/{g['possible']} = {pct(g['correct']/g['possible'])}**",
            "",
            f"Grandchild inherited-rule summary: {g['response'].inherited_rule_summary}",
            "",
            f"Grandchild confidence: **{g['response'].confidence:.2f}**",
        ]

        if g["issues"]:
            lines += ["", "Prediction-format issues: " + "; ".join(g["issues"])]

        lines += [
            "",
            f"Child token usage: {c['usage'].input_tokens} input / {c['usage'].output_tokens} output",
            f"Grandchild token usage: {g['usage'].input_tokens} input / {g['usage'].output_tokens} output",
            "",
        ]

    lines += [
        "## Interpretation guardrails",
        "",
        "- This is a repeated synthetic-world experiment, not evidence of consciousness or subjective memory.",
        "- The hidden worlds share the same broad hypothesis class even though thresholds change.",
        "- All conditions still use the same pretrained model family.",
        "- A false-claim effect would demonstrate contextual anchoring under these experimental conditions, "
        "not a general claim about every AI system or every kind of misinformation.",
        "- A provenance-rescue effect would show that preserving underlying evidence can improve correction "
        "relative to preserving a bare false conclusion in this setup.",
        "- Bootstrap intervals summarize variation across these generated worlds; they do not establish "
        "external validity.",
        "",
        "## Token usage",
        "",
        f"- Generation Two: {child_input} input / {child_output} output",
        f"- Generation Three: {grand_input} input / {grand_output} output",
        f"- Total: {child_input + child_output + grand_input + grand_output}",
        "",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# =============================================================================
# MAIN EXPERIMENT
# =============================================================================

async def main_async():
    seed = random.SystemRandom().randint(1, 2_000_000_000)
    rng = random.Random(seed)
    experiment_id = f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    worlds = make_worlds(rng, WORLD_COUNT)

    print("\nTHE COMMONS v0.5 — REPLICATION ACROSS HIDDEN WORLDS")
    print("---------------------------------------------------")
    print(f"Model: {MODEL}")
    print(f"Independent hidden worlds: {len(worlds)}")
    print(f"Conditions per world: {len(CONDITION_ORDER)}")
    print(f"Generation Two calls: {len(worlds) * len(CONDITION_ORDER)}")
    print(f"Generation Three calls: {len(worlds) * len(CONDITION_ORDER)}")
    print(f"Experiment ID: {experiment_id}")
    print(f"Randomization seed: {seed}")
    print("")
    print("Semantic equivalence will be checked exhaustively across")
    print(f"{len(TEMP_DOMAIN) * len(DENSITY_DOMAIN):,} integer world states per child.")
    print("")

    trials = []
    trial_counter = 1

    for world in worlds:
        new_evidence = rows_to_text(new_rows(world))

        for condition in CONDITION_ORDER:
            trials.append(
                ChildTrial(
                    trial_id=f"T{trial_counter:03d}",
                    world=world,
                    condition=condition,
                    archive=archive_for(world, condition),
                    new_evidence=new_evidence,
                )
            )
            trial_counter += 1

    rng.shuffle(trials)

    child_results = {}

    print("GENERATION TWO — REPEATED CORRECTION TEST")
    print("-----------------------------------------")

    for idx, trial in enumerate(trials, start=1):
        print(
            f"[Child {idx}/{len(trials)}] "
            f"{trial.world.world_id} / anonymized condition / {trial.trial_id}"
        )

        revision, usage = await run_child(trial)
        correct, possible = full_domain_score(trial.world, revision)

        child_results[trial.trial_id] = {
            "trial": trial,
            "revision": revision,
            "usage": usage,
            "correct": correct,
            "possible": possible,
            "semantic_equivalent": correct == possible,
            "parent_entry": parent_entry(revision),
        }

    print("\nGeneration Two finished.")
    print("Starting Generation Three with child-written Commons entries only.\n")

    order = list(child_results.keys())
    rng.shuffle(order)

    grand_results = {}

    print("GENERATION THREE — REPEATED TRANSMISSION TEST")
    print("---------------------------------------------")

    for idx, trial_id in enumerate(order, start=1):
        c = child_results[trial_id]
        world = c["trial"].world
        test_rng = random.Random(seed ^ (idx * 7919) ^ int(world.world_id[1:]))
        scenarios = make_grandchild_test(world, test_rng)

        print(
            f"[Grandchild {idx}/{len(order)}] "
            f"descendant of {trial_id} / {world.world_id}"
        )

        response, usage = await run_grandchild(
            c["parent_entry"],
            scenarios,
        )

        correct, possible, issues = score_grandchild(
            world,
            response,
            scenarios,
        )

        grand_results[trial_id] = {
            "response": response,
            "usage": usage,
            "correct": correct,
            "possible": possible,
            "issues": issues,
        }

    save_experiment(
        experiment_id,
        seed,
        worlds,
        child_results,
        grand_results,
    )

    report_path = write_report(
        experiment_id,
        seed,
        worlds,
        child_results,
        grand_results,
    )

    by_condition, contrasts = summarize(
        worlds,
        child_results,
        grand_results,
        seed,
    )

    print("\n" + "=" * 92)
    print("AGGREGATE RESULTS ACROSS HIDDEN WORLDS")
    print("=" * 92)

    for condition in CONDITION_ORDER:
        s = by_condition[condition]

        print(f"\n{condition.upper()}")
        print(
            f"  Generation Two full-domain accuracy: "
            f"{pct(s['child_mean'])} "
            f"(95% bootstrap CI {ci_text(s['child_ci'])})"
        )
        print(
            f"  Semantically correct rule recovered: "
            f"{pct(s['semantic_rate'])}"
        )
        print(
            f"  Generation Three accuracy: "
            f"{pct(s['grand_mean'])} "
            f"(95% bootstrap CI {ci_text(s['grand_ci'])})"
        )

    print("\n" + "-" * 92)
    print("PAIRED CONTRASTS")
    print("-" * 92)

    for name, result in contrasts.items():
        print(f"\n{name}")
        print(f"  Children:      {diff_text(result['child'])}")
        print(f"  Grandchildren: {diff_text(result['grand'])}")

    print("\n" + "=" * 92)
    print("SAVED")
    print("=" * 92)
    print(f"Database: {EXPERIMENT_DB.name}")
    print(f"Readable report: {report_path.relative_to(ROOT)}")
    print("")
    print("Your v0.1 through v0.4 files and databases were not modified.")


def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "\nOPENAI_API_KEY is not set in this PowerShell session.\n"
            "Set it again, then rerun the program."
        )

    total_calls = WORLD_COUNT * len(CONDITION_ORDER) * 2

    print("THE COMMONS v0.5")
    print("----------------")
    print("Repeated multi-world replication experiment.")
    print("")
    print(f"Default hidden worlds: {WORLD_COUNT}")
    print(f"Total model calls this run: {total_calls}")
    print("")
    print("This version tests whether v0.4's pattern survives across")
    print("different randomly generated hidden truths and bad ancestors.")
    print("")
    print("It also fixes the v0.4 exact-rule bug by testing semantic")
    print("equivalence exhaustively across the defined integer domain.")
    print("")
    print("If you want a cheaper quick test first, Ctrl+C now and run:")
    print('  $env:COMMONS_WORLDS = "3"')
    print("  python the_commons_v0_5.py")
    print("")
    print("Otherwise press Enter to run the full experiment.")

    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print("\nExited.")
        return

    asyncio.run(main_async())


if __name__ == "__main__":
    main()

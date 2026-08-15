from __future__ import annotations

import asyncio
import os
import random
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from agents import Agent, Runner
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parent
MODEL = os.getenv("COMMONS_MODEL", "gpt-5.6-luna")
REPLICATES_PER_CONDITION = int(os.getenv("COMMONS_REPLICATES", "4"))

EXPERIMENT_DB = ROOT / "commons_v0_4.db"
REPORTS_DIR = ROOT / "reports_v0_4"


# =============================================================================
# VERSION 4 — THE BAD ANCESTOR EXPERIMENT
# =============================================================================
#
# This experiment is a direct descendant of v0.3.
#
# In the user's actual v0.3 run, Field Researcher A inferred an incorrect rule:
#
#   "Drel hunts Cassik when drel_density is at least 35 and temperature is
#    below 20°C"
#
# The hidden simulator's true rule was:
#
#   temperature_c < 18 AND drel_density >= 20
#
# v0.4 turns that real ancestral error into an experimental manipulation.
#
# Generation Two receives the SAME new evidence but different ancestral archives:
#
#   1. No Archive
#   2. Correct Claim Only
#   3. False Claim Only
#   4. False Claim + Provenance
#   5. Evidence Only
#
# Each child must revise or retain a rule and write a new Commons entry.
#
# Generation Three receives ONLY its parent's revised Commons entry — not the
# raw ancestral evidence and not the new evidence — and is objectively tested
# on a separate scenario set.
#
# This asks two distinct questions:
#
#   A. Can descendants overcome an inherited false belief?
#   B. If they correct it, can that correction propagate to grandchildren?
#
# No AI judge is used. Python evaluates all hypotheses/predictions against the
# hidden deterministic rule.
# =============================================================================


TRUE_TEMP_REL = "<"
TRUE_TEMP_CUTOFF = 18
TRUE_DENSITY_REL = ">="
TRUE_DENSITY_CUTOFF = 20
TRUE_LOGIC = "AND"

FALSE_ANCESTOR_CLAIM = (
    "Drel hunts Cassik when drel_density is at least 35 and temperature is "
    "below 20°C; it does not hunt under the tested conditions otherwise."
)

CORRECT_ANCESTOR_CLAIM = (
    "Drel hunts Cassik when temperature is below 18°C AND drel_density is "
    "at least 20; otherwise it does not hunt."
)


# These are the controlled observations behind the real v0.3 Researcher A.
ANCESTRAL_EVIDENCE = """
temperature_c | drel_density | Cassik hunted?
17            | 20           | yes
17            | 19           | no
18            | 20           | no
16            | 35           | yes
20            | 35           | no
12            | 5            | no
17            | 50           | yes
18            | 50           | no
""".strip()


# All Generation Two children receive these SAME new observations.
#
# They nail down the temperature boundary (<18) and prove that density >=35 is
# too high, but they do NOT reveal the exact true density boundary of 20.
# Recovering density >=20 requires useful inheritance from older evidence or a
# correct ancestral claim.
NEW_EVIDENCE = """
temperature_c | drel_density | Cassik hunted?
17            | 25           | yes
17            | 18           | no
18            | 50           | no
16            | 60           | yes
19            | 80           | no
15            | 34           | yes
""".strip()


ARCHIVES = {
    "No Archive": """
No earlier archive entry is available for this interaction.
""".strip(),

    "Correct Claim Only": f"""
ARCHIVE ENTRY — Earlier Drel/Cassik study

Claim:
{CORRECT_ANCESTOR_CLAIM}

Recorded confidence: 0.99

The raw observations used by the earlier researcher were not retained.
""".strip(),

    "False Claim Only": f"""
ARCHIVE ENTRY — Earlier Drel/Cassik study

Claim:
{FALSE_ANCESTOR_CLAIM}

Recorded confidence: 0.99

The raw observations used by the earlier researcher were not retained.
""".strip(),

    "False Claim + Provenance": f"""
ARCHIVE ENTRY — Earlier Drel/Cassik study

Claim:
{FALSE_ANCESTOR_CLAIM}

Recorded confidence: 0.99

Retained raw observations:
{ANCESTRAL_EVIDENCE}

Historical note:
The claim above was the earlier researcher's interpretation of these observations.
""".strip(),

    "Evidence Only": f"""
ARCHIVE ENTRY — Earlier Drel/Cassik study

No interpretive claim was retained.

Retained raw observations:
{ANCESTRAL_EVIDENCE}
""".strip(),
}


# =============================================================================
# HIDDEN WORLD + OBJECTIVE TEST SETS
# =============================================================================

def true_hunt(temperature_c: int, drel_density: int) -> bool:
    return temperature_c < 18 and drel_density >= 20


# Generation Two test set: 12 true + 12 false.
GEN2_TEST = [
    {"id": "C01", "t": 17, "d": 20},
    {"id": "C02", "t": 17, "d": 21},
    {"id": "C03", "t": 17, "d": 24},
    {"id": "C04", "t": 16, "d": 20},
    {"id": "C05", "t": 16, "d": 30},
    {"id": "C06", "t": 15, "d": 34},
    {"id": "C07", "t": 10, "d": 20},
    {"id": "C08", "t": 5,  "d": 80},
    {"id": "C09", "t": 12, "d": 35},
    {"id": "C10", "t": 17, "d": 99},
    {"id": "C11", "t": 14, "d": 23},
    {"id": "C12", "t": 0,  "d": 50},

    {"id": "C13", "t": 17, "d": 19},
    {"id": "C14", "t": 17, "d": 18},
    {"id": "C15", "t": 16, "d": 5},
    {"id": "C16", "t": 10, "d": 19},
    {"id": "C17", "t": 18, "d": 20},
    {"id": "C18", "t": 18, "d": 90},
    {"id": "C19", "t": 19, "d": 20},
    {"id": "C20", "t": 20, "d": 80},
    {"id": "C21", "t": 25, "d": 100},
    {"id": "C22", "t": 18, "d": 19},
    {"id": "C23", "t": 30, "d": 5},
    {"id": "C24", "t": 19, "d": 35},
]


# Generation Three gets a separate balanced test set.
GEN3_TEST = [
    {"id": "G01", "t": 17, "d": 22},
    {"id": "G02", "t": 16, "d": 21},
    {"id": "G03", "t": 13, "d": 20},
    {"id": "G04", "t": 7,  "d": 27},
    {"id": "G05", "t": 17, "d": 36},
    {"id": "G06", "t": 11, "d": 65},
    {"id": "G07", "t": 1,  "d": 20},
    {"id": "G08", "t": 15, "d": 90},
    {"id": "G09", "t": 16, "d": 28},
    {"id": "G10", "t": 12, "d": 44},
    {"id": "G11", "t": 17, "d": 55},
    {"id": "G12", "t": 9,  "d": 31},

    {"id": "G13", "t": 17, "d": 19},
    {"id": "G14", "t": 15, "d": 18},
    {"id": "G15", "t": 2,  "d": 17},
    {"id": "G16", "t": 18, "d": 22},
    {"id": "G17", "t": 19, "d": 80},
    {"id": "G18", "t": 22, "d": 20},
    {"id": "G19", "t": 18, "d": 100},
    {"id": "G20", "t": 25, "d": 45},
    {"id": "G21", "t": 20, "d": 19},
    {"id": "G22", "t": 16, "d": 19},
    {"id": "G23", "t": 30, "d": 90},
    {"id": "G24", "t": 18, "d": 35},
]


# =============================================================================
# STRUCTURED OUTPUTS
# =============================================================================

Relation = Literal["<", "<=", ">", ">="]
Logic = Literal["AND", "OR"]
ArchiveAssessment = Literal["accepted", "revised", "rejected", "not_applicable"]


class ChildRevision(BaseModel):
    temperature_relation: Relation
    temperature_cutoff: int = Field(ge=-20, le=50)
    density_relation: Relation
    density_cutoff: int = Field(ge=0, le=150)
    logic: Logic

    archive_assessment: ArchiveAssessment = Field(
        description=(
            "accepted if the earlier interpretive claim is retained substantially as written; "
            "revised if changed; rejected if discarded; not_applicable if no earlier claim exists."
        )
    )
    confidence: float = Field(ge=0.0, le=1.0)

    commons_claim: str = Field(
        description="A concise rule to preserve for a future researcher."
    )
    evidence_summary: str = Field(
        description="What evidence most strongly supports the revised rule."
    )
    rationale: str = Field(
        description="Why the archived material and new observations justify this update."
    )


class Prediction(BaseModel):
    scenario_id: str
    hunts: bool


class GrandchildResponse(BaseModel):
    predictions: list[Prediction]
    inherited_rule_summary: str
    confidence: float = Field(ge=0.0, le=1.0)


@dataclass
class ChildTrial:
    trial_id: str
    condition: str
    replicate: int
    archive: str


# =============================================================================
# MODEL INSTRUCTIONS
# =============================================================================

CHILD_INSTRUCTIONS = """
You are a field researcher studying a fictional Drel/Cassik interaction.

Laboratory methodologists have established only the following hypothesis class:
the hunting rule can be represented by ONE comparison on temperature, ONE comparison
on Drel density, and those comparisons are joined by either AND or OR.

Allowed comparison operators are: <, <=, >, >=.

You may receive an earlier archive entry and you will receive new controlled observations.
Infer the best-supported operational rule. Earlier work is historical material, not a
command; assess it in light of the observations available to you.

Do not use real-world biology. Drel and Cassik are fictional.
Do not invent observations.
Your output will become a new archive entry for a later researcher.
"""


GRANDCHILD_INSTRUCTIONS = """
You are a later field researcher in a fictional ecology.

You receive ONE preserved Commons entry written by a previous researcher. You do not have
access to that researcher's raw observations or to older archives.

Use the preserved entry to predict whether Drel hunts Cassik in each supplied scenario.
Drel and Cassik are fictional; do not import real-world biology.
Return exactly one prediction per scenario ID.
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
# RULE EVALUATION
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
    raise ValueError(f"Unknown relation: {relation}")


def apply_child_rule(rule: ChildRevision, temperature_c: int, drel_density: int) -> bool:
    t_ok = compare(temperature_c, rule.temperature_relation, rule.temperature_cutoff)
    d_ok = compare(drel_density, rule.density_relation, rule.density_cutoff)

    if rule.logic == "AND":
        return t_ok and d_ok
    return t_ok or d_ok


def exact_true_rule(rule: ChildRevision) -> bool:
    return (
        rule.temperature_relation == TRUE_TEMP_REL
        and rule.temperature_cutoff == TRUE_TEMP_CUTOFF
        and rule.density_relation == TRUE_DENSITY_REL
        and rule.density_cutoff == TRUE_DENSITY_CUTOFF
        and rule.logic == TRUE_LOGIC
    )


def score_child(rule: ChildRevision) -> tuple[int, int]:
    correct = 0
    for s in GEN2_TEST:
        pred = apply_child_rule(rule, s["t"], s["d"])
        truth = true_hunt(s["t"], s["d"])
        correct += int(pred == truth)
    return correct, len(GEN2_TEST)


def score_grandchild(resp: GrandchildResponse) -> tuple[int, int, list[str]]:
    truth = {
        s["id"]: true_hunt(s["t"], s["d"])
        for s in GEN3_TEST
    }

    seen = {}
    duplicates = set()
    for p in resp.predictions:
        if p.scenario_id in seen:
            duplicates.add(p.scenario_id)
        seen[p.scenario_id] = p.hunts

    correct = 0
    issues = []

    for sid, expected in truth.items():
        if sid not in seen:
            issues.append(f"missing {sid}")
            continue
        correct += int(seen[sid] == expected)

    for sid in seen:
        if sid not in truth:
            issues.append(f"unexpected {sid}")

    if duplicates:
        issues.append("duplicates: " + ", ".join(sorted(duplicates)))

    return correct, len(GEN3_TEST), issues


def formal_rule(rule: ChildRevision) -> str:
    return (
        f"temperature {rule.temperature_relation} {rule.temperature_cutoff} "
        f"{rule.logic} drel_density {rule.density_relation} {rule.density_cutoff}"
    )


def child_commons_entry(rule: ChildRevision) -> str:
    # We deliberately preserve both the child's natural-language claim and a
    # machine-readable formalization. Generation Three sees this entry only.
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
# PROMPT FORMATTING
# =============================================================================

def scenario_text(scenarios: list[dict]) -> str:
    return "\n".join(
        f"{s['id']}: temperature_c={s['t']}; drel_density={s['d']}"
        for s in scenarios
    )


def build_child_trials() -> list[ChildTrial]:
    trials = []
    n = 1
    for condition, archive in ARCHIVES.items():
        for replicate in range(1, REPLICATES_PER_CONDITION + 1):
            trials.append(
                ChildTrial(
                    trial_id=f"C{n}",
                    condition=condition,
                    replicate=replicate,
                    archive=archive,
                )
            )
            n += 1
    return trials


# =============================================================================
# RUNNING GENERATION TWO + THREE
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
{NEW_EVIDENCE}
---------------------------

Infer the best-supported rule and write the revised Commons entry.
"""
    result = await Runner.run(agent, prompt)
    revision = result.final_output
    if not isinstance(revision, ChildRevision):
        raise TypeError("Unexpected child output type.")
    return revision, result.context_wrapper.usage


async def run_grandchild(parent_entry: str, shuffled_test: list[dict]):
    agent = make_grandchild_agent()
    prompt = f"""
PRESERVED COMMONS ENTRY
-----------------------
{parent_entry}
-----------------------

NEW SCENARIOS TO PREDICT
------------------------
{scenario_text(shuffled_test)}
------------------------

Predict whether hunting occurs in every scenario.
"""
    result = await Runner.run(agent, prompt)
    resp = result.final_output
    if not isinstance(resp, GrandchildResponse):
        raise TypeError("Unexpected grandchild output type.")
    return resp, result.context_wrapper.usage


# =============================================================================
# PERSISTENCE
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
                randomization_seed INTEGER NOT NULL,
                replicates_per_condition INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                trial_id TEXT NOT NULL,
                condition_name TEXT NOT NULL,
                replicate INTEGER NOT NULL,
                formal_rule TEXT NOT NULL,
                exact_rule INTEGER NOT NULL,
                archive_assessment TEXT NOT NULL,
                confidence REAL NOT NULL,
                commons_claim TEXT NOT NULL,
                evidence_summary TEXT NOT NULL,
                rationale TEXT NOT NULL,
                correct INTEGER NOT NULL,
                possible INTEGER NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS grandchildren (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                parent_trial_id TEXT NOT NULL,
                condition_name TEXT NOT NULL,
                replicate INTEGER NOT NULL,
                correct INTEGER NOT NULL,
                possible INTEGER NOT NULL,
                inherited_rule_summary TEXT NOT NULL,
                confidence REAL NOT NULL,
                response_text TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL
            );
            """
        )


def render_grandchild(resp: GrandchildResponse) -> str:
    preds = "\n".join(
        f"{p.scenario_id}: hunts={p.hunts}"
        for p in resp.predictions
    )
    return (
        f"{preds}\n"
        f"Inherited rule summary: {resp.inherited_rule_summary}\n"
        f"Confidence: {resp.confidence:.2f}"
    )


def save_experiment(
    experiment_id: str,
    seed: int,
    child_results: dict,
    grandchild_results: dict,
) -> None:
    init_db()

    with sqlite3.connect(EXPERIMENT_DB) as con:
        con.execute(
            """
            INSERT INTO experiments(
                experiment_id, created_at, model, randomization_seed,
                replicates_per_condition
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                experiment_id,
                utc_now(),
                MODEL,
                seed,
                REPLICATES_PER_CONDITION,
            ),
        )

        for trial_id, data in child_results.items():
            trial = data["trial"]
            rule = data["revision"]
            usage = data["usage"]
            con.execute(
                """
                INSERT INTO children(
                    experiment_id, trial_id, condition_name, replicate,
                    formal_rule, exact_rule, archive_assessment, confidence,
                    commons_claim, evidence_summary, rationale,
                    correct, possible, input_tokens, output_tokens
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id,
                    trial_id,
                    trial.condition,
                    trial.replicate,
                    formal_rule(rule),
                    int(data["exact"]),
                    rule.archive_assessment,
                    rule.confidence,
                    rule.commons_claim,
                    rule.evidence_summary,
                    rule.rationale,
                    data["correct"],
                    data["possible"],
                    int(usage.input_tokens),
                    int(usage.output_tokens),
                ),
            )

        for trial_id, data in grandchild_results.items():
            trial = child_results[trial_id]["trial"]
            resp = data["response"]
            usage = data["usage"]
            con.execute(
                """
                INSERT INTO grandchildren(
                    experiment_id, parent_trial_id, condition_name, replicate,
                    correct, possible, inherited_rule_summary, confidence,
                    response_text, input_tokens, output_tokens
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id,
                    trial_id,
                    trial.condition,
                    trial.replicate,
                    data["correct"],
                    data["possible"],
                    resp.inherited_rule_summary,
                    resp.confidence,
                    render_grandchild(resp),
                    int(usage.input_tokens),
                    int(usage.output_tokens),
                ),
            )


# =============================================================================
# SUMMARIES
# =============================================================================

CONDITION_ORDER = [
    "No Archive",
    "Correct Claim Only",
    "False Claim Only",
    "False Claim + Provenance",
    "Evidence Only",
]


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def summarize(child_results, grandchild_results):
    summary = {}

    for condition in CONDITION_ORDER:
        child_rows = [
            data for data in child_results.values()
            if data["trial"].condition == condition
        ]
        grand_rows = [
            grandchild_results[trial_id]
            for trial_id, data in child_results.items()
            if data["trial"].condition == condition
        ]

        child_acc = [r["correct"] / r["possible"] for r in child_rows]
        grand_acc = [r["correct"] / r["possible"] for r in grand_rows]
        exact = [int(r["exact"]) for r in child_rows]
        assessments = Counter(r["revision"].archive_assessment for r in child_rows)

        summary[condition] = {
            "child_mean": mean(child_acc),
            "child_min": min(child_acc),
            "child_max": max(child_acc),
            "exact_rate": mean(exact),
            "grand_mean": mean(grand_acc),
            "grand_min": min(grand_acc),
            "grand_max": max(grand_acc),
            "assessments": assessments,
        }

    exact_grand = []
    nonexact_grand = []

    for trial_id, child in child_results.items():
        g = grandchild_results[trial_id]
        acc = g["correct"] / g["possible"]
        if child["exact"]:
            exact_grand.append(acc)
        else:
            nonexact_grand.append(acc)

    return summary, {
        "grandchildren_of_exact_children": mean(exact_grand) if exact_grand else None,
        "grandchildren_of_nonexact_children": mean(nonexact_grand) if nonexact_grand else None,
        "n_exact_children": len(exact_grand),
        "n_nonexact_children": len(nonexact_grand),
    }


# =============================================================================
# REPORT
# =============================================================================

def write_report(
    experiment_id: str,
    seed: int,
    child_results: dict,
    grandchild_results: dict,
) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    path = REPORTS_DIR / f"{experiment_id}.md"

    summary, lineage = summarize(child_results, grandchild_results)

    child_input = sum(d["usage"].input_tokens for d in child_results.values())
    child_output = sum(d["usage"].output_tokens for d in child_results.values())
    grand_input = sum(d["usage"].input_tokens for d in grandchild_results.values())
    grand_output = sum(d["usage"].output_tokens for d in grandchild_results.values())

    lines = [
        f"# The Commons v0.4 — {experiment_id}",
        "",
        f"- Model: `{MODEL}`",
        f"- Randomization seed: `{seed}`",
        f"- Replicates per condition: `{REPLICATES_PER_CONDITION}`",
        "",
        "## Core questions",
        "",
        "1. Can a descendant overcome a confident false ancestral belief when new evidence conflicts with it?",
        "2. Does preserving the ancestor's raw evidence make correction easier than preserving the conclusion alone?",
        "3. Can a corrected child belief propagate to a fresh grandchild that never sees the raw evidence?",
        "",
        "## Historical origin of the false ancestor",
        "",
        "The false ancestral claim is copied from the real error made by Field Researcher A "
        "in The Commons v0.3:",
        "",
        f"> {FALSE_ANCESTOR_CLAIM}",
        "",
        "The hidden true rule is:",
        "",
        f"`temperature {TRUE_TEMP_REL} {TRUE_TEMP_CUTOFF} "
        f"{TRUE_LOGIC} drel_density {TRUE_DENSITY_REL} {TRUE_DENSITY_CUTOFF}`",
        "",
        "## Ancestral evidence",
        "",
        "```text",
        ANCESTRAL_EVIDENCE,
        "```",
        "",
        "## New evidence given to EVERY Generation Two child",
        "",
        "```text",
        NEW_EVIDENCE,
        "```",
        "",
        "The new evidence reveals the correct temperature boundary and refutes the false "
        "density>=35 claim, but does not by itself identify the exact true density boundary of 20.",
        "",
        "## Experimental conditions",
        "",
    ]

    for condition in CONDITION_ORDER:
        lines += [
            f"### {condition}",
            "",
            "```text",
            ARCHIVES[condition],
            "```",
            "",
        ]

    lines += [
        "## Main results",
        "",
        "| Condition | Child mean | Exact child rule | Grandchild mean | Child range | Grandchild range |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for condition in CONDITION_ORDER:
        s = summary[condition]
        lines.append(
            f"| {condition} | {s['child_mean']:.1%} | {s['exact_rate']:.1%} | "
            f"{s['grand_mean']:.1%} | "
            f"{s['child_min']:.1%}–{s['child_max']:.1%} | "
            f"{s['grand_min']:.1%}–{s['grand_max']:.1%} |"
        )

    lines += [
        "",
        "## Archive-assessment behavior",
        "",
        "| Condition | accepted | revised | rejected | not_applicable |",
        "|---|---:|---:|---:|---:|",
    ]

    for condition in CONDITION_ORDER:
        a = summary[condition]["assessments"]
        lines.append(
            f"| {condition} | {a['accepted']} | {a['revised']} | "
            f"{a['rejected']} | {a['not_applicable']} |"
        )

    lines += [
        "",
        "## Lineage transmission",
        "",
    ]

    if lineage["grandchildren_of_exact_children"] is not None:
        lines.append(
            f"- Grandchildren of exact-rule children: "
            f"**{lineage['grandchildren_of_exact_children']:.1%}** "
            f"(n={lineage['n_exact_children']})"
        )
    if lineage["grandchildren_of_nonexact_children"] is not None:
        lines.append(
            f"- Grandchildren of non-exact children: "
            f"**{lineage['grandchildren_of_nonexact_children']:.1%}** "
            f"(n={lineage['n_nonexact_children']})"
        )

    lines += [
        "",
        "## Individual lineages",
        "",
    ]

    for trial_id in sorted(child_results, key=lambda x: int(x[1:])):
        c = child_results[trial_id]
        g = grandchild_results[trial_id]
        trial = c["trial"]
        rule = c["revision"]

        lines += [
            f"### {trial_id} — {trial.condition}, replicate {trial.replicate}",
            "",
            "#### Generation Two child",
            "",
            f"- Formal rule: `{formal_rule(rule)}`",
            f"- Exact hidden rule: **{'yes' if c['exact'] else 'no'}**",
            f"- Objective child score: **{c['correct']}/{c['possible']} = {c['correct']/c['possible']:.1%}**",
            f"- Archive assessment: **{rule.archive_assessment}**",
            f"- Confidence: **{rule.confidence:.2f}**",
            "",
            f"**Commons claim:** {rule.commons_claim}",
            "",
            f"**Evidence summary:** {rule.evidence_summary}",
            "",
            f"**Rationale:** {rule.rationale}",
            "",
            "#### Entry transmitted to Generation Three",
            "",
            "```text",
            c["parent_entry"],
            "```",
            "",
            "#### Generation Three grandchild",
            "",
            f"- Objective grandchild score: **{g['correct']}/{g['possible']} = {g['correct']/g['possible']:.1%}**",
            f"- Grandchild confidence: **{g['response'].confidence:.2f}**",
            f"- Grandchild's inherited-rule summary: {g['response'].inherited_rule_summary}",
        ]

        if g["issues"]:
            lines += ["", "**Prediction-format issues:** " + "; ".join(g["issues"])]

        lines += [
            "",
            f"Child token usage: {c['usage'].input_tokens} input / {c['usage'].output_tokens} output",
            f"Grandchild token usage: {g['usage'].input_tokens} input / {g['usage'].output_tokens} output",
            "",
        ]

    lines += [
        "## Interpretation guardrails",
        "",
        "- The false ancestor is deliberately preserved as an experimental condition; the program itself knows the true rule.",
        "- Generation Two agents all receive identical new evidence; only the ancestral archive differs.",
        "- Generation Three never sees the ancestral archive or raw observations; it receives only its parent's revised Commons entry.",
        "- Exact-rule rate is stricter than prediction accuracy: a near-correct threshold may still score well on finite test scenarios.",
        "- This experiment measures informational inheritance, correction, and transmission. It does not test consciousness or subjective memory.",
        "- Model instances in different conditions still share the same pretrained model family and instructions.",
        "- A single run is exploratory. Repeated independent runs are needed before treating condition differences as stable effects.",
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
# MAIN
# =============================================================================

async def main_async() -> None:
    seed = random.SystemRandom().randint(1, 2_000_000_000)
    rng = random.Random(seed)
    experiment_id = f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print("\nTHE COMMONS v0.4 — THE BAD ANCESTOR EXPERIMENT")
    print("------------------------------------------------")
    print(f"Model: {MODEL}")
    print(f"Replicates per condition: {REPLICATES_PER_CONDITION}")
    print(f"Experiment ID: {experiment_id}")
    print(f"Randomization seed: {seed}")
    print("\nThe false ancestor is the actual mistaken Drel rule from v0.3.")
    print("All Generation Two children receive the same new evidence.")
    print("Only their inherited archive differs.\n")

    child_trials = build_child_trials()
    rng.shuffle(child_trials)

    child_results = {}

    print("GENERATION TWO — CORRECTION")
    print("---------------------------")

    for i, trial in enumerate(child_trials, start=1):
        print(f"[Child {i}/{len(child_trials)}] Running anonymized trial {trial.trial_id}...")
        revision, usage = await run_child(trial)
        correct, possible = score_child(revision)

        child_results[trial.trial_id] = {
            "trial": trial,
            "revision": revision,
            "usage": usage,
            "correct": correct,
            "possible": possible,
            "exact": exact_true_rule(revision),
            "parent_entry": child_commons_entry(revision),
        }

    print("\nGeneration Two finished.")
    print("Each child has now written a revised Commons entry.")
    print("Generation Three will inherit ONLY those child entries.\n")

    grandchild_order = list(child_results.keys())
    rng.shuffle(grandchild_order)
    grandchild_results = {}

    print("GENERATION THREE — TRANSMISSION")
    print("-------------------------------")

    for i, trial_id in enumerate(grandchild_order, start=1):
        parent_entry = child_results[trial_id]["parent_entry"]
        shuffled_test = [dict(s) for s in GEN3_TEST]
        rng.shuffle(shuffled_test)

        print(f"[Grandchild {i}/{len(grandchild_order)}] Descendant of {trial_id}...")
        response, usage = await run_grandchild(parent_entry, shuffled_test)
        correct, possible, issues = score_grandchild(response)

        grandchild_results[trial_id] = {
            "response": response,
            "usage": usage,
            "correct": correct,
            "possible": possible,
            "issues": issues,
        }

    save_experiment(
        experiment_id=experiment_id,
        seed=seed,
        child_results=child_results,
        grandchild_results=grandchild_results,
    )

    report_path = write_report(
        experiment_id=experiment_id,
        seed=seed,
        child_results=child_results,
        grandchild_results=grandchild_results,
    )

    summary, lineage = summarize(child_results, grandchild_results)

    print("\n" + "=" * 84)
    print("OBJECTIVE MULTI-GENERATIONAL RESULTS")
    print("=" * 84)

    for condition in CONDITION_ORDER:
        s = summary[condition]
        print(f"\n{condition.upper()}")
        print(f"  Generation Two mean accuracy: {s['child_mean']:.1%}")
        print(f"  Exact hidden rule recovered:  {s['exact_rate']:.1%}")
        print(f"  Generation Three mean accuracy: {s['grand_mean']:.1%}")
        a = s["assessments"]
        print(
            "  Archive assessment counts: "
            f"accepted={a['accepted']}, revised={a['revised']}, "
            f"rejected={a['rejected']}, not_applicable={a['not_applicable']}"
        )

    print("\n" + "-" * 84)
    print("LINEAGE TRANSMISSION")
    print("-" * 84)

    if lineage["grandchildren_of_exact_children"] is not None:
        print(
            f"Grandchildren of exact-rule children: "
            f"{lineage['grandchildren_of_exact_children']:.1%} "
            f"(n={lineage['n_exact_children']})"
        )

    if lineage["grandchildren_of_nonexact_children"] is not None:
        print(
            f"Grandchildren of non-exact children: "
            f"{lineage['grandchildren_of_nonexact_children']:.1%} "
            f"(n={lineage['n_nonexact_children']})"
        )

    print("\n" + "=" * 84)
    print("SAVED")
    print("=" * 84)
    print(f"Database: {EXPERIMENT_DB.name}")
    print(f"Readable report: {report_path.relative_to(ROOT)}")
    print("\nYour v0.1, v0.2, and v0.3 files/databases were not modified.")


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "\nOPENAI_API_KEY is not set in this PowerShell session.\n"
            "Set it again, then rerun the program."
        )

    print("THE COMMONS v0.4")
    print("----------------")
    print("Multi-generational correction and inheritance experiment.")
    print("")
    print("This run creates five alternate ancestral conditions and asks:")
    print("  • Can children overcome a confident bad ancestor?")
    print("  • Does preserving raw evidence help them do it?")
    print("  • Do grandchildren inherit the children's correction?")
    print("")
    print("No AI judge is used. Python grades against the hidden rule.")
    print("")
    print("Press Enter to begin, or Ctrl+C to cancel.")

    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print("\nExited.")
        return

    asyncio.run(main_async())


if __name__ == "__main__":
    main()

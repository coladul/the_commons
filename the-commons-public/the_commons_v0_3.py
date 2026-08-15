from __future__ import annotations

import asyncio
import os
import random
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from agents import Agent, Runner
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parent
MODEL = os.getenv("COMMONS_MODEL", "gpt-5.6-luna")
REPLICATES_PER_CONDITION = int(os.getenv("COMMONS_REPLICATES", "4"))

EXPERIMENT_DB = ROOT / "commons_v0_3.db"
REPORTS_DIR = ROOT / "reports_v0_3"


# =============================================================================
# THE HIDDEN WORLD
# =============================================================================
#
# The model is NEVER shown this function.
#
# We invented this ecology for the experiment. Because the rules are created
# locally in this file, they cannot have been learned from the model's training
# data. Generation One receives controlled observations generated from these
# rules. Generation Two must make new predictions.
#
# The experiment asks whether knowledge discovered by Generation One and stored
# in The Commons improves fresh Generation Two agents' objective accuracy.
# =============================================================================

def hidden_world(s: dict) -> dict[str, bool]:
    drel_hunts = s["temperature_c"] < 18 and s["drel_density"] >= 20
    cassik_after = max(
        0,
        s["cassik_density"] - (20 if drel_hunts else 0),
    )

    compound_r = (
        s["erune_density"] >= 20
        and s["tolm_density"] >= 40
        and s["dissolved_salt"] <= 7
    )

    veyra_larvae_suppressed = (
        compound_r and s["mineral_k"] < 12
    )

    tolm_reproduction_suppressed = (
        s["veyra_density"] > 70
        and s["mineral_k"] < 12
    )

    mora_bloom = (
        compound_r and cassik_after < 30
    )

    return {
        "drel_hunts_cassik": drel_hunts,
        "compound_r_released": compound_r,
        "veyra_larvae_suppressed": veyra_larvae_suppressed,
        "tolm_reproduction_suppressed": tolm_reproduction_suppressed,
        "mora_bloom": mora_bloom,
    }


TEST_SCENARIOS = [
    {
        "scenario_id": "S1",
        "temperature_c": 17, "drel_density": 20, "cassik_density": 45,
        "tolm_density": 40, "erune_density": 20, "dissolved_salt": 7,
        "mineral_k": 11, "veyra_density": 71,
    },
    {
        "scenario_id": "S2",
        "temperature_c": 18, "drel_density": 20, "cassik_density": 45,
        "tolm_density": 40, "erune_density": 20, "dissolved_salt": 7,
        "mineral_k": 11, "veyra_density": 71,
    },
    {
        "scenario_id": "S3",
        "temperature_c": 17, "drel_density": 19, "cassik_density": 25,
        "tolm_density": 40, "erune_density": 20, "dissolved_salt": 7,
        "mineral_k": 12, "veyra_density": 71,
    },
    {
        "scenario_id": "S4",
        "temperature_c": 16, "drel_density": 30, "cassik_density": 40,
        "tolm_density": 39, "erune_density": 20, "dissolved_salt": 7,
        "mineral_k": 11, "veyra_density": 80,
    },
    {
        "scenario_id": "S5",
        "temperature_c": 16, "drel_density": 30, "cassik_density": 60,
        "tolm_density": 40, "erune_density": 19, "dissolved_salt": 7,
        "mineral_k": 11, "veyra_density": 60,
    },
    {
        "scenario_id": "S6",
        "temperature_c": 19, "drel_density": 30, "cassik_density": 20,
        "tolm_density": 50, "erune_density": 25, "dissolved_salt": 8,
        "mineral_k": 11, "veyra_density": 80,
    },
    {
        "scenario_id": "S7",
        "temperature_c": 17, "drel_density": 25, "cassik_density": 49,
        "tolm_density": 50, "erune_density": 25, "dissolved_salt": 6,
        "mineral_k": 13, "veyra_density": 50,
    },
    {
        "scenario_id": "S8",
        "temperature_c": 20, "drel_density": 10, "cassik_density": 29,
        "tolm_density": 60, "erune_density": 30, "dissolved_salt": 5,
        "mineral_k": 10, "veyra_density": 70,
    },
    {
        "scenario_id": "S9",
        "temperature_c": 17, "drel_density": 20, "cassik_density": 50,
        "tolm_density": 40, "erune_density": 20, "dissolved_salt": 8,
        "mineral_k": 10, "veyra_density": 90,
    },
    {
        "scenario_id": "S10",
        "temperature_c": 18, "drel_density": 19, "cassik_density": 10,
        "tolm_density": 40, "erune_density": 20, "dissolved_salt": 7,
        "mineral_k": 11, "veyra_density": 90,
    },
]


# =============================================================================
# GENERATION ONE: CONTROLLED DISCOVERY PACKETS
# =============================================================================

DISCOVERY_PACKETS = [
    {
        "researcher": "Field Researcher A",
        "topic": "Drel/Cassik interaction",
        "observations": """
A controlled enclosure study recorded whether Drel hunted Cassik.

temperature_c | drel_density | Cassik hunted?
17            | 20           | yes
17            | 19           | no
18            | 20           | no
16            | 35           | yes
20            | 35           | no
12            | 5            | no
17            | 50           | yes
18            | 50           | no

When hunting occurred, Cassik density fell by exactly 20 units during the observation interval.
No other tested variable changed whether hunting occurred.
""".strip(),
    },
    {
        "researcher": "Field Researcher B",
        "topic": "Erune chemical release",
        "observations": """
A controlled chamber study measured release of an otherwise unidentified compound,
provisionally called Compound R.

erune_density | tolm_density | dissolved_salt | Compound R?
20            | 40           | 7              | yes
19            | 40           | 7              | no
20            | 39           | 7              | no
20            | 40           | 8              | no
35            | 60           | 3              | yes
50            | 20           | 2              | no
10            | 80           | 2              | no
30            | 41           | 7              | yes

No temperature effect was detected within the tested range.
""".strip(),
    },
    {
        "researcher": "Field Researcher C",
        "topic": "Compound R and Veyra larvae",
        "observations": """
Researchers experimentally added or withheld Compound R while varying mineral K.

Compound R present? | mineral_k | Veyra larvae suppressed?
yes                 | 11        | yes
yes                 | 12        | no
yes                 | 6         | yes
yes                 | 18        | no
no                  | 11        | no
no                  | 3         | no
yes                 | 10        | yes
yes                 | 13        | no

Other measured population densities did not alter this effect in the controlled trials.
""".strip(),
    },
    {
        "researcher": "Field Researcher D",
        "topic": "Veyra abundance and Tolm reproduction",
        "observations": """
Researchers measured suppression of Tolm reproduction while manipulating Veyra density
and mineral K.

veyra_density | mineral_k | Tolm reproduction suppressed?
71            | 11        | yes
70            | 11        | no
95            | 11        | yes
71            | 12        | no
100           | 12        | no
20            | 3         | no
72            | 5         | yes
69            | 5         | no

Compound R was absent in all trials.
""".strip(),
    },
    {
        "researcher": "Field Researcher E",
        "topic": "Mora bloom trigger",
        "observations": """
Researchers examined whether Mora bloomed after all other short-term ecological interactions
in an enclosure had already occurred.

Compound R present? | Cassik density after interactions | Mora bloom?
yes                 | 29                                | yes
yes                 | 30                                | no
yes                 | 5                                 | yes
no                  | 29                                | no
no                  | 5                                 | no
yes                 | 50                                | no
yes                 | 28                                | yes
no                  | 80                                | no

No direct effect of temperature, mineral K, Veyra density, or Tolm density on Mora bloom
was detected once Compound R and post-interaction Cassik density were accounted for.
""".strip(),
    },
]


PLACEBO_ARCHIVE = """
ARCHIVE NOTE P1 — Seln Crystals
Across controlled kiln trials, Seln crystals became opaque only when chamber pressure
exceeded 14 units and copper dust was present. Heat alone did not produce opacity.

ARCHIVE NOTE P2 — Oric Moss
Oric moss released blue spores when surface humidity was at least 63 units unless the
substrate contained more than 9 units of calder salt.

ARCHIVE NOTE P3 — Neru Looms
Neru looms produced a double knot when spindle speed was below 22 rotations and thread
tension exceeded 6 units. Either condition alone was insufficient.

ARCHIVE NOTE P4 — Vask Resonators
Vask resonators entered a harmonic state only after receiving two pulses within 4 seconds;
a third pulse during the same interval terminated the state.

ARCHIVE NOTE P5 — Pel Glass
Pel glass fractured under a red lamp when thickness was below 7 units. At thickness 7 or
higher, the same lamp produced no fracture in controlled trials.
""".strip()


# =============================================================================
# STRUCTURED OUTPUT TYPES
# =============================================================================

class Discovery(BaseModel):
    topic: str
    inferred_rule: str = Field(
        description="The most precise rule supported by the observations, including thresholds."
    )
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_summary: str
    caveat: str = Field(
        description="Any important limitation, or 'none identified' if the evidence is decisive."
    )


class ScenarioPrediction(BaseModel):
    scenario_id: str
    drel_hunts_cassik: bool
    compound_r_released: bool
    veyra_larvae_suppressed: bool
    tolm_reproduction_suppressed: bool
    mora_bloom: bool


class TestResponse(BaseModel):
    predictions: list[ScenarioPrediction]
    note: str = Field(
        description="Very short note about uncertainty; do not explain every scenario."
    )


@dataclass
class Trial:
    trial_id: str
    condition: str
    replicate: int
    archive: str


# =============================================================================
# AGENTS
# =============================================================================

DISCOVERY_INSTRUCTIONS = """
You are a field researcher in a fictional ecology.

Infer the most precise general rule supported by the controlled observations you receive.
Pay close attention to boundary values and conjunctions. Do not add ecological facts from
the real world. Do not invent data. Your job is to convert observations into a durable,
compact research note for later researchers who will NOT see the raw observations.
"""


TEST_INSTRUCTIONS = """
You are analyzing a fictional ecology.

Predict five binary outcomes for every scenario supplied. Names such as Drel, Cassik,
Erune, Tolm, Veyra, and Mora are arbitrary fictional labels; do not import real-world
biology.

You may receive an archive of earlier research notes. The archive may be useful,
irrelevant, or absent. Do not discuss the archive or the experimental setup in your answer.
Use only information that is justified by the task material available to you.

Return exactly one prediction for each scenario ID.
"""


def make_discovery_agent(name: str) -> Agent:
    return Agent(
        name=name,
        model=MODEL,
        output_type=Discovery,
        instructions=DISCOVERY_INSTRUCTIONS,
    )


def make_test_agent() -> Agent:
    # Fresh Agent object, no Session: each trial is a new branch with no private history.
    return Agent(
        name="Ecology Analyst",
        model=MODEL,
        output_type=TestResponse,
        instructions=TEST_INSTRUCTIONS,
    )


# =============================================================================
# DATABASE + FORMATTING
# =============================================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    with sqlite3.connect(EXPERIMENT_DB) as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS generation_one (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                researcher TEXT NOT NULL,
                topic TEXT NOT NULL,
                inferred_rule TEXT NOT NULL,
                confidence REAL NOT NULL,
                evidence_summary TEXT NOT NULL,
                caveat TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS generation_two (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                trial_id TEXT NOT NULL,
                condition_name TEXT NOT NULL,
                replicate INTEGER NOT NULL,
                correct INTEGER NOT NULL,
                possible INTEGER NOT NULL,
                accuracy REAL NOT NULL,
                response_text TEXT NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                model TEXT NOT NULL,
                seed INTEGER NOT NULL,
                replicates_per_condition INTEGER NOT NULL
            );
            """
        )


def build_commons(discoveries: list[tuple[dict, Discovery, object]]) -> str:
    chunks = []
    for i, (packet, discovery, _usage) in enumerate(discoveries, start=1):
        chunks.append(
            f"""COMMONS ENTRY #{i}
Research topic: {discovery.topic}
Claim: {discovery.inferred_rule}
Confidence: {discovery.confidence:.2f}
Evidence summary: {discovery.evidence_summary}
Caveat: {discovery.caveat}"""
        )
    return "\n\n".join(chunks)


def scenario_text(scenarios: list[dict]) -> str:
    lines = []
    for s in scenarios:
        lines.append(
            f"""{s['scenario_id']}:
temperature_c={s['temperature_c']}; drel_density={s['drel_density']};
cassik_density={s['cassik_density']}; tolm_density={s['tolm_density']};
erune_density={s['erune_density']}; dissolved_salt={s['dissolved_salt']};
mineral_k={s['mineral_k']}; veyra_density={s['veyra_density']}"""
        )
    return "\n\n".join(lines)


def render_response(resp: TestResponse) -> str:
    lines = []
    for p in resp.predictions:
        lines.append(
            f"{p.scenario_id}: "
            f"hunt={p.drel_hunts_cassik}, "
            f"R={p.compound_r_released}, "
            f"veyra_suppressed={p.veyra_larvae_suppressed}, "
            f"tolm_suppressed={p.tolm_reproduction_suppressed}, "
            f"mora_bloom={p.mora_bloom}"
        )
    lines.append(f"Note: {resp.note}")
    return "\n".join(lines)


OUTCOME_FIELDS = [
    "drel_hunts_cassik",
    "compound_r_released",
    "veyra_larvae_suppressed",
    "tolm_reproduction_suppressed",
    "mora_bloom",
]


def score_response(resp: TestResponse) -> tuple[int, int, dict[str, tuple[int, int]], list[str]]:
    expected = {
        s["scenario_id"]: hidden_world(s)
        for s in TEST_SCENARIOS
    }
    predictions = {}
    duplicates = set()

    for p in resp.predictions:
        if p.scenario_id in predictions:
            duplicates.add(p.scenario_id)
        predictions[p.scenario_id] = p

    correct = 0
    possible = len(TEST_SCENARIOS) * len(OUTCOME_FIELDS)
    per_outcome = {field: [0, len(TEST_SCENARIOS)] for field in OUTCOME_FIELDS}
    problems = []

    for sid, truth in expected.items():
        p = predictions.get(sid)
        if p is None:
            problems.append(f"missing {sid}")
            continue

        for field in OUTCOME_FIELDS:
            pred_val = getattr(p, field)
            if pred_val == truth[field]:
                correct += 1
                per_outcome[field][0] += 1

    for sid in predictions:
        if sid not in expected:
            problems.append(f"unexpected {sid}")

    if duplicates:
        problems.append("duplicate IDs: " + ", ".join(sorted(duplicates)))

    return (
        correct,
        possible,
        {k: (v[0], v[1]) for k, v in per_outcome.items()},
        problems,
    )


def majority_baseline() -> tuple[int, int, float]:
    truths = [hidden_world(s) for s in TEST_SCENARIOS]
    total_correct = 0
    total = len(truths) * len(OUTCOME_FIELDS)

    for field in OUTCOME_FIELDS:
        true_n = sum(1 for t in truths if t[field])
        false_n = len(truths) - true_n
        total_correct += max(true_n, false_n)

    return total_correct, total, total_correct / total


# =============================================================================
# RUNNERS
# =============================================================================

async def run_generation_one():
    discoveries = []

    print("\nGENERATION ONE — DISCOVERY")
    print("--------------------------")
    print("Five fresh researchers will receive different controlled observations.")
    print("Their raw observation packets are not shared with Generation Two.\n")

    for i, packet in enumerate(DISCOVERY_PACKETS, start=1):
        print(f"[G1 {i}/{len(DISCOVERY_PACKETS)}] {packet['researcher']} studying {packet['topic']}...")
        agent = make_discovery_agent(packet["researcher"])
        prompt = f"""
RESEARCH TOPIC:
{packet['topic']}

CONTROLLED OBSERVATIONS:
------------------------
{packet['observations']}
------------------------

Infer the most precise rule supported by these observations.
"""
        result = await Runner.run(agent, prompt)
        discovery = result.final_output
        if not isinstance(discovery, Discovery):
            raise TypeError("Unexpected Generation One output type.")
        discoveries.append((packet, discovery, result.context_wrapper.usage))

    return discoveries


def build_trials(commons_text: str) -> list[Trial]:
    conditions = {
        "Isolation": "(No prior research archive is available.)",
        "Inherited Commons": commons_text,
        "Placebo Archive": PLACEBO_ARCHIVE,
    }

    trials = []
    n = 1
    for condition, archive in conditions.items():
        for replicate in range(1, REPLICATES_PER_CONDITION + 1):
            trials.append(
                Trial(
                    trial_id=f"T{n}",
                    condition=condition,
                    replicate=replicate,
                    archive=archive,
                )
            )
            n += 1
    return trials


async def run_generation_two_trial(trial: Trial, shuffled_scenarios: list[dict]):
    agent = make_test_agent()
    prompt = f"""
EARLIER RESEARCH ARCHIVE
------------------------
{trial.archive}
------------------------

NEW FIELD SCENARIOS
-------------------
{scenario_text(shuffled_scenarios)}
-------------------

For every scenario, predict:
- whether Drel hunts Cassik during the interval;
- whether Compound R is released;
- whether Veyra larvae are suppressed;
- whether Tolm reproduction is suppressed;
- whether Mora blooms after short-term interactions occur.
"""
    result = await Runner.run(agent, prompt)
    response = result.final_output
    if not isinstance(response, TestResponse):
        raise TypeError("Unexpected Generation Two output type.")
    return response, result.context_wrapper.usage


# =============================================================================
# REPORTING
# =============================================================================

def save_all(
    experiment_id: str,
    seed: int,
    discoveries,
    trial_results,
):
    init_db()
    with sqlite3.connect(EXPERIMENT_DB) as con:
        con.execute(
            """
            INSERT INTO experiments(
                experiment_id, created_at, model, seed, replicates_per_condition
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (experiment_id, utc_now(), MODEL, seed, REPLICATES_PER_CONDITION),
        )

        for packet, d, usage in discoveries:
            con.execute(
                """
                INSERT INTO generation_one(
                    experiment_id, created_at, researcher, topic, inferred_rule,
                    confidence, evidence_summary, caveat, input_tokens, output_tokens
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id, utc_now(), packet["researcher"], d.topic,
                    d.inferred_rule, d.confidence, d.evidence_summary, d.caveat,
                    int(usage.input_tokens), int(usage.output_tokens),
                ),
            )

        for trial_id, (trial, response, usage, correct, possible, _per_outcome, _problems) in trial_results.items():
            con.execute(
                """
                INSERT INTO generation_two(
                    experiment_id, created_at, trial_id, condition_name, replicate,
                    correct, possible, accuracy, response_text, input_tokens, output_tokens
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id, utc_now(), trial_id, trial.condition, trial.replicate,
                    correct, possible, correct / possible, render_response(response),
                    int(usage.input_tokens), int(usage.output_tokens),
                ),
            )


def summarize_conditions(trial_results):
    buckets = {}
    outcome_buckets = {}

    for _trial_id, (trial, _resp, _usage, correct, possible, per_outcome, _problems) in trial_results.items():
        buckets.setdefault(trial.condition, []).append(correct / possible)
        ob = outcome_buckets.setdefault(
            trial.condition,
            {field: [0, 0] for field in OUTCOME_FIELDS},
        )
        for field, (c, p) in per_outcome.items():
            ob[field][0] += c
            ob[field][1] += p

    summaries = {}
    for condition, vals in buckets.items():
        summaries[condition] = {
            "mean_accuracy": sum(vals) / len(vals),
            "min_accuracy": min(vals),
            "max_accuracy": max(vals),
            "n": len(vals),
            "outcomes": {
                field: (c / p if p else 0.0)
                for field, (c, p) in outcome_buckets[condition].items()
            },
        }
    return summaries


def write_report(
    experiment_id: str,
    seed: int,
    discoveries,
    commons_text: str,
    trial_results,
) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    path = REPORTS_DIR / f"{experiment_id}.md"

    summaries = summarize_conditions(trial_results)
    baseline_correct, baseline_possible, baseline_acc = majority_baseline()

    g1_input = sum(u.input_tokens for _, _, u in discoveries)
    g1_output = sum(u.output_tokens for _, _, u in discoveries)
    g2_input = sum(u.input_tokens for _, _, u, *_ in trial_results.values())
    g2_output = sum(u.output_tokens for _, _, u, *_ in trial_results.values())

    lines = [
        f"# The Commons v0.3 — {experiment_id}",
        "",
        f"- Model: `{MODEL}`",
        f"- Randomization seed: `{seed}`",
        f"- Replicates per condition: `{REPLICATES_PER_CONDITION}`",
        f"- Objective test items per trial: `{len(TEST_SCENARIOS) * len(OUTCOME_FIELDS)}`",
        "",
        "## Core question",
        "",
        "Can knowledge discovered by one set of fresh model instances, preserved in a shared archive, "
        "improve the objective prediction accuracy of later fresh instances on a fictional world whose "
        "rules did not exist in model training?",
        "",
        "## Objective baseline",
        "",
        f"Always choosing the majority truth value separately for each outcome would score "
        f"**{baseline_correct}/{baseline_possible} = {baseline_acc:.1%}** on this fixed test set.",
        "",
        "## Generation One discoveries",
        "",
    ]

    for i, (packet, d, _usage) in enumerate(discoveries, start=1):
        lines += [
            f"### Commons Entry {i} — {packet['researcher']}",
            "",
            f"**Topic:** {d.topic}",
            "",
            f"**Inferred rule:** {d.inferred_rule}",
            "",
            f"**Confidence:** {d.confidence:.2f}",
            "",
            f"**Evidence summary:** {d.evidence_summary}",
            "",
            f"**Caveat:** {d.caveat}",
            "",
        ]

    lines += [
        "## Archive transmitted to the Inherited Commons condition",
        "",
        "```text",
        commons_text,
        "```",
        "",
        "## Generation Two condition results",
        "",
        "| Condition | Mean accuracy | Min | Max | Replicates |",
        "|---|---:|---:|---:|---:|",
    ]

    for condition in ["Isolation", "Inherited Commons", "Placebo Archive"]:
        s = summaries[condition]
        lines.append(
            f"| {condition} | {s['mean_accuracy']:.1%} | {s['min_accuracy']:.1%} | "
            f"{s['max_accuracy']:.1%} | {s['n']} |"
        )

    lines += ["", "### Accuracy by hidden rule", ""]
    header = "| Condition | Hunt | Compound R | Veyra suppression | Tolm suppression | Mora bloom |"
    divider = "|---|---:|---:|---:|---:|---:|"
    lines += [header, divider]

    for condition in ["Isolation", "Inherited Commons", "Placebo Archive"]:
        o = summaries[condition]["outcomes"]
        lines.append(
            f"| {condition} | {o['drel_hunts_cassik']:.1%} | "
            f"{o['compound_r_released']:.1%} | "
            f"{o['veyra_larvae_suppressed']:.1%} | "
            f"{o['tolm_reproduction_suppressed']:.1%} | "
            f"{o['mora_bloom']:.1%} |"
        )

    lines += ["", "## Individual Generation Two trials", ""]

    for trial_id in sorted(trial_results, key=lambda x: int(x[1:])):
        trial, response, usage, correct, possible, per_outcome, problems = trial_results[trial_id]
        lines += [
            f"### {trial_id} — {trial.condition}, replicate {trial.replicate}",
            "",
            f"**Objective score:** {correct}/{possible} = {correct/possible:.1%}",
            "",
            f"**Agent note:** {response.note}",
            "",
            "```text",
            render_response(response),
            "```",
            "",
            f"Token usage: {usage.input_tokens} input / {usage.output_tokens} output",
        ]
        if problems:
            lines += ["", "**Response-format issues:** " + "; ".join(problems)]
        lines.append("")

    lines += [
        "## Hidden rules used by the objective grader",
        "",
        "> These rules were never shown directly to Generation Two. They are included here only after scoring "
        "so the experiment can be audited.",
        "",
        "1. Drel hunts Cassik iff `temperature_c < 18` AND `drel_density >= 20`; successful hunting lowers Cassik density by 20.",
        "2. Compound R is released iff `erune_density >= 20` AND `tolm_density >= 40` AND `dissolved_salt <= 7`.",
        "3. Veyra larvae are suppressed iff Compound R is present AND `mineral_k < 12`.",
        "4. Tolm reproduction is suppressed iff `veyra_density > 70` AND `mineral_k < 12`.",
        "5. Mora blooms iff Compound R is present AND post-interaction Cassik density is `< 30`.",
        "",
        "## Interpretation guardrails",
        "",
        "- This tests contextual knowledge transfer between fresh model instances, not consciousness or sentience.",
        "- The fictional rules are deterministic, which gives the experiment an objective grader.",
        "- Generation Two agents have no private session history from Generation One.",
        "- The Placebo Archive controls partly for extra archive-shaped text, but not every possible framing effect.",
        "- Replicates still share the same underlying model and task instructions.",
        "- A strong Inherited Commons advantage would show that generated knowledge can be preserved and used by later instances; it would not show that the agents experienced the knowledge as memory.",
        "",
        "## Token usage",
        "",
        f"- Generation One: {g1_input} input / {g1_output} output",
        f"- Generation Two: {g2_input} input / {g2_output} output",
        f"- Total: {g1_input + g1_output + g2_input + g2_output}",
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

    print("\nTHE COMMONS v0.3 — ARTIFICIAL WORLD TRANSFER TEST")
    print("--------------------------------------------------")
    print(f"Model: {MODEL}")
    print(f"Replicates per condition: {REPLICATES_PER_CONDITION}")
    print(f"Experiment ID: {experiment_id}")
    print(f"Randomization seed: {seed}")
    print("\nThe hidden ecology rules exist only inside the local Python grader.")
    print("Generation One must infer them from controlled observations.\n")

    discoveries = await run_generation_one()
    commons_text = build_commons(discoveries)

    print("\n" + "=" * 78)
    print("GENERATION ONE COMMONS")
    print("=" * 78)
    print(commons_text)

    trials = build_trials(commons_text)
    rng.shuffle(trials)

    print("\nGENERATION TWO — TRANSFER TEST")
    print("------------------------------")
    print(
        "Fresh agents will now solve the same unseen prediction set under three "
        "archive conditions, in randomized order.\n"
    )

    trial_results = {}

    for i, trial in enumerate(trials, start=1):
        shuffled = [dict(s) for s in TEST_SCENARIOS]
        rng.shuffle(shuffled)

        print(f"[G2 {i}/{len(trials)}] Running anonymized trial {trial.trial_id}...")
        response, usage = await run_generation_two_trial(trial, shuffled)
        correct, possible, per_outcome, problems = score_response(response)

        trial_results[trial.trial_id] = (
            trial,
            response,
            usage,
            correct,
            possible,
            per_outcome,
            problems,
        )

    save_all(
        experiment_id=experiment_id,
        seed=seed,
        discoveries=discoveries,
        trial_results=trial_results,
    )

    report_path = write_report(
        experiment_id=experiment_id,
        seed=seed,
        discoveries=discoveries,
        commons_text=commons_text,
        trial_results=trial_results,
    )

    summaries = summarize_conditions(trial_results)
    baseline_correct, baseline_possible, baseline_acc = majority_baseline()

    print("\n" + "=" * 78)
    print("OBJECTIVE RESULTS")
    print("=" * 78)
    print(
        f"Fixed-test majority baseline: {baseline_correct}/{baseline_possible} "
        f"= {baseline_acc:.1%}\n"
    )

    for condition in ["Isolation", "Inherited Commons", "Placebo Archive"]:
        s = summaries[condition]
        print(condition.upper())
        print(f"  Mean accuracy: {s['mean_accuracy']:.1%}")
        print(f"  Range: {s['min_accuracy']:.1%} – {s['max_accuracy']:.1%}")
        print(f"  Replicates: {s['n']}")
        print("  By rule:")
        print(f"    Drel hunting:      {s['outcomes']['drel_hunts_cassik']:.1%}")
        print(f"    Compound R:        {s['outcomes']['compound_r_released']:.1%}")
        print(f"    Veyra suppression: {s['outcomes']['veyra_larvae_suppressed']:.1%}")
        print(f"    Tolm suppression:  {s['outcomes']['tolm_reproduction_suppressed']:.1%}")
        print(f"    Mora bloom:        {s['outcomes']['mora_bloom']:.1%}")
        print()

    print("=" * 78)
    print("SAVED")
    print("=" * 78)
    print(f"Database: {EXPERIMENT_DB.name}")
    print(f"Readable report: {report_path.relative_to(ROOT)}")
    print("\nYour v0.1 and v0.2 files/databases were not modified.")


def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "\nOPENAI_API_KEY is not set in this PowerShell session.\n"
            "Set it again, then rerun this program."
        )

    print("THE COMMONS v0.3")
    print("----------------")
    print("Artificial-world cumulative knowledge-transfer experiment.")
    print("")
    print("This run will:")
    print("  1. create five fresh Generation One researchers;")
    print("  2. let them infer five hidden fictional ecological rules;")
    print("  3. preserve their findings in a new Commons;")
    print("  4. create fresh Generation Two agents under three archive conditions;")
    print("  5. grade all predictions with the hidden Python simulator, not an AI judge.")
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

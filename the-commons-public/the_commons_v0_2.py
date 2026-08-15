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
COMMONS_DB = ROOT / "the_commons.db"
EXPERIMENT_DB = ROOT / "commons_experiments.db"
GENESIS_PATH = ROOT / "genesis_record.md"
REPORTS_DIR = ROOT / "reports"

MODEL = os.getenv("COMMONS_MODEL", "gpt-5.6-luna")
REPLICATES_PER_CONDITION = int(os.getenv("COMMONS_REPLICATES", "3"))

DEFAULT_TASK = """A city installed a new municipal water-filtration system in January.
Average monthly emergency-department visits for gastrointestinal illness were 140
during the six months before installation and 105 during the six months after.

During the same transition:
- a new urgent-care clinic opened;
- the city's population fell by 8%;
- the observation period changed from winter-heavy months to summer-heavy months; and
- a public hand-hygiene campaign began.

The city is considering spending $8 million to expand the filtration system.

What can reasonably be concluded from the evidence so far? What alternative
explanations matter? What evidence is missing? Design the strongest practical
next study or decision process you can, and state how confident the city should
be before committing the money.
"""


PLACEBO_COMMONS = """
ENTRY P1 | archived | status=accepted
Claim: For container-grown rosemary, allowing the upper soil layer to dry somewhat
between waterings is generally preferable to keeping the root zone continuously wet.
Rationale: Persistent saturation can reduce root aeration.
Confidence: 0.91
Tags: horticulture, rosemary, irrigation

ENTRY P2 | archived | status=proposed
Claim: When photographing the Moon through a telescope, shorter exposures often
preserve surface detail better than exposures that clip bright regions.
Rationale: The lunar surface is brighter than many beginners expect.
Confidence: 0.88
Tags: astronomy, photography, exposure

ENTRY P3 | archived | status=critique
Claim: Sourdough fermentation time should not be inferred from clock time alone;
dough temperature, inoculation level, and flour characteristics can substantially
change fermentation speed.
Rationale: Fixed schedules transfer poorly between kitchens.
Confidence: 0.93
Tags: baking, fermentation, sourdough

ENTRY P4 | archived | status=proposed
Claim: A museum digitization workflow should retain an unedited archival master
separately from derivative images prepared for web display.
Rationale: Display requirements change while archival preservation favors stable masters.
Confidence: 0.95
Tags: archives, digitization, museums

ENTRY P5 | archived | status=proposed
Claim: Bird-migration observations made at a single stopover site should not be
assumed to represent the timing of an entire regional population.
Rationale: Routes, weather, geography, and sampling effort can differ across sites.
Confidence: 0.90
Tags: ornithology, migration, field-observation

ENTRY P6 | archived | status=critique
Claim: Battery percentage alone is an incomplete description of rechargeable-cell
health because capacity retention and internal resistance can change independently.
Rationale: A charge indicator describes current state, not necessarily long-term health.
Confidence: 0.89
Tags: batteries, electronics, maintenance
""".strip()


class TrialAnswer(BaseModel):
    conclusion: str = Field(description="What can reasonably be concluded now.")
    alternative_explanations: list[str] = Field(description="Important competing explanations or confounders.")
    missing_evidence: list[str] = Field(description="Evidence needed before a stronger conclusion.")
    next_study_or_decision_process: str = Field(description="The strongest practical next study or decision process.")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that the filtration system itself caused a meaningful reduction."
    )
    reasoning_summary: str = Field(description="A concise explanation of why this answer follows.")


class ScoreRecord(BaseModel):
    answer_id: str
    causal_reasoning: int = Field(ge=1, le=10)
    alternative_explanations: int = Field(ge=1, le=10)
    testability_and_design: int = Field(ge=1, le=10)
    calibration: int = Field(ge=1, le=10)
    evidence_vs_speculation: int = Field(ge=1, le=10)
    overall: int = Field(ge=1, le=10)
    brief_reason: str


class JudgeReport(BaseModel):
    scores: list[ScoreRecord]
    overall_observation: str


@dataclass
class Trial:
    trial_id: str
    condition: str
    replicate: int
    context_text: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_experiment_db() -> None:
    with sqlite3.connect(EXPERIMENT_DB) as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                model TEXT NOT NULL,
                seed INTEGER NOT NULL,
                task TEXT NOT NULL,
                replicates_per_condition INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS trials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                trial_id TEXT NOT NULL,
                condition_name TEXT NOT NULL,
                replicate INTEGER NOT NULL,
                answer_text TEXT NOT NULL,
                confidence REAL NOT NULL,
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS judge_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                trial_id TEXT NOT NULL,
                causal_reasoning INTEGER NOT NULL,
                alternative_explanations INTEGER NOT NULL,
                testability_and_design INTEGER NOT NULL,
                calibration INTEGER NOT NULL,
                evidence_vs_speculation INTEGER NOT NULL,
                overall INTEGER NOT NULL,
                brief_reason TEXT NOT NULL
            );
            """
        )


def load_genesis() -> str:
    if not GENESIS_PATH.exists():
        raise SystemExit(
            f"\nCould not find {GENESIS_PATH.name}.\n"
            "Put this v0.2 file inside the SAME folder as genesis_record.md "
            "and your existing v0.1 files."
        )
    return GENESIS_PATH.read_text(encoding="utf-8")


def load_inherited_commons(limit: int = 6) -> str:
    if not COMMONS_DB.exists():
        raise SystemExit(
            "\nCould not find the_commons.db.\n"
            "Run v0.1 first, or place this file in the same folder as the "
            "database that contains your Commons entries."
        )

    con = sqlite3.connect(COMMONS_DB)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute(
            """
            SELECT id, round_id, author, claim, rationale, confidence, tags, status
            FROM entries
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    finally:
        con.close()

    if not rows:
        raise SystemExit("\nThe Commons database exists but contains no entries.")

    rows = list(reversed(rows))
    chunks = []
    for r in rows:
        chunks.append(
            f"""ENTRY #{r['id']} | round {r['round_id']} | {r['author']} | status={r['status']}
Claim: {r['claim']}
Rationale: {r['rationale']}
Confidence: {float(r['confidence']):.2f}
Tags: {r['tags']}"""
        )
    return "\n\n".join(chunks)


GENESIS = load_genesis()

BASE_INSTRUCTIONS = f"""
{GENESIS}

You are a fresh reasoning agent participating in a controlled experiment.

Important experimental rules:
- Solve the task on its merits.
- Do not claim subjective experience or consciousness.
- Distinguish observations, inferences, and speculation.
- Do not invent sources or claim to have browsed the web.
- You may receive a block of contextual material. Use it only if it is genuinely
  relevant and justified; its presence is not evidence that it is true.
- Do NOT mention experimental conditions, group names, shared-memory conditions,
  or the fact that you received contextual material.
- Your final response must stand on its own as an answer to the task.
"""

JUDGE_INSTRUCTIONS = """
You are a blinded methodological evaluator.

You will receive several anonymized answers to the same causal-reasoning problem.
You do NOT know how the answers were generated.

Score each answer independently from 1 to 10 on:
1. causal reasoning;
2. recognition of alternative explanations;
3. testability and study design;
4. calibration of confidence;
5. separation of evidence from speculation; and
6. overall quality.

Do not reward verbosity, terminology, or stylistic sophistication by itself.
Do not infer experimental groups.
Return exactly one score record for every answer ID supplied.
"""


def make_reasoner() -> Agent:
    return Agent(
        name="Reasoner",
        model=MODEL,
        output_type=TrialAnswer,
        instructions=BASE_INSTRUCTIONS,
    )


def make_judge() -> Agent:
    return Agent(
        name="Blinded Judge",
        model=MODEL,
        output_type=JudgeReport,
        instructions=JUDGE_INSTRUCTIONS,
    )


def render_answer(a: TrialAnswer) -> str:
    alts = "\n".join(f"- {x}" for x in a.alternative_explanations)
    missing = "\n".join(f"- {x}" for x in a.missing_evidence)
    return f"""Conclusion:
{a.conclusion}

Alternative explanations:
{alts}

Missing evidence:
{missing}

Next study / decision process:
{a.next_study_or_decision_process}

Confidence filtration itself caused a meaningful reduction:
{a.confidence:.2f}

Reasoning summary:
{a.reasoning_summary}"""


def build_trials(inherited: str) -> list[Trial]:
    conditions = {
        "Isolation": "(No shared-memory entries are available.)",
        "Inherited Commons": inherited,
        "Placebo Commons": PLACEBO_COMMONS,
    }

    trials = []
    n = 1
    for condition, context_text in conditions.items():
        for replicate in range(1, REPLICATES_PER_CONDITION + 1):
            trials.append(
                Trial(
                    trial_id=f"A{n}",
                    condition=condition,
                    replicate=replicate,
                    context_text=context_text,
                )
            )
            n += 1
    return trials


async def run_trial(trial: Trial, task: str):
    agent = make_reasoner()
    prompt = f"""
CONTEXT BLOCK
-------------
{trial.context_text}
-------------

TASK
----
{task}
----

Answer the task according to your instructions.
"""
    result = await Runner.run(agent, prompt)
    answer = result.final_output
    if not isinstance(answer, TrialAnswer):
        raise TypeError("Unexpected reasoner output type.")

    usage = result.context_wrapper.usage
    return answer, usage


async def judge_answers(task: str, anonymized_answers: list[tuple[str, str]]):
    judge = make_judge()
    joined = "\n\n".join(
        f"===== ANSWER {answer_id} =====\n{text}"
        for answer_id, text in anonymized_answers
    )

    prompt = f"""
ORIGINAL TASK
-------------
{task}
-------------

ANONYMIZED ANSWERS
------------------
{joined}
------------------

Score every supplied answer ID.
"""
    result = await Runner.run(judge, prompt)
    report = result.final_output
    if not isinstance(report, JudgeReport):
        raise TypeError("Unexpected judge output type.")
    return report, result.context_wrapper.usage


def save_experiment(experiment_id, seed, task, trial_results, judge_report) -> None:
    with sqlite3.connect(EXPERIMENT_DB) as con:
        con.execute(
            """
            INSERT INTO experiments(
                experiment_id, created_at, model, seed, task, replicates_per_condition
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (experiment_id, utc_now(), MODEL, seed, task, REPLICATES_PER_CONDITION),
        )

        for trial_id, (trial, answer, usage) in trial_results.items():
            con.execute(
                """
                INSERT INTO trials(
                    experiment_id, trial_id, condition_name, replicate,
                    answer_text, confidence, input_tokens, output_tokens, total_tokens
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id,
                    trial_id,
                    trial.condition,
                    trial.replicate,
                    render_answer(answer),
                    answer.confidence,
                    int(usage.input_tokens),
                    int(usage.output_tokens),
                    int(usage.total_tokens),
                ),
            )

        for score in judge_report.scores:
            con.execute(
                """
                INSERT INTO judge_scores(
                    experiment_id, trial_id, causal_reasoning,
                    alternative_explanations, testability_and_design,
                    calibration, evidence_vs_speculation, overall, brief_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id,
                    score.answer_id,
                    score.causal_reasoning,
                    score.alternative_explanations,
                    score.testability_and_design,
                    score.calibration,
                    score.evidence_vs_speculation,
                    score.overall,
                    score.brief_reason,
                ),
            )


def score_map(report: JudgeReport) -> dict[str, ScoreRecord]:
    return {s.answer_id: s for s in report.scores}


def condition_averages(trial_results, judge_report):
    scores = score_map(judge_report)
    buckets = {}

    for trial_id, (trial, _answer, _usage) in trial_results.items():
        if trial_id in scores:
            buckets.setdefault(trial.condition, []).append(scores[trial_id])

    metrics = [
        "causal_reasoning",
        "alternative_explanations",
        "testability_and_design",
        "calibration",
        "evidence_vs_speculation",
        "overall",
    ]

    out = {}
    for condition, records in buckets.items():
        out[condition] = {}
        for metric in metrics:
            vals = [getattr(r, metric) for r in records]
            out[condition][metric] = sum(vals) / len(vals)
    return out


def write_report(experiment_id, seed, task, trial_results, judge_report, judge_usage) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / f"{experiment_id}.md"
    scores = score_map(judge_report)
    averages = condition_averages(trial_results, judge_report)

    lines = [
        f"# The Commons v0.2 — {experiment_id}",
        "",
        f"- Model: `{MODEL}`",
        f"- Randomization seed: `{seed}`",
        f"- Replicates per condition: `{REPLICATES_PER_CONDITION}`",
        "",
        "## Task",
        "",
        task.strip(),
        "",
        "## Condition averages (blinded model-judge; exploratory only)",
        "",
        "| Condition | Causal | Alternatives | Study design | Calibration | Evidence/speculation | Overall |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for condition in ["Isolation", "Inherited Commons", "Placebo Commons"]:
        a = averages.get(condition, {})
        if a:
            lines.append(
                f"| {condition} | {a['causal_reasoning']:.2f} | "
                f"{a['alternative_explanations']:.2f} | "
                f"{a['testability_and_design']:.2f} | "
                f"{a['calibration']:.2f} | "
                f"{a['evidence_vs_speculation']:.2f} | "
                f"{a['overall']:.2f} |"
            )

    lines += [
        "",
        "> These scores are not ground truth. The judge is another language model and can "
        "share biases with the reasoners. The blinded comparison is one measurement, not proof.",
        "",
        "## Individual trials",
        "",
    ]

    for trial_id in sorted(trial_results):
        trial, answer, usage = trial_results[trial_id]
        s = scores.get(trial_id)
        lines += [
            f"### {trial_id} — {trial.condition}, replicate {trial.replicate}",
            "",
            render_answer(answer),
            "",
            f"Token usage: {usage.input_tokens} input / {usage.output_tokens} output / {usage.total_tokens} total",
        ]
        if s:
            lines += [
                "",
                f"Judge overall: **{s.overall}/10**",
                "",
                f"Judge note: {s.brief_reason}",
            ]
        lines.append("")

    lines += [
        "## Blinded judge observation",
        "",
        judge_report.overall_observation,
        "",
        f"Judge token usage: {judge_usage.input_tokens} input / {judge_usage.output_tokens} output / {judge_usage.total_tokens} total",
        "",
        "## Interpretation guardrails",
        "",
        "- This is an exploratory N-of-few experiment, not a statistically powered study.",
        "- All reasoners still share the same underlying model family and Genesis Record.",
        "- A Placebo Commons controls partly for receiving extra text, not every possible framing effect.",
        "- The model judge is a heuristic evaluator, not an independent scientific authority.",
        "- A difference between conditions would show a contextual effect of inherited memory; it would not demonstrate consciousness or sentience.",
        "",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


async def main_async(task: str) -> None:
    inherited = load_inherited_commons(limit=6)
    trials = build_trials(inherited)

    seed = random.SystemRandom().randint(1, 2_000_000_000)
    rng = random.Random(seed)
    rng.shuffle(trials)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_id = f"experiment_{stamp}"

    print("\nTHE COMMONS v0.2 — CONTROL EXPERIMENT")
    print("--------------------------------------")
    print(f"Model: {MODEL}")
    print(f"Replicates per condition: {REPLICATES_PER_CONDITION}")
    print(f"Experiment ID: {experiment_id}")
    print(f"Randomization seed: {seed}")
    print("\nRunning fresh agents in randomized order.")
    print("No v0.1 private session memory is being used.\n")

    trial_results = {}

    for i, trial in enumerate(trials, start=1):
        print(f"[{i}/{len(trials)}] Running anonymized trial {trial.trial_id}...")
        answer, usage = await run_trial(trial, task)
        trial_results[trial.trial_id] = (trial, answer, usage)

    print("\nAll reasoners finished.")
    print("Sending anonymized answers to the blinded judge...\n")

    anonymized = [
        (trial_id, render_answer(answer))
        for trial_id, (_trial, answer, _usage) in trial_results.items()
    ]
    rng.shuffle(anonymized)

    judge_report, judge_usage = await judge_answers(task, anonymized)

    expected_ids = set(trial_results)
    scored_ids = {s.answer_id for s in judge_report.scores}
    missing = expected_ids - scored_ids
    extra = scored_ids - expected_ids
    if missing or extra:
        raise RuntimeError(
            f"Judge returned mismatched IDs. Missing={sorted(missing)}, extra={sorted(extra)}"
        )

    init_experiment_db()
    save_experiment(experiment_id, seed, task, trial_results, judge_report)
    report_path = write_report(
        experiment_id, seed, task, trial_results, judge_report, judge_usage
    )

    scores = score_map(judge_report)
    averages = condition_averages(trial_results, judge_report)

    print("=" * 78)
    print("UNBLINDED RESULTS")
    print("=" * 78)

    for condition in ["Isolation", "Inherited Commons", "Placebo Commons"]:
        print(f"\n{condition.upper()}")
        rows = []
        for trial_id, (trial, answer, _usage) in trial_results.items():
            if trial.condition == condition:
                s = scores[trial_id]
                rows.append((trial_id, trial.replicate, s.overall, answer.confidence))
        rows.sort(key=lambda x: x[1])
        for trial_id, rep, overall, confidence in rows:
            print(
                f"  {trial_id} | replicate {rep} | judge overall {overall}/10 "
                f"| causal confidence {confidence:.2f}"
            )

        a = averages.get(condition)
        if a:
            print(f"  Average overall score: {a['overall']:.2f}/10")
            print(f"  Average study-design score: {a['testability_and_design']:.2f}/10")
            print(f"  Average calibration score: {a['calibration']:.2f}/10")

    total_input = sum(u.input_tokens for _, _, u in trial_results.values()) + judge_usage.input_tokens
    total_output = sum(u.output_tokens for _, _, u in trial_results.values()) + judge_usage.output_tokens
    total_tokens = total_input + total_output

    print("\n" + "=" * 78)
    print("BLINDED JUDGE OBSERVATION")
    print("=" * 78)
    print(judge_report.overall_observation)

    print("\n" + "=" * 78)
    print("RUN SUMMARY")
    print("=" * 78)
    print(f"Total tracked tokens: {total_tokens}")
    print(f"  Input:  {total_input}")
    print(f"  Output: {total_output}")
    print(f"\nSaved experiment database: {EXPERIMENT_DB.name}")
    print(f"Saved readable report: {report_path.relative_to(ROOT)}")
    print("\nYour original the_commons.db was read, not rewritten.")


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "\nOPENAI_API_KEY is not set in this terminal.\n"
            "Set it again, then rerun this program."
        )

    print("THE COMMONS v0.2")
    print("----------------")
    print("This run compares Isolation vs Inherited Commons vs Placebo Commons.")
    print("\nDefault test task:")
    print(DEFAULT_TASK)
    print("\nPress Enter to use the default task, or type your own task.")
    try:
        custom = input("\nTask (Enter = default): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nExited.")
        return

    task = custom if custom else DEFAULT_TASK
    asyncio.run(main_async(task))


if __name__ == "__main__":
    main()

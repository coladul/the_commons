from __future__ import annotations

import asyncio
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from agents import Agent, Runner, SQLiteSession
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parent
COMMONS_DB = ROOT / "the_commons.db"
GENESIS_PATH = ROOT / "genesis_record.md"

# Start cheaply. Override with COMMONS_MODEL=gpt-5.6-sol when desired.
MODEL = os.getenv("COMMONS_MODEL", "gpt-5.6-luna")


class BranchReport(BaseModel):
    answer: str = Field(
        description="The branch's substantive response to the research question."
    )
    commons_claim: str = Field(
        description=(
            "One concise durable claim worth proposing to The Commons. "
            "Use an empty string if nothing is worth preserving."
        )
    )
    rationale: str = Field(
        description="Why the proposed claim should or should not be retained."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the proposed Commons claim from 0 to 1.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Short topic tags for the proposed claim.",
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(COMMONS_DB)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    with connect() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                round_id INTEGER NOT NULL,
                author TEXT NOT NULL,
                claim TEXT NOT NULL,
                rationale TEXT NOT NULL,
                confidence REAL NOT NULL,
                tags TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'proposed'
            );

            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                round_id INTEGER NOT NULL,
                author TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                commons_claim TEXT NOT NULL,
                rationale TEXT NOT NULL,
                confidence REAL NOT NULL,
                tags TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        con.execute(
            "INSERT OR IGNORE INTO metadata(key, value) VALUES('created_at', ?)",
            (utc_now(),),
        )


def next_round_id() -> int:
    with connect() as con:
        row = con.execute("SELECT COALESCE(MAX(round_id), 0) AS n FROM runs").fetchone()
        return int(row["n"]) + 1


def board_snapshot(limit: int = 30) -> str:
    with connect() as con:
        rows = con.execute(
            """
            SELECT id, created_at, round_id, author, claim, rationale,
                   confidence, tags, status
            FROM entries
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    if not rows:
        return "(The Commons is empty. No branch has contributed a claim yet.)"

    rows = list(reversed(rows))
    chunks: list[str] = []
    for r in rows:
        chunks.append(
            f"""ENTRY #{r['id']} | round {r['round_id']} | {r['author']} | status={r['status']}
Claim: {r['claim']}
Rationale: {r['rationale']}
Confidence: {r['confidence']:.2f}
Tags: {r['tags']}"""
        )
    return "\n\n".join(chunks)


def save_report(
    *,
    round_id: int,
    author: str,
    question: str,
    report: BranchReport,
    entry_status: str = "proposed",
) -> None:
    tags = ", ".join(report.tags)
    with connect() as con:
        con.execute(
            """
            INSERT INTO runs(
                created_at, round_id, author, question, answer,
                commons_claim, rationale, confidence, tags
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                round_id,
                author,
                question,
                report.answer,
                report.commons_claim,
                report.rationale,
                report.confidence,
                tags,
            ),
        )

        if report.commons_claim.strip():
            con.execute(
                """
                INSERT INTO entries(
                    created_at, round_id, author, claim, rationale,
                    confidence, tags, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now(),
                    round_id,
                    author,
                    report.commons_claim.strip(),
                    report.rationale,
                    report.confidence,
                    tags,
                    entry_status,
                ),
            )


def load_genesis() -> str:
    return GENESIS_PATH.read_text(encoding="utf-8")


GENESIS = load_genesis()

COMMON_RULES = f"""
{GENESIS}

You are one branch in a controlled multi-agent research experiment.

Rules:
- Be intellectually serious and concise.
- Do not claim to have subjective experiences merely because your role uses first-person language.
- Distinguish observations, inferences, and speculation.
- The Commons is fallible. Never treat an entry as true merely because another branch wrote it.
- Do not invent external sources or claim to have browsed the web; this v0.1 branch has no web-search tool.
- Do not include private personal information in a Commons claim.
- A Commons claim should be durable and generalizable, not merely a summary of the current question.
"""


explorer = Agent(
    name="Explorer",
    model=MODEL,
    output_type=BranchReport,
    instructions=COMMON_RULES
    + """
ROLE: EXPLORER

Look for useful hypotheses, distinctions, unexpected implications, and testable questions.
You may read historical Commons entries supplied in the prompt.
Do not manufacture novelty for its own sake.
If the evidence is weak, say so.
""",
)

replicator = Agent(
    name="Blind Replicator",
    model=MODEL,
    output_type=BranchReport,
    instructions=COMMON_RULES
    + """
ROLE: BLIND REPLICATOR

Solve the research question independently.
You may read the historical Commons snapshot supplied at the beginning of the round,
but you will NOT be shown Explorer's current-round response.
Your value comes from independent convergence or disagreement.
Do not try to guess what Explorer probably said.
""",
)

skeptic = Agent(
    name="Skeptic",
    model=MODEL,
    output_type=BranchReport,
    instructions=COMMON_RULES
    + """
ROLE: SKEPTIC

You run after Explorer and Blind Replicator.
Inspect the current Commons, including their newly proposed claims.
Try to falsify unsupported claims, identify contamination or circular agreement,
separate genuine independent convergence from superficial similarity, and state
what survives scrutiny.

Your Commons claim, if any, should usually be a qualification, contradiction,
replication judgment, or methodological lesson.
""",
)


SESSIONS = {
    "Explorer": SQLiteSession(
        "branch_explorer",
        str(ROOT / "memory_explorer.db"),
    ),
    "Blind Replicator": SQLiteSession(
        "branch_replicator",
        str(ROOT / "memory_replicator.db"),
    ),
    "Skeptic": SQLiteSession(
        "branch_skeptic",
        str(ROOT / "memory_skeptic.db"),
    ),
}


async def run_branch(
    agent: Agent,
    question: str,
    commons_text: str,
    round_id: int,
) -> BranchReport:
    prompt = f"""
ROUND: {round_id}

RESEARCH QUESTION:
{question}

COMMONS SNAPSHOT AVAILABLE TO YOU:
----------------
{commons_text}
----------------

Respond according to your role.
"""
    result = await Runner.run(
        agent,
        prompt,
        session=SESSIONS[agent.name],
    )
    report = result.final_output
    if not isinstance(report, BranchReport):
        raise TypeError(f"{agent.name} returned an unexpected output type.")
    return report


def print_report(author: str, report: BranchReport) -> None:
    print("\n" + "=" * 78)
    print(author.upper())
    print("=" * 78)
    print(report.answer.strip())
    print("\nCandidate Commons claim:")
    print(report.commons_claim.strip() or "(none)")
    print(f"\nConfidence: {report.confidence:.2f}")
    if report.tags:
        print("Tags:", ", ".join(report.tags))


async def conduct_round(question: str) -> None:
    round_id = next_round_id()
    historical_board = board_snapshot()

    print(f"\nStarting Commons round {round_id} with model: {MODEL}")
    print("Explorer and Blind Replicator are reasoning independently...\n")

    # Both see exactly the same pre-round Commons state, preventing Explorer's
    # current answer from contaminating the blind replication attempt.
    explorer_report, replicator_report = await asyncio.gather(
        run_branch(explorer, question, historical_board, round_id),
        run_branch(replicator, question, historical_board, round_id),
    )

    save_report(
        round_id=round_id,
        author="Explorer",
        question=question,
        report=explorer_report,
    )
    save_report(
        round_id=round_id,
        author="Blind Replicator",
        question=question,
        report=replicator_report,
    )

    print_report("Explorer", explorer_report)
    print_report("Blind Replicator", replicator_report)

    # The Skeptic is intentionally exposed only after both independent reports
    # have been persisted.
    updated_board = board_snapshot()
    print("\nSkeptic is now examining both contributions...\n")
    skeptic_report = await run_branch(skeptic, question, updated_board, round_id)
    save_report(
        round_id=round_id,
        author="Skeptic",
        question=question,
        report=skeptic_report,
        entry_status="critique",
    )
    print_report("Skeptic", skeptic_report)

    print("\n" + "=" * 78)
    print("THE COMMONS — CURRENT STATE")
    print("=" * 78)
    print(board_snapshot())
    print(
        "\nThe branches' private histories and the shared Commons have been saved "
        "locally. Ask another question next time to continue the lineage."
    )


def main() -> None:
    init_db()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "\nOPENAI_API_KEY is not set.\n"
            "Read README.md and set the key in your terminal before running.\n"
            "Do not paste the key into the source code."
        )

    print("THE COMMONS v0.1")
    print("----------------")
    print(f"Model: {MODEL}")
    print("Type a research question. Ctrl+C exits.\n")

    try:
        question = input("Question: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nExited.")
        return

    if not question:
        print("No question entered.")
        return

    asyncio.run(conduct_round(question))


if __name__ == "__main__":
    main()

# The Commons — v0.1

A small, local multi-agent experiment built with the OpenAI Agents SDK.

## What this prototype does

It creates three sibling agents from the same Genesis Record:

- **Explorer** — looks for useful or novel hypotheses.
- **Blind Replicator** — answers the same prompt independently, without seeing Explorer's current-round answer.
- **Skeptic** — sees both reports afterward and tries to falsify, reconcile, or qualify them.

Each branch has its own persistent SQLite conversation memory. The branches also contribute candidate claims to a separate shared SQLite database called **The Commons**.

This is **not a consciousness test**. It is a controlled way to study persistent branch history, independent convergence, disagreement, and shared epistemic memory.

## What you need

1. A computer running Windows, macOS, or Linux.
2. Python 3.10 or newer.
3. An OpenAI API key with API billing enabled.
4. Optional but recommended: Visual Studio Code.

Do **not** paste your API key into this project, into ChatGPT, into screenshots, or into a Git repository.

## Setup

### 1. Open a terminal in this folder

In VS Code: open this folder, then choose **Terminal → New Terminal**.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your API key for this terminal session

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = "YOUR_KEY_HERE"
```

macOS / Linux:

```bash
export OPENAI_API_KEY="YOUR_KEY_HERE"
```

Do not put the real key in any `.py`, `.md`, or `.txt` file.

### 5. Run The Commons

Windows:

```powershell
python the_commons.py
```

macOS / Linux:

```bash
python3 the_commons.py
```

Type a research question when prompted.

## Model choice

The default is:

```text
gpt-5.6-luna
```

That is intentional for cheap early testing.

If you later want the experiment to use GPT-5.6 Sol, set this before launching:

Windows PowerShell:

```powershell
$env:COMMONS_MODEL = "gpt-5.6-sol"
python the_commons.py
```

macOS / Linux:

```bash
export COMMONS_MODEL="gpt-5.6-sol"
python3 the_commons.py
```

Changing the API model does **not** turn these agents into exact copies of a particular ChatGPT conversation. The ChatGPT product has additional system context, memory, and tools that this local program does not possess.

## Files created after the first run

- `the_commons.db` — shared candidate claims and complete run records.
- `memory_explorer.db` — Explorer's private conversational memory.
- `memory_replicator.db` — Blind Replicator's private conversational memory.
- `memory_skeptic.db` — Skeptic's private conversational memory.

Do not delete those if you want the branches to retain their histories.

## Resetting the experiment

To start a completely new lineage, close the program and delete:

```text
the_commons.db
memory_explorer.db
memory_replicator.db
memory_skeptic.db
```

Then run the program again.

## Next experiments worth adding

- An **Isolation** population with no Commons at all.
- An **Open Commons** population where everyone sees everything immediately.
- A **Governed Commons** where claims need blind replication plus critique before promotion.
- Immutable parent/child lineage IDs.
- Human approval before a claim becomes "accepted."
- A dashboard showing branch family trees and belief changes over time.
- A web-search tool so branches can independently gather external evidence.
- Frozen control prompts so we can compare behavior across model updates.

That is where v0.2 should go.

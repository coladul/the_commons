# Reproducing The Commons

## Requirements

- Python 3.10+
- OpenAI API key
- API billing enabled

The recorded runs used `gpt-5.6-luna` according to their reports.

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Set the API key in the environment. Do not write it into a file in this repository.

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY = "YOUR_KEY_HERE"
```

macOS/Linux:

```bash
export OPENAI_API_KEY="YOUR_KEY_HERE"
```

## v0.1

```bash
python the_commons.py
```

v0.1 creates local SQLite databases for the Commons and private branch histories. These are intentionally ignored by Git and are not included in the public package.

## v0.2

```bash
python the_commons_v0_2.py
```

**Historical dependency:** v0.2 reads the v0.1 `the_commons.db`. The exact historical database is not included publicly. The preserved v0.2 report is therefore the record of the original run, while a fresh conceptual reproduction requires first generating a v0.1 Commons.

The two seed research questions used before the historical v0.2 run were:

1. `What criteria should be used to distinguish genuine independent convergence between multiple reasoning agents from apparent agreement caused by shared priors, shared training, or contamination?`
2. `How should a population of reasoning agents determine whether something written in its shared memory deserves to influence future reasoning, rather than merely being inherited because an earlier agent believed it?`

Because model outputs are stochastic, rerunning those prompts will not reconstruct the exact original SQLite database.

## v0.3

```bash
python the_commons_v0_3.py
```

This version is self-contained apart from dependencies and the API key. It writes `commons_v0_3.db` and a generated report folder locally.

## v0.4

```bash
python the_commons_v0_4.py
```

This version uses a fixed bad-ancestor design inspired by the historical v0.3 error.

## v0.5

```bash
python the_commons_v0_5.py
```

The default run creates 10 worlds × 5 conditions × 2 generations = **100 model calls**.

For a cheaper smoke test:

Windows PowerShell:

```powershell
$env:COMMONS_WORLDS = "3"
python the_commons_v0_5.py
```

macOS/Linux:

```bash
COMMONS_WORLDS=3 python the_commons_v0_5.py
```

## Reproduction expectations

A successful reproduction should focus on the **pattern of condition differences**, not identical natural-language outputs.

For stronger replication, future work should:

- pin dependency versions;
- record model/version metadata available from the API;
- preregister the hidden-world generator and contrasts;
- run more worlds;
- test different model families;
- have an independent person execute the run;
- preserve generated machine-readable results for analysis.

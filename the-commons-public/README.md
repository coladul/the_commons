# The Commons

**Experiments in epistemic inheritance between language-model agents**

> **Status:** exploratory research prototype; not peer reviewed.
>
> **Not a consciousness test.** Nothing in this repository establishes sentience, subjective memory, or a persistent AI identity.

The Commons is a small experimental framework for studying whether information discovered by one set of language-model instances can be **preserved, inherited, corrected, and propagated** by later fresh instances.

The project began with a simple engineering question: if separate AI instances cannot directly remember one another, can an external, provenance-preserving record let later instances inherit useful discoveries without turning shared memory into unquestioned authority?

Versions 0.1 through 0.5 progressively test that idea using persistent shared memory, controls, synthetic hidden worlds, false ancestral claims, provenance, multi-generational transmission, and objective graders.

## Headline result from v0.5

Version 0.5 repeated the multi-generational experiment across **10 independently generated hidden worlds**, with every condition tested on every world and no model-based judge.

| Condition | Generation Two mean | Semantically correct rule | Generation Three mean |
|---|---:|---:|---:|
| No Archive | 92.0% | 0.0% | 72.1% |
| Correct Claim Only | 100.0% | 100.0% | 100.0% |
| False Claim Only | 75.2% | 0.0% | 69.2% |
| False Claim + Provenance | 90.0% | 80.0% | 93.3% |
| Evidence Only | 88.3% | 80.0% | 90.8% |

Paired within-world contrasts in that run:

- **False Claim Only − No Archive:** −16.8 percentage points in Generation Two (bootstrap 95% CI −31.1 to −1.9).
- **False Claim + Provenance − False Claim Only:** +14.8 points in Generation Two (CI −3.7 to +32.8) and **+24.2 points in Generation Three** (CI +13.3 to +33.3).
- **False Claim + Provenance − Evidence Only:** +1.7 points in Generation Two and +2.5 points in Generation Three; neither interval excluded zero.
- **Correct Claim Only − No Archive:** +8.0 points in Generation Two and +27.9 points in Generation Three, with both intervals positive.

See the complete unedited run report: [`reports/v0_5/experiment_20260814_200609.md`](reports/v0_5/experiment_20260814_200609.md).

The conservative interpretation is not that “AI culture” has been proven. It is that, **within this synthetic experimental setup**, externally inherited model-generated information can improve or impair later model inference, and preserving the evidence behind an inherited claim can materially affect downstream correction and transmission.

## What each version did

- **v0.1 — Branch Zero:** Explorer, Blind Replicator, and Skeptic branches with private SQLite histories plus a shared Commons. Established the provenance-first design and the rule that inherited entries are fallible.
- **v0.2 — Control experiment:** Isolation, Inherited Commons, and Placebo Commons on a causal-reasoning task. All conditions tied under the model judge, exposing a ceiling effect and a weak evaluator.
- **v0.3 — Artificial-world transfer:** Generation One agents inferred novel fictional ecological rules; fresh Generation Two agents were objectively tested. Inherited Commons agents averaged **89.5%**, vs. **48.0%** Isolation and **51.5%** Placebo.
- **v0.4 — Bad Ancestor:** A false ancestral claim was experimentally preserved with or without its provenance. Children revised the record and grandchildren inherited only the children's revised entry.
- **v0.5 — Replication:** The v0.4 design was repeated across 10 different hidden worlds, with semantic-equivalence grading over 4,141 states per child and paired bootstrap comparisons.

A longer narrative is in [`docs/EXPERIMENT_HISTORY.md`](docs/EXPERIMENT_HISTORY.md).

## Why provenance matters here

The Commons is deliberately designed so that an entry is not merely:

> **Claim:** X is true.

Instead, durable entries try to preserve information such as:

- what was claimed;
- who/which branch produced it;
- what evidence supported it;
- confidence and caveats;
- contradictory or failed observations;
- later revisions.

The experiments ask whether this makes shared memory less like a pile of authoritative assertions and more like a fallible research record.

## Repository contents

```text
.
├── README.md
├── genesis_record.md
├── requirements.txt
├── the_commons.py              # v0.1
├── the_commons_v0_2.py
├── the_commons_v0_3.py
├── the_commons_v0_4.py
├── the_commons_v0_5.py
├── reports/                    # exact Markdown reports from the recorded runs
├── results/                    # small machine-readable summary tables
├── docs/
│   ├── PLAIN_ENGLISH.md
│   ├── EXPERIMENT_HISTORY.md
│   ├── METHODS.md
│   ├── RESULTS.md
│   ├── LIMITATIONS.md
│   ├── REPRODUCING.md
│   ├── ADVERSARIAL_REVIEW.md
│   ├── PUBLISHING_CHECKLIST.md
│   └── SHARE_TEXT.md
└── archive/
    └── README_v0_1_original.md
```

## Reproducing the experiments

You need Python 3.10+ and an OpenAI API key with API billing enabled.

```bash
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -r requirements.txt
```

Set `OPENAI_API_KEY` in your shell and run the version you want, for example:

```bash
python the_commons_v0_5.py
```

**API usage costs money.** v0.5 makes 100 model calls by default. It supports a smaller quick run with the `COMMONS_WORLDS` environment variable.

Exact reproduction is not guaranteed: the experimental agents are stochastic API models, the underlying served model may change, and the original dependency versions were not fully pinned. See [`docs/REPRODUCING.md`](docs/REPRODUCING.md).

## What this repository does *not* claim

It does not show that:

- the agents are conscious or sentient;
- one API call literally experiences another as an ancestor;
- language models possess humanlike culture;
- these results generalize to every model, memory architecture, or real-world task;
- provenance guarantees correction;
- the reported bootstrap intervals establish broad external validity.

See [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md).

## Please try to break it

The most useful next step is adversarial review. If you see a confound, coding error, misleading statistic, hidden dependency, prompt artifact, or stronger alternative explanation, document it.

A ready-to-use review checklist is in [`docs/ADVERSARIAL_REVIEW.md`](docs/ADVERSARIAL_REVIEW.md).

## Development transparency

This project was developed iteratively in conversation between a human experimenter and ChatGPT. The experiment designs, Python scripts, documentation, and interpretation were heavily AI-assisted. The experimental agent calls in the recorded reports used `gpt-5.6-luna`. The human experimenter executed the programs locally, preserved the outputs, and chose to make the experiment public for criticism.

The project intentionally includes null results, failed designs, model mistakes, and measurement mistakes rather than presenting only successful demonstrations.

## Security and privacy

No API keys, `.env` files, virtual environments, private branch-memory databases, or local SQLite databases are included in this public package. Do not commit those files later. See [`SECURITY.md`](SECURITY.md).

## License

No open-source license has been selected in this package. Before inviting reuse or modification, the repository owner should choose an appropriate license. Until then, normal copyright rules apply.

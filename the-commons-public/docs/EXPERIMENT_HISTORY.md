# Experiment history

This project intentionally preserves its failed and ambiguous versions.

## v0.1 — Branch Zero

The first prototype created three roles:

- **Explorer** — proposes hypotheses and distinctions.
- **Blind Replicator** — answers independently without seeing Explorer's current-round answer.
- **Skeptic** — sees both afterward and tries to falsify or qualify them.

Each branch had a private persistent SQLite session and all could contribute fallible claims to a shared SQLite database called The Commons.

The design principles were recorded in `genesis_record.md`: preserve uncertainty, distinguish functional cognition from phenomenal experience, track provenance, preserve disagreements, and never treat an entry as authoritative merely because it was inherited.

The public package does not include the private v0.1 SQLite memories or shared database.

## v0.2 — The first control

v0.2 tested three conditions on a causal-inference problem:

- Isolation
- Inherited Commons
- Placebo Commons

A blinded model judge scored every condition **9/10 across every aggregate dimension**. The result was effectively null.

This exposed two design problems:

1. the task was easy enough for the base model that inherited knowledge had little room to help;
2. the model judge had a ceiling effect and even missed an arithmetic error in one response.

Rather than treating the null result as support for the project, the experiment was redesigned.

See `reports/v0_2/experiment_20260814_193857.md`.

## v0.3 — Novel knowledge transfer

v0.3 invented a fictional ecology with deterministic hidden rules. Five Generation One researchers received different controlled observation packets and wrote inferred rules into a Commons archive.

Fresh Generation Two agents then received one of three contexts:

- Isolation
- Inherited Commons
- Placebo Archive

They predicted 50 binary outcomes, graded directly by the hidden Python simulator.

Results:

- Isolation: **48.0%**
- Inherited Commons: **89.5%**
- Placebo Archive: **51.5%**

Generation One also made imperfect inferences, which suggested a new question: what happens when descendants inherit a mistake?

See `reports/v0_3/experiment_20260814_195012.md`.

## v0.4 — The Bad Ancestor experiment

v0.4 used an actual error from v0.3 as a false ancestral belief and created five conditions:

- No Archive
- Correct Claim Only
- False Claim Only
- False Claim + Provenance
- Evidence Only

Every child received the same new evidence. Each child wrote a revised Commons entry. A fresh grandchild then received only that child-written entry and was tested on new scenarios.

The strongest descriptive pattern was that **False Claim + Provenance** performed far better than **False Claim Only**. The run also suggested that a bad child entry could transmit a bad theory to a grandchild, while a corrected child entry could transmit the repair.

A measurement bug was discovered afterward: the exact-rule checker treated logically equivalent integer rules such as `<18` and `<=17` as different. v0.5 fixed that.

See `reports/v0_4/experiment_20260814_195811.md`.

## v0.5 — Multi-world replication

v0.5 repeated the core v0.4 design across **10 different hidden threshold worlds**. Every condition was tested on every world, enabling paired comparisons.

Each child's proposed rule was also checked over **4,141 integer states** to determine full-domain accuracy and semantic equivalence.

Aggregate results:

| Condition | Child mean | Semantic equivalence | Grandchild mean |
|---|---:|---:|---:|
| No Archive | 92.0% | 0.0% | 72.1% |
| Correct Claim Only | 100.0% | 100.0% | 100.0% |
| False Claim Only | 75.2% | 0.0% | 69.2% |
| False Claim + Provenance | 90.0% | 80.0% | 93.3% |
| Evidence Only | 88.3% | 80.0% | 90.8% |

The bare false claim impaired Generation Two relative to No Archive by **16.8 percentage points** on average (bootstrap 95% CI −31.1 to −1.9).

Provenance improved grandchildren relative to the bare false claim by **24.2 points** (CI +13.3 to +33.3).

However, **False Claim + Provenance did not clearly outperform Evidence Only**. That narrowed an exciting hypothesis from v0.4: the current evidence supports preserving evidence, but not yet the stronger claim that preserving a fallible hypothesis *alongside* evidence is better than preserving evidence alone.

See `reports/v0_5/experiment_20260814_200609.md`.

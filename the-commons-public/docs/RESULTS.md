# Results summary

## v0.2: null / ceiling-effect result

The blinded model judge gave all three conditions aggregate 9/10 scores. This version did not detect a Commons effect and motivated objective hidden-world grading.

## v0.3: useful information transferred

Generation Two objective accuracy:

| Condition | Mean accuracy |
|---|---:|
| Isolation | 48.0% |
| Inherited Commons | 89.5% |
| Placebo Commons | 51.5% |

This established that model-generated discoveries could be placed in an external archive and improve later fresh instances on novel scenarios in the synthetic world.

## v0.4: false inheritance and correction

| Condition | Child mean | Grandchild mean |
|---|---:|---:|
| No Archive | 72.9% | 78.1% |
| Correct Claim Only | 97.9% | 97.9% |
| False Claim Only | 63.5% | 70.8% |
| False Claim + Provenance | 97.9% | 96.9% |
| Evidence Only | 77.1% | 72.9% |

This single-world result suggested a large provenance benefit, but it required replication and contained an overly literal exact-rule metric.

## v0.5: repeated hidden worlds

| Condition | Child mean | Child bootstrap 95% CI | Semantic-equivalence rate | Grandchild mean | Grandchild bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|
| No Archive | 92.0% | 84.0–97.7% | 0.0% | 72.1% | 68.8–74.6% |
| Correct Claim Only | 100.0% | 100.0–100.0% | 100.0% | 100.0% | 100.0–100.0% |
| False Claim Only | 75.2% | 61.5–88.7% | 0.0% | 69.2% | 65.4–72.5% |
| False Claim + Provenance | 90.0% | 75.1–100.0% | 80.0% | 93.3% | 83.8–100.0% |
| Evidence Only | 88.3% | 71.1–100.0% | 80.0% | 90.8% | 77.1–100.0% |

### Paired v0.5 contrasts

| Contrast | Generation Two | Generation Three |
|---|---:|---:|
| False Claim Only − No Archive | −16.8% (CI −31.1 to −1.9) | −2.9% (CI −7.1 to +0.8) |
| False Claim + Provenance − False Claim Only | +14.8% (CI −3.7 to +32.8) | +24.2% (CI +13.3 to +33.3) |
| False Claim + Provenance − Evidence Only | +1.7% (CI −13.9 to +17.4) | +2.5% (CI −9.6 to +15.4) |
| Correct Claim Only − No Archive | +8.0% (CI +2.3 to +15.9) | +27.9% (CI +25.0 to +31.2) |

## Current conservative interpretation

Within this specific family of synthetic threshold tasks:

1. correct inherited knowledge is strongly useful;
2. a confident bare false claim can bias later inference even when the model explicitly says it revised the claim;
3. preserving the evidence behind an inherited false claim can substantially improve downstream correction and grandchild performance;
4. the current data do **not** show a clear advantage of "false claim + provenance" over "evidence only";
5. provenance does not guarantee correct reasoning: individual provenance conditions still produced confidently wrong rules in some worlds.

The full reports should be treated as the source of record.

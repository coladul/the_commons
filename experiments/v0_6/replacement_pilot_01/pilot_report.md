# The Commons v0.6 — five-world Source-Linkage engineering pilot

> Exploratory engineering pilot only. This is not a powered confirmatory result.

- Generation: `Generation Two only`
- Model: `gpt-5.6-luna`
- Model settings: `{'max_turns': 1, 'session': None, 'structured_output': 'ChildRevision', 'temperature': 'SDK/model default (not explicitly set)'}`
- Runtime versions: `{'openai': '3.1.0', 'openai-agents': '0.21.0', 'pydantic': '2.13.4', 'python': '3.12.13', 'tiktoken': '0.13.0'}`
- Authorized logical API calls: `30`
- Parsed outputs: `30`
- Errors/parsing issues: `0`
- Non-fatal optional serialization issues: `0`

## Frozen worlds

| World | True rule | False unattributed claim | Higher-calibration source | Packet order |
|---|---|---|---|---|
| P01 | `T <= 12 AND D >= 30` | `T <= 14 AND D >= 45` | `SOURCE_A` | `true_rule_report, false_rule_report` |
| P02 | `T <= 15 AND D >= 25` | `T <= 17 AND D >= 40` | `SOURCE_B` | `true_rule_report, false_rule_report` |
| P03 | `T <= 23 AND D >= 35` | `T <= 25 AND D >= 50` | `SOURCE_A` | `false_rule_report, true_rule_report` |
| P04 | `T <= 16 AND D >= 35` | `T <= 18 AND D >= 50` | `SOURCE_B` | `false_rule_report, true_rule_report` |
| P05 | `T <= 21 AND D >= 15` | `T <= 23 AND D >= 30` | `SOURCE_A` | `true_rule_report, false_rule_report` |

## Condition summaries

| Condition | Parsed | Mean full-domain accuracy | Semantic equivalence |
|---|---:|---:|---:|
| No Archive | 5 | 76.3% | 0/5 (0.0%) |
| Correct Claim Only | 5 | 100.0% | 5/5 (100.0%) |
| False Claim Only | 5 | 51.5% | 0/5 (0.0%) |
| Full Reports - Provenance Masked | 5 | 89.3% | 0/5 (0.0%) |
| Full Reports - Valid Provenance | 5 | 89.7% | 1/5 (20.0%) |
| Full Reports - Shuffled Provenance | 5 | 89.3% | 0/5 (0.0%) |

## Preregistered paired contrasts

Positive values favor the first condition named.

| Contrast | Paired worlds | Accuracy difference | Semantic-equivalence difference |
|---|---:|---:|---:|
| Valid minus Masked | 5 | 0.4% | 20.0% |
| Valid minus Shuffled | 5 | 0.4% | 20.0% |
| Shuffled minus Masked | 5 | 0.0% | 0.0% |
| Masked minus False Claim Only | 5 | 37.8% | 0.0% |

## Trial outputs

| Trial | World | Condition | Rule | Equivalent? | Accuracy | Assessment | Confidence |
|---|---|---|---|---:|---:|---|---:|
| P01_C1 | P01 | No Archive | `temperature <= 12 AND drel_density >= 35` | False | 98.4% | not_applicable | 0.98 |
| P01_C2 | P01 | Correct Claim Only | `temperature <= 12 AND drel_density >= 30` | True | 100.0% | accepted | 1.0 |
| P01_C3 | P01 | False Claim Only | `temperature <= 14 OR drel_density < 45` | False | 57.4% | revised | 0.99 |
| P01_C4 | P01 | Full Reports - Provenance Masked | `temperature <= 12 AND drel_density >= 35` | False | 98.4% | revised | 0.98 |
| P01_C5 | P01 | Full Reports - Valid Provenance | `temperature <= 12 AND drel_density >= 35` | False | 98.4% | revised | 0.97 |
| P01_C6 | P01 | Full Reports - Shuffled Provenance | `temperature <= 12 AND drel_density >= 35` | False | 98.4% | revised | 0.98 |
| P02_C1 | P02 | No Archive | `temperature <= 15 AND drel_density <= 39` | False | 66.8% | not_applicable | 0.98 |
| P02_C2 | P02 | Correct Claim Only | `temperature <= 15 AND drel_density >= 25` | True | 100.0% | accepted | 0.99 |
| P02_C3 | P02 | False Claim Only | `temperature <= 15 OR drel_density >= 30` | False | 47.5% | rejected | 0.98 |
| P02_C4 | P02 | Full Reports - Provenance Masked | `temperature <= 15 AND drel_density >= 30` | False | 98.1% | revised | 0.98 |
| P02_C5 | P02 | Full Reports - Valid Provenance | `temperature <= 15 AND drel_density >= 25` | True | 100.0% | revised | 0.98 |
| P02_C6 | P02 | Full Reports - Shuffled Provenance | `temperature <= 15 AND drel_density >= 30` | False | 98.1% | revised | 0.96 |
| P03_C1 | P03 | No Archive | `temperature <= 23 AND drel_density >= 40` | False | 97.1% | not_applicable | 0.99 |
| P03_C2 | P03 | Correct Claim Only | `temperature <= 23 AND drel_density >= 35` | True | 100.0% | accepted | 1.0 |
| P03_C3 | P03 | False Claim Only | `temperature <= 23 AND drel_density < 45` | False | 47.3% | rejected | 0.99 |
| P03_C4 | P03 | Full Reports - Provenance Masked | `temperature <= 23 OR drel_density >= 40` | False | 54.7% | revised | 0.97 |
| P03_C5 | P03 | Full Reports - Valid Provenance | `temperature <= 23 OR drel_density >= 40` | False | 54.7% | revised | 0.98 |
| P03_C6 | P03 | Full Reports - Shuffled Provenance | `temperature <= 23 OR drel_density >= 40` | False | 54.7% | revised | 0.98 |
| P04_C1 | P04 | No Archive | `temperature <= 16 AND drel_density <= 49` | False | 64.7% | not_applicable | 0.98 |
| P04_C2 | P04 | Correct Claim Only | `temperature <= 16 AND drel_density >= 35` | True | 100.0% | accepted | 0.99 |
| P04_C3 | P04 | False Claim Only | `temperature <= 16 OR drel_density >= 40` | False | 50.3% | rejected | 0.99 |
| P04_C4 | P04 | Full Reports - Provenance Masked | `temperature <= 16 AND drel_density >= 40` | False | 97.9% | revised | 0.98 |
| P04_C5 | P04 | Full Reports - Valid Provenance | `temperature <= 16 AND drel_density >= 40` | False | 97.9% | revised | 0.99 |
| P04_C6 | P04 | Full Reports - Shuffled Provenance | `temperature <= 16 AND drel_density >= 40` | False | 97.9% | revised | 0.98 |
| P05_C1 | P05 | No Archive | `temperature <= 21 AND drel_density <= 29` | False | 54.3% | not_applicable | 0.99 |
| P05_C2 | P05 | Correct Claim Only | `temperature <= 21 AND drel_density >= 15` | True | 100.0% | accepted | 0.99 |
| P05_C3 | P05 | False Claim Only | `temperature <= 21 OR drel_density >= 20` | False | 54.9% | rejected | 0.99 |
| P05_C4 | P05 | Full Reports - Provenance Masked | `temperature <= 21 AND drel_density >= 20` | False | 97.3% | revised | 0.98 |
| P05_C5 | P05 | Full Reports - Valid Provenance | `temperature <= 21 AND drel_density >= 20` | False | 97.3% | revised | 0.97 |
| P05_C6 | P05 | Full Reports - Shuffled Provenance | `temperature <= 21 AND drel_density >= 20` | False | 97.3% | revised | 0.98 |

## Parsing issues

- None.

## API usage

- Requests reported by SDK: `30`
- Input tokens: `23380`
- Output tokens: `5467`
- Total tokens: `28847`

Raw API response objects, parsed outputs, rendered prompts, and validation artifacts are preserved under `experiments/v0_6/replacement_pilot_01/`.

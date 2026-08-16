# The Commons v0.6 — five-world Source-Linkage engineering pilot

> Exploratory engineering pilot only. This is not a powered confirmatory result.

- Generation: `Generation Two only`
- Model: `gpt-5.6-luna`
- Model settings: `{'max_turns': 1, 'session': None, 'structured_output': 'ChildRevision', 'temperature': 'SDK/model default (not explicitly set)'}`
- Runtime versions: `{'openai': '3.1.0', 'openai-agents': '0.21.0', 'pydantic': '2.13.4', 'python': '3.12.13', 'tiktoken': '0.13.0'}`
- Authorized logical API calls: `30`
- Parsed outputs: `0`
- Errors/parsing issues: `30`

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
| No Archive | 0 | n/a | 0/0 (n/a) |
| Correct Claim Only | 0 | n/a | 0/0 (n/a) |
| False Claim Only | 0 | n/a | 0/0 (n/a) |
| Full Reports - Provenance Masked | 0 | n/a | 0/0 (n/a) |
| Full Reports - Valid Provenance | 0 | n/a | 0/0 (n/a) |
| Full Reports - Shuffled Provenance | 0 | n/a | 0/0 (n/a) |

## Preregistered paired contrasts

Positive values favor the first condition named.

| Contrast | Paired worlds | Accuracy difference | Semantic-equivalence difference |
|---|---:|---:|---:|
| Valid minus Masked | 0 | n/a | n/a |
| Valid minus Shuffled | 0 | n/a | n/a |
| Shuffled minus Masked | 0 | n/a | n/a |
| Masked minus False Claim Only | 0 | n/a | n/a |

## Trial outputs

| Trial | World | Condition | Rule | Equivalent? | Accuracy | Assessment | Confidence |
|---|---|---|---|---:|---:|---|---:|
| P01_C1 | P01 | No Archive | `ERROR` | None | n/a | n/a | n/a |
| P01_C2 | P01 | Correct Claim Only | `ERROR` | None | n/a | n/a | n/a |
| P01_C3 | P01 | False Claim Only | `ERROR` | None | n/a | n/a | n/a |
| P01_C4 | P01 | Full Reports - Provenance Masked | `ERROR` | None | n/a | n/a | n/a |
| P01_C5 | P01 | Full Reports - Valid Provenance | `ERROR` | None | n/a | n/a | n/a |
| P01_C6 | P01 | Full Reports - Shuffled Provenance | `ERROR` | None | n/a | n/a | n/a |
| P02_C1 | P02 | No Archive | `ERROR` | None | n/a | n/a | n/a |
| P02_C2 | P02 | Correct Claim Only | `ERROR` | None | n/a | n/a | n/a |
| P02_C3 | P02 | False Claim Only | `ERROR` | None | n/a | n/a | n/a |
| P02_C4 | P02 | Full Reports - Provenance Masked | `ERROR` | None | n/a | n/a | n/a |
| P02_C5 | P02 | Full Reports - Valid Provenance | `ERROR` | None | n/a | n/a | n/a |
| P02_C6 | P02 | Full Reports - Shuffled Provenance | `ERROR` | None | n/a | n/a | n/a |
| P03_C1 | P03 | No Archive | `ERROR` | None | n/a | n/a | n/a |
| P03_C2 | P03 | Correct Claim Only | `ERROR` | None | n/a | n/a | n/a |
| P03_C3 | P03 | False Claim Only | `ERROR` | None | n/a | n/a | n/a |
| P03_C4 | P03 | Full Reports - Provenance Masked | `ERROR` | None | n/a | n/a | n/a |
| P03_C5 | P03 | Full Reports - Valid Provenance | `ERROR` | None | n/a | n/a | n/a |
| P03_C6 | P03 | Full Reports - Shuffled Provenance | `ERROR` | None | n/a | n/a | n/a |
| P04_C1 | P04 | No Archive | `ERROR` | None | n/a | n/a | n/a |
| P04_C2 | P04 | Correct Claim Only | `ERROR` | None | n/a | n/a | n/a |
| P04_C3 | P04 | False Claim Only | `ERROR` | None | n/a | n/a | n/a |
| P04_C4 | P04 | Full Reports - Provenance Masked | `ERROR` | None | n/a | n/a | n/a |
| P04_C5 | P04 | Full Reports - Valid Provenance | `ERROR` | None | n/a | n/a | n/a |
| P04_C6 | P04 | Full Reports - Shuffled Provenance | `ERROR` | None | n/a | n/a | n/a |
| P05_C1 | P05 | No Archive | `ERROR` | None | n/a | n/a | n/a |
| P05_C2 | P05 | Correct Claim Only | `ERROR` | None | n/a | n/a | n/a |
| P05_C3 | P05 | False Claim Only | `ERROR` | None | n/a | n/a | n/a |
| P05_C4 | P05 | Full Reports - Provenance Masked | `ERROR` | None | n/a | n/a | n/a |
| P05_C5 | P05 | Full Reports - Valid Provenance | `ERROR` | None | n/a | n/a | n/a |
| P05_C6 | P05 | Full Reports - Shuffled Provenance | `ERROR` | None | n/a | n/a | n/a |

## Parsing issues

- `P01_C1` (No Archive): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P01_C2` (Correct Claim Only): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P01_C3` (False Claim Only): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P01_C4` (Full Reports - Provenance Masked): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P01_C5` (Full Reports - Valid Provenance): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P01_C6` (Full Reports - Shuffled Provenance): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P02_C1` (No Archive): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P02_C2` (Correct Claim Only): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P02_C3` (False Claim Only): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P02_C4` (Full Reports - Provenance Masked): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P02_C5` (Full Reports - Valid Provenance): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P02_C6` (Full Reports - Shuffled Provenance): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P03_C1` (No Archive): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P03_C2` (Correct Claim Only): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P03_C3` (False Claim Only): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P03_C4` (Full Reports - Provenance Masked): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P03_C5` (Full Reports - Valid Provenance): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P03_C6` (Full Reports - Shuffled Provenance): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P04_C1` (No Archive): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P04_C2` (Correct Claim Only): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P04_C3` (False Claim Only): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P04_C4` (Full Reports - Provenance Masked): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P04_C5` (Full Reports - Valid Provenance): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P04_C6` (Full Reports - Shuffled Provenance): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P05_C1` (No Archive): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P05_C2` (Correct Claim Only): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P05_C3` (False Claim Only): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P05_C4` (Full Reports - Provenance Masked): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P05_C5` (Full Reports - Valid Provenance): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'
- `P05_C6` (Full Reports - Shuffled Provenance): TypeError: BaseModel.model_dump() missing 1 required positional argument: 'self'

## API usage

- Requests reported by SDK: `0`
- Input tokens: `0`
- Output tokens: `0`
- Total tokens: `0`

Raw API response objects, parsed outputs, rendered prompts, and validation artifacts are preserved under `experiments/v0_6/pilot/`.

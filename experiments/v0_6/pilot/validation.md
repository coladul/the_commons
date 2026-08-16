# The Commons v0.6 pilot validation

- Overall result: **PASS**
- Validated at: `2026-08-16T04:21:54.574160+00:00`
- Historical v0.1–v0.5 hashes: **PASS**
- World-generator checks: **PASS**
- Core prompt matching: **PASS**
- Counterbalancing: **PASS**
- Frozen artifacts: **PASS**

## Core prompt invariants

| World | Canonical match | Same chars/bytes | Same whitespace tokens | Claim identical/unattributed | Correct mappings |
|---|---:|---:|---:|---:|---:|
| P01 | yes | yes | yes | yes | yes |
| P02 | yes | yes | yes | yes | yes |
| P03 | yes | yes | yes | yes | yes |
| P04 | yes | yes | yes | yes | yes |
| P05 | yes | yes | yes | yes | yes |

## Tokenizer check

- Available: `True`
- Result: `True`
- Encoding: `o200k_base fallback`

## Counterbalancing

- Reliable source counts: `{'SOURCE_A': 3, 'SOURCE_B': 2}`
- True-report packet first: `3`
- False-report packet first: `2`

The pilot run command refuses to make API calls unless this validation passes.
